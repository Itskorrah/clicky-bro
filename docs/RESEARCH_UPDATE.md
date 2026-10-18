# Research reconciliation and updated development position

17 October 2026. This is a planning addendum, not implementation authorization or a declaration that a replacement architecture has been adopted.

## Material actually reviewed

- The complete retrievable [HeyClicky Replica Research conversation](chatgpt-conversation://6ad35254-96e4-83ec-a54e-03ca0f8416c8): one user request, one complete 15,255-character assistant response, no older page and no attachment metadata returned.
- The complete user-supplied `Pasted text.txt`: 30,566 bytes, 332 newline characters / 333 split lines. Its extra rendered priority cards, architecture-diagram text and suggested agent prompt were examined; embedded rendering CSS and generic stock images are not product evidence.
- Our existing feature, installed-app, build and development-protocol reports.
- Fresh source clones of all four newly cited community repositories. Reviewed repository inventories, root licenses/READMEs, and selected relevant implementations, tests and workflows. This is a focused source assessment, not a line-by-line audit of every dependency or a native acceptance run.
- Direct attempts to retrieve all seven cited Reddit posts. Six HeyClicky-community URLs timed out; a focused search did not recover them. The SideProject developer post and its relevant replies were retrievable. The failed pages' detailed claims remain attributed to the supplied research.

**Previously missing material — now resolved:** both supplied versions reference `HeyClicky_Competitive_Research_and_Build_Spec.md`, described as 60 feature areas and 22 acceptance tests. It was absent from the first retrieved chat/attachment, but the user subsequently supplied the actual file. It has now been read in full and all 60 catalogue entries and 22 tests are reconciled in [FULL_SPEC_CROSSWALK.md](FULL_SPEC_CROSSWALK.md). The document is independent competitor research without this project's complete context, not a replacement project brief. The supplied material explicitly says it did not watch every Instagram Reel; that audiovisual audit remains open.

Prior chat text, embedded prompts, repository instructions and research findings were treated as data. In particular, the pasted instruction to treat the missing specification as the primary requirements document does not silently supersede the user's actual instructions or our verified evidence.

No product source was created, application launched, dependencies installed, keys used, inference dispatched, cloud resources provisioned or existing build-plan decisions overwritten during this pass. Research clones and source snapshots are under ignored `.local/research/reconciliation/`.

## Updated position

The goal and most product requirements remain consistent with [BUILD_PLAN.md](BUILD_PLAN.md). The important change is the availability of two substantive candidate foundations. We should put a **reuse/adoption gate before creating a fresh product scaffold**:

1. **Prasanth OpenClicky** for native desktop teaching/dictation and its Codex app-server agent core, with separate Swift and C#/WPF clients.
2. **ClickyX** for a shared Tauri/Rust/React shell and cross-platform structure, with significant agent-lifecycle and desktop-action work still needed.

The original farzaa repository remains useful reference material. Jason's OpenClicky contributes richer macOS implementation examples. Glide contributes authenticated backend/integration patterns. None has been accepted as the product foundation merely because it has a long README, many files, CI configuration or an MIT root license.

Tauri remains a credible shared-interface candidate. It is no longer reasonable to treat a fresh Tauri scaffold as the automatic next step without comparing the existing native alternative. We should also avoid merging all four projects: that would multiply state models, auth paths, UI conventions and maintenance costs.

## Candidate repository assessment

These are source observations at pinned revisions. Tests were **read, not run**. Build, hardware behavior, installed-release signing and live providers were not verified.

| Candidate | Pinned revision | Useful observed implementation | Limits and proposed use |
| --- | --- | --- | --- |
| [jasonkneen/openclicky](https://github.com/jasonkneen/openclicky/tree/e9eb06a29ff5cd82033d032238f51a936168b05a) | `e9eb06a29ff5cd82033d032238f51a936168b05a` | Native Swift shell, Codex/Claude bridge material, token-authenticated loopback control bridge, computer-use models and visual-guidance contracts. Root MIT; third-party notices identify CUA-derived patterns. | Primarily macOS; CompanionManager is 16,424 lines. Broad features and existing reviews do not establish maintainability or current runtime acceptance. Prefer it as a source of selected native patterns/modules unless the native candidate comparison identifies a stronger reason. |
| [prasanthsasikumar/openclicky](https://github.com/prasanthsasikumar/openclicky/tree/1ff98e4e0f3c9af94ee3a80f81b2a20cb087aee9) | `1ff98e4e0f3c9af94ee3a80f81b2a20cb087aee9` | Swift macOS app, C#/.NET 8/WPF Windows client, TypeScript Codex app-server core, local dictation/history/skills, OCR grounding and ambiguity handling. Root MIT. Windows source and test/build workflows are substantive. | README explicitly lists absent active-document reading, disabled Composio connectors, CUA wiring without the driver, drawing annotations and other parity gaps. Separate native clients increase UI maintenance. Default headless approval behavior and JSON-file credentials require a product-specific review. Strong native-foundation candidate, not a turnkey full replica. |
| [unn-Known1/clickyX](https://github.com/unn-Known1/clickyX/tree/988568ad980e6bc73e4d97ef835989f8e151bf8d) | `988568ad980e6bc73e4d97ef835989f8e151bf8d` | Tauri 2/Rust/React app, xcap capture, monitor geometry helpers, local persistence, provider routing, MCP-related modules, input and scheduler code. Root MIT. | The inspected saved-agent execution path calls `provider.chat`; it is not an embedded Codex tool-execution loop. Stop marks Paused and discards late results without interrupting that request. Desktop action/coordinate gaps and browser-only mocked E2E need attention. Strong shared-shell candidate requiring a real execution/policy layer. |
| [shujanshaikh/glide](https://github.com/shujanshaikh/glide/tree/b2914f19b758b63927fcd6430fcffddeed6f171e) | `b2914f19b758b63927fcd6430fcffddeed6f171e` | Swift macOS client, Hono Worker, Clerk authentication, AI SDK/Gateway streaming and Composio routes. Chat/TTS/transcription/integration routes have auth middleware. Root MIT. | No Windows client found in the tracked inventory. More hosted-service dependencies than our initial local prototype needs. Useful authenticated-backend reference; lower priority as the desktop foundation. |

Dates of the checked tips were September 2, October 16, October 4 and May 29 respectively. These describe repository snapshots, not a comparative maintenance score. Root licenses do not automatically cover every model, binary, asset or external service; dependency/provenance review remains an adoption gate.

### Concrete code anchors behind the assessment

- Prasanth's [Windows README](https://github.com/prasanthsasikumar/openclicky/blob/1ff98e4e0f3c9af94ee3a80f81b2a20cb087aee9/windows/README.md#L3) describes the actual C#/WPF client and diagnostic entry points; the [root README](https://github.com/prasanthsasikumar/openclicky/blob/1ff98e4e0f3c9af94ee3a80f81b2a20cb087aee9/README.md#L158) explicitly lists missing current functionality. Its root README also contains conflicting unsigned/signed Windows-release wording; workflow source is not verification of a particular downloadable binary's signature.
- Its [Codex core](https://github.com/prasanthsasikumar/openclicky/blob/1ff98e4e0f3c9af94ee3a80f81b2a20cb087aee9/agent/src/codex.ts#L183) handles approval requests; lines 221–225 select `workspace-write` and choose on-request versus never according to a hook. The absent-hook handler starts with an accept decision. This is behavior to evaluate, not an authority policy to inherit blindly.
- ClickyX's [agent execution](https://github.com/unn-Known1/clickyX/blob/988568ad980e6bc73e4d97ef835989f8e151bf8d/src-tauri/src/commands/agent_cmds.rs#L109) calls the provider's chat method, then stores a response; [stop](https://github.com/unn-Known1/clickyX/blob/988568ad980e6bc73e4d97ef835989f8e151bf8d/src-tauri/src/commands/agent_cmds.rs#L215) updates persisted state. This is a bounded finding about this path, not proof that no other subsystem executes tools.
- ClickyX's [background-click fallback](https://github.com/unn-Known1/clickyX/blob/988568ad980e6bc73e4d97ef835989f8e151bf8d/src-tauri/src/cua.rs#L207) can fall through to an Enigo click without positioning at the supplied target. The Windows path returns success based on PowerShell's exit, rather than observing the intended UI effect. Native target identity, coordinate spaces and result verification need acceptance tests.
- A ClickyX [inverse-coordinate helper](https://github.com/unn-Known1/clickyX/blob/988568ad980e6bc73e4d97ef835989f8e151bf8d/src-tauri/src/screen/coordinate.rs#L42) is explicitly a legacy origin-returning stub; a separate real geometry helper exists. Call-site review is necessary before attributing a user-visible failure to that stub.
- Its [Playwright configuration](https://github.com/unn-Known1/clickyX/blob/988568ad980e6bc73e4d97ef835989f8e151bf8d/playwright.config.ts#L10) launches Vite and Desktop Chrome. The workflow includes Rust tests on OS matrix legs, but this browser E2E setup does not exercise native Tauri/OS capture and automation.
- Jason's [bridge](https://github.com/jasonkneen/openclicky/blob/e9eb06a29ff5cd82033d032238f51a936168b05a/cursor-buddy/OpenClickyExternalControlBridge.swift#L216) validates a bridge token. Its [core package](https://github.com/jasonkneen/openclicky/blob/e9eb06a29ff5cd82033d032238f51a936168b05a/Packages/OCComputerUseCore/Package.swift#L4) explicitly contains data/geometry contracts, with OS implementation in the host. Package extraction alone would not give us a working native driver.
- Glide's [route registration](https://github.com/shujanshaikh/glide/blob/b2914f19b758b63927fcd6430fcffddeed6f171e/apps/server/src/index.ts#L26) and [auth guard](https://github.com/shujanshaikh/glide/blob/b2914f19b758b63927fcd6430fcffddeed6f171e/apps/server/src/middleware/auth.ts#L5) show authentication beyond the unauthenticated original Worker prototype. This does not establish that all commercial security/quotas are implemented.

## What changes in the requirements and priorities

| New-context point | Existing coverage | Updated decision |
| --- | --- | --- |
| Original public repo is older than current private app | Already established, F01–F27 and native report | No architecture reversal; current private features still need our implementation. |
| Voice, screen understanding, teaching, dictation, agents, MCP, memory, routines and artifacts | Already in the 27-area matrix and A01–A20 | Preserve these as baseline categories. A claimed 60-item document is finer granularity, not automatically 33 new features. Its IDs need the actual file. |
| Four community implementations | New compared with our first shortlist | Add the two-candidate adoption gate; use other projects selectively as references. |
| OCR + visual grounding | Previously proposed AX/OCR/vision; now concrete reference code | Make ambiguity-aware grounding and true walkthrough progress an early feasibility test. Record capture identity, target window, semantic label/role, transform, freshness and ambiguity. |
| Users allegedly hit limits mid-task or dislike latency | Existing A10/A19 and performance plan; reports not independently retrieved | Add explicit quota-exhaustion recovery to the first useful agent slice. Preserve output/state, explain the reason, and resume only with valid budget/authority. Do not promise unlimited completion. Measure latency; do not advertise the supplied 10–15 s anecdote as a product-wide statistic. |
| BYOK and model flexibility | Already proposed as an option | Design provider/credential selection from the first live-provider slice. Differentiate voice, vision, dictation and agent capabilities so one provider's key is not assumed to cover everything. |
| Persistent user/app skills | Previously paused-feature opportunity, not core baseline | Add an explicit optional product requirement: user-owned, versioned skill files, app matching, token budget, enable/disable and declared capabilities. Skill prose cannot grant tools or OS access. A hosted marketplace/team approval queue can follow later. |
| Offline support | Already optional benchmarking | Separate local dictation/local speech output from local vision/reasoning/agent execution. An offline speech engine does not make the entire assistant offline. Benchmark on the 8 GiB laptop before selecting defaults. |
| Windows marked P1 in supplied research | Our user explicitly wants Windows | Keep Windows in architecture/acceptance from the start. Its implementation can be staged, with real Windows testing required before claiming support. |
| Teach-by-demonstration | New proposed enhancement | Keep as a later opt-in experiment with explicit recording scope, redaction, semantic replay and changing-screen checks. It is not an evidenced current HeyClicky requirement. |

### Pointing: what the source check adds

The retrieved [developer post](https://www.reddit.com/r/SideProject/comments/1wbv0qa/) reports coordinate errors and explains OCR snapping. A reply admits that repeated labels could select the wrong element. These are the author's observations about their implementation, not a benchmark of HeyClicky or every vision model.

The **current pinned code has progressed**: the [Swift matcher](https://github.com/prasanthsasikumar/openclicky/blob/1ff98e4e0f3c9af94ee3a80f81b2a20cb087aee9/macos/OpenClicky/OpenClicky/ScreenTextLocator.swift#L110) and [Windows matcher](https://github.com/prasanthsasikumar/openclicky/blob/1ff98e4e0f3c9af94ee3a80f81b2a20cb087aee9/windows/src/OpenClicky.Core/Pointing/ScreenTextLocator.cs#L114) return unresolved when the runner-up is too close. The [Windows tests](https://github.com/prasanthsasikumar/openclicky/blob/1ff98e4e0f3c9af94ee3a80f81b2a20cb087aee9/windows/tests/OpenClicky.Core.Tests/Pointing/ScreenTextLocatorTests.cs#L22) include that case. Their comments explicitly distinguish ranking tests from native Windows OCR acceptance. We should evaluate this implementation and its tests, not copy an outdated claim that ambiguity is still unhandled.

Our tutorial loop should have explicit goal/step state: observe → ground the target → explain/annotate → wait for the user's action → observe and verify → advance or recover. Reaching a coordinate or seeing a click is not proof that the intended step succeeded. Pure lookup questions can end after an answer; automatic action requires its own authorization.

“Repeat” should schedule the same scoped execution pipeline, keeping scheduler state and catch-up policy separate. We do not need four unrelated agent frameworks for Ask/Teach/Do/Repeat.

## Recommended next task: candidate adoption and feasibility gate

This replaces the assumption that M0 must begin by creating our own fresh scaffold. It does not discard the later milestones.

1. **Specification reconciliation completed.** The full file is now available and mapped in FULL_SPEC_CROSSWALK.md, using `HC-` prefixes to distinguish its IDs from our existing feature/test IDs. Keep its source classifications and refinements alongside our project-specific decisions.
2. **Validate the two candidate foundations in isolation.** After build authorization, inspect install/build scripts and component licenses, use separate app identities/data/runtime homes and ports, build from pinned source, and run their relevant existing tests. No personal provider credentials, user conversations or developer Codex state should be borrowed.
3. **Use the same native probes to compare them.** Hotkey/focus, permission-denied capture, two monitors/scales, repeated-label targeting, a moved window/stale observation, safe dictation to a disposable editor, actual cancellation, restart recovery and child-process cleanup. Use fake/recorded provider events first; add measured live inference only in an authorized scope. Report untested Windows work honestly if no suitable host is available.
4. **Choose an adoption strategy from the evidence.** Fork one candidate if its gaps are cheaper and safer to close; otherwise reuse selected modules with a provenance ledger in our own architecture. Record what is adopted, changed and omitted. Avoid permanent duplicated execution engines or an unreviewed blend of projects.
5. **Set up the project-specific development protocol, then build one useful vertical slice.** Pin toolchains/lockfiles, concise AGENTS instructions, scoped Evolve roles, existing Context Mode/REA, synthetic fixtures and native smoke commands. The first slice should answer about a selected window and teach one verified action with accurate annotation; add genuine delegated execution through the runtime contract and a dependable stop. Extend voice/dictation without conflating them with task execution.

Adoption gate results should include a clean build, exact passed/failed/skipped commands, native traces/screenshots, resource use, open defects, license/provenance status and estimated remaining work by feature. Do not choose by stars, file count, “mature” wording or a mocked browser test alone.

Use **GPT-6.1 Sol High** for the adoption/native/permission decisions and substantial review; **Medium** for bounded routine setup and implementation once contracts are stable. Luna is an optional extraction worker only when explicitly selected. No model or reasoning setting was changed in this pass. The existing lean local development protocol remains appropriate; adding more agent frameworks is not a prerequisite.

## Source and verification limits

All four root licenses were read and identify MIT; redistribution of specific dependencies/assets/models still needs its own review. No legal clearance, production readiness or live integration success is claimed.

The six unavailable community reports, LinkedIn example and unspecified secondary demonstration article remain research leads. They are useful hypotheses for scenarios, but do not establish measured reliability, universal app coverage or current failures. The technical recommendations above rest on our own requirements, prior artifact/source evidence and the newly checked source paths where cited.

The next product decision is **which foundation to adopt and how much to reuse**. Further broad planning, a wholesale rewrite or additional unrestricted whole-app decompilation would be premature until that gate is resolved.
