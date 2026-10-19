# Native design and cursor development checkpoint — 19 October 2026

**Purpose:** Recover the work after a ChatGPT execution timeout without losing scope, merging unverified native changes, or reopening unrelated work. Treat this file as a dated implementation ledger, not a release claim.

## Current GitHub state

| PR | Status | Verified scope |
| --- | --- | --- |
| [#7 — public Clicky Bro branding](https://github.com/Itskorrah/clicky-bro/pull/7) | **Merged to main** (`652784ea590bb45882c505e3c65ab9cd6a4016ad`) | User-facing title, tray, permission and welcome string read-back; original SVG logo present in README |
| [#8 — native colour customisation](https://github.com/Itskorrah/clicky-bro/pull/8) | **Draft, unmerged** | Isolated Swift palette compilation, accent contrast assertions; source review, but no current native project build |
| [#9 — cursor geometry and visual polish](https://github.com/Itskorrah/clicky-bro/pull/9) | **Draft, unmerged** | Pure Swift bubble placement compiled on Linux and passed 5 isolated assertions; no native overlay acceptance |
| [#1 — capture diagnostics and agent Stop](https://github.com/Itskorrah/clicky-bro/pull/1) | **Draft, unmerged** | Source work from prior independent branch; changes affect authority and permission boundaries, and **must not be bundled with cosmetic PRs** |

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

The source-only Linux container has Swift 6.2.1 but **no Xcode, AppKit runtime, .NET SDK, native Windows GUI or access to the private repository via git/network**. GitHub connector fetch/update was used to push. Do not claim the Linux smoke tests validate microphone capture, native colour picker, cursor smoothness or screen reader accessibility. Historical 18 October tests listed elsewhere predate these changes.

The next assistant/agent should **continue implementation and verification** rather than restating the design plan. Use evidence-backed small commits and merge only after the required local/platform tests.
