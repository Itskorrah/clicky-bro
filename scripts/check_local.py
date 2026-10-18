#!/usr/bin/env python3
"""Run clicky-bro's offline checks without GitHub Actions or surprise installs.

Exit 0: all selected checks passed; 1: at least one failed; 2: none failed but
at least one was skipped. A skipped check is never evidence of a passing build.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from typing import Callable, Optional

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Check:
    name: str
    argv: tuple[str, ...]
    prerequisite: str = "always"
    timeout: int = 240


@dataclass(frozen=True)
class Result:
    name: str
    status: str
    elapsed_seconds: float
    return_code: Optional[int] = None
    reason: str = ""


def checklist(*, native: bool = False, windows: bool = False, linux: bool = False) -> list[Check]:
    python = sys.executable
    checks = [
        Check("root-python", (python, "-m", "unittest", "discover", "-s", "tests", "-v"), timeout=180),
        Check("agent-typecheck", ("npm", "run", "typecheck", "--prefix", "app", "--workspace", "agent"), "npm-deps"),
        Check("agent-build", ("npm", "run", "build", "--prefix", "app", "--workspace", "agent"), "npm-deps"),
        Check("agent-tests", ("npm", "run", "test", "--prefix", "app", "--workspace", "agent", "--", "--maxWorkers=1"), "npm-deps", 600),
        Check("backend-typecheck", ("npm", "run", "typecheck", "--prefix", "app", "--workspace", "backend"), "npm-deps"),
        Check("backend-tests", ("npm", "run", "test", "--prefix", "app", "--workspace", "backend"), "npm-deps", 600),
        Check("eslint", ("npm", "run", "lint", "--prefix", "app"), "npm-deps"),
    ]
    if native:
        checks.append(Check("macos-native-tests", (python, "scripts/dev.py", "test-native"), "macos", 1800))
    if windows:
        checks.append(Check("windows-core-tests", (
            "dotnet", "test", "app/windows/tests/OpenClicky.Core.Tests/OpenClicky.Core.Tests.csproj", "--nologo",
        ), "dotnet", 1200))
    if linux:
        checks.append(Check("linux-python-tests", (python, "-m", "pytest", "app/linux/tests", "-q"), "pytest", 600))
    return checks


def unavailable(check: Check, root: Path, *, system: Optional[str] = None,
                which: Callable[[str], Optional[str]] = shutil.which) -> str:
    system = system or platform.system()
    if check.prerequisite == "macos" and system != "Darwin":
        return "macOS/Xcode required; this platform cannot verify native AppKit or TCC"
    if check.prerequisite == "npm-deps" and not (root / "app/node_modules").is_dir():
        return "npm dependencies absent; run npm ci --prefix app --ignore-scripts manually"
    if check.prerequisite == "pytest":
        try:
            import pytest  # noqa: F401 - explicit prerequisite check
        except ImportError:
            return "pytest not installed in the selected Python environment"
    tool = check.argv[0]
    if tool != sys.executable and not which(tool):
        return f"{tool} is not installed or not on PATH"
    if check.prerequisite == "dotnet" and not which("dotnet"):
        return "dotnet SDK unavailable"
    return ""


def execute(check: Check, root: Path, *, system: Optional[str] = None,
            which: Callable[[str], Optional[str]] = shutil.which,
            runner: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> Result:
    reason = unavailable(check, root, system=system, which=which)
    if reason:
        return Result(check.name, "skipped", 0.0, reason=reason)
    start = time.monotonic()
    try:
        completed = runner(check.argv, cwd=root, capture_output=True, text=True,
                           timeout=check.timeout, check=False)
        status = "passed" if completed.returncode == 0 else "failed"
        # Do not persist stdout/stderr: a provider test could accidentally print secrets.
        return Result(check.name, status, round(time.monotonic() - start, 3),
                      return_code=completed.returncode,
                      reason="" if status == "passed" else "Check exited non-zero; rerun the command for details")
    except subprocess.TimeoutExpired:
        return Result(check.name, "failed", round(time.monotonic() - start, 3),
                      reason=f"Timed out after {check.timeout}s")
    except OSError as error:
        return Result(check.name, "failed", round(time.monotonic() - start, 3),
                      reason=f"Could not start check: {type(error).__name__}")


def exit_code(results: list[Result]) -> int:
    if any(r.status == "failed" for r in results):
        return 1
    if any(r.status == "skipped" for r in results):
        return 2
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true", help="include macOS native tests (requires a Mac)")
    parser.add_argument("--windows", action="store_true", help="include portable .NET Windows core tests")
    parser.add_argument("--linux", action="store_true", help="include Linux Python/pytest tests")
    parser.add_argument("--list", action="store_true", help="show planned checks without running")
    parser.add_argument("--report", type=Path, help="write a status-only JSON report (never command output)")
    args = parser.parse_args(argv)
    checks = checklist(native=args.native, windows=args.windows, linux=args.linux)
    if args.list:
        for check in checks:
            print(f"{check.name}: {' '.join(check.argv)}")
        return 0
    results = []
    for check in checks:
        result = execute(check, ROOT)
        results.append(result)
        print(f"[{result.status.upper()}] {result.name}: {result.reason or str(result.elapsed_seconds) + 's'}", flush=True)
    summary = {"platform": platform.system(), "python": sys.version.split()[0],
               "results": [asdict(r) for r in results], "exit_code": exit_code(results)}
    if args.report:
        destination = args.report.resolve()
        if destination.exists():
            parser.error("Report already exists: choose a new path; existing evidence is preserved")
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(summary, stream, indent=2)
            stream.write("\n")
    print("All selected checks passed" if summary["exit_code"] == 0 else
          "Some checks failed" if summary["exit_code"] == 1 else "Some checks were skipped (not verified)")
    return summary["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
