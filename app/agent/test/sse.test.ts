import { describe, expect, it } from "vitest";
import { parseSseChunk, parseSseStream, readSseAnswer } from "../src/sse.js";

const event = (value: string) => "data: " + JSON.stringify({ choices: [{ delta: { content: value } }] });
const encode = new TextEncoder();
async function* chunks(...values: string[]) {
  for (const value of values) yield encode.encode(value);
}

describe("bounded SSE responses", () => {
  it("joins valid LF events and ignores content after DONE", () => {
    const result = parseSseChunk(event("hello") + "\n\n" + event(" world") + "\n\ndata: [DONE]\n\n" + event("discard") + "\n\n");
    expect(result.text).toBe("hello world");
    expect(result.done).toBe(true);
  });

  it("supports CRLF streams split at an arbitrary byte boundary", () => {
    const stream = event("A") + "\r\n\r\n" + event("B") + "\r\n\r\ndata: [DONE]\r\n\r\n";
    const first = parseSseChunk(stream.slice(0, stream.indexOf("\r\n\r\n") + 3));
    const second = parseSseChunk(first.rest + stream.slice(stream.indexOf("\r\n\r\n") + 3));
    expect(first.text + second.text).toBe("AB");
    expect(second.done).toBe(true);
  });

  it("keeps a dangling CR until the next chunk instead of inventing a blank line", () => {
    const first = parseSseChunk(event("a") + "\r");
    expect(first.text).toBe("");
    expect(parseSseChunk(first.rest + "\n\r\n").text).toBe("a");
  });

  it("ignores comments and accepts multiline event data", () => {
    const data = ': heartbeat\r\ndata: {\r\ndata: "choices":[{"delta":{"content":"ok"}}]\r\ndata: }\r\n\r\n';
    expect(parseSseStream(data)).toBe("ok");
  });

  it("supports standalone CR and rejects oversized event bodies", () => {
    expect(parseSseStream(event("a") + "\r\r" + event("b") + "\r\r")).toBe("ab");
    expect(() => parseSseChunk("data: " + "x".repeat(1024 * 1024 + 1))).toThrow(/1 MiB/);
  });

  it("rejects incomplete streams instead of accepting partial answers", async () => {
    await expect(readSseAnswer(chunks(event("part") + "\n\n"))).rejects.toThrow(/completion marker/);
    await expect(readSseAnswer(chunks("data: [DONE]\n\n"))).rejects.toThrow(/empty response/);
  });

  it("streams validated answers with deltas", async () => {
    const deltas: string[] = [];
    const response = await readSseAnswer(chunks(event("a") + "\r", "\n\r\n", event("b") + "\n\n", "data: [DONE]\n\n"), t => deltas.push(t));
    expect(response).toBe("ab");
    expect(deltas).toEqual(["a", "b"]);
  });

  it("decodes multibyte characters even when split across byte chunks", async () => {
    const bytes = encode.encode(event("é🎉") + "\n\ndata: [DONE]\n\n");
    async function* oneByteAtATime() {
      for (const byte of bytes) yield Uint8Array.from([byte]);
    }
    expect(await readSseAnswer(oneByteAtATime())).toBe("é🎉");
  });

  it("bounds total response size", async () => {
    const many = event("x".repeat(100_000)) + "\n\n";
    async function* large() {
      for (let i = 0; i < 50; i++) yield encode.encode(many);
      yield encode.encode("data: [DONE]\n\n");
    }
    await expect(readSseAnswer(large())).rejects.toThrow(/4 MiB/);
  });
});
