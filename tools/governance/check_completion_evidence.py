"""E-GOV-003: Check that a completed-task report has required evidence.

Checks a completed-task README.md for the minimum evidence categories required
before acceptance: task card link, changed files summary, evidence artifacts,
and closure/gate decision.

Exit codes:
  0 — PASS (all required evidence categories present)
  1 — FAIL (one or more required categories missing or empty)
  2 — SKIP (not a completed-task directory, or file not found)

False-positive cases (documented):
  - Very old archives may use a different format and legitimately lack some
    sections. The tool checks for the presence of content patterns, not strict
    heading names.
  - A report may have evidence inlined in a different section name (e.g.
    "Verification" instead of "Evidence"). The tool uses multiple strategies.
  - Pure-documentation tasks may not have build/test evidence. The tool does
    not penalize missing build evidence if "Skipped Checks" or "Risks" section
    explains why.
  - The tool does not validate evidence quality — only presence of evidence
    markers. A passing score means evidence categories appear to be addressed,
    not that the evidence is correct.
"""

import argparse
import os
import re
import sys
from typing import Optional


# --- Section detection helpers ---

def _has_task_card_link(text: str) -> bool:
    """Check for a reference to a task card."""
    patterns = [
        r"docs/agentic/tasks/",                # path reference
        r"#[#]?\s*[Tt]ask\s*[Cc]ard",          # "# Task Card" or "## Task Card" heading
        r"[Tt]ask\s*[Cc]ard:",                 # "Task Card:" with colon
        r"\*\*Task Card\*\*",                   # bold markdown
        r"task_id:",                            # YAML frontmatter field
    ]
    return any(re.search(p, text) for p in patterns)


def _has_changed_files(text: str) -> bool:
    """Check for a summary of changed files or a git diff reference."""
    patterns = [
        r"[Ff]iles?\s*[Cc]hanged",         # "Files Changed" heading
        r"[Cc]hanged\s*[Ff]iles?",          # "Changed Files" heading
        r"[Cc]hanged:",                      # "Changed:" inline label
        r"[Cc]ommit[:\s]",                   # commit reference
        r"git\s+diff",                      # git diff reference
        r"Files?\s*[Aa]nd\s*[Aa]rtifacts", # "Files And Artifacts" heading
        r"[Ww]hat\s*[Cc]hanged",            # "What Changed" heading
    ]
    return any(re.search(p, text) for p in patterns)


def _has_evidence_artifacts(text: str) -> bool:
    """Check for evidence of validation, testing, or verification."""
    patterns = [
        r"#[#]?\s*[Ee]vidence",              # "## Evidence" or "# Evidence" heading
        r"[Ee]vidence:",                       # "Evidence:" inline label
        r"```(?:text|bash|bat|sh|shell)",     # code block with commands
        r"(?:passed|PASSED|\[OK\])",          # pass markers
        r"CTest|ctest",                       # test runner
        r"validate-",                         # validate-docs, validate-task-card, etc.
        r"pytest|unittest",                   # Python test runner
        r"build.*pass|pass.*build",           # build evidence
        r"[Cc]losure\s*[Ss]core",             # closure score output
        r"run-quality-gates",                 # quality gate invocation
        r"check-dependencies",                # dependency check
    ]
    return any(re.search(p, text) for p in patterns)


def _has_gate_decision(text: str) -> bool:
    """Check for a closure or gate decision."""
    patterns = [
        r"[Gg]ate\s*[Dd]ecision",           # explicit gate decision heading
        r"[Cc]losure\s*[Ss]core",           # closure score
        r"[Dd]ecision",                      # decision section
        r"[Aa]ccept(?:ed|ance)?\s*[Gg]ate", # acceptance gate
        r"[Ss]tatus:\s*complete",            # YAML status
        r"[Rr]esidual\s*[Rr]isks?",          # residual risks (implies gate thinking)
        r"[Ss]kipped\s*[Cc]hecks",           # skipped checks (implies gate thinking)
        r"[Aa]rchive\s*[Hh]andoff",          # archive handoff
    ]
    return any(re.search(p, text) for p in patterns)


# --- Main check ---

