#!/usr/bin/env python3
"""Map repository files and exclusions without executing or reading source code."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from common import (EvolveError, atomic_json, git, managed_path, now,
                    project_root, repository_files)

EXCLUDED_PARTS = {".git", ".evolve", "node_modules", "target", "dist", "build",
                  "vendor", "__pycache__", ".venv", "venv", ".next", ".cache"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".keystore"}
LANGUAGES = {".py": "Python", ".rs": "Rust", ".ts": "TypeScript", ".tsx": "TypeScript",
             ".js": "JavaScript", ".jsx": "JavaScript", ".go": "Go", ".swift": "Swift",
             ".kt": "Kotlin", ".java": "Java", ".cs": "C#", ".cpp": "C++",
             ".c": "C", ".rb": "Ruby", ".php": "PHP", ".ex": "Elixir"}
MANIFESTS = {"package.json", "Cargo.toml", "pyproject.toml", "requirements.txt",
             "go.mod", "Package.swift", "Gemfile", "pom.xml", "build.gradle", "composer.json"}


def inventory(root: Path, limit: int = 20000) -> dict:
    if limit < 1:
        raise EvolveError("max-files must be positive.")
    candidates = repository_files(root)
    included = []
    excluded = []
    languages = Counter()
    for name in candidates:
        path = Path(name)
        reason = None
        if set(path.parts) & EXCLUDED_PARTS:
            reason = "generated, dependency or working-state directory"
        elif path.name == ".env" or path.name.startswith(".env.") or path.suffix.lower() in SENSITIVE_SUFFIXES:
            reason = "potential credentials; contents not read"
        elif (root / name).is_symlink():
            reason = "symlink; target not followed"
        elif not (root / name).is_file():
            reason = "missing/non-file"
        elif len(included) >= limit:
            reason = "inventory limit"
        if reason:
            excluded.append({"path": name, "reason": reason})
            continue
        included.append(name)
        if path.suffix in LANGUAGES:
            languages[LANGUAGES[path.suffix]] += 1
    return {
        "version": 1, "project": str(root), "generated": now(),
        "revision": git(root, "rev-parse", "--verify", "HEAD", allow_failure=True).decode().strip() or None,
        "files": included, "excluded": excluded,
        "languages_by_file_count": dict(languages.most_common()),
        "manifests": [n for n in included if Path(n).name in MANIFESTS],
        "instructions": [n for n in included if Path(n).name in {"AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md"}],
        "ci_files": [n for n in included if n.startswith(".github/workflows/") or Path(n).name in {".gitlab-ci.yml", "Jenkinsfile"}],
        "limit": "File inventory is not audit coverage. Ignored untracked files are absent; tracked generated files are explicitly excluded.",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".")
    p.add_argument("--max-files", type=int, default=20000)
    p.add_argument("--output", help="Project-relative JSON path; omit to print")
    args = p.parse_args(argv)
    try:
        root = project_root(args.project)
        data = inventory(root, args.max_files)
        if args.output:
            path = managed_path(root, args.output)
            if path.exists():
                raise EvolveError("Output already exists; choose a new inventory filename.")
            atomic_json(path, data)
            print(json.dumps({"output": args.output, "files": len(data["files"]), "excluded": len(data["excluded"])}))
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    except (EvolveError, OSError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
