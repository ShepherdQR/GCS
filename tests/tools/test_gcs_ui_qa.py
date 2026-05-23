import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
UI_QA_PATH = REPO_ROOT / "tools" / "ui_qa" / "gcs_ui_qa.py"


def load_ui_qa_module():
    spec = importlib.util.spec_from_file_location("gcs_ui_qa_under_test", UI_QA_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GcsUiQaTests(unittest.TestCase):
    def test_ui_qa_contract_passes(self):
        module = load_ui_qa_module()
        result = module.run_checks(REPO_ROOT)
        self.assertEqual([], result.errors)

    def test_fixture_covers_viewer_semantics(self):
        module = load_ui_qa_module()
        fixture = REPO_ROOT / "fixtures" / "scene" / "ui_qa" / "mixed_geometry_constraints.json"
        data = module.json.loads(fixture.read_text(encoding="utf-8"))
        self.assertTrue({0, 1, 2}.issubset({int(item["type"]) for item in data["geometries"]}))
        self.assertTrue(set(range(5)).issubset({int(item["type"]) for item in data["constraints"]}))


if __name__ == "__main__":
    unittest.main()
