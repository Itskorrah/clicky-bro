# Test clicky-bro on Windows

A Windows 11 host was available on 19 October 2026, but the required .NET SDK
was missing, so the WPF client could not be built or launched. Native Windows
visual, interaction and accessibility acceptance has not yet been performed.
Earlier WPF builds and portable-core test runs on macOS do not count as Windows
acceptance. Use the [Windows Codex handoff](../CODEX_WINDOWS.md) to continue.
The repository contains a native Windows client and shared TypeScript agent,
not a macOS executable port.

## Build and run

On a Windows 11 x64 PC, install Git, Node.js 24 and the .NET 8 SDK. Download or
clone this private repository while signed in as an authorized GitHub user.
Open PowerShell in its root folder:

```powershell
npm ci --prefix app --ignore-scripts
npm run build --prefix app --workspace agent
dotnet build app/windows/OpenClicky.Windows.sln -c Debug
dotnet test app/windows/tests/OpenClicky.Core.Tests/OpenClicky.Core.Tests.csproj -c Debug
dotnet run --project app/windows/src/OpenClicky.Windows -c Debug
```

The program is named `clicky-bro.exe`; internal project/namespace names retain
OpenClicky for compatibility. The client uses its own `.clicky-bro` identity and
settings under your user profile. Keep an existing OpenClicky/HeyClicky install's
settings separate; no migration is automatic.

Provider checks are optional; the app build and offline checks do not require a
Gemini key. Only run a live provider check when the user's already-authorized
free usage is confirmed. A free-model allowlist is not a billing cap. Do not
enable billing or paid fallback; skip provider checks if the available free
usage cannot be confirmed. Never paste a key into a Git-tracked file or report.

If that optional boundary is satisfied, enter your own Gemini key in the app's
account/provider settings and choose `gemini-3.5-flash-lite`. Use the Windows
system voice and Windows speech input for initial checks. Do not enable billing.

If you want to use the shared agent, set its command to Node plus the absolute
path to `app/agent/dist/cli.js` in this checkout. Use a new empty agent workspace.
Gemini requests use the native Gemini runtime; no developer Codex sign-in or
OpenAI key is required. The default CLI command is `clicky-bro`, which is not
installed globally by the build above. In `%USERPROFILE%\.clicky-bro\shell.json`,
merge these nonsecret fields with the existing settings, using your actual paths:

```json
{
  "cliCommand": [
    "C:\\Program Files\\nodejs\\node.exe",
    "C:\\your-checkout\\app\\agent\\dist\\cli.js"
  ],
  "workspace": "C:\\Users\\you\\clicky-bro-workspace",
  "answerSource": "gemini",
  "answerModels": {
    "gemini": "gemini-3.5-flash-lite"
  }
}
```

Alternatively, an explicitly configured local key JSON file containing an
`api_key` field can be supplied with `CLICKY_BRO_GEMINI_KEY_FILE` before launch.
The CLI and Windows client accept that file; keep it outside Git and restrict
its Windows file permissions to your user. Do not send its contents in a report.
The native app otherwise stores settings/keys in the private user settings file
above. Its app data is `%LOCALAPPDATA%\clicky-bro`; no automatic upstream migration
or updater is enabled.

For an explicitly authorized workspace-only file test, run this from a terminal
with your private Gemini key file configured (this consumes free-model requests):

```powershell
node app/agent/dist/cli.js run "Create hello.txt containing hello" --cwd "$HOME\clicky-bro-workspace" --allow-workspace-writes --events
```

Omit `--allow-workspace-writes` to verify that the same write is denied. The flag
grants workspace writes for that CLI invocation; it does not authorize shell or
desktop actions. The native desktop action lane instead shows Allow once prompts.

## Acceptance checklist

Use disposable windows/documents, never personal or financial applications.

1. Launch and quit twice. Confirm settings/history are preserved and the old
   HeyClicky app's settings remain unchanged.
2. Ask a text question. Confirm the answer, provider/model and a clear failure
   if the key is invalid or quota is exhausted.
3. Verify the exact capture scope shown by the Windows client before sharing.
   macOS's chosen-window picker does not establish the Windows capture contract.
4. Try visual pointing with two monitors, different display scales, duplicate
   button labels and a moved window. Confirm position and refusal on ambiguity.
