# 19 October 2026 — focused implementation and verification record

**Baseline:** main `a29725405681304139f214589693fc41360d2a07` (single original repository commit). This checkout contains adopted native Swift/WPF/TypeScript foundations, an explicit privacy/authority design and 18 Oct verification notes. Private runtime files and user keys were not available to this GitHub-only execution environment and were not accessed.

## Research / decision

This pass compared:
1. **Apple's ScreenCaptureKit single-window filter:** `SCContentFilter(desktopIndependentWindow:)` scopes capture to the chosen `SCWindow`, unlike a display-wide filter. The existing implementation correctly uses this, so keep it. [Apple filter API](https://developer.apple.com/documentation/screencapturekit/sccontentfilter/init%28desktopindependentwindow%3A%29).
2. **Apple's shareable-content enumeration:** `SCShareableContent.excludingDesktopWindows(_:onScreenWindowsOnly:)` reports windows currently available to the running app; it does not certify an image. Re-resolve the selected window and owner PID before and after capture. [Apple API](https://developer.apple.com/documentation/screencapturekit/scshareablecontent/getexcludingdesktopwindows%28_%3Aonscreenwindowsonly%3Acompletionhandler%3A%29).
3. **CoreGraphics Screen Recording preflight:** `CGPreflightScreenCaptureAccess` reports one permission signal, not a demonstrated successful frame; application identity and OS TCC can diverge during ad-hoc rebuilds. Combine the indicator with a local `SCScreenshotManager` attempt, and never interpret a Settings toggle as native acceptance. [Apple preflight API](https://developer.apple.com/documentation/coregraphics/cgpreflightscreencaptureaccess%28%29).
4. **Google Gemini function-call continuation:** persist the complete original response parts, including thought signatures, so an authorised tool continuation can send them back correctly. The existing protocol already does this; focus instead on the stop/approval trust boundary. [Google thought signatures](https://ai.google.dev/gemini-api/docs/generate-content/thought-signatures).

Evolve's audit → prioritise → implement → verify → ship methodology is already vendored in this repository under `.agents/skills/evolve/` with its MIT licence. pstack was consulted as a root-cause / subtract-before-adding reference, not invoked as a Cursor-native command. No new runtime packages or licences were added.

## Selected acceptance criteria / implementation

| Slice | Failure mode / expectation | Change |
| --- | --- | --- |
| Capture | Moving the shared window during screenshot must not lead to a misaligned pointer or accepted stale frame | Compare **whole** window rect after capture, not just size; request a fresh Ask if moved |
| Capture diagnostics | A green permission checkbox might coexist with unusable TCC capture; no extra screen permission or network should be inferred | Privacy settings provide explicit test of an *already selected* window; report both preflight and actual local JPEG, without storing/sending pixels |
| Gemini file approval | Model text, a read-only helper or session-wide approval must never become permission to write a local file | Allow only a single explicit `accept`; reject `acceptForSession` |
| Gemini Stop | A pending UI approval hook can remain unresolved after Stop | Race that hook against abort and ensure cancellation is checked before any filesystem effect |
| Workspace usefulness | Empty workspace gives no safe first-run use cases | Three starter drafts: error.txt explanation, goal.txt plan, draft.txt review; default-deny memory/writes; explicit save/run |
| Permission copy | Old product name can cause approval of the wrong app's TCC row | Refer to the exact running bundle rather than an adopted upstream product name |

## Verification boundaries

**Done:** inspected branch head/history and repo tree, applicable root/native instructions, selected implementation and tests, previous build logs, Apple/Google documentation and existing Evolve source. Read source/test differences back from the remote branch. Regression cases were authored for moved-window geometry, diagnostic state, starter default-deny, session-wide write approval and Stop during pending approval.

**Not done / unavailable:** source clone in the container failed because `github.com` DNS resolution was unavailable; Linux has Swift 6.2 but no macOS AppKit/ScreenCaptureKit, Xcode, Windows .NET SDK or physical desktop. This branch's TypeScript/npm, Python suite and native macOS/.NET test commands have **not** run. The prior 705/705 macOS, 119 TS, 15 Python and 1,066/1,071 Windows results in `docs/BUILD_STATUS.md` are prior-run evidence only. No real image was captured, no microphone accessed, no paid model called, no UI screenshot generated, no runtime or production data modified. A static/source review is not a passing test.

**Physical-device follow-through:** execute `docs/TESTING_MACOS.md` with a disposable editor and window on each display; record local frame result, app identity, privilege prompts, interrupted tool effects, workflow success/failure and screenshot evidence (redacted). Reject any release until these checks pass.

## Changes deliberately deferred

A full workspace visual redesign without the app running would risk generic UI and unmeasured regressions. Integration of additional paid model providers, arbitrary third-party desktop actions, connector sign-in, automated updates and full Windows parity are not justified before native capture and approval acceptance. No CI workflow was activated to avoid unapproved private-repo runner usage. 
