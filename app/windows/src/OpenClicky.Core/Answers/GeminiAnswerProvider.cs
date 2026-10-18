// Port of macos/OpenClicky/OpenClicky/GeminiAnswerProvider.swift
//
// Answers through Google's Gemini API (`streamGenerateContent` with `alt=sse`). Gemini has its
// own shapes: turns are `contents` with roles user/model, images are `inlineData`, tools are
// `functionDeclarations`, and a tool call arrives whole as a `functionCall` part. The request is
// built and the stream is read by pure static functions, unit-tested in AnswerProviderHttpTests.
// The key travels in the `x-goog-api-key` header, never in the URL, so it cannot end up in a log
// line that prints a URL.

using System.Text;
using System.Text.Json.Nodes;
using OpenClicky.Core.Configuration;
using OpenClicky.Core.Providers;

namespace OpenClicky.Core.Answers;

public sealed class GeminiAnswerProvider(string apiKey, string model, AnswerHttpTransport? transport = null) : IAnswerProvider
{
    public string ApiKey { get; } = apiKey;
    public string Model { get; } = model;
    private readonly AnswerHttpTransport transport = transport ?? AnswerHttpTransports.Shared;

    // Supplied only by the host's explicit action lane. An ordinary answer/teaching request has no executor.
    public Func<ClaudeToolCall, CancellationToken, Task<string>>? ToolExecutor { get; set; }
    public static readonly IReadOnlySet<string> FreeModelAllowlist = new HashSet<string>(StringComparer.Ordinal)
    { "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-3-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite" };

    public async Task<AnswerResult> AnswerAsync(AnswerRequest request, Action<string> onTextChunk, CancellationToken cancellationToken = default)
    {
        if (!FreeModelAllowlist.Contains(Model)) throw new AnswerProviderException(AnswerSource.Gemini, 0, "model is outside clicky-bro's free-only allowlist");
        var body = MakeRequestBody(Model, request);
        var contents = (JsonArray)body["contents"]!;
        var text = new StringBuilder();
        var outcomes = new List<string>();
        var actionCount = 0;
        for (var turn = 0; turn < 3; turn++)
        {
            cancellationToken.ThrowIfCancellationRequested();
            using var httpRequest = MakeHttpRequest(ApiKey, Model, request);
            httpRequest.Content = DirectProviderRequests.JsonContent(body);
            var response = await transport(httpRequest, cancellationToken).ConfigureAwait(false);
            if (response.StatusCode is < 200 or > 299)
            {
                var errorBody = await AnswerProviderHttpSupport.ReadWholeBodyAsync(response.BodyLines, cancellationToken).ConfigureAwait(false);
                var vendorMessage = AnswerProviderHttpSupport.VendorErrorMessage(errorBody);
                if (!string.IsNullOrEmpty(ApiKey)) vendorMessage = vendorMessage.Replace(ApiKey, "[redacted]", StringComparison.Ordinal);
                var message = response.StatusCode == 429 ? "quota/rate limit reached; retry later. No paid fallback was attempted." : vendorMessage;
                if (outcomes.Count > 0) message += " Completed action outcomes: " + string.Join("; ", outcomes);
                throw new AnswerProviderException(AnswerSource.Gemini, response.StatusCode, message);
            }
            var accumulator = new GeminiStreamAccumulator();
            await foreach (var line in response.BodyLines.WithCancellation(cancellationToken).ConfigureAwait(false))
            {
                cancellationToken.ThrowIfCancellationRequested();
                IReadOnlyList<string> chunks;
                try { chunks = accumulator.Consume(line); }
                catch (GeminiStreamAccumulator.StreamRefusalException error) { throw new AnswerProviderException(AnswerSource.Gemini, response.StatusCode, string.IsNullOrEmpty(ApiKey) ? error.Message : error.Message.Replace(ApiKey, "[redacted]", StringComparison.Ordinal)); }
                foreach (var chunk in chunks) { text.Append(chunk); onTextChunk(chunk); }
            }
            if (accumulator.FinishReason != "STOP")
                throw new AnswerProviderException(AnswerSource.Gemini, 0, "response ended without a complete answer; no actions were retried");
            var result = accumulator.Result();
            if (result.ToolCalls.Count == 0 || ToolExecutor is null) return new AnswerResult(text.ToString(), result.ToolCalls);
            contents.Add(new JsonObject { ["role"] = "model", ["parts"] = accumulator.ModelParts.DeepClone() });
            var responses = new JsonArray();
            foreach (var call in result.ToolCalls)
            {
                cancellationToken.ThrowIfCancellationRequested();
                var outcome = actionCount >= 2 ? "Action limit reached; action was not executed." : await ToolExecutor(call, cancellationToken).ConfigureAwait(false);
                actionCount++;
                outcomes.Add(outcome);
                cancellationToken.ThrowIfCancellationRequested();
                var functionResponse = new JsonObject { ["name"] = call.Name, ["response"] = new JsonObject { ["outcome"] = outcome } };
                if (accumulator.OriginalCallIds.TryGetValue(call.Id, out var originalId)) functionResponse["id"] = originalId;
                responses.Add(new JsonObject { ["functionResponse"] = functionResponse });
            }
            contents.Add(new JsonObject { ["role"] = "user", ["parts"] = responses });
        }
        throw new AnswerProviderException(AnswerSource.Gemini, 0, "request limit reached. Completed action outcomes: " + string.Join("; ", outcomes));
    }

