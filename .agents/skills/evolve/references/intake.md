# Intake and baseline

## Establish the task

Resolve these from the user's request and existing context before asking:
repository/checkout, desired outcomes, included/excluded areas, product direction,
delivery permission, environment constraints and any explicit execution budget.
Do not reinterpret "improve" as permission to remove capabilities or switch stacks.
An audit-only request ends with findings. An implementation request continues into
working changes. Maintain permission across the run; the ledger only records it.

## Inspect the foundation

1. Read applicable AGENTS/CLAUDE instructions, contribution rules, architecture
   decisions, manifests, root scripts, CI and relevant roadmap sections.
2. Confirm the actual checkout, remotes, base revision and uncommitted/untracked
   work. Identify pre-existing user edits; use an isolated checkout when needed.
3. Map entry points, layers, persistence, key external dependencies, deployment
   model and the most important user workflows. Trace representative operations.
4. Discover the project's real check commands. Inspect scripts before executing
   them, especially migrations, network operations or production-targeted commands.
5. Run relevant baseline checks. Record command, source snapshot, actual result,
   duration and environmental limitations. A pre-existing failure is still a risk.
6. Launch/exercise the application where available. Use synthetic data and local
   resources. Separate code presence from reachable behaviour and full functionality.

When the baseline is broken, prioritise restoring a trustworthy feedback loop
and the affected user flow. Do not disable failing checks or declare "pre-existing"
as sufficient reason to deliver new work on top of unassessed failure.

## Coverage and scope

Maintain an inventory of modules/workflows, relevance, investigation methods and
status: not examined, inspected, exercised or verified. File counts are an
inventory, not a measure of understanding. Generated code, binaries, vendored
dependencies and private data may be excluded with a reason. Investigate reachable
risks in dependencies without reading every vendored line.

Initial discovery should be enough to choose useful work. Deepen it as tasks reveal
unknowns. Do not spend the available run building an exhaustive roadmap before
implementing anything. Report genuine unknowns and the missing evidence that would
resolve them.

## Record a compact operating brief

- Goal, scope and important user workflows.
- Repo/base revision and pre-existing changes.
- Stack, boundaries, persistence and runtime constraints.
- Verified commands and baseline results.
- Delivery permission as stated by the user; relevant target repo/base branch.
- Investigation coverage, immediate candidates and known blockers.

Keep private operational detail in `.evolve/`. Update it when assumptions change.
Project documentation that users/contributors need belongs in the project's normal
docs, reviewed and sanitised separately.
