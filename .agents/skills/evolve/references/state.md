# State, evidence and resumption

Keep private working records under `.evolve/` at the application repository root.
The helpers require Python 3.10+ and Git. Run them by absolute path from that root,
or pass `--project` before the ledger subcommand. They do not run audits, interpret
test adequacy, grant permissions, push or merge.

## Ledger lifecycle

```sh
python3 "<EVOLVE_ROOT>/scripts/evolve.py" init --goal "Improve reliability" --delivery local
python3 "<EVOLVE_ROOT>/scripts/evolve.py" add --title "Handle cancelled saves" --evidence "save flow loses changes after cancellation" --category correctness --impact 5 --effort 2 --risk 3 --criterion regression --criterion review --file src/save.py
python3 "<EVOLVE_ROOT>/scripts/evolve.py" start --task E001
python3 "<EVOLVE_ROOT>/scripts/evolve.py" run --task E001 --criterion regression -- <actual test command> <args>
python3 "<EVOLVE_ROOT>/scripts/evolve.py" observe --task E001 --criterion review --artifact .evolve/review-E001.md --detail "Inspected diff and acceptance paths" --outcome pass
python3 "<EVOLVE_ROOT>/scripts/evolve.py" gate --task E001
python3 "<EVOLVE_ROOT>/scripts/evolve.py" finish --task E001 --summary "Cancelled saves retain document state; regression and review passed"
python3 "<EVOLVE_ROOT>/scripts/evolve.py" next
```

The example paths/commands describe a hypothetical project. Replace them with the
actual application and evidence. Criteria are named check labels; define their
observable meaning in the task brief before implementation.

`add --depends-on E001` creates ordering. Only complete dependencies make a queued
task eligible. `start` refuses explicit file overlap with another active task;
this is a bookkeeping guard, not enforcement of filesystem ownership. Include
the real shared files and coordinate integration.

`move --task E001 --status blocked|deferred|rejected|queued --reason "..."`
records a decision. Requeue affected work explicitly rather than silently erasing
history. `delivery --task E001 --status local|committed|pr|merged --ref "..."`
records a separately verified delivery result for a completed task.

## What freshness means

The snapshot hashes tracked files and Git-visible untracked files, including
deletions, executable modes, symlink identities and initialized submodule snapshots,
excluding `.evolve/`. Symlink targets are not followed. Git-ignored untracked
files are outside it. Required runtime/config/generated inputs outside that set
need their own verified evidence; this is not a hermetic build attestation.

`run` registers a pending attempt before executing an explicit argv without a shell,
captures bounded combined output,
records actual exit/timeout status, and compares before/after snapshots. Commands
that change the snapshot cannot provide fresh verification until a later stable
check is run. The newest attempt for each criterion is authoritative. All criteria
must have fresh passing evidence for `gate`/`finish`.

Running attempts block completion. Overlapping attempts for the same task/criterion
are refused so an older pass cannot supersede a newer failure. If a runner crashes,
verify it has stopped and use `recover-check --task E001 --criterion regression
--reason "verified abandoned runner"` to mark the attempt interrupted, then recheck.
Recovery does not cancel a live command or turn its result into a pass.

`observe` records the operator's declared result, detail and the artifact hash.
It checks existence/freshness; it cannot prove a screenshot was inspected or an
observation is true. The agent remains responsible for actual inspection.

Logs and recorded arguments are redacted on a best-effort basis. Never put secrets
in command arguments or print confidential inputs. Inspect artifacts before sharing;
the helper does not discover every possible private value.

## Resume and interruption

Run `status` and `reconcile`, compare the current source with the saved baseline,
and inspect active or completed tasks whose evidence has become stale. Revalidate
relevant scope after another contributor's changes. Do not replay destructive
commands merely because an old task is active.

State writes are atomic and serialized with `.evolve/lock`. A crashed writer may
leave a lock. Verify no writer remains before removing that lock; never auto-break
it because it looks old. Do not overwrite corrupt state; preserve/recover it and
report lost evidence. `init` is idempotent and never replaces an existing goal/mode.

The ledger does not reset the application or create a background runtime. Leave
the next action, actual blockers, source/delivery refs and unfinished work clear
enough for another session to continue.
