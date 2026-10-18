import fs from "node:fs";
import path from "node:path";
import type { AgentConfig } from "./config.js";
import { geminiAsk } from "./gemini.js";
import { readSseAnswer } from "./sse.js";
export { parseSseChunk, parseSseStream } from "./sse.js";
import { openaiRoute, needsOpenAI, DIRECT_DEFAULTS } from "./providerRoute.js";

export interface AskOptions {
  imagePath?: string;
  system?: string;
  /** Streamed text deltas as they arrive. */
  onDelta?: (text: string) => void;
  fetchImpl?: typeof fetch;
}

export const ASK_SYSTEM_PROMPT =
  "You are clicky-bro's quick-answer lane (the \"higher model\"). Answer the user's question directly and " +
  "concisely, in a voice that could be read aloud. If a screenshot is attached, treat it as the user's " +
  "current desktop context. Do not claim to have performed actions; this lane only answers.";

const MIME: Record<string, string> = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp" };

export function imageToDataUrl(imagePath: string): string {
  const mime = MIME[path.extname(imagePath).toLowerCase()] ?? "image/png";
  return `data:${mime};base64,${fs.readFileSync(imagePath).toString("base64")}`;
}

/**
 * The lightweight "ask" lane: one chat completion, no agent spawn. With the person's own OpenAI key
 * it goes straight to OpenAI; otherwise through the backend on their token, which picks the model
 * (OPENAI_MODEL) for "default".
 */
export async function ask(cfg: AgentConfig, question: string, opts: AskOptions = {}): Promise<string> {
  if (cfg.geminiApiKey) return geminiAsk(cfg, question, opts);
  const route = openaiRoute(cfg, "/v1/chat/completions", "/chat/completions", { "content-type": "application/json", accept: "text/event-stream" });
  if (!route) throw new Error(`ask ${needsOpenAI}`);
  const f = opts.fetchImpl ?? fetch;

  const userContent: unknown = opts.imagePath
    ? [
        { type: "text", text: question },
        { type: "image_url", image_url: { url: imageToDataUrl(opts.imagePath) } },
      ]
    : question;

  const res = await f(route.url, {
    method: "POST",
    headers: route.headers,
    body: JSON.stringify({
      model: route.direct ? DIRECT_DEFAULTS.openaiModel : "default",
      stream: true,
      messages: [
        { role: "system", content: opts.system ?? ASK_SYSTEM_PROMPT },
        { role: "user", content: userContent },
      ],
    }),
  });
  if (!res.ok) throw new Error(`${route.direct ? "openai" : "backend"} ${res.status}: ${(await res.text()).slice(0, 500)}`);

  const contentType = res.headers.get("content-type") ?? "";
  if (!contentType.includes("text/event-stream")) {
    // Non-streaming upstream (e.g. a provider that ignores stream:true).
    const json: any = await res.json();
    const text = json.choices?.[0]?.message?.content ?? "";
    if (!text.trim()) throw new Error("Answer provider returned an empty response.");
    opts.onDelta?.(text);
    return text;
  }

  if (!res.body) throw new Error("Answer provider returned an empty stream.");
  return readSseAnswer(res.body as unknown as AsyncIterable<Uint8Array>, opts.onDelta);
}
