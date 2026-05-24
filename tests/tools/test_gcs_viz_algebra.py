import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = REPO_ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from gcs_viz.algebra import (  # noqa: E402
    BehaviorModel,
    ConstraintType,
    GCSGraph,
    GeometryType,
    SolveMode,
    read_graph_json,
    write_graph_json,
)


class GcsVizAlgebraTests(unittest.TestCase):
    def make_behavior_graph(self) -> GCSGraph:
        graph = GCSGraph()
        graph.add_rigid_set(0)
        graph.add_rigid_set(1)
        graph.add_geometry(GeometryType.Point, 0, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], geom_id=0)
        graph.add_geometry(GeometryType.Point, 1, [1.0, 0.0, 0.0, 0.0, 0.0, 0.0], geom_id=1)
        graph.add_constraint(ConstraintType.Distance, [0, 1], value=1.0, cid=0)
        graph.behavior = BehaviorModel(
            mode=SolveMode.Drag,
            fixed_geometry_ids=[0],
            driven_geometry_ids=[1],
            target_constraint_ids=[0],
        )
        graph.history.append({"action": "Solve", "payload": {}})
        return graph

    def test_current_json_schema_names_behavior_intent(self):
        graph = self.make_behavior_graph()

        payload = graph.to_dict()

        self.assertEqual(payload["format_version"], "gcs-0.3")
        self.assertEqual(payload["state_version"], 0)
        self.assertEqual(payload["behavior"]["mode"], int(SolveMode.Drag))
        self.assertEqual(payload["behavior"]["fixed_geometry_ids"], [0])
        self.assertEqual(payload["behavior"]["driven_geometry_ids"], [1])
        self.assertEqual(payload["behavior"]["target_constraint_ids"], [0])

    def test_json_read_write_preserves_behavior_and_history(self):
        graph = self.make_behavior_graph()

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "python_behavior_roundtrip.gcs.json"
            write_graph_json(graph, str(path))
            raw = json.loads(path.read_text(encoding="utf-8"))
            loaded = read_graph_json(str(path))

        self.assertEqual(raw["format_version"], "gcs-0.3")
        self.assertEqual(loaded.behavior.mode, SolveMode.Drag)
        self.assertEqual(loaded.behavior.fixed_geometry_ids, [0])
        self.assertEqual(loaded.behavior.driven_geometry_ids, [1])
        self.assertEqual(loaded.behavior.target_constraint_ids, [0])
        self.assertEqual(loaded.history, [{"action": "Solve", "payload": {}}])

    def test_legacy_saved_scene_reads_and_normalizes_to_current_schema(self):
        legacy_path = REPO_ROOT / "fixtures" / "scene" / "saved" / "triangle_003_graph.json"

        graph = read_graph_json(str(legacy_path))
        payload = graph.to_dict()

        self.assertEqual(payload["format_version"], "gcs-0.3")
        self.assertIn("state_version", payload)
        self.assertIn("behavior", payload)
        self.assertIn("history", payload)


if __name__ == "__main__":
    unittest.main()
