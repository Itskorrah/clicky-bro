# Local REA and HeyClicky investigation

Prepared 17 October 2026. This investigation does not modify or execute HeyClicky.

## Installed tools

- REA 6.5.0, pinned in `~/.local/share/rea/runtime/`.
- CLI launcher: `~/.local/bin/rea`.
- Ghidra 12.1.4 in `~/.local/share/rea/toolchains/ghidra_12.1.4_PUBLIC/`.
- Eclipse Temurin JDK 21.0.12.1, native Apple Silicon build, in the same toolchain directory.
- Ghidra's ARM64 decompiler was built locally from the source included in the verified Ghidra release, using `make -j2 ghidra_opt ARCH_TYPE="-arch arm64" OSDIR=mac_arm_64`.
- Both downloaded archives were checked against their published SHA-256 digests. The manifest is `~/.local/share/rea/toolchains/manifest.json`.

## Codex integration

REA setup added the `mcp_servers.rea` entry in `~/.codex/config.toml` and installed the matching skill in `~/.agents/skills/reverse-engineer-anything/`.

The original configuration is preserved at `~/.codex/config.toml.rea.backup`. Its hash matches the recorded pre-setup file. Parsed settings outside the REA registration were checked for equality.

Only REA's server configuration was then extended with a Node search path, a 2 GiB Java heap setting and longer analysis timeouts. These limits do not bound all native decompiler memory or all process CPU usage.

After the Codex restart, this chat's live `binary_session` call confirmed REA 6.5.0, aligned server identity, and available Ghidra 12.1.4 with passing Java/native-decompiler checks. An earlier independent MCP client also completed an initialize/tools-list handshake and discovered 207 tools. The live check establishes the current chat connection separately from that earlier handshake.

Readiness check:

```sh
rea doctor --client codex --provider ghidra --skill --json
```

The configured Node runtime, Ghidra version, headless launcher, ARM64 native decompiler, JDK, Codex registration and installed skill all passed this check.

## Local investigation files

Raw results and the ARM64 analysis copy are under `.local/rea/` in this project. `.git/info/exclude` excludes `.local/`; raw proprietary material is not added to Git. No account databases, session tokens or user conversations were inspected.

- `target-manifest.json`: original and ARM64-copy identities.
- `evidence/mcp-tools.json`: actual connected tool schemas.
- `evidence/open-heyclicky.json`: REA's validated target binding.
- `evidence/`: subsequent decompilation and export results.
- `mcp-session.mjs`: persistent local MCP investigation driver.

The driver's transport and target are local. HeyClicky is never launched by this workflow. Tool results supplied to Codex may enter the coding model's context; this is not a claim that the entire research workflow is offline.

## Initial architecture evidence

Installed target: `/Applications/HeyClicky.app`, version 1.0.53, build 64.

| Observation | Evidence path inside the bundle | Limit |
| --- | --- | --- |
| Universal ARM64/x86_64 native executable | `Contents/MacOS/HeyClicky`; `Contents/Info.plist` | Packaging and native linkage do not establish all runtime behaviour. |
| Build metadata records commit `cfc4ee64` | `Contents/Resources/ClickyBuildInfo.plist` | A packaged build label is not the original source tree. |
| Bundled Codex runtime version 0.152.1 with architecture-specific executables | `Contents/Resources/CodexRuntime/` and its vendor package metadata | Strong evidence for an embedded agent runtime; exact invocation must be traced. |
| Separate universal native computer-use helper | `Contents/Helpers/cua-driver` | Helper presence does not prove which actions are exposed or authorized. |
| Packaged computer-use instructions | `Contents/Resources/ClickyBundledSkills/cua-driver/SKILL.md` | Instructions document intended use; enforcement needs code or runtime evidence. |
| Eleven integration-skill directories | `Contents/Resources/ClickyIntegrationSkills/` | Instructions are not proof of working authenticated integrations. |
| Bundled model selection metadata | `Contents/Resources/ClickyCodexModelCatalog.json` | Not proof of currently available server models. |
| Update and observability components | Sparkle, Sentry, PostHog and PLCrashReporter bundle/framework paths | Presence does not establish telemetry contents, destinations or retention. |

## Decompilation boundaries

Ghidra produces reconstructed pseudocode and assembly, not the exact original Swift source, comments, project layout or private backend implementation. Optimisation and stripped symbols can obscure types, names and control flow. Treat reconstruction as evidence with limitations, not a source-code recovery claim.

