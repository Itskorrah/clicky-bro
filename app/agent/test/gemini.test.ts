import { describe, it, expect } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { GeminiAgent, geminiAsk } from "../src/gemini.js";
import { resolveConfig } from "../src/config.js";
function fixture() {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "clicky-bro-gemini-"));
    const cfg = resolveConfig({ workspace: path.join(root, "workspace"), codexHome: path.join(root, "runtime", "codex"), geminiApiKey: "test-only", geminiModel: "gemini-3.5-flash-lite" }, {});
    return { root, cfg };
}
const answer = (parts: unknown[]) => Response.json({ candidates: [{ finishReason: "STOP", content: { role: "model", parts } }] });
describe("native Gemini runtime", () => {
    it.each(["MAX_TOKENS", "SAFETY", "RECITATION", "OTHER", undefined])("never executes tools from incomplete/refused generation %s", async (reason) => {
        const { cfg } = fixture(); let calls = 0; let approvals = 0;
        const agent = new GeminiAgent(cfg, { onApproval: async () => { approvals++; return "accept"; } }, async () => {
            calls++;
            return Response.json({ candidates: [{ finishReason: reason, content: { role: "model", parts: [{ functionCall: { name: "write_file", args: { path: "must-not-exist.txt", content: "bad" } } }] } }] });
        });
        await agent.start(); const result = await agent.run("Write only after a complete valid model response");
        expect(result.status).toBe("failed"); expect(calls).toBe(1); expect(approvals).toBe(0);
        expect(fs.existsSync(path.join(cfg.workspace, "must-not-exist.txt"))).toBe(false);
    });

    it("preserves signatures and call IDs and sends genuine approved write results", async () => {
        const { cfg } = fixture(), requests: any[] = [];
        const modelPart = { thoughtSignature: "opaque-signature", functionCall: { id: "call-1", name: "write_file", args: { path: "hello.txt", content: "hello" } } };
        const agent = new GeminiAgent(cfg, { onApproval: async () => "accept" }, async (_url, init) => {
            requests.push(JSON.parse(init!.body as string));
            return requests.length === 1 ? answer([modelPart]) : answer([{ text: "Saved hello.txt" }]);
        });
        await agent.start();
        const result = await agent.run("Write hello.txt");
        expect(result.status).toBe("completed");
        expect(fs.readFileSync(path.join(cfg.workspace, "hello.txt"), "utf8")).toBe("hello");
        expect(requests[1].contents[1].parts[0]).toEqual(modelPart);
        expect(requests[1].contents[2].parts[0].functionResponse).toMatchObject({ id: "call-1", name: "write_file", response: { bytes: 5 } });
        expect((await agent.readThread(result.threadId)).turns).toHaveLength(1);
    });
    it("denies writes when no approval hook exists", async () => {
        const { cfg } = fixture();
        let calls = 0;
        const requests: any[] = [];
        const agent = new GeminiAgent(cfg, {}, async (_u, init) => { requests.push(JSON.parse(init!.body as string)); return calls++ === 0 ? answer([{ functionCall: { name: "write_file", args: { path: "denied.txt", content: "x" } } }]) : answer([{ text: "Write denied" }]); });
        await agent.start();
        await agent.run("write");
        expect(fs.existsSync(path.join(cfg.workspace, "denied.txt"))).toBe(false);
        expect(requests[1].contents.at(-1).parts[0].functionResponse.response.error).toMatch(/approval required/);
    });
    it("prevents traversal and symlink reads outside the workspace", async () => {
        const { cfg, root } = fixture();
        let calls = 0;
        const requests: any[] = [];
        fs.writeFileSync(path.join(root, "outside"), "secret");
        const agent = new GeminiAgent(cfg, {}, async (_u, init) => { requests.push(JSON.parse(init!.body as string)); return calls++ === 0 ? answer([{ functionCall: { name: "read_file", args: { path: "escape" } } }]) : answer([{ text: "Denied" }]); });
        await agent.start();
        fs.symlinkSync(path.join(root, "outside"), path.join(cfg.workspace, "escape"));
        await agent.run("read");
        expect(requests[1].contents.at(-1).parts[0].functionResponse.response.error).toMatch(/outside/);
    });
    it("stops on quota with saved work and no fallback", async () => {
        const { cfg } = fixture();
        let calls = 0;
        const agent = new GeminiAgent(cfg, {}, async () => { calls++; return new Response("quota", { status: 429 }); });
        await agent.start();
        const result = await agent.run("hello");
        expect(calls).toBe(1);
        expect(result.status).toBe("failed");
        expect(result.error).toMatch(/quota/);
        expect((await agent.readThread(result.threadId)).turns[0].user).toEqual(["hello"]);
    });
    it("aborts an outstanding provider request", async () => {
        const { cfg } = fixture();
        let observed = false;
        const agent = new GeminiAgent(cfg, {}, async (_u, init) => new Promise((_resolve, reject) => { observed = true; init!.signal!.addEventListener("abort", () => reject(new Error("cancelled"))); }));
        await agent.start();
        const pending = agent.run("hello");
        expect(observed).toBe(true);
        await agent.stop();
        expect((await pending).status).toBe("interrupted");
    });
    it("rejects nonallowlisted models before any network access", async () => {
        const { cfg } = fixture();
        cfg.geminiModel = "paid-model";
        const agent = new GeminiAgent(cfg, {}, async () => { throw new Error("must not call"); });
        await expect(agent.start()).rejects.toThrow(/allowlist/);
    });
    it("ask lane sends a screenshot and never declares tools", async () => {
        const { cfg, root } = fixture();
        const image = path.join(root, "image.png");
        fs.writeFileSync(image, Buffer.from([1, 2, 3]));
        let body: any;
        expect(await geminiAsk(cfg, "what is this", { imagePath: image, fetchImpl: async (_u, init) => { body = JSON.parse(init!.body as string); expect(init!.headers).toMatchObject({ "x-goog-api-key": "test-only" }); return answer([{ thought: true, text: "hidden" }, { text: "an image" }]); } })).toBe("an image");
        expect(body.tools).toBeUndefined();
        expect(body.contents[0].parts[1].inlineData.mimeType).toBe("image/png");
    });
});
