#!/usr/bin/env python3
"""Collect wall-clock samples or compare explicit, comparable benchmark records."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform
import statistics
import sys

from common import (EvolveError, atomic_json, load_json, managed_path,
                    now, project_root, run_command, snapshot)


def validate(record: dict) -> None:
    required = ("name", "unit", "direction", "workload", "environment", "samples")
    if any(key not in record for key in required):
        raise EvolveError("Benchmark requires name, unit, direction, workload, environment and samples.")
    if any(not isinstance(record[key], str) or not record[key].strip() for key in ("name", "unit", "workload")):
        raise EvolveError("Benchmark name, unit and workload must be non-empty strings.")
    if record["direction"] not in {"lower", "higher"}:
        raise EvolveError("direction must be lower or higher.")
    environment = record["environment"]
    if not isinstance(environment, dict) or any(not environment.get(k) for k in ("machine", "runtime", "mode")):
        raise EvolveError("environment must identify machine, runtime and mode.")
    samples = record["samples"]
    if not isinstance(samples, list) or len(samples) < 3:
        raise EvolveError("At least three actual samples are required.")
    if any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or x <= 0 for x in samples):
        raise EvolveError("Samples must be positive finite numbers.")


def summary(samples: list[float]) -> dict:
    median = statistics.median(samples)
    deviation = statistics.median(abs(x - median) for x in samples)
    return {"count": len(samples), "median": median, "min": min(samples),
            "max": max(samples), "relative_mad_percent": 100 * deviation / median}


def compare(before: dict, after: dict) -> dict:
    validate(before)
    validate(after)
    for field in ("name", "unit", "direction", "workload", "environment"):
        if before[field] != after[field]:
            raise EvolveError(f"Incomparable benchmarks: {field} differs.")
    old, new = summary(before["samples"]), summary(after["samples"])
    change = 100 * (new["median"] - old["median"]) / old["median"]
    improvement = -change if before["direction"] == "lower" else change
    noise = max(old["relative_mad_percent"], new["relative_mad_percent"])
    return {"name": before["name"], "unit": before["unit"], "before": old,
            "after": new, "improvement_percent": improvement,
            "within_observed_variation": abs(improvement) <= noise,
            "limit": "Descriptive repeated measurements, not a statistical significance test or causal proof."}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action", required=True)
    comparison = sub.add_parser("compare")
    comparison.add_argument("before")
    comparison.add_argument("after")
    comparison.add_argument("--max-regression", type=float, help="Fail if median regression exceeds this percentage")
    run = sub.add_parser("run")
    run.add_argument("--project", default=".")
    run.add_argument("--name", required=True)
    run.add_argument("--workload", required=True)
    run.add_argument("--runtime", required=True, help="Runtime/compiler version relevant to the workload")
    run.add_argument("--machine", required=True, help="Explicit runner/hardware identity shared only by comparable runs")
    run.add_argument("--mode", required=True, help="For example release, debug, warm-cache")
    run.add_argument("--samples", type=int, default=7)
    run.add_argument("--warmups", type=int, default=1)
    run.add_argument("--timeout", type=float, default=120)
    run.add_argument("--output", required=True, help="New project-relative JSON file")
    run.add_argument("command", nargs=argparse.REMAINDER)
    args = p.parse_args(argv)
    try:
        if args.action == "compare":
            result = compare(load_json(Path(args.before)), load_json(Path(args.after)))
            if args.max_regression is not None and (not math.isfinite(args.max_regression) or args.max_regression < 0):
                raise EvolveError("max-regression must be a finite non-negative percentage.")
            print(json.dumps(result, indent=2, allow_nan=False))
            return 1 if args.max_regression is not None and -result["improvement_percent"] > args.max_regression else 0
        root = project_root(args.project)
        if not 3 <= args.samples <= 100 or not 0 <= args.warmups <= 20:
            raise EvolveError("Use 3–100 samples and 0–20 warmups.")
        output = managed_path(root, args.output)
        if output.exists():
            raise EvolveError("Output exists; choose a new benchmark filename.")
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        before = snapshot(root)
        samples = []
        command_record = None
        for index in range(args.warmups + args.samples):
            result = run_command(root, command, args.timeout)
            if result["status"] != "pass":
                raise EvolveError("Benchmark command failed or timed out; no passing record was written.")
            command_record = result["argv"]
            if index >= args.warmups:
                samples.append(result["seconds"])
        after = snapshot(root)
        if before["fingerprint"] != after["fingerprint"]:
            raise EvolveError("Benchmark changed source files; results are not a stable workload.")
        record = {"version": 1, "name": args.name, "unit": "seconds", "direction": "lower",
                  "workload": args.workload, "samples": samples, "warmups": args.warmups,
                  "environment": {"machine": args.machine, "os": platform.platform(), "architecture": platform.machine(),
                                  "runtime": args.runtime, "mode": args.mode, "argv": command_record},
                  "source": before, "collected": now(),
                  "limit": "Process wall-clock time includes launch and output capture overhead. Use a profiler for internal latency or memory."}
        validate(record)
        atomic_json(output, record)
        print(json.dumps({"output": args.output, "summary": summary(samples)}, indent=2))
        return 0
    except (EvolveError, OSError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
