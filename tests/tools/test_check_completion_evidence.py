"""Tests for E-GOV-003 check_completion_evidence validator."""

import os
import tempfile
import unittest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tools.governance.check_completion_evidence import (
    _has_task_card_link,
    _has_changed_files,
    _has_evidence_artifacts,
    _has_gate_decision,
    check_completion_evidence,
)


class EvidenceDetectionTests(unittest.TestCase):
    """Tests for individual evidence category detectors."""

    def test_task_card_link_by_path(self):
        self.assertTrue(_has_task_card_link(
            "Task Card: `docs/agentic/tasks/2026-05-28-foo.md`"
        ))

    def test_task_card_link_by_heading(self):
        self.assertTrue(_has_task_card_link(
            "## Task Card\n\nReference to the task card."
        ))

    def test_task_card_link_by_frontmatter(self):
        self.assertTrue(_has_task_card_link(
            "---\ntask_id: 2026-05-28-foo\n---\n"
        ))

    def test_task_card_link_missing(self):
        self.assertFalse(_has_task_card_link(
            "# Completed Task\n\nNo task card reference.\n"
        ))

    def test_changed_files_by_heading(self):
        self.assertTrue(_has_changed_files(
            "## Files Changed\n\n- `src/gcs/kernel/kernel.cpp`\n"
        ))

    def test_changed_files_by_commit(self):
        self.assertTrue(_has_changed_files(
            "Commit: `69c63a9`\n"
        ))

    def test_changed_files_by_section(self):
        self.assertTrue(_has_changed_files(
            "## What Changed\n\nAdded new module.\n"
        ))

    def test_changed_files_missing(self):
        self.assertFalse(_has_changed_files(
            "# Done\n\nTask is complete.\n"
        ))

    def test_evidence_artifacts_by_section(self):
        self.assertTrue(_has_evidence_artifacts(
            "## Evidence\n\n- validate-docs: passed\n"
        ))

    def test_evidence_artifacts_by_code_block(self):
        self.assertTrue(_has_evidence_artifacts(
            "```bash\npython tools/agentic_design/agentic_toolkit.py validate-docs\n```"
        ))

    def test_evidence_artifacts_by_test_runner(self):
        self.assertTrue(_has_evidence_artifacts(
            "CTest: 128 tests, 0 failures"
        ))

    def test_evidence_artifacts_missing(self):
        self.assertFalse(_has_evidence_artifacts(
            "The task is complete. No evidence section."
        ))

    def test_gate_decision_by_closure_score(self):
        self.assertTrue(_has_gate_decision(
            "Closure score: 38/40."
        ))

    def test_gate_decision_by_residual_risks(self):
        self.assertTrue(_has_gate_decision(
            "## Residual Risks\n\n- Minor uncertainty about future format.\n"
        ))

    def test_gate_decision_by_decision_section(self):
        self.assertTrue(_has_gate_decision(
            "## Decisions\n\n- Keep task-card validation opt-in.\n"
        ))

    def test_gate_decision_missing(self):
        self.assertFalse(_has_gate_decision(
            "# Done\n\nEverything is fine."
        ))


class CheckCompletionEvidenceTests(unittest.TestCase):
    """Tests for the main check_completion_evidence function."""

    def _write_temp_report(self, content: str) -> str:
        """Write content to a temp file path that looks like a completed-task report."""
        # Create a temp dir to look like a completed-task directory
        tmp_dir = tempfile.mkdtemp(prefix="completed-task-test-")
        report_path = os.path.join(tmp_dir, "README.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        # Rename dir to include 'completed-tasks' in path
        parent = tempfile.mkdtemp()
        completed_dir = os.path.join(parent, "docs", "completed-tasks", "test-task")
        os.makedirs(completed_dir, exist_ok=True)
        final_path = os.path.join(completed_dir, "README.md")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(content)
        # Clean up the tmp_dir
        import shutil
        shutil.rmtree(tmp_dir)
        # Return parent for cleanup
        self._cleanup_dirs = getattr(self, "_cleanup_dirs", [])
        self._cleanup_dirs.append(parent)
        return final_path

    def tearDown(self):
        import shutil
        for d in getattr(self, "_cleanup_dirs", []):
            shutil.rmtree(d, ignore_errors=True)
        self._cleanup_dirs = []

    def test_full_report_passes(self):
        content = """---
task_id: test-task
status: complete
---

# Completed Task: Test

Task Card: `docs/agentic/tasks/test-task.md`

## What Changed

- Added `foo.cpp`
Commit: `abc1234`

## Evidence

- validate-docs: passed
- CTest: 10 tests, 0 failures

## Decisions

- Accept the change.

## Residual Risks

- None.
"""
        report = self._write_temp_report(content)
        result = check_completion_evidence(report)
        self.assertTrue(result["passed"], f"Expected PASS, got: {result['details']}")
        self.assertFalse(result["skipped"])
        self.assertTrue(result["categories"]["task_card_link"])
        self.assertTrue(result["categories"]["changed_files"])
        self.assertTrue(result["categories"]["evidence_artifacts"])
        self.assertTrue(result["categories"]["gate_decision"])

    def test_evidence_free_report_fails(self):
        content = """---
task_id: test-task
status: complete
---

# Completed Task: Test

Task Card: `docs/agentic/tasks/test-task.md`

The task was completed successfully. All work is done.
"""
        report = self._write_temp_report(content)
        result = check_completion_evidence(report)
        self.assertFalse(result["passed"])
        self.assertFalse(result["skipped"])
        # Should have task card link but not files/evidence/decision
        self.assertTrue(result["categories"]["task_card_link"])
        # At least two other categories should be missing
        missing = sum(1 for v in result["categories"].values() if not v)
        self.assertGreaterEqual(missing, 2)

    def test_minimal_but_complete_passes(self):
        content = """# Minimal Task

Task: `docs/agentic/tasks/minimal.md`
Changed: `src/foo.cpp` (commit `def5678`)
Evidence: `validate-docs` passed; `CTest` 0 failures.
Decision: accepted; residual risk is low.
"""
        report = self._write_temp_report(content)
        result = check_completion_evidence(report)
        self.assertTrue(result["passed"], f"Expected PASS, got: {result['details']}")

    def test_not_a_completed_task_skips(self):
        content = """# Just a regular markdown file

Nothing to see here.
"""
        # File path doesn't contain 'completed-tasks'
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = f.name

        try:
            result = check_completion_evidence(tmp_path)
            self.assertTrue(result["skipped"])
            self.assertFalse(result["passed"])
        finally:
            os.unlink(tmp_path)

    def test_missing_file_skips(self):
        result = check_completion_evidence("/nonexistent/path/README.md")
        self.assertTrue(result["skipped"])

    def test_too_short_report_skips(self):
        content = "Too short."
        report = self._write_temp_report(content)
        result = check_completion_evidence(report)
        self.assertTrue(result["skipped"])


if __name__ == "__main__":
    unittest.main()
