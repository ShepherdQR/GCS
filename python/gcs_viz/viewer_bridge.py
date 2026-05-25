from typing import Iterable, Mapping, Optional

from gcs_viz.algebra import GCSGraph, GeometryType, ConstraintType


def view_renderers() -> dict:
    from gcs_viz.visualizer import (
        build_3d_on_figure,
        build_graph_on_figure,
        build_three_view_on_figure,
    )

    return {
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


def _coerce_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _append_int(focus: dict, key: str, value):
    int_value = _coerce_int(value)
    if int_value is not None:
        focus[key].append(int_value)


def _normalized_focus(mode: str, focus: dict) -> Optional[dict]:
    normalized = {"mode": mode}
    has_targets = False
    for key in ("rigid_set_ids", "geometry_ids", "constraint_ids"):
        values = sorted(set(focus.get(key, [])))
        normalized[key] = values
        has_targets = has_targets or bool(values)
    return normalized if has_targets else None


def selection_focus(
    graph: GCSGraph,
    rigid_set_ids: Optional[Iterable] = None,
    geometry_ids: Optional[Iterable] = None,
    constraint_ids: Optional[Iterable] = None,
) -> Optional[dict]:
    focus = {
        "rigid_set_ids": [],
        "geometry_ids": [],
        "constraint_ids": [],
    }

    for rs_id in rigid_set_ids or []:
        int_rs_id = _coerce_int(rs_id)
        rigid_set = graph.find_rigid_set(int_rs_id) if int_rs_id is not None else None
        if rigid_set is None:
            continue
        _append_int(focus, "rigid_set_ids", rigid_set.id)
        for gid in rigid_set.geometry_ids:
            _append_int(focus, "geometry_ids", gid)

    for gid in geometry_ids or []:
        int_gid = _coerce_int(gid)
        geometry = graph.find_geometry(int_gid) if int_gid is not None else None
        if geometry is None:
            continue
        _append_int(focus, "geometry_ids", geometry.id)
        _append_int(focus, "rigid_set_ids", geometry.rigid_set_id)

    for cid in constraint_ids or []:
        int_cid = _coerce_int(cid)
        constraint = graph.find_constraint(int_cid) if int_cid is not None else None
        if constraint is None:
            continue
        _append_int(focus, "constraint_ids", constraint.id)
        for gid in constraint.geometry_ids:
            _append_int(focus, "geometry_ids", gid)
            geometry = graph.find_geometry(_coerce_int(gid))
            if geometry is not None:
                _append_int(focus, "rigid_set_ids", geometry.rigid_set_id)

    return _normalized_focus("selection", focus)


def history_focus_from_entry(entry: Mapping, graph: GCSGraph) -> Optional[dict]:
    action = entry.get("action")
    payload = entry.get("payload") or {}
    focus = {
        "rigid_set_ids": [],
        "geometry_ids": [],
        "constraint_ids": [],
    }

    if action in ("AddRigidSet", "RemoveRigidSet"):
        _append_int(focus, "rigid_set_ids", payload.get("id"))
    elif action in ("AddGeometry", "RemoveGeometry"):
        geometry_id = _coerce_int(payload.get("id"))
        _append_int(focus, "geometry_ids", geometry_id)
        _append_int(focus, "rigid_set_ids", payload.get("rigid_set_id"))
        geometry = graph.find_geometry(geometry_id) if geometry_id is not None else None
        if geometry is not None:
            _append_int(focus, "rigid_set_ids", geometry.rigid_set_id)
    elif action in ("AddConstraint", "RemoveConstraint", "UpdateConstraint"):
        constraint_id = _coerce_int(payload.get("id"))
        _append_int(focus, "constraint_ids", constraint_id)
        geometry_ids = payload.get("geometry_ids")
        if geometry_ids is None and constraint_id is not None:
            constraint = graph.find_constraint(constraint_id)
            geometry_ids = constraint.geometry_ids if constraint is not None else []
        for gid in geometry_ids or []:
            geometry_id = _coerce_int(gid)
            _append_int(focus, "geometry_ids", geometry_id)
            geometry = graph.find_geometry(geometry_id) if geometry_id is not None else None
            if geometry is not None:
                _append_int(focus, "rigid_set_ids", geometry.rigid_set_id)

    return _normalized_focus("replay", focus)


def render_graph_view(
    graph: GCSGraph,
    fig,
    view: str = "3d",
    title: Optional[str] = None,
    focus: Optional[Mapping] = None,
):
    renderer = view_renderers().get(view)
    if renderer is None:
        raise ValueError(f"Unknown view mode: {view}")
    if title is None:
        return renderer(graph, fig, focus=focus)
    return renderer(graph, fig, title=title, focus=focus)


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
