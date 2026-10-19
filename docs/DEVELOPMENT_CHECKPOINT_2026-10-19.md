# Clicky-bro development checkpoint — 19 October 2026

**Purpose:** Record the state after updating and checking the capture/Stop,
theme and companion PRs. This is a development checkpoint, not a release claim.

## Git and pull requests

The code baseline for this acceptance pass was `2a82bdbdbe6b7f465492a3ca3f73e7f1677054e4`,
the merge commit for PR #12. PR #11 merged the refreshed documentation as
`13990561f820b3c6e6ad248410693853b4d0b732`, then PR #13 merged the current
checkpoint correction as `e942ac243b4a41282d95b61217831e0cda8661d1`. The
implementation PRs remain drafts:

| PR | Tested source revision and base | Verified here | Acceptance still open |
| --- | --- | --- | --- |
| [#1 — capture diagnostics and Stop safety](https://github.com/Itskorrah/clicky-bro/pull/1) | `6b5de4a`; base `main` | macOS native suite 710/710; 7 offline checks | Real ScreenCaptureKit/TCC grant, denial and revocation; selected-window movement/closure; Stop during a live pending request |
| [#8 — native theme customisation](https://github.com/Itskorrah/clicky-bro/pull/8) | `30d552f`; base `main` | Settings route native build passed; appearance controls/preset menu observed; integrated #8+#9 test suite 714/714 | Custom picker and restart persistence on Mac; native WPF picker, persistence, DPI and accessibility on Windows |
| [#9 — companion geometry and motion](https://github.com/Itskorrah/clicky-bro/pull/9) | `946ca50`; base `feature/native-theme-customisation-2026-10-19` (#8) | Integrated #8+#9 test suite 714/714; WPF cross-build passed | Native overlay screenshots, motion/input/accessibility checks and measured performance; native Windows overlay/DPI tests |

The implementation source revisions above were pushed as updated draft PRs.
Subsequent mainline and branch-documentation commits did not change the tested
app source. PR #9 is stacked on #8 to keep its diff limited to companion work.
PR #12 and #11 are merged; PRs #1, #8 and #9 are not merged because native
acceptance is incomplete.

## Evidence and boundaries

- `safety-native-final`: **710 passed, 0 failed, 0 skipped**, macOS 26.5 arm64,
  source `6b5de4a`. The seven local offline checks also passed. This verifies
  native unit and offline regressions, not live capture or the real Stop UI.
- `theme-settings-build`: the native Settings route built at `30d552f`.
  `companion-native-final-2`: **714 passed, 0 failed, 0 skipped** on the
  integrated theme/companion tree, including the `CoreGraphics` import committed
  as `946ca50`. The actual General Settings window showed Light/Dark/Auto,
  accent presets, companion-follows-accent, Reset and Reduce Motion controls.
  No preference was changed; custom colour entry and restart persistence were
  not tested.
- The WPF cross-build passed on macOS. The Windows portable core suite reported
  **1,076 passed, 5 failed, 0 skipped (1,081 total)**. The failures are tests
  using Windows drive/path separators or npm-shim assumptions on a macOS host.
  They remain failures and do not establish Windows runtime behavior.
- No Windows computer was available. No TCC permission was granted or changed.
  The 19 October native acceptance checks made no provider requests; the
  earlier 18 October helper/restart acceptance used two live Gemini GUI requests
  (see [TESTING_MACOS.md](TESTING_MACOS.md)). No paid fallback was enabled and
  no GitHub Actions workflow was run. Evidence is stored under ignored
  `.local/evidence/acceptance-2026-10-19/` and is not committed.
- The test-only `import CoreGraphics` fix was compiled and tested as part of the
  714-test source tree, then committed unchanged as `946ca50`.

## Navy UI and icon refresh follow-up

After the checkpoint above, `codex/navy-ui-icon-refresh` was implemented from
PR #9 head `497bba1`. The addendum in [IMPLEMENTATION_2026-10-19.md](IMPLEMENTATION_2026-10-19.md)
records the new Primer-inspired Navy palette, preserved saved themes, regenerated
cross-platform icon, and current evidence: macOS build passed, 717 native tests
passed, WPF cross-build passed, Python suite passed 39 tests, and the Windows
core suite on macOS reported 1,079 passes plus the same five host-specific
failures. It remains a branch candidate; no native Windows or screenshot
acceptance is claimed, and it is not merged into `main`.

## Development workflow

KStack's `native-desktop` route marked the task substantial and required native
platform verification. The scoped KStack router, verifier and ship guidance was
used with the project Evolve build and verify skills. One Luna Max worker
independently reviewed PR evidence and remaining acceptance. KStack remains in
an ignored local checkout; it was not installed globally and does not replace
Codex's subagent mechanism. No host-wide model, authentication or skill settings
were changed. Native builds were kept sequential on this 8 GiB Mac.

## Remaining work

1. Obtain user-selected Screen Recording permission for the exact macOS bundle
   at test time, then verify grant/denial/revocation, selected-window scope,
   target movement/closure and Stop during a pending action. Keep personal
   window contents out of evidence.
2. Finish theme acceptance on both native platforms: custom colours, persistence,
   real UI behavior, mixed-DPI displays and accessibility.
3. Finish companion acceptance on both native platforms: real screenshots,
   boundaries, click-through, cancellation, reduced motion, accessibility and
   before/after performance measurements.
4. Merge PR #1 separately after its safety gates pass. Merge #8 only after its
   own gates, then #9 after its dependent gates. Re-run changed-head checks after
   any rebase or merge.
5. Keep broader connector, artifact-preview, Windows workspace UI, signing,
   notarisation, updater and commercial-service work outside these PRs until
   separately specified and verified.
