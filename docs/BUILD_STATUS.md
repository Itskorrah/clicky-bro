> **19 October 2026 acceptance update:** Source `main` was `2a82bdbdbe6b7f465492a3ca3f73e7f1677054e4` after PR #12. PR #1 is updated to `6b5de4a`, PR #8 to `30d552f`, and PR #9 to `946ca50` (stacked on #8); all remain drafts. Current macOS native test suites pass on the updated safety and combined theme/companion source. The WPF cross-build passes on macOS, while the portable Windows core suite has five host-specific path failures. No Windows host was available, and full capture/TCC acceptance remains pending. See the [current development checkpoint](DEVELOPMENT_CHECKPOINT_2026-10-19.md).

# clicky-bro development status

Updated 19 October 2026. This is a local development build based on the pinned
MIT native OpenClicky source, not a completed commercial HeyClicky replacement.
The historical runtime checks below were recorded on earlier source revisions;
the source and tests distinguish implementation from runtime acceptance.

## Current PR and acceptance state

| PR | Updated source | Current evidence | Still pending |
| --- | --- | --- | --- |
| [#1 — capture diagnostics and Stop safety](https://github.com/Itskorrah/clicky-bro/pull/1) | `6b5de4a`; based on current `main`; draft | macOS native suite 710 passed, 0 failed, 0 skipped; seven offline checks passed | Real ScreenCaptureKit/TCC workflow, permission denial/revocation, and native Stop during a live pending request |
| [#8 — native theme customisation](https://github.com/Itskorrah/clicky-bro/pull/8) | `30d552f`; based on `main`; draft | Native Settings route builds; combined #8+#9 macOS suite 714 passed; theme-head portable core suite 1,070 passed/5 failed; real Settings controls/presets inspected without changing preferences | macOS custom picker and restart persistence; native Windows colour dialog, persistence, mixed DPI and accessibility |
| [#9 — companion geometry and motion](https://github.com/Itskorrah/clicky-bro/pull/9) | `946ca50`; based on #8; draft | Combined macOS suite 714 passed; WPF cross-build passed | Native overlay screenshots, measured frame-time/CPU/GPU, mixed-DPI Windows, accessibility and click-through acceptance |

Windows core tests on macOS reported **1,070 passed, 5 failed, 0 skipped of 1,075** on the #8 theme head and **1,076 passed, 5 failed, 0 skipped of 1,081** on the integrated #8+#9 head. The same five failures cover Windows drive/path separators and npm shim assumptions on the macOS host; they remain failures in the reports and are not Windows passes. No GitHub Actions runs were used. Test reports and raw logs stay in ignored `.local/evidence/`.

The current isolated macOS app's General Settings window and theme controls were inspected through accessibility. The accent menu and Reduce Motion control were visible; no theme preference changed. The custom colour picker and visual companion comparisons were not exercised. The isolated app was quit after inspection.

## 19 October 2026 change note (branch pending review)

The focused [implementation record](IMPLEMENTATION_2026-10-19.md) adds whole-frame
position/size revalidation, an explicit local-only capture diagnostic in Privacy,
strictly per-action Gemini file approvals, Stop while a native approval hook is
pending, and three read-only workspace starter drafts. Regression tests were added
but **not executed in the Linux/GitHub-only environment**; none of the historical
test totals below includes these commits. Native capture permission, UI, dictation
and Windows desktop acceptance remain open. See the root [PRODUCT_STATUS.md](../PRODUCT_STATUS.md).
No new real-device screenshots, fresh build, deployment or release evidence was
produced on this branch.

## Implemented in this checkout

| Area | Current behavior | Acceptance still needed |
| --- | --- | --- |
| Local environment | Isolated app IDs; launcher-staged agent under `~/Library/Caches/clicky-bro/development`; private runtime under `~/Library/Application Support/clicky-bro/development`; one-time preservation migration from `.local/`; own Gemini key | Fresh-machine setup and release packaging |
| macOS Ask/capture | User chooses one window; capture revalidates its identity and never falls back to a display; sharing has a visible Stop control | Current development bundle's Screen Recording permission is not accepted; real permission denial, closed/moved window, mixed-monitor capture and focus checks |
| Teach/actions | Teach observes and verifies steps without action tools; Agent mode is off by default and separately confirms native effects | Real-world grounding, ambiguity and cancellation on disposable native windows |
| Gemini execution | Direct native/TypeScript Gemini protocol, original tool metadata and results, bounded requests/actions, strict successful terminal response before tools, explicit failure without paid fallback | Task quality and sustained usage beyond small synthetic probes |
| Voice/dictation | Native system speech selected by default; existing native dictation engines retained | Actual microphone/transcription, focus-safe insertion, interruption and language acceptance |
| Helpers and memory | macOS editor, persistent scoped helpers and explicit opt-in notes; file-write permission independent of memory/scope text | Windows UI parity, follow-up/steering, richer lifecycle and memory provenance |
| Routines | Local intervals, per-session opt-in, persisted occurrence deduplication, no burst replay, interrupted restart state | Sleep/clock/DST/native scheduling observations and richer schedules |
| Files/history | Gemini threads, saved run status and text artifacts; bounded list/read/write tools inside the workspace | Safe rich file previews, attachments and end-to-end artifact workflows |
| Skills/integrations | Adopted skill/settings source retained; direct Gemini supports the declared workspace file tools | General MCP/connector execution, scoped auth, real account-service acceptance |
| Windows | Native WPF client, Gemini continuation, default-deny per-action native approval, cancellation checks and write-in-place target guards | Physical Windows desktop acceptance, chosen-capture contract and new workspace UI |

Scope and memory are instructions, not an operating-system sandbox. Helpers can
read supported text files in the configured agent workspace, and only the separate
write checkbox grants their supported workspace writes. Keep that workspace
separate from personal documents. Desktop automation uses a different native
approval path. Unsupported general voice actions fail closed instead of executing
through the older realtime callback.

## Earlier base-application verification

The following table documents the previously merged base application, before the
current PR #1/#8/#9 heads. It is historical context and does not replace the
current branch results above.

The following checks ran locally with synthetic fixtures and isolated data.
Raw logs are ignored under `.local/evidence/`; credentials and user runtime state
are excluded from delivery.

| Check | Result / boundary |
| --- | --- |
| Offline Python suite | 15 passed: 8 private-runtime migration/staging tests and 7 provider/credential tests |
| TypeScript agent typecheck and build | Passed |
| TypeScript agent suite | 119 passed, 3 explicit real-Codex integration tests skipped |
| Native provider/teaching focused security suite | 29 passed before the full native run |
| Independent repair reproduction | Five incomplete/refused response variants: no effects or approvals. Valid STOP control: approved fixture write succeeds. Windows/native strict terminal guards and key redaction reviewed. |
| Initial live Python Gemini probes | Text, generated image, function selection and calculator continuation all passed (4 requests) |
| Actual native Gemini smoke | Generated red-square image correctly answered; 1 request, approximately 3.0 seconds |
| Actual system-speech smoke | Local Daniel voice produced 294 KiB / 3.4 seconds of audio in approximately 0.96 seconds; no cloud TTS |
| Actual direct Gemini CLI run | Approved disposable `acceptance.txt` write matched exact expected content; completed result and 1 artifact recorded |
| macOS live helper run/restart | Passed 18 October 2026. The root launched the private Application Support runtime, ran the text-only helper once, and observed completed `CLICKY_BRO_HELPER_OK` with inline `Answer.txt` artifact. After Cmd-Q and relaunch, the same completed row and artifact remained visible and matched persisted state; one previously completed migrated run also remained. The helper run took 2.313 seconds; two live Gemini GUI requests were used for this batch. This validates the helper/runtime persistence slice only. |
| Native macOS unit suite | Authoritative run: 705 passed, 0 failed, 0 skipped, covering the preceding functional, privacy and Stop-observer fixes. The final standalone app build passed after the accessibility-row follow-up. A focused helper-button UI test compiled but timed out while enabling automation mode before its body ran; it is not a passing UI result. Broader UI automation, capture and permission acceptance remain open. |

The old real-Codex/fake-model integration suite reproduced 2 failures/1 pass on
untouched upstream before becoming explicit opt-in; it is not passing evidence.
The initial full macOS attempt was stopped after an inherited unpaced audio
harness flooded its queue. Its partial passing cases were not counted as a
completed run. The authoritative native unit run passed 705/705. The later
accessibility-row source follow-up compiled in the final standalone app build,
but its focused UI test timed out before executing; broader automated UI and
capture acceptance remain pending. The Windows results currently verified are
below.

| Windows check | Result / boundary |
| --- | --- |
| Windows core suite on macOS | Earlier base source: .NET SDK 8.0.426; 1,066 passed, 5 failed, 0 skipped / 1,071 total. The five failures matched the untouched upstream baseline; all nine base-source cancellation, identity and clipboard-restoration regressions passed. This is portable core-test evidence, not Windows OS acceptance. See `docs/TESTING_WINDOWS.md`. |
| Windows WPF cross-build | Earlier base source: cross-build passed with .NET SDK 8.0.426, 0 errors and 1 inherited `WFAC010` high-DPI manifest warning. This is not Windows OS acceptance. Exact commands are in `docs/TESTING_WINDOWS.md`. |

## Material limits

- Windows desktop testing is explicitly deferred by the user until their PC is
  available for it. A Mac cross-build is not evidence of Windows capture, audio,
  hotkey, focus or input behavior.
- The ignored self-contained Windows publish folder was produced before the
  latest cancellation/target-safety repairs and is stale. It is not a final
  source artifact and has not been executed on Windows.
- Current macOS development-bundle Screen Recording permission is not accepted.
  Final launch diagnostics reported Accessibility, Screen Recording and
  microphone unavailable and `screenContent` false. Settings can show an Allowed
  entry from an older build while an ad-hoc rebuild has a different CDHash; the
  current bundle has not completed a full capture test. The user has enabled
  the old OpenClicky row, but has not yet removed it and added the exact current app at
  `~/Library/Caches/clicky-bro/DerivedData-local/Build/Products/Debug/OpenClicky.app`.
  Follow [TESTING_MACOS.md](TESTING_MACOS.md) after the final build. The
  reviewed code and source tests show no automatic display-capture fallback, but
  that is not a runtime capture acceptance result. A later
  rebuild may require repeating registration until a properly signed distribution
  has a stable code identity. No TCC reset or signing configuration change was
  made. The live helper run/restart passed; capture, Accessibility and
  microphone acceptance remain pending.
- Native macOS Accessibility, selected-window capture, teaching and dictation
  still need manual acceptance before release claims.
- Native text-field rewriting is disabled when exact shared-window identity
  cannot be established. Realtime actions direct users to the approved Agent
  route. These are explicit safety limits, not feature parity.
- New workspace routines only run while this application is open. Interrupted
  work is recorded; it is not silently retried or resumed.
- No customer accounts, billing/plans/teams/referrals, managed connector backend,
  production notifications, signed installer, trusted update service or commercial
  deployment was provisioned. Inherited interfaces do not establish those services.
- Private local key files use owner-only permissions; OS credential-store
  integration remains release work. Free-model availability and limits belong
  to the provider and can change; an allowlist is not a billing cap.
- Upstream OpenClicky names remain in internal project/class names and retained
  attribution. The project-owned product name is clicky-bro. This build is not
  installed over HeyClicky.

## Continue

Use the root README and [TESTING_MACOS.md](TESTING_MACOS.md) for Mac acceptance,
and [TESTING_WINDOWS.md](TESTING_WINDOWS.md) when a Windows PC is available.
[NEXT_STEPS.md](NEXT_STEPS.md) prioritizes acceptance and remaining feature work
against the research crosswalk. This pass used KStack's native-desktop routing
and verification guidance with the project's Evolve implementation/verification
skills. KStack remains a local ignored checkout, not a global install or a
runtime agent swarm. Keep native builds sequential on this 8 GiB Mac.
