# clicky-bro

A local desktop assistant in development: ask about a chosen window, get visual
guidance, dictate text and run bounded helpers with your own Gemini key.

The native foundation is adopted from Prasanth OpenClicky, with its Swift macOS,
C#/WPF Windows and TypeScript agent source retained under `app/`. Licenses and
attribution are preserved; see [provenance](docs/PROVENANCE.md) and the
[foundation decision](docs/FOUNDATION_DECISION.md).

**This is a development build, not a finished HeyClicky replacement.** A feature
being present in adopted source is not proof that it works on every platform.
See [build status](docs/BUILD_STATUS.md) for verification and remaining gaps.

## Run on this Mac

Requires Xcode, Node.js 24 and Python 3.9+. From the repository root:

```bash
npm ci --prefix app --ignore-scripts
npm run build --prefix app --workspace agent
python3 scripts/gemini.py configure
python3 scripts/dev.py build
python3 scripts/dev.py launch
```

The key prompt is hidden; do not put keys into source or chat. An existing local
key can be reused without running `configure` again. Builds fetch the pinned
native dependencies on first use. Generated native products live under
`~/Library/Caches/clicky-bro/`. The developer launcher stages the agent there
and uses the private runtime at
`~/Library/Application Support/clicky-bro/development`; it migrates existing
settings/workspace from ignored `.local/runtime/native/` and
`.local/workspaces/default/` once, preserving the originals. The canonical
Gemini key remains in ignored `.local/credentials/gemini.json`; the launcher
refreshes a private runtime copy for each launch. This does not install over
HeyClicky.

The Workspace window contains Helpers, Memory, Routines and Runs & files. A helper
can reason/read within the agent workspace. File writes require its separate
checkbox; scope and memory text cannot grant permission. Desktop actions use a
separate native approval flow. Routines run only while the app is open and the
session's scheduling switch is enabled.

For window questions/teaching, use the menu-bar companion. The current local
development bundle has not yet passed Screen Recording permission acceptance:
macOS can show an Allowed entry for an older build even though an ad-hoc rebuild
changed the app's code identity. Follow the [macOS test guide](docs/TESTING_MACOS.md)
to register the exact current bundle and verify capture. Grant Accessibility
only when testing native pointing/insertion, and microphone/speech permissions
when testing dictation. Sharing never silently expands to all displays.

## Current feature-branch improvements (19 October 2026)

The [product status](PRODUCT_STATUS.md) distinguishes shipped source, old test evidence and pending real-device acceptance. The new **Settings → Privacy & Security → Selected-window capture test** checks the OS permission signal separately from whether ScreenCaptureKit can actually return a JPEG from the window you already chose. It never opens another window picker, saves the frame or sends it to an AI provider. A window moving or resizing mid-capture invalidates that screenshot instead of providing a misplaced pointer.

In **Workspace → Helpers**, choose **Start with a template** to draft one of three read-only helpers: explain a local `error.txt`, plan from `goal.txt`, or review `draft.txt`. Place that file inside the agent's configured workspace, inspect the draft, then save and run it. No template turns on memory, file writes or desktop actions. Results appear in **Runs & files**. These workflows still need hands-on acceptance and are not a replacement for selected-window Teach.

Gemini helper writes now require approval of each individual file action; a session-wide grant is insufficient, and Stop interrupts a pending approval. The native companion’s Stop control also cancels active agent work rather than only silencing speech. The source and regression tests for these changes are in a PR; **they have not yet passed a new native build**. See the [implementation record](docs/IMPLEMENTATION_2026-10-19.md) for reproducible commands and limitations.

## Verify

```bash
python3 -m unittest discover -s tests -v
npm test --prefix app --workspace agent -- --maxWorkers=1
python3 scripts/dev.py test-native
```

Optional live checks consume Gemini quota:

```bash
python3 scripts/dev.py smoke-answer
python3 scripts/dev.py smoke-voice
```

The first uses a synthetic image through the actual native provider; the second
renders system speech locally. Neither verifies native screen permissions or
real-world task reliability. [Gemini setup](docs/GEMINI_SETUP.md) includes key
replacement and standalone connection checks.

The offline Python suite passed 15/15 (8 private-runtime migration tests and 7
provider/credential tests). The authoritative native macOS unit suite passed
705/705 for the preceding functional, privacy and Stop fixes. The final
standalone app build also passed after the accessibility-row follow-up. A
focused helper-button UI test compiled but timed out enabling automation before
its test body ran, so no UI-test pass is claimed. That automated UI check and
broader capture/permission acceptance remain pending. The root did complete one
live GUI helper run and restart check: the exact `CLICKY_BRO_HELPER_OK` result
and inline artifact were present before and after relaunch. This accepts that
helper persistence slice only. The current
development bundle's Screen Recording permission and full capture flow remain
unaccepted; the Settings toggle alone is not evidence of capture.

## Windows later

Use the [Windows test guide](docs/TESTING_WINDOWS.md). The current macOS-hosted
Windows core run passed 1,066 of 1,071 tests; its five failures match the
upstream path/PATHEXT baseline. The final-source WPF cross-build passed after a
pinned restore using absolute isolated NuGet paths (0 errors, one inherited
high-DPI manifest warning). Neither check establishes Windows capture/audio/input
behavior. The user has explicitly deferred physical Windows testing.

## Development protocol

Work locally with Codex, using the scoped Evolve skills in `.agents/skills/`.
Task metadata for this delivery records GPT-6.1 Sol High for the root task and
GPT-6 Luna Max for the delegated Windows lane; neither assignment changed host
or global settings. Keep the short orchestration to at most two workers and run
heavy builds sequentially on the 8 GiB Mac. REA is for concrete artifact
questions; Context Mode is for large output. [AGENTS.md](AGENTS.md) contains
repository rules.

No account billing, hosted backend, automatic paid-model fallback or external
service integrations are enabled by this setup. Customer accounts, distribution,
updates and commercial deployment require separate implementation and acceptance.
