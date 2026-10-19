# clicky-bro: current position and next acceptance work

Updated 19 October 2026 after the Windows build attempt. The theme, navy UI,
companion and icon stack is integrated into `main` ahead of its remaining native
acceptance gates. The Windows host was available, but missing .NET SDK blocked
the native build and app launch. This integration does not count as platform
acceptance or release approval. Capture and Stop safety PR #1 remains separate.
No desktop release or full HeyClicky parity is claimed.

The [Navy UI and icon refresh](IMPLEMENTATION_2026-10-19.md) and theme controls
are on `main` at source commit `5d2bcfee3639c58daca873a43ca76404c68f57d8`.
GitHub marked PR #8 merged when its head reached `main`; PR #9 remains an open
draft against the earlier theme branch even though its source is already in
`main`. Native Windows, custom-colour persistence and full visual acceptance
remain next.

## Current position

- The theme and companion stack was fast-forwarded to `main` at
  `5d2bcfee3639c58daca873a43ca76404c68f57d8` at the user's request, before
  native acceptance was complete. The Windows session fetched current `main`
  and began from `4535f2c74b733f39de1406be79e36ca555b9f454`. The tested
  verifier/branding fixes are in `06ee376a41ac89035c8bdb5097304909b56c5377`;
  this documentation follow-up records the results and pending acceptance.
- PR #1 is updated to `6b5de4a`: **710 macOS native tests passed**, 0 failed and
  0 skipped; seven offline checks passed. The code and unit suite are ready for
  review, while live selected-window capture, TCC denial/revocation and a real
  pending-request Stop interaction remain open.
- PR #8's theme controls are now included in `main` (the final UI stack source
  is `5d2bcfe`; GitHub marked PR #8 merged). The macOS Settings route builds and the native
  Swift suite on the integrated #8+#9 source passed **714/714**. The actual
  Settings window and its appearance controls were inspected without changing
  preferences. Its Windows core run on macOS was 1,070/1,075. Custom colour
  entry, restart persistence and native Windows acceptance remain open.
- The PR #9 source, including the navy UI/icon refresh, is included in `main`
  at `5d2bcfe`; PR #9 still appears as an open draft against the prior theme
  branch. The latest macOS native suite passed **717/717**; the WPF cross-build
  passed with 0 errors; focused palette tests passed **7/7**. The full portable
  Windows core suite reports **1,079 passed, 5 failed, 0 skipped (1,084 total)**
  on macOS. The same five failures assume Windows path separators, drive paths
  or npm shims while running on macOS. These are reported failures, not Windows
  passes. GitHub reports no checks for the updated PR branch.
- The Windows 11 Pro build-26200 host has an Intel Core i7-10700F and NVIDIA
  GeForce RTX 3070. The native client was not built or launched because no .NET
  SDK was installed and the local download attempt was reset. Node build and
  typechecks passed; the Python, agent and backend suites have documented
  Windows portability or skill-format failures. See the dated results in
  [TESTING_WINDOWS.md](TESTING_WINDOWS.md). No Windows app screenshots or
  performance measurements exist yet.
- The macOS Screen Recording permission was not granted or changed. The 18
  October helper/runtime persistence check used two live Gemini GUI requests,
  as recorded in [TESTING_MACOS.md](TESTING_MACOS.md). This Windows attempt used
  no provider requests or paid fallback, Actions runs or deployments.

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
4. **Complete the remaining gates on `main`.** PRs #8/#9 are integrated before
   their native acceptance gates pass. Keep PR #1 separate. Re-run checks after
   source changes; report actual results and label host-only or skipped checks.
5. **Finish Windows acceptance from `main`.** Install the .NET 8 SDK, fetch
   `main` with `git pull --ff-only`, then follow [CODEX_WINDOWS.md](../CODEX_WINDOWS.md)
   and the pending checklist in [TESTING_WINDOWS.md](TESTING_WINDOWS.md). Record
   the exact tested commit, OS build and actual native evidence. Push verified
   follow-up commits to `main` as authorized.

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
review. An independent reviewer checked the updated PR branches against the
local evidence. Luna Max had been requested, but the host did not expose
effective model metadata for independent confirmation. KStack is a local ignored checkout
and CLI/skill pack; it did not install globally or create a runtime agent swarm.
Native builds were serialized on the 8 GiB Mac. No global model or
authentication settings were changed.

For the 19 October Windows attempt, KStack's local `native-desktop` route and
doctor ran; `verify-project` reported no trusted project verification commands
configured. The local CLI inspected the repository root and `app`, routed the
Windows project to `native-desktop`, and ran `verify-project` and `doctor` using
`.local/kstack-state`; KStack's available skill checks passed. The project
Evolve build and independent verification skills were read and followed. No
worker was delegated because the current thread exposed no effective-model
metadata to verify the requested Luna Max setting. The active model therefore
remains unconfirmed; no global model or authentication setting was changed.