    // MARK: request

    /// <summary>Foundation's `urlPathAllowed`: unreserved characters plus the sub-delims, ":", "@" and "/".</summary>
    private const string UrlPathAllowedPunctuation = "-._~!$&'()*+,;=:@/";

    public static Uri? StreamGenerateContentUrl(string model)
    {
        var pathSafeModel = new StringBuilder();
        foreach (var utf8Byte in Encoding.UTF8.GetBytes(model))
        {
            var character = (char)utf8Byte;
            if (utf8Byte < 0x80 && (char.IsAsciiLetterOrDigit(character) || UrlPathAllowedPunctuation.Contains(character))) pathSafeModel.Append(character);
            else pathSafeModel.Append('%').Append(utf8Byte.ToString("X2"));
        }
        return Uri.TryCreate($"https://generativelanguage.googleapis.com/v1beta/models/{pathSafeModel}:streamGenerateContent?alt=sse", UriKind.Absolute, out var url) ? url : null;
    }

    /// <summary>
    /// JSON Schema keywords Gemini's function declarations reject ("Unknown name
    /// \"additionalProperties\""): its parameters are an OpenAPI subset, so these are removed.
    /// </summary>
    public static readonly IReadOnlySet<string> SchemaKeywordsGeminiRejects = new HashSet<string>
    {
        "additionalProperties", "$schema", "$id", "$comment", "$defs", "definitions", "examples",
    };

    /// <summary>
    /// The schema without the keywords Gemini rejects, at every depth. The keys directly inside
    /// `properties` are argument names, not keywords, so an argument that happens to be called
    /// "examples" is kept.
    /// </summary>
    public static JsonNode? SchemaGeminiAccepts(JsonNode? schemaValue)
    {
        switch (schemaValue)
        {
            case JsonArray schemaArray:
                return new JsonArray(schemaArray.Select(SchemaGeminiAccepts).ToArray());
            case JsonObject schemaObject:
                var acceptedSchemaObject = new JsonObject();
                foreach (var (keyword, keywordValue) in schemaObject)
                {
                    if (SchemaKeywordsGeminiRejects.Contains(keyword)) continue;
                    if (keyword == "properties" && keywordValue is JsonObject propertiesByArgumentName)
                    {
                        var acceptedProperties = new JsonObject();
                        foreach (var (argumentName, argumentSchema) in propertiesByArgumentName)
                        {
                            acceptedProperties[argumentName] = SchemaGeminiAccepts(argumentSchema);
                        }
                        acceptedSchemaObject[keyword] = acceptedProperties;
                    }
                    else
                    {
                        acceptedSchemaObject[keyword] = SchemaGeminiAccepts(keywordValue);
                    }
                }
                return acceptedSchemaObject;
            case null:
                return null;
            default:
                return schemaValue.DeepClone();
        }
    }

