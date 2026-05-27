import json
import os
import re
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
    if "constraint_states" in focus:
        states = {
            int(constraint_id): state
            for constraint_id, state in focus["constraint_states"].items()
        }
        normalized["constraint_states"] = states
        has_targets = has_targets or bool(states)
    return normalized if has_targets else None


def _normal_constraint_state(state) -> str:
    normalized = str(state or "").strip().lower()
    if normalized in ("satisfied", "ok", "solved"):
        return "satisfied"
    if normalized in ("violated", "violation", "failed", "error"):
        return "violated"
    return "unknown"


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


def constraint_state_projection(
    graph: GCSGraph,
    constraint_states: Optional[Mapping] = None,
    fill_unknown: bool = False,
) -> Optional[dict]:
    projected_states = {}
    raw_states = constraint_states or {}
    for constraint in graph.constraints:
        if constraint.id in raw_states:
            projected_states[constraint.id] = _normal_constraint_state(raw_states[constraint.id])
            continue
        string_id = str(constraint.id)
        if string_id in raw_states:
            projected_states[constraint.id] = _normal_constraint_state(raw_states[string_id])
            continue
        if fill_unknown:
            projected_states[constraint.id] = "unknown"

    if not projected_states:
        return None
    return {
        "mode": "diagnostic",
        "rigid_set_ids": [],
        "geometry_ids": [],
        "constraint_ids": [],
        "constraint_states": projected_states,
    }


def combine_focus_with_constraint_states(
    focus: Optional[Mapping],
    graph: GCSGraph,
    constraint_states: Optional[Mapping] = None,
    fill_unknown: bool = False,
) -> Optional[dict]:
    projected = constraint_state_projection(graph, constraint_states, fill_unknown=fill_unknown)
    if focus is None:
        return projected

    combined = {
        "mode": focus.get("mode", "selection"),
        "rigid_set_ids": list(focus.get("rigid_set_ids", [])),
        "geometry_ids": list(focus.get("geometry_ids", [])),
        "constraint_ids": list(focus.get("constraint_ids", [])),
    }
    if projected is not None:
        combined["constraint_states"] = dict(projected["constraint_states"])
    elif "constraint_states" in focus:
        combined["constraint_states"] = dict(focus.get("constraint_states") or {})
    return _normalized_focus(combined["mode"], combined)


def constraint_states_from_solve_text(
    graph: GCSGraph,
    output: str,
    fill_unknown: bool = False,
) -> dict:
    raw_states = {}
    pattern = re.compile(
        r"\b(?:C|Constraint)\s*#?\s*(\d+)\b.*\b(SATISFIED|VIOLATED)\b",
        re.IGNORECASE,
    )
    for line in output.splitlines():
        match = pattern.search(line.strip())
        if not match:
            continue
        state = "satisfied" if match.group(2).upper() == "SATISFIED" else "violated"
        raw_states[int(match.group(1))] = state

    projected = constraint_state_projection(graph, raw_states, fill_unknown=fill_unknown)
    if projected is None:
        return {}
    return projected["constraint_states"]


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


def _deletion_hints_from_entry(entry: Mapping) -> list[dict[str, object]]:
    action = entry.get("action")
    payload = entry.get("payload") or {}
    if action == "RemoveRigidSet":
        kind = "rigid_set"
        label = "Removed rigid set"
    elif action == "RemoveGeometry":
        kind = "geometry"
        label = "Removed geometry"
    elif action == "RemoveConstraint":
        kind = "constraint"
        label = "Removed constraint"
    else:
        return []

    removed_id = _coerce_int(payload.get("id"))
    if removed_id is None:
        return []
    return [{
        "kind": kind,
        "id": removed_id,
        "label": f"{label} {removed_id}",
    }]


