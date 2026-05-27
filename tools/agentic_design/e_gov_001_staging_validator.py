#!/usr/bin/env python3
r"""E-GOV-001 staging validator candidate.

Checks that staged files are within the claimed task scope and no secret-like
files are accidentally staged.  Uses only the Python standard library so it can
run in restricted local environments.

Usage:
  python tools\agentic_design\e_gov_001_staging_validator.py --staged
  python tools\agentic_design\e_gov_001_staging_validator.py --staged --scope docs/product/
  python tools\agentic_design\e_gov_001_staging_validator.py --staged --task-card docs/agentic/tasks/my-task.md
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]

SECRET_PATTERNS: tuple[str, ...] = (
    ".env",
    "credentials.json",
    "credentials",
    "secret",
    "*.pem",
    "*.key",
    "*.pfx",
    "*.p12",
    "*.keystore",
    ".npmrc",
    ".pypirc",
    "service-account.json",
    "id_rsa",
    "id_ed25519",
)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def git_staged_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[FAIL] git diff --cached failed: {result.stderr.strip()}")
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def looks_like_secret(file_path: str) -> tuple[bool, str]:
    name = Path(file_path).name.lower()
    for pattern in SECRET_PATTERNS:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True, pattern
        elif name == pattern or pattern in name:
            return True, pattern
    return False, ""


def read_task_card_scope(task_card_path: str | None) -> list[str] | None:
    if task_card_path is None:
        return None
    card = ROOT / task_card_path
    if not card.exists():
        print(f"[WARN] Task card not found: {task_card_path}")
        return None
    text = card.read_text(encoding="utf-8")
    scope: list[str] = []
    for line in text.splitlines():
        if line.startswith("affected_paths:") or line.startswith("scope:"):
            scope.extend(p.strip() for p in line.split(":", 1)[1].split(",") if p.strip())
    return scope or None


def build_allowlist() -> list[str]:
    return [
        "docs/agentic/tasks/",
        "docs/completed-tasks/",
        "docs/agentic/metrics-dashboard.md",
        "docs/architecture/95-gcs-narrative-map.md",
        "docs/architecture/98-narrative-line-capability-demonstrations.md",
        "docs/architecture/99-weak-line-development-plan.md",
        "CLAUDE.md",
        ".claude/",
    ]


def check_staged(args: argparse.Namespace) -> int:
    staged = git_staged_files()
    if not staged:
        print("[OK]  No staged files.")
        return 0

    failures = 0

    # --- Check 1: secret-like files ---
    for f in staged:
        is_secret, pattern = looks_like_secret(f)
        if is_secret:
            print(f"[FAIL] Secret-like file staged: {f} (matches pattern: {pattern})")
            failures += 1
    if not any(looks_like_secret(f)[0] for f in staged):
        print("[OK]  No secret-like files staged.")

    # --- Check 2: scope check ---
    scope = args.scope
    if args.task_card:
        scope = read_task_card_scope(args.task_card)
        if scope:
            scope = [s.strip() for s in scope]

    if scope:
        allowlist = build_allowlist()
        for f in staged:
            in_scope = any(f.startswith(s) for s in scope)
            allowed = any(f.startswith(a) for a in allowlist)
            if not in_scope and not allowed:
                print(f"[FAIL] File outside task scope: {f}")
                print(f"       scope={scope}")
                failures += 1
        if all(any(f.startswith(s) for s in scope) or any(f.startswith(a) for a in allowlist) for f in staged):
            print(f"[OK]  All staged files within scope or allowlist. scope={scope}")
    else:
        print("[INFO] No scope provided; skipping scope check. Use --scope or --task-card.")

    # --- Summary ---
    if failures:
        print(f"\n{failures} violation(s) found.")
        return 1
    else:
        print(f"\n[OK]  All checks passed ({len(staged)} staged file(s)).")
        return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="E-GOV-001 staging validator candidate")
    parser.add_argument("--staged", action="store_true", help="Check staged files")
    parser.add_argument("--scope", help="Comma-separated scope prefixes")
    parser.add_argument("--task-card", help="Path to task card (reads scope from affected_paths)")
    args = parser.parse_args(argv)

    if not args.staged:
        parser.print_help()
        return 0

    return check_staged(args)


if __name__ == "__main__":
    raise SystemExit(main())
