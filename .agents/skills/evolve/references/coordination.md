# Coordinate parallel agents

Use delegation only where the host permits it and the task benefits. The coordinator
owns scope, priorities, integration, evidence vetting and delivery. Available slots,
models and tool capabilities come from the host; do not invent them.

## Investigation

Give each investigator a bounded area/category, the user outcome, base revision,
relevant project conventions, exclusions, and the finding format. Require evidence,
confidence and actual methods. Include secret-handling and instruction-hierarchy
rules; a child may not inherit them. Read cited locations before accepting findings.

Useful parallel work includes independent workflows, packages, audit categories,
technical research or a fresh review. Overlapping investigations need an explicit
purpose, such as independent confirmation of a high-risk claim.

## Implementation

Assign file/module ownership and interface contracts. Use separate worktrees when
supported. If isolation is unavailable, serialize overlapping edits and parallelise
read-only work instead. Never pretend separate agent conversations isolate files.

Agree on shared schema/API changes before dependants implement against them. Bound
concurrency to the tool/environment and resource budget. Separate build/cache paths
where the stack requires them; account for disk and cleanup.

Agents return a focused diff, acceptance evidence, remaining concerns and next
action. They do not push or merge beyond the user's permission. The coordinator
reviews/integrates changes, resolves conflicts by understanding both sides, and
rechecks the integrated result.

## Review

Give the reviewer raw outcome/criteria/source and artifacts, not the desired verdict.
Do not let the implementer be the only judge of consequential work when independent
review is available. Vet findings and repair actual problems. Stop nesting agents
when another agent adds no independent evidence.

## Shared state

The coordinator is the normal ledger owner. Helper writes are lock-protected, but
that does not isolate application edits. Investigators can return findings without
writing the ledger. Coordinate command/check recording against a stable source
snapshot; concurrent source edits make evidence stale and require rechecks.
