<div align="center">

<img src="app/macos/OpenClicky/OpenClicky/Assets.xcassets/AppIcon.appiconset/1024-mac.png" width="132" alt="Clicky Bro navy assistant icon" />

<h1>Clicky Bro</h1>

<p><strong>Your desktop, explained. Your words, written. Your work, moving.</strong></p>

<p>A native desktop assistant for macOS and Windows: contextual help, on-device dictation, and carefully scoped helpers.</p>

<p>
  <img alt="Development alpha" src="https://img.shields.io/badge/status-development%20alpha-D97706?style=flat-square" />
  <img alt="macOS SwiftUI" src="https://img.shields.io/badge/macOS-SwiftUI-2563EB?style=flat-square&logo=apple&logoColor=white" />
  <img alt="Windows WPF" src="https://img.shields.io/badge/Windows-WPF-334155?style=flat-square&logo=windows&logoColor=white" />
  <img alt="TypeScript shared agent" src="https://img.shields.io/badge/agent-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" />
  <a href="app/LICENSE"><img alt="MIT-licensed adopted core" src="https://img.shields.io/badge/adopted%20core-MIT-64748B?style=flat-square" /></a>
</p>

<p>
  <a href="#capabilities">Capabilities</a> ·
  <a href="#get-started">Get started</a> ·
  <a href="#privacy-security-and-authority">Privacy &amp; safety</a> ·
  <a href="docs/PRODUCT_ROADMAP.md">Roadmap</a> ·
  <a href="CODEX_WINDOWS.md">Windows handoff</a>
</p>

</div>

---

> [!IMPORTANT]
> **Development alpha — not a general release.** Clicky Bro has native application source for macOS and Windows, but current-bundle capture, microphone, focus-safe insertion, accessibility and physical Windows acceptance are still open. There are no signed or notarised public installers. Read the [current build status](docs/BUILD_STATUS.md) before relying on any capability.

## Use with Codex — copy-and-paste workflows

Open the relevant project in Codex, paste this prompt and let it prepare the local environment, **verify** the setup and begin the actual workflow. Existing permissions and platform limits still apply.

```text
Set up and use https://github.com/Itskorrah/clicky-bro in my current Codex project. Read its README, AGENTS guidance (if present) and prompts/codex/setup-and-run.md. Inspect the current checkout and existing skills first. Open the latest Clicky Bro checkout and read `AGENTS.md`, `CODEX_WINDOWS.md`, `docs/TESTING_WINDOWS.md`, `docs/NEXT_STEPS.md`, `docs/BUILD_STATUS.md` and its Evolve skill instructions. Inspect active platform, branch and local work before changing anything. Reuse installed project skills, run `python3 scripts/check_local.py --report .local/evidence/offline.json` and the feasible native checks described in the repository, then choose the highest-impact currently feasible item from the documented handoff. Implement a complete, bounded improvement, test the real platform path and update status/evidence. Continue with further independent priority work where practical. Preserve the native SwiftUI/AppKit, WPF and shared TypeScript boundaries and app identity. Do not migrate other apps, access Codex tokens, enable paid model fallback or treat macOS cross-build as Windows physical acceptance. Follow existing local worker/tool constraints and keep secret runtime data out of Git. Run appropriate local tests, then for verified authorised scoped changes commit, push, open a PR and merge when permitted without bypassing branch protection. Do not depend on GitHub Actions. Report evidence and blockers.
```

Other copyable Codex workflows: [full setup and run](prompts/codex/setup-and-run.md) · [update](prompts/codex/update.md) · [resume](prompts/codex/resume.md) · [extended autonomous](prompts/codex/autonomous.md).

## The product

Clicky Bro brings three desktop workflows together while making the data shared, the execution location and the required permissions visible.

| Ask &amp; learn | Dictate &amp; write | Work with helpers |
| --- | --- | --- |
| Choose a window for contextual answers and pointer-based guidance. Observation does not grant permission to click. | Use Apple Speech or a downloadable Parakeet model for local transcription. Optional cloud providers remain separate. | Create bounded helpers with opt-in memory, local routines and saved text artifacts. |
| A missing or stale capture target must fail clearly, without widening to the whole desktop. | Formatting, shortcuts, history and insertion exist in the native foundation; real-device acceptance remains open. | Direct Gemini supports scoped workspace file tools. Other account and connector integrations are not implied. |

## Navy identity and native interface

The refreshed visual system uses a **Primer-inspired navy and slate palette** across the existing native macOS and Windows interfaces.

- **Navy Slate** is the default accent for new installs: **#2B547B** in light appearance and **#80A9D4** in dark appearance.
- Surfaces use restrained GitHub-like neutrals: **#F6F8FA** and white in light mode; **#0D1117**, **#161B22** and **#21262D** in dark mode.
- Classic Coral and other saved presets, valid custom colours, Light/Dark/Auto appearance and unrelated settings are preserved. Reset changes only the accent preset and companion-follow preference.
- The new app mark is the navy tile with a cobalt assistant face and a small cyan spark. The same artwork is generated for macOS, Windows and the companion status/tray surfaces. The editable vector mark is available at [docs/assets/clicky-bro-mark.svg](docs/assets/clicky-bro-mark.svg).
- The existing native layout remains in place. The work improves colour, focus, hover and pressed states without replacing the settings app with a web dashboard.

