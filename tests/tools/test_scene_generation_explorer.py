import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_PATH = REPO_ROOT / "tools" / "scene_generation" / "tools.py"


def load_tools(store_dir: Path):
    spec = importlib.util.spec_from_file_location("scene_generation_tools_under_test", TOOLS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.STORE_DIR = str(store_dir)
    return module


def small_request():
    return {
        "exploration_id": "unit_explorer_v1",
        "seed": 4242,
        "budget": {"max_candidates": 12, "max_accepts": 3},
        "topology_policy": {
            "vertex_counts": [4, 5],
            "methods": ["cycle_plus_chords"],
            "extra_edge_range": [0, 1],
        },
        "coverage_goals": [
            "mixed_rigid_sets",
            "biconnected_geometry_primal",
            "invalid_signature_negative_case",
            "same_rigid_set_negative_case",
        ],
        "gate_profile": "local_only",
    }


class SceneGenerationExplorerTests(unittest.TestCase):
    def test_explorer_is_deterministic_and_keeps_negative_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tools = load_tools(Path(tmp))

            first = tools.tool_explore_scene_space(small_request())
            second = tools.tool_explore_scene_space(small_request())

            self.assertEqual(first, second)
            self.assertEqual(first["status"], "accepted_with_rejections")
            self.assertGreaterEqual(first["summary"]["accepted"], 1)
            self.assertIn("invalid_signature_negative_case", first["coverage"]["satisfied_goals"])
            self.assertIn("same_rigid_set_negative_case", first["coverage"]["satisfied_goals"])
            rejection_reasons = first["coverage"]["histograms"]["rejection_reasons"]
            self.assertEqual(rejection_reasons["invalid_constraint_signature"], 1)
            self.assertEqual(rejection_reasons["constraint_same_rigid_set"], 1)

    def test_promotion_package_blocks_unsupported_public_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tools = load_tools(Path(tmp))

            result = tools.tool_explore_scene_space(small_request())
            candidate_id = result["accepted_candidates"][0]["candidate_id"]

            blocked = tools.tool_promote_candidate(
                {
                    "exploration_id": "unit_explorer_v1",
                    "candidate_id": candidate_id,
                }
            )
            self.assertEqual(blocked["status"], "promotion_blocked")
            self.assertEqual(blocked["reason_code"], "promotion_gate_unsupported")
            self.assertIn("scene_io_round_trip", blocked["known_unsupported_gates"])

            local = tools.tool_promote_candidate(
                {
                    "exploration_id": "unit_explorer_v1",
                    "candidate_id": candidate_id,
                    "promotion_id": "unit_explorer_v1_local_promotion",
                    "gate_profile": "local_only",
                }
            )
            self.assertEqual(local["status"], "promotion_package_written")
            package = Path(tmp) / "promotions" / "unit_explorer_v1_local_promotion" / "package.json"
            self.assertTrue(package.exists())


if __name__ == "__main__":
    unittest.main()
