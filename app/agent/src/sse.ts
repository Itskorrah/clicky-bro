/** A bounded, incremental parser for OpenAI-compatible chat-completion SSE. */
const MAX_EVENT_CHARS = 1024 * 1024;

export function parseSseChunk(buffer: string): { text: string; rest: string; done: boolean } {
  // CRLF, LF and CR are valid event-stream line endings. Preserve a trailing CR
  // until the next network chunk so a split CRLF is not counted as two lines.
  let rest = buffer.replace(/\r\n/g, "\n").replace(/\r(?!$)/g, "\n");
  let text = "";
  let done = false;
  let separator: number;

  while ((separator = rest.indexOf("\n\n")) >= 0) {
    if (separator > MAX_EVENT_CHARS) throw new Error("Answer stream event exceeded 1 MiB");
    const event = rest.slice(0, separator);
    rest = rest.slice(separator + 2);
    const payload = event.split("\n")
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).replace(/^ /, ""))
      .join("\n");
    if (payload === "[DONE]") {
      done = true;
      break; // Never include data after the terminal marker.
    }
    if (!payload) continue; // Comments, heartbeat events and empty data.
    try {
      const message = JSON.parse(payload);
      const delta = message.choices?.[0]?.delta?.content ?? message.choices?.[0]?.message?.content;
      if (typeof delta === "string") text += delta;
    } catch {
      // Ignore non-JSON keep-alives rather than accidentally rendering them.
    }
  }
  if (rest.length > MAX_EVENT_CHARS) throw new Error("Answer stream event exceeded 1 MiB");
  return { text, rest, done };
}

/** Whole-buffer convenience for tests. */
export function parseSseStream(text: string): string {
  return parseSseChunk(text + "\n\n").text;
}

/** Consume network fragments and reject a truncated or empty model answer. */
export async function readSseAnswer(
  chunks: AsyncIterable<Uint8Array>,
  onDelta?: (text: string) => void,
): Promise<string> {
  const decoder = new TextDecoder();
  let buffer = "";
  let answer = "";
  let completed = false;
  for await (const chunk of chunks) {
    buffer += decoder.decode(chunk, { stream: true });
    const parsed = parseSseChunk(buffer);
    buffer = parsed.rest;
    if (parsed.text) {
      answer += parsed.text;
      if (answer.length > 4 * 1024 * 1024) throw new Error("Answer exceeded 4 MiB");
      onDelta?.(parsed.text);
    }
    if (parsed.done) {
      completed = true;
      break;
    }
  }
  if (!completed) throw new Error("Answer stream ended before the completion marker; try again.");
  if (!answer.trim()) throw new Error("Answer provider returned an empty response.");
  return answer;
}
