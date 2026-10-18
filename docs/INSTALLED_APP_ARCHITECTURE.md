# Installed HeyClicky: architecture and targeted native investigation

Research date: 17 October 2026. Target `/Applications/HeyClicky.app`, version **1.0.53**, build **64**, bundle identifier `com.humansongs.clicky`, packaged build label `cfc4ee64`. This report describes static artifact evidence. The application, its bundled Codex runtime and its computer-use helper were not executed. No account store, token, conversation history or private user database was inspected.

## Conclusion

Current HeyClicky is best explained by a native macOS shell integrating voice/screen interaction with an embedded Codex agent runtime, a supervised computer-use helper, MCP services and remote product services. This is an architectural inference supported by packaging, native instructions and configuration construction; it is not a runtime trace or recovered private source tree.

The public April repository is an earlier implementation. Its Claude/ElevenLabs/AssemblyAI pipeline cannot be assumed to describe this commercial build. The current artifact includes a Codex Responses-provider configuration, realtime voice classes and Deepgram dictation endpoint construction. Provider selection in a particular account or session remains unobserved.

## Evidence classes and local ledger

`OBS` means directly observed bytes, metadata, instructions or resources. `INF` means an interpretation supported by those observations. `UNK` identifies a required fact that static evidence did not establish. Website claims are in [FEATURE_AUDIT.md](FEATURE_AUDIT.md), not silently promoted to runtime observations.

Raw evidence is local-only under `.local/rea/evidence/`; extracted machine-code regions are in `.local/rea/targets/`. The existing `.local/` Git exclusion keeps proprietary bytes, pseudocode and bundled instruction text out of the product repository. The tracked documents contain findings and references, not a reconstructed copy of private implementation code.

| Evidence | Identity / location | What it establishes |
| --- | --- | --- |
| N01 | REA Mach-O parent `ev_17bbba0adbff73a6546abbc32b2780a88f66ba33c182411c905e3db8eba75672`; `main-macho-evidence.json` | ARM64 slice, image layout, dependencies and tool provenance. The summary view is `ev_e44780ad5f42fee231b207e8e81c2877ac66540b56054b5e64b472599def3afb`. |
| N02 | `target-manifest.json`, `resource-manifest.json`, `bundle-observations.json` | Original/copied executable identity and selected resource hashes; packaged runtime/helper/catalog inventory. |
| N03 | `native-reference-survey.json`; `scan_native.py` | A read-only survey of 94,096 LC_FUNCTION_STARTS entries and selected ADRP+ADD references. A function-start partition is a candidate boundary, not proof of complete semantic ownership. |
| N04 | `bounded-region-provenance.json`, `*-llvm.asm`, `*-annotated.asm`, `indirect-symbol-map.json` | Exact source offsets, byte lengths, mapped addresses, LLVM disassembly, adjacent ADRP+ADD literal mappings and indirect stub names. All four selected literal references were checked against the original image. |
| N05 | `runtime-launch-rea.json`; `ev_a9a0e1e75c0dc7c97ad32925c86ddb4ce561f7255e6bb5f4e80c0b3a5e9d8287` | Reconstructed pseudocode for a 1,528-byte region that passes the `app-server` literal through two code paths to another function. |
| N06 | `runtime-config-rea.json`; `ev_f33ee93c07e38e739a040efec9c328118760044f035f8bd45fee7f6426ddd4dc` | Reconstructed configuration construction in a 10,804-byte region, corroborated by original-image literal references. |
| N07 | `dictation-token-rea.json`; `ev_16e854ae0df67e6c7eae716a272727e3d99836f027216529d5af46515b6ecbb6` | A 284-byte region constructs a value using `/v2/dictation/deepgram-token`; it does not itself establish a successful network request. |
| N08 | `computer-use-gate-rea.json`; `ev_4373c7d095f077d05168ed9176498c79d7a5afa18d9348f2ea7d98e52e2b4881` | Reconstructed branches in a 14,300-byte MCP handler region, with original-image references to initialization, tool calls, thread metadata and a refusal response. |
| N09 | `main-strings.txt`, `main-nm.txt`, `helper-strings.txt`, `entitlements.plist` | Bounded string/name candidates, helper linkage and signed entitlement declarations. Strings do not establish execution or complete call paths. |
| N10 | Earlier `whole-app-import-timeout.json`, `entry-byte-provenance.json`, `entry-byte-decompilation.json` | Full import remained incomplete; earlier 24-byte entry test was only a toolchain smoke test. The four larger regions above are new evidence, not a claim that full import now passed. |

