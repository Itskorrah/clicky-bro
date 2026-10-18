"""Small, portable primitives shared by Evolve's optional helpers."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import threading
import time
from datetime import datetime, timezone


class EvolveError(Exception):
    """An actionable condition that should not produce a traceback."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def project_root(value: str = ".") -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise EvolveError(f"Project directory does not exist: {root}")
    return root


def relative_path(value: str) -> Path:
    # Reject both POSIX and Windows traversal even on a different host OS.
    if not value or value.startswith("/") or "\\" in value or ":" in value:
        raise EvolveError("Use a non-empty project-relative path with forward slashes.")
    path = Path(value)
    if path.is_absolute() or any(p in {"", ".", ".."} for p in value.split("/")):
        raise EvolveError("Paths must stay within the project; traversal is refused.")
    return path


def managed_path(root: Path, relative: str) -> Path:
    path = root / relative_path(relative)
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            raise EvolveError(f"Symlink in managed path: {current}")
    return path


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix=".evolve-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise EvolveError(f"Cannot read valid JSON from {path.name}: {error}") from error
    if not isinstance(data, dict):
        raise EvolveError(f"Expected a JSON object in {path.name}.")
    return data


def git(root: Path, *arguments: str, allow_failure: bool = False) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments], capture_output=True, timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise EvolveError("Git is unavailable or timed out; use the manual workflow.") from error
    if result.returncode and not allow_failure:
        raise EvolveError("A working Git repository is required for this helper.")
    return result.stdout


def repository_files(root: Path) -> list[str]:
    if git(root, "rev-parse", "--show-toplevel").decode().strip() != str(root):
        # Resolve platform path spelling (e.g. /private/var on macOS).
        actual = Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
        if actual != root:
            raise EvolveError("Run the helper at the repository root, not a nested directory.")
    files = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return sorted(set(os.fsdecode(p) for p in files.split(b"\0") if p))


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def snapshot(root: Path, visited: set[Path] | None = None) -> dict:
    """Hash tracked and visible untracked files; never emit their contents."""
    visited = set(visited or ())
    if root in visited or len(visited) >= 16:
        raise EvolveError("Submodule snapshot recursion is cyclic or too deep; inspect it before verification.")
    visited.add(root)
    gitlinks = {}
    for entry in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, filename = entry.split(b"\t", 1)
        mode, revision, stage = metadata.split()
        if mode == b"160000":
            gitlinks.setdefault(os.fsdecode(filename), []).append(revision + b":" + stage)
    digest = hashlib.sha256()
    for name in repository_files(root):
        if name == ".evolve" or name.startswith(".evolve/"):
            continue
        path = root / name
        digest.update(os.fsencode(name) + b"\0")
        link = next((p for p in (path, *path.parents) if p != root and root in p.parents and p.is_symlink()), None)
        if link is not None:
            digest.update(b"link\0" + os.fsencode(str(link.relative_to(root))) + b"\0" + os.fsencode(os.readlink(link)))
        elif name in gitlinks:
            digest.update(b"gitlink\0" + b",".join(sorted(gitlinks[name])))
            if (path / ".git").exists():
                nested = snapshot(path.resolve(), visited)
                digest.update(b"initialized\0" + str(nested["revision"]).encode() + b"\0" + nested["fingerprint"].encode())
            else:
                digest.update(b"uninitialized\0")
        elif path.is_file():
            digest.update(b"file\0" + str(path.stat().st_mode & 0o111).encode() + b"\0" + file_hash(path).encode())
        else:
            digest.update(b"missing\0")
    revision = git(root, "rev-parse", "--verify", "HEAD", allow_failure=True).decode().strip() or None
    return {"revision": revision, "fingerprint": digest.hexdigest(),
            "algorithm": "git-worktree-sha256-v1", "time": now()}


def redact(value: str) -> str:
    """Best effort only: callers must still inspect evidence before sharing."""
    for key, secret in os.environ.items():
        if len(secret) >= 8 and re.search(r"TOKEN|SECRET|PASSWORD|API.?KEY", key, re.I):
            value = value.replace(secret, "<REDACTED>")
    value = re.sub(r"\b(?:gh[pousr]_[A-Za-z0-9_]{10,}|github_pat_[A-Za-z0-9_]+|sk-(?:proj-)?[A-Za-z0-9_-]{12,}|AKIA[A-Z0-9]{16})\b", "<REDACTED>", value)
    value = re.sub(r"(?i)(authorization\s*:\s*(?:bearer|basic)\s+)\S+", r"\1<REDACTED>", value)
    value = re.sub(r"(?i)((?:password|api[_-]?key|secret|token)\s*[:=]\s*)[^\s,;]+", r"\1<REDACTED>", value)
    return value


def redact_argv(arguments: list[str]) -> list[str]:
    result = []
    hide_next = False
    for argument in arguments:
        result.append("<REDACTED>" if hide_next else redact(argument))
        hide_next = bool(re.fullmatch(r"--?(?:password|token|secret|api[-_]key)", argument, re.I))
    return result


def run_command(root: Path, arguments: list[str], timeout: float) -> dict:
    """Execute an explicit argv without a shell; drain bounded combined output."""
    if not arguments or not 0 < timeout <= 3600:
        raise EvolveError("Supply a command and a timeout greater than 0 and at most 3600 seconds.")
    started = time.perf_counter()
    options = {"start_new_session": True} if os.name != "nt" else {
        "creationflags": subprocess.CREATE_NEW_PROCESS_GROUP
    }
    try:
        process = subprocess.Popen(arguments, cwd=root, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, **options)
    except OSError as error:
        raise EvolveError(f"Could not start the command: {redact(str(error))}") from error
    chunks = []
    size = 0
    truncated = False

    def drain():
        nonlocal size, truncated
        assert process.stdout is not None
        try:
            while True:
                block = os.read(process.stdout.fileno(), 8192)
                if not block:
                    break
                available = max(0, 512 * 1024 - size)
                if available:
                    chunks.append(block[:available])
                size += min(available, len(block))
                truncated |= len(block) > available
        except (OSError, ValueError):
            truncated = True
        finally:
            process.stdout.close()

    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                           capture_output=True, check=False)
            if process.poll() is None:
                process.kill()
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait(timeout=10)
    reader.join(timeout=2)
    incomplete = reader.is_alive()
    if reader.is_alive():
        # A detached child may keep the pipe open; don't certify complete output.
        truncated = True
        if os.name != "nt":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        reader.join(timeout=2)
        if reader.is_alive() and process.stdout is not None:
            process.stdout.close()
    output = redact(b"".join(chunks).decode("utf-8", errors="replace"))
    return {
        "argv": redact_argv(arguments), "exit_code": process.returncode,
        "status": "timeout" if timed_out else ("incomplete" if incomplete else ("pass" if process.returncode == 0 else "fail")),
        "seconds": round(time.perf_counter() - started, 6),
        "output": output, "output_truncated": truncated,
    }


class StateLock:
    def __init__(self, root: Path):
        self.path = managed_path(root, ".evolve/lock")

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        deadline = time.monotonic() + 5
        while True:
            try:
                descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                with os.fdopen(descriptor, "w") as handle:
                    handle.write(f"pid={os.getpid()} time={now()}\n")
                return self
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise EvolveError("State is locked. Wait for the writer; after a crash, verify no writer remains before removing .evolve/lock.")
                time.sleep(0.05)

    def __exit__(self, *unused):
        self.path.unlink()
