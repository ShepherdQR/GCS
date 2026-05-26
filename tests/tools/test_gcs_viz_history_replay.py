import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = REPO_ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from gcs_viz.algebra import read_graph_json  # noqa: E402
from gcs_viz.viewer_bridge import (  # noqa: E402
    apply_history_entry,
    build_history_graph,
    combine_focus_with_constraint_states,
    constraint_state_projection,
    constraint_states_from_solve_text,
    graph_summary,
    history_focus_from_entry,
    project_history_frame,
    selection_focus,
)


class GcsVizHistoryReplayTests(unittest.TestCase):
    def make_history(self):
        return [
            {"action": "AddRigidSet", "payload": {"id": 0}},
            {"action": "AddRigidSet", "payload": {"id": 1}},
            {
                "action": "AddGeometry",
                "payload": {"id": 0, "type": 0, "rigid_set_id": 0, "v": [0, 0, 0, 0, 0, 0]},
            },
            {
                "action": "AddGeometry",
                "payload": {"id": 1, "type": 0, "rigid_set_id": 1, "v": [1, 0, 0, 0, 0, 0]},
            },
            {
                "action": "AddConstraint",
                "payload": {"id": 0, "type": 3, "geometry_ids": [0, 1], "value": 1},
            },
            {"action": "UpdateConstraint", "payload": {"id": 0, "value": 2}},
            {"action": "Solve", "payload": {}},
        ]

    def test_build_history_graph_replays_supported_actions(self):
        replay = build_history_graph(self.make_history(), 6)

        self.assertEqual(len(replay.rigid_sets), 2)
        self.assertEqual(len(replay.geometries), 2)
        self.assertEqual(len(replay.constraints), 1)
        self.assertEqual(replay.constraints[0].value, 2.0)
        self.assertEqual(graph_summary(replay)["constraints"], 1)

    def test_history_replay_is_prefix_addressable(self):
        history = self.make_history()

        empty = build_history_graph(history, -1)
        before_constraint = build_history_graph(history, 3)
        after_constraint = build_history_graph(history, 4)

        self.assertEqual(len(empty.geometries), 0)
        self.assertEqual(len(before_constraint.geometries), 2)
        self.assertEqual(len(before_constraint.constraints), 0)
        self.assertEqual(len(after_constraint.constraints), 1)

    def test_solve_marker_and_unknown_actions_do_not_corrupt_replay(self):
        replay = build_history_graph(self.make_history(), 5)
        before = graph_summary(replay)

        self.assertTrue(apply_history_entry(replay, {"action": "Solve", "payload": {}}))
        self.assertFalse(apply_history_entry(replay, {"action": "FutureAction", "payload": {"id": 99}}))
        after = graph_summary(replay)

        self.assertEqual(before, after)

    def test_legacy_saved_scene_history_reconstructs_topology(self):
        graph = read_graph_json(str(REPO_ROOT / "fixtures" / "scene" / "saved" / "triangle_003_graph.json"))

        replay = build_history_graph(graph.history, len(graph.history) - 1)

        self.assertEqual(len(replay.rigid_sets), 3)
        self.assertEqual(len(replay.geometries), 3)
        self.assertEqual(len(replay.constraints), 3)
        self.assertEqual(replay.constraints[-1].value, 2.0)

    def test_selection_focus_projects_related_ids(self):
        graph = build_history_graph(self.make_history(), 4)

        self.assertEqual(
            selection_focus(graph, rigid_set_ids=[0]),
            {
                "mode": "selection",
                "rigid_set_ids": [0],
                "geometry_ids": [0],
                "constraint_ids": [],
            },
        )
        self.assertEqual(
            selection_focus(graph, geometry_ids=[1]),
            {
                "mode": "selection",
                "rigid_set_ids": [1],
                "geometry_ids": [1],
                "constraint_ids": [],
            },
        )
        self.assertEqual(
            selection_focus(graph, constraint_ids=[0]),
            {
                "mode": "selection",
                "rigid_set_ids": [0, 1],
                "geometry_ids": [0, 1],
                "constraint_ids": [0],
            },
        )

    def test_selection_focus_ignores_bad_or_missing_ids(self):
        graph = build_history_graph(self.make_history(), 4)

        self.assertIsNone(
            selection_focus(
                graph,
                rigid_set_ids=["missing"],
                geometry_ids=[99],
                constraint_ids=[None],
            )
        )

    def test_history_focus_from_entry_matches_replay_action_context(self):
        history = self.make_history()
        replay = build_history_graph(history, 5)

        self.assertEqual(
            history_focus_from_entry(history[5], replay),
            {
                "mode": "replay",
                "rigid_set_ids": [0, 1],
                "geometry_ids": [0, 1],
                "constraint_ids": [0],
            },
        )

    def test_history_focus_returns_none_for_unfocused_markers(self):
        history = self.make_history()
        replay = build_history_graph(history, 6)

        self.assertIsNone(history_focus_from_entry(history[6], replay))

    def test_constraint_state_projection_normalizes_known_states(self):
        graph = build_history_graph(self.make_history(), 4)

        self.assertEqual(
            constraint_state_projection(graph, {0: "VIOLATED"}),
            {
                "mode": "diagnostic",
                "rigid_set_ids": [],
                "geometry_ids": [],
                "constraint_ids": [],
                "constraint_states": {0: "violated"},
            },
        )

    def test_constraint_state_projection_can_fill_unknowns(self):
        graph = build_history_graph(self.make_history(), 4)

        self.assertEqual(
            constraint_state_projection(graph, {}, fill_unknown=True)["constraint_states"],
            {0: "unknown"},
        )

    def test_constraint_states_from_solve_text_requires_constraint_ids(self):
        graph = build_history_graph(self.make_history(), 4)

        aggregate_only = "Constraint report: 1 SATISFIED\n>>> All constraints satisfied <<<"
        self.assertEqual(constraint_states_from_solve_text(graph, aggregate_only), {})
        self.assertEqual(
            constraint_states_from_solve_text(graph, aggregate_only, fill_unknown=True),
            {0: "unknown"},
        )

    def test_constraint_states_from_solve_text_extracts_safe_ids(self):
        graph = build_history_graph(self.make_history(), 4)

        self.assertEqual(
            constraint_states_from_solve_text(graph, "Constraint 0 distance VIOLATED"),
            {0: "violated"},
        )
        self.assertEqual(
            constraint_states_from_solve_text(graph, "C0 distance SATISFIED"),
            {0: "satisfied"},
        )

    def test_combine_focus_with_constraint_states_preserves_selection(self):
        graph = build_history_graph(self.make_history(), 4)
        focus = selection_focus(graph, constraint_ids=[0])

        self.assertEqual(
            combine_focus_with_constraint_states(focus, graph, {0: "violated"}),
            {
                "mode": "selection",
                "rigid_set_ids": [0, 1],
                "geometry_ids": [0, 1],
                "constraint_ids": [0],
                "constraint_states": {0: "violated"},
            },
        )

    def test_project_history_frame_contains_replay_contract(self):
        history = self.make_history()
        frame = project_history_frame(history, 5)

        self.assertEqual(frame["mode"], "history_frame")
        self.assertEqual(frame["step"], 6)
        self.assertEqual(frame["total"], 7)
        self.assertEqual(frame["action"], "UpdateConstraint")
        self.assertEqual(frame["progress"], (6 / 7) * 100.0)
        self.assertEqual(
            frame["focus"],
            {
                "mode": "replay",
                "rigid_set_ids": [0, 1],
                "geometry_ids": [0, 1],
                "constraint_ids": [0],
            },
        )

    def test_project_history_frame_defines_deletion_hints(self):
        history = [
            {"action": "AddRigidSet", "payload": {"id": 0}},
            {
                "action": "AddGeometry",
                "payload": {"id": 0, "type": 0, "rigid_set_id": 0, "v": [0, 0, 0, 0, 0, 0]},
            },
            {"action": "RemoveGeometry", "payload": {"id": 0, "rigid_set_id": 0}},
        ]
        frame = project_history_frame(history, 2)

        self.assertEqual(frame["action_label"], "RemoveGeometry - Removed geometry 0")
        self.assertEqual(
            frame["deletion_hints"],
            [{"kind": "geometry", "id": 0, "label": "Removed geometry 0"}],
        )


if __name__ == "__main__":
    unittest.main()