Selected ARM64 image SHA-256: `0dd14f802fbc703e68df8604ece2676f873a1165db1d7d85ead3ebc07bfddca1`.

## How the four native regions were investigated

The main image's symbols are largely stripped: the ordinary text symbol inventory is dominated by crash-reporting exports rather than named HeyClicky functions. To avoid another expensive whole-image import, the read-only survey decoded the Mach-O section table and ULEB128 function-start table, located selected embedded strings, and searched ARM64 ADRP+ADD address materialization candidates. LLVM disassembly validated the selected pairs. This is a deliberately narrow analysis, not a general Swift decompiler.

Each chosen region was copied byte-for-byte from the original ARM64 slice and mapped at its original virtual address as a headerless ARM64 analysis carrier. REA/Ghidra 12.1.4 returned pseudocode for each region successfully. Carrier sizes total **26,916 bytes**; overlapping semantic/runtime dependencies are not included. Each analysis session was exported and closed.

| Region | Start address | Source file offset | Length | Carrier SHA-256 |
| --- | --- | --- | --- | --- |
| Runtime argument builder | `0x1011fd394` | `0x11fd394` | 1,528 | `b7414a126eb648e1d58b76f6b4708ff324652950acc9377d0194c6902bcd48fb` |
| Runtime configuration builder | `0x1011e88ac` | `0x11e88ac` | 10,804 | `7f4b4fdac543d651b2d79d93abf74c3c16824dd745f839b50dd45540ad2f7d5c` |
| Dictation token endpoint builder | `0x10142ec3c` | `0x142ec3c` | 284 | `3c2c202f4f2bfbbe656ee6e23339e67a1b0031ac3908d57261a7b274b0d3aa28` |
| MCP request-handler candidate | `0x100ea1b48` | `0xea1b48` | 14,300 | `7198345956e0ba9cd8d2e86683b3882e161d7ec879698f4ca17dd1bb2e2a9354` |

These particular file offsets were measured from the image section mapping. They must not become an assumption that subtracting `0x100000000` always produces a valid file offset for arbitrary Mach-O data.

Important limits: the carriers omit imports, metadata, literal/data storage and most callees. Ghidra uses a generic ARM64 convention, so Swift implicit arguments, asynchronous continuations, ownership operations and types remain imperfectly reconstructed. Numeric call names and guessed parameters are not recovered Swift function names. Original-image annotations corroborate selected literals and imported stub identities; they do not automatically restore all missing semantics. No claim below depends on compiling the pseudocode.

## Subsystem findings

### Native shell and interaction surfaces

**OBS:** The universal application links SwiftUI/AppKit and system media, capture, speech, security and persistence APIs. Info.plist declares a menu-bar-style application (`LSUIElement`), macOS 14.2 minimum, and microphone/speech/screen/document-folder usage descriptions. Reflection and source-path strings identify HomeSpace, Notch, AnnotationOverlay and document preview components. N01/N02/N09.

**INF:** Voice, task/chat UI, visual guidance and output previews are native shell concerns around a separate execution engine. Their existence is supported; exact focus behavior, animation fidelity, accessibility and performance were not exercised.

**UNK:** Whether every packaged screen is reachable in this build/account; which legacy views are still used. No UI-quality judgment is based on unseen screenshots.

### Embedded Codex and process supervision

**OBS:** `Contents/Resources/CodexRuntime/` contains architecture-specific executables and helper paths. Vendor metadata identifies version 0.152.1. The packaged shell launcher selects ARM64 or x86_64, sets its helper PATH and executes the matching binary with supplied arguments. N02.

**OBS:** N05's two branches materialize `app-server` at `0x1020ae5bf`, then pass constructed values to `0x1011f659c`. N06 constructs model/provider configuration entries, history/log/SQLite paths, developer/model instructions, selected skills, trusted project settings and MCP server entries. The `clicky` provider configuration specifies the Responses wire format. Packaged strings include `CODEX_HOME` and an isolated-app-server startup diagnostic. N04/N05/N06/N09.

