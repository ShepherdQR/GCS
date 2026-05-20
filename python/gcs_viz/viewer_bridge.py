from typing import Iterable, Mapping, Optional

from gcs_viz.algebra import GCSGraph, GeometryType, ConstraintType
from gcs_viz.visualizer import (
    build_3d_on_figure,
    build_graph_on_figure,
    build_three_view_on_figure,
)


VIEW_RENDERERS = {
    "3d": build_3d_on_figure,
    "graph": build_graph_on_figure,
    "3view": build_three_view_on_figure,
}


def graph_summary(graph: GCSGraph) -> dict:
    return {
        "rigid_sets": len(graph.rigid_sets),
        "geometries": len(graph.geometries),
        "constraints": len(graph.constraints),
        "dof": graph.compute_dof(),
        "status": graph.classify_dof_status(),
    }


def render_graph_view(graph: GCSGraph, fig, view: str = "3d", title: Optional[str] = None):
    renderer = VIEW_RENDERERS.get(view)
    if renderer is None:
        raise ValueError(f"Unknown view mode: {view}")
    if title is None:
        return renderer(graph, fig)
    return renderer(graph, fig, title=title)


def render_message(fig, message: str, title: Optional[str] = None):
    fig.clear()
    ax = fig.add_subplot(111)
    ax.axis("off")
    if title:
        ax.set_title(title)
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes)
    return ax


def build_history_graph(history: Iterable[Mapping], through_index: int) -> GCSGraph:
    replay_graph = GCSGraph()
    if through_index < 0:
        return replay_graph
    for entry in list(history)[:through_index + 1]:
        apply_history_entry(replay_graph, entry)
    return replay_graph


def apply_history_entry(replay_graph: GCSGraph, entry: Mapping) -> bool:
    action = entry.get("action")
    payload = entry.get("payload") or {}

    try:
        if action == "AddRigidSet":
            rs_id = payload.get("id")
            if rs_id is not None and replay_graph.find_rigid_set(int(rs_id)) is None:
                replay_graph.add_rigid_set(int(rs_id))
            return True
        if action == "RemoveRigidSet":
            return replay_graph.remove_rigid_set(int(payload["id"]))
        if action == "AddGeometry":
            gid = int(payload["id"])
            rs_id = int(payload["rigid_set_id"])
            if replay_graph.find_rigid_set(rs_id) is None:
                replay_graph.add_rigid_set(rs_id)
            if replay_graph.find_geometry(gid) is None:
                replay_graph.add_geometry(
                    GeometryType(int(payload["type"])),
                    rs_id,
                    v=list(payload.get("v", [0.0] * 6)),
                    geom_id=gid,
                )
            return True
        if action == "RemoveGeometry":
            return replay_graph.remove_geometry(int(payload["id"]))
        if action == "AddConstraint":
            cid = int(payload["id"])
            if replay_graph.find_constraint(cid) is None:
                replay_graph.add_constraint(
                    ConstraintType(int(payload["type"])),
                    list(payload.get("geometry_ids", [])),
                    value=float(payload.get("value", 0.0)),
                    cid=cid,
                )
            return True
        if action == "RemoveConstraint":
            return replay_graph.remove_constraint(int(payload["id"]))
        if action == "UpdateConstraint":
            constraint = replay_graph.find_constraint(int(payload["id"]))
            if constraint is not None:
                constraint.value = float(payload.get("value", constraint.value))
            return constraint is not None
        if action == "Solve":
            return True
    except (KeyError, TypeError, ValueError):
        return False

    return False
