import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCREENSHOT_BASELINE_PATH = REPO_ROOT / "tools" / "ui_qa" / "gcs_screenshot_baseline.py"


def load_screenshot_baseline_module():
    spec = importlib.util.spec_from_file_location("gcs_screenshot_baseline_under_test", SCREENSHOT_BASELINE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def tiny_png(width: int = 8, height: int = 6) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I4sIIBBBBB", 13, b"IHDR", width, height, 8, 2, 0, 0, 0)
        + b"\x00\x00\x00\x00"
        + struct.pack(">I4s", 0, b"IEND")
        + b"\x00\x00\x00\x00"
    )


def write_manifest(root: Path, entry: dict[str, object]) -> Path:
    path = root / "screenshot-baselines.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "gcs.screenshot_baselines.v1",
                "baselines": [entry],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


class GcsScreenshotBaselineTests(unittest.TestCase):
    def test_current_manifest_passes(self):
        module = load_screenshot_baseline_module()
        result = module.run_checks()

        self.assertEqual([], result.errors)
        self.assertGreaterEqual(result.baselines_checked, 1)

    def test_missing_png_fixture_fails(self):
        module = load_screenshot_baseline_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = write_manifest(root, {
                "id": "missing",
                "path": "missing.png",
                "width": 8,
                "height": 6,
                "bytes": 1,
                "sha256": "0" * 64,
            })
            result = module.run_checks(manifest_path=manifest, repo_root=root)

        self.assertTrue(any("missing PNG artifact" in error for error in result.errors))

    def test_dimension_mismatch_fixture_fails(self):
        module = load_screenshot_baseline_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "artifact.png"
            data = tiny_png(width=8, height=6)
            artifact.write_bytes(data)
            manifest = write_manifest(root, {
                "id": "wrong-dimensions",
                "path": "artifact.png",
                "width": 9,
                "height": 6,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
            result = module.run_checks(manifest_path=manifest, repo_root=root)

        self.assertTrue(any("width is 8, expected 9" in error for error in result.errors))

    def test_hash_mismatch_fixture_fails(self):
        module = load_screenshot_baseline_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "artifact.png"
            data = tiny_png()
            artifact.write_bytes(data)
            manifest = write_manifest(root, {
                "id": "wrong-hash",
                "path": "artifact.png",
                "width": 8,
                "height": 6,
                "bytes": len(data),
                "sha256": "f" * 64,
            })
            result = module.run_checks(manifest_path=manifest, repo_root=root)

        self.assertTrue(any("sha256 changed" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
