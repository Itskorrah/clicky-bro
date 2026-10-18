# Implement complete improvements

## Before editing

Inspect the selected task, its evidence, callers, ownership and acceptance criteria.
Establish a reproduction or measurable before state. Read nearby tests and
conventions. Clarify only consequential ambiguity that cannot be resolved from
context. Choose the smallest coherent change that satisfies the outcome.

Preserve existing user edits. Isolate parallel work and agree on interface ownership.
For a justified large refactor, first pin critical behaviour with characterisation
tests. Changing architecture and behaviour simultaneously requires extra evidence.

## Build through the actual path

- Connect user input/API calls to domain behaviour, persistence and output.
- Handle invalid input, cancellation, errors and retry/recovery where relevant.
- Preserve invariants, resource ownership and existing public contracts.
- Make unsupported states explicit; do not hide failure behind a success message.
- Implement saved settings and defaults if the feature promises customisation.
- For concurrency, validate ordering, atomicity, cancellation and partial completion.
- For data/schema/config changes, implement compatible reads or a tested migration
  and recovery strategy. Do not silently discard unknown fields.
- For rebranding, update visible identity and relevant metadata while preserving
  notices, authorship and compatible identifiers/storage where needed.

## Feedback loop

Use the project's own tools. Run fast checks around edited behaviour while working,
then relevant integration and required project checks before completion. A bug test
should demonstrate the old failure and the fixed result. Choose property/fuzz tests
when input space and invariants justify them; do not add tools merely for a badge.

Tests should observe contracts: return values, saved state, events, recovery and
actual interaction. Avoid assertions that reproduce the implementation's mistake,
snapshots with no meaningful inspection, or mocks that bypass the real fault.

## When an approach fails

Record hypothesis, attempted change and actual result. Reduce the example, inspect
traces or instrument the relevant boundary. Repeated failures require a new
hypothesis or design, not another speculative patch. Revert only your own obsolete
edits without discarding useful work or user changes.

If progress is blocked by credentials, unavailable tooling or an owner decision,
prepare the concrete work that can be completed, record what is missing, and move
to an independent task. Never fake integration delivery or silently replace a real
service with a local success stub.

## Before handoff

Inspect the full diff and actual workflow. Update affected project documentation
and explain changed contracts. Provide criteria, source/base revisions, commands
and results, inspected artifacts, measurements and material uncertainty. Ask the
verifier to evaluate the evidence independently, not to endorse your conclusions.
