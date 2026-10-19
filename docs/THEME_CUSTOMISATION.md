# Classic UI — native theme customisation

The approved Clicky Bro settings design is the existing macOS SwiftUI and Windows WPF sidebar with its native grouped controls, **not** a replacement dashboard. Light, Dark and Auto remain the same separate appearance preference. This implementation adds optional accent and companion colours without altering existing window geometry or persisted dictation settings.

## User controls

Open **General → Colour scheme**:
- **Classic Coral** is the default, preserving the historic look.
- Choose Azure Blue, Emerald, Violet, Graphite or Custom for the application accent.
- Custom uses the system colour picker and/or a six-digit RGB value.
- **Companion follows accent** is enabled by default. Turn it off to select a different companion tint.
- **Reset colours** restores Classic Coral and companion-follow mode, leaving the user's chosen light/dark appearance and unrelated settings untouched.

macOS offers native `ColorPicker`; Windows offers a native `ColorDialog` alongside a validated `#RRGGBB` input. Invalid Windows input displays an inline error instead of changing saved preferences.

## Architecture

Both platforms persist identical keys:

| Key | Default | Meaning |
| --- | --- | --- |
| `appearance.accentPreset` | `coral` | `coral`, `azure`, `emerald`, `violet`, `graphite`, `custom` |
| `appearance.customAccentHex` | `#D24E2A` | RGB custom application accent |
| `appearance.companionFollowsAccent` | `true` | Follow app colour rather than a separate pointer tint |
| `appearance.customCompanionHex` | `#E8653F` | RGB custom pointer tint |

Old preferences are never rewritten on load. Unknown preset/invalid old colour values fall back to Classic Coral. Existing appearance, orb, shortcut, cloud keys, model preferences and bundle identifiers are unchanged.

**Source of truth:** `ClickyThemePalette.swift` and `ClickyAccentPalette.cs` hold matching preset IDs, contrast and input validation rules. They transform arbitrary user choices into colours with at least **4.5:1 contrast against their designated settings surfaces**. Companion bubble foreground colour is also selected for contrast against its own background. These calculations do not certify contrast against arbitrary application windows beneath the overlay or every possible system material; native screenshot and accessibility review remain necessary.

On macOS, the `DS.Colors.accent` and `overlayCursorColor` computed colours read the approved keys; SwiftUI settings and companion state refresh on changes. On Windows, `MainWindowTheme` updates the actual WPF-UI resource dictionary values; the overlay updates triangle/waveform/spinner and bubble brushes without rebuilding windows. Both clients retain native system-appearance handling.

## Verification boundary

The stand-alone Swift palette implementation passed a Linux Swift compiler and 42 isolated input/contrast/fallback assertions. Matching project tests exist for Swift Testing and xUnit; the full tests are **not executed** without a checkout and native toolchain. There is no verified real macOS or Windows UI run, focus, DPI, high-contrast, screen reader or saved-settings screenshot for this feature yet.

Before a general release:
1. Compile on a Mac with Xcode and a Windows machine with the .NET 8 SDK; run the full local verifier and project-level tests.
2. Switch each preset and custom colours under Light/Dark/Auto. Verify updates in sidebar, forms, orb and floating pointer without restart or state loss; check selected/focus/high-contrast controls.
3. Restart and update OS appearance; validate persistence, system theme follow and contrast on both.
4. Check invalid preference values, revocation/recovery, multi-monitor changes and reduced-motion transitions.
5. Record genuine redacted UI screenshots for light/dark and custom themes; never substitute the HTML design reference for a native acceptance capture.

This implementation deliberately keeps the existing layout and does not install a web framework or ship another dashboard.
