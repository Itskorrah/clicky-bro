---
name: evolve-build
description: Implement a selected application improvement completely, preserve existing behaviour, and add meaningful regression coverage. Use for an Evolve task, a verified fault, a scoped feature, or a justified refactor with clear acceptance criteria.
---

# Evolve Build

Complete the selected outcome through the application's real execution path.
The task's acceptance criteria define completion. Preserve existing user work and
contracts; adapt to project conventions instead of imposing a stack.

## Shared resources

Load sibling `evolve` or resolve it next to this skill. Read
[implementation](../evolve/references/implementation.md) and
[verification](../evolve/references/verification.md). Load performance,
compatibility or stack guidance there only when applicable. Missing shared
resources mean use this procedure and disclose the unavailable helpers.

## Procedure

1. Confirm the trigger, evidence, scope, dependencies and observable criteria.
   Inspect relevant callers, state/persistence and failure behaviour. Establish
   the before state and the applicable baseline checks.
2. For a real defect, create the smallest useful failing reproduction or test.
   For a new feature, specify the actual user flow and critical edge cases.
3. Work in an isolated checkout if parallel implementation or existing user
   changes require it. Edit only your owned scope; communicate interface changes
   before other agents depend on them.
4. Implement a complete slice: model, integration, user-facing controls, saved
   state, validation and errors as needed. Unsupported cases remain explicitly
   unsupported. Preserve public API/file compatibility unless a change is in scope.
5. Run fast relevant checks while developing. Use the project's existing test
   patterns and verify behaviour through stable boundaries. Avoid meaningless
   assertions or reducing checks to make a failure disappear.
6. Inspect the resulting workflow. Measure claimed performance improvements with
   comparable inputs. Update relevant usage and architecture docs.
7. Hand the diff, criteria, commands/results, artifacts and remaining concerns to
   verification. Address findings, then repeat affected checks after final edits.

Research only questions that affect the implementation. If the design cannot
satisfy the outcome, change approach with a recorded reason. Do not substitute a
mock, disabled control, static screenshot or happy-path-only implementation for
complete behaviour. Report incomplete work rather than marking it finished.