    /// <summary>
    /// Gemini 3 models think before answering by default, and that thinking is paid out of
    /// `maxOutputTokens`: measured 2026-10-11 on gemini-3.8-flash, a 40-token limit was spent
    /// entirely on 37 thought tokens and the answer came back empty (finishReason MAX_TOKENS).
    /// The ask lane is short and spoken, so Gemini 3 is asked to think little ("low"; "minimal" is
    /// refused by 3.8-flash). Even "low" still spends 30-40 thought tokens on a one-word image
    /// question, so a limit of a few dozen tokens is still too small; the ask lane's 1024 is fine.
    /// Older models are left to their defaults: 2.5 takes `thinkingBudget` instead, and 2.5 Pro
    /// refuses a budget of 0.
    /// </summary>
    public static JsonObject? ThinkingConfig(string model) =>
        model.StartsWith("gemini-3", StringComparison.Ordinal) ? new JsonObject { ["thinkingLevel"] = "low" } : null;

    /// <summary>The request body as a JSON object (kept separate from the HttpRequestMessage so tests can read it).</summary>
    public static JsonObject MakeRequestBody(string model, AnswerRequest answerRequest)
    {
        var contents = new JsonArray();
        foreach (var earlierTurn in answerRequest.History)
        {
            contents.Add(new JsonObject { ["role"] = "user", ["parts"] = new JsonArray(new JsonObject { ["text"] = earlierTurn.User }) });
            contents.Add(new JsonObject { ["role"] = "model", ["parts"] = new JsonArray(new JsonObject { ["text"] = earlierTurn.Assistant }) });
        }

        // Each screenshot, then its label (which display, and the pixel size the [POINT:…]
        // coordinates are measured against), then the question itself.
        var currentUserParts = new JsonArray();
        foreach (var labelledImage in answerRequest.Images)
        {
            currentUserParts.Add(new JsonObject
            {
                ["inlineData"] = new JsonObject { ["mimeType"] = labelledImage.MediaType, ["data"] = Convert.ToBase64String(labelledImage.Data) },
            });
            currentUserParts.Add(new JsonObject { ["text"] = labelledImage.Label });
        }
        currentUserParts.Add(new JsonObject { ["text"] = answerRequest.UserPrompt });
        contents.Add(new JsonObject { ["role"] = "user", ["parts"] = currentUserParts });

        var generationConfig = new JsonObject { ["maxOutputTokens"] = answerRequest.MaxTokens };
        if (ThinkingConfig(model) is { } thinkingConfig) generationConfig["thinkingConfig"] = thinkingConfig;
        var body = new JsonObject
        {
            ["contents"] = contents,
            ["generationConfig"] = generationConfig,
        };
        if (answerRequest.SystemPrompt.Length > 0)
        {
            body["systemInstruction"] = new JsonObject { ["parts"] = new JsonArray(new JsonObject { ["text"] = answerRequest.SystemPrompt }) };
        }
        if (answerRequest.Tools.Count > 0)
        {
            var functionDeclarations = new JsonArray(answerRequest.Tools.Select(quickActionTool => (JsonNode)new JsonObject
            {
                ["name"] = quickActionTool.Name,
                ["description"] = quickActionTool.Description,
                ["parameters"] = SchemaGeminiAccepts(AnswerProviderHttpSupport.InputSchemaObject(quickActionTool.InputSchemaJson)),
            }).ToArray());
            body["tools"] = new JsonArray(new JsonObject { ["functionDeclarations"] = functionDeclarations });
        }
        return body;
    }

