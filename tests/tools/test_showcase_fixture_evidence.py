import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = REPO_ROOT / "tools" / "architecture_visualization" / "showcase_fixture_evidence.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("showcase_fixture_evidence_under_test", CHECKER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def copy_showcase_tree(root: Path) -> Path:
    source = REPO_ROOT / "fixtures" / "scene" / "showcase"
    target = root / "fixtures" / "scene" / "showcase"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    brief = root / "docs" / "architecture" / "88-p6-1-integrated-showcase-brief.md"
    brief.parent.mkdir(parents=True, exist_ok=True)
    brief.write_text("# Brief\n", encoding="utf-8")
    return target


def mutate_json(path: Path, mutator) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutator(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class ShowcaseFixtureEvidenceTests(unittest.TestCase):
    def test_current_showcase_fixture_evidence_passes(self):
        checker = load_checker()
        result = checker.run_checks()

        self.assertEqual([], result.errors)
        self.assertEqual(result.fixtures_checked, 2)

    def test_missing_required_panel_fails(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            showcase = copy_showcase_tree(root)
            metadata = showcase / "integrated_feature_showcase.metadata.json"

            def remove_panel(data):
                data["showcase_brief"]["required_panels"].remove("negative_variant")

            mutate_json(metadata, remove_panel)
            result = checker.run_checks(
                manifest_path=showcase / "manifest.json",
                repo_root=root,
            )

        self.assertTrue(any("missing required showcase panel 'negative_variant'" in error for error in result.errors))

    def test_rank_mismatch_fails(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            showcase = copy_showcase_tree(root)
            metadata = showcase / "integrated_feature_showcase.metadata.json"

            def change_rank(data):
                data["expected_solver_evidence"]["local_numeric_reports"][0]["rank"] = 7

            mutate_json(metadata, change_rank)
            result = checker.run_checks(
                manifest_path=showcase / "manifest.json",
                repo_root=root,
            )

        self.assertTrue(any("local_numeric_reports[0].rank must be 2" in error for error in result.errors))

    def test_negative_report_code_mismatch_fails(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            showcase = copy_showcase_tree(root)
            metadata = showcase / "integrated_feature_showcase_missing_fixed.metadata.json"

            def change_report_code(data):
                data["expected_public_evidence"]["report_code"] = "kernel.other"

            mutate_json(metadata, change_report_code)
            result = checker.run_checks(
                manifest_path=showcase / "manifest.json",
                repo_root=root,
            )

        self.assertTrue(any("report_code must be kernel.solve_intent_missing_fixed_entity" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
