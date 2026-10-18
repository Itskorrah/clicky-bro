# Verification and review

## Match evidence to the claim

| Claim | Minimum useful evidence |
| --- | --- |
| Bug fixed | Original trigger/reproduction now passes and a regression test observes the fault |
| Feature complete | Real user/API flow, persistence where promised, and relevant failure/edge cases |
| Faster or smaller | Repeated comparable workloads, environment/source records and measured distribution |
| UI improved | Actual before/after states plus interaction checks appropriate to the claim |
| Compatibility preserved | Representative fixtures and meaningful round-trip/API contract assertions |
| Ready for delivery | Final diff review and current applicable checks at the final revision |

Evidence requirements grow with consequence. A copy change need not acquire a new
test suite. Saving, authentication, migration or concurrency work needs tests that
exercise its important failure modes. Existing baseline failures require explicit
assessment; do not invent waivers or disable gates.

## Independently inspect

Give a fresh reviewer the user outcome, criteria, base revision, diff and artifacts.
Ask it to inspect source and tests and reproduce suspected issues. Avoid feeding it
the implementer's rationale as the expected answer. Vet review findings as carefully
as audit findings. If no independent agent is available, perform a deliberate
separate review pass and disclose that limitation.

Check changed code, callers, data ownership, error handling, reachability and contract
compatibility. Read assertions and fixture setup: tests can pass while a feature is
unreachable or mocked out. Check scope and unnecessary complexity.

## Verify the final source

Run relevant regression/integration tests and the project's required checks after
the last applicable edit. Integration can introduce regressions after branch-local
checks, so validate the integrated result. Keep platform-specific claims limited to
platforms actually exercised. Missing device/browser credentials are missing evidence.

Record command, working directory, runtime/source snapshot, actual exit result,
time and inspected output. Sanitise artifacts. The runner's exit status and
freshness checks help bookkeeping; they do not assess assertions, accessibility,
exploitability or whether an observation is true.

## Verdict

Use accepted, changes required, or blocked by missing evidence. List which criteria
passed/failed/remain unverified, actionable findings and the next repair. Source
changes invalidate affected evidence. Re-run rather than carrying forward a stale
pass. An explicit project/user exception must be recorded with reason and scope;
it cannot be created by the implementer to finish a task.

Before finishing, inspect resource leaks, generated files, logs, secrets and private
data in the deliverable. Do not certify "all bugs fixed" or "production-ready"
from a finite suite or audit. State the actual result and practical limits.
