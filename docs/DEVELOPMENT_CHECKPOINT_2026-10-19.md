# Native design and cursor development checkpoint — 19 October 2026

**Purpose:** Recover the work after a ChatGPT execution timeout without losing scope, merging unverified native changes, or reopening unrelated work. Treat this file as a dated implementation ledger, not a release claim.

## Current GitHub state

| PR | Status | Verified scope |
| --- | --- | --- |
| [#7 — public Clicky Bro branding](https://github.com/Itskorrah/clicky-bro/pull/7) | **Merged to main** (`652784ea590bb45882c505e3c65ab9cd6a4016ad`) | User-facing title, tray, permission and welcome string read-back; original SVG logo present in README |
| [#8 — native colour customisation](https://github.com/Itskorrah/clicky-bro/pull/8) | **Draft, unmerged**; head `91162ff`, base `16b81f0` | Swift palette compile and 42 isolated colour assertions were reported before the final bubble-contrast helper; no current native project build |
| [#9 — cursor geometry and visual polish](https://github.com/Itskorrah/clicky-bro/pull/9) | **Draft, unmerged**; head `8c3df1d`, base `16b81f0` | Pure Swift bubble placement compiled on Linux and passed 5 isolated assertions; no native overlay acceptance |
| [#1 — capture diagnostics and agent Stop](https://github.com/Itskorrah/clicky-bro/pull/1) | **Draft, unmerged; unverified**; head `e6feadd`, base `e77b4b5` | No current-branch full suite or native permission/safety acceptance. Its base is two commits behind `main`; refresh it before integration. Changes affect authority boundaries and **must not be bundled with cosmetic PRs** |

**Current `main`:** `16b81f05fbda90278b30ae7ef9e7d0fc47cb7dd7` (includes merged PR #10).

**Never equate a green GitHub mergeability flag, isolated Swift compile or source read-back with a passing native AppKit or WPF application.** GitHub Actions minutes are exhausted; do not trigger workflows merely to collect a checkmark.

## Approved visual direction

Preserve the existing settings structure and UI seen in the reference Windows screenshots: native sidebar, grouped cards, native controls, familiar layout and Light/Dark/Auto. Classic Coral is the default identity; Azure, other presets and custom companion colours are optional. A clean cursor should keep click-through, pointer authority and the current targeted flight/guide behaviour while reducing heavy glow and keeping status bubbles away from display edges. Use the existing SwiftUI/AppKit and WPF stacks.

Design audit sources: [Evolve](../.agents/skills/evolve/SKILL.md), ibelick's [improve-ui](https://github.com/ibelick/ui-skills/blob/main/skills/improve-ui/SKILL.md), [fixing-motion-performance](https://github.com/ibelick/ui-skills/blob/main/skills/fixing-motion-performance/SKILL.md) and [fixing-accessibility](https://github.com/ibelick/ui-skills/blob/main/skills/fixing-accessibility/SKILL.md). Apply web heuristics to native UI, **do not** introduce React or a second view stack.

## Implemented but awaiting native verification

### PR #8
- Pure `ClickyThemePalette.swift` and `ClickyAccentPalette.cs`; validated hex strings and readable preset colours.
- New macOS/Windows keys for accent preset, custom accent, companion-follow and custom companion RGB; existing preferences and identifiers preserved.
- New native General → Colour scheme settings controls; Windows colour dialog and hex validation; SwiftUI ColorPicker.
- WPF existing live resource dictionary and companion refresh paths; SwiftUI dynamic palette consumption.
- On-accent text foreground chosen separately to keep speech bubbles readable.
- Matching Swift Testing and xUnit regression tests. Potential issues must be diagnosed by **compilation**, not attributed to passing colour maths.

### PR #9
- Bubble bounds helpers `BubblePosition.swift` and `OverlayBubbleGeometry.cs` with matching platform tests.
- Screen-edge constraining of welcome, navigation and caption messages.
- Smaller, restrained pointer and bubble shadow effects while keeping existing tracking and navigation architecture.
- Swift 6.2.1 Linux compiled the exact standalone pure geometry helper with warnings as errors; five relevant isolated checks passed. **No actual render smoothness or performance improvements were measured.**

### PR #1
- Permission/capture diagnostics and Stop/approval code. Keep authority/testing review independent of visual changes. A broad per-workspace write checkbox is **not** the same as per-effect confirmation.

## Next work — concrete gates

1. **Mac:** check out PR #8; run `npm ci --prefix app --ignore-scripts`, then `python3 scripts/check_local.py --native`; run Xcode Swift Tests; launch the exact current bundle. Test each preset in Light/Dark/Auto, custom colour picker, settings search, restart persistence, screen sharing and selected-window TCC. Fix actual source/build errors before merging.
2. **Windows:** on a Windows machine with .NET 8 SDK, run `dotnet build app/windows/OpenClicky.Windows.sln -c Debug` and relevant xUnit projects. Exercise WinForms colour chooser within WPF, invalid hex, dynamic WPF-UI resources, actual cursor repaint and restart.
3. **PR #9:** rebase after integrating #8, then inspect genuine screenshots of the companion in both themes and record comparative CPU/GPU/frame timing on 60 and 120+ Hz screens, DPI 100/150/200% and multiple monitors. Verify bubble visibility, reduced-motion status, keyboard/screen reader behaviour, cancellation and no click interception.
4. **PR #1:** separately test ScreenCaptureKit and OS permission denial, window movement, target loss, Stop during pending actions and Gemini approval interruption. Only then review merge.
5. **Icons and installers:** #7 adds an original SVG mark for README, **not** verified replacement native Mac app icon assets or Windows `.ico`. Create properly sized native binaries, verify their real rendered identity, retain existing bundle IDs/data/credentials, and audit signing/updater migration before release.
6. **Usability/accessibility:** test Settings search/filter focus, errors, reduced motion, high contrast, VoiceOver/Narrator, narrow windows and scale. Record native screenshot evidence and fix observed failures. This is not yet certified.
7. **Release:** app updater/feed, macOS signing and notarisation, Windows signing and installation/uninstallation remain blocked on credentials/hardware and must not be represented as shipped.

### Baseline conditions

The continuation that produced this checkpoint ran in a source-only Linux
container with Swift 6.2.1 but **no Xcode, AppKit runtime, .NET SDK, native
Windows GUI or Git access to the private repository**. This local checkout is now
on macOS with Xcode 26.6 and Swift 6.3.3; `dotnet` is not installed. No native
build has yet been run here against PR #8, #9 or #1. The macOS gates above can now
be attempted locally. A WPF cross-build can run on macOS with .NET and Windows
targeting enabled, but `dotnet` is not installed here; Windows runtime and
physical acceptance require a Windows host. Do not treat the Linux smoke tests
as microphone, native colour picker, cursor smoothness or screen-reader
acceptance.

The next step is to run PR #8's macOS build and interaction gates, then reconcile
PR #9 against that result. Keep PR #1 independent and update it to current `main`
before integration. Use evidence-backed changes and merge only after the required
local/platform tests.
