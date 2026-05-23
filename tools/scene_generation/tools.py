#!/usr/bin/env python3
"""GCS scene-generation tools.

Entry point:
    python tools.py <command> --input '<json>'

`tools.py` is the compatibility CLI facade. Stable contracts, storage rules,
and promotion adapters live under `gcs_scene_generation/` so later modules can
be split without changing command names.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOL_DIR not in sys.path:
    sys.path.insert(0, TOOL_DIR)

from gcs_scene_generation import contracts as scene_contracts
from gcs_scene_generation import gcs_model
from gcs_scene_generation import promotion as promotion_adapters
from gcs_scene_generation import storage as scene_storage
from gcs_scene_generation import topology

REPO_ROOT = os.path.abspath(os.path.join(TOOL_DIR, "..", ".."))
STORE_DIR = os.environ.get(
    "GCS_SCENE_GENERATION_STORE_DIR",
    os.path.join(TOOL_DIR, ".store"),
)
DEFAULT_GCS_EXE = os.path.join(
    REPO_ROOT,
    "out",
    "build",
    "clang-ninja",
    "GCS.exe" if os.name == "nt" else "GCS",
)

GEOMETRY_TYPES = scene_contracts.GEOMETRY_TYPES
CONSTRAINT_TYPES = scene_contracts.CONSTRAINT_TYPES
CONSTRAINT_TYPE_PREFERENCE = scene_contracts.CONSTRAINT_TYPE_PREFERENCE
VALID_CONSTRAINT_SIGNATURES = scene_contracts.VALID_CONSTRAINT_SIGNATURES
GEOMETRY_TYPE_MAP = scene_contracts.GEOMETRY_TYPE_MAP
CONSTRAINT_TYPE_MAP = scene_contracts.CONSTRAINT_TYPE_MAP
FAILURE_REASON_CODES = scene_contracts.FAILURE_REASON_CODES
is_valid_constraint_signature = scene_contracts.is_valid_constraint_signature


# ---------------------------------------------------------------------------
# Stable storage
# ---------------------------------------------------------------------------


def _store_path(graph_id: str) -> str:
    return scene_storage.store_path(STORE_DIR, graph_id)


def save_graph(graph_id: str, data: dict) -> None:
    scene_storage.save_graph(STORE_DIR, graph_id, data)


def load_graph(graph_id: str) -> dict:
    return scene_storage.load_graph(STORE_DIR, graph_id)


def list_graphs() -> list[dict]:
    return scene_storage.list_graphs(STORE_DIR)


def delete_graph(graph_id: str) -> dict:
    return scene_storage.delete_graph(STORE_DIR, graph_id)


def _safe_store_id(value: str, field_name: str = "id") -> str:
    return scene_storage.safe_store_id(value, field_name)


def _write_json_file(path: str, data: dict | list) -> None:
    scene_storage.write_json_file(path, data)


def _read_json_file(path: str) -> dict:
    return scene_storage.read_json_file(path)


def _exploration_root(exploration_id: str) -> str:
    return scene_storage.exploration_root(STORE_DIR, exploration_id)


def _promotion_root(promotion_id: str) -> str:
    return scene_storage.promotion_root(STORE_DIR, promotion_id)


def _candidate_slot(candidate_id: str) -> str:
    return scene_storage.candidate_slot(candidate_id)


def _candidate_root(exploration_id: str, candidate_id: str) -> str:
    return scene_storage.candidate_root(STORE_DIR, exploration_id, candidate_id)


def _append_trace(trace_path: str, event: dict) -> None:
    scene_storage.append_trace(trace_path, event)


def _sha256_text(text: str) -> str:
    return scene_storage.sha256_text(text)


# ---------------------------------------------------------------------------
# Generic graph helpers
# ---------------------------------------------------------------------------


def _sort_key(value):
    return topology.sort_key(value)


def _canonical_edge(u, v):
    return topology.canonical_edge(u, v)


def _unique_edges(edges) -> list[list]:
    return topology.unique_edges(edges)


def build_adjacency(vertices, edges) -> dict:
    return topology.build_adjacency(vertices, edges)


def connected_components(vertices, edges) -> list[list]:
    return topology.connected_components(vertices, edges)


def tarjan_articulation_bcc(vertices, edges) -> tuple[list, list[dict], int]:
    return topology.tarjan_articulation_bcc(vertices, edges)


def _geometry_primal_edges(gcs: dict) -> list[list[int]]:
    return gcs_model.geometry_primal_edges(gcs)


def _generated_id(prefix: str, rng: random.Random) -> str:
    return f"{prefix}_{rng.randint(1, 999):03d}"


def _rng(seed) -> random.Random:
    return random.Random(seed)


# ---------------------------------------------------------------------------
# GCS model helpers
# ---------------------------------------------------------------------------


def _first_valid_constraint_type(g1: dict, g2: dict, allowed=None) -> str | None:
    allowed_set = set(allowed or CONSTRAINT_TYPES)
    for ctype in CONSTRAINT_TYPE_PREFERENCE:
        if ctype in allowed_set and is_valid_constraint_signature(ctype, g1["type"], g2["type"]):
            return ctype
    return None


def _normalize_distribution(allowed_types: list[str], distribution: dict) -> list[tuple[str, float]]:
    weights = []
    for gtype in allowed_types:
        if gtype not in GEOMETRY_TYPES:
            raise ValueError(f"Unknown geometry type '{gtype}'")
        weights.append((gtype, float(distribution.get(gtype, 1.0))))
    total = sum(weight for _, weight in weights)
    if total <= 0:
        raise ValueError("Geometry type distribution must have positive weight")
    return [(gtype, weight / total) for gtype, weight in weights]


def _choose_weighted(rng: random.Random, weighted: list[tuple[str, float]]) -> str:
    target = rng.random()
    cumulative = 0.0
    for item, weight in weighted:
        cumulative += weight
        if target <= cumulative:
            return item
    return weighted[-1][0]


def _rebuild_rigid_sets(gcs: dict, num_rigid_sets: int | None = None) -> None:
    gcs_model.rebuild_rigid_sets(gcs, num_rigid_sets)


def _geometry_map(gcs: dict) -> dict:
    return gcs_model.geometry_map(gcs)


def _constraint_has_distinct_rigid_sets(constraint: dict, geom_by_id: dict) -> bool:
    return gcs_model.constraint_has_distinct_rigid_sets(constraint, geom_by_id)


def _graph_coloring(vertices, edges, requested_colors: int, rng: random.Random, randomize: bool = False) -> dict | None:
    return gcs_model.graph_coloring(vertices, edges, requested_colors, rng, randomize)


def _assign_rigid_sets_for_edges(
    vertices,
    edges,
    requested_count: int,
    rng: random.Random,
    assignment: str,
    allow_new_rigid_sets: bool,
) -> tuple[dict, int, bool]:
    return gcs_model.assign_rigid_sets_for_edges(
        vertices,
        edges,
        requested_count,
        rng,
        assignment,
        allow_new_rigid_sets,
    )


# ---------------------------------------------------------------------------
# Command: generate_skeleton_graph
# ---------------------------------------------------------------------------


def tool_generate_skeleton_graph(params: dict) -> dict:
    num_vertices = int(params["num_vertices"])
    method = params.get("method", "cycle_plus_chords")
    extra_edges = int(params.get("extra_edges", 0))
    seed = params.get("seed")
    rng = _rng(seed)

    if num_vertices < 3:
        return {"error": "num_vertices must be >= 3 for vertex biconnectivity"}
    if extra_edges < 0:
        return {"error": "extra_edges must be >= 0"}

    vertices = list(range(num_vertices))
    if method == "cycle_plus_chords":
        edges = [[i, (i + 1) % num_vertices] for i in range(num_vertices)]
        possible_chords = []
        for i in range(num_vertices):
            for j in range(i + 2, num_vertices):
                if i == 0 and j == num_vertices - 1:
                    continue
                possible_chords.append([i, j])
        rng.shuffle(possible_chords)
        edges.extend(possible_chords[: min(extra_edges, len(possible_chords))])
        certificate = {
            "base": "cycle",
            "augmentation": "added_chords" if extra_edges else "none",
            "property_preserved": "adding_edges_preserves_vertex_biconnectivity",
        }
    elif method == "ear_decomposition":
        edges = [[0, 1], [1, 2], [0, 2]]
        next_vertex = 3
        while next_vertex < num_vertices:
            base_edge = edges[rng.randrange(len(edges))]
            u, v = base_edge
            edges.append([u, next_vertex])
            edges.append([next_vertex, v])
            next_vertex += 1
        if extra_edges:
            existing = {_canonical_edge(u, v) for u, v in edges}
            possible = []
            for i in range(num_vertices):
                for j in range(i + 1, num_vertices):
                    if _canonical_edge(i, j) not in existing:
                        possible.append([i, j])
            rng.shuffle(possible)
            edges.extend(possible[: min(extra_edges, len(possible))])
        certificate = {
            "base": "triangle",
            "augmentation": "ear_decomposition",
            "property_preserved": "ear_decomposition_preserves_vertex_biconnectivity",
        }
    else:
        return {"error": f"Unknown method: {method}"}

    edges = _unique_edges(edges)
    graph_id = params.get("graph_id", _generated_id("skeleton", rng))
    result = {
        "graph_id": graph_id,
        "num_vertices": num_vertices,
        "vertices": vertices,
        "edges": edges,
        "generation": {
            "method": method,
            "seed": seed,
            "extra_edges": extra_edges,
        },
        "generation_certificate": certificate,
    }
    save_graph(graph_id, result)
    return result


# ---------------------------------------------------------------------------
# Command: lift_skeleton_to_gcs
# ---------------------------------------------------------------------------


def tool_lift_skeleton_to_gcs(params: dict) -> dict:
    skeleton_graph_id = params["skeleton_graph_id"]
    seed = params.get("seed")
    rng = _rng(seed)

    try:
        skeleton = load_graph(skeleton_graph_id)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    geometry_policy = params.get(
        "geometry_type_policy",
        {"allowed_types": ["Point", "Line", "Plane"], "distribution": {"Point": 0.6, "Line": 0.3, "Plane": 0.1}},
    )
    constraint_policy = params.get(
        "constraint_type_policy",
        {"allowed_types": list(CONSTRAINT_TYPES), "respect_type_signature": True},
    )
    rigid_policy = params.get(
        "rigid_set_policy",
        {"num_rigid_sets": 3, "assignment": "random_balanced", "allow_new_rigid_sets": True},
    )

    try:
        allowed_geom_types = list(geometry_policy.get("allowed_types", GEOMETRY_TYPES))
        weighted_geom_types = _normalize_distribution(allowed_geom_types, geometry_policy.get("distribution", {}))
        allowed_constraint_types = list(constraint_policy.get("allowed_types", CONSTRAINT_TYPES))
        unknown_constraints = [ctype for ctype in allowed_constraint_types if ctype not in CONSTRAINT_TYPES]
        if unknown_constraints:
            return {"error": f"Unknown constraint type(s): {unknown_constraints}"}
    except ValueError as exc:
        return {"error": str(exc)}

    num_vertices = int(skeleton["num_vertices"])
    vertices = skeleton.get("vertices", list(range(num_vertices)))
    edges = _unique_edges(skeleton.get("edges", []))

    try:
        rigid_assignments, actual_rs_count, expanded = _assign_rigid_sets_for_edges(
            vertices=vertices,
            edges=edges,
            requested_count=int(rigid_policy.get("num_rigid_sets", 3)),
            rng=rng,
            assignment=rigid_policy.get("assignment", "random_balanced"),
            allow_new_rigid_sets=bool(rigid_policy.get("allow_new_rigid_sets", True)),
        )
    except ValueError as exc:
        return {"error": str(exc)}

    geom_types = {vertex: _choose_weighted(rng, weighted_geom_types) for vertex in vertices}
    geometries = []
    for vertex in sorted(vertices, key=_sort_key):
        geometries.append(
            {
                "id": vertex,
                "type": geom_types[vertex],
                "rigid_set_id": rigid_assignments[vertex],
                "v": [0.0] * 6,
            }
        )

    geom_by_id = {g["id"]: g for g in geometries}
    constraints = []
    respect_signature = bool(constraint_policy.get("respect_type_signature", True))
    for idx, (u, v) in enumerate(edges):
        g1 = geom_by_id[u]
        g2 = geom_by_id[v]
        if g1["rigid_set_id"] == g2["rigid_set_id"]:
            return {"error": f"Internal error: edge {u}-{v} was assigned within one rigid set"}
        candidates = []
        for ctype in allowed_constraint_types:
            if not respect_signature or is_valid_constraint_signature(ctype, g1["type"], g2["type"]):
                candidates.append(ctype)
        if not candidates:
            ctype = _first_valid_constraint_type(g1, g2, CONSTRAINT_TYPE_PREFERENCE)
            if ctype is None:
                return {"error": f"No valid constraint type for {g1['type']}-{g2['type']}"}
        else:
            ctype = rng.choice(candidates)
        constraints.append({"id": idx, "type": ctype, "geometry_ids": [u, v], "value": 0.0})

    gcs_graph_id = params.get("gcs_graph_id", _generated_id("gcs", rng))
    gcs = {
        "gcs_graph_id": gcs_graph_id,
        "rigid_sets": [],
        "geometries": geometries,
        "constraints": constraints,
        "num_geometries": len(geometries),
        "num_constraints": len(constraints),
        "status": "constructed",
        "generation": {
            "source_skeleton_graph_id": skeleton_graph_id,
            "seed": seed,
            "rigid_set_policy": rigid_policy,
            "rigid_sets_expanded": expanded,
        },
    }
    _rebuild_rigid_sets(gcs, actual_rs_count)
    save_graph(gcs_graph_id, gcs)
    return {
        "gcs_graph_id": gcs_graph_id,
        "num_rigid_sets": len(gcs["rigid_sets"]),
        "num_geometries": len(geometries),
        "num_constraints": len(constraints),
        "status": "constructed",
        "rigid_set_invariant": "constraints_connect_distinct_rigid_sets",
        "rigid_sets_expanded": expanded,
    }


# ---------------------------------------------------------------------------
# Command: project_gcs_graph
# ---------------------------------------------------------------------------


def tool_project_gcs_graph(params: dict) -> dict:
    gcs_graph_id = params["gcs_graph_id"]
    projection = params.get("projection", "geometry_primal")
    rng = _rng(params.get("seed"))

    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    geom_by_id = _geometry_map(gcs)
    if projection == "geometry_primal":
        vertices = sorted(geom_by_id.keys(), key=_sort_key)
        edges = _geometry_primal_edges(gcs)
        rule = "geometries sharing one constraint are connected"
    elif projection == "incidence_bipartite":
        vertices = [f"G{gid}" for gid in sorted(geom_by_id.keys(), key=_sort_key)]
        vertices.extend(f"C{c['id']}" for c in sorted(gcs.get("constraints", []), key=lambda c: c["id"]))
        edges = []
        for constraint in sorted(gcs.get("constraints", []), key=lambda c: c["id"]):
            for gid in sorted(constraint.get("geometry_ids", []), key=_sort_key):
                edges.append([f"G{gid}", f"C{constraint['id']}"])
        rule = "bipartite: geometry and constraint nodes, edge if geometry participates in constraint"
    elif projection == "rigidset_quotient":
        vertices = sorted({g["rigid_set_id"] for g in gcs.get("geometries", [])})
        edges = []
        for constraint in gcs.get("constraints", []):
            rs_ids = []
            for gid in constraint.get("geometry_ids", []):
                geometry = geom_by_id.get(gid)
                if geometry is not None:
                    rs_ids.append(geometry["rigid_set_id"])
            for i in range(len(rs_ids)):
                for j in range(i + 1, len(rs_ids)):
                    if rs_ids[i] != rs_ids[j]:
                        edges.append([rs_ids[i], rs_ids[j]])
        edges = _unique_edges(edges)
        rule = "rigid sets as nodes, edge if constraints connect different rigid sets"
    else:
        return {"error": f"Unknown projection: {projection}"}

    projected_graph_id = params.get("projected_graph_id", _generated_id("proj", rng))
    result = {
        "projected_graph_id": projected_graph_id,
        "source_gcs_graph_id": gcs_graph_id,
        "projection": projection,
        "vertices": vertices,
        "edges": edges,
        "projection_rule": rule,
    }
    save_graph(projected_graph_id, result)
    return result


# ---------------------------------------------------------------------------
# Command: check_vertex_biconnected
# ---------------------------------------------------------------------------


def tool_check_vertex_biconnected(params: dict) -> dict:
    graph_id = params.get("projected_graph_id") or params.get("graph_id")
    if not graph_id:
        return {"error": "Must provide projected_graph_id or graph_id"}
    try:
        graph = load_graph(graph_id)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    vertices = graph.get("vertices", list(range(int(graph.get("num_vertices", 0)))))
    edges = _unique_edges(graph.get("edges", []))
    if not vertices:
        return {"error": "Graph has no vertices"}

    articulation_points, bcc_list, num_components = tarjan_articulation_bcc(vertices, edges)
    result = {
        "is_vertex_biconnected": len(vertices) >= 3 and num_components == 1 and not articulation_points,
        "num_connected_components": num_components,
        "articulation_points": articulation_points,
        "biconnected_components": bcc_list,
        "certificate": {
            "algorithm": "Tarjan articulation point / biconnected components",
            "root_children_condition_satisfied": True,
            "lowlink_conditions_satisfied": True,
        },
    }
    return result


# ---------------------------------------------------------------------------
# Command: validate_gcs_schema
# ---------------------------------------------------------------------------


def tool_validate_gcs_schema(params: dict) -> dict:
    gcs_graph_id = params["gcs_graph_id"]
    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    violations = []
    geometries = gcs.get("geometries", [])
    constraints = gcs.get("constraints", [])
    rigid_sets = gcs.get("rigid_sets", [])

    geom_ids = [g.get("id") for g in geometries]
    constraint_ids = [c.get("id") for c in constraints]
    rs_ids = [rs.get("id") for rs in rigid_sets]

    for gid, count in Counter(geom_ids).items():
        if count > 1:
            violations.append({"type": "duplicate_geometry_id", "geometry_id": gid, "message": f"Geometry id {gid} is not unique."})
    for cid, count in Counter(constraint_ids).items():
        if count > 1:
            violations.append({"type": "duplicate_constraint_id", "constraint_id": cid, "message": f"Constraint id {cid} is not unique."})
    for rs_id, count in Counter(rs_ids).items():
        if count > 1:
            violations.append({"type": "duplicate_rigid_set_id", "rigid_set_id": rs_id, "message": f"RigidSet id {rs_id} is not unique."})

    geom_by_id = {g.get("id"): g for g in geometries}
    rs_by_id = {rs.get("id"): rs for rs in rigid_sets}

    for geometry in geometries:
        gid = geometry.get("id")
        gtype = geometry.get("type")
        rs_id = geometry.get("rigid_set_id")
        if gtype not in GEOMETRY_TYPES:
            violations.append({"type": "invalid_geometry_type", "geometry_id": gid, "message": f"Geometry {gid} has unknown type {gtype}."})
        if rs_id not in rs_by_id:
            violations.append({"type": "geometry_not_in_rigid_set", "geometry_id": gid, "message": f"Geometry {gid} references non-existent RigidSet {rs_id}."})
        values = geometry.get("v", [])
        if len(values) != 6:
            violations.append({"type": "invalid_geometry_parameter_length", "geometry_id": gid, "message": f"Geometry {gid} has {len(values)} parameters, expected 6."})
        elif gtype == "Line" and values[:3] == values[3:6]:
            violations.append({"type": "degenerate_line", "geometry_id": gid, "message": f"Line {gid} is degenerate (start == end)."})
        elif gtype == "Plane" and _vec_len(values[3:6]) < 1e-12:
            violations.append({"type": "zero_plane_normal", "geometry_id": gid, "message": f"Plane {gid} has zero normal vector."})

    memberships = defaultdict(list)
    for rs in rigid_sets:
        for gid in rs.get("geometry_ids", []):
            memberships[gid].append(rs.get("id"))
            if gid not in geom_by_id:
                violations.append({"type": "rigid_set_unknown_geometry", "rigid_set_id": rs.get("id"), "geometry_id": gid, "message": f"RigidSet {rs.get('id')} references non-existent Geometry {gid}."})
    for geometry in geometries:
        gid = geometry.get("id")
        rs_id = geometry.get("rigid_set_id")
        if memberships.get(gid, []) != [rs_id]:
            violations.append(
                {
                    "type": "rigid_set_membership_mismatch",
                    "geometry_id": gid,
                    "message": f"Geometry {gid} declares RigidSet {rs_id} but memberships are {memberships.get(gid, [])}.",
                }
            )

    for constraint in constraints:
        cid = constraint.get("id")
        ctype = constraint.get("type")
        gids = constraint.get("geometry_ids", [])
        if ctype not in CONSTRAINT_TYPES:
            violations.append({"type": "invalid_constraint_type", "constraint_id": cid, "message": f"Constraint {cid} has unknown type {ctype}."})
        if len(gids) < 2:
            violations.append({"type": "invalid_constraint_arity", "constraint_id": cid, "message": f"Constraint {cid} has arity {len(gids)}, expected >= 2."})
        if len(gids) != len(set(gids)):
            violations.append({"type": "duplicate_constraint_geometry", "constraint_id": cid, "geometry_ids": gids, "message": f"Constraint {cid} references a geometry more than once."})
        for gid in gids:
            if gid not in geom_by_id:
                violations.append({"type": "invalid_geometry_reference", "constraint_id": cid, "geometry_id": gid, "message": f"Constraint {cid} references non-existent Geometry {gid}."})
        if len(gids) >= 2 and all(gid in geom_by_id for gid in gids[:2]) and ctype in CONSTRAINT_TYPES:
            g1 = geom_by_id[gids[0]]
            g2 = geom_by_id[gids[1]]
            if not is_valid_constraint_signature(ctype, g1.get("type"), g2.get("type")):
                violations.append(
                    {
                        "type": "invalid_constraint_signature",
                        "constraint_id": cid,
                        "geometry_ids": gids,
                        "message": f"{ctype} constraint has invalid signature {g1.get('type')}-{g2.get('type')}.",
                    }
                )
        if len(gids) >= 2 and all(gid in geom_by_id for gid in gids):
            if not _constraint_has_distinct_rigid_sets(constraint, geom_by_id):
                rs_values = [geom_by_id[gid]["rigid_set_id"] for gid in gids]
                violations.append(
                    {
                        "type": "constraint_same_rigid_set",
                        "constraint_id": cid,
                        "geometry_ids": gids,
                        "rigid_set_ids": rs_values,
                        "message": f"Constraint {cid} connects geometries that are not all in distinct rigid sets.",
                    }
                )
        if ctype == "Distance" and float(constraint.get("value", 0.0)) < 0.0:
            violations.append({"type": "negative_distance", "constraint_id": cid, "message": f"Distance constraint {cid} has a negative value."})
        if ctype == "Angle":
            value = float(constraint.get("value", 0.0))
            if value < 0.0 or value > 180.0:
                violations.append({"type": "invalid_angle_range", "constraint_id": cid, "message": f"Angle constraint {cid} has value {value}, expected [0, 180]."})

    return {
        "valid": not violations,
        "violations": violations,
        "checked_invariants": ["constraint_endpoints_in_distinct_rigid_sets"],
    }


# ---------------------------------------------------------------------------
# Command: repair_gcs_graph
# ---------------------------------------------------------------------------


def tool_repair_gcs_graph(params: dict) -> dict:
    gcs_graph_id = params["gcs_graph_id"]
    target_repairs = params.get("target_repairs", [])
    repair_policy = params.get("repair_policy", "minimal_change")

    try:
        original = load_graph(gcs_graph_id)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    gcs = copy.deepcopy(original)
    edits = []

    def recolor_for_edges(required_edges, reason: str):
        vertices = sorted([g["id"] for g in gcs.get("geometries", [])], key=_sort_key)
        current_count = max(1, len(gcs.get("rigid_sets", [])))
        colors, actual_count, expanded = _assign_rigid_sets_for_edges(
            vertices,
            _unique_edges(required_edges),
            current_count,
            _rng(params.get("seed")),
            assignment="deterministic_balanced",
            allow_new_rigid_sets=True,
        )
        before = {g["id"]: g.get("rigid_set_id") for g in gcs.get("geometries", [])}
        for geometry in gcs.get("geometries", []):
            new_rs = colors[geometry["id"]]
            if geometry.get("rigid_set_id") != new_rs:
                edits.append(
                    {
                        "operation": "move_geometry_rigid_set",
                        "geometry_id": geometry["id"],
                        "old_rigid_set_id": geometry.get("rigid_set_id"),
                        "new_rigid_set_id": new_rs,
                        "reason": reason,
                    }
                )
                geometry["rigid_set_id"] = new_rs
        if expanded:
            edits.append({"operation": "expand_rigid_sets", "old_count": current_count, "new_count": actual_count, "reason": reason})
        _rebuild_rigid_sets(gcs, actual_count)
        return before

    if "fix_constraint_signature" in target_repairs:
        geom_by_id = _geometry_map(gcs)
        for constraint in gcs.get("constraints", []):
            gids = constraint.get("geometry_ids", [])
            if len(gids) < 2 or gids[0] not in geom_by_id or gids[1] not in geom_by_id:
                continue
            g1 = geom_by_id[gids[0]]
            g2 = geom_by_id[gids[1]]
            if not is_valid_constraint_signature(constraint.get("type"), g1.get("type"), g2.get("type")):
                new_type = _first_valid_constraint_type(g1, g2)
                if new_type:
                    edits.append(
                        {
                            "operation": "replace_constraint_type",
                            "constraint_id": constraint["id"],
                            "old_type": constraint.get("type"),
                            "new_type": new_type,
                        }
                    )
                    constraint["type"] = new_type

    if "separate_rigid_sets" in target_repairs or "fix_same_rigid_set_constraints" in target_repairs:
        geom_by_id = _geometry_map(gcs)
        needs_recolor = any(
            not _constraint_has_distinct_rigid_sets(constraint, geom_by_id)
            for constraint in gcs.get("constraints", [])
            if len(constraint.get("geometry_ids", [])) >= 2
        )
        if needs_recolor:
            try:
                recolor_for_edges(_geometry_primal_edges(gcs), "constraints_connect_distinct_rigid_sets")
            except ValueError as exc:
                return {"error": str(exc)}

    if "make_geometry_primal_vertex_biconnected" in target_repairs:
        vertices = sorted([g["id"] for g in gcs.get("geometries", [])], key=_sort_key)
        if len(vertices) < 3:
            return {"error": "At least 3 geometries are required for vertex biconnectivity"}
        existing_edges = _geometry_primal_edges(gcs)
        articulation_points, _, num_components = tarjan_articulation_bcc(vertices, existing_edges)
        if num_components == 1 and not articulation_points:
            repaired_id = params.get("repaired_gcs_graph_id", f"{gcs_graph_id}_repaired")
            gcs["gcs_graph_id"] = repaired_id
            gcs["num_geometries"] = len(gcs.get("geometries", []))
            gcs["num_constraints"] = len(gcs.get("constraints", []))
            gcs["status"] = "repaired"
            save_graph(repaired_id, gcs)
            return {
                "repaired_gcs_graph_id": repaired_id,
                "edits": edits,
                "repair_certificate": {"policy": repair_policy, "post_validation_required": True},
            }
        cycle_edges = [[vertices[i], vertices[(i + 1) % len(vertices)]] for i in range(len(vertices))]
        required_edges = _unique_edges(existing_edges + cycle_edges)
        try:
            recolor_for_edges(required_edges, "make_geometry_primal_vertex_biconnected")
        except ValueError as exc:
            return {"error": str(exc)}
        geom_by_id = _geometry_map(gcs)
        existing = {_canonical_edge(u, v) for u, v in existing_edges}
        next_id = max([c["id"] for c in gcs.get("constraints", [])], default=-1) + 1
        for u, v in cycle_edges:
            edge_key = _canonical_edge(u, v)
            if edge_key in existing:
                continue
            g1 = geom_by_id[u]
            g2 = geom_by_id[v]
            ctype = _first_valid_constraint_type(g1, g2)
            if ctype is None:
                return {"error": f"No valid constraint type for added edge {u}-{v}"}
            constraint = {"id": next_id, "type": ctype, "geometry_ids": [u, v], "value": 0.0}
            gcs.setdefault("constraints", []).append(constraint)
            edits.append(
                {
                    "operation": "add_constraint",
                    "new_constraint_id": next_id,
                    "geometry_ids": [u, v],
                    "constraint_type": ctype,
                    "reason": "add_hamiltonian_cycle_edge_for_biconnectivity",
                }
            )
            existing.add(edge_key)
            next_id += 1

    repaired_id = params.get("repaired_gcs_graph_id", f"{gcs_graph_id}_repaired")
    gcs["gcs_graph_id"] = repaired_id
    gcs["num_geometries"] = len(gcs.get("geometries", []))
    gcs["num_constraints"] = len(gcs.get("constraints", []))
    gcs["status"] = "repaired"
    save_graph(repaired_id, gcs)
    return {
        "repaired_gcs_graph_id": repaired_id,
        "edits": edits,
        "repair_certificate": {"policy": repair_policy, "post_validation_required": True},
    }


# ---------------------------------------------------------------------------
# Command: serialize_gcs_graph
# ---------------------------------------------------------------------------


def tool_serialize_gcs_graph(params: dict) -> dict:
    gcs_graph_id = params["gcs_graph_id"]
    fmt = params.get("format", "custom_text_v1")
    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    if fmt == "json":
        serialization = json.dumps(gcs, indent=2, sort_keys=True)
    elif fmt == "custom_text_v1":
        rigid_sets = sorted(gcs.get("rigid_sets", []), key=lambda rs: rs["id"])
        geometries = sorted(gcs.get("geometries", []), key=lambda g: g["id"])
        constraints = sorted(gcs.get("constraints", []), key=lambda c: c["id"])
        lines = []
        lines.append(str(len(rigid_sets)))
        lines.append(" ".join(str(rs["id"]) for rs in rigid_sets))
        lines.append(str(len(geometries)))
        for geometry in geometries:
            lines.append(f"{geometry['id']} {GEOMETRY_TYPE_MAP[geometry['type']]} {geometry['rigid_set_id']}")
        lines.append(str(len(constraints)))
        for constraint in constraints:
            gids = " ".join(str(gid) for gid in constraint.get("geometry_ids", []))
            lines.append(f"{constraint['id']} {CONSTRAINT_TYPE_MAP[constraint['type']]} {len(constraint.get('geometry_ids', []))} {gids}")
        lines.append("")
        for geometry in geometries:
            values = " ".join(_format_float(v) for v in geometry.get("v", [0.0] * 6))
            lines.append(f"{geometry['id']} {values}")
        lines.append("")
        for constraint in constraints:
            lines.append(f"{constraint['id']} {_format_float(constraint.get('value', 0.0))}")
        serialization = "\n".join(lines)
    else:
        return {"error": f"Unknown format: {fmt}"}

    checksum = hashlib.sha256(serialization.encode("utf-8")).hexdigest()[:16]
    return {"serialization": serialization, "checksum": checksum, "canonical": True, "format": fmt}


def _format_float(value) -> str:
    return f"{float(value):.12g}"


# ---------------------------------------------------------------------------
# Command: generate_graph_report
# ---------------------------------------------------------------------------


def tool_generate_graph_report(params: dict) -> dict:
    gcs_graph_id = params["gcs_graph_id"]
    include = params.get(
        "include",
        [
            "schema_validation",
            "projection_statistics",
            "biconnectivity_certificate",
            "constraint_type_histogram",
            "rigidset_summary",
        ],
    )
    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    vertices = sorted([g["id"] for g in gcs.get("geometries", [])], key=_sort_key)
    edges = _geometry_primal_edges(gcs)
    report = {
        "graph_id": gcs_graph_id,
        "summary": {
            "num_rigid_sets": len(gcs.get("rigid_sets", [])),
            "num_geometries": len(gcs.get("geometries", [])),
            "num_constraints": len(gcs.get("constraints", [])),
        },
    }

    if "schema_validation" in include:
        validation = tool_validate_gcs_schema({"gcs_graph_id": gcs_graph_id})
        report["schema_valid"] = validation.get("valid", False)
        report["schema_violations"] = validation.get("violations", [])
        report["rigid_set_invariant_valid"] = not any(v.get("type") == "constraint_same_rigid_set" for v in validation.get("violations", []))

    if "projection_statistics" in include:
        report["projection_statistics"] = {"num_vertices": len(vertices), "num_edges": len(edges), "projection": "geometry_primal"}

    if "biconnectivity_certificate" in include:
        articulation_points, bcc_list, num_components = tarjan_articulation_bcc(vertices, edges)
        report["geometry_primal_biconnected"] = len(vertices) >= 3 and num_components == 1 and not articulation_points
        report["num_connected_components"] = num_components
        report["articulation_points"] = articulation_points
        report["num_biconnected_components"] = len(bcc_list)

    if "constraint_type_histogram" in include:
        report["constraint_type_histogram"] = dict(sorted(Counter(c["type"] for c in gcs.get("constraints", [])).items()))

    if "rigidset_summary" in include:
        report["rigidset_summary"] = [
            {"id": rs["id"], "num_geometries": len(rs.get("geometry_ids", [])), "geometry_ids": rs.get("geometry_ids", [])}
            for rs in sorted(gcs.get("rigid_sets", []), key=lambda rs: rs["id"])
        ]

    return report


# ---------------------------------------------------------------------------
# Command: assign_geometry_parameters
# ---------------------------------------------------------------------------


def _vec_sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def _vec_add(a, b):
    return [a[i] + b[i] for i in range(3)]


def _vec_scale(a, scale):
    return [a[i] * scale for i in range(3)]


def _vec_len(a):
    return math.sqrt(sum(a[i] * a[i] for i in range(3)))


def _vec_normalize(a):
    length = _vec_len(a)
    if length < 1e-12:
        return [0.0, 0.0, 1.0]
    return [a[i] / length for i in range(3)]


def _vec_dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def _angle_between_vectors(a, b):
    na = _vec_normalize(a)
    nb = _vec_normalize(b)
    cos_value = max(-1.0, min(1.0, _vec_dot(na, nb)))
    return math.degrees(math.acos(cos_value))


def _line_direction(line_v):
    return _vec_sub(line_v[3:6], line_v[:3])


def _plane_normal(plane_v):
    return plane_v[3:6]


def _layout_positions(geometries, layout: str, layout_params: dict, rng: random.Random) -> dict:
    center = layout_params.get("center", [0.0, 0.0, 0.0])
    positions = {}
    if layout == "circular":
        radius = float(layout_params.get("radius", 2.0))
        plane = layout_params.get("plane", "xy")
        n = max(1, len(geometries))
        for index, geometry in enumerate(sorted(geometries, key=lambda g: g["id"])):
            angle = 2.0 * math.pi * index / n
            if plane == "xz":
                pos = [center[0] + radius * math.cos(angle), center[1], center[2] + radius * math.sin(angle)]
            elif plane == "yz":
                pos = [center[0], center[1] + radius * math.cos(angle), center[2] + radius * math.sin(angle)]
            else:
                pos = [center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle), center[2]]
            positions[geometry["id"]] = pos
    elif layout == "random":
        radius = float(layout_params.get("radius", 3.0))
        for geometry in sorted(geometries, key=lambda g: g["id"]):
            positions[geometry["id"]] = [
                center[0] + rng.uniform(-radius, radius),
                center[1] + rng.uniform(-radius, radius),
                center[2] + rng.uniform(-radius, radius),
            ]
    elif layout == "grid":
        spacing = float(layout_params.get("spacing", 2.0))
        cols = max(1, int(math.ceil(math.sqrt(len(geometries)))))
        for index, geometry in enumerate(sorted(geometries, key=lambda g: g["id"])):
            row = index // cols
            col = index % cols
            positions[geometry["id"]] = [center[0] + col * spacing, center[1] - row * spacing, center[2]]
    else:
        raise ValueError(f"Unknown layout: {layout}")
    return positions


def tool_assign_geometry_parameters(params: dict) -> dict:
    gcs_graph_id = params["gcs_graph_id"]
    layout = params.get("layout", "circular")
    layout_params = params.get("layout_params", {})
    rng = _rng(params.get("seed"))

    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    gcs = copy.deepcopy(gcs)
    try:
        positions = _layout_positions(gcs.get("geometries", []), layout, layout_params, rng)
    except ValueError as exc:
        return {"error": str(exc)}

    for geometry in sorted(gcs.get("geometries", []), key=lambda g: g["id"]):
        pos = positions[geometry["id"]]
        if geometry["type"] == "Point":
            geometry["v"] = [pos[0], pos[1], pos[2], 0.0, 0.0, 0.0]
        elif geometry["type"] == "Line":
            direction = _vec_normalize([rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0)])
            half_len = rng.uniform(0.5, 1.5)
            start = _vec_sub(pos, _vec_scale(direction, half_len))
            end = _vec_add(pos, _vec_scale(direction, half_len))
            geometry["v"] = [*start, *end]
        elif geometry["type"] == "Plane":
            normal = _vec_normalize([rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0), rng.uniform(0.3, 1.0)])
            geometry["v"] = [pos[0], pos[1], pos[2], *normal]

    geom_by_id = _geometry_map(gcs)
    for constraint in sorted(gcs.get("constraints", []), key=lambda c: c["id"]):
        gids = constraint.get("geometry_ids", [])
        if len(gids) < 2 or gids[0] not in geom_by_id or gids[1] not in geom_by_id:
            continue
        g1 = geom_by_id[gids[0]]
        g2 = geom_by_id[gids[1]]
        if constraint["type"] == "Distance":
            constraint["value"] = round(_vec_len(_vec_sub(g1["v"][:3], g2["v"][:3])), 6)
        elif constraint["type"] == "Angle":
            if g1["type"] == "Line" and g2["type"] == "Line":
                value = _angle_between_vectors(_line_direction(g1["v"]), _line_direction(g2["v"]))
            elif g1["type"] == "Line" and g2["type"] == "Plane":
                value = abs(90.0 - _angle_between_vectors(_line_direction(g1["v"]), _plane_normal(g2["v"])))
            elif g1["type"] == "Plane" and g2["type"] == "Line":
                value = abs(90.0 - _angle_between_vectors(_plane_normal(g1["v"]), _line_direction(g2["v"])))
            elif g1["type"] == "Plane" and g2["type"] == "Plane":
                value = _angle_between_vectors(_plane_normal(g1["v"]), _plane_normal(g2["v"]))
            else:
                value = rng.uniform(15.0, 75.0)
            constraint["value"] = round(max(0.0, min(180.0, value)), 6)
        else:
            constraint["value"] = 0.0

    gcs["status"] = "parameters_assigned"
    save_graph(gcs_graph_id, gcs)
    return {
        "gcs_graph_id": gcs_graph_id,
        "status": "parameters_assigned",
        "num_geometries": len(gcs.get("geometries", [])),
        "num_constraints": len(gcs.get("constraints", [])),
    }


# ---------------------------------------------------------------------------
# Command: explore_scene_space
# ---------------------------------------------------------------------------


def _as_int_list(value, default: list[int]) -> list[int]:
    if value is None:
        return list(default)
    if isinstance(value, int):
        return [int(value)]
    return [int(item) for item in value]


def _as_str_list(value, default: list[str]) -> list[str]:
    if value is None:
        return list(default)
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def _extra_edge_values(value) -> list[int]:
    if value is None:
        return [0, 1, 2, 3]
    if isinstance(value, int):
        return [int(value)]
    if isinstance(value, list) and len(value) == 2 and all(isinstance(item, (int, float)) for item in value):
        lo = int(value[0])
        hi = int(value[1])
        if hi < lo:
            raise ValueError("extra_edge_range upper bound must be >= lower bound")
        return list(range(lo, hi + 1))
    return [int(item) for item in value]


def _default_exploration_request(params: dict) -> dict:
    seed = int(params.get("seed", 0))
    exploration_id = _safe_store_id(params.get("exploration_id", f"exploration_{seed}"), "exploration_id")
    budget = params.get("budget", {})
    topology_policy = params.get("topology_policy", {})
    gcs_policy = params.get("gcs_policy", {})
    parameter_policy = params.get("parameter_policy", {})
    write_policy = params.get("write_policy", {})

    request = {
        "exploration_id": exploration_id,
        "seed": seed,
        "budget": {
            "max_candidates": int(budget.get("max_candidates", 32)),
            "max_accepts": int(budget.get("max_accepts", 8)),
            "max_seconds": float(budget.get("max_seconds", 0.0)),
        },
        "topology_policy": {
            "vertex_counts": _as_int_list(topology_policy.get("vertex_counts"), [3, 4, 5, 8]),
            "methods": _as_str_list(topology_policy.get("methods"), ["cycle_plus_chords", "ear_decomposition"]),
            "extra_edge_values": _extra_edge_values(topology_policy.get("extra_edge_range")),
            "require_vertex_biconnected": bool(topology_policy.get("require_vertex_biconnected", True)),
        },
        "gcs_policy": {
            "geometry_types": _as_str_list(gcs_policy.get("geometry_types"), list(GEOMETRY_TYPES)),
            "constraint_types": _as_str_list(gcs_policy.get("constraint_types"), list(CONSTRAINT_TYPES)),
            "rigid_set_counts": _as_int_list(gcs_policy.get("rigid_set_counts"), [2, 3]),
            "require_cross_rigid_set_constraints": bool(gcs_policy.get("require_cross_rigid_set_constraints", True)),
        },
        "parameter_policy": {
            "layouts": _as_str_list(parameter_policy.get("layouts"), ["circular", "grid", "random"]),
            "avoid_degenerate_geometry": bool(parameter_policy.get("avoid_degenerate_geometry", True)),
            "value_tolerance": float(parameter_policy.get("value_tolerance", 1e-9)),
        },
        "coverage_goals": _as_str_list(
            params.get("coverage_goals"),
            [
                "all_geometry_types",
                "all_constraint_types",
                "mixed_rigid_sets",
                "biconnected_geometry_primal",
                "invalid_signature_negative_case",
                "same_rigid_set_negative_case",
            ],
        ),
        "gate_profile": params.get("gate_profile", "local_only"),
        "public_gate_config": params.get("public_gate_config", {}),
        "write_policy": {
            "store": write_policy.get("store", "scratch"),
            "keep_rejected": bool(write_policy.get("keep_rejected", True)),
            "promote": bool(write_policy.get("promote", False)),
        },
        "allow_unsupported_gates": bool(params.get("allow_unsupported_gates", False)),
    }

    if request["budget"]["max_candidates"] < 1:
        raise ValueError("budget.max_candidates must be >= 1")
    if request["budget"]["max_accepts"] < 1:
        raise ValueError("budget.max_accepts must be >= 1")
    if any(v < 3 for v in request["topology_policy"]["vertex_counts"]):
        raise ValueError("topology_policy.vertex_counts must all be >= 3")
    unknown_geometry = [g for g in request["gcs_policy"]["geometry_types"] if g not in GEOMETRY_TYPES]
    if unknown_geometry:
        raise ValueError(f"Unknown geometry type(s): {unknown_geometry}")
    unknown_constraints = [c for c in request["gcs_policy"]["constraint_types"] if c not in CONSTRAINT_TYPES]
    if unknown_constraints:
        raise ValueError(f"Unknown constraint type(s): {unknown_constraints}")
    if request["write_policy"]["store"] != "scratch":
        raise ValueError("write_policy.store currently supports only 'scratch'")
    if request["gate_profile"] not in {"local_only", "local_plus_public_smoke", "promotion"}:
        raise ValueError("gate_profile must be one of local_only, local_plus_public_smoke, or promotion")
    return request


def _candidate_seed(seed: int, candidate_index: int, offset: int) -> int:
    return (int(seed) * 100_003 + candidate_index * 101 + offset) % 2_147_483_647


def _geometry_distribution(geometry_types: list[str]) -> dict:
    if not geometry_types:
        return {}
    weight = 1.0 / len(geometry_types)
    return {gtype: weight for gtype in geometry_types}


def _endpoint_signature(g1: dict, g2: dict) -> str:
    return "-".join(sorted([g1.get("type", "?"), g2.get("type", "?")]))


def _candidate_record(gcs: dict, report: dict, gates: list[dict], serialization: dict, variant: str) -> dict:
    geom_by_id = _geometry_map(gcs)
    geometry_hist = Counter(g.get("type") for g in gcs.get("geometries", []))
    constraint_hist = Counter(c.get("type") for c in gcs.get("constraints", []))
    signature_hist = Counter()
    for constraint in gcs.get("constraints", []):
        gids = constraint.get("geometry_ids", [])
        if len(gids) >= 2 and gids[0] in geom_by_id and gids[1] in geom_by_id:
            signature_hist[_endpoint_signature(geom_by_id[gids[0]], geom_by_id[gids[1]])] += 1
    return {
        "variant": variant,
        "num_geometries": len(gcs.get("geometries", [])),
        "num_constraints": len(gcs.get("constraints", [])),
        "num_rigid_sets": len(gcs.get("rigid_sets", [])),
        "geometry_types": dict(sorted(geometry_hist.items())),
        "constraint_types": dict(sorted(constraint_hist.items())),
        "endpoint_signatures": dict(sorted(signature_hist.items())),
        "schema_valid": bool(report.get("schema_valid", False)),
        "geometry_primal_biconnected": bool(report.get("geometry_primal_biconnected", False)),
        "gates": gates,
        "digest": _sha256_text(serialization.get("serialization", "")),
    }


def _make_gate(gate_id: str, status: str, reason_code: str | None = None, evidence=None, artifact_ids=None) -> dict:
    return {
        "gate_id": gate_id,
        "status": status,
        "reason_code": reason_code,
        "evidence": evidence or {},
        "artifact_ids": artifact_ids or [],
        "duration_ms": 0,
    }


def _canonical_public_scene_text(scene: dict) -> str:
    return promotion_adapters.canonical_public_scene_text(scene)


def _public_scene_root() -> str:
    return promotion_adapters.public_scene_root(STORE_DIR)


def _public_scene_path(public_scene_id: str) -> str:
    return promotion_adapters.public_scene_path(STORE_DIR, public_scene_id)


def _solver_scene_from_gcs(gcs: dict) -> dict:
    return promotion_adapters.solver_scene_from_gcs(gcs)


def _write_public_scene(gcs_graph_id: str) -> dict:
    gcs = load_graph(gcs_graph_id)
    return promotion_adapters.write_public_scene(STORE_DIR, gcs_graph_id, gcs)


def _validate_public_scene_kernel(scene: dict) -> tuple[bool, list[dict]]:
    return promotion_adapters.validate_public_scene_kernel(scene)


def _normalize_solver_command(public_gate_config: dict | None) -> list[str]:
    return promotion_adapters.normalize_solver_command(public_gate_config, DEFAULT_GCS_EXE)


def _command_available(command: list[str]) -> bool:
    return promotion_adapters.command_available(command)


def _trim_lines(text: str, limit: int = 40) -> list[str]:
    return promotion_adapters.trim_lines(text, limit)


def _run_solver_smoke(scene_path: str, public_gate_config: dict | None) -> dict:
    return promotion_adapters.run_solver_smoke(scene_path, public_gate_config, REPO_ROOT, DEFAULT_GCS_EXE)


def _runtime_public_gates(smoke: dict, unavailable_status: str) -> list[dict]:
    if not smoke.get("available"):
        evidence = {
            "command": smoke.get("command", []),
            "stderr_lines": smoke.get("stderr_lines", []),
            "message": "Set GCS_EXE or public_gate_config.solver_command to enable CLI public gates.",
        }
        return [
            _make_gate("runtime_smoke", unavailable_status, "runtime_smoke_failed", evidence),
            _make_gate("diagnostics_evidence", unavailable_status, "diagnostics_evidence_failed", evidence),
        ]

    runtime_passed = smoke.get("exit_code") == 0
    output = "\n".join(smoke.get("stdout_lines", []) + smoke.get("stderr_lines", []))
    diagnostics_passed = runtime_passed and "diagnostics" in output and "Status:" in output
    return [
        _make_gate(
            "runtime_smoke",
            "passed" if runtime_passed else "failed",
            None if runtime_passed else "runtime_smoke_failed",
            smoke,
        ),
        _make_gate(
            "diagnostics_evidence",
            "passed" if diagnostics_passed else "failed",
            None if diagnostics_passed else "diagnostics_evidence_failed",
            {
                "status_line_present": "Status:" in output,
                "diagnostics_line_present": "diagnostics" in output,
                "stdout_lines": smoke.get("stdout_lines", []),
                "stderr_lines": smoke.get("stderr_lines", []),
            },
        ),
    ]


def _public_adapter_gates(gcs_graph_id: str,
                          projection: dict,
                          gate_profile: str,
                          allow_unsupported: bool,
                          public_gate_config: dict | None) -> list[dict]:
    public_scene = _write_public_scene(gcs_graph_id)
    scene_text = _canonical_public_scene_text(public_scene["scene"])
    round_trip = json.loads(scene_text)
    round_trip_digest = _sha256_text(_canonical_public_scene_text(round_trip))
    kernel_valid, kernel_issues = _validate_public_scene_kernel(round_trip)
    unavailable_status = "skipped" if gate_profile == "local_plus_public_smoke" or allow_unsupported else "unsupported"
    smoke = _run_solver_smoke(public_scene["path"], public_gate_config)

    gates = [
        _make_gate(
            "scene_io_round_trip",
            "passed" if round_trip_digest == public_scene["digest"] else "failed",
            None if round_trip_digest == public_scene["digest"] else "io_round_trip_failed",
            {
                "public_scene_id": public_scene["public_scene_id"],
                "path": public_scene["path"],
                "digest": public_scene["digest"],
                "round_trip_digest": round_trip_digest,
                "entity_count": public_scene["entity_count"],
                "constraint_count": public_scene["constraint_count"],
            },
            [public_scene["public_scene_id"]],
        ),
        _make_gate(
            "kernel_validation",
            "passed" if kernel_valid else "failed",
            None if kernel_valid else "kernel_validation_failed",
            {"issues": kernel_issues},
            [public_scene["public_scene_id"]],
        ),
        _make_gate(
            "viewer_projection",
            "passed" if "error" not in projection else "failed",
            None if "error" not in projection else "viewer_projection_failed",
            {
                "num_vertices": len(projection.get("vertices", [])),
                "num_edges": len(projection.get("edges", [])),
            },
            [projection.get("graph_id") or projection.get("projected_graph_id") or "geometry_primal"],
        ),
    ]
    gates.extend(_runtime_public_gates(smoke, unavailable_status))
    return gates


def _run_candidate_gates(gcs_graph_id: str,
                         projection_id: str,
                         gate_profile: str,
                         allow_unsupported: bool = False,
                         public_gate_config: dict | None = None) -> tuple[list[dict], dict, dict, dict]:
    validation = tool_validate_gcs_schema({"gcs_graph_id": gcs_graph_id})
    projection = tool_project_gcs_graph(
        {
            "gcs_graph_id": gcs_graph_id,
            "projection": "geometry_primal",
            "projected_graph_id": projection_id,
        }
    )
    biconnectivity = tool_check_vertex_biconnected({"projected_graph_id": projection_id})
    report = tool_generate_graph_report({"gcs_graph_id": gcs_graph_id})
    serialization = tool_serialize_gcs_graph({"gcs_graph_id": gcs_graph_id, "format": "json"})

    gates = [
        _make_gate(
            "local_schema_validation",
            "passed" if validation.get("valid") else "failed",
            None if validation.get("valid") else _first_violation_reason(validation),
            {"violations": validation.get("violations", [])},
            [gcs_graph_id],
        ),
        _make_gate(
            "geometry_primal_projection",
            "passed" if "error" not in projection else "failed",
            projection.get("error"),
            {"num_vertices": len(projection.get("vertices", [])), "num_edges": len(projection.get("edges", []))},
            [projection_id],
        ),
        _make_gate(
            "geometry_primal_biconnectivity",
            "passed" if biconnectivity.get("is_vertex_biconnected") else "failed",
            None if biconnectivity.get("is_vertex_biconnected") else _topology_failure_reason(biconnectivity),
            {
                "articulation_points": biconnectivity.get("articulation_points", []),
                "num_connected_components": biconnectivity.get("num_connected_components"),
            },
            [projection_id],
        ),
        _make_gate(
            "canonical_serialization",
            "passed" if serialization.get("canonical") else "failed",
            None if serialization.get("canonical") else serialization.get("error", "serialization_failed"),
            {"checksum": serialization.get("checksum"), "format": serialization.get("format")},
            [gcs_graph_id],
        ),
    ]

    if gate_profile in {"local_plus_public_smoke", "promotion"}:
        gates.extend(
            _public_adapter_gates(
                gcs_graph_id,
                projection,
                gate_profile,
                allow_unsupported,
                public_gate_config,
            )
        )
    return gates, report, projection, serialization


def _first_violation_reason(validation: dict) -> str:
    violations = validation.get("violations", [])
    if not violations:
        return "invalid_request"
    reason = violations[0].get("type", "invalid_request")
    return reason if reason in FAILURE_REASON_CODES else "invalid_request"


def _topology_failure_reason(biconnectivity: dict) -> str:
    if int(biconnectivity.get("num_connected_components") or 0) != 1:
        return "topology_not_connected"
    if biconnectivity.get("articulation_points"):
        return "topology_has_articulation"
    return "topology_has_articulation"


def _candidate_failure_reason(gates: list[dict]) -> str:
    for gate in gates:
        if gate["status"] == "failed":
            reason = gate.get("reason_code") or "invalid_request"
            return reason if reason in FAILURE_REASON_CODES else "invalid_request"
    for gate in gates:
        if gate["status"] == "unsupported":
            return "promotion_gate_unsupported"
    return "invalid_request"


def _coverage_from_records(accepted_records: list[dict], rejected_records: list[dict], request: dict) -> dict:
    goals = set(request["coverage_goals"])
    requested_geometry = set(request["gcs_policy"]["geometry_types"])
    requested_constraints = set(request["gcs_policy"]["constraint_types"])
    geometry_hist = Counter()
    constraint_hist = Counter()
    signature_hist = Counter()
    rigid_set_hist = Counter()
    topology_size_hist = Counter()
    gate_status_hist = Counter()
    rejection_hist = Counter()

    for record in accepted_records:
        geometry_hist.update(record.get("geometry_types", {}))
        constraint_hist.update(record.get("constraint_types", {}))
        signature_hist.update(record.get("endpoint_signatures", {}))
        rigid_set_hist[str(record.get("num_rigid_sets"))] += 1
        topology_size_hist[str(record.get("num_geometries"))] += 1
        for gate in record.get("gates", []):
            gate_status_hist[f"{gate['gate_id']}:{gate['status']}"] += 1
    for record in rejected_records:
        reason = record.get("reason_code", "invalid_request")
        rejection_hist[reason] += 1

    accepted_geometry = set(geometry_hist)
    accepted_constraints = set(constraint_hist)
    satisfied = set()
    if "all_geometry_types" in goals and requested_geometry.issubset(accepted_geometry):
        satisfied.add("all_geometry_types")
    if "all_constraint_types" in goals and requested_constraints.issubset(accepted_constraints):
        satisfied.add("all_constraint_types")
    if "mixed_rigid_sets" in goals and any(int(key) > 1 for key in rigid_set_hist):
        satisfied.add("mixed_rigid_sets")
    if "biconnected_geometry_primal" in goals and any(r.get("geometry_primal_biconnected") for r in accepted_records):
        satisfied.add("biconnected_geometry_primal")
    if "invalid_signature_negative_case" in goals and rejection_hist.get("invalid_constraint_signature"):
        satisfied.add("invalid_signature_negative_case")
    if "same_rigid_set_negative_case" in goals and rejection_hist.get("constraint_same_rigid_set"):
        satisfied.add("same_rigid_set_negative_case")
    if "io_round_trip_candidate" in goals:
        io_passed = any(
            gate.get("gate_id") == "scene_io_round_trip" and gate.get("status") == "passed"
            for record in accepted_records
            for gate in record.get("gates", [])
        )
        if io_passed:
            satisfied.add("io_round_trip_candidate")

    return {
        "satisfied_goals": sorted(satisfied),
        "missing_goals": sorted(goals - satisfied),
        "histograms": {
            "geometry_types": dict(sorted(geometry_hist.items())),
            "constraint_types": dict(sorted(constraint_hist.items())),
            "endpoint_signatures": dict(sorted(signature_hist.items())),
            "rigid_set_counts": dict(sorted(rigid_set_hist.items())),
            "topology_sizes": dict(sorted(topology_size_hist.items())),
            "gate_statuses": dict(sorted(gate_status_hist.items())),
            "rejection_reasons": dict(sorted(rejection_hist.items())),
        },
    }


def _candidate_score(record: dict, before_coverage: dict, after_coverage: dict) -> float:
    before_goals = set(before_coverage.get("satisfied_goals", []))
    after_goals = set(after_coverage.get("satisfied_goals", []))
    new_goals = len(after_goals - before_goals)
    geometry_diversity = len(record.get("geometry_types", {}))
    constraint_diversity = len(record.get("constraint_types", {}))
    simplicity = 1.0 / max(1, int(record.get("num_constraints", 1)))
    return round(new_goals * 10.0 + geometry_diversity + constraint_diversity + simplicity, 6)


def _save_candidate_artifacts(exploration_id: str, candidate_id: str, artifacts: dict, provenance: dict, report: dict, projection: dict) -> None:
    root = _candidate_root(exploration_id, candidate_id)
    _write_json_file(os.path.join(root, "provenance.json"), provenance)
    _write_json_file(os.path.join(root, "report.json"), report)
    _write_json_file(os.path.join(root, "geometry_primal.json"), projection)
    role_names = {
        "skeleton_graph_id": "skeleton",
        "gcs_graph_id": "gcs",
        "skeleton": "skeleton",
        "gcs": "gcs",
    }
    for role, graph_id in artifacts.items():
        if not graph_id or role == "projection_ids":
            continue
        if isinstance(graph_id, list):
            continue
        file_role = role_names.get(role, role)
        try:
            _write_json_file(os.path.join(root, f"{file_role}.json"), load_graph(graph_id))
        except FileNotFoundError:
            pass


def _invalid_constraint_type_for(g1: dict, g2: dict) -> str | None:
    for ctype in CONSTRAINT_TYPES:
        if not is_valid_constraint_signature(ctype, g1.get("type"), g2.get("type")):
            return ctype
    return None


def _make_negative_candidate(base_gcs_id: str, negative_gcs_id: str, variant: str) -> dict:
    base = load_graph(base_gcs_id)
    gcs = copy.deepcopy(base)
    gcs["gcs_graph_id"] = negative_gcs_id
    gcs["status"] = variant
    geom_by_id = _geometry_map(gcs)
    if variant == "invalid_signature_negative_case":
        for constraint in sorted(gcs.get("constraints", []), key=lambda c: c["id"]):
            gids = constraint.get("geometry_ids", [])
            if len(gids) < 2 or gids[0] not in geom_by_id or gids[1] not in geom_by_id:
                continue
            invalid = _invalid_constraint_type_for(geom_by_id[gids[0]], geom_by_id[gids[1]])
            if invalid:
                constraint["type"] = invalid
                save_graph(negative_gcs_id, gcs)
                return gcs
    elif variant == "same_rigid_set_negative_case":
        for constraint in sorted(gcs.get("constraints", []), key=lambda c: c["id"]):
            gids = constraint.get("geometry_ids", [])
            if len(gids) < 2 or gids[0] not in geom_by_id or gids[1] not in geom_by_id:
                continue
            geom_by_id[gids[1]]["rigid_set_id"] = geom_by_id[gids[0]]["rigid_set_id"]
            _rebuild_rigid_sets(gcs)
            save_graph(negative_gcs_id, gcs)
            return gcs
    raise ValueError(f"Could not create negative candidate variant {variant}")


def _build_positive_candidate(request: dict, candidate_index: int, combo: dict) -> tuple[dict, dict, dict, dict, dict, list[dict]]:
    exploration_id = request["exploration_id"]
    candidate_id = f"{exploration_id}_c{candidate_index:04d}"
    skeleton_id = f"{candidate_id}_skel"
    gcs_id = f"{candidate_id}_gcs"
    projection_id = f"{candidate_id}_geom_primal"
    seed = request["seed"]
    seed_path = {
        "exploration_seed": seed,
        "topology_seed": _candidate_seed(seed, candidate_index, 1),
        "lift_seed": _candidate_seed(seed, candidate_index, 2),
        "parameter_seed": _candidate_seed(seed, candidate_index, 3),
    }

    skeleton = tool_generate_skeleton_graph(
        {
            "graph_id": skeleton_id,
            "num_vertices": combo["num_vertices"],
            "method": combo["method"],
            "extra_edges": combo["extra_edges"],
            "seed": seed_path["topology_seed"],
        }
    )
    if "error" in skeleton:
        raise ValueError(skeleton["error"])

    lift = tool_lift_skeleton_to_gcs(
        {
            "skeleton_graph_id": skeleton_id,
            "gcs_graph_id": gcs_id,
            "seed": seed_path["lift_seed"],
            "geometry_type_policy": {
                "allowed_types": request["gcs_policy"]["geometry_types"],
                "distribution": _geometry_distribution(request["gcs_policy"]["geometry_types"]),
            },
            "constraint_type_policy": {
                "allowed_types": request["gcs_policy"]["constraint_types"],
                "respect_type_signature": True,
            },
            "rigid_set_policy": {
                "num_rigid_sets": combo["num_rigid_sets"],
                "assignment": "random_balanced",
                "allow_new_rigid_sets": True,
            },
        }
    )
    if "error" in lift:
        raise ValueError(lift["error"])

    assigned = tool_assign_geometry_parameters(
        {
            "gcs_graph_id": gcs_id,
            "layout": combo["layout"],
            "seed": seed_path["parameter_seed"],
        }
    )
    if "error" in assigned:
        raise ValueError(assigned["error"])

    gates, report, projection, serialization = _run_candidate_gates(
        gcs_id,
        projection_id,
        request["gate_profile"],
        request["allow_unsupported_gates"],
        request.get("public_gate_config", {}),
    )
    gcs = load_graph(gcs_id)
    artifacts = {
        "skeleton": skeleton_id,
        "gcs": gcs_id,
        "projection_ids": [projection_id],
    }
    provenance = {
        "candidate_id": candidate_id,
        "parent_exploration_id": exploration_id,
        "variant": "positive",
        "seed_path": seed_path,
        "artifacts": {
            "skeleton_graph_id": skeleton_id,
            "gcs_graph_id": gcs_id,
            "projection_ids": [projection_id],
        },
        "policies": {
            "topology": combo,
            "gcs_policy": request["gcs_policy"],
            "parameter_policy": {"layout": combo["layout"]},
        },
        "digest": _sha256_text(serialization.get("serialization", "")),
    }
    return gcs, report, projection, serialization, provenance, gates


def _build_candidate_combos(request: dict) -> list[dict]:
    topology = request["topology_policy"]
    gcs_policy = request["gcs_policy"]
    parameter = request["parameter_policy"]
    combos = []
    for num_vertices in sorted(topology["vertex_counts"]):
        for method in sorted(topology["methods"]):
            for extra_edges in sorted(topology["extra_edge_values"]):
                for num_rigid_sets in sorted(gcs_policy["rigid_set_counts"]):
                    for layout in sorted(parameter["layouts"]):
                        combos.append(
                            {
                                "num_vertices": num_vertices,
                                "method": method,
                                "extra_edges": extra_edges,
                                "num_rigid_sets": num_rigid_sets,
                                "layout": layout,
                            }
                        )
    rng = _rng(request["seed"])
    rng.shuffle(combos)
    return combos


def tool_explore_scene_space(params: dict) -> dict:
    try:
        request = _default_exploration_request(params)
    except ValueError as exc:
        return {"status": "failed", "reason_code": "invalid_request", "error": str(exc)}

    exploration_id = request["exploration_id"]
    root = _exploration_root(exploration_id)
    trace_path = os.path.join(root, "trace.jsonl")
    os.makedirs(root, exist_ok=True)
    if os.path.exists(trace_path):
        os.remove(trace_path)
    _write_json_file(os.path.join(root, "request.json"), request)

    accepted = []
    accepted_records = []
    rejected = []
    rejected_records = []
    attempted = 0
    event_index = 0
    start = time.monotonic()
    stop_reason = "search_exhausted"
    combos = _build_candidate_combos(request)

    def trace(event_type: str, candidate_id: str | None, payload: dict) -> None:
        nonlocal event_index
        event = {
            "event_index": event_index,
            "event_type": event_type,
            "candidate_id": candidate_id,
            "payload": payload,
        }
        event_index += 1
        _append_trace(trace_path, event)

    def should_stop() -> str | None:
        if len(accepted) >= request["budget"]["max_accepts"]:
            return "max_accepts"
        if attempted >= request["budget"]["max_candidates"]:
            return "max_candidates"
        max_seconds = request["budget"]["max_seconds"]
        if max_seconds > 0.0 and (time.monotonic() - start) >= max_seconds:
            return "max_seconds"
        return None

    for combo_index, combo in enumerate(combos):
        reason = should_stop()
        if reason:
            stop_reason = reason
            break

        candidate_index = attempted
        candidate_id = f"{exploration_id}_c{candidate_index:04d}"
        attempted += 1
        trace("candidate_started", candidate_id, {"combo": combo})
        try:
            gcs, report, projection, serialization, provenance, gates = _build_positive_candidate(request, candidate_index, combo)
            record = _candidate_record(gcs, report, gates, serialization, "positive")
            before_coverage = _coverage_from_records(accepted_records, rejected_records, request)
            candidate_after = accepted_records + [record] if record["schema_valid"] and record["geometry_primal_biconnected"] else accepted_records
            after_coverage = _coverage_from_records(candidate_after, rejected_records, request)
            score = _candidate_score(record, before_coverage, after_coverage)
            provenance["reports"] = {"graph_report": report, "gates": gates}
            _save_candidate_artifacts(exploration_id, candidate_id, provenance["artifacts"], provenance, report, projection)
            if record["schema_valid"] and record["geometry_primal_biconnected"] and (
                set(after_coverage["satisfied_goals"]) - set(before_coverage["satisfied_goals"]) or not accepted
            ):
                record["score"] = score
                accepted_records.append(record)
                accepted.append(
                    {
                        "candidate_id": candidate_id,
                        "gcs_graph_id": provenance["artifacts"]["gcs_graph_id"],
                        "score": score,
                        "schema_valid": True,
                        "geometry_primal_biconnected": True,
                        "digest": record["digest"],
                        "coverage_contributions": sorted(set(after_coverage["satisfied_goals"]) - set(before_coverage["satisfied_goals"])),
                    }
                )
                trace("candidate_accepted", candidate_id, {"score": score})
            else:
                reason_code = _candidate_failure_reason(record["gates"]) if not record["schema_valid"] else "no_coverage_gain"
                rejected_record = {
                    "candidate_id": candidate_id,
                    "reason_code": reason_code,
                    "evidence_ids": [f"{candidate_id}_report"],
                    "variant": "positive",
                }
                rejected.append(rejected_record)
                rejected_records.append(rejected_record)
                trace("candidate_rejected", candidate_id, {"reason_code": reason_code})

            requested_negative = []
            current_coverage = _coverage_from_records(accepted_records, rejected_records, request)
            if "invalid_signature_negative_case" in current_coverage["missing_goals"]:
                requested_negative.append("invalid_signature_negative_case")
            if "same_rigid_set_negative_case" in current_coverage["missing_goals"]:
                requested_negative.append("same_rigid_set_negative_case")
            for variant in requested_negative:
                reason = should_stop()
                if reason:
                    stop_reason = reason
                    break
                negative_index = attempted
                negative_id = f"{exploration_id}_c{negative_index:04d}"
                attempted += 1
                negative_gcs_id = f"{negative_id}_gcs"
                negative_projection_id = f"{negative_id}_geom_primal"
                trace("candidate_started", negative_id, {"variant": variant, "source_candidate_id": candidate_id})
                negative_gcs = _make_negative_candidate(provenance["artifacts"]["gcs_graph_id"], negative_gcs_id, variant)
                gates, negative_report, negative_projection, negative_serialization = _run_candidate_gates(
                    negative_gcs_id,
                    negative_projection_id,
                    request["gate_profile"],
                    request["allow_unsupported_gates"],
                    request.get("public_gate_config", {}),
                )
                reason_code = _candidate_failure_reason(gates)
                negative_provenance = {
                    "candidate_id": negative_id,
                    "parent_exploration_id": exploration_id,
                    "variant": variant,
                    "source_candidate_id": candidate_id,
                    "seed_path": provenance["seed_path"],
                    "artifacts": {
                        "skeleton_graph_id": provenance["artifacts"]["skeleton_graph_id"],
                        "gcs_graph_id": negative_gcs_id,
                        "projection_ids": [negative_projection_id],
                    },
                    "policies": {"negative_variant": variant},
                    "reports": {"graph_report": negative_report, "gates": gates},
                    "digest": _sha256_text(negative_serialization.get("serialization", "")),
                }
                if request["write_policy"]["keep_rejected"]:
                    _save_candidate_artifacts(
                        exploration_id,
                        negative_id,
                        {"gcs": negative_gcs_id, "projection_ids": [negative_projection_id]},
                        negative_provenance,
                        negative_report,
                        negative_projection,
                    )
                rejected_record = {
                    "candidate_id": negative_id,
                    "reason_code": reason_code,
                    "evidence_ids": [f"{negative_id}_report"],
                    "variant": variant,
                }
                rejected.append(rejected_record)
                rejected_records.append(rejected_record)
                trace("candidate_rejected", negative_id, {"reason_code": reason_code, "variant": variant})
        except Exception as exc:
            rejected_record = {
                "candidate_id": candidate_id,
                "reason_code": "invalid_request",
                "evidence_ids": [f"{candidate_id}_exception"],
                "variant": "positive",
                "message": str(exc),
            }
            rejected.append(rejected_record)
            rejected_records.append(rejected_record)
            trace("candidate_rejected", candidate_id, {"reason_code": "invalid_request", "message": str(exc)})

        if stop_reason != "search_exhausted":
            break
    else:
        stop_reason = "search_exhausted"

    coverage = _coverage_from_records(accepted_records, rejected_records, request)
    if accepted and rejected:
        status = "accepted_with_rejections"
    elif accepted:
        status = "accepted"
    elif rejected:
        status = "rejected_only"
    else:
        status = "no_candidates_accepted"
    result = {
        "exploration_id": exploration_id,
        "status": status,
        "seed": request["seed"],
        "stop_reason": stop_reason,
        "summary": {
            "attempted": attempted,
            "accepted": len(accepted),
            "rejected": len(rejected),
        },
        "coverage": coverage,
        "accepted_candidates": accepted,
        "rejected_candidates": rejected,
        "trace_id": f"{exploration_id}_trace",
    }
    if request["write_policy"]["promote"]:
        result["promotion_results"] = [
            tool_promote_candidate(
                {
                    "exploration_id": exploration_id,
                    "candidate_id": candidate["candidate_id"],
                    "promotion_id": f"{candidate['candidate_id']}_promotion",
                    "gate_profile": request["gate_profile"],
                    "allow_unsupported_gates": request["allow_unsupported_gates"],
                    "public_gate_config": request.get("public_gate_config", {}),
                }
            )
            for candidate in accepted
        ]
    _write_json_file(os.path.join(root, "result.json"), result)
    trace("exploration_finished", None, {"status": status, "stop_reason": stop_reason, "summary": result["summary"]})
    return result


# ---------------------------------------------------------------------------
# Command: promote_candidate
# ---------------------------------------------------------------------------


def _load_candidate_provenance(exploration_id: str, candidate_id: str) -> dict:
    path = os.path.join(_candidate_root(exploration_id, candidate_id), "provenance.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Candidate '{candidate_id}' not found for exploration '{exploration_id}'")
    return _read_json_file(path)


def tool_promote_candidate(params: dict) -> dict:
    try:
        exploration_id = _safe_store_id(params["exploration_id"], "exploration_id")
        candidate_id = _safe_store_id(params["candidate_id"], "candidate_id")
        promotion_id = _safe_store_id(params.get("promotion_id", f"{candidate_id}_promotion"), "promotion_id")
    except (KeyError, ValueError) as exc:
        return {"status": "failed", "reason_code": "invalid_request", "error": str(exc)}

    gate_profile = params.get("gate_profile", "promotion")
    allow_unsupported = bool(params.get("allow_unsupported_gates", False))
    copy_to_fixtures = bool(params.get("copy_to_fixtures", False))
    public_gate_config = dict(params.get("public_gate_config", {}))
    if "gcs_exe" in params:
        public_gate_config["gcs_exe"] = params["gcs_exe"]
    if "solver_command" in params:
        public_gate_config["solver_command"] = params["solver_command"]

    try:
        provenance = _load_candidate_provenance(exploration_id, candidate_id)
        gcs_graph_id = provenance["artifacts"]["gcs_graph_id"]
        if not os.path.exists(_store_path(gcs_graph_id)):
            nested_gcs_path = os.path.join(_candidate_root(exploration_id, candidate_id), "gcs.json")
            if os.path.exists(nested_gcs_path):
                save_graph(gcs_graph_id, _read_json_file(nested_gcs_path))
        projection_id = f"{candidate_id}_promotion_geom_primal"
        gates, report, projection, json_serialization = _run_candidate_gates(
            gcs_graph_id,
            projection_id,
            gate_profile,
            allow_unsupported,
            public_gate_config,
        )
        text_serialization = tool_serialize_gcs_graph({"gcs_graph_id": gcs_graph_id, "format": "custom_text_v1"})
        public_scene = _solver_scene_from_gcs(load_graph(gcs_graph_id))
    except Exception as exc:
        return {"status": "failed", "reason_code": "invalid_request", "error": str(exc)}

    blocking_gate = next((gate for gate in gates if gate["status"] in {"failed", "unsupported"}), None)
    status = "promotion_package_written" if blocking_gate is None else "promotion_blocked"
    reason_code = None if blocking_gate is None else (blocking_gate.get("reason_code") or "promotion_gate_unsupported")
    package = {
        "promotion_id": promotion_id,
        "status": status,
        "reason_code": reason_code,
        "source": {
            "exploration_id": exploration_id,
            "candidate_id": candidate_id,
            "gcs_graph_id": gcs_graph_id,
        },
        "candidate_provenance": provenance,
        "local_validation_report": report,
        "gate_reports": gates,
        "canonical_serialization": {
            "json_checksum": json_serialization.get("checksum"),
            "text_checksum": text_serialization.get("checksum"),
            "json_digest": _sha256_text(json_serialization.get("serialization", "")),
            "text_digest": _sha256_text(text_serialization.get("serialization", "")),
            "public_scene_digest": _sha256_text(_canonical_public_scene_text(public_scene)),
        },
        "fixture_metadata_proposal": {
            "fixture_id": candidate_id,
            "generator": "tools.scene_generation.explore_scene_space",
            "schema": "scene-generation-promotion-v1",
        },
        "known_unsupported_gates": [gate["gate_id"] for gate in gates if gate["status"] == "unsupported"],
    }
    root = _promotion_root(promotion_id)
    _write_json_file(os.path.join(root, "package.json"), package)
    _write_json_file(os.path.join(root, "geometry_primal.json"), projection)
    _write_json_file(os.path.join(root, "scene.json"), load_graph(gcs_graph_id))
    _write_json_file(os.path.join(root, "public_scene.gcs.json"), public_scene)

    copied_fixture_path = None
    if copy_to_fixtures and status == "promotion_package_written":
        fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fixtures", "scene", "generated"))
        copied_fixture_path = os.path.join(fixture_dir, f"{candidate_id}.gcs.json")
        _write_json_file(copied_fixture_path, public_scene)
    elif copy_to_fixtures and status != "promotion_package_written":
        package["copy_to_fixtures_blocked"] = True
        _write_json_file(os.path.join(root, "package.json"), package)

    return {
        "promotion_id": promotion_id,
        "status": status,
        "reason_code": reason_code,
        "package_id": promotion_id,
        "copied_fixture_path": copied_fixture_path,
        "known_unsupported_gates": package["known_unsupported_gates"],
    }


TOOLS = {
    "generate_skeleton_graph": tool_generate_skeleton_graph,
    "lift_skeleton_to_gcs": tool_lift_skeleton_to_gcs,
    "assign_geometry_parameters": tool_assign_geometry_parameters,
    "project_gcs_graph": tool_project_gcs_graph,
    "check_vertex_biconnected": tool_check_vertex_biconnected,
    "validate_gcs_schema": tool_validate_gcs_schema,
    "repair_gcs_graph": tool_repair_gcs_graph,
    "serialize_gcs_graph": tool_serialize_gcs_graph,
    "generate_graph_report": tool_generate_graph_report,
    "explore_scene_space": tool_explore_scene_space,
    "promote_candidate": tool_promote_candidate,
}


def _read_input(args) -> dict:
    if args.input:
        try:
            return json.loads(args.input)
        except json.JSONDecodeError:
            return _parse_shell_stripped_json(args.input)
    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            return json.load(f)
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return _parse_shell_stripped_json(raw)


def _parse_shell_stripped_json(raw: str):
    """Parse simple JSON after a shell has stripped quotes from keys/strings."""

    text = raw.strip()
    index = 0

    def fail(message):
        raise ValueError(f"Invalid --input JSON: {message} near {text[index:index + 24]!r}")

    def skip_ws():
        nonlocal index
        while index < len(text) and text[index].isspace():
            index += 1

    def parse_quoted():
        nonlocal index
        quote = text[index]
        index += 1
        chars = []
        while index < len(text):
            ch = text[index]
            index += 1
            if ch == quote:
                return "".join(chars)
            if ch == "\\" and index < len(text):
                chars.append(text[index])
                index += 1
            else:
                chars.append(ch)
        fail("unterminated string")

    def parse_bare(stop_chars):
        nonlocal index
        start = index
        while index < len(text) and text[index] not in stop_chars:
            index += 1
        token = text[start:index].strip()
        if not token:
            fail("empty token")
        if token == "true":
            return True
        if token == "false":
            return False
        if token == "null":
            return None
        try:
            if any(ch in token for ch in ".eE"):
                return float(token)
            return int(token)
        except ValueError:
            return token

    def parse_array():
        nonlocal index
        index += 1
        result = []
        while True:
            skip_ws()
            if index >= len(text):
                fail("unterminated array")
            if text[index] == "]":
                index += 1
                return result
            result.append(parse_value())
            skip_ws()
            if index < len(text) and text[index] == ",":
                index += 1
                continue
            if index < len(text) and text[index] == "]":
                index += 1
                return result
            fail("expected ',' or ']'")

    def parse_object():
        nonlocal index
        index += 1
        result = {}
        while True:
            skip_ws()
            if index >= len(text):
                fail("unterminated object")
            if text[index] == "}":
                index += 1
                return result
            if text[index] in ("'", '"'):
                key = parse_quoted()
            else:
                key = parse_bare(":")
            skip_ws()
            if index >= len(text) or text[index] != ":":
                fail("expected ':'")
            index += 1
            result[str(key)] = parse_value()
            skip_ws()
            if index < len(text) and text[index] == ",":
                index += 1
                continue
            if index < len(text) and text[index] == "}":
                index += 1
                return result
            fail("expected ',' or '}'")

    def parse_value():
        skip_ws()
        if index >= len(text):
            fail("unexpected end")
        ch = text[index]
        if ch == "{":
            return parse_object()
        if ch == "[":
            return parse_array()
        if ch in ("'", '"'):
            return parse_quoted()
        return parse_bare(",]}")

    value = parse_value()
    skip_ws()
    if index != len(text):
        fail("trailing input")
    if not isinstance(value, dict):
        raise ValueError("--input must parse to a JSON object")
    return value


def main() -> None:
    all_commands = sorted(list(TOOLS.keys()) + ["list", "delete"])
    parser = argparse.ArgumentParser(
        description="GCS scene-generation tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python tools.py list
  python tools.py generate_skeleton_graph --input '{"graph_id":"demo_skel","num_vertices":6,"extra_edges":2,"seed":42}'
  python tools.py lift_skeleton_to_gcs --input '{"skeleton_graph_id":"demo_skel","gcs_graph_id":"demo_gcs","seed":43}'
  python tools.py assign_geometry_parameters --input '{"gcs_graph_id":"demo_gcs","seed":44}'
  python tools.py validate_gcs_schema --input '{"gcs_graph_id":"demo_gcs"}'
  python tools.py explore_scene_space --input '{"exploration_id":"demo_explore","seed":45}'
  python tools.py promote_candidate --input '{"exploration_id":"demo_explore","candidate_id":"demo_explore_c0000","gate_profile":"local_only"}'
""",
    )
    parser.add_argument("command", choices=all_commands)
    parser.add_argument("--input", "-i", type=str, help="JSON input string")
    parser.add_argument("--input-file", "-f", type=str, help="Path to JSON input file")
    args = parser.parse_args()

    if args.command == "list":
        result = list_graphs()
    elif args.command == "delete":
        result = delete_graph(_read_input(args)["graph_id"])
    else:
        result = TOOLS[args.command](_read_input(args))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