**INF:** The app starts an embedded Codex app-server using app-owned state and provider routing rather than merely invoking the user's developer installation. This inference has stronger support than runtime packaging alone; the process-spawn boundary and resulting argv/environment were not recorded in a running process.

**OBS:** The configuration builder includes `approval_policy = "never"` and `sandbox_mode = "danger-full-access"`. This is code-level evidence of a constructed configuration, not evidence that every account/session uses that exact effective policy. The signed app's App Sandbox entitlement is false. N04/N06/N09.

**Design implication:** Our runtime must isolate its data from the developer's Codex home, pin and negotiate the runtime protocol, supervise shutdown/restart, and enforce the product's authority rules outside prompts. A consent gate for one MCP helper cannot by itself constrain shell/filesystem/network tools. Do not infer equivalent protection from a friendly approval UI or copy the unrestricted runtime configuration as a default.

### Computer use and the consent boundary

**OBS:** A separate universal native `Contents/Helpers/cua-driver` links AppKit, ApplicationServices, ScreenCaptureKit, Metal and VideoToolbox. The main image contains daemon/socket/parent-liveness parameters, managed policy filenames, a separate gate token name and relay-restart diagnostics. These are artifact observations, not a successful launch. N02/N09.

**OBS:** N08 contains branches handling MCP initialization, `tools/call`, tool names, thread metadata, session headers, and construction of an unavailable-tool refusal. A 64-byte accessor candidate elsewhere references the longer per-turn input-consent refusal text. The full mapping from tool classification and conversation lineage to authorization state has not been recovered. N03/N04/N08/N09.

**OBS:** Embedded YAML/Rego policy text restricts input delivery to background mode and rejects desktop-coordinate input and selected tab/address-bar shortcuts. The packaged CUA skill describes observation without turn approval, input consent for the current conversation/turn or an optional always-allow setting, AX-first operation, separate browser windows, snapshot-before-action and post-action verification. Those are intended contracts and policy resources; they are not substitutes for testing enforcement.

The packaged skill also acknowledges that window-scoped pixel fallback may briefly activate the target, despite its broader no-foreground wording. It says drag, double-click, cursor movement, recording/replay and zoom are not exposed in its default managed runtime. The website's removal of the agent cursor layer must be distinguished from teaching overlays. See F04/F13/F14 and current/historical notes in the feature audit.

**Design implication:** Separate teach-only overlays, observations and real mutations. Bind grants to run, task, target and expiry; revoke on stop; prevent spawned helpers from gaining wider authority. Prefer structured APIs/AX/UIA actions. If focus must change, present that as an explicit fallback and measure it. Never promise background control for every app or secure input surface.

### Voice and dictation

**OBS:** Current artifact type/path strings identify RealtimeVoiceClient/Controller, audio route recovery, interruption, push-to-talk, always-on experimental text and Apple Speech support. Dictation strings describe Deepgram streaming, batch fallback, cleanup, focus-target capture, secure-field checks and clipboard salvage. N07 constructs the Deepgram token endpoint path. N01/N07/N09.

**INF:** Conversation voice and cross-app dictation are separate pipelines; the current build has a newer streaming dictation path than the public prototype. Apple Speech packaging does not establish a universally available offline mode, and endpoint presence does not prove a provider was called in a particular session.

**UNK:** End-to-end latency, transcription quality, live routing, default model/voice, cleanup fidelity and insertion reliability. No microphone or external transcription was used here.

**Design implication:** Independent `SpeechInput`, `SpeechOutput` and `TextInsertion` contracts; cancellation/generation IDs against late callbacks; original transcript preserved when cleanup fails; capture target identity before recognition and revalidate before insertion. Handle terminals, secure fields, IMEs and clipboard ownership deliberately.

### Conversations, memory, files and routines

**OBS:** Packaged instructions describe one workspace per named helper, dated notes in AGENTS.md, deliverables under output/ and work files under tmp/. Those instructions are target data only; this investigation did not adopt them as its own instructions. The main image contains thread/start/resume/read/steer/interrupt/archive protocol names, local thread-history/cache filenames and SQLite-related symbols/paths. N02/N09.

