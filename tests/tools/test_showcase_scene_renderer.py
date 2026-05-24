import importlib.util
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDERER_PATH = REPO_ROOT / "tools" / "architecture_visualization" / "render_showcase_scene.py"


def load_renderer():
    spec = importlib.util.spec_from_file_location("showcase_scene_renderer_under_test", RENDERER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ShowcaseSceneRendererTests(unittest.TestCase):
    def test_loads_public_scene_and_negative_metadata(self):
        renderer = load_renderer()

        model = renderer.load_showcase_model()

        self.assertEqual([entity.id for entity in model.entities], [0, 1, 2, 3, 4, 5])
        self.assertEqual([constraint.id for constraint in model.constraints], [0, 1, 2, 3])
        self.assertEqual(model.fixed_geometry_ids, (0,))
        self.assertEqual(model.components, ((0, 1, 2), (3, 4, 5)))
        self.assertEqual(
            model.negative_metadata["expected_public_evidence"]["report_code"],
            "kernel.solve_intent_missing_fixed_entity",
        )

    def test_svg_is_valid_and_names_public_evidence(self):
        renderer = load_renderer()
        model = renderer.load_showcase_model()

        svg = renderer.render_svg(model)

        ET.fromstring(svg)
        self.assertEqual(svg, renderer.render_svg(model))
        self.assertIn("entity-0", svg)
        self.assertIn("constraint-3", svg)
        self.assertIn("fixed", svg)
        self.assertIn("kernel.solve_intent_missing_fixed_entity", svg)
        self.assertIn("fixtures/scene/showcase/integrated_feature_showcase.gcs.json", svg)

    def test_main_writes_svg_and_report(self):
        renderer = load_renderer()
        with tempfile.TemporaryDirectory() as tmp:
            out_svg = Path(tmp) / "showcase.svg"
            out_report = Path(tmp) / "showcase.md"

            exit_code = renderer.main([
                "--out-svg",
                str(out_svg),
                "--out-report",
                str(out_report),
            ])

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_svg.exists())
            self.assertTrue(out_report.exists())
            ET.parse(out_svg)
            self.assertIn("Integrated Showcase Scene Report", out_report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
