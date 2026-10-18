# Clicky Bro product roadmap and production gates

**19 October 2026.** Prioritised by everyday user value, dependency order, feasibility, privacy risk and verifiable acceptance. Plans are **not implemented features**. The [build status](BUILD_STATUS.md) and [PR #1](https://github.com/Itskorrah/clicky-bro/pull/1) take precedence for current work.

## Current baseline

The source incorporates a pinned MIT OpenClicky native foundation. macOS and WPF clients, local Apple/Parakeet dictation, chosen-window capture, Gemini BYOK helper tools, history, memory and routines exist. A local no-Actions test runner is merged; targeted answer-stream correctness fixes are merged. Native Mac/Windows release acceptance remains incomplete. PR #1's selected-window diagnostics, helper templates and action Stop changes **are a draft** until verified.

Evolve method: investigate real workflow → small testable implementation slice → direct local tests → independent source/OS review → safe merge. Every feature earns its status separately: researched / source added / built / automation passed / physical platform accepted / distributable.

## Dependency-aware priorities

| Rank | Workstream | Why it matters | Minimum acceptable evidence |
| --- | --- | --- | --- |
| P0 | Native selected-window permissions/Stop and real dictation acceptance | Users cannot trust other features until capture and input are safe | Actual current-build Mac TCC, microphone, focus, Stop and failure/recovery recordings on synthetic data |
| P0 | Azure native visual system | Fragmented accent colours and inconsistent hierarchy harm daily use | Tokens + semantic components + Home/companion/dictation/workspace/settings in light/dark, real screenshots and keyboard/VoiceOver tests |
| P0 | Offline speech model experience | No subscription required for local transcription; multilingual gaps | Explicit per-model download, pinned validated model, genuine local ASR from microphone, benchmark against Parakeet, no data leaves app |
| P0 | Dictation correctness | Lost focus or bad edits waste user trust | App-specific paste/focus/undo, long takes, changing selection, audio loss, raw vs cleaned transcript |
| P1 | Document context and grounded teaching | A screenshot misses documents outside the visible page | Real PDF/selection with page citations; no unselected source captured; target move/close before pointing |
| P1 | Agent authority and recovery | Must stop, deny, retry and avoid repeat writes | Per-action approval, concurrent task isolation, cancellation during pending approval, restart reconciliation and receipts |
| P1 | Workspaces/history/files | Current helpers need modern UX and durable context | Search, per-chat drafts, real artifacts and source attribution, privacy-aware retention and Windows parity |
| P2 | Real account/MCP integrations | Small useful workflow beats a catalogue of broken connectors | Exact scoped token/auth, error/re-auth/revoke, read-only dry run and authorised action receipt |
| P2 | Platform distribution | No reliable consumer delivery without packaging | Signed/notarised Mac bundle, Windows installer, clean-machine upgrade/uninstall, auto-update tests |

## Offline speech implementation decision

Do **not** replace Parakeet or choose Whisper solely on vendor benchmarks. The existing macOS/Windows Parakeet runtime uses sherpa-onnx, checks the 465 MB model SHA-256 and unloads during idle/memory pressure. Whisper is not yet integrated. sherpa-onnx supports offline Whisper encoder/decoder/tokens through its same C recognizer API, making it a practical *candidate* without adding a second inference engine; verify the exact pinned runtime header and ABI before adding config.

Proposed first slice:
1. Explicit model install consent with clearly displayed archive size, disk requirement, local privacy and attribution; cancel, retry, delete and checksum-verified installation. No background model downloads without opt-in.
2. Adapter-level Whisper Tiny and Small (multilingual) behind the existing speech-provider interface. Pin exact archive, checksum, model identifiers, runtime and licence. The UI must not offer an engine until installation and a real transcription probe pass.
3. Compare local transcriptions using a deterministic offline evaluation corpus (Australian English, varied accents, technical terms, Arabic and longer pauses) and report WER/CER, first partial, final latency, memory, CPU and language auto-detection. Do not invent performance numbers.
4. Optional local-only end-to-end mode that prevents both cloud STT **and** cloud transcript polishing, including retry/error fallback paths. Expose destination labels per stage.
5. VAD and chunked long-take support only after comparison; avoid repeatedly decoding complete 30-minute audio.

Sources: [sherpa-onnx offline C API](https://github.com/k2-fsa/sherpa-onnx/blob/master/sherpa-onnx/c-api/docs/offline-asr.dox), [whisper.cpp](https://github.com/ggml-org/whisper.cpp), [Whisper open weights](https://github.com/openai/whisper). Audit each distributable model weight and package separately.

## Visual redesign slices

The native code now has an Azure semantic token foundation; [design spec](DESIGN_SYSTEM.md). The rest should land as separate PRs: (1) reusable native controls and selected states; (2) Home with Ask/Dictate/Work and real recent runs; (3) compact companion/audio/permission cards; (4) Workspaces and history/artifact previews; (5) model management and settings; (6) Windows parity. Never claim new UI quality solely because colour constants changed.

For each slice test system/light/dark, reduced motion, magnification, keyboard navigation, high contrast, screen-reader labels, compact widths, two monitors, and real error states. No browser mock-up should be labelled native acceptance.

## Key security and privacy scenarios

- Closing/moving a selected window never broadens capture to display-wide. Revoking Screen Recording invalidates the capture.
- New messages and Stop cancel still-pending automation/approvals; already completed effects are not falsely called undone.
- Helper scopes and prompt text do not authorise tools. File-write permission is enforced independently of the model and ideally per effect.
- Local voice mode cannot send audio or resulting words to a cloud polisher. Remove/forget actually deletes local model/history data according to the selected control.
- Untrusted PDF/web/email content cannot grant authority or exfiltrate secrets through a prompt instruction.
- Routines do not burst-replay after sleep/restart and cannot execute outside the declared schedule/grants.
- Provider quota exhaustion preserves state and gives the user a recoverable path; no unauthorised paid fallback.
- Real connector account revocation terminates the capability; saving a token is not a successful connection.

## Verification and blockers

1. **Mac hardware/Xcode** required to accept PR #1, native Swift type/build, real microphone, ScreenCaptureKit/TCC and all interface screenshots.
2. **Windows workstation/.NET and GUI** required for WPF launch, input, accessibility, native screenshots and installer acceptance. Portable builds alone do not count.
3. **Model weights, download and real audio fixtures** required for Whisper compatibility/accuracy/latency claims. Offline evaluator code can be verified without them, but no ASR result can be accepted without inference.
4. **Signed distribution credentials** required for notarisation, trusted Windows signing and update distribution; do not spend or publish without authorisation.
5. **Third-party account credentials** required only for integration acceptance; use synthetic fixtures for all earlier steps.
6. **GitHub Actions** intentionally not used. Run scripts/check_local.py with explicit chosen platforms; exit 2 is incomplete, not a pass.

## Definition of better-than-industry-standard

Not a marketing superlative. Demonstrate, with repeatable comparisons, shorter time to first successful dictation, accurately recognised speech across the target languages, low error rates, discoverable approval/Stop, predictable privacy, resilient restart, accessible layouts and stable installation. Benchmark against real tasks with recorded hardware/OS/version, not an unverified feature count.