**OBS:** `/me/memory`, `/me/memory/save`, a cached-memory key prefix and a UserMemoryProfileResponse type are present. These support a local/remote memory data-flow hypothesis but do not establish server schema, retention or the correctness of deletion. No actual user memory was read. N09.

**OBS:** Routine metadata includes local routine keys, run triggers, wake/network observers, keep-awake types, polling state, and prompt text explicitly warning against promises while the Mac is asleep/off. Separate scheduled-cron and remote-task vocabulary also exists. These are distinguishable feature families; they must not be merged into a claim that local routines always execute in the cloud. N09; WEB-C in feature audit.

**INF:** Sessions are richer than the public ten-exchange in-memory array, agent memory mixes workspace notes with account context, and local routine recovery handles wake/network transitions. Exact persistence atomicity, schema, scheduling/catch-up algorithm and private remote-task execution are unresolved.

**Design implication:** Own a versioned local state model; expose memory with scope/source/date/edit/delete controls; keep artifact provenance per run; define one catch-up policy, durable run leases and idempotency receipts. A provider transport retry is not permission to repeat an external write with an uncertain outcome.

### Integrations, suggestions and service dependencies

**OBS:** Eleven integration-skill directories, custom connector OAuth/secret/store type names, composio MCP configuration and multi-account routing instructions are packaged. A bundled catalogue lists 14 models; it is not a live entitlement list. Proactive-agent client/types, daily-slot keys, approval/denial events and suggestion-history keys also exist. N02/N06/N09.

**INF:** The commercial product coordinates integrations and suggestions through account-backed remote services as well as local tools. Product parity requires supported authentication/inference/connector services of our own; finding endpoint strings does not provide their server implementation or authorize use of HeyClicky's private service.

**OBS:** `Resources/LICENSE` is MIT with a Nous Research copyright; `ATTRIBUTION.md` explicitly scopes it to vendored Hermes skills and separately identifies a Blender skill. Its sentence about unfinished skill wiring may be stale, especially given paused community Skills in the changelog. Do not read this file as an MIT licence for the entire private app or proof that current tools do not work.

## Investigation coverage and open questions

| Original question | Status | Remaining evidence needed |
| --- | --- | --- |
| How does this differ from the public source? | Answered for architecture/feature inventory | Runtime comparison for specific workflows. |
| Embedded runtime and configuration? | Partially answered with native code and packaging | Controlled process launch trace and supported-protocol negotiation. |
| Voice, screen and dictation components? | Partially answered | Permission-controlled interaction, audio/capture traces and failure tests. |
| Computer-use policy and helper? | Partially answered | Denial/allow/revoke/child-run tests, full code-level authorization lineage. |
| Persistence, memory and scheduling? | Partially answered | Synthetic-account restart/sleep/offline scenarios and targeted code tracing when needed. |
| Exact original source/private backend? | Unresolved and not supplied by decompilation | Not required to design our own implementation; hosted code is absent. |
| Windows implementation? | Design proposal only | Native adapter prototype and real Windows acceptance. |

The research phase delivered a bounded feature/architecture baseline and build plan. It did **not** finish a complete reverse engineering of all private behavior. The open questions above are explicit validation work, not silently marked complete.

## Recommended follow-up investigation

Use controlled fixtures and an explicitly selected test account for any later runtime comparison. First observe onboarding, permission denial and a read-only teaching task. Then compare one synthetic dictation task, one consent-denied/allowed computer-use task and one routine across restart/sleep. Account sign-in, OS permission grants, remote usage and external writes must match the actual test scope. Avoid recording real personal content.

Further native analysis should answer a named blocker. Reuse the source hashes, reference survey and narrow carriers; request full-image analysis only if its expected benefit justifies a deliberate time/resource budget. Repeated unchanged whole-image timeouts are not progress.

See [REA_SETUP.md](REA_SETUP.md) for installed tools and earlier limits, [FEATURE_AUDIT.md](FEATURE_AUDIT.md) for product/source evidence, and [BUILD_PLAN.md](BUILD_PLAN.md) for the proposed implementation.
