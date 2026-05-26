from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_DIR = REPO_ROOT / "python"
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "docs"
    / "architecture"
    / "70-visualization"
    / "assets"
    / "ve002-d5-viewer-evidence-workbench.review.png"
)
DEFAULT_MANIFEST = (
    REPO_ROOT
    / "docs"
    / "architecture"
    / "70-visualization"
    / "assets"
    / "ve002-d5-viewer-evidence-workbench.capture.json"
)


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    title: str
    scene_path: str | None
    view: str
    root_geometry: str
    configure: Callable
    notes: str


def repo_relative(path: Path, repo_root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scenario_definitions() -> list[dict[str, str | None]]:
    return [
        {
            "id": "empty_model",
            "scene_path": None,
            "view": "3d",
            "phase_10_target": "empty model",
        },
        {
            "id": "triangle_003_graph_focus",
            "scene_path": "fixtures/scene/saved/triangle_003.json",
            "view": "graph",
            "phase_10_target": "triangle_003.json",
        },
        {
            "id": "mixed_constraints_replay",
            "scene_path": "fixtures/scene/ui_qa/mixed_geometry_constraints.json",
            "view": "graph",
            "phase_10_target": "mixed constraints plus active replay",
        },
        {
            "id": "d5_showcase_narrow_diagnostics",
            "scene_path": "fixtures/scene/showcase/integrated_feature_showcase.gcs.json",
            "view": "3view",
            "phase_10_target": "D5 diagnostic workbench plus narrow width",
        },
    ]


def _add_python_path(repo_root: Path) -> None:
    python_path = str(repo_root / "python")
    if python_path not in sys.path:
        sys.path.insert(0, python_path)


def _metadata_summary(repo_root: Path) -> dict[str, object]:
    return {
        "python": sys.version.split()[0],
        "python_executable": Path(sys.executable).name,
        "platform": platform.platform(),
    }


def _graph_summary(graph) -> dict[str, object]:
    return {
        "rigid_sets": len(graph.rigid_sets),
        "geometries": len(graph.geometries),
        "constraints": len(graph.constraints),
        "dof": graph.compute_dof(),
        "status": graph.classify_dof_status(),
    }


def _capture_canvas(app, path: Path) -> None:
    app.root.update_idletasks()
    app.root.update()
    app.fig.savefig(path, dpi=120, facecolor=app.fig.get_facecolor())


def _set_common_model(app, graph, scene_path: Path | None) -> None:
    app._cancel_history_replay()
    app.graph = graph
    app._clear_constraint_states()
    app._selection_focus = None
    app._set_current_model(str(scene_path) if scene_path else "")
    app._refresh_tables()


def _configure_empty(app, repo_root: Path, modules) -> dict[str, object]:
    algebra, _, _, _ = modules
    graph = algebra.GCSGraph()
    _set_common_model(app, graph, None)
    app.view_var.set("3d")
    app._set_solve_summary("idle", "No model loaded")
    app._set_replay_state("Replay ready", "Step 0 / 0", "No active replay", 0.0)
    app._log_info("Phase 10 empty-model visual QA state")
    app._draw_graph_on_canvas(app.graph, "3d", use_welcome=True)
    return {
        "rail_state": {
            "solve": app.solve_summary_var.get(),
            "replay": app.replay_state_var.get(),
            "log": app.log_label.cget("text"),
        },
        "focus": None,
    }


def _configure_triangle(app, repo_root: Path, modules) -> dict[str, object]:
    algebra, viewer_bridge, _, _ = modules
    scene = repo_root / "fixtures" / "scene" / "saved" / "triangle_003.json"
    graph = algebra.read_graph_file(str(scene))
    _set_common_model(app, graph, scene)
    app.root.geometry("1280x820+40+40")
    app.view_var.set("graph")
    focus = viewer_bridge.selection_focus(graph, constraint_ids=[0])
    app._selection_focus = focus
    app._set_solve_summary("unknown", "Reviewer focus on C0; solve not rerun in capture")
    app._set_replay_state("Replay ready", "Step 0 / 0", "No active replay", 0.0)
    app._log_info("Triangle scene loaded for visual QA")
    app._draw_graph_on_canvas(
        graph,
        "graph",
        title="Phase 10 - triangle_003 graph focus",
        focus=focus,
    )
    return {
        "scene": repo_relative(scene, repo_root),
        "graph_summary": _graph_summary(graph),
        "focus": focus,
        "rail_state": {
            "solve": app.solve_summary_var.get(),
            "replay": app.replay_state_var.get(),
            "log": app.log_label.cget("text"),
        },
    }


def _configure_mixed_replay(app, repo_root: Path, modules) -> dict[str, object]:
    algebra, viewer_bridge, _, _ = modules
    scene = repo_root / "fixtures" / "scene" / "ui_qa" / "mixed_geometry_constraints.json"
    graph = algebra.read_graph_file(str(scene))
    _set_common_model(app, graph, scene)
    app.root.geometry("1280x820+40+40")
    app.view_var.set("graph")
    history = list(graph.history)
    frame_index = len(history) - 1
    projection = viewer_bridge.project_history_frame(history, frame_index)
    replay_graph = viewer_bridge.build_history_graph(history, frame_index)
    focus = projection.get("focus")
    states = {0: "satisfied", 1: "satisfied", 2: "unknown", 3: "violated", 4: "unknown"}
    focus = viewer_bridge.combine_focus_with_constraint_states(
        focus,
        replay_graph,
        states,
        fill_unknown=True,
    )
    app._constraint_states = states
    app._set_solve_summary("warning", "Replay diagnostic overlay: C3 violated")
    app._set_replay_state(
        "Replay running",
        f"Step {projection['step']} / {projection['total']}",
        projection["action_label"],
        projection["progress"],
    )
    app._log_warning("Replay frame visual QA: diagnostic overlay is active")
    app._draw_graph_on_canvas(
        replay_graph,
        "graph",
        title=projection["title"],
        focus=focus,
    )
    return {
        "scene": repo_relative(scene, repo_root),
        "graph_summary": _graph_summary(replay_graph),
        "history_frame": projection,
        "constraint_states": states,
        "focus": focus,
        "rail_state": {
            "solve": app.solve_summary_var.get(),
            "replay": app.replay_state_var.get(),
            "step": app.replay_step_var.get(),
            "action": app.replay_action_var.get(),
            "log": app.log_label.cget("text"),
        },
    }


def _configure_d5_showcase(app, repo_root: Path, modules) -> dict[str, object]:
    algebra, viewer_bridge, _, _ = modules
    scene = repo_root / "fixtures" / "scene" / "showcase" / "integrated_feature_showcase.gcs.json"
    metadata = repo_root / "fixtures" / "scene" / "showcase" / "integrated_feature_showcase.metadata.json"
    graph = algebra.read_graph_file(str(scene))
    _set_common_model(app, graph, scene)
    app.root.geometry("960x700+40+40")
    app.view_var.set("3view")
    states = {0: "satisfied", 1: "satisfied", 2: "violated", 3: "unknown"}
    focus = viewer_bridge.selection_focus(graph, constraint_ids=[2])
    focus = viewer_bridge.combine_focus_with_constraint_states(
        focus,
        graph,
        states,
        fill_unknown=True,
    )
    app._constraint_states = states
    app._selection_focus = focus
    app._set_solve_summary("warning", "Accepted with warnings; C2 selected as diagnostic focus")
    app._set_replay_state("Replay running", "Step 4 / 6", "Solve - report evidence only", 66.7)
    app._log_warning("D5 capture: diagnostic focus C2 with narrow workbench width")
    app._draw_graph_on_canvas(
        graph,
        "3view",
        title="D5 Solver Evidence Workbench - diagnostic focus",
        focus=focus,
    )
    return {
        "scene": repo_relative(scene, repo_root),
        "metadata": repo_relative(metadata, repo_root),
        "graph_summary": _graph_summary(graph),
        "constraint_states": states,
        "focus": focus,
        "rail_state": {
            "solve": app.solve_summary_var.get(),
            "replay": app.replay_state_var.get(),
            "step": app.replay_step_var.get(),
            "action": app.replay_action_var.get(),
            "log": app.log_label.cget("text"),
        },
        "narrow_width_px": 960,
    }


def _build_scenarios() -> list[Scenario]:
    definitions = scenario_definitions()
    return [
        Scenario(
            scenario_id="empty_model",
            title="Empty model / welcome",
            scene_path=definitions[0]["scene_path"],
            view="3d",
            root_geometry="1280x820+40+40",
            configure=_configure_empty,
            notes="Exercises the empty workbench state and welcome renderer.",
        ),
        Scenario(
            scenario_id="triangle_003_graph_focus",
            title="triangle_003 / graph focus",
            scene_path=definitions[1]["scene_path"],
            view="graph",
            root_geometry="1280x820+40+40",
            configure=_configure_triangle,
            notes="Exercises object focus and graph-node label contrast.",
        ),
        Scenario(
            scenario_id="mixed_constraints_replay",
            title="UI QA mixed constraints / replay frame",
            scene_path=definitions[2]["scene_path"],
            view="graph",
            root_geometry="1280x820+40+40",
            configure=_configure_mixed_replay,
            notes="Exercises active replay rail projection plus diagnostic overlay states.",
        ),
        Scenario(
            scenario_id="d5_showcase_narrow_diagnostics",
            title="D5 showcase / diagnostic focus",
            scene_path=definitions[3]["scene_path"],
            view="3view",
            root_geometry="960x700+40+40",
            configure=_configure_d5_showcase,
            notes="Exercises the Solver Evidence Workbench chain at narrow desktop width.",
        ),
    ]


def _compose_contact_sheet(panel_paths: list[Path], scenarios: list[Scenario], output: Path, modules) -> None:
    _, _, matplotlib, plt = modules
    image_module = __import__("matplotlib.image", fromlist=["imread"])

    fig, axes = plt.subplots(2, 2, figsize=(16, 13.2), dpi=100)
    fig.patch.set_facecolor("#F5F2EC")
    for axis, panel_path, scenario in zip(axes.flat, panel_paths, scenarios):
        image = image_module.imread(panel_path)
        axis.imshow(image)
        axis.axis("off")
        axis.set_title(
            f"{scenario.title}\nview={scenario.view}; root={scenario.root_geometry}",
            fontsize=12,
            color="#2D2A26",
            pad=10,
        )
    fig.suptitle(
        "VE-002 D5 viewer visual QA capture",
        fontsize=18,
        color="#2D2A26",
        y=0.985,
    )
    fig.text(
        0.5,
        0.018,
        "Generated from GCSPlatformGUI TkAgg canvas states; OS screen grab was not required for this baseline.",
        ha="center",
        va="bottom",
        fontsize=10,
        color="#5F5B53",
    )
    fig.tight_layout(rect=(0.02, 0.04, 0.98, 0.95))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)


