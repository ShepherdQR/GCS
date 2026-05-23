import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_PATH = REPO_ROOT / "tools" / "scene_generation" / "tools.py"
PACKAGE_ROOT = REPO_ROOT / "tools" / "scene_generation"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from gcs_scene_generation import contracts, gcs_model, projection, promotion, storage, topology, validation


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
    def test_package_contract_modules_are_structured_boundaries(self):
        self.assertTrue(contracts.is_valid_constraint_signature("Distance", "Point", "Plane"))
        self.assertFalse(contracts.is_valid_constraint_signature("Parallel", "Point", "Plane"))
        with self.assertRaises(ValueError):
            storage.safe_store_id("../escape", "candidate_id")

        scene = promotion.solver_scene_from_gcs(
            {
                "rigid_sets": [{"id": 1}],
                "geometries": [
                    {"id": 10, "type": "Point", "rigid_set_id": 1, "v": [1, 2]},
                    {"id": 20, "type": "Plane", "rigid_set_id": 1, "v": [0, 0, 1, 0, 0, 0]},
                ],
                "constraints": [
                    {"id": 100, "type": "Distance", "geometry_ids": [10, 20], "value": 3.5},
                ],
            }
        )

        self.assertEqual(scene["format_version"], "gcs-0.3")
        self.assertEqual(scene["geometries"][0]["type"], contracts.GEOMETRY_TYPE_MAP["Point"])
        self.assertEqual(len(scene["geometries"][0]["v"]), 6)
        self.assertEqual(scene["constraints"][0]["type"], contracts.CONSTRAINT_TYPE_MAP["Distance"])
        self.assertTrue(promotion.canonical_public_scene_text(scene).endswith("\n"))
        self.assertEqual(topology.unique_edges([[2, 1], [1, 2], [2, 2]]), [[1, 2]])
        gcs_model.rebuild_rigid_sets({"geometries": [], "rigid_sets": []}, 0)

    def test_validation_and_projection_modules_report_structured_contracts(self):
        gcs = {
            "rigid_sets": [{"id": 0, "geometry_ids": [1]}, {"id": 1, "geometry_ids": [2]}],
            "geometries": [
                {"id": 1, "type": "Point", "rigid_set_id": 0, "v": [0, 0, 0, 0, 0, 0]},
                {"id": 2, "type": "Plane", "rigid_set_id": 1, "v": [0, 0, 0, 0, 0, 1]},
            ],
            "constraints": [{"id": 7, "type": "Parallel", "geometry_ids": [1, 2], "value": 0.0}],
        }

        report = validation.validate_gcs_schema(gcs)
        self.assertFalse(report["valid"])
        self.assertEqual(report["violations"][0]["type"], "invalid_constraint_signature")

        incidence = projection.project_gcs_graph("invalid_gcs", gcs, "incidence_bipartite", "invalid_incidence")
        self.assertEqual(incidence["vertices"], ["G1", "G2", "C7"])
        self.assertEqual(incidence["edges"], [["G1", "C7"], ["G2", "C7"]])
        self.assertEqual(
            projection.project_gcs_graph("invalid_gcs", gcs, "unknown", "bad_projection")["error"],
            "Unknown projection: unknown",
        )

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

    def test_manual_generation_path_survives_package_split(self):
        with tempfile.TemporaryDirectory() as tmp:
            tools = load_tools(Path(tmp))

            skeleton = tools.tool_generate_skeleton_graph(
                {
                    "graph_id": "manual_skeleton",
                    "num_vertices": 5,
                    "method": "cycle_plus_chords",
                    "extra_edges": 1,
                    "seed": 11,
                }
            )
            lift = tools.tool_lift_skeleton_to_gcs(
                {
                    "skeleton_graph_id": skeleton["graph_id"],
                    "gcs_graph_id": "manual_gcs",
                    "seed": 12,
                }
            )
            assigned = tools.tool_assign_geometry_parameters({"gcs_graph_id": lift["gcs_graph_id"], "seed": 13})
            validation = tools.tool_validate_gcs_schema({"gcs_graph_id": assigned["gcs_graph_id"]})
            projection = tools.tool_project_gcs_graph(
                {
                    "gcs_graph_id": assigned["gcs_graph_id"],
                    "projected_graph_id": "manual_geometry_primal",
                }
            )
            biconnectivity = tools.tool_check_vertex_biconnected({"projected_graph_id": projection["projected_graph_id"]})

            self.assertEqual(assigned["status"], "parameters_assigned")
            self.assertTrue(validation["valid"])
            self.assertTrue(biconnectivity["is_vertex_biconnected"])

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
