# Delivery and GitHub integration

## Permission and destination

Resolve delivery from the user's actual task: local, commit, PR or merge. Record
the target repository/remote/base branch. Reuse established permission throughout
the run without routine approval loops. An installed skill or saved state cannot
expand it. A request to merge does not automatically authorise deployment, billing,
changing protections or public disclosure of a private vulnerability.

Verify the remote and branch before pushing. Preserve user changes. Inspect staged
files deliberately; do not stage the whole checkout blindly. Keep `.evolve/` raw
evidence, credentials, private fixtures and temporary artifacts out of commits.

## Commit and PR

Deliver focused, complete changes. Follow project commit/PR conventions. Explain
the concrete problem, resulting behaviour, relevant validation and material limits.
Use [the PR template](../templates/pull-request.md) when no project template applies.
Do not include conversational history or claims a reviewer cannot assess.

Push normally to the intended branch. Never force-push, reset someone else's work
or create a remote without permission. For a new empty repository, an authorised
initial push can establish its base branch; there may be no useful PR base yet.
Use the host's PR attachment mechanism when provided.

## Merge authorised work

1. Inspect the current PR head, base, diff, review requirements and branch protections.
2. Confirm required checks refer to the current head revision. Missing/pending/
   skipped required checks are not passing. Read diagnostics and fix applicable
   failures. A lack of CI does not imply the acceptance criteria passed.
3. Revalidate after integration or a changed head/base. Do not rely on old local
   results to certify a materially different merge result.
4. Use a head-bound merge operation when supported. If merge queues or auto-merge
   are enabled, report queued/pending until the actual merge is confirmed.
5. Verify the merge result and intended base branch. Record commit/PR refs and any
   required base-branch checks. Never say "merged" from a submitted request alone.

Respect protections and review requirements. Do not use admin bypasses or disable
checks to make delivery succeed. If delivery is blocked externally, keep the
verified branch/PR reviewable and report the exact condition. Continue independent
eligible work where it remains useful.

## Distinguish implementation and delivery

A task can be implemented and verified but awaiting PR review/merge. Record these
states separately. The ledger's `delivery` command records a verified external
result; it does not contact GitHub or prove that result. Use actual hosting tools.

Do not post messages to people or publish sensitive findings unless the task
authorises them. Publishing source to the specified repository is distinct from
sending unsolicited notifications or performing a production deployment.