def project_history_frame(history: Iterable[Mapping], index: int) -> dict:
    history_list = list(history)
    total = len(history_list)
    if total == 0:
        return {
            "mode": "history_frame",
            "index": -1,
            "step": 0,
            "total": 0,
            "action": "Empty",
            "action_label": "No history",
            "progress": 0.0,
            "title": "Replay History",
            "focus": None,
            "deletion_hints": [],
        }
    if index < 0 or index >= total:
        raise IndexError(f"history frame index {index} out of range for {total} entries")

    entry = history_list[index]
    action = str(entry.get("action", "Unknown"))
    replay_graph = build_history_graph(history_list, index)
    focus = history_focus_from_entry(entry, replay_graph)
    deletion_hints = _deletion_hints_from_entry(entry)
    deletion_label = "; ".join(str(hint["label"]) for hint in deletion_hints)
    action_label = f"{action} - {deletion_label}" if deletion_label else action
    step = index + 1
    return {
        "mode": "history_frame",
        "index": index,
        "step": step,
        "total": total,
        "action": action,
        "action_label": action_label,
        "progress": (step / total) * 100.0,
        "title": f"Replay History - Step {step}/{total}: {action_label}",
        "focus": focus,
        "deletion_hints": deletion_hints,
    }


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


def parse_replay_evidence_report(report_path: str) -> Optional[dict]:
    """Parse a GCS replay evidence JSON report into a GUI-friendly summary.

    Reads the structured report produced by ``GCS.exe --save-replay-evidence``
    and extracts the fields most relevant for diagnostic display: status,
    accepted flag, report codes, stage list, rank evidence, and residual
    evidence.

    Returns a dict with keys:
        schema, accepted, status, committed, rolled_back,
        base_version, final_version, report_codes,
        stage_count, stages (list of {stage_name, status, durable_mutation}),
        rank_evidence (nullable),
        residual_evidence (nullable).
    Returns None if the file cannot be read or parsed.
    """
    if not os.path.isfile(report_path):
        return None
    try:
        with open(report_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None

    summary = {
        "schema": data.get("schema", ""),
        "accepted": data.get("accepted", False),
        "status": data.get("status", "unknown"),
        "committed": data.get("committed", False),
        "rolled_back": data.get("rolled_back", False),
        "base_version": data.get("base_version", 0),
        "final_version": data.get("final_version", 0),
        "report_codes": data.get("report_codes", []),
    }

    stages = data.get("stages") or []
    summary["stage_count"] = len(stages)
    summary["stages"] = []
    for stage in stages:
        summary["stages"].append({
            "stage_name": stage.get("stage", "?"),
            "status": stage.get("status", "?"),
            "durable_mutation": stage.get("durable_mutation", False),
        })

    # Rank evidence from the report (may be nested)
    rank = data.get("rank_evidence")
    if rank is None:
        for stage in stages:
            rank = stage.get("rank_evidence")
            if rank is not None:
                break
    summary["rank_evidence"] = rank

    # Residual evidence
    residual = data.get("residual_evidence")
    if residual is None:
        for stage in stages:
            residual = stage.get("residual_evidence")
            if residual is not None:
                break
    summary["residual_evidence"] = residual

    return summary


def format_evidence_summary(evidence: Optional[dict]) -> str:
    """Render a parsed replay evidence dict as a human-readable text block."""
    if evidence is None:
        return "No replay evidence available."

    lines = [
        f"Schema: {evidence.get('schema', '?')}",
        f"Status: {evidence.get('status', '?')}",
        f"Accepted: {evidence.get('accepted', False)}",
        f"Committed: {evidence.get('committed', False)}",
        f"Version: {evidence.get('base_version', 0)} -> {evidence.get('final_version', 0)}",
        f"Report codes: {', '.join(evidence.get('report_codes', []))}",
        f"Stages ({evidence.get('stage_count', 0)}):",
    ]
    for stage in evidence.get("stages", []):
        mutation_marker = " *" if stage.get("durable_mutation") else ""
        lines.append(
            f"  [{stage.get('status', '?')}] {stage.get('stage_name', '?')}{mutation_marker}"
        )

    rank = evidence.get("rank_evidence")
    if rank:
        lines.append(
            f"Rank: variables={rank.get('variable_dimension', '?')} "
            f"free={rank.get('free_variable_dimension', '?')} "
            f"residuals={rank.get('residual_dimension', '?')} "
            f"rank={rank.get('rank', '?')} "
            f"nullity={rank.get('nullity', '?')}"
        )

    residual = evidence.get("residual_evidence")
    if residual:
        lines.append(
            f"Residual: norm={residual.get('norm', '?')} "
            f"max={residual.get('max_abs', residual.get('max', '?'))} "
            f"tolerance={residual.get('tolerance', '?')}"
        )

    return "\n".join(lines)