See the [theme controls and persistence contract](docs/THEME_CUSTOMISATION.md), [design system](docs/DESIGN_SYSTEM.md), [app icon guide](docs/APP_ICON.md) and [implementation record](docs/IMPLEMENTATION_2026-10-19.md). Fresh, redacted screenshots from real devices are still an acceptance gate; the historical captures elsewhere in the repository are not evidence of the refreshed interface.

## Capabilities

Source presence is not the same as end-to-end acceptance. The table describes the current implementation and its open checks.

| Capability | Current implementation | Acceptance still open |
| --- | --- | --- |
| macOS desktop app and menu-bar companion | Native SwiftUI and AppKit | Current-bundle permissions, capture, microphone, focus and visible UI checks |
| Windows desktop app and tray companion | Native WPF/C# with shared TypeScript agent | Physical Windows rendering, capture, input, DPI and accessibility checks |
| Chosen-window context and visual guidance | Native capture and teaching flows are present | Permission denial/revocation, stale targets, multi-display and safe teaching |
| Local dictation | macOS Apple Speech and Parakeet V3; Windows Parakeet V3 foundation | Real microphone, language, insertion and focus-change checks |
| Helpers, memory, routines and text artifacts | macOS foundation supports these workflows | Broader lifecycle checks and Windows UI/persistence parity |
| Gemini BYOK and workspace tools | Provider and bounded file tools are implemented | Native approval, cancellation and live-provider acceptance |
| Navy themes and app icon | Native theme controls, shared palette and regenerated app icons | Native screenshots, custom-picker/restart checks, mixed DPI and accessibility |
| Offline verification | Local verification runner is available | Run it on the target operating system; skipped checks are not passes |

The [feature crosswalk](docs/FULL_SPEC_CROSSWALK.md), [feature audit](docs/FEATURE_AUDIT.md) and [product roadmap](docs/PRODUCT_ROADMAP.md) track the wider scope. Whisper, guaranteed offline-only operation, full-document retrieval, broad account integrations and commercial distribution are not represented as delivered.

## Current engineering status