def capture_viewer_evidence(
    repo_root: Path = REPO_ROOT,
    output: Path = DEFAULT_OUTPUT,
    manifest: Path = DEFAULT_MANIFEST,
) -> dict[str, object]:
    _add_python_path(repo_root)

    from gcs_viz import algebra
    from gcs_viz import viewer_bridge
    from gcs_viz.platform_gui import GCSPlatformGUI
    import matplotlib
    import matplotlib.pyplot as plt

    modules = (algebra, viewer_bridge, matplotlib, plt)
    app = GCSPlatformGUI()
    scenarios = _build_scenarios()
    panel_metadata: list[dict[str, object]] = []
    panel_paths: list[Path] = []

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            for scenario in scenarios:
                app.root.geometry(scenario.root_geometry)
                details = scenario.configure(app, repo_root, modules)
                panel_path = temp_root / f"{scenario.scenario_id}.png"
                _capture_canvas(app, panel_path)
                panel_paths.append(panel_path)
                panel_metadata.append(
                    {
                        "id": scenario.scenario_id,
                        "title": scenario.title,
                        "scene_path": scenario.scene_path,
                        "view": scenario.view,
                        "root_geometry": scenario.root_geometry,
                        "notes": scenario.notes,
                        "canvas_png_bytes": panel_path.stat().st_size,
                        "details": details,
                    }
                )
            _compose_contact_sheet(panel_paths, scenarios, output, modules)
    finally:
        app.root.destroy()

    artifact_info = {
        "path": repo_relative(output, repo_root),
        "bytes": output.stat().st_size,
        "sha256": sha256_file(output),
    }
    payload = {
        "schema_version": "gcs.viewer_visual_evidence.v1",
        "evidence_id": "VE-002",
        "title": "D5 Solver Evidence Workbench viewer visual QA capture",
        "generated_by": repo_relative(Path(__file__), repo_root),
        "artifact": artifact_info,
        "environment": _metadata_summary(repo_root),
        "scope": {
            "desktop_launcher": "GCSPlatformGUI",
            "capture_surface": "TkAgg Matplotlib canvas exported from platform_gui.py",
            "full_window_screen_grab": "not captured in this shell; rail state is recorded in JSON",
            "narrative_map_updated": False,
        },
        "scenarios": panel_metadata,
    }
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture D5 viewer visual evidence")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)

    payload = capture_viewer_evidence(output=args.output, manifest=args.manifest)
    print(f"Wrote {payload['artifact']['path']}")
    print(f"sha256 {payload['artifact']['sha256']}")
    print(f"Wrote {repo_relative(args.manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