5. Test microphone input, system speech and dictation into a disposable editor.
   Move focus mid-dictation; confirm it does not paste into an unrelated window.
6. Keep Agent mode off for teaching. Enable it deliberately for a narrow action,
   inspect the native per-action permission window. Cancel must leave the target
   unchanged; Allow once permits only that proposed action. Close the prompt or
   use Stop while it is open, and verify no action runs afterward.
7. Run a harmless workspace file task through the agent. Denied writes must not
   modify files. Explicitly allowed writes must stay inside that workspace.
8. Disconnect the network or use a controlled fake provider. Confirm failure,
   saved work and cancellation rather than fabricated completion.

Report the app version, Windows version, monitor scales, exact trigger and any
sanitized error message. Do not share API keys or screenshots of private data.

## Present limits

Cross-target compilation is not native Windows acceptance. Some upstream core
tests contain Windows-specific path assumptions and fail when run on macOS;
baseline and adopted results are recorded in BUILD_STATUS.md. The added macOS
Helpers/Memory/Routines workspace window is not yet implemented as the same
Windows UI. Connected account services and general MCP execution through the
new Gemini runtime are not claimed working without explicit configuration.

## 18 October Windows-source checks on macOS (historical)

On 18 October 2026, the Windows core suite ran on the macOS development host
with the pinned .NET SDK 8.0.426:

```sh
DOTNET_CLI_HOME=.local/dotnet-home DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 \
  .local/dotnet/dotnet test app/windows/tests/OpenClicky.Core.Tests/OpenClicky.Core.Tests.csproj \
  --no-restore --verbosity quiet -m:1 \
  --logger 'trx;LogFileName=windows-final-core.trx' \
  --results-directory .local/evidence/windows-agent
```

Result: 1,066 passed, 5 failed, 0 skipped, 1,071 total. The five failures are
the same drive-letter, `PATH`, `PATHEXT` and npm-shim assumptions recorded for
the untouched upstream baseline; they were not skipped or weakened. All nine
new cancellation, field-identity and clipboard-restoration regressions passed.
The machine-readable result is ignored under
`.local/evidence/windows-agent/windows-final-core.trx`.

The matching baseline failures are:

- `OpenClicky.Core.Tests.Answers.AnswerProviderPlanTests.ProcessEnvironmentDropsPlanOverridesAndPutsTheExecutablesFolderFirst`
- `OpenClicky.Core.Tests.Answers.AnswerProviderPlanTests.LocatingTriesCommonDirectoriesInOrder`
- `OpenClicky.Core.Tests.Answers.PlanCliLaunchTests.AnNpmShimRunsItsScriptWithNode`
- `OpenClicky.Core.Tests.Answers.AnswerProviderPlanTests.ClaudeCodeStreamsTextDeltasAndReturnsTheResult`
- `OpenClicky.Core.Tests.Answers.AnswerProviderPlanTests.ThePathIsSearchedInOrderWithPathExtAndAnExeBeforeACmd`

The first WPF cross-build attempt used relative `DOTNET_CLI_HOME=.local/dotnet-home`
and stopped with `NETSDK1064` for `CommunityToolkit.Mvvm` 8.3.2. The package was
already present in the isolated cache, while generated `project.assets.json`
recorded relative package-folder and NuGet-config paths. Restoring with absolute
paths to that same cache corrected the assets. The final-source cross-build then
passed with zero errors and one inherited `WFAC010` high-DPI manifest warning.
The restore also requires `EnableWindowsTargeting=true` on macOS:

```sh
DOTNET_CLI_HOME=/Users/korrah/Documents/ChatGPT/clicky-pal/.local/dotnet-home \
NUGET_PACKAGES=/Users/korrah/Documents/ChatGPT/clicky-pal/.local/dotnet-home/.nuget/packages \
DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 \
.local/dotnet/dotnet restore app/windows/src/OpenClicky.Windows/OpenClicky.Windows.csproj \
  --configfile /Users/korrah/Documents/ChatGPT/clicky-pal/.local/dotnet-home/.nuget/NuGet/NuGet.Config \
  --verbosity minimal --disable-parallel -p:EnableWindowsTargeting=true

DOTNET_CLI_HOME=/Users/korrah/Documents/ChatGPT/clicky-pal/.local/dotnet-home \
NUGET_PACKAGES=/Users/korrah/Documents/ChatGPT/clicky-pal/.local/dotnet-home/.nuget/packages \
DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 \
.local/dotnet/dotnet build app/windows/src/OpenClicky.Windows/OpenClicky.Windows.csproj \
  -p:EnableWindowsTargeting=true --no-restore --verbosity quiet -m:1
```

