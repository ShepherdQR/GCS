import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TOKEN_LINT_PATH = REPO_ROOT / "tools" / "ui_qa" / "gcs_token_lint.py"


def load_token_lint_module():
    spec = importlib.util.spec_from_file_location("gcs_token_lint_under_test", TOKEN_LINT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GcsTokenLintTests(unittest.TestCase):
    def test_repo_token_lint_passes(self):
        module = load_token_lint_module()
        result = module.run_checks(repo_root=REPO_ROOT)
        self.assertEqual([], result.errors)

    def test_forced_raw_hex_fixture_fails(self):
        module = load_token_lint_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad_renderer.py"
            path.write_text('BAD_COLOR = "#123456"\n', encoding="utf-8")
            result = module.run_checks(paths=[path], allowed_raw_hex_sources=[], repo_root=REPO_ROOT)

        self.assertTrue(any("raw hex #123456" in error for error in result.errors))

    def test_unknown_gcs_token_fixture_fails(self):
        module = load_token_lint_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad_token.py"
            path.write_text('VALUE = GCS_TOKENS["surface.imaginary"]\n', encoding="utf-8")
            result = module.run_checks(paths=[path], allowed_raw_hex_sources=[], repo_root=REPO_ROOT)

        self.assertTrue(any("unknown GCS_TOKENS token 'surface.imaginary'" in error for error in result.errors))

    def test_unknown_spec_canonical_token_fixture_fails(self):
        module = load_token_lint_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad_spec.yaml"
            path.write_text('canonical_token: "evidence.imaginary"\n', encoding="utf-8")
            result = module.run_checks(paths=[path], allowed_raw_hex_sources=[], repo_root=REPO_ROOT)

        self.assertTrue(any("unknown canonical_token 'evidence.imaginary'" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
