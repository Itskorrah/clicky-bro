# clicky-bro: current position and next acceptance work

Updated 19 October 2026 after the native acceptance pass. The project has a
working macOS and Windows source tree, but the safety, theme and companion PRs
remain drafts until their platform acceptance gates pass. No desktop release or
full HeyClicky parity is claimed.

The later [Navy UI and icon refresh](IMPLEMENTATION_2026-10-19.md) is on
`codex/navy-ui-icon-refresh`, based on the integrated PR #9 source. Its macOS
build/tests and Windows cross-build pass; native Windows, custom-colour
persistence and full visual acceptance remain next.

## Current position

- The tested code baseline was `2a82bdbdbe6b7f465492a3ca3f73e7f1677054e4`,
  including PR #12. PR #11 and PR #13 later merged documentation updates as
  `1399056` and `e942ac2`.
- PR #1 is updated to `6b5de4a`: **710 macOS native tests passed**, 0 failed and
  0 skipped; seven offline checks passed. The code and unit suite are ready for
  review, while live selected-window capture, TCC denial/revocation and a real
  pending-request Stop interaction remain open.
- PR #8 is updated to `30d552f`: the macOS Settings route builds and the native
  Swift suite on the integrated #8+#9 source passed **714/714**. The actual
  Settings window and its appearance controls were inspected without changing
  preferences. Its Windows core run on macOS was 1,070/1,075. Custom colour
  entry, restart persistence and native Windows acceptance remain open.
- PR #9 is updated to `946ca50` and stacked on #8. The same integrated native
  suite passed **714/714**. WPF cross-builds passed on macOS. The portable
  Windows core suite reports **1,076 passed, 5 failed, 0 skipped** on the
  combined tree; the #8 theme-head run was **1,070 passed, 5 failed, 0 skipped**.
  The same five failures assume Windows path separators, drive paths or npm
  shims while running on macOS. These are reported failures, not Windows passes.
- There was no Windows PC available. The macOS Screen Recording permission was
  not granted or changed. The 18 October helper/runtime persistence check used
  two live Gemini GUI requests, as recorded in [TESTING_MACOS.md](TESTING_MACOS.md).
  The 19 October native acceptance checks used no provider requests or paid
  fallback, Actions runs or deployments.

See [BUILD_STATUS.md](BUILD_STATUS.md) for evidence and boundaries and the
[19 October checkpoint](DEVELOPMENT_CHECKPOINT_2026-10-19.md) for the exact PR
heads and integration status.

## Remaining acceptance, in order

1. **Capture and Stop (PR #1, keep separate).** On the exact current macOS app
   bundle, test Screen Recording granted, denied and revoked; capture only a
   disposable selected window; move or close it during capture and verify a
   clear failure with no display fallback. Stop while a request/action is
   pending and confirm no later effects. Exercise cancellation and refusal in
   the native helper flow. Do not include personal window contents in evidence.
2. **Themes (PR #8).** On macOS, exercise all presets and custom colour input in
   Light/Dark/Auto, companion-follow and custom tint, Reset, Reduce Motion,
   contrast, restart persistence and settings search. On Windows, exercise the
   native colour dialog, invalid hex, saved values, pointer repaint, mixed-DPI
   monitors, keyboard use and Narrator.
3. **Companion (PR #9).** Capture actual native screenshots of welcome,
   caption and navigation bubbles near every edge, on a small display and with
   oversized text. Verify click-through, cancellation, keyboard/screen-reader
   behavior and Reduce Motion. Measure CPU/GPU and frame times before and after
   on 60/120/144 Hz screens; do not claim a performance improvement until the
   measurements support it. Repeat WPF overlay and mixed-DPI checks on Windows.
4. **Integrate only after the corresponding gates.** Keep #1 independent. Merge
   #8 after its Mac and Windows acceptance; then merge #9 against #8 after its
   own native acceptance. Re-run the relevant current-head checks after any
   changed source or base. Keep PRs draft while a gate is pending.
5. **Keep the primary checkout on `main`** after this pass. The documentation
   reconciliation has merged; continue the remaining platform acceptance in the
   attached feature worktrees.

## Product work after these PRs

- Bring Helpers, Memory and Routines UI/persistence to Windows and accept them on
  the actual Windows client.
- Add one connector at a time with scoped authentication, explicit denial and
  revocation behavior, and real action receipts. General MCP and multi-account
  support are not implied by the adopted source.
- Add safe artifact previews, provenance, helper follow-up and deliberately
  designed restart/resume behavior.
- Complete the mapped feature crosswalk through observed workflows. Accounts,
  plans, teams, billing, signed installers, notarisation and trusted updates
  require separate implementation and acceptance; none is shipped by these PRs.

## Development workflow used

KStack's `native-desktop` route identified native platform acceptance as a
required verification step and selected focused routing/verification guidance.
The project Evolve build and verify skills scoped implementation and independent
review. One Luna Max reviewer checked the updated PR branches against the local
evidence. KStack is a local ignored checkout and CLI/skill pack; it did not
install globally or create a runtime agent swarm. Native builds were serialized
on the 8 GiB Mac. No global model or authentication settings were changed.