An earlier cross-build and self-contained publish preceded the latest source
repairs; that publish folder is stale and does not verify this source. No Windows
hardware, capture, audio or input test has run.

## 19 October earlier theme and companion checks on macOS (historical)

The PR #8 theme branch at `30d552f` and the integrated PR #8/#9 branch at
`946ca50` were checked on the macOS development host. The WPF cross-build passed.
The portable core suite reported **1,076 passed, 5 failed, 0 skipped (1,081
total)**. All five failures exercise Windows-specific drive paths, path
separators, `PATHEXT` or npm-shim behavior while executing on macOS. The failures
are retained in the test report; no production code or tests were weakened to
hide host differences. This result is neither a native Windows test pass nor a
reason to claim the five tests pass on Windows.

No Windows PC was available during this macOS verification pass. Native WPF
colour dialog, settings persistence, companion rendering, mixed-DPI monitors,
screen reader, keyboard, capture, audio and input acceptance remain pending.
The [Windows handoff](../CODEX_WINDOWS.md) contains the continuation steps.
Reports for this run are under ignored `.local/evidence/acceptance-2026-10-19/`.

## 19 October navy and icon checks on macOS (latest recorded)

The navy/icon source at 210ec8e was checked on macOS. The native macOS suite
passed **717/717**; the Python suite passed **39/39**; focused palette checks
passed **7/7**. The WPF cross-build completed with **0 errors** and one inherited
WFAC010 high-DPI manifest warning. The Windows portable core suite, run on
macOS, reported **1,079 passed, 5 failed, 0 skipped (1,084 total)**. Those five
failures depend on Windows paths or npm-shim behavior on a macOS host; they are
not a Windows pass. GitHub reported no checks for PR #9 at that time.

Native Windows theme, icon, overlay, DPI, keyboard, Narrator, capture, audio and
input acceptance remain open. No Windows hardware check is claimed. See
[CODEX_WINDOWS.md](../CODEX_WINDOWS.md) for the continuation checklist.

## 19 October 2026 native Windows attempt

The required initial `git status --short --branch` reported `## No commits yet
on master`; the worktree had no local files or commits to preserve. After adding
the supplied `origin` and checking the current remote, `main` was fetched and
checked out at `4535f2c74b733f39de1406be79e36ca555b9f454`. The automated checks
ran against this source plus the README, verifier and focused-test changes
listed below. That exact tested tree was committed as
`06ee376a41ac89035c8bdb5097304909b56c5377` (parent `4535f2c`); the status and
handoff documentation is a separate follow-up.

**Device and display:** Windows 11 Pro, version `10.0.26200`, build `26200`,
x64; Intel Core i7-10700F at 2.90 GHz; NVIDIA GeForce RTX 3070. Windows Forms
reported two logical 1920x1080 displays. WMI separately reported 2560x1440 at
143 Hz, and `HKCU:\Control Panel\Desktop\LogPixels` was `120` (125% system
scaling). These APIs disagree about the display mode; physical monitor
identity, per-monitor scaling and active refresh rate were not independently
settled. No app performance measurement was possible.

**Toolchain:** Node.js `v24.1.0`; Python `3.13.5`. `dotnet --info` showed only
the .NET 5.0.4 host/runtime and no installed SDK; `dotnet --list-sdks` was
empty. Windows Package Manager listed Microsoft .NET SDK `8.0.426`, but its
user-scope install reported `No applicable installer found`. A direct local SDK
download attempt could not reach Microsoft's endpoints because the HTTPS
connection was reset. No machine-scope install or global settings change was
made.

**Build and automated checks:**

