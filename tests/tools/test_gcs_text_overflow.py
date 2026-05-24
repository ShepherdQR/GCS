import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TEXT_OVERFLOW_PATH = REPO_ROOT / "tools" / "ui_qa" / "gcs_text_overflow.py"


def load_text_overflow_module():
    spec = importlib.util.spec_from_file_location("gcs_text_overflow_under_test", TEXT_OVERFLOW_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GcsTextOverflowTests(unittest.TestCase):
    def test_figure71_text_budgets_pass(self):
        module = load_text_overflow_module()
        html = (
            REPO_ROOT
            / "docs"
            / "architecture"
            / "70-visualization"
            / "assets"
            / "figure71-gcs-step-1-40-evidence-map.html"
        )
        result = module.run_checks(paths=[html], repo_root=REPO_ROOT)
        self.assertEqual([], result.errors)
        self.assertGreater(result.budgets_checked, 20)

    def test_forced_overflow_fixture_fails(self):
        module = load_text_overflow_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "overflow.html"
            path.write_text(
                '<p data-gcs-text-label="bad" data-gcs-text-budget="8">'
                "This text is far too long"
                "</p>",
                encoding="utf-8",
            )
            result = module.run_checks(paths=[path], repo_root=REPO_ROOT)

        self.assertTrue(any("bad text length" in error for error in result.errors))

    def test_missing_budget_fixture_fails(self):
        module = load_text_overflow_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "missing.html"
            path.write_text("<p>No budget marker</p>", encoding="utf-8")
            result = module.run_checks(paths=[path], repo_root=REPO_ROOT)

        self.assertTrue(any("no data-gcs-text-budget markers found" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
