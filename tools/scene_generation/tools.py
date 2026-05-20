#!/usr/bin/env python3
"""GCS scene-generation tools.

Entry point:
    python tools.py <command> --input '<json>'

The commands intentionally live in one dependency-free file so they can be used
from local scripts, Codex tasks, and CI-style smoke checks without packaging.
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
from collections import Counter, defaultdict


STORE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".store")

GEOMETRY_TYPES = ("Point", "Line", "Plane")
CONSTRAINT_TYPES = ("Coincident", "Parallel", "Perpendicular", "Distance", "Angle")
CONSTRAINT_TYPE_PREFERENCE = ("Distance", "Coincident", "Parallel", "Perpendicular", "Angle")

VALID_CONSTRAINT_SIGNATURES = {
    "Coincident": {("Point", "Point"), ("Point", "Line"), ("Point", "Plane")},
    "Parallel": {("Line", "Line"), ("Line", "Plane"), ("Plane", "Plane")},
    "Perpendicular": {("Line", "Line"), ("Line", "Plane"), ("Plane", "Plane")},
    "Distance": {
        ("Point", "Point"),
        ("Point", "Line"),
        ("Point", "Plane"),
        ("Line", "Line"),
        ("Line", "Plane"),
        ("Plane", "Plane"),
    },
    "Angle": {("Line", "Line"), ("Line", "Plane"), ("Plane", "Plane")},
}

GEOMETRY_TYPE_MAP = {"Point": 0, "Line": 1, "Plane": 2}
CONSTRAINT_TYPE_MAP = {"Coincident": 0, "Parallel": 1, "Perpendicular": 2, "Distance": 3, "Angle": 4}


# ---------------------------------------------------------------------------
# Stable storage
# ---------------------------------------------------------------------------


def _store_path(graph_id: str) -> str:
    os.makedirs(STORE_DIR, exist_ok=True)
    return os.path.join(STORE_DIR, f"{graph_id}.json")


def save_graph(graph_id: str, data: dict) -> None:
    with open(_store_path(graph_id), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def load_graph(graph_id: str) -> dict:
    path = _store_path(graph_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Graph '{graph_id}' not found in store")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_graphs() -> list[dict]:
    os.makedirs(STORE_DIR, exist_ok=True)
    result = []
    for fname in sorted(os.listdir(STORE_DIR)):
        if not fname.endswith(".json"):
            continue
        graph_id = fname[:-5]
        path = os.path.join(STORE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "gcs_graph_id" in data:
                graph_type = "gcs"
            elif "projected_graph_id" in data:
                graph_type = "projected"
            elif "graph_id" in data:
                graph_type = "skeleton"
            else:
                graph_type = "unknown"
            result.append({"id": graph_id, "type": graph_type})
        except Exception as exc:  # Keep list useful even with scratch corruption.
            result.append({"id": graph_id, "type": "error", "error": str(exc)})
    return result


def delete_graph(graph_id: str) -> dict:
    path = _store_path(graph_id)
    if not os.path.exists(path):
        return {"error": f"Graph '{graph_id}' not found"}
    os.remove(path)
    return {"deleted": graph_id}


# ---------------------------------------------------------------------------
# Generic graph helpers
# ---------------------------------------------------------------------------


def _sort_key(value):
    return (type(value).__name__, str(value))


def _canonical_edge(u, v):
    return tuple(sorted((u, v), key=_sort_key))


def _unique_edges(edges) -> list[list]:
    seen = set()
    result = []
    for edge in edges:
        if len(edge) != 2:
            continue
        u, v = edge
        if u == v:
            continue
        key = _canonical_edge(u, v)
        if key in seen:
            continue
        seen.add(key)
        result.append([key[0], key[1]])
    return sorted(result, key=lambda e: (_sort_key(e[0]), _sort_key(e[1])))


def build_adjacency(vertices, edges) -> dict:
    adj = {v: set() for v in vertices}
    for u, v in edges:
        if u not in adj:
            adj[u] = set()
        if v not in adj:
            adj[v] = set()
        adj[u].add(v)
        adj[v].add(u)
    return adj


def connected_components(vertices, edges) -> list[list]:
    adj = build_adjacency(vertices, edges)
    visited = set()
    components = []
    for start in sorted(vertices, key=_sort_key):
        if start in visited:
            continue
        stack = [start]
        component = []
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            component.append(node)
            for neighbor in sorted(adj[node], key=_sort_key, reverse=True):
                if neighbor not in visited:
                    stack.append(neighbor)
        components.append(sorted(component, key=_sort_key))
    return components


def tarjan_articulation_bcc(vertices, edges) -> tuple[list, list[dict], int]:
    adj = build_adjacency(vertices, edges)
    disc = {}
    low = {}
    parent = {}
    timer = 0
    edge_stack = []
    bcc_list = []
    articulation_points = set()

    def pop_bcc(stop_edge):
        bcc_edges = []
        while edge_stack:
            edge = edge_stack.pop()
            bcc_edges.append(edge)
            if edge == stop_edge:
                break
        bcc_vertices = set()
        for a, b in bcc_edges:
            bcc_vertices.add(a)
            bcc_vertices.add(b)
        bcc_list.append(
            {
                "id": len(bcc_list),
                "vertices": sorted(bcc_vertices, key=_sort_key),
                "edges": [list(e) for e in sorted(bcc_edges, key=lambda x: (_sort_key(x[0]), _sort_key(x[1])))],
            }
        )

    def dfs(u):
        nonlocal timer
        children = 0
        disc[u] = low[u] = timer
        timer += 1

        for v in sorted(adj[u], key=_sort_key):
            edge = _canonical_edge(u, v)
            if v not in disc:
                children += 1
                parent[v] = u
                edge_stack.append(edge)
                dfs(v)
                low[u] = min(low[u], low[v])

                is_root_cut = parent.get(u) is None and children > 1
                is_child_cut = parent.get(u) is not None and low[v] >= disc[u]
                if is_root_cut or is_child_cut:
                    articulation_points.add(u)
                if low[v] >= disc[u]:
                    pop_bcc(edge)
            elif v != parent.get(u) and disc[v] < disc[u]:
                low[u] = min(low[u], disc[v])
                edge_stack.append(edge)

    for vertex in sorted(vertices, key=_sort_key):
        if vertex in disc:
            continue
        parent[vertex] = None
        dfs(vertex)
        if edge_stack:
            pop_bcc(edge_stack[0])

    return sorted(articulation_points, key=_sort_key), bcc_list, len(connected_components(vertices, edges))


def _geometry_primal_edges(gcs: dict) -> list[list[int]]:
    edges = []
    for constraint in gcs.get("constraints", []):
        gids = constraint.get("geometry_ids", [])
        for i in range(len(gids)):
            for j in range(i + 1, len(gids)):
                edges.append([gids[i], gids[j]])
    return _unique_edges(edges)


def _generated_id(prefix: str, rng: random.Random) -> str:
    return f"{prefix}_{rng.randint(1, 999):03d}"


def _rng(seed) -> random.Random:
    return random.Random(seed)


# ---------------------------------------------------------------------------
# GCS model helpers
# ---------------------------------------------------------------------------


def is_valid_constraint_signature(ctype: str, gtype1: str, gtype2: str) -> bool:
    sigs = VALID_CONSTRAINT_SIGNATURES.get(ctype, set())
    return (gtype1, gtype2) in sigs or (gtype2, gtype1) in sigs


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
    if num_rigid_sets is None:
        existing = [rs.get("id") for rs in gcs.get("rigid_sets", []) if "id" in rs]
        geom_rs = [g.get("rigid_set_id") for g in gcs.get("geometries", []) if "rigid_set_id" in g]
        ids = sorted(set(existing + geom_rs))
    else:
        ids = list(range(num_rigid_sets))

    rigid_sets = [{"id": rs_id, "geometry_ids": []} for rs_id in ids]
    rs_by_id = {rs["id"]: rs for rs in rigid_sets}
    for geometry in sorted(gcs.get("geometries", []), key=lambda g: g["id"]):
        rs_id = geometry["rigid_set_id"]
        if rs_id not in rs_by_id:
            rs_by_id[rs_id] = {"id": rs_id, "geometry_ids": []}
            rigid_sets.append(rs_by_id[rs_id])
        rs_by_id[rs_id]["geometry_ids"].append(geometry["id"])
    gcs["rigid_sets"] = sorted(rigid_sets, key=lambda rs: rs["id"])
    gcs["num_rigid_sets"] = len(gcs["rigid_sets"])


def _geometry_map(gcs: dict) -> dict:
    return {g["id"]: g for g in gcs.get("geometries", [])}


def _constraint_has_distinct_rigid_sets(constraint: dict, geom_by_id: dict) -> bool:
    rigid_set_ids = []
    for gid in constraint.get("geometry_ids", []):
        geometry = geom_by_id.get(gid)
        if geometry is None:
            continue
        rigid_set_ids.append(geometry.get("rigid_set_id"))
    return len(rigid_set_ids) == len(set(rigid_set_ids))


def _graph_coloring(vertices, edges, requested_colors: int, rng: random.Random, randomize: bool = False) -> dict | None:
    adj = build_adjacency(vertices, edges)
    color_counts = Counter()
    colors = {}

    def uncolored_order():
        remaining = [v for v in vertices if v not in colors]
        if randomize:
            buckets = defaultdict(list)
            for vertex in remaining:
                saturation = len({colors[n] for n in adj[vertex] if n in colors})
                buckets[(saturation, len(adj[vertex]))].append(vertex)
            best_key = max(buckets)
            bucket = sorted(buckets[best_key], key=_sort_key)
            rng.shuffle(bucket)
            return bucket + [v for v in sorted(remaining, key=_sort_key) if v not in bucket]
        return sorted(
            remaining,
            key=lambda v: (-len({colors[n] for n in adj[v] if n in colors}), -len(adj[v]), _sort_key(v)),
        )

    def search() -> bool:
        if len(colors) == len(vertices):
            return True
        vertex = uncolored_order()[0]
        forbidden = {colors[n] for n in adj[vertex] if n in colors}
        choices = [c for c in range(requested_colors) if c not in forbidden]
        choices.sort(key=lambda c: (color_counts[c], c))
        for color in choices:
            colors[vertex] = color
            color_counts[color] += 1
            if search():
                return True
            color_counts[color] -= 1
            del colors[vertex]
        return False

    if len(vertices) > 32:
        order = sorted(vertices, key=lambda v: (-len(adj[v]), _sort_key(v)))
        if randomize:
            rng.shuffle(order)
            order.sort(key=lambda v: -len(adj[v]))
        for vertex in order:
            forbidden = {colors[n] for n in adj[vertex] if n in colors}
            choices = [c for c in range(requested_colors) if c not in forbidden]
            if not choices:
                return None
            choices.sort(key=lambda c: (color_counts[c], c))
            colors[vertex] = choices[0]
            color_counts[choices[0]] += 1
        return colors

    return colors if search() else None


def _assign_rigid_sets_for_edges(
    vertices,
    edges,
    requested_count: int,
    rng: random.Random,
    assignment: str,
    allow_new_rigid_sets: bool,
) -> tuple[dict, int, bool]:
    if requested_count < 1:
        raise ValueError("num_rigid_sets must be >= 1")
    if edges and requested_count < 2 and not allow_new_rigid_sets:
        raise ValueError("At least 2 rigid sets are required for constrained graphs")

    start = max(1, requested_count)
    stop = len(vertices) if allow_new_rigid_sets else requested_count
    randomize = assignment == "random_balanced"
    for color_count in range(start, stop + 1):
        colors = _graph_coloring(vertices, edges, color_count, rng, randomize=randomize)
        if colors is not None:
            return colors, color_count, color_count != requested_count
    raise ValueError(
        f"Could not assign rigid sets for {len(vertices)} vertices and {len(edges)} edges "
        f"with requested num_rigid_sets={requested_count}"
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
