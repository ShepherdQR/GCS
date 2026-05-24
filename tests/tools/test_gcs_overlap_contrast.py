import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OVERLAP_CONTRAST_PATH = REPO_ROOT / "tools" / "ui_qa" / "gcs_overlap_contrast.py"


def load_overlap_contrast_module():
    spec = importlib.util.spec_from_file_location("gcs_overlap_contrast_under_test", OVERLAP_CONTRAST_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GcsOverlapContrastTests(unittest.TestCase):
    def test_figure71_overlap_contrast_passes(self):
        module = load_overlap_contrast_module()
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
        self.assertGreaterEqual(result.boxes_checked, 6)
        self.assertGreater(result.contrast_checked, 10)

    def test_forced_overlap_fixture_fails(self):
        module = load_overlap_contrast_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "overlap.html"
            path.write_text(
                '<section data-gcs-box-label="a" data-gcs-box-group="g" data-gcs-box="0,0,10,10"></section>'
                '<section data-gcs-box-label="b" data-gcs-box-group="g" data-gcs-box="5,5,10,10"></section>'
                '<p data-gcs-contrast-label="ok" data-gcs-contrast-fg="#181715" '
                'data-gcs-contrast-bg="#f7f4ec">ok</p>',
                encoding="utf-8",
            )
            result = module.run_checks(paths=[path], repo_root=REPO_ROOT)

        self.assertTrue(any("layout boxes overlap" in error for error in result.errors))

    def test_forced_low_contrast_fixture_fails(self):
        module = load_overlap_contrast_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "contrast.html"
            path.write_text(
                '<section data-gcs-box-label="a" data-gcs-box-group="g" data-gcs-box="0,0,1,1"></section>'
                '<p data-gcs-contrast-label="bad" data-gcs-contrast-fg="#777777" '
                'data-gcs-contrast-bg="#777777">bad</p>',
                encoding="utf-8",
            )
            result = module.run_checks(paths=[path], repo_root=REPO_ROOT)

        self.assertTrue(any("bad contrast" in error for error in result.errors))

    def test_missing_markers_fixture_fails(self):
        module = load_overlap_contrast_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "missing.html"
            path.write_text("<p>No markers</p>", encoding="utf-8")
            result = module.run_checks(paths=[path], repo_root=REPO_ROOT)

        self.assertTrue(any("no data-gcs-box markers found" in error for error in result.errors))
        self.assertTrue(any("no data-gcs-contrast markers found" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
