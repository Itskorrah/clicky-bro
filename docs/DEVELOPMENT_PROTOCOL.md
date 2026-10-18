# Development environment and engineering protocol

Research date: 17 October 2026. This is a proposed implementation protocol, with the research tools' observed status recorded separately. No product framework, global skill installation, account configuration, paid inference or product implementation was added in this investigation.

## Recommendation

Use Codex as the development coordinator, Evolve's evidence and verification workflow as the engineering backbone, Context Mode for large research/build output, and REA for specific questions about shipped artifacts. Adapt Replica's feature inventory and comparison templates; do not run its whole web deployment pipeline for a desktop assistant. More agent frameworks and MCP servers would add maintenance before they solve an observed problem.

For the product, investigate Tauri 2 + TypeScript + a Rust core with small native platform adapters. Make the final framework decision only after a macOS/Windows feasibility prototype proves overlay behavior, capture, shortcuts, text insertion, accessibility and packaging. Electron remains a credible alternative if native WebView behavior or development effort defeats that prototype. SwiftUI remains a good macOS-only choice but does not supply a Windows implementation.

## Exact source snapshots reviewed

The research clones live under `.local/research/tooling/` and are excluded from Git through the existing `.local/` rule. Revisions were obtained from each local clone's Git HEAD, rather than inferred from a README date.

