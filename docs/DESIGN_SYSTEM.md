# Clicky Bro Classic — native design contract

**State:** native design-token foundation and a proposed customisable Classic theme implementation, 19 October 2026. The native customisation feature is not accepted until compiled and tested on both operating systems. No replacement of the existing settings layout is authorised.

## Product principle

A quiet, friendly desktop assistant. One primary action at a time. When a person shares a window, records audio, authorises a file write or waits on a model, the UI explains what is happening and offers an effective way to stop. No decorative cards that look actionable but do nothing, fake metrics, or always-on visual noise.

This work is **inspired by the simplicity of HeyClicky**, not an asset/branding/layout copy. Do not ship competitor artwork, mascot animation, marketing claims or proprietary fonts. Preserve the adopted OpenClicky attribution.

## Tokens

The Azure preset reference is [Azure tokens](../design/tokens.json), with matching declarations in the original code. The new adjustable accent uses native persisted preference keys and separate palette resolvers, detailed in [THEME_CUSTOMISATION.md](THEME_CUSTOMISATION.md):

- macOS: [DesignSystem.swift](../app/macos/OpenClicky/OpenClicky/DesignSystem.swift), DS.Colors (adaptive to the active NSAppearance)
- Windows C#: [Theme/DS.cs](../app/windows/src/OpenClicky.Windows/Theme/DS.cs), AzureLight and AzureDark
- Windows XAML: [OpenClickyTheme.xaml](../app/windows/src/OpenClicky.Windows/Theme/OpenClickyTheme.xaml), ClickyBro.Azure.Light/Dark named resources

The token-parity and contrast checks are in [test_azure_palette.py](../tests/test_azure_palette.py). These tests are **static design-contract checks**, not native app screenshot or compiled-WPF evidence.

| Role | Light | Dark | Guidance |
| --- | --- | --- | --- |
| Canvas | #F7FAFF | #0B1220 | Window/app canvas; macOS may retain vibrancy |
| Surface | #FFFFFF | #172338 | Panels, cards, app composer |
| Raised | #EFF6FF | #1D2B44 | Selection and elevated surfaces |
| Primary text | #0F172A | #F8FAFC | Essential labels, headings |
| Secondary text | #64748B | #A8B6CA | Explanatory copy, captions |
| Border | #DEE7F3 | #334155 | Dividers, controls, subtle separation |
| Accent | #2563EB | #60A5FA | Primary action, keyboard focus, selected navigation |
| Pointer | #3B82F6 | #3B82F6 | Distinct overlay target indicator |

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
