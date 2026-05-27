"""Tests for E-GOV-001 check_staged_scope validator."""

import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

# Import the module under test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tools.governance.check_staged_scope import (
    _is_in_scope,
    _read_task_affected_paths,
    check_staged_scope,
)


class ScopeMatchingTests(unittest.TestCase):
    """Tests for _is_in_scope path matching."""

    def test_exact_file_match(self):
        self.assertTrue(_is_in_scope("docs/product/foo.md", ["docs/product/"]))

    def test_subdirectory_match(self):
        self.assertTrue(
            _is_in_scope("docs/product/demos/d1/README.md", ["docs/product/"])
        )

    def test_no_match(self):
        self.assertFalse(_is_in_scope("src/gcs/kernel/kernel.cpp", ["docs/product/"]))

    def test_empty_scope(self):
        self.assertFalse(_is_in_scope("docs/product/foo.md", []))

    def test_multiple_scope_paths(self):
        scope = ["docs/product/", "src/gcs/kernel/"]
        self.assertTrue(_is_in_scope("docs/product/foo.md", scope))
        self.assertTrue(_is_in_scope("src/gcs/kernel/kernel.cpp", scope))
        self.assertFalse(_is_in_scope("tools/scene_generation/foo.py", scope))

    def test_exact_scope_match_no_trailing_slash(self):
        self.assertTrue(
            _is_in_scope("CLAUDE.md", ["CLAUDE.md"])
        )

    def test_windows_backslash_normalization(self):
        self.assertTrue(
            _is_in_scope("docs\\product\\foo.md", ["docs/product/"])
        )


class TaskCardParsingTests(unittest.TestCase):
    """Tests for _read_task_affected_paths."""

    def test_bullet_list_under_heading(self):
        content = """# Task Card

## Affected Paths

- `docs/product/`
- `src/gcs/kernel/`

## Description

Some work.
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = f.name

        try:
            paths = _read_task_affected_paths(tmp_path)
            self.assertIn("docs/product/", paths)
            self.assertIn("src/gcs/kernel/", paths)
        finally:
            os.unlink(tmp_path)

    def test_no_affected_paths_heading(self):
        content = """# Task Card

## Description

No affected paths section here.
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = f.name

        try:
            paths = _read_task_affected_paths(tmp_path)
            self.assertEqual(paths, [])
        finally:
            os.unlink(tmp_path)

    def test_missing_file(self):
        paths = _read_task_affected_paths("/nonexistent/path/task.md")
        self.assertEqual(paths, [])

    def test_backtick_paths_fallback(self):
        content = """# Task

## Affected Paths

- `docs/product/`
- `src/gcs/`
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = f.name

        try:
            paths = _read_task_affected_paths(tmp_path)
            # Should find backtick-quoted paths under the heading
            self.assertIn("docs/product/", paths)
            self.assertIn("src/gcs/", paths)
        finally:
            os.unlink(tmp_path)


class CheckStagedScopeIntegrationTests(unittest.TestCase):
    """Integration tests that mock git calls."""

    @patch("tools.governance.check_staged_scope._repo_root")
    @patch("tools.governance.check_staged_scope._staged_files")
    def test_all_in_scope_passes(self, mock_staged, mock_root):
        mock_root.return_value = "/fake/repo"
        mock_staged.return_value = [
            "docs/product/new-demo.md",
            "docs/product/gcs-demo-ladder.md",
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("""# Task

## Affected Paths

- `docs/product/`

""")
            tmp_path = f.name

        try:
            result = check_staged_scope(tmp_path)
            self.assertTrue(result["passed"])
            self.assertEqual(len(result["out_of_scope"]), 0)
            self.assertEqual(len(result["in_scope"]), 2)
        finally:
            os.unlink(tmp_path)

    @patch("tools.governance.check_staged_scope._repo_root")
    @patch("tools.governance.check_staged_scope._staged_files")
    def test_out_of_scope_fails(self, mock_staged, mock_root):
        mock_root.return_value = "/fake/repo"
        mock_staged.return_value = [
            "docs/product/new-demo.md",
            "docs/research/OpusTime/OpusTime.md",
            "docs/reports/report_/something.md",
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("""# Task

## Affected Paths

- `docs/product/`

""")
            tmp_path = f.name

        try:
            result = check_staged_scope(tmp_path)
            self.assertFalse(result["passed"])
            self.assertEqual(len(result["out_of_scope"]), 2)
            self.assertEqual(len(result["in_scope"]), 1)
        finally:
            os.unlink(tmp_path)

    @patch("tools.governance.check_staged_scope._repo_root")
    @patch("tools.governance.check_staged_scope._staged_files")
    def test_allowlist_adds_scope(self, mock_staged, mock_root):
        mock_root.return_value = "/fake/repo"
        mock_staged.return_value = [
            "docs/product/new-demo.md",
            "CLAUDE.md",
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("""# Task

## Affected Paths

- `docs/product/`

""")
            tmp_path = f.name

        try:
            result = check_staged_scope(tmp_path, allowlist=["CLAUDE.md"])
            self.assertTrue(result["passed"])
            self.assertEqual(len(result["out_of_scope"]), 0)
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
