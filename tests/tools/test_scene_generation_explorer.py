import importlib.util
import json
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


def write_fake_solver(path: Path, exit_code: int = 0):
    path.write_text(
        "\n".join(
            [
                "import sys",
                "from pathlib import Path",
                "scene = Path(sys.argv[1])",
                "print('GCS C++23 canonical kernel solver skeleton')",
                "print(f'Input: {scene}')",
                "print('Status: Solved')",
                "print('Accepted: true')",
                "print('  session_runtime.pre_solve_diagnostics: Ok')",
                "print('  diagnostics.glue_local_sections: Ok')",
                "print('  runtime.commit: Runtime committed the verified proposed state.')",
                f"raise SystemExit({exit_code})",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def gate_by_id(package: dict, gate_id: str) -> dict:
    for gate in package["gate_reports"]:
        if gate["gate_id"] == gate_id:
            return gate
    raise AssertionError(f"missing gate {gate_id}")


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

    def test_promotion_package_blocks_when_solver_command_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tools = load_tools(Path(tmp))

            result = tools.tool_explore_scene_space(small_request())
            candidate_id = result["accepted_candidates"][0]["candidate_id"]

            blocked = tools.tool_promote_candidate(
                {
                    "exploration_id": "unit_explorer_v1",
                    "candidate_id": candidate_id,
                    "public_gate_config": {"solver_command": [str(Path(tmp) / "missing_solver.py")]},
                }
            )
            self.assertEqual(blocked["status"], "promotion_blocked")
            self.assertEqual(blocked["reason_code"], "runtime_smoke_failed")
            self.assertIn("runtime_smoke", blocked["known_unsupported_gates"])

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

    def test_promotion_package_uses_public_gate_adapters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tools = load_tools(root)
            fake_solver = root / "fake_solver.py"
            write_fake_solver(fake_solver)

            request = small_request()
            request["coverage_goals"] = ["mixed_rigid_sets", "biconnected_geometry_primal"]
            request["public_gate_config"] = {
                "solver_command": [sys.executable, str(fake_solver)],
            }
            result = tools.tool_explore_scene_space(request)
            candidate_id = result["accepted_candidates"][0]["candidate_id"]

            promoted = tools.tool_promote_candidate(
                {
                    "exploration_id": "unit_explorer_v1",
                    "candidate_id": candidate_id,
                    "promotion_id": "unit_explorer_v1_public_promotion",
                    "public_gate_config": {
                        "solver_command": [sys.executable, str(fake_solver)],
                    },
                }
            )

            self.assertEqual(promoted["status"], "promotion_package_written")
            self.assertEqual(promoted["known_unsupported_gates"], [])

            package_path = root / "promotions" / "unit_explorer_v1_public_promotion" / "package.json"
            public_scene_path = root / "promotions" / "unit_explorer_v1_public_promotion" / "public_scene.gcs.json"
            package = json.loads(package_path.read_text(encoding="utf-8"))
            public_scene = json.loads(public_scene_path.read_text(encoding="utf-8"))

            for gate_id in [
                "scene_io_round_trip",
                "kernel_validation",
                "viewer_projection",
                "runtime_smoke",
                "diagnostics_evidence",
            ]:
                self.assertEqual(gate_by_id(package, gate_id)["status"], "passed")
            self.assertEqual(public_scene["format_version"], "gcs-0.3")
            self.assertIn("public_scene_digest", package["canonical_serialization"])


if __name__ == "__main__":
    unittest.main()
