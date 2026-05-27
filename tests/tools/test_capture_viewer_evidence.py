import importlib.util
import json
import struct
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_PATH = REPO_ROOT / "tools" / "ui_qa" / "capture_viewer_evidence.py"
CAPTURE_MANIFEST = (
    REPO_ROOT
    / "docs"
    / "architecture"
    / "70-visualization"
    / "assets"
    / "ve002-d5-viewer-evidence-workbench.capture.json"
)
CAPTURE_PNG = (
    REPO_ROOT
    / "docs"
    / "architecture"
    / "70-visualization"
    / "assets"
    / "ve002-d5-viewer-evidence-workbench.review.png"
)


def load_capture_module():
    spec = importlib.util.spec_from_file_location("capture_viewer_evidence_under_test", CAPTURE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    return struct.unpack(">II", data[16:24])


class CaptureViewerEvidenceTests(unittest.TestCase):
    def test_scenario_definitions_cover_phase_10_targets(self):
        module = load_capture_module()
        scenarios = module.scenario_definitions()
        scenario_ids = {scenario["id"] for scenario in scenarios}

        self.assertEqual(
            {
                "empty_model",
                "triangle_003_graph_focus",
                "mixed_constraints_replay",
                "d5_showcase_narrow_diagnostics",
            },
            scenario_ids,
        )
        self.assertTrue(any("narrow" in scenario["phase_10_target"] for scenario in scenarios))

    def test_committed_capture_manifest_matches_review_png(self):
        self.assertTrue(CAPTURE_MANIFEST.is_file())
        self.assertTrue(CAPTURE_PNG.is_file())

        manifest = json.loads(CAPTURE_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual("gcs.viewer_visual_evidence.v1", manifest["schema_version"])
        self.assertEqual("VE-002", manifest["evidence_id"])
        self.assertEqual(
            "docs/architecture/70-visualization/assets/ve002-d5-viewer-evidence-workbench.review.png",
            manifest["artifact"]["path"],
        )
        self.assertGreater(manifest["artifact"]["bytes"], 300000)
        self.assertEqual((1600, 1320), png_size(CAPTURE_PNG))

    def test_capture_scope_keeps_narrative_map_unchanged(self):
        manifest = json.loads(CAPTURE_MANIFEST.read_text(encoding="utf-8"))
        self.assertFalse(manifest["scope"]["narrative_map_updated"])
        self.assertIn("TkAgg Matplotlib canvas", manifest["scope"]["capture_surface"])


if __name__ == "__main__":
    unittest.main()
