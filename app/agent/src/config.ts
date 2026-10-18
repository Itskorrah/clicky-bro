import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

export interface AgentConfig {
  /** clicky-bro backend base URL (no trailing slash). */
  backendUrl: string;
  /** Supabase JWT or exchanged session token presented to the backend. */
  token?: string;
  /** Google key; used only with the native Gemini runtime, never Codex auth. */
  geminiApiKey?: string;
  geminiModel?: string;
  /** Isolated CODEX_HOME. Stable across runs so threads can be resumed. */
  codexHome: string;
  /** Codex binary (name on PATH or absolute path). */
  codexBin: string;
  /** Directory the agent works in. */
  workspace: string;
  /** Directories outside the workspace that Codex's workspace-write sandbox may write to.
   *  Empty means the workspace only (Codex's own default). */
  writableRoots: string[];
  /** Optional model override for Codex runs. */
  model?: string;
  /** Repo root (contains skills/ and config/). */
  root: string;
  verbose: boolean;
  /** Composio MCP server URL; when set, the `composio` MCP server is rendered into the Codex config. */
  composioMcpUrl?: string;
  /** Composio consumer API key (`ck_…`, dashboard.composio.dev); sent as `x-consumer-api-key`. Without it
   *  Codex's MCP OAuth login (`codex mcp login composio`) authenticates the server. */
  composioApiKey?: string;
  /** Path to cua-driver; when set, the `computer-use` MCP server is rendered into the Codex config. */
  cuaDriverBin?: string;
  /** ffmpeg binary used for microphone capture in the voice lane. */
  ffmpegBin: string;
  /** The user's skill library root (library/, active/, activations.json). Shared with the macOS app. */
  userSkillsDir: string;
  /** The user's own OpenAI key (bring your own key): sent to the backend per request, never stored there. */
  openaiApiKey?: string;
  /** Optional Anthropic key for the Claude lanes when bringing your own keys. */
  anthropicApiKey?: string;
  /** Wall-clock cap (ms) on a single CodexAgent.run() turn before it rejects instead of hanging
   *  forever on a Codex bug that never emits a terminal event. See codex.ts DEFAULT_RUN_TIMEOUT_MS. */
  runTimeoutMs: number;
}

/** Repo root: agent/src/config.ts or agent/dist/config.js → ../../ */
export function repoRoot(): string {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
}

const stripSlash = (u: string) => u.replace(/\/+$/, "");

function privateGeminiKey(file: string | undefined): string | undefined {
  if (!file) return undefined;
  const stat = fs.lstatSync(file);
  if (!stat.isFile() || stat.isSymbolicLink()) throw new Error("Gemini key file must be a regular private file");
  if (process.platform !== "win32" && ((stat.mode & 0o077) !== 0 || stat.uid !== process.getuid?.())) throw new Error("Gemini key file must be owned by you and have mode 600");
  const key = JSON.parse(fs.readFileSync(file, "utf8")).api_key;
  if (typeof key !== "string" || !key.trim()) throw new Error("Gemini key file has no api_key");
  return key.trim();
}

/** `~/Desktop, /Volumes/Work` → absolute paths. Undefined means the default (workspace only). */
function parseWritableRoots(value: string | undefined, home: string): string[] {
  if (value === undefined) return [];
  return value
    .split(",")
    .map((entry) => entry.trim())
    .filter((entry) => entry.length > 0)
    .map((entry) => path.resolve(entry.startsWith("~") ? path.join(home, entry.slice(1)) : entry));
}

/**
 * Where cua-driver is, so the `computer-use` MCP server is actually rendered. Without this the
 * agent's instructions advertise Computer Use while no such server is attached, and the model
 * spends turns enumerating MCP resources looking for it before falling back to the shell.
 * An explicit CUA_DRIVER_BIN wins; an explicit empty string disables it.
 */
function resolveCuaDriverBin(configured: string | undefined, home: string): string | undefined {
  if (configured !== undefined) return configured === "" ? undefined : configured;
  const candidates = [
    path.join(home, ".local", "bin", "cua-driver"),
    "/Applications/CuaDriver.app/Contents/MacOS/cua-driver",
  ];
  return candidates.find((candidate) => {
    try {
      fs.accessSync(candidate, fs.constants.X_OK);
      return true;
    } catch {
      return false;
    }
  });
}

/** Flags win over env, env over defaults. */
export function resolveConfig(flags: Partial<AgentConfig> = {}, env: NodeJS.ProcessEnv = process.env): AgentConfig {
  const home = env.HOME ?? os.homedir();
  return {
    backendUrl: stripSlash(flags.backendUrl ?? env.CLICKY_BRO_BACKEND_URL ?? env.BACKEND_URL ?? "http://127.0.0.1:18787"),
    token: flags.token ?? env.CLICKY_BRO_TOKEN ?? undefined,
    geminiApiKey: flags.geminiApiKey ?? env.CLICKY_BRO_GEMINI_KEY ?? privateGeminiKey(env.CLICKY_BRO_GEMINI_KEY_FILE) ?? env.GEMINI_API_KEY,
    geminiModel: flags.geminiModel ?? env.CLICKY_BRO_GEMINI_MODEL ?? "gemini-3.5-flash-lite",
    codexHome: flags.codexHome ?? env.CLICKY_BRO_CODEX_HOME ?? path.join(home, ".clicky-bro", "codex-home"),
    codexBin: flags.codexBin ?? env.CLICKY_BRO_CODEX_BIN ?? "codex",
    workspace: path.resolve(flags.workspace ?? env.CLICKY_BRO_WORKSPACE ?? process.cwd()),
    // Additional writable roots require explicit user configuration.
    writableRoots: flags.writableRoots ?? parseWritableRoots(env.CLICKY_BRO_WRITABLE_ROOTS, home),
    model: flags.model ?? env.CLICKY_BRO_MODEL ?? undefined,
    root: flags.root ?? repoRoot(),
    verbose: flags.verbose ?? env.CLICKY_BRO_VERBOSE === "1",
    composioMcpUrl: flags.composioMcpUrl ?? env.COMPOSIO_MCP_URL ?? undefined,
    composioApiKey: flags.composioApiKey ?? env.COMPOSIO_API_KEY ?? undefined,
    cuaDriverBin: flags.cuaDriverBin ?? resolveCuaDriverBin(env.CUA_DRIVER_BIN, home),
    ffmpegBin: flags.ffmpegBin ?? env.CLICKY_BRO_FFMPEG_BIN ?? "ffmpeg",
    userSkillsDir: path.resolve(flags.userSkillsDir ?? env.CLICKY_BRO_USER_SKILLS_DIR ?? path.join(home, ".clicky-bro", "skills")),
    openaiApiKey: flags.openaiApiKey ?? env.CLICKY_BRO_OPENAI_KEY ?? undefined,
    anthropicApiKey: flags.anthropicApiKey ?? env.CLICKY_BRO_ANTHROPIC_KEY ?? undefined,
    // 10 minutes by default (see codex.ts DEFAULT_RUN_TIMEOUT_MS): long enough for any real agent
    // task, short enough that a Codex bug which never emits a terminal event can't hang forever.
    runTimeoutMs: flags.runTimeoutMs ?? parsePositiveInt(env.CLICKY_BRO_RUN_TIMEOUT_MS) ?? 10 * 60 * 1000,
  };
}

/** A positive integer from an env var, or undefined if unset/not a positive integer. */
function parsePositiveInt(value: string | undefined): number | undefined {
  if (!value) return undefined;
  const n = Number(value);
  return Number.isFinite(n) && n > 0 ? n : undefined;
}
