---
name: evolve-verify
description: Independently verify an application change against its acceptance criteria, real workflows and regression risks. Use before finishing or delivering an Evolve task, when reviewing an implementation, or when claims exceed available evidence.
---

# Evolve Verify

Evaluate the result independently. Acceptance criteria, source and observable
behaviour are authoritative evidence; the implementer's confidence is not.

## Shared resources

Resolve sibling `evolve` using the host loader or adjacent directory and read
[verification](../evolve/references/verification.md) and
[state/evidence](../evolve/references/state.md). If unavailable, verify manually
using this procedure and explicitly identify missing freshness guards.

## Procedure

1. Obtain the user's outcome, criteria, base revision, current diff and artifact
   locations. Inspect applicable project instructions and required checks.
2. Read the actual changed code, callers, storage and integration seams. Check
   scope compliance, preserved contracts and maintainability. Trace each claimed
   outcome to an implemented path; investigate unreachable or mocked behaviour.
3. Re-run appropriate tests/checks on the final source. Inspect assertions, test
   setup and fixture realism. A process exiting zero is evidence of execution,
   not proof that its tests cover the promised outcome.
4. Exercise the core flow and relevant failure/recovery paths. For UI work inspect
   captures and interactions. For performance inspect comparable repeated
   measurements. For compatibility inspect round trips and preserved information.
5. Reproduce suspected regressions before reporting them. Distinguish introduced
   failures, pre-existing failures and unavailable checks. Give actionable findings
   with source references, triggers, impact and expected behaviour.
6. Render a verdict: accepted, changes required, or blocked by missing evidence.
   State exactly which criteria passed, failed or remain unverified.

Use a fresh-context reviewer when the host provides one, but do not spawn nested
reviewers indefinitely. Review reports must be vetted. Any source change after
verification invalidates affected results and requires relevant rechecks. Never
waive a required gate, fabricate observations or claim a platform you did not run.
