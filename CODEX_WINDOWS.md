# Windows Codex handoff

Use this file to continue the Clicky Bro work on a real Windows PC. The theme, navy UI, companion and icon stack is now on `main`; this session's main job is native Windows build, regression and acceptance evidence. The source was integrated before all platform gates passed, at the user's direction. That is not a Windows acceptance pass or release approval. Read this with [AGENTS.md](AGENTS.md), [the Windows test guide](docs/TESTING_WINDOWS.md), [the next-steps record](docs/NEXT_STEPS.md) and [the current build status](docs/BUILD_STATUS.md).

> **Latest Windows attempt — 19 October 2026:** the work started from a clean `main` checkout at `4535f2c74b733f39de1406be79e36ca555b9f454`; the verifier and branding changes tested in that session are commit `06ee376a41ac89035c8bdb5097304909b56c5377`. The run was on Windows 11 Pro build 26200. Node typechecks/build and several checks ran, but the Windows client could not be built or launched because no .NET SDK is installed; the direct download was reset and Windows Package Manager had no applicable user-scope installer. This did not complete native UI acceptance. See [the dated Windows evidence](docs/TESTING_WINDOWS.md#19-october-2026-native-windows-attempt).

## Where to continue

- Repository: [Itskorrah/clicky-bro](https://github.com/Itskorrah/clicky-bro)
- Start from `main`. It contains the theme controls and the navy UI, companion and icon work. The UI source landed at `5d2bcfee3639c58daca873a43ca76404c68f57d8`; later handoff documentation may advance `main` beyond that source revision.
- [PR #8](https://github.com/Itskorrah/clicky-bro/pull/8) was marked merged by GitHub when its head reached `main`. [PR #9](https://github.com/Itskorrah/clicky-bro/pull/9) remains an open draft stacked on the theme branch, although its code is already present on `main`; do not check it out to continue the Windows acceptance work.
- PR #1 is independent and covers capture diagnostics and Stop safety.
- Fetch `main` before testing. Keep working on `main` and record the exact tested commit. Do not treat direct integration as completed platform acceptance.

## Start the Windows session

In an existing clone, first preserve any local work. If the working tree is dirty, inspect it and keep those changes; do not reset or clean it.

~~~powershell
git status --short --branch
git fetch origin
git switch main
git pull --ff-only
git rev-parse HEAD
~~~

If the repository is not on the Windows PC yet:

~~~powershell
git clone https://github.com/Itskorrah/clicky-bro.git
cd clicky-bro
git switch main
git pull --ff-only
git rev-parse HEAD
~~~

If GitHub CLI is unavailable, fetch the branch directly:

~~~powershell
git fetch origin
git switch main
git pull --ff-only
git rev-parse HEAD
~~~

Record the actual commit hash and Windows version in the results. Before making changes, read the current [project rules](AGENTS.md), [theme contract](docs/THEME_CUSTOMISATION.md), [implementation record](docs/IMPLEMENTATION_2026-10-19.md) and [current position](docs/NEXT_STEPS.md). The user has authorized continuing work and pushing verified changes to `main`; preserve unrelated local work and report every changed commit.

## Development workflow and model budget

Continue with the user's requested [KStack development stack](https://github.com/Itskorrah/kstack). Check whether a local KStack checkout already exists under .local/kstack. If missing, run git clone https://github.com/Itskorrah/kstack.git .local/kstack, then read its current Windows setup and use its native-desktop workflow. Keep KStack local to this checkout; do not change global Codex, shell, authentication or billing configuration. Use the repository's Evolve audit, build and verify skills. Record which workflow and skills actually ran; a written instruction is not evidence that a tool or active model changed.

Model settings are controlled by the Windows Codex session, not this file. The conversation included a cost concern about GPT-6.1 Sol, while AGENTS.md specifies the project model route. Follow the latest explicit user/session instruction, verify the actual active and delegated model metadata, and do not change global settings or claim that this file switched a model. If workers are delegated, use only models and effort levels authorized by the current AGENTS.md and user instructions, keep them focused, and use at most two.

For the 19 October 2026 session, the user requested GPT-6 Luna Max. The current thread metadata did not expose the effective model or effort, so that choice could not be independently verified. No worker was delegated and no global model setting was changed.

Do not enable paid fallback or billing. A live provider check is optional and should use only an already-authorized, bounded free-model setup. Do not copy a key from another computer, expose credentials, or read developer Codex tokens.

## Build and run

Use Windows 11 x64 with Git, Node.js 24 and the .NET 8 SDK. Python 3.9+ is needed only for the Python suite and local-verifier commands below. Run from the repository root:

~~~powershell
node --version
dotnet --info
npm ci --prefix app --ignore-scripts
npm run build --prefix app --workspace agent
dotnet build app/windows/OpenClicky.Windows.sln -c Debug
dotnet test app/windows/tests/OpenClicky.Core.Tests/OpenClicky.Core.Tests.csproj -c Debug
dotnet run --project app/windows/src/OpenClicky.Windows -c Debug
~~~

Run the repository's documented local verifier as appropriate:

~~~powershell
py -3 -m unittest discover -s tests -v
py -3 scripts/check_local.py --list
py -3 scripts/check_local.py --windows
~~~

Report every failure and skip as it occurred. Do not weaken tests or relabel the five macOS-host-specific failures recorded in earlier reports as Windows failures or passes; the native Windows run will establish its own result.

## Windows acceptance to complete

Use a disposable Windows account/profile if available, disposable windows and a fresh empty workspace. Otherwise preserve the current Clicky Bro profile and unrelated app settings; do not reset, delete or migrate existing state. Keep personal documents, financial apps and credentials out of screenshots and test fixtures.

### PR #8 — theme controls

- On a new profile, confirm Navy Slate is the default. On an existing profile, confirm a saved preset/custom value remains selected.
- Exercise Classic Coral, Azure Blue, Emerald, Violet, Graphite and Custom in Light, Dark and Auto appearance.
- Open the native colour dialog, enter a valid custom colour, then invalid hex. Confirm invalid input shows an error and does not replace the last saved value.
- Exercise Companion follows accent and a separate companion tint. Confirm the navigation/sidebar and companion surfaces repaint without restarting.
- Test Save, Reset and restart. Reset should choose Navy Slate and follow-accent mode while preserving appearance, saved custom hex values and unrelated settings.
- Check hover, pressed, selected, disabled and keyboard-focus states. Navigate without a mouse and inspect with Narrator. Verify text and focus remain legible in both appearances.
- Move between monitors with different scaling (for example 100%, 150% and 200%). Check clipping, sizing, picker placement and overlays before and after moving a window.

### PR #9 — icon, companion and overlays

- Inspect the installed/build-run app icon, taskbar and tray at actual Windows sizes. Confirm the navy tile, assistant face and cyan spark remain legible and are not clipped.
- Capture real, sanitized screenshots of the app and welcome, caption and navigation bubbles. Include edge placement, a smaller display and enlarged text.
- Verify each surface's intended click-through and interaction behavior, dismissal/cancellation and keyboard/screen-reader behavior.
- Toggle Reduce Motion and check that state changes remain understandable without disruptive motion.
- Check mixed-DPI and multi-monitor movement, edge placement and clipping while overlays are visible.
- Measure baseline and changed CPU/GPU use and frame times on the available display refresh rate. Record device, display scale, sampling method and results; do not claim a performance improvement without comparable measurements.

### Windows baseline behavior

Complete the broader checklist in [docs/TESTING_WINDOWS.md](docs/TESTING_WINDOWS.md): launch/quit and persistence; capture scope and stale-target handling; visual guidance; microphone, speech and dictation focus; native action approval, refusal and Stop; workspace write boundaries; and clear recovery on provider or network failure. Keep Agent mode off unless a narrow action specifically needs testing. Use harmless fixtures and verify denied actions leave the target unchanged.

## Still requires a Mac

Windows evidence does not complete the open macOS gates:

- **PR #1:** current-bundle Screen Recording granted, denied and revoked; selected-window capture when a window moves or closes; a real pending-request Stop/cancellation check.
- **PR #8:** native custom colour picker, persistence through restart, appearance changes, contrast and fresh Settings screenshots.
- **PR #9:** fresh native companion screenshots, accessibility and click-through checks, and comparable CPU/GPU/frame-time measurements.

Return to a Mac for these checks. PR #8 is already merged; PR #9 remains an open draft on its former theme branch, and PR #1 remains separate. Do not change those states as part of this Windows follow-up. After acceptance, update the evidence with the exact tested commit and re-run checks whenever source or PR base changes.

## Record and report results

Append a concise Windows result to [docs/TESTING_WINDOWS.md](docs/TESTING_WINDOWS.md) or create a dated evidence note. Include:

- tested branch and full commit hash;
- Windows edition/build, CPU/GPU, monitor count, resolution and scale;
- exact build/test commands, pass/fail/skip totals and relevant error names;
- each manual acceptance item and what happened;
- sanitized screenshots of disposable content only;
- known limitations and any check that could not be performed.

Do not report a cross-build, browser rendering or macOS run as Windows acceptance. The current user authorized verified follow-up commits to `main`; keep PR #9's former branch and PR #1 separate.