| Repository | Exact revision | Root license / version | Recommendation |
| --- | --- | --- | --- |
| [Itskorrah/evolve](https://github.com/Itskorrah/evolve/tree/89e0b5d39746cfc0503436d1335497a6a2e84d0f) | `89e0b5d39746cfc0503436d1335497a6a2e84d0f` | MIT | Adopt its coordinator, scoped implementation and independent verification methods. Install project-scoped only after implementation is authorized. |
| [Itskorrah/replica-skill-universal](https://github.com/Itskorrah/replica-skill-universal/tree/53b6ccf9a14617fefecdc76ae52e8745914cc6e5) | `53b6ccf9a14617fefecdc76ae52e8745914cc6e5` | MIT | Adapt reconnaissance, parity matrix, original branding and comparison templates. Skip unmodified stack/deployment orchestration. |
| [mksglu/context-mode](https://github.com/mksglu/context-mode/tree/5f6298a9bdc480ebc7c88a29c9fbdf38ae2f8cb6) | `5f6298a9bdc480ebc7c88a29c9fbdf38ae2f8cb6` | Elastic License 2.0; `1.0.169` | Keep as a development tool. Its license and execution model differ from the MIT tools. Do not assume it can be turned into a hosted commercial feature. |
| [morluto/rea](https://github.com/morluto/rea/tree/4a076f368c62bdfb19415accad342e03a38d1005) | `4a076f368c62bdfb19415accad342e03a38d1005` | MIT; `6.5.0` | Keep for bounded artifact/native investigation. It is a research tool, not the product's agent runtime. |

### Evolve: useful engineering structure, not a quality guarantee

The actual [coordinator skill](https://github.com/Itskorrah/evolve/blob/89e0b5d39746cfc0503436d1335497a6a2e84d0f/skills/evolve/SKILL.md), build/verify skills, [coordination reference](https://github.com/Itskorrah/evolve/blob/89e0b5d39746cfc0503436d1335497a6a2e84d0f/skills/evolve/references/coordination.md), helper code and tests were inspected. Useful concrete properties:

- Each selected problem needs a trigger, evidence, impact, acceptance checks and a bounded scope.
- The helper records a source fingerprint, including executable modes and initialized submodule state, so passing checks cannot silently be carried across changed source.
- `common.py:167` executes an explicit argument vector without shell evaluation, bounds retained combined output to 512 KiB and handles timeout process-tree cleanup. The ledger also has locking and stale-evidence tests.
- Parallel work has ownership rules and independent review; separate conversations do not isolate shared files.

Fresh local verification in this investigation: `scripts/validate.py` returned `valid: true`; `python3 -W error::ResourceWarning -m unittest discover -s tests -v` passed **60 tests**. This ran in Context Mode's Python **3.12.4** environment. Logs are `.local/research/tooling/evolve/research-validate.log` and `research-tests.log`. The project supports Python 3.10+; the laptop login shell's `/usr/bin/python3` is 3.9.6 and must not be used blindly for these helpers. No Windows run was performed here, and tests of a ledger do not prove that a product behaves correctly.

Its main limitation is overhead and false confidence if every small change becomes a large audit cycle. Use the full ledger for milestones and substantial changes; use focused checks for small reversible edits. Evidence structure cannot judge whether the acceptance criteria are adequate.

### Replica: reuse its methods selectively

The actual [recon skill, lines 49–64](https://github.com/Itskorrah/replica-skill-universal/blob/53b6ccf9a14617fefecdc76ae52e8745914cc6e5/replica-recon/SKILL.md#L49-L64) expressly forbids reading app source, decompiling binaries and copying private endpoints. The user has explicitly requested REA artifact investigation here, and supplied a public source repository; that research scope takes precedence over this optional skill workflow. We therefore evaluated Replica as material to adapt, rather than invoking its original reconnaissance workflow and claiming compliance with its clean-room method.

Its [architect skill, lines 44–63](https://github.com/Itskorrah/replica-skill-universal/blob/53b6ccf9a14617fefecdc76ae52e8745914cc6e5/replica-architect/SKILL.md#L44-L63) defaults to Next.js, hosted Postgres, managed auth, Stripe and Vercel. Those are reasonable web defaults, but do not address native desktop capture, focus, OS permissions, installers or local scheduling. The test/deploy skills also emphasize browser and hosted application paths.

Keep its explicit feature inventory, skip reasons, observable workflows, source attribution, original branding and state-by-state comparison. Write desktop-specific acceptance checks. Do not install all eleven skills just to duplicate Evolve's coordinator or let a web default choose the product architecture.

### Context Mode: connected tools are useful; hooks need separate proof

The actual `src/executor.ts`, `src/adapters/codex/hooks.ts`, `src/adapters/codex/index.ts`, package metadata and license were inspected. Its Node requirement is **22.5+**. The installed copy and reviewed source both identify as **1.0.169**.

Live `ctx_execute` successfully cloned/read the research repositories, filtered large output and ran Evolve's checks during this investigation. That proves tool reachability and execution. It does not establish that SessionStart, PreCompact or other hooks fired in this chat.

The [Codex hook adapter](https://github.com/mksglu/context-mode/blob/5f6298a9bdc480ebc7c88a29c9fbdf38ae2f8cb6/src/adapters/codex/hooks.ts#L1-L23) documents runtime-gated PreCompact support, input rewrites requiring sufficiently recent Codex, unsupported `ask` and post-tool output rewriting, and an upstream failing-shell hook limitation. Verify native hook discovery/trust and a real lifecycle event after deliberate setup. A doctor heuristic alone should not cause a reinstall or settings rewrite.

The executor creates subprocesses and temporary working directories; that is useful output containment, not a claim of a complete OS security boundary. Tool execution can access host resources available to its process. Retain explicit project paths, host permissions, redacted fixtures and task-owned process cleanup. Context Mode's subprocess PATH also differed from the login shell during this investigation: bare `node` was unavailable inside the subprocess although `/Users/korrah/.local/bin/node` works in the login shell. A project tool wrapper must set deliberate runtime paths rather than assume all tools share one environment.

The [Elastic 2.0 license](https://github.com/mksglu/context-mode/blob/5f6298a9bdc480ebc7c88a29c9fbdf38ae2f8cb6/LICENSE#L10-L31) includes a restriction on offering substantial functionality as a hosted/managed service, plus license-key and notice restrictions. Using it to develop this app is distinct from embedding or reselling it as a customer-facing service.

### REA: evidence for implementation decisions

The actual [skill](https://github.com/morluto/rea/blob/4a076f368c62bdfb19415accad342e03a38d1005/.agents/skills/reverse-engineer-anything/SKILL.md), installation documentation, package metadata and [third-party license documentation](https://github.com/morluto/rea/blob/4a076f368c62bdfb19415accad342e03a38d1005/licenses/README.md) were inspected. REA supports multiple artifact types and providers; it is not necessary for ordinary public source browsing. Its package supports Node `^22.19.0 || ^24.11.0 || >=26.0.0`.

The existing setup uses REA 6.5.0, Ghidra 12.1.4, JDK 21 and a native ARM64 decompiler. The independently successful 24-byte native smoke test and the incomplete whole-executable import are documented in `REA_SETUP.md`. Do not equate the smoke test with whole-app decompilation or repeat the unchanged timed-out import. Scope each further query to a concrete unknown and preserve the byte/artifact identity, address, provider settings and limits.

No need to copy Ghidra, REA or HeyClicky's packaged helper into the shipped product. If any toolchain components are ever redistributed, inventory the actual component licenses/NOTICE files rather than applying REA's root MIT license to every embedded third-party binary.

## Current laptop and proposed setup

Observed locally: Apple Silicon macOS **26.5**, **8 GiB** physical RAM (`hw.memsize=8589934592`), Xcode **26.6**, Node **24.21.0** at `/Users/korrah/.local/bin/node`. `rustc` and `cargo` were not discoverable in the login-shell PATH. This is not proof that no copy exists elsewhere. Context Mode provides Python 3.12.4; login-shell Python is 3.9.6.

Keep local development on this laptop. Codex model inference and online providers still use remote services; local repository/build execution does not mean offline inference. Windows build/test hosts can be local physical hardware or a deliberately configured VM; shared CI is optional validation, rather than the main development environment.

| Layer | Proposed setup after build approval | Why |
| --- | --- | --- |
| Source | One Git repository, short `AGENTS.md`, task branches/worktrees only when useful | Preserve existing work and reduce conflicting edits. |
| Runtime pins | `rust-toolchain.toml`, Cargo lockfile, Node version file, one JS package manager and lockfile; Python 3.10+ explicit path for Evolve | Reproducible tool choice across shell, MCP and Windows. |
| Project skills | Pinned Evolve coordinator/build/verify; adapted desktop parity checklist; existing REA and Context Mode reused | Keep tool responsibilities clear and eliminate duplicate orchestration. |
| App candidate | Tauri 2, Vite + TypeScript UI, Rust application core, SQLite | Shared desktop core with native capability adapters; no web hosting dependency for the initial local app. |
| Native adapters | Swift/AppKit/ScreenCaptureKit on macOS; Win32/WinRT/UI Automation on Windows | Native OS behavior must be explicitly implemented and tested. |
| Test tools | Rust unit/integration tests, focused UI/component tests, desktop E2E harness plus native permission tests | Test user-visible outcomes through real process and OS boundaries. |
| Diagnostics | Structured local logs, run IDs, redacted event traces; OpenTelemetry only once useful | Debug runs without recording private transcripts/screenshots by default. |

On an 8 GiB laptop, run one expensive native analysis, large Rust build or local transcription benchmark at a time. Start with one coordinator and at most two workers for independent source/docs work. Cap Ghidra Java heap as already configured, but remember native memory is additional. Avoid Docker, a Windows VM, a local large speech model and a whole-program decompiler running together. Benchmark resource usage before promising always-on local AI.

## Additional tools worth considering

These are alternatives evaluated from primary documentation, not an installation shopping list.

| Candidate | Decision and reason | Primary evidence |
| --- | --- | --- |
| Official Codex app-server | Strong runtime candidate if the product wants an embedded Codex experience. It exposes auth, threads/history, approvals and streamed events; pin the protocol/runtime and isolate its user data from the developer's Codex installation. Keep it behind an `AgentRuntime` interface. | [App-server documentation](https://learn.chatgpt.com/docs/app-server) |
| Official Codex SDK | Good for scripts/engineering automation; use app-server for a rich custom conversation/approval client. Do not add both layers without a reason. | [SDK documentation](https://learn.chatgpt.com/docs/codex-sdk) |
| Tauri 2 | Preferred feasibility candidate: system WebViews, a Rust core and command capabilities. Capabilities must explicitly constrain app commands; custom commands are not magically least-privilege. Prove overlay and OS integration before committing. | [Capabilities](https://v2.tauri.app/security/capabilities/), [current releases](https://v2.tauri.app/release/) |
| Electron | Fallback worth a measured prototype if a consistent browser renderer or mature desktop tooling saves significant effort. Use sandboxed/context-isolated renderers, narrow IPC and no Node integration in untrusted content. Compare memory/startup with Tauri on this laptop. | [Electron security guide](https://www.electronjs.org/docs/latest/tutorial/security) |
| WebdriverIO Tauri service | Prefer investigating this for real desktop WebView E2E. Current docs describe an embedded driver supporting macOS, Windows and Linux. Build-time test plugins must be absent from release builds. Native capture/accessibility still needs independent tests. | [Tauri WebDriver guide](https://v2.tauri.app/develop/tests/webdriver/), [WebdriverIO Tauri](https://webdriver.io/docs/desktop-testing/tauri) |
| Playwright | Useful for browser integrations and renderer-only tests. A browser run with mocked native IPC cannot establish native desktop behavior. Add when a real browser flow needs it. | [Tauri testing boundaries](https://tauri.app/develop/tests/) |
| whisper.cpp | Credible optional local transcription path, including Apple Silicon support. Benchmark a small quantized model, memory, accents, silence/noise and streaming latency before including it. Review the specific model's license separately. | [Upstream README](https://github.com/ggml-org/whisper.cpp/blob/master/README.md) |
| OpenTelemetry | Good vendor-neutral traces/metrics once cross-process diagnosis becomes difficult; begin with local redacted events and no transcript payloads. | [Project documentation](https://opentelemetry.io/docs/what-is-opentelemetry/) |
| CrewAI/AutoGen/LangGraph-style extra orchestration | Defer. Native Codex agents already provide development delegation; the product first needs a durable single-run state machine, cancellation and permissions. Add another framework only for a demonstrated runtime requirement. | Engineering recommendation; no comparative benchmark claimed. |

Open-source runtime code and access to hosted inference are separate dependencies. An Apache/MIT license does not grant a subscription, model entitlement, permission to share developer credentials, or commercial distribution approval for a third party's service. Evaluate supported product authentication and account requirements before choosing the product's billing model. The initial feasibility work can use recorded/fake provider events without spending on live inference.

## Agent responsibilities and economical model choices

These are roles that can share one agent on small tasks. They are not five permanently running agents.

| Role | Bounded responsibility | Starting model/effort recommendation |
| --- | --- | --- |
| Coordinator / architect | Acceptance criteria, contracts, unresolved risks, integration decisions | GPT-6.1 Sol **High** for this architecture/investigation; **Medium** for routine scoped planning. |
| Researcher | A named subsystem or source set; return exact evidence and unknowns | GPT-6 Luna **High** for extraction; GPT-6.1 Sol **High** when native interpretation or tradeoffs matter. |
| Implementer | One scoped behavior or owned package with real acceptance checks | GPT-6.1 Sol **Medium**, increasing to **High** for multi-process, security or native concurrency work. |
| Independent reviewer | Raw criteria, source/diff and artifacts; challenge implementation and missing tests | GPT-6.1 Sol **High** for substantial changes. A different chat/prompt is independence of perspective, not a guarantee. |
| Release verifier | Reproducible platform build, installer and upgrade outcomes | GPT-6.1 Sol **Medium/High**, depending on the failure or platform complexity. |

Escalate an unresolved difficult design/native failure to GPT-6 Astra at its lowest supported reasoning setting with the failing evidence and a focused question; move higher only when the result warrants it. Where the UI labels this **Light**, the configuration/tool value is `low`; Medium maps to `medium` and High to `high`. Do not send `reasoning_effort: "light"` to a tool that accepts `low`. Do not default to Max/Ultra for every task. Current official documentation recommends GPT-6.1 Sol for complex coding at lower cost than Astra, Luna for focused work, and says higher effort consumes more time/tokens. The task-specific efforts above are our proposed operating choices, not benchmark results. [Official models](https://learn.chatgpt.com/docs/models), [official subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Model availability depends on the user's account, plan, client and workspace. Keep current settings unless the user requests a change; select a supported visible model. Subagents inherit the parent's model and effort unless explicitly configured; an instruction saying “use Luna” is not evidence that a running worker changed model. Before each milestone, explain the proposed model/effort and why. Do not spend on API inference or create scheduled runs as an incidental part of a local test.

### Coordination contract

1. The coordinator writes the concrete goal, evidence sources, owned files, dependencies, non-goals and “done when” criteria.
2. Read-only research can run in parallel. Overlapping implementation is serialized or uses separate worktrees. Share contracts first; one owner integrates.
3. Each worker returns source revisions, exact evidence locations, commands/results, confidence and remaining unknowns. It must distinguish advertisement, bundled instructions, static code and runtime observation.
4. One process owns the ledger. Snapshot source before verification; do not record a passing check against source changed during that check.
5. The reviewer receives the criteria and raw artifacts rather than a request to confirm success. Resolve material findings, then run only the checks affected by subsequent edits.
6. A final report states what changed, the observed result, what was tested and any material unverified boundary. New paid integrations, publication and real external side effects remain deliberate steps in the authorized scope.

## Definition of done and tests

Track each parity feature with: reference behavior, evidence class/version, implementation state, macOS acceptance, Windows acceptance, failure/cancellation handling and remaining unknowns. “Implemented”, “mock-tested”, “live-provider verified”, “OS verified” and “release verified” are separate states.

| Layer | Required evidence |
| --- | --- |
| Pure core | State transitions, command-policy decisions, schema validation, migration rollback, scheduler time/DST logic, cancellation and idempotency. Test outcomes rather than private helper structure. |
| Runtime transport | A controlled child process, real JSON-RPC framing, streamed event handling, approval request/response, disconnect, retry, cancellation and orphan-process cleanup. Recorded/fake model events are labeled as such. |
| Storage | Restart/resume, migration from previous fixtures, corrupted-record recovery, export/delete and secret redaction. Use synthetic conversations. |
| UI | User tasks across empty/loading/streaming/error/denied states, keyboard/focus behavior, accessible names, high contrast/text scaling and same-state screenshots. |
| Native adapter | Real OS permission grant/deny/revoke, focus restoration, multi-monitor scaling, display rearrangement, capture stop, microphone changes, hotkey conflicts and failed text insertion. |
| Agent execution | Approved and denied filesystem/command/network actions, untrusted page/document instructions, user stop, tool loops and maximum duration/cost. No model can self-grant OS or product permissions. |
| Integration | Dedicated sandbox/test accounts and user-approved live actions; OAuth connect/revoke/refresh, multiple accounts, duplicate-event prevention and expired credentials. Fixture tests do not establish a real integration. |
| Release | Signed installer, fresh install, upgrade retaining settings, uninstall, updater rejection of tampering, offline launch, crash recovery and telemetry defaults on every supported platform. |

The current Tauri docs have an important distinction: direct `tauri-driver` supports Windows/Linux, while the current WebdriverIO embedded route supports macOS too. Neither route proves operating-system capture or global desktop automation merely by interacting with a WebView. Do not repeat the outdated blanket statement that all Tauri macOS E2E is unavailable. [Current official guide](https://v2.tauri.app/develop/tests/webdriver/).

Set performance targets after measuring a reproducible baseline. Record machine, release/debug build, screen count/scaling, audio device, warm/cold state, model/provider and run count. Useful metrics are shortcut-to-panel latency, voice-to-final-transcript latency, first useful agent event, tool success/correction rate, idle/active RAM and CPU, battery impact and per-completed-task inference cost. Report measured percentiles and failures; do not make numerical “better than Clicky” claims without an equivalent test.

### Windows acceptance is a real milestone

Use a supported Windows 11 machine or VM with an interactive desktop, native build tools and WebView2; avoid treating WSL as a substitute for Windows desktop behavior. Initially target Windows x64; Windows ARM64 needs its own architecture/runtime decision and test matrix.

Prove the vertical slice on Windows early: global hotkey opens a non-disruptive overlay; selected-window capture succeeds with the expected user permission; a controlled transcript enters a disposable target app; a bounded agent action runs with approval; stop cancels it; state resumes after restart. Microsoft documents Windows Graphics Capture's system-picker and capture UX, which is a different platform contract from ScreenCaptureKit. [Microsoft capture documentation](https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture).

Test mixed DPI monitors, Unicode/IME text, elevated versus ordinary targets, protected windows, locked session, sleep/resume, headset changes, autostart, update and installer trust. Do not promise universal control of secure-desktop or higher-privilege applications. A Windows compile or headless CI pass is useful build evidence but not interactive hardware acceptance. This investigation did not run Windows.

## Recommended next implementation sequence

1. Approve the architecture risks and parity inventory, then record short project instructions and pinned environment commands. Install only missing project tools with rollback paths.
2. Build the thin native feasibility slice on macOS and Windows using recorded/fake agent events; make the framework decision from that evidence.
3. Deliver one useful end-to-end workflow: invoke → voice/text + selected screen context → proposed action → approval → execution → visible result → cancel/recover.
4. Add durable agent sessions, memory controls and routines; then authenticated integrations and file artifacts, each with meaningful end-to-end acceptance.
5. Improve measured weaknesses: transparent memory, precise screen sharing, explicit action scopes, reliable cancellation, resumable work and cost controls.
6. Complete installer/update, accessibility, privacy and real-platform acceptance before release claims. Run targeted independent product review at milestones rather than continuously expanding the tool stack.

The environment can make good work reproducible and reviewable. It cannot make “everything perfect” or verify undisclosed behavior in a commercial app without further observable evidence.
