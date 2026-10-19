# Navy UI and app icon refresh — 19 October 2026

This addendum records the user-requested GitHub-inspired navy UI and icon work. The implementation is on `codex/navy-ui-icon-refresh`, based on integrated PR #9 head `497bba1` (which includes PR #8's custom theme controls). It is not merged into `main`; PRs #8 and #9 remain drafts pending their own platform acceptance.

## What changed

- Added a Primer-inspired palette: light `#F6F8FA` canvas, dark `#0D1117` canvas, layered surfaces, cool-gray borders and readable text. Navy Slate (`#2B547B` light, `#80A9D4` dark) is now the accent when no choice is saved.
- Preserved valid saved presets, including Classic Coral, plus valid custom accent and companion hex values. Reset selects Navy Slate and follow-accent mode while retaining saved custom hex and Light/Dark/Auto appearance.
- Applied the surface and focus treatment to native macOS and WPF settings, including visible Windows hover, pressed and keyboard-focus states.
- Replaced the beveled coral-ring/pointer icon with a flat navy tile, cobalt assistant face and cyan spark. The editable deterministic source generates the macOS PNGs and Windows ICO; the macOS status item and Windows app/tray now use the same tiled composition. Removed unused Windows ring-and-pointer geometry.
- Unified sidebar navigation icon colours with the selected accent on both platforms, with contrasting glyph colour for light and dark accents. The Windows icons refresh when the accent changes.
- Updated the shared token manifest, design contract, customization notes and palette parity tests. Two generated concepts informed the icon direction; neither raster concept is shipped.

## Stack and workflow

KStack was run from `.local/tools/kstack-20261019` with the `native-desktop` profile. It classified this as substantial/elevated-risk native UI work and required verification. Its optional UI-skill candidates were not installed. Evolve tracked the icon and UI tasks. Two focused implementation workers were requested with Luna/max settings and disjoint icon/theme ownership; an independent reviewer then checked the integrated changes. The host did not expose recorded turn metadata for independent confirmation. Reviews caught and fixed AppKit template rendering overriding the full-colour status icon, missing custom-colour fallbacks, legacy sidebar tints and unused ring geometry.

## Verification

- macOS native build and tests: **717 passed, 0 failed, 0 skipped**, macOS 26.5 arm64. Result bundle: `/Users/korrah/Library/Caches/clicky-bro/DerivedData-local/Logs/Test/Test-OpenClicky-2026.10.19_20-45-57-+1100.xcresult`.
- WPF cross-build on macOS: passed, 0 errors and one existing `WFAC010` high-DPI manifest warning.
- Windows core tests executed on macOS: **1,079 passed, 5 failed, 0 skipped (1,084 total)**. The five failures are the known Windows drive/path, `PATH`/`PATHEXT` and npm-shim assumptions under macOS. Report: ignored `.local/evidence/navy-icon-refresh/navy-icon-final-core-after-sidebar.trx`. This is not a Windows test pass.
- Root Python suite: **39 passed**. Swift syntax parse, XAML XML parse and `git diff --check` passed. The PNG manifest and all ten Windows ICO dimensions were validated; the icon preview was inspected at 16 px and 32 px against light and dark surfaces.
- The icon preview was inspected at 16 px and 32 px against light and dark surfaces. It remains legible at both sizes.

## Still needed

There was no Windows machine for native WPF appearance, colour-dialog, persistence, mixed-DPI, keyboard or Narrator acceptance. `pwsh` was also unavailable, so the Windows PowerShell icon generator was source-reviewed but not executed; the checked-in ICO was generated from the shared master with Pillow and its ten dimensions were validated. The macOS app opens to an OS system dialog in the current desktop session, so the settings window, custom picker and restart persistence could not be inspected safely; a same-state native screenshot was not captured. Keep the feature PRs in draft and do not merge them to `main` until these platform checks are completed.
