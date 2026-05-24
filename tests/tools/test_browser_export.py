import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BROWSER_EXPORT_PATH = REPO_ROOT / "tools" / "architecture_visualization" / "browser_export.py"


def load_browser_export_module():
    sys.path.insert(0, str(BROWSER_EXPORT_PATH.parent))
    spec = importlib.util.spec_from_file_location("browser_export_under_test", BROWSER_EXPORT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BrowserExportTests(unittest.TestCase):
    def test_reuse_existing_artifacts_records_declared_outputs(self):
        module = load_browser_export_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            png = temp_root / "figure.png"
            pdf = temp_root / "figure.pdf"
            png.write_bytes(b"png-bytes")
            pdf.write_bytes(b"pdf-bytes")

            artifacts, unsupported = module.reuse_existing_artifacts(
                {"png": png, "pdf": pdf},
                ["png", "pdf", "svg"],
            )

        self.assertEqual(["png", "pdf"], [item["format"] for item in artifacts])
        self.assertTrue(all(item["exists"] for item in artifacts))
        self.assertEqual(["svg"], [item["format"] for item in unsupported])

    def test_existing_artifact_manifest_can_export_without_browser(self):
        module = load_browser_export_module()
        artifacts = [
            {
                "format": "png",
                "path": "docs/architecture/70-visualization/assets/example.png",
                "exists": True,
                "bytes": 10,
                "exit_code": 0,
                "diagnostic": "reused existing artifact",
            }
        ]
        manifest = module.build_manifest(
            REPO_ROOT / "tools" / "architecture_visualization" / "specs" / "figure71.yaml",
            {"id": "figure71", "schema_version": "gcs.execution_map.v1"},
            REPO_ROOT / "docs" / "architecture" / "70-visualization" / "assets" / "figure71.html",
            ["png"],
            None,
            artifacts,
            [],
            [{"token": "--gcs-surface-paper", "passed": True}],
            False,
            "existing-artifacts",
        )

        self.assertEqual("exported", manifest["status"])
        self.assertEqual("existing-artifacts", manifest["browser"]["backend"])
        self.assertTrue(manifest["html_tokens_passed"])


if __name__ == "__main__":
    unittest.main()
