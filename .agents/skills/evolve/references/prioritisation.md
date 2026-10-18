# Priorities and task selection

Make the next choice from evidence and the user's outcomes. The queue is a
decision aid, not a target number of changes.

## Rank opportunities

Consider impact (who/how often/how severely), confidence, effort, dependencies and
regression risk. The ledger's optional impact × confidence / effort score orders
eligible tasks; it does not override critical integrity/security work, dependency
ordering or engineering judgement. Risk informs the required safeguards, not an
automatic reason to avoid hard problems.

Usually start with document/data integrity, reachable serious vulnerabilities,
crashes and broken core flows. Restore verification when its absence prevents
safe progress. Then address measured performance, recurring user friction and
maintenance problems that impede useful changes. Follow explicit user priorities
when they change this order.

## Define an executable task

Write enough detail to implement and verify without rediscovering the decision:
trigger, evidence, scope, contracts to preserve, acceptance criteria, check methods
and dependencies. Use [the task template](../templates/task.md). A criterion must
describe observable behaviour, not "clean code" or "production-ready".

Prefer a complete vertical slice. A large change may need several dependency-aware
slices, each leaving working behaviour. Do not ship a control before its real
operation exists or migrate data without a recovery plan. Avoid selecting numerous
unrelated improvements just because they fit in one PR.

## Avoid low-value churn

Do not manufacture work from fixed file-size thresholds, arbitrary coverage goals,
fashionable patterns or the absence of services an application does not need.
Renaming for taste, speculative abstraction and broad formatting sweeps need a
specific benefit. Preserve intentional architecture when it serves the product.

Keep the active queue small enough to complete and verify. Hold longer-term ideas
as compact findings. After each delivered change, update rankings using new
evidence. Track why work is blocked/deferred and what makes it eligible again.

## Protect completion capacity

Observe the actual host/user budget. Choose a task small enough that implementation,
review, relevant checks and delivery can finish. Reserve capacity for a checkpoint.
If a task grows, narrow to a complete safe slice or preserve it as unfinished.
Never mark it done because the run is ending.
