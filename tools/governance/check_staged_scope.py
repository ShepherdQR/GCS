"""E-GOV-001: Check that staged files match task scope.

Reads a task card's ``affected_paths`` (from YAML frontmatter or heading
section) and compares them against ``git diff --cached --name-only``.
Reports any staged files that fall outside the declared scope.

Exit codes:
  0 — PASS (all staged files in scope, or no staged files)
  1 — FAIL (one or more staged files outside scope)
  2 — SKIP (could not determine scope, e.g. no task card or no paths)

False-positive cases (documented):
  - CLAUDE.md, AGENTS.md, .claude/ files may be auto-staged by tooling but
    not listed in task scope. Use --allowlist for these.
  - Shared infrastructure files (CMakeLists.txt, scripts/) may need to be
    touched across many tasks. Prefer listing them explicitly in the task
    card rather than using a blanket allowlist.
  - Generated or lock files (audit.db, __pycache__) should not be staged
    for task-scoped commits. If they appear, the staging was likely a
    mistake.
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


def _parse_yaml_frontmatter_paths(text: str) -> list[str]:
    """Extract ``affected_paths`` from YAML frontmatter (``---`` delimited).

    Handles the task card YAML frontmatter convention:
        ---
        affected_paths:
          - docs/agentic/
          - src/gcs/kernel/
        ---
    """
    if not text.startswith("---"):
        return []

    end = text.find("---", 3)
    if end == -1:
        return []

    frontmatter = text[3:end]
    paths: list[str] = []
    in_affected = False

    for line in frontmatter.splitlines():
        stripped = line.strip()
        if stripped.startswith("affected_paths:"):
            in_affected = True
            # Check for inline list: affected_paths: [path1, path2]
            inline = stripped[len("affected_paths:"):].strip()
            if inline.startswith("[") and inline.endswith("]"):
                for item in inline[1:-1].split(","):
                    item = item.strip().strip("\"'")
                    if item:
                        paths.append(item)
                in_affected = False
            continue

        if in_affected:
            if stripped.startswith("- "):
                path = stripped[2:].strip().strip("\"'")
                if path:
                    paths.append(path)
            elif stripped.startswith("-"):
                path = stripped[1:].strip().strip("\"'")
                if path:
                    paths.append(path)
            elif stripped and not stripped.startswith("#"):
                # Next top-level key — exit affected_paths block
                if not stripped.startswith("  ") and not stripped.startswith("\t"):
                    in_affected = False

    return paths


def _read_task_affected_paths(task_card_path: str) -> list[str]:
    """Extract affected_paths from a task card markdown file.

    Parses YAML frontmatter first (the primary convention for GCS task cards),
    then falls back to heading-based bullet lists. Returns the list of path
    prefixes that the task is scoped to.
    """
    if not os.path.isfile(task_card_path):
        return []

    with open(task_card_path, "r", encoding="utf-8") as fh:
        text = fh.read()

    # Strategy 1: YAML frontmatter (primary task card convention)
    paths = _parse_yaml_frontmatter_paths(text)
    if paths:
        return paths

    # Strategy 2: heading with bullet list
    heading_pattern = re.compile(
        r"##\s+Affected\s+Paths\s*\n(.*?)(?=\n##|\Z)", re.DOTALL
    )
    heading_match = heading_pattern.search(text)
    if heading_match:
        section = heading_match.group(1)
        for line in section.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                path = stripped[2:].strip().strip("`")
                if path:
                    paths.append(path)

    # Strategy 3: loose backtick-quoted path-like lines
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
        passed: bool — True when all staged files are in scope
        skipped: bool — True when scope could not be determined (no task card
            or no affected_paths found)
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

    skipped = len(scope_paths) == 0

    return {
        "passed": len(out_of_scope) == 0 and not skipped,
        "skipped": skipped,
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
        if result.get("skipped", False):
            print("E-GOV-001 SKIPPED: No affected_paths found in task card.")
            print(f"  Task card: {result['task_card_path']}")
            print("  Add 'affected_paths' to the task card's YAML frontmatter")
            print("  or use --allowlist to specify paths explicitly.")
        elif not result["staged_files"]:
            print("E-GOV-001 PASSED: No staged files. Nothing to check.")
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

    if result.get("skipped", False):
        return 2
    return 0 if result.get("passed", False) else 1


if __name__ == "__main__":
    sys.exit(main())
