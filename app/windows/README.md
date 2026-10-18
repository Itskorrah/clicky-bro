# clicky-bro for Windows

Native C# / .NET 8 / WPF desktop client, adopted from Prasanth OpenClicky.
Internal project, namespace and asset filenames retain their upstream names.
Runtime data, CLI settings, window identity, login-item registry value, updater
opt-in and display name belong to clicky-bro. Attribution and upstream license
remain in the repository.

The maintained build, provider setup and physical acceptance checklist is
[Test clicky-bro on Windows](../../docs/TESTING_WINDOWS.md).

## Build from the repository root

On Windows 11 x64 with Node.js 24 and .NET SDK 8:

```powershell
npm ci --prefix app --ignore-scripts
npm run build --prefix app --workspace agent
dotnet build app/windows/OpenClicky.Windows.sln -c Debug
dotnet test app/windows/tests/OpenClicky.Core.Tests -c Debug
dotnet run --project app/windows/src/OpenClicky.Windows -c Debug
```

For a self-contained x64 folder (no separate .NET runtime needed on the PC):

```powershell
dotnet publish app/windows/src/OpenClicky.Windows -c Release -r win-x64 --self-contained true -o artifacts/windows-x64
```

Run `clicky-bro.exe` in that folder. Node is still required for the optional
shared Gemini helper CLI; use its absolute `app/agent/dist/cli.js` path in
settings, as described in the Windows guide.

## Gemini and local files

Choose Gemini and `gemini-3.5-flash-lite` in provider settings. The native answer
lane and shared agent use Google's native API; they do not reuse Codex sign-in.
An explicit free-model allowlist, no provider fallback, bounded tool calls,
cancellation and quota errors are implemented. Availability and rate limits
still depend on the account.

- `%USERPROFILE%\.clicky-bro\shell.json`: provider keys/settings, CLI command and
  workspace. Keep the key private; do not commit this file.
- `%LOCALAPPDATA%\clicky-bro\`: preferences, dictation database, downloaded models
  and `Logs\app.log`.
- `CLICKY_BRO_GEMINI_KEY_FILE`: optional explicit local JSON key file (`api_key`),
  read in memory by the app and CLI. Keep it outside Git and owner-private.

Agent mode defaults off. Teaching does not offer action tools. The existing
typed desktop-action lane requires Agent mode plus a native Allow once prompt
for each proposed action (missing/failed/cancelled confirmation denies it). The
shared CLI denies file writes
without `--approve` or an explicit `--allow-workspace-writes` grant. No arbitrary
shell execution is available through the new Gemini CLI.

## What has been verified

The Windows project cross-compiles on macOS with `EnableWindowsTargeting=true`.
Core tests and deterministic Gemini protocol/action tests run locally on .NET 8.
Five existing tests make Windows path assumptions and also fail on macOS in the
untouched upstream baseline. Physical Windows capture, audio, monitor scaling,
permissions and input acceptance remain pending. See the root build status for
current counts and exact evidence; cross-compilation is not Windows acceptance.

Installer packaging is available in `installer/build-release.ps1`; it is local
unless explicitly passed publication flags. Automatic update checks are off by
default for this development build. No signing or public distribution is claimed.

The upstream architecture mapping remains in [PORTING.md](PORTING.md).
