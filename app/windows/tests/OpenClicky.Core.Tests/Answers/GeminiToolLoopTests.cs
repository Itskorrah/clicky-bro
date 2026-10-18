using System.Text.Json.Nodes;
using OpenClicky.Core.Answers;

namespace OpenClicky.Core.Tests.Answers;

public sealed class GeminiToolLoopTests
{
    private static AnswerRequest Request() => new([], "Answer safely", [], "Set volume", [new("set_volume", "Set volume", "{\"type\":\"object\",\"properties\":{\"level\":{\"type\":\"integer\"}}}")]);

    [Theory]
    [InlineData("MAX_TOKENS")]
    [InlineData("SAFETY")]
    [InlineData("RECITATION")]
    [InlineData("OTHER")]
    [InlineData(null)]
    public async Task IncompleteOrRefusedToolsNeverReachAnExecutor(string? reason)
    {
        var actions = 0;
        var payload = new JsonObject { ["candidates"] = new JsonArray(new JsonObject {
            ["finishReason"] = reason,
            ["content"] = new JsonObject { ["parts"] = new JsonArray(new JsonObject {
                ["functionCall"] = new JsonObject { ["name"] = "set_volume", ["args"] = new JsonObject { ["level"] = 40 } }
            }) }
        }) };
        var provider = new GeminiAnswerProvider("test-only", "gemini-3.5-flash-lite", AnswerHttpTransports.Canned(200, ["data: " + payload.ToJsonString()]))
        { ToolExecutor = (_, _) => { actions++; return Task.FromResult("must not execute"); } };
        await Assert.ThrowsAsync<AnswerProviderException>(() => provider.AnswerAsync(Request(), _ => { }));
        Assert.Equal(0, actions);
    }

    [Fact]
    public async Task StreamErrorsNeverExposeTheCredential()
    {
        const string key = "synthetic-key-for-redaction";
        var payload = new JsonObject { ["error"] = new JsonObject { ["message"] = "Provider rejected " + key } };
        var provider = new GeminiAnswerProvider(key, "gemini-3.5-flash-lite", AnswerHttpTransports.Canned(200, ["data: " + payload.ToJsonString()]));
        var error = await Assert.ThrowsAsync<AnswerProviderException>(() => provider.AnswerAsync(Request(), _ => { }));
        Assert.DoesNotContain(key, error.Message);
        Assert.Contains("[redacted]", error.Message);
    }

    [Fact]
    public async Task GenuineOutcomeAndOpaqueSignatureReturnToGemini()
    {
        var bodies = new List<JsonNode>();
        var actions = 0;
        AnswerHttpTransport transport = async (request, token) =>
        {
            bodies.Add(JsonNode.Parse(await request.Content!.ReadAsStringAsync(token))!);
            var line = bodies.Count == 1
                ? """data: {"candidates":[{"content":{"role":"model","parts":[{"thoughtSignature":"opaque","functionCall":{"id":"original-id","name":"set_volume","args":{"level":40}}}]},"finishReason":"STOP"}]}"""
                : """data: {"candidates":[{"content":{"role":"model","parts":[{"text":"Volume set."}]},"finishReason":"STOP"}]}""";
            return await AnswerHttpTransports.Canned(200, [line])(request, token);
        };
        var provider = new GeminiAnswerProvider("test-only", "gemini-3.5-flash-lite", transport)
        {
            ToolExecutor = (call, token) => { token.ThrowIfCancellationRequested(); actions++; Assert.Equal("40", call.Arguments["level"]); return Task.FromResult("The actual volume is now 40 percent."); }
        };
        var result = await provider.AnswerAsync(Request(), _ => { });
        Assert.Equal(1, actions); Assert.Equal("Volume set.", result.Text); Assert.Empty(result.ToolCalls);
        Assert.Equal("opaque", bodies[1]["contents"]![1]!["parts"]![0]!["thoughtSignature"]!.GetValue<string>());
        var response = bodies[1]["contents"]![2]!["parts"]![0]!["functionResponse"]!;
        Assert.Equal("original-id", response["id"]!.GetValue<string>());
        Assert.Equal("The actual volume is now 40 percent.", response["response"]!["outcome"]!.GetValue<string>());
    }

    [Fact]
    public async Task QuotaAfterAnActionStopsWithoutFallbackAndReportsCommittedOutcome()
    {
        var requests = 0; var actions = 0;
        AnswerHttpTransport transport = (request, token) =>
            AnswerHttpTransports.Canned(++requests == 1 ? 200 : 429, requests == 1
                ? ["""data: {"candidates":[{"content":{"parts":[{"functionCall":{"name":"set_volume","args":{"level":40}}}]},"finishReason":"STOP"}]}"""]
                : ["quota"])(request, token);
        var provider = new GeminiAnswerProvider("test-only", "gemini-3.5-flash-lite", transport)
        { ToolExecutor = (_, _) => { actions++; return Task.FromResult("Volume changed to 40 percent"); } };
        var error = await Assert.ThrowsAsync<AnswerProviderException>(() => provider.AnswerAsync(Request(), _ => { }));
        Assert.Equal(429, error.Status); Assert.Contains("Volume changed", error.Message); Assert.Equal(2, requests); Assert.Equal(1, actions);
    }

    [Fact]
    public async Task NoExecutorLeavesActionForHostAndDoesNotRetry()
    {
        var requests = 0;
        AnswerHttpTransport transport = (request, token) =>
        {
            requests++;
            return AnswerHttpTransports.Canned(200, ["""data: {"candidates":[{"content":{"parts":[{"functionCall":{"name":"set_volume","args":{"level":40}}}]},"finishReason":"STOP"}]}"""])(request, token);
        };
        var result = await new GeminiAnswerProvider("test-only", "gemini-3.5-flash-lite", transport).AnswerAsync(Request(), _ => { });
        Assert.Single(result.ToolCalls); Assert.Equal(1, requests);
    }

    [Fact]
    public async Task CancellationPreventsRequestsAndUnsupportedModelCannotSpend()
    {
        AnswerHttpTransport transport = (_, _) => throw new InvalidOperationException("Network must not be called");
        await Assert.ThrowsAsync<AnswerProviderException>(() => new GeminiAnswerProvider("test-only", "paid-model", transport).AnswerAsync(Request(), _ => { }));
        using var cancellation = new CancellationTokenSource(); cancellation.Cancel();
        await Assert.ThrowsAnyAsync<OperationCanceledException>(() => new GeminiAnswerProvider("test-only", "gemini-3.5-flash-lite", transport).AnswerAsync(Request(), _ => { }, cancellation.Token));
    }
}
