import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSITOR_PATH = REPO_ROOT / "tools" / "architecture_visualization" / "showcase_scene_html_compositor.py"


def load_compositor():
    spec = importlib.util.spec_from_file_location("showcase_scene_html_compositor_under_test", COMPOSITOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ShowcaseSceneHtmlCompositorTests(unittest.TestCase):
    def test_rendered_html_names_required_showcase_evidence(self):
        compositor = load_compositor()
        html = compositor.render_html(compositor.load_context())

        self.assertIn("GCS Integrated Showcase Evidence", html)
        self.assertIn("gluing.accepted", html)
        self.assertIn("kernel.solve_intent_missing_fixed_entity", html)
        self.assertIn("ViewerBridgeContract.ShowcaseFixtureProjectsBoundaryRankAndResidualEvidence", html)
        self.assertIn("data-gcs-box-label=\"figure72-scene_contract\"", html)
        self.assertIn("data-gcs-contrast-label=\"numeric_evidence-title\"", html)
        self.assertIn("data-gcs-text-label=\"figure72-subtitle\"", html)
        self.assertNotIn("position: absolute", html)

    def test_rendered_html_is_deterministic(self):
        compositor = load_compositor()
        context = compositor.load_context()

        self.assertEqual(compositor.render_html(context), compositor.render_html(context))

    def test_main_writes_and_checks_html(self):
        compositor = load_compositor()
        with tempfile.TemporaryDirectory() as tmp:
            out_html = Path(tmp) / "showcase.html"

            write_exit = compositor.main(["--out-html", str(out_html)])
            check_exit = compositor.main(["--out-html", str(out_html), "--check"])

            self.assertEqual(write_exit, 0)
            self.assertEqual(check_exit, 0)
            self.assertTrue(out_html.exists())


if __name__ == "__main__":
    unittest.main()
