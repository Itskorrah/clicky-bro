# Foundation decision: native OpenClicky adoption for clicky-bro

Decision date: 17 October 2026. Adopt the pinned Prasanth OpenClicky source at
`1ff98e4e0f3c9af94ee3a80f81b2a20cb087aee9`, preserving its Swift macOS,
C#/WPF Windows and TypeScript agent boundaries. Source is under `app/`.

## Evidence before adoption

| Candidate | Commands/results | Relevant findings |
| --- | --- | --- |
| Prasanth OpenClicky | macOS Debug xcodebuild succeeded; agent build/typecheck passed; 103 TS tests passed, 4 real-Codex tests skipped in the scrubbed environment | Existing Gemini streaming/image input, substantial native voice/dictation/overlay/teaching and Windows source. Needs private identity/data paths, real Gemini agent continuation, explicit action approval and outcome-based teaching. |
| ClickyX `988568ad980e6bc73e4d97ef835989f8e151bf8d` | npm frontend build passed; 171 tests in 24 files passed; lint passed with 59 warnings; Rust `cargo test --locked` failed because the pinned lockfile needs updating | Source inspection found RGBA-to-JPEG incompatibility, image-free streaming, a plain-chat saved-agent worker, Stop that discards results rather than aborting requests, and POINT tags that can click directly. No native acceptance claimed. |

Raw evidence is in ignored `.local/evidence/native-candidate/` and
`.local/evidence/shared-candidate/`. Frontend or bridge tests do not prove native
desktop behavior. The Rust lockfile failure alone did not decide the outcome;
the native candidate has substantially more of the required workflows with
fewer execution engines to replace.

## What is retained and changed

Retain the useful native shell, dictation, providers, settings, skills, window
geometry, process bridge and Windows contracts. This is one foundation, not a
merge of several apps. New clicky-bro changes isolate identity and data; choose
Gemini's reviewed free-model default and local speech; constrain shared pixels
to one chosen window; add bounded tool-result continuation, action confirmation,
cancel checks and evidence-based teaching; and add durable helpers, explicit
memory, routines and run artifacts.

The TypeScript Gemini agent is separate from the developer's Codex session.
It must work with the authorized Gemini key and may not borrow Codex tokens.
External account connectors and commercial backend services are not silently
inherited or provisioned. Unconfigured services remain unavailable.

## Platform and acceptance boundaries

The initial baseline build ran on this Apple Silicon Mac. Windows source/core
tests and a cross-build, if available, are distinct from Windows desktop runtime
acceptance. No physical Windows host is available in this session. Capture,
focus, mixed-DPI placement, permissions, audio and input must still be tested
on every platform claimed for release.

The six authorized phases remain active until their acceptance work is done;
adopting source does not mark inherited features verified. See BUILD_STATUS.md
for the evolving implementation and remaining gaps.