As of **19 October 2026**, the theme, navy UI, companion and icon stack from [PR #8](https://github.com/Itskorrah/clicky-bro/pull/8) and [PR #9](https://github.com/Itskorrah/clicky-bro/pull/9) is integrated into `main` at source commit `5d2bcfee3639c58daca873a43ca76404c68f57d8`, at the user's request and before all platform acceptance gates passed. PR #8 was marked merged; PR #9 remains an open draft against its former theme branch, although its source is present in `main`. [PR #1](https://github.com/Itskorrah/clicky-bro/pull/1) remains separate for capture diagnostics and Stop safety. Integration does not count as native acceptance or release approval.

The latest local verification for the navy/icon source reported:

- macOS native suite: **717 passed**.
- Python suite: **39 passed**; focused palette checks: **7 passed**.
- Windows WPF cross-build on macOS: **0 errors**, with one inherited high-DPI manifest warning.
- Windows portable core tests run on macOS: **1,079 passed, 5 failed**. The five failures depend on Windows paths or npm-shim behavior on a macOS host; they remain failures and are **not** a Windows pass.
- GitHub reported zero check-runs for source commit `5d2bcfe` after integration. No physical Windows acceptance or release approval is claimed.

See [build evidence](docs/BUILD_STATUS.md), [the current checkpoint](docs/DEVELOPMENT_CHECKPOINT_2026-10-19.md) and the [remaining acceptance sequence](docs/NEXT_STEPS.md). The exact continuation instructions for a Windows PC are in [CODEX_WINDOWS.md](CODEX_WINDOWS.md).

## Get started

These commands build the development app from source. They do not install a consumer release. Use disposable windows and files for testing, and keep provider keys out of Git.

### macOS

Requires Xcode, Node.js 24 and Python 3.9 or later.

~~~bash
git clone https://github.com/Itskorrah/clicky-bro.git
cd clicky-bro
npm ci --prefix app --ignore-scripts
npm run build --prefix app --workspace agent
python3 scripts/gemini.py configure
python3 scripts/dev.py build
python3 scripts/dev.py launch
~~~

The Gemini setup prompt hides key input. The launcher stages development products in Clicky Bro's own user cache and keeps its runtime under its private Application Support location. It does not reuse HeyClicky's identity. Permissions are tied to the exact running build; follow [macOS testing and troubleshooting](docs/TESTING_MACOS.md). Provider tests can consume quota; check [Gemini setup](docs/GEMINI_SETUP.md) first.

### Windows

Requires Windows 11 x64, Git, Node.js 24 and the .NET 8 SDK. Python 3.9 or
later is optional for the Python suite and local verification scripts.

~~~powershell
npm ci --prefix app --ignore-scripts
npm run build --prefix app --workspace agent
dotnet build app/windows/OpenClicky.Windows.sln -c Debug
dotnet test app/windows/tests/OpenClicky.Core.Tests/OpenClicky.Core.Tests.csproj -c Debug
dotnet run --project app/windows/src/OpenClicky.Windows -c Debug
~~~

The app uses its own Clicky Bro identity and settings. Do not migrate or overwrite another app's profile. A macOS cross-build does not prove Windows capture, focus, microphone, hotkey, input or accessibility behaviour. Follow the [Windows acceptance guide](docs/TESTING_WINDOWS.md) and [Windows Codex handoff](CODEX_WINDOWS.md).

## Offline dictation

- **Apple Speech** requires no extra model download. On-device behaviour depends on the supported OS and language.
- **Parakeet V3 through sherpa-onnx** downloads an archive of about 465 MB, checks its SHA-256, reports progress, supports cancellation and removal, and unloads when idle or under memory pressure. It supports 25 primarily European languages, not Arabic.
- **Cloud transcription and text polishing are separate choices.** Using a local recognizer does not guarantee the complete writing workflow stays offline.

Model quality, installation, language coverage and real microphone behaviour need device-specific checks. Downloadable multilingual Whisper models and a guaranteed offline-only mode remain roadmap work.

## Privacy, security and authority

Clicky Bro is designed to be local-first. It is not formally security-certified.

- **Choose what to share.** A person chooses a window for contextual capture. A missing or stale target must not broaden capture to the whole screen.
- **Keep speech destinations distinct.** Local recognition, cloud transcription and model-based text cleanup have separate data paths.
- **Observation is not action authority.** Teaching can point and explain; clicking requires distinct user authority. Content from a document, webpage or model response cannot approve an action.
- **Scope workspace access.** File writes require a separate opt-in. That opt-in currently allows writes within the selected workspace; it is not per-file confirmation. Use a disposable workspace.
- **Make cancellation effective.** Stop and pending-action handling are tracked in [PR #1](https://github.com/Itskorrah/clicky-bro/pull/1) and still need full live acceptance.
- **Preserve provenance.** The adopted application source is MIT-licensed. Third-party code, models and redistribution terms require their own review.

See [source provenance](docs/PROVENANCE.md) and [the project engineering rules](AGENTS.md).

## Development and verification

Clicky Bro keeps native SwiftUI/AppKit and WPF clients, with a shared TypeScript agent.

| Area | Location |
| --- | --- |
| macOS app | app/macos/ |
| Windows app and .NET core | app/windows/ |
| Shared agent and workspace tools | app/agent/ |
| Optional provider backend | app/backend/ |
| Cross-platform design tokens | design/tokens.json |
| Native macOS launcher | scripts/dev.py |
| CI-free verification runner | scripts/check_local.py |
| Product and acceptance records | docs/ |
| Project Evolve workflow | .agents/skills/evolve/ |
| KStack desktop-development workflow | User-managed local tooling; not part of the shipped app |

KStack's native-desktop workflow and the project's Evolve audit/build/verify skills guide scoped work. They do not install app dependencies or change global Codex, authentication or billing settings.

Run the local checks on a suitable machine:

~~~bash
npm ci --prefix app --ignore-scripts
python3 scripts/check_local.py --list
python3 scripts/check_local.py --report .local/evidence/checks.json

# On a Mac with Xcode
python3 scripts/check_local.py --native

# With the .NET SDK
python3 scripts/check_local.py --windows
~~~

Exit code **0** means every selected check passed, **1** means a check failed and **2** means at least one check was skipped. Reports do not contain captured command output or provider secrets, and existing reports are not overwritten. Source tests cannot replace real OS permission, audio, GUI or accessibility acceptance.

## Roadmap and release gates

1. **Native safety:** prove current-bundle capture, permission denial and revocation, microphone use, focus-safe insertion and Stop on real devices.
2. **Theme and companion:** inspect native settings, custom colours, persistence, edge placement, click-through, reduced motion and accessibility on macOS and Windows.
3. **Cross-platform parity:** complete Windows Helpers, Memory and Routines UI/persistence, and verify the native app on a Windows PC.
4. **Broader workflows:** add integrations one at a time with scoped authentication, clear denial/revocation and real action receipts.
5. **Distribution:** review licences, stabilize application identity, sign installers and validate update/rollback behavior.

Accounts, plans, billing, signed installers, notarisation and trusted updates are separate product work; this development branch does not claim them as shipped.

## Contributing and acknowledgements

Read [AGENTS.md](AGENTS.md), the [foundation decision](docs/FOUNDATION_DECISION.md), the [Evolve skill](.agents/skills/evolve/SKILL.md) and [provenance notes](docs/PROVENANCE.md) before changing capture, native permissions or agent authority. Preserve user state, test with benign fixtures and report the exact commit and platform for each result.

The adopted native foundation is based on the pinned [Prasanth OpenClicky](https://github.com/prasanthsasikumar/openclicky) MIT source. Original credits and third-party licences remain with the source under app/. HeyClicky and Superwhisper are independent product references; Clicky Bro is not affiliated with them and does not use competitor artwork.

<div align="center">
  <sub>Thoughtful desktop assistance, clear permissions and honest acceptance status.</sub>
</div>