    public static HttpRequestMessage MakeHttpRequest(string apiKey, string model, AnswerRequest answerRequest)
    {
        if (StreamGenerateContentUrl(model) is not { } url)
        {
            throw new AnswerProviderException(AnswerSource.Gemini, 0, $"\"{model}\" is not a model name Gemini can be asked for");
        }
        var httpRequest = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = DirectProviderRequests.JsonContent(MakeRequestBody(model, answerRequest)),
        };
        httpRequest.SetHeader("Accept", "text/event-stream");
        httpRequest.SetHeader("x-goog-api-key", apiKey);
        return httpRequest;
    }

    // MARK: stream

    /// <summary>The answer in a whole list of SSE lines (what the streaming loop builds line by line).</summary>
    public static AnswerResult ParseStream(IEnumerable<string> lines)
    {
        var streamAccumulator = new GeminiStreamAccumulator();
        foreach (var line in lines) streamAccumulator.Consume(line);
        return streamAccumulator.Result();
    }
}

/// <summary>
/// Reads a Gemini SSE stream one line at a time. Every `data:` line is a whole
/// GenerateContentResponse; its first candidate's parts are text (shown as it comes) or a complete
/// `functionCall`. Gemini gives a call no id, so each gets "gemini-&lt;n&gt;" in the order it came.
/// </summary>
public sealed class GeminiStreamAccumulator
{
    /// <summary>
    /// A question Gemini declined after the 200: a `promptFeedback.blockReason` (safety) or an
    /// `error` object inside the stream.
    /// </summary>
    public sealed class StreamRefusalException(string message) : Exception(message);

    public JsonArray ModelParts { get; } = new();
    public Dictionary<string, string> OriginalCallIds { get; } = new();
    private readonly StringBuilder accumulatedText = new();
    private readonly List<ClaudeToolCall> toolCalls = [];

    public string AccumulatedText => accumulatedText.ToString();
    public string? FinishReason { get; private set; }

    /// <summary>The text pieces this line carried, in order (usually one, sometimes none).</summary>
    public IReadOnlyList<string> Consume(string line)
    {
        if (AnswerProviderHttpSupport.SseDataPayload(line) is not { } dataPayload
            || JsonHelpers.TryParse(dataPayload) is not JsonObject streamEvent)
        {
            return [];
        }
        if (streamEvent["error"] is JsonObject streamError)
        {
            throw new StreamRefusalException(JsonHelpers.String(streamError["message"]) ?? "the stream broke off");
        }
        if (streamEvent["promptFeedback"] is JsonObject promptFeedback && JsonHelpers.String(promptFeedback["blockReason"]) is { } blockReason)
        {
            throw new StreamRefusalException($"Gemini would not answer this question ({blockReason})");
        }
        if ((streamEvent["candidates"] as JsonArray)?.FirstOrDefault() is not JsonObject firstCandidate) return [];
        if (JsonHelpers.String(firstCandidate["finishReason"]) is { } candidateFinishReason) FinishReason = candidateFinishReason;
        if (firstCandidate["content"] is not JsonObject content || content["parts"] is not JsonArray parts) return [];

        var textChunks = new List<string>();
        foreach (var part in parts.OfType<JsonObject>())
        {
            ModelParts.Add(part.DeepClone());
            // A thinking model can be asked to include its thoughts; they are never the answer.
            if (JsonHelpers.Bool(part["thought"]) == true) continue;
            if (part["functionCall"] is JsonObject functionCall && JsonHelpers.String(functionCall["name"]) is { Length: > 0 } functionName)
            {
                var argumentsObject = functionCall["args"] as JsonObject ?? new JsonObject();
                var callId = JsonHelpers.String(functionCall["id"]) ?? $"gemini-{toolCalls.Count + 1}";
                if (JsonHelpers.String(functionCall["id"]) is { } originalId) OriginalCallIds[callId] = originalId;
                toolCalls.Add(new ClaudeToolCall(
                    callId,
                    functionName,
                    AnswerProviderHttpSupport.ToolArguments(argumentsObject)));
                continue;
            }
            if (JsonHelpers.String(part["text"]) is { Length: > 0 } textChunk)
            {
                accumulatedText.Append(textChunk);
                textChunks.Add(textChunk);
            }
        }
        return textChunks;
    }

    public AnswerResult Result() => new(AccumulatedText, toolCalls.ToList());
}
