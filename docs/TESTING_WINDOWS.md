# Test clicky-bro on Windows

Physical Windows testing is deferred by the user. The repository contains a
native Windows client and shared TypeScript agent, not a macOS executable port.

## Build and run

On a Windows 11 x64 PC, install Git, Node.js 24 and the .NET 8 SDK. Download or
clone this private repository while signed in as an authorized GitHub user.
Open PowerShell in its root folder:

```powershell
npm ci --prefix app --ignore-scripts
npm run build --prefix app --workspace agent
dotnet build app/windows/OpenClicky.Windows.sln -c Debug
dotnet test app/windows/tests/OpenClicky.Core.Tests -c Debug
dotnet run --project app/windows/src/OpenClicky.Windows -c Debug
```

The program is named `clicky-bro.exe`; internal project/namespace names retain
OpenClicky for compatibility. The client uses its own `.clicky-bro` identity and
settings under your user profile. Keep an existing OpenClicky/HeyClicky install's
settings separate; no migration is automatic.

In the app's account/provider settings, enter your own Gemini key and choose
`gemini-3.5-flash-lite`. Use the Windows system voice and Windows speech input for
initial checks. Do not enable billing or paste a key into a Git-tracked file.

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

## Latest local Windows-source checks

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
