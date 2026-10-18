import { describe, it, expect } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { resolveConfig, repoRoot } from "../src/config.js";

describe("resolveConfig", () => {
  it("reads only the explicitly configured private Gemini key file", () => {
    const dir=fs.mkdtempSync(path.join(os.tmpdir(),"clicky-bro-key-test-"));
    const file=path.join(dir,"key.json");fs.writeFileSync(file,JSON.stringify({api_key:"test-only"}),{mode:0o600});
    expect(resolveConfig({}, {HOME:dir,CLICKY_BRO_GEMINI_KEY_FILE:file}).geminiApiKey).toBe("test-only");
    expect(resolveConfig({}, {HOME:dir}).geminiApiKey).toBeUndefined();
    fs.rmSync(dir,{recursive:true});
  });
  it.skipIf(process.platform === "win32")("rejects symlinks and public Gemini key files", () => {
    const dir=fs.mkdtempSync(path.join(os.tmpdir(),"clicky-bro-key-test-"));
    const file=path.join(dir,"key.json");fs.writeFileSync(file,'{"api_key":"test-only"}',{mode:0o644});
    expect(()=>resolveConfig({}, {CLICKY_BRO_GEMINI_KEY_FILE:file})).toThrow(/mode 600/);
    fs.chmodSync(file,0o600);const link=path.join(dir,"link");fs.symlinkSync(file,link);
    expect(()=>resolveConfig({}, {CLICKY_BRO_GEMINI_KEY_FILE:link})).toThrow(/regular private file/);
    fs.rmSync(dir,{recursive:true});
  });
  it("applies defaults", () => {
    const c = resolveConfig({}, { HOME: "/home/u" });
    expect(c.backendUrl).toBe("http://127.0.0.1:18787");
    expect(c.codexHome).toBe("/home/u/.clicky-bro/codex-home");
    expect(c.codexBin).toBe("codex");
    expect(c.workspace).toBe(process.cwd());
    expect(c.token).toBeUndefined();
    expect(c.model).toBeUndefined();
    expect(c.verbose).toBe(false);
  });
  it("env then flags win", () => {
    const c = resolveConfig(
      { token: "flag" },
      { HOME: "/h", BACKEND_URL: "http://b:1/", CLICKY_BRO_TOKEN: "env", CLICKY_BRO_WORKSPACE: "/ws", CLICKY_BRO_MODEL: "m" },
    );
    expect(c.backendUrl).toBe("http://b:1");
    expect(c.token).toBe("flag");
    expect(c.workspace).toBe("/ws");
    expect(c.model).toBe("m");
  });
  it("repoRoot points at the directory holding skills/ and config/", () => {
    const root = repoRoot();
    expect(fs.existsSync(path.join(root, "skills", "ModelInstructions.md"))).toBe(true);
    expect(fs.existsSync(path.join(root, "config", "codex-config.toml"))).toBe(true);
  });

  describe("runTimeoutMs", () => {
    it("defaults to 10 minutes", () => {
      expect(resolveConfig({}, { HOME: "/home/u" }).runTimeoutMs).toBe(10 * 60 * 1000);
    });
    it("takes an override from the env", () => {
      expect(resolveConfig({}, { HOME: "/home/u", CLICKY_BRO_RUN_TIMEOUT_MS: "5000" }).runTimeoutMs).toBe(5000);
    });
    it("ignores a non-positive env value and falls back to the default", () => {
      expect(resolveConfig({}, { HOME: "/home/u", CLICKY_BRO_RUN_TIMEOUT_MS: "not-a-number" }).runTimeoutMs).toBe(10 * 60 * 1000);
      expect(resolveConfig({}, { HOME: "/home/u", CLICKY_BRO_RUN_TIMEOUT_MS: "0" }).runTimeoutMs).toBe(10 * 60 * 1000);
    });
    it("lets a flag win over the env", () => {
      expect(resolveConfig({ runTimeoutMs: 42 }, { HOME: "/home/u", CLICKY_BRO_RUN_TIMEOUT_MS: "5000" }).runTimeoutMs).toBe(42);
    });
  });
});