| Command or check | Result |
| --- | --- |
| `npm ci --prefix app --ignore-scripts` | Passed; installed 299 packages. npm reported 7 audit findings (1 moderate, 6 high); no audit fix was run. |
| `npm run build --prefix app --workspace agent` | Passed. The Windows verifier also passed agent typecheck/build, backend typecheck and ESLint. |
| `dotnet build app/windows/OpenClicky.Windows.sln -c Debug` | Failed to start because no compatible .NET SDK is installed. |
| `dotnet test app/windows/tests/OpenClicky.Core.Tests/OpenClicky.Core.Tests.csproj -c Debug` | Failed for the same missing SDK. The verifier skipped `windows-core-tests` and recorded `dotnet SDK unavailable (installed runtimes do not include an SDK)`. |
| `py -3 -m unittest discover -s tests -v` | Failed: 43 tests total, 33 passed, 1 failed, 8 errors, 1 skipped. The failure expects POSIX mode `0600`; the errors are Windows-incompatible `os.getuid`/POSIX ownership assumptions in `scripts/dev.py`. These were not weakened. |
| `py -3 -m unittest discover -s tests -p test_check_local.py -v` | Passed 9/9, including Windows npm shim resolution, missing-SDK skip and Unicode-output handling. |
| `py -3 -m unittest discover -s tests -p test_public_branding.py -v` | Passed 3/3 after making source reads explicitly UTF-8. |
| `npm run test --prefix app --workspace agent` (also run by the Windows verifier) | Failed. Direct diagnostics reported 28 failed, 101 passed, 4 skipped, plus 11 unhandled errors. Failures include attempts to spawn POSIX `.bin/tsx`/fake `.sh` files and Unix-specific path, shell and symlink assumptions. |
| `npm run test --prefix app --workspace backend` | Failed: 261 passed, 1 failed out of 262. The failed skill checker found 17 bundled documents missing its required `Layout`, `Common tasks`, `Pointing hints` and `Gotchas` sections. |
| `py -3 scripts/check_local.py --windows --report .local/evidence/windows-2026-10-19/local-verifier-final.json` | Completed with exit code 1: agent typecheck/build, backend typecheck and ESLint passed; root Python, agent tests and backend tests failed; Windows core tests were skipped because the SDK is absent. |

The verifier was repaired during this run to resolve Windows `npm.cmd` through
Node without a shell, detect runtime-only .NET installs before starting an SDK
command, and decode subprocess output as UTF-8 with replacement. The README now
links the editable vector mark, and the branding test reads UTF-8 source files
explicitly. No provider or billing checks ran.

The Windows icon generator ran and wrote an ignored evidence file:
`.local/evidence/windows-2026-10-19/windows-regenerated.ico`. The checked-in
and generated ICO both contain 16, 20, 24, 32, 40, 48, 64, 96, 128 and 256 pixel
entries. A visual comparison is saved as
`.local/evidence/windows-2026-10-19/icon-sizes-comparison.png`. This validates
the standalone icon assets and generator only; the app, taskbar and tray were
not built or inspected.

**Native acceptance status:**

| Acceptance area | Result |
| --- | --- |
| Theme controls: Navy default and saved values; all presets/custom colour; Light/Dark/Auto; valid/invalid hex; native picker; follow-accent/custom tint; Reset and restart persistence | Not run; the app was not built or launched. No user settings were touched. |
| Theme keyboard focus, contrast and Narrator | Pending; no native app surface was available. |
| Mixed-DPI monitor behavior | Pending. Display API readings conflicted, and no per-monitor DPI movement test ran. |
| App/taskbar/tray icon at real Windows sizes | Standalone ICO entries and the Windows generator were inspected at 16, 32, 48 and 256 px; actual app/taskbar/tray rendering remains pending. |
| Sanitized screenshots of welcome, caption and navigation overlays | Not captured; no app overlay was running. |
| Click-through, interaction, cancellation, keyboard/screen-reader behavior, Reduce Motion, edge placement and multiple monitors | Pending; not run. |
| CPU/GPU and frame-time baseline/comparison | Not measured; no app process or overlay was available. No performance claim is made. |
| Broader baseline: launch/quit, persistence, capture scope, dictation/focus, action approval/refusal/Stop, workspace boundaries and failure recovery | Pending; no app run. Disposable-window/file fixtures were not created and no account/provider state was changed. |

The machine-readable verifier summary is in ignored
`.local/evidence/windows-2026-10-19/local-verifier-final.json`. There are no
screenshots of the running app because it never launched. Continue with the
.NET 8 SDK installed, then work through every native item above and the complete
[Windows handoff](../CODEX_WINDOWS.md) checklist. Keep Windows evidence separate
from the macOS-only checks recorded earlier.
