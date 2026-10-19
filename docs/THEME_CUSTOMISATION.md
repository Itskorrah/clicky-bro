# Navy UI — native theme customisation

The approved Clicky Bro settings design is the existing macOS SwiftUI and Windows WPF sidebar with its native grouped controls, **not** a replacement dashboard. Light, Dark and Auto remain the same separate appearance preference. This implementation adds optional accent and companion colours without altering existing window geometry or persisted dictation settings.

## User controls

Open **General → Colour scheme**:
- **Navy Slate** is the default for new installs. Existing saved selections remain selected.
- Choose Classic Coral, Azure Blue, Emerald, Violet, Graphite or Custom for the application accent.
- Custom uses the system colour picker and/or a six-digit RGB value.
- **Companion follows accent** is enabled by default. Turn it off to select a different companion tint.
- **Reset colours** restores Navy Slate and companion-follow mode, leaving custom hex values, the user's chosen Light/Dark/Auto appearance and unrelated settings untouched.

macOS offers native `ColorPicker`; Windows offers a native `ColorDialog` alongside a validated `#RRGGBB` input. Invalid Windows input displays an inline error instead of changing saved preferences.

## Architecture

Both platforms persist identical keys:

| Key | Default | Meaning |
| --- | --- | --- |
| `appearance.accentPreset` | `navy` | `navy`, `coral`, `azure`, `emerald`, `violet`, `graphite`, `custom` |
| `appearance.customAccentHex` | `#2B547B` | RGB custom application accent |
| `appearance.companionFollowsAccent` | `true` | Follow app colour rather than a separate pointer tint |
| `appearance.customCompanionHex` | `#2B547B` | RGB custom pointer tint |

Old preferences are never rewritten on load. Valid saved choices such as Classic Coral and saved custom hex values remain in place. Unknown presets or invalid/missing custom colour values resolve visually to the Navy Slate palette, with its companion tint adjusted as needed for contrast; they are not migrated or written back while loading. Reset changes only the accent preset and companion-follow setting. Existing appearance, orb, shortcut, cloud keys, model preferences and bundle identifiers are unchanged.

**Source of truth:** `ClickyThemePalette.swift` and `ClickyAccentPalette.cs` hold matching preset IDs, contrast and input validation rules. They transform arbitrary user choices into colours with at least **4.5:1 contrast against the light canvas (`#F6F8FA`) and highest dark surface (`#21262D`)**. The shared Primer-inspired surfaces use `#F6F8FA` / `#FFFFFF` in Light and `#0D1117` / `#161B22` / `#21262D` in Dark, with cool-gray borders and readable primary, secondary and tertiary text. Companion bubble foreground colour is also selected for contrast against its own background. These calculations do not certify contrast against arbitrary application windows beneath the overlay or every possible system material; native screenshot and accessibility review remain necessary.

On macOS, the `DS.Colors.accent` and `overlayCursorColor` computed colours read the approved keys; SwiftUI settings and companion state refresh on changes. On Windows, `MainWindowTheme` updates the actual WPF-UI resource dictionary values; the overlay updates triangle/waveform/spinner and bubble brushes without rebuilding windows. Both clients retain native system-appearance handling.

## Verification boundary

**Previously recorded evidence (before this Navy refresh):** the native macOS Settings route built at theme head `30d552f`. The latest recorded integrated theme-plus-companion Swift suite passed **714 tests, 0 failed, 0 skipped** on the earlier #8+#9 source tree. The real General Settings window was inspected through accessibility; Light/Dark/Auto, preset menu, companion-follows-accent, Reset and Reduce Motion controls were present. The WPF cross-build passed on macOS at theme head `30d552f`; its portable core suite reported **1,070 passed, 5 failed, 0 skipped (1,075 total)**, with the same five macOS path/shim failures reproduced in the later #8+#9 run. Those results do not verify this Navy refresh or native Windows behavior.

**Navy refresh verification — 19 October 2026:** the macOS app build passed with an existing Info.plist build-phase warning, and the native suite passed **717 tests, 0 failed, 0 skipped** on macOS 26.5 arm64. The WPF project cross-build passed on macOS with 0 errors and one `WFAC010` high-DPI manifest warning. The portable Windows core suite reported **1,079 passed, 5 failed, 0 skipped (1,084 total)**; the five failures are the known Windows path/PATHEXT/npm-shim assumptions while running on macOS, so they are not Windows passes. The repository's Python suite passed **39 tests**. Swift parsing, XAML XML parsing, icon PNG/ICO dimension checks and `git diff --check` also passed. These results do not replace native Windows visual/accessibility acceptance.

Still open: custom picker interaction and persistence across restart on macOS; native Windows colour dialog, stored values, mixed-DPI and multi-monitor rendering, keyboard order and Narrator; and real redacted screenshots of the app and companion in each theme. Windows native acceptance is deferred because no Windows PC was available. Keep any PR in draft until its applicable acceptance checks are complete.

Before a general release:
1. Compile on a Mac with Xcode and a Windows machine with the .NET 8 SDK; run the full local verifier and project-level tests.
2. Switch each preset and custom colours under Light/Dark/Auto. Verify updates in sidebar, forms, orb and floating pointer without restart or state loss; check selected/focus/high-contrast controls.
3. Restart and update OS appearance; validate persistence, system theme follow and contrast on both.
4. Check invalid preference values, revocation/recovery, multi-monitor changes and reduced-motion transitions.
5. Record genuine redacted UI screenshots for light/dark and custom themes; never substitute the HTML design reference for a native acceptance capture.

This implementation deliberately keeps the existing layout and does not install a web framework or ship another dashboard.
