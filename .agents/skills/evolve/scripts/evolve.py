#!/usr/bin/env python3
"""Persistent tasks and evidence. State records work; it never grants permission."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

from common import (EvolveError, StateLock, atomic_json, file_hash, load_json,
                    managed_path, now, project_root, redact, relative_path,
                    redact_argv, run_command, snapshot)

CATEGORIES = ("correctness", "security", "performance", "architecture", "product", "design", "tests", "dependencies", "tooling", "docs")
CONFIDENCE = {"high": 1.0, "medium": 0.6, "low": 0.25}


def read_state(root: Path) -> dict:
    path = managed_path(root, ".evolve/state.json")
    if not path.is_file():
        raise EvolveError("No Evolve state. Run init first.")
    state = load_json(path)
    if state.get("version") != 1 or state.get("project") != str(root) or not isinstance(state.get("tasks"), list):
        raise EvolveError("State version/project is invalid. Do not overwrite it; reconcile or recover a backup.")
    validate_state(state)
    return state


def validate_state(state: dict) -> None:
    message = "State task/check structure is invalid. Preserve state.json and recover a verified backup; do not overwrite evidence."
    fingerprints = lambda s: isinstance(s, dict) and isinstance(s.get("fingerprint"), str) and bool(re.fullmatch(r"[0-9a-f]{64}", s["fingerprint"]))
    if not isinstance(state.get("goal"), str) or state.get("delivery_mode") not in {"local", "commit", "pr", "merge"} or not fingerprints(state.get("baseline")):
        raise EvolveError(message)
    identifiers = set()
    for task in state["tasks"]:
        if not isinstance(task, dict):
            raise EvolveError(message)
        identifier = task.get("id")
        if not isinstance(identifier, str) or not re.fullmatch(r"E[0-9]{3,}", identifier) or identifier in identifiers:
            raise EvolveError(message)
        identifiers.add(identifier)
        if task.get("status") not in {"queued", "active", "complete", "blocked", "deferred", "rejected"} or task.get("category") not in CATEGORIES or task.get("confidence") not in CONFIDENCE:
            raise EvolveError(message)
        if any(isinstance(task.get(k), bool) or not isinstance(task.get(k), int) or not 1 <= task[k] <= 5 for k in ("impact", "effort", "risk")):
            raise EvolveError(message)
        if any(not isinstance(task.get(k), str) for k in ("title", "evidence")):
            raise EvolveError(message)
        for field in ("criteria", "files", "depends_on"):
            if not isinstance(task.get(field), list) or any(not isinstance(x, str) for x in task[field]):
                raise EvolveError(message)
        if not task["criteria"] or len(set(task["criteria"])) != len(task["criteria"]) or any(not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", c) for c in task["criteria"]):
            raise EvolveError(message)
        for filename in task["files"]:
            relative_path(filename)
        if not isinstance(task.get("checks"), list) or not isinstance(task.get("history"), list):
            raise EvolveError(message)
        for check in task["checks"]:
            if not isinstance(check, dict) or check.get("criterion") not in task["criteria"] or check.get("kind") not in {"command", "observation"} or check.get("status") not in {"running", "pass", "fail", "timeout", "error", "incomplete", "interrupted"}:
                raise EvolveError(message)
            if not fingerprints(check.get("before")) or not fingerprints(check.get("after")):
                raise EvolveError(message)
            if check["status"] == "running" and not isinstance(check.get("id"), str):
                raise EvolveError(message)
            if check.get("artifact"):
                relative_path(check["artifact"])
                if not isinstance(check.get("artifact_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", check["artifact_sha256"]):
                    raise EvolveError(message)
    for task in state["tasks"]:
        if any(d not in identifiers or d == task["id"] for d in task["depends_on"]):
            raise EvolveError(message)
    resolved = set()
    remaining = list(state["tasks"])
    while remaining:
        ready = [t for t in remaining if set(t["depends_on"]) <= resolved]
        if not ready:
            raise EvolveError("State dependencies contain a cycle. Preserve the ledger and correct the recorded dependencies.")
        resolved.update(t["id"] for t in ready)
        remaining = [t for t in remaining if t["id"] not in resolved]


def save_state(root: Path, state: dict) -> None:
    state["updated"] = now()
    atomic_json(managed_path(root, ".evolve/state.json"), state)


def task_by_id(state: dict, identifier: str) -> dict:
    for task in state["tasks"]:
        if task["id"] == identifier:
            return task
    raise EvolveError(f"Unknown task: {identifier}")


def eligible(state: dict, task: dict) -> bool:
    return all(task_by_id(state, dependency)["status"] == "complete" for dependency in task["depends_on"])


def priority(task: dict) -> float:
    return round(task["impact"] * CONFIDENCE[task["confidence"]] / task["effort"], 3)


def gate(root: Path, task: dict, current: dict | None = None) -> dict:
    current = current or snapshot(root)
    reasons = []
    if not task["criteria"]:
        reasons.append("No acceptance criteria registered.")
    for criterion in task["criteria"]:
        evidence = [e for e in task["checks"] if e["criterion"] == criterion]
        if not evidence:
            reasons.append(f"{criterion}: no evidence")
            continue
        latest = evidence[-1]
        if latest["status"] != "pass":
            reasons.append(f"{criterion}: latest result is {latest['status']}")
        if latest["before"]["fingerprint"] != latest["after"]["fingerprint"]:
            reasons.append(f"{criterion}: command changed the source snapshot")
        if latest["after"]["fingerprint"] != current["fingerprint"]:
            reasons.append(f"{criterion}: evidence is stale after source changes")
        if latest.get("artifact"):
            artifact = managed_path(root, latest["artifact"])
            if not artifact.is_file() or file_hash(artifact) != latest["artifact_sha256"]:
                reasons.append(f"{criterion}: inspected artifact is missing or changed")
    return {"task": task["id"], "ready": not reasons, "reasons": reasons,
            "snapshot": current, "limit": "Fresh evidence does not establish test adequacy or the truth of an observation."}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".", help="Repository root (default: working directory)")
    commands = p.add_subparsers(dest="action", required=True)
    init = commands.add_parser("init", help="Create state without replacing existing state")
    init.add_argument("--goal", required=True)
    init.add_argument("--delivery", choices=("local", "commit", "pr", "merge"), default="local")
    for name in ("status", "next", "reconcile"):
        commands.add_parser(name)
    add = commands.add_parser("add", help="Register a scoped task with evidence and named criteria")
    add.add_argument("--title", required=True)
    add.add_argument("--evidence", required=True)
    add.add_argument("--category", choices=CATEGORIES, required=True)
    for field in ("impact", "effort", "risk"):
        add.add_argument("--" + field, type=int, choices=range(1, 6), default=3)
    add.add_argument("--confidence", choices=CONFIDENCE, default="high")
    add.add_argument("--criterion", action="append", required=True)
    add.add_argument("--file", action="append", default=[])
    add.add_argument("--depends-on", action="append", default=[])
    for name in ("start", "gate"):
        commands.add_parser(name).add_argument("--task", required=True)
    finish = commands.add_parser("finish")
    finish.add_argument("--task", required=True)
    finish.add_argument("--summary", required=True)
    move = commands.add_parser("move", help="Requeue, defer, block or reject a task with a reason")
    move.add_argument("--task", required=True)
    move.add_argument("--status", choices=("queued", "blocked", "deferred", "rejected"), required=True)
    move.add_argument("--reason", required=True)
    run = commands.add_parser("run", help="Run an explicit argv and capture fresh check evidence")
    run.add_argument("--task", required=True)
    run.add_argument("--criterion", required=True)
    run.add_argument("--timeout", type=float, default=120)
    run.add_argument("command", nargs=argparse.REMAINDER)
    observe = commands.add_parser("observe", help="Record an inspected local artifact, not automated proof")
    observe.add_argument("--task", required=True)
    observe.add_argument("--criterion", required=True)
    observe.add_argument("--artifact", required=True)
    observe.add_argument("--detail", required=True)
    observe.add_argument("--outcome", choices=("pass", "fail"), required=True)
    delivery = commands.add_parser("delivery", help="Record separately verified delivery; does not perform Git actions")
    delivery.add_argument("--task", required=True)
    delivery.add_argument("--status", choices=("local", "committed", "pr", "merged"), required=True)
    delivery.add_argument("--ref", required=True)
    recover = commands.add_parser("recover-check", help="Mark an abandoned check interrupted after verifying its runner has stopped")
    recover.add_argument("--task", required=True)
    recover.add_argument("--criterion", required=True)
    recover.add_argument("--reason", required=True)
    return p


def check_active(task: dict, criterion: str) -> None:
    if task["status"] != "active":
        raise EvolveError("Start the task before recording evidence.")
    if criterion not in task["criteria"]:
        raise EvolveError("Criterion is not registered on the task.")


def execute(args: argparse.Namespace) -> tuple[dict, int]:
    root = project_root(args.project)
    if args.action == "init":
        with StateLock(root):
            if managed_path(root, ".evolve/state.json").exists():
                state = read_state(root)
                return {"created": False, "state": state}, 0
            state = {"version": 1, "project": str(root), "goal": redact(args.goal),
                     "delivery_mode": args.delivery, "created": now(),
                     "baseline": snapshot(root), "tasks": []}
            save_state(root, state)
            return {"created": True, "state": state}, 0
    if args.action in {"status", "next", "reconcile", "gate"}:
        state = read_state(root)
        if args.action == "status":
            return state, 0
        if args.action == "next":
            tasks = [t for t in state["tasks"] if t["status"] == "queued" and eligible(state, t)]
            tasks.sort(key=lambda t: (-priority(t), t["risk"], t["id"]))
            return {"next": tasks[0] if tasks else None,
                    "active": [t["id"] for t in state["tasks"] if t["status"] == "active"]}, 0
        if args.action == "gate":
            result = gate(root, task_by_id(state, args.task))
            return result, 0 if result["ready"] else 1
        current = snapshot(root)
        return {"snapshot": current,
                "source_changed_since_baseline": current["fingerprint"] != state["baseline"]["fingerprint"],
                "active": [t["id"] for t in state["tasks"] if t["status"] == "active"],
                "completed_with_stale_evidence": [t["id"] for t in state["tasks"] if t["status"] == "complete" and not gate(root, t, current)["ready"]],
                "instruction": "Reinspect changed scope; use move --status queued to reopen affected work. This report does not automatically rewrite history."}, 0
    if args.action in {"run", "observe"}:
        before = snapshot(root)
        with StateLock(root):
            state = read_state(root)
            task = task_by_id(state, args.task)
            check_active(task, args.criterion)
            if any(c["criterion"] == args.criterion and c["status"] == "running" for c in task["checks"]):
                raise EvolveError("This criterion already has a running check. Wait for it or recover an abandoned attempt explicitly.")
            attempt = f"C{len(task['checks']) + 1:04d}"
            task["checks"].append({"id": attempt, "kind": "command" if args.action == "run" else "observation",
                                   "criterion": args.criterion, "status": "running",
                                   "before": before, "after": before, "time": now(), "runner_pid": os.getpid()})
            save_state(root, state)
        if args.action == "run":
            command = args.command[1:] if args.command[:1] == ["--"] else args.command
            try:
                result = run_command(root, command, args.timeout)
            except EvolveError as error:
                result = {"argv": redact_argv(command), "exit_code": None,
                          "status": "error", "seconds": 0,
                          "output": redact(str(error)), "output_truncated": False}
            after = snapshot(root)
            check = {"kind": "command", "criterion": args.criterion, "before": before,
                     "after": after, **result}
            code = 0 if result["status"] == "pass" else 1
        else:
            try:
                artifact = managed_path(root, args.artifact)
                if not artifact.is_file():
                    raise EvolveError("Observation requires an existing project-relative artifact.")
                check = {"kind": "observation", "criterion": args.criterion,
                         "status": args.outcome, "detail": redact(args.detail),
                         "artifact": args.artifact, "artifact_sha256": file_hash(artifact),
                         "before": before, "after": snapshot(root)}
                code = 0 if args.outcome == "pass" else 1
            except (EvolveError, OSError) as error:
                check = {"kind": "observation", "criterion": args.criterion, "status": "error",
                         "detail": redact(str(error)), "before": before, "after": snapshot(root)}
                code = 1
        with StateLock(root):
            state = read_state(root)
            task = task_by_id(state, args.task)
            pending = next(c for c in task["checks"] if c.get("id") == attempt)
            if pending["status"] != "running":
                raise EvolveError("Attempt was recovered/interrupted; its late result cannot supply a pass.")
            pending.update(check)
            pending["completed"] = now()
            save_state(root, state)
        return pending, code
    with StateLock(root):
        state = read_state(root)
        if args.action == "add":
            criteria = list(dict.fromkeys(args.criterion))
            if any(not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", c) for c in criteria):
                raise EvolveError("Criteria must be lowercase labels such as regression, integration or review.")
            for path in args.file:
                relative_path(path)
            dependencies = list(dict.fromkeys(args.depends_on))
            for dependency in dependencies:
                task_by_id(state, dependency)
            identifier = f"E{max((int(t['id'][1:]) for t in state['tasks']), default=0) + 1:03d}"
            task = {"id": identifier, "title": redact(args.title), "evidence": redact(args.evidence),
                    "category": args.category, "impact": args.impact, "effort": args.effort,
                    "risk": args.risk, "confidence": args.confidence, "criteria": criteria,
                    "files": args.file, "depends_on": dependencies, "status": "queued",
                    "checks": [], "history": [{"time": now(), "status": "queued"}],
                    "delivery": None}
            state["tasks"].append(task)
        else:
            task = task_by_id(state, args.task)
            if args.action == "start":
                if task["status"] != "queued" or not eligible(state, task):
                    raise EvolveError("Only an eligible queued task can start; complete dependencies first.")
                for other in state["tasks"]:
                    if other["status"] == "active" and set(other["files"]) & set(task["files"]):
                        raise EvolveError("Another active task owns an overlapping file scope.")
                task["status"] = "active"
                task["started_snapshot"] = snapshot(root)
                task["history"].append({"time": now(), "status": "active"})
            elif args.action == "finish":
                if task["status"] != "active":
                    raise EvolveError("Only an active task can finish.")
                result = gate(root, task)
                if not result["ready"]:
                    raise EvolveError("Task cannot finish: " + "; ".join(result["reasons"]))
                task["status"] = "complete"
                task["summary"] = redact(args.summary)
                task["verified_snapshot"] = result["snapshot"]
                task["history"].append({"time": now(), "status": "complete"})
            elif args.action == "move":
                task["status"] = args.status
                task["history"].append({"time": now(), "status": args.status, "reason": redact(args.reason)})
            elif args.action == "delivery":
                if task["status"] != "complete":
                    raise EvolveError("Record delivery only for a completed task.")
                task["delivery"] = {"status": args.status, "ref": redact(args.ref), "time": now(),
                                    "limit": "Recorded by the operator; verify remote status using the hosting tools."}
            elif args.action == "recover-check":
                pending = [c for c in task["checks"] if c["criterion"] == args.criterion and c["status"] == "running"]
                if not pending:
                    raise EvolveError("No running attempt for this criterion.")
                for check in pending:
                    check["status"] = "interrupted"
                    check["recovery_reason"] = redact(args.reason)
                    check["completed"] = now()
        save_state(root, state)
        return task, 0


def main(argv: list[str] | None = None) -> int:
    try:
        result, code = execute(parser().parse_args(argv))
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return code
    except (EvolveError, OSError) as error:
        print(json.dumps({"error": redact(str(error))}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
