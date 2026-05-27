"""E-GOV-001: Check that staged files match task scope.

Reads a task card's ``affected_paths`` and compares them against
``git diff --cached --name-only``. Reports any staged files that fall
outside the declared scope.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Optional


def _repo_root() -> str:
    """Return the absolute path to the git repository root."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError("Not in a git repository")
    return result.stdout.strip()


def _staged_files() -> list[str]:
    """Return list of staged file paths relative to repo root."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed: {result.stderr.strip()}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _read_task_affected_paths(task_card_path: str) -> list[str]:
    """Extract affected_paths from a task card markdown file.

    Looks for a fenced code block labelled ``affected_paths`` or a bullet list
    under an ``## Affected Paths`` heading. Returns the list of path prefixes
    that the task is scoped to.
    """
    if not os.path.isfile(task_card_path):
        return []

    with open(task_card_path, "r", encoding="utf-8") as fh:
        text = fh.read()

    paths: list[str] = []

    # Try to find a fenced code block labelled affected_paths
    block_pattern = re.compile(
        r"```\s*(?:text|yaml)?\s*\n"
        r"(?:#\s*affected_paths.*\n)?"
        r"(.*?)"
        r"```",
        re.DOTALL,
    )
    heading_pattern = re.compile(
        r"##\s+Affected\s+Paths\s*\n(.*?)(?=\n##|\Z)", re.DOTALL
    )

    # Strategy 1: look for heading with bullet list
    heading_match = heading_pattern.search(text)
    if heading_match:
        section = heading_match.group(1)
        for line in section.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                path = stripped[2:].strip().strip("`")
                if path:
                    paths.append(path)

    # Strategy 2: check for path-like lines anywhere
    if not paths:
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- `") and stripped.endswith("`"):
                path_candidate = stripped[3:-1].strip()
                if "/" in path_candidate or path_candidate.endswith(".md"):
                    paths.append(path_candidate)

    return paths


def _is_in_scope(file_path: str, scope_paths: list[str]) -> bool:
    """Check if a file path matches any of the scope path prefixes.

    A file ``docs/product/foo.md`` is in scope if any scope path such as
    ``docs/product/`` is a prefix of the file path.
    """
    normalized = file_path.replace("\\", "/")
    for scope in scope_paths:
        normalized_scope = scope.replace("\\", "/").rstrip("/")
        if normalized.startswith(normalized_scope + "/") or normalized == normalized_scope:
            return True
    return False


def check_staged_scope(
    task_card_path: str,
    *,
    allowlist: Optional[list[str]] = None,
) -> dict:
    """Run the E-GOV-001 scope check.

    Args:
        task_card_path: Path to the task card markdown file.
        allowlist: Optional list of additional allowed paths (e.g. CLAUDE.md).

    Returns a dict with:
        passed: bool
        staged_files: list of all staged paths
        in_scope: list of staged paths matching task scope
        out_of_scope: list of staged paths outside task scope
        task_card_path: the path that was checked
        scope_paths: the extracted scope path list
    """
    repo_root = _repo_root()

    staged = _staged_files()
    scope_paths = _read_task_affected_paths(task_card_path)
    if allowlist:
        scope_paths = list(scope_paths) + list(allowlist)

    in_scope: list[str] = []
    out_of_scope: list[str] = []
    for file_path in staged:
        if _is_in_scope(file_path, scope_paths):
            in_scope.append(file_path)
        else:
            out_of_scope.append(file_path)

    return {
        "passed": len(out_of_scope) == 0,
        "staged_files": staged,
        "in_scope": in_scope,
        "out_of_scope": out_of_scope,
        "task_card_path": task_card_path,
        "scope_paths": scope_paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="E-GOV-001: Check staged files against task card scope."
    )
    parser.add_argument(
        "task_card",
        help="Path to the task card markdown file.",
    )
    parser.add_argument(
        "--allowlist",
        nargs="*",
        default=None,
        help="Additional allowed path prefixes (optional).",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output result as JSON instead of human-readable text.",
    )
    args = parser.parse_args()

    try:
        result = check_staged_scope(args.task_card, allowlist=args.allowlist)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        if not result["staged_files"]:
            print("E-GOV-001: No staged files. Nothing to check.")
        elif result["passed"]:
            print(f"E-GOV-001 PASSED: All {len(result['staged_files'])} staged "
                  f"file(s) are within task scope.")
            for f in result["staged_files"]:
                print(f"  [OK] {f}")
        else:
            print(f"E-GOV-001 FAILED: {len(result['out_of_scope'])} of "
                  f"{len(result['staged_files'])} staged file(s) are outside "
                  f"task scope.")
            print()
            print("Task scope paths:")
            for s in result["scope_paths"]:
                print(f"  {s}")
            if not result["scope_paths"]:
                print("  (no scope paths found in task card)")
            print()
            print("In scope:")
            for f in result["in_scope"]:
                print(f"  [OK] {f}")
            if not result["in_scope"]:
                print("  (none)")
            print()
            print("Out of scope:")
            for f in result["out_of_scope"]:
                print(f"  [VIOLATION] {f}")

    return 0 if result.get("passed", False) else 1


if __name__ == "__main__":
    sys.exit(main())
