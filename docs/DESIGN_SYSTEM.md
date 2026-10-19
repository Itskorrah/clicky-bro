# Clicky Bro Navy — native design contract

**State:** Navy/Primer-inspired surface and token refresh implemented on `codex/navy-ui-icon-refresh`, 19 October 2026. The macOS app builds and its native suite passes; the WPF app cross-builds on macOS. Native Windows and full native screenshot/accessibility acceptance remain open. No replacement of the existing settings layout was introduced.

## Product principle

A quiet, friendly desktop assistant. One primary action at a time. When a person shares a window, records audio, authorises a file write or waits on a model, the UI explains what is happening and offers an effective way to stop. No decorative cards that look actionable but do nothing, fake metrics, or always-on visual noise.

This work is **inspired by the simplicity of HeyClicky**, not an asset/branding/layout copy. Do not ship competitor artwork, mascot animation, marketing claims or proprietary fonts. Preserve the adopted OpenClicky attribution.

## Tokens

The Navy/Primer-inspired reference is [design tokens](../design/tokens.json), with matching declarations in the native code. The adjustable accent uses native persisted preference keys and separate palette resolvers, detailed in [THEME_CUSTOMISATION.md](THEME_CUSTOMISATION.md):

- macOS: [DesignSystem.swift](../app/macos/OpenClicky/OpenClicky/DesignSystem.swift), DS.Colors (adaptive to the active NSAppearance)
- Windows C#: [Theme/DS.cs](../app/windows/src/OpenClicky.Windows/Theme/DS.cs), PrimerLight and PrimerDark
- Windows XAML: [OpenClickyTheme.xaml](../app/windows/src/OpenClicky.Windows/Theme/OpenClickyTheme.xaml), ClickyBro.Primer.Light/Dark named resources

The token-parity and contrast checks are in [test_primer_palette.py](../tests/test_primer_palette.py). These are **static design-contract checks**, not native Windows or screenshot/accessibility acceptance.

| Role | Light | Dark | Guidance |
| --- | --- | --- | --- |
| Canvas | #F6F8FA | #0D1117 | Window/app canvas; macOS may retain vibrancy |
| Surface | #FFFFFF | #161B22 | Panels, cards, app composer |
| Raised | #F6F8FA | #21262D | Selection and elevated surfaces |
| Primary text | #1F2328 | #E6EDF3 | Essential labels, headings |
| Secondary text | #59636E | #A1AAB4 | Explanatory copy, captions |
| Tertiary text | #66707A | #8B949E | Lower-priority labels and metadata |
| Border | #D0D7DE | #30363D | Dividers, controls, subtle separation |
| Navy accent | #2B547B | #80A9D4 | New/unset preference, keyboard focus and selected navigation |
| Pointer default | #2B547B | #80A9D4 | Default overlay target tint; valid saved custom tint stays selected |

Do not use accent blue as the only indicator of permission/approval, success or failure. Danger and warning states retain distinct semantic colours and text labels.

## Layout directions — acceptance not yet claimed

**Home / start:** One composer with Ask, Dictate and Work modes; selected context chips; recent real runs and latest files; obvious privacy source controls. Do not automatically attach Home screenshots to text questions.

**Companion:** Minimal idle state, labelled listening/transcribing/thinking/speaking/pointing/acting/waiting-for-approval; visible Stop and stop-sharing. Its natural compact HUD remains intentionally always dark even when the app uses light mode. The main window follows the chosen/system appearance.

**Dictation:** Visible engine, network/local label, partial words, clean text and raw transcript access, audio error recovery, lost-focus destination warning, keyboard-only controls. Never claim local-only operation if optional transcript polishing uses a cloud provider.

**Workspace:** Task/run status, actual action approvals, timeline and saved artifacts; distinguish scoped read-only versus file-write authority. Recover existing state after restart before adding features.

**Settings:** Simplify sections, use restrained monochromatic/blue icons, place speech models/download size/privacy and selected-window diagnostics where the user can find them. Avoid ten unrelated bright navigation colours. Separate provider billing/key setup from everyday preferences.

## Typography and interactions

Use native SF system text on macOS and Segoe UI Variable on Windows, not redistributed licensed font files. Suggested size hierarchy: page title 22–28, section 16–18, primary body 13–15, helper copy 12–13, captions at least 11 where legible. Avoid overusing bold. Icons are supporting cues; pair meaningful statuses with text.

Use consistent 8/12/16/24 point spacing, 8–12 point control/card radius, restrained hairline dividers and accent emphasis only where navigation or primary action benefits. Prefer responsive columns and readable line lengths over a fixed 380-pixel app dashboard. Interactive targets must work with keyboard focus, high-DPI scaling and assistive technology.

Keep state changes clear without perpetual loading animation. Honour Reduce Motion, low-power behaviour and system light/dark mode. Do not make device recording feel like an always-on background process.

## UI state acceptance matrix

| Surface | Normal | Failure and interruption |
| --- | --- | --- |
| Onboarding | Current executable permissions/identity; no surprise model download | Denied permission, stale TCC, quit/restart, manual retry |
| Ask | Exactly chosen window or none, visible context | Window moved/closed, permission denied, capture pending, Stop |
| Dictate | Selected input/engine, local/cloud badge | No microphone, no destination, changed focus, Stop/retry |
| Model selection | Installed/available/storage/download progress | Low disk, metered data, cancellation, checksum failure, removal |
| Helpers | Scoped workspace and declared authority | Denial, timeout, concurrent run, restart, quota exhausted |
| Appearance | Follow system/light/dark consistently | High contrast, reduced motion, screen reader, 125–200% scaling |

Before calling the UI redesigned or ready for distribution, capture native screenshots and manual interaction evidence for **each** main surface in both themes. Use a Mac and Windows machine, including a non-primary monitor. This is open work.

## Implementation rules

1. Maintain native SwiftUI/AppKit and WPF. Do not introduce a second cross-platform view framework for cosmetic reuse.
2. Keep semantic tokens aligned and add the token test for every new shared colour. A static XAML colour entry is not a working system-theme switch; wire theme dictionaries before claiming automatic Windows theme switching.
3. Build one complete Home/companion slice with real interactions and explicit error states before migrating every settings form.
4. Validate contrast and keyboard order, then compile and run with real provider/microphone/Screen Recording permissions; do not pass mock snapshots off as app acceptance.
