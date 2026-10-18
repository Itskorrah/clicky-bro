# Adapt to the project's stack

Read the project's manifests, pinned toolchain, scripts and CI. Use those versions
and commands unless an upgrade is part of a justified task. Verify unfamiliar or
version-dependent advice against current primary documentation. Never choose a new
framework merely because another skill's examples use it.

| Stack | Investigation and verification considerations |
| --- | --- |
| Rust/native | Ownership, input bounds, panic/error paths, allocation, cancellation, thread affinity, native UI and supported targets. Use project fmt/clippy/tests and release workloads; sanitizers/fuzzing where supported and warranted. |
| JavaScript/TypeScript/web | Actual runtime/browser contracts, input validation, async races, state/persistence, rendering/invalidation, bundle/runtime work, accessibility and real browser flows. A typecheck does not validate runtime input. |
| Python | Actual interpreter/environment, exception handling, data validation, process/resource behaviour, typing where adopted, tests through real interfaces and packaging/installability. |
| Go/services | Context cancellation, goroutine ownership, data races, timeouts, retries, connection/resource lifecycle and API/storage integration. Use race checks when they can test the risk. |
| Swift/Kotlin/mobile | Platform lifecycle, state ownership, main-thread work, accessibility, persistence, device/simulator differences and platform-specific acceptance. |
| C/C++ | Memory ownership, lifetimes, UB/input bounds, ABI compatibility and compiler/build-mode differences. Use existing sanitizers/static analysis when available. |

These are routes to relevant evidence, not mandatory tooling additions. Use the
stack's established conventions and meaningful checks. Report unsupported targets
or unavailable device/platform tests honestly.

## Dependency decisions

Check maintenance, compatibility with the pinned runtime/targets, licence, size and
operational requirements. Prefer capabilities already in the project when they
satisfy the outcome. An upgrade needs migration notes and relevant regression checks;
"latest" is not an acceptance criterion.

Review reachable security advisories using primary sources and project-specific
conditions. Do not treat a vulnerability count as a complete security assessment
or silence an alert by suppressing the tool without assessing the issue.
