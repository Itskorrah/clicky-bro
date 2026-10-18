# clicky-bro product status

**Updated:** 19 October 2026 — feature branch `improve/capture-diagnostics-2026-10-19`. This is source in review, **not a signed release or an accepted HeyClicky replacement**.

## Evidence levels

| Area | Source implemented | Automated evidence | Physical/device acceptance | Released |
| --- | --- | --- | --- | --- |
| macOS selected-window capture | Window/PID pinning, explicit selection, Stop sharing, fail-closed capture; this branch adds full-rectangle revalidation and a local frame diagnostic | Existing captured-geometry tests; new moved/resized/diagnostic tests added **but not executed in this environment** | **Open**: current app bundle TCC, permission denial/revocation, multiple displays, moved/closed window, restart | No |
| Ask / Teach / Agent | Separate read-only guidance and action-gated agent lanes, verification and cancellation paths | Prior macOS source suites recorded 705/705 on 18 October; this branch is **not covered by that run** | **Open**: real selected-window task evidence and Stop during live native approval | No |
| Gemini BYOK / scoped files | Direct free-model allowlist, quota errors and bounded tools; this branch blocks session-wide write approval and unblocks pending approval on Stop | New synthetic TS regressions added; **not run locally here** | Earlier live Gemini text helper and restart persistence accepted 18 October; new approval flow unaccepted | No |
| Workspace | Helpers, opt-in memory, session-only routines, local run/artifact records, three read-only starter drafts | Prior workspace source tests; starter default-deny tests added **not run here** | Earlier text-only helper persistence run accepted; starter workflows not end-to-end accepted | No |
| Voice and dictation | Existing microphone, native and remote speech providers, insertion architecture | Earlier system-speech smoke accepted | **Open**: actual microphone, transcription, long dictation, focus-safe insertion, language tests | No |
| Windows | Adopted .NET/WPF source with earlier targeted guard tests | 18 Oct report: 1,066 passed / 5 inherited baseline failures; prior WPF cross-build | **Open**: physical Windows capture and desktop workflows; Windows workspace parity | No |
| Distribution | Developer launcher and isolated local paths | Earlier standalone app build reported passed | **Open**: stable signing, install/update/permission identity, clean Mac setup | No |

Previous test numbers are historical evidence recorded in [docs/BUILD_STATUS.md](docs/BUILD_STATUS.md), not freshly rerun validation. No screenshot of the **current** macOS bundle exists in this change; do not reuse inherited OpenClicky assets as before/after evidence.

## What this branch changes

- Settings → Privacy & Security offers **Selected-window capture test**. It compares CoreGraphics' permission preflight with an actual local ScreenCaptureKit JPEG from the *already shared* window. It does not select another window, upload or persist that image. Neither an Allowed TCC switch nor a successful synthetic test proves the pixels are semantically correct.
- A window that changes **position or size** during the asynchronous screenshot now requires a fresh capture. Window ID and owning PID remain enforced; no display fallback is introduced.
- Gemini workspace writes require a distinct `accept` for that action; `acceptForSession` is explicitly insufficient. Stop interrupts a pending approval wait without allowing a late write.
- The companion’s Stop control, application shutdown and a replacement question now cancel active agent work as well as the current answer. Actual in-flight native effects must still be checked on macOS: cancellation cannot undo an effect already completed.
- Workspace starter drafts cover **error explanation** (`error.txt`), **step planning** (`goal.txt`) and **draft review** (`draft.txt`). They are read-only, memory-off, never auto-run and produce ordinary audited run results only when saved and explicitly run. They are examples, not proven live-screen workflows.

## Privacy and trust boundaries

The model may read selected-window pixels only after the user has chosen that window; this image is sent to the selected model on an Ask/Teach request, but **not** during the new local diagnostic. A text file placed in the workspace is untrusted input, not a grant of OS authority. Memory and scope are context only. The helper write checkbox is a persistent opt-in for workspace-file writes: the current native CLI uses it to automatically accept eligible `gemini/write_file` requests **without a second confirmation dialog**. In interactive approval mode, each file request must return an explicit `accept`; a session-wide grant is rejected. Both modes still enforce the workspace path boundary, but the native helper path needs a finer-grained confirmation design before sensitive workspaces are appropriate. No native automation, paid fallback or external account connection is activated by this branch. Never place real passwords, keys or personal screens in acceptance fixtures. Review the upstream licences before a release ([docs/PROVENANCE.md](docs/PROVENANCE.md)).

## Reproduction

On a Mac with Xcode and Node.js 24, from the repository root:

```sh
npm ci --prefix app --ignore-scripts
npm run typecheck --prefix app --workspace agent
npm test --prefix app --workspace agent -- --maxWorkers=1
python3 -m unittest discover -s tests -v
python3 scripts/dev.py build
python3 scripts/dev.py test-native
python3 scripts/dev.py launch
```

For native acceptance, use [docs/TESTING_MACOS.md](docs/TESTING_MACOS.md). For Windows use [docs/TESTING_WINDOWS.md](docs/TESTING_WINDOWS.md). Building on Linux cannot validate AppKit, ScreenCaptureKit, macOS TCC, WPF or Windows desktop focus. No paid provider smoke was triggered on this branch.

## Ranked blockers and next actions

1. **P0 / current bundle permission:** run the selected-window frame diagnostic on a physical Mac, record macOS version, bundle identifier, code signature identity, preflight vs frame result, and denial/closed/moved/restart/multi-monitor cases. Repair failures *observed there*.
2. **P0 / desktop safety:** run Stop during actual model execution and native approval, teach a task without effects, reject cross-window actions, and verify in a disposable app.
3. **P1 / voice:** run microphone permission, Apple on-device dictation, long speech, interruption and focus-change insertion acceptance.
4. **P1 / UI:** capture real compact/large, light/dark, keyboard and text-scale states before deciding on a full redesign. The diagnostic and starter controls have not been visually checked.
5. **P1 / provider:** validate key setup, model availability and 429/invalid-key UX on opt-in free quota; do not silently switch to paid models.
6. **P2 / Windows and release:** verify physical Windows capture and approvals, design workspace parity, then plan stable macOS signing and opt-in updates. No release or unattended automation before acceptance.

See [the branch implementation record](docs/IMPLEMENTATION_2026-10-19.md) for rationale and the unavailable checks.