def check_completion_evidence(report_path: str) -> dict:
    """Check a completed-task report for required evidence categories.

    Args:
        report_path: Path to the README.md of a completed-task directory.

    Returns a dict with:
        passed: bool — True when all required categories are present
        skipped: bool — True when the path is not a completed-task report
        categories: dict of category name -> bool (present/absent)
        report_path: the path that was checked
        details: list of human-readable findings
    """
    if not os.path.isfile(report_path):
        return {
            "passed": False,
            "skipped": True,
            "categories": {},
            "report_path": report_path,
            "details": [f"File not found: {report_path}"],
        }

    # Require that we're in a completed-task directory
    normalized = report_path.replace("\\", "/")
    if "completed-tasks" not in normalized or not normalized.endswith("README.md"):
        return {
            "passed": False,
            "skipped": True,
            "categories": {},
            "report_path": report_path,
            "details": [
                "Not a completed-task report (path must contain 'completed-tasks' "
                "and end with README.md)"
            ],
        }

    with open(report_path, "r", encoding="utf-8") as fh:
        text = fh.read()

    if len(text.strip()) < 50:
        return {
            "passed": False,
            "skipped": True,
            "categories": {},
            "report_path": report_path,
            "details": ["Report is too short to contain meaningful evidence."],
        }

    categories = {
        "task_card_link": _has_task_card_link(text),
        "changed_files": _has_changed_files(text),
        "evidence_artifacts": _has_evidence_artifacts(text),
        "gate_decision": _has_gate_decision(text),
    }

    all_present = all(categories.values())
    details: list[str] = []

    if not categories["task_card_link"]:
        details.append("MISSING: task card link (reference to docs/agentic/tasks/)")
    if not categories["changed_files"]:
        details.append("MISSING: changed files summary (no file list or commit hash found)")
    if not categories["evidence_artifacts"]:
        details.append("MISSING: evidence artifacts (no test results, validation output, or build evidence)")
    if not categories["gate_decision"]:
        details.append("MISSING: gate decision (no acceptance, closure score, or residual risk assessment)")

    if all_present:
        details.append("All required evidence categories present.")

    return {
        "passed": all_present,
        "skipped": False,
        "categories": categories,
        "report_path": report_path,
        "details": details,
    }


# --- CLI ---

def main() -> int:
    parser = argparse.ArgumentParser(
        description="E-GOV-003: Check completed-task report for required evidence."
    )
    parser.add_argument(
        "report_path", nargs="?",
        help="Path to the completed-task README.md file.",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output result as JSON.",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Check all completed-task reports under docs/completed-tasks/.",
    )
    args = parser.parse_args()

    if args.all:
        return _run_all(args)

    if not args.report_path:
        parser.error("report_path is required unless --all is used")

    result = check_completion_evidence(args.report_path)
    _print_result(result, args.json)

    if result.get("skipped", False):
        return 2
    return 0 if result.get("passed", False) else 1


def _run_all(args) -> int:
    """Check all completed-task reports."""
    # Find repo root from current working directory
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            repo_root = result.stdout.strip()
        else:
            repo_root = os.getcwd()
    except Exception:
        repo_root = os.getcwd()

    completed_dir = os.path.join(repo_root, "docs", "completed-tasks")

    if not os.path.isdir(completed_dir):
        print("ERROR: docs/completed-tasks/ not found", file=sys.stderr)
        return 2

    all_results: list[dict] = []
    for entry in sorted(os.listdir(completed_dir)):
        entry_path = os.path.join(completed_dir, entry)
        readme = os.path.join(entry_path, "README.md")
        if os.path.isdir(entry_path) and os.path.isfile(readme):
            result = check_completion_evidence(readme)
            all_results.append(result)
            if not args.json:
                status = (
                    "PASS" if result["passed"]
                    else "SKIP" if result["skipped"]
                    else "FAIL"
                )
                print(f"[{status}] {entry}")

    passed = sum(1 for r in all_results if r["passed"])
    failed = sum(1 for r in all_results if not r["passed"] and not r["skipped"])
    skipped = sum(1 for r in all_results if r["skipped"])

    if not args.json:
        print(f"\nTotal: {len(all_results)} | PASS: {passed} | FAIL: {failed} | SKIP: {skipped}")

    return 1 if failed > 0 else 0


def _print_result(result: dict, as_json: bool) -> None:
    if as_json:
        import json
        json.dump(result, sys.stdout, indent=2)
        print()
        return

    if result.get("skipped", False):
        print("E-GOV-003 SKIPPED:", result["details"][0] if result["details"] else "")
        return

    cats = result["categories"]
    if result["passed"]:
        print(f"E-GOV-003 PASSED: All {sum(1 for v in cats.values() if v)}/{len(cats)} "
              f"evidence categories present.")
    else:
        missing = sum(1 for v in cats.values() if not v)
        present = sum(1 for v in cats.values() if v)
        print(f"E-GOV-003 FAILED: {missing}/{len(cats)} evidence categories missing "
              f"({present}/{len(cats)} present).")
    print()
    for detail in result["details"]:
        print(f"  {detail}")


if __name__ == "__main__":
    sys.exit(main())