### Verified native decompilation smoke test

REA's CLI successfully decompiled the first 24 bytes of the actual ARM64 entrypoint, through its first `RET` instruction. The original source offset, slice identity, carrier identity and load address are retained in `.local/rea/evidence/entry-byte-provenance.json`.

- Provider: Ghidra 12.1.4, default raw-binary analysis, 512 MiB Java heap.
- Evidence: `ev_0e3695984c19e8a25a89c012d383f126b528a66f73c5bf5a53ae9ea97fe3391a`.
- Complete result: `.local/rea/evidence/entry-byte-decompilation.json`.
- Readable output: `.local/rea/evidence/heyclicky-entry-pseudocode.c`.

```c
undefined8 entry(void)
{
  func_0x0001018575a4();
  return 0;
}
```

This establishes working native decompilation on real app instructions. The byte carrier contains no Mach-O imports, Swift metadata or the called function's body; it does not establish that function's purpose or whole-application semantics. It is separate from the whole-executable import below.

The first focused native target is the main executable's ARM64 slice. Its Mach-O `LC_MAIN` entry offset is 25,567,712 (`0x18621e0`), corresponding to analysis address `0x1018621e0` at image base `0x100000000`.

The default import was cancelled after several minutes of expensive whole-program analysis. Its log and cancellation status are retained in `.local/rea/evidence/default-profile-*`. An intermediate import with Objective-C message recovery disabled still spent substantial time in decompiler switch recovery, and was also cancelled with its diagnostics retained. The minimal verification uses `REA_GHIDRA_DISABLED_ANALYZERS="Objective-C Message Analyzer,Decompiler Switch Analysis"`; these exact overrides are recorded in the REA analysis profile. They omit facts those analyzers would recover, including some Objective-C call targets and switch control flow. The normal Codex server configuration retains the default profile, so this is an investigation-specific tradeoff, not a silent global reduction in analysis.

**Whole-executable status: incomplete.** The import with both expensive analyzers disabled reached REA's 600,000 ms provider startup limit before it could serve the entry-function query. No completed whole-program database or full-app pseudocode was returned. Diagnostics are retained in `.local/rea/evidence/whole-app-import-timeout.json`. Ghidra reported unsupported Objective-C type encodings and constant-propagation/address-space warnings during import; those are analysis limitations, not evidence of bugs in HeyClicky. The independent 24-byte test above establishes the native toolchain works, not that this large Swift program has been fully analysed.

Prefer bounded code-region investigation and subsystem-specific evidence next. A deliberately longer, resource-budgeted whole-program import or a different native provider can be evaluated when it answers a concrete question; do not repeatedly run the unchanged timed-out import and call it progress.

## Next investigation questions

The approved follow-up research is now recorded in [INSTALLED_APP_ARCHITECTURE.md](INSTALLED_APP_ARCHITECTURE.md). Four bounded regions totaling 26,916 bytes were successfully decompiled: runtime argument/configuration builders, a dictation token endpoint builder and an MCP request-handler candidate. Original-image instruction/literal mappings corroborate the selected references. This advances the evidence beyond the initial 24-byte smoke test, while whole-image analysis remains incomplete. Runtime routing, exact authorization enforcement, private services and full feature behavior remain unverified.

See [FEATURE_AUDIT.md](FEATURE_AUDIT.md), [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md) and [BUILD_PLAN.md](BUILD_PLAN.md) for the feature matrix, reviewed tools and proposed macOS/Windows implementation.

1. Trace how the native shell launches and configures its bundled agent runtime.
2. Trace the helper/tool registration and authorization boundaries.
3. Map conversation persistence, routine scheduling and recovery behaviour.
4. Map audio/transcription/response transport separately from agent execution.
5. Compare evidenced behaviour with the public Swift source and identify reusable platform-independent contracts for Windows.

Use targeted function and reference analysis rather than indiscriminately exporting every embedded dependency. Keep static observations, inferred architecture and runtime-verified behaviour separate.

## Sources

- [REA skill](https://github.com/morluto/rea/blob/main/.agents/skills/reverse-engineer-anything/SKILL.md)
- [REA installation and native decompiler build instructions](https://github.com/morluto/rea/blob/main/docs/installation.md)
- [Official Ghidra release](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build)
- [Official Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp)
