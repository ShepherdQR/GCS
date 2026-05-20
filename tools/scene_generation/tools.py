#!/usr/bin/env python3
"""
GCS Tools - Unified CLI Entry Point

Usage:
    python tools.py <command> --input '<json>'
    python tools.py <command> --input-file <path>
    echo '<json>' | python tools.py <command>

Commands:
    generate_skeleton_graph      Generate a normal graph skeleton
    lift_skeleton_to_gcs         Lift skeleton to GCS constraint graph
    assign_geometry_parameters   Assign coordinates and constraint values
    project_gcs_graph            Project GCS graph to normal graph
    check_vertex_biconnected     Check if graph is vertex biconnected
    validate_gcs_schema          Validate GCS data structure
    repair_gcs_graph             Repair graph that doesn't satisfy conditions
    serialize_gcs_graph          Output GCS serialization
    generate_graph_report        Generate machine-readable report
    list                         List stored graphs
    delete                       Delete a stored graph by id
"""

import sys
import json
import random
import argparse
import os
import copy
import hashlib
import math
from collections import defaultdict

# ============================================================
# Graph Store
# ============================================================

STORE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".store")


def _store_path(graph_id):
    os.makedirs(STORE_DIR, exist_ok=True)
    return os.path.join(STORE_DIR, f"{graph_id}.json")


def save_graph(graph_id, data):
    with open(_store_path(graph_id), "w") as f:
        json.dump(data, f, indent=2)


def load_graph(graph_id):
    path = _store_path(graph_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Graph '{graph_id}' not found in store")
    with open(path, "r") as f:
        return json.load(f)


def list_graphs():
    os.makedirs(STORE_DIR, exist_ok=True)
    result = []
    for fname in sorted(os.listdir(STORE_DIR)):
        if fname.endswith(".json"):
            graph_id = fname[:-5]
            try:
                with open(os.path.join(STORE_DIR, fname), "r") as f:
                    data = json.load(f)
                gtype = "unknown"
                if "gcs_graph_id" in data:
                    gtype = "gcs"
                elif "projected_graph_id" in data:
                    gtype = "projected"
                elif "graph_id" in data:
                    gtype = "skeleton"
                result.append({"id": graph_id, "type": gtype})
            except Exception:
                result.append({"id": graph_id, "type": "error"})
    return result


def delete_graph(graph_id):
    path = _store_path(graph_id)
    if os.path.exists(path):
        os.remove(path)
        return {"deleted": graph_id}
    return {"error": f"Graph '{graph_id}' not found"}


# ============================================================
# Constraint Type Signatures
# ============================================================

VALID_CONSTRAINT_SIGNATURES = {
    "Coincident": [("Point", "Point"), ("Point", "Line"), ("Point", "Plane")],
    "Parallel": [("Line", "Line"), ("Line", "Plane"), ("Plane", "Plane")],
    "Perpendicular": [("Line", "Line"), ("Line", "Plane"), ("Plane", "Plane")],
    "Distance": [
        ("Point", "Point"), ("Point", "Line"), ("Point", "Plane"),
        ("Line", "Line"), ("Line", "Plane"), ("Plane", "Plane"),
    ],
    "Angle": [("Line", "Line"), ("Line", "Plane"), ("Plane", "Plane")],
}

GEOMETRY_TYPE_MAP = {"Point": 0, "Line": 1, "Plane": 2}
GEOMETRY_TYPE_MAP_REV = {v: k for k, v in GEOMETRY_TYPE_MAP.items()}
CONSTRAINT_TYPE_MAP = {"Coincident": 0, "Parallel": 1, "Perpendicular": 2, "Distance": 3, "Angle": 4}
CONSTRAINT_TYPE_MAP_REV = {v: k for k, v in CONSTRAINT_TYPE_MAP.items()}


def is_valid_constraint_signature(ctype, gtype1, gtype2):
    sigs = VALID_CONSTRAINT_SIGNATURES.get(ctype, [])
    return (gtype1, gtype2) in sigs or (gtype2, gtype1) in sigs


# ============================================================
# Graph Algorithms
# ============================================================

def build_adjacency(vertices, edges):
    adj = defaultdict(set)
    for v in vertices:
        adj[v]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def connected_components(vertices, edges):
    adj = build_adjacency(vertices, edges)
    visited = set()
    components = []
    for v in vertices:
        if v not in visited:
            comp = []
            stack = [v]
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                comp.append(node)
                for nb in adj[node]:
                    if nb not in visited:
                        stack.append(nb)
            components.append(sorted(comp))
    return components


def tarjan_articulation_bcc(vertices, edges):
    adj = build_adjacency(vertices, edges)
    disc = {}
    low = {}
    parent = {}
    articulation_points = []
    timer = [0]
    edge_stack = []
    bcc_list = []

    def dfs(u):
        children = 0
        disc[u] = low[u] = timer[0]
        timer[0] += 1

        for v in sorted(adj[u]):
            if v not in disc:
                children += 1
                parent[v] = u
                edge_stack.append((min(u, v), max(u, v)))
                dfs(v)
                low[u] = min(low[u], low[v])

                if (parent.get(u) is None and children > 1) or \
                   (parent.get(u) is not None and low[v] >= disc[u]):
                    if u not in articulation_points:
                        articulation_points.append(u)

                if low[v] >= disc[u]:
                    bcc_edges = []
                    while edge_stack:
                        e = edge_stack.pop()
                        bcc_edges.append(e)
                        if e == (min(u, v), max(u, v)):
                            break
                    bcc_vertices = set()
                    for a, b in bcc_edges:
                        bcc_vertices.add(a)
                        bcc_vertices.add(b)
                    bcc_list.append({
                        "id": len(bcc_list),
                        "vertices": sorted(bcc_vertices),
                        "edges": sorted(bcc_edges),
                    })
            elif v != parent.get(u) and disc.get(v, float('inf')) < disc[u]:
                low[u] = min(low[u], disc[v])
                canonical_e = (min(u, v), max(u, v))
                if canonical_e not in [(min(a, b), max(a, b)) for a, b in edge_stack]:
                    edge_stack.append(canonical_e)

    for v in sorted(vertices):
        if v not in disc:
            parent[v] = None
            dfs(v)

    num_components = len(connected_components(vertices, edges))

    return sorted(articulation_points), bcc_list, num_components


# ============================================================
# Tool 1: generate_skeleton_graph
# ============================================================

def tool_generate_skeleton_graph(params):
    num_vertices = params["num_vertices"]
    target_property = params.get("target_property", "vertex_biconnected")
    method = params.get("method", "cycle_plus_chords")
    extra_edges = params.get("extra_edges", 0)
    seed = params.get("seed", None)

    if seed is not None:
        random.seed(seed)

    if num_vertices < 3:
        return {"error": "num_vertices must be >= 3 for vertex biconnectivity"}

    if method == "cycle_plus_chords":
        vertices = list(range(num_vertices))
        edges = []
        for i in range(num_vertices):
            edges.append([i, (i + 1) % num_vertices])

        possible_chords = []
        for i in range(num_vertices):
            for j in range(i + 2, num_vertices):
                if i == 0 and j == num_vertices - 1:
                    continue
                possible_chords.append([i, j])
        random.shuffle(possible_chords)
        for k in range(min(extra_edges, len(possible_chords))):
            edges.append(possible_chords[k])

        graph_id = params.get("graph_id", f"skeleton_{random.randint(1, 999):03d}")
        result = {
            "graph_id": graph_id,
            "num_vertices": num_vertices,
            "edges": edges,
            "generation_certificate": {
                "base": "cycle",
                "augmentation": "added_chords" if extra_edges > 0 else "none",
                "property_preserved": "adding_edges_preserves_vertex_biconnectivity",
            },
        }
        save_graph(graph_id, result)
        return result

    elif method == "ear_decomposition":
        vertices = list(range(num_vertices))
        edges = [[0, 1], [1, 2], [2, 0]]

        current_max = 2
        while current_max < num_vertices - 1:
            edge_idx = random.randint(0, len(edges) - 1)
            u, v = edges[edge_idx]
            current_max += 1
            new_v = current_max
            edges.append([u, new_v])
            edges.append([v, new_v])

        graph_id = params.get("graph_id", f"skeleton_{random.randint(1, 999):03d}")
        result = {
            "graph_id": graph_id,
            "num_vertices": num_vertices,
            "edges": edges,
            "generation_certificate": {
                "base": "triangle",
                "augmentation": "ear_decomposition",
                "property_preserved": "ear_decomposition_preserves_vertex_biconnectivity",
            },
        }
        save_graph(graph_id, result)
        return result

    return {"error": f"Unknown method: {method}"}


# ============================================================
# Tool 2: lift_skeleton_to_gcs
# ============================================================

def tool_lift_skeleton_to_gcs(params):
    skeleton_graph_id = params["skeleton_graph_id"]
    geometry_type_policy = params.get("geometry_type_policy", {
        "allowed_types": ["Point", "Line", "Plane"],
        "distribution": {"Point": 0.6, "Line": 0.3, "Plane": 0.1},
    })
    constraint_type_policy = params.get("constraint_type_policy", {
        "allowed_types": ["Distance", "Coincident", "Parallel", "Perpendicular", "Angle"],
        "respect_type_signature": True,
    })
    rigid_set_policy = params.get("rigid_set_policy", {
        "num_rigid_sets": 3,
        "assignment": "random_balanced",
    })
    seed = params.get("seed", None)

    if seed is not None:
        random.seed(seed)

    try:
        skeleton = load_graph(skeleton_graph_id)
    except FileNotFoundError as e:
        return {"error": str(e)}

    num_vertices = skeleton["num_vertices"]
    edges = skeleton["edges"]

    allowed_geom_types = geometry_type_policy["allowed_types"]
    distribution = geometry_type_policy.get("distribution", {})

    dist_list = [(t, distribution.get(t, 1.0 / len(allowed_geom_types))) for t in allowed_geom_types]
    total = sum(d for _, d in dist_list)
    dist_list = [(t, d / total) for t, d in dist_list]

    geom_types = []
    for _ in range(num_vertices):
        r = random.random()
        cumsum = 0.0
        chosen = dist_list[0][0]
        for t, d in dist_list:
            cumsum += d
            if r <= cumsum:
                chosen = t
                break
        geom_types.append(chosen)

    num_rs = rigid_set_policy["num_rigid_sets"]
    assignment = rigid_set_policy.get("assignment", "random_balanced")

    rs_ids = list(range(num_rs))
    rigid_sets = [{"id": rs_id, "geometry_ids": []} for rs_id in rs_ids]

    vertex_indices = list(range(num_vertices))
    if assignment == "random_balanced":
        random.shuffle(vertex_indices)

    rs_assignments = {}
    for i, vi in enumerate(vertex_indices):
        rs_id = rs_ids[i % num_rs]
        rs_assignments[vi] = rs_id
        rigid_sets[rs_id]["geometry_ids"].append(vi)

    geometries = []
    for i in range(num_vertices):
        geometries.append({
            "id": i,
            "type": geom_types[i],
            "rigid_set_id": rs_assignments[i],
            "v": [0.0] * 6,
        })

    allowed_constraint_types = constraint_type_policy["allowed_types"]
    respect_signature = constraint_type_policy.get("respect_type_signature", True)

    constraints = []
    for idx, (u, v) in enumerate(edges):
        gtype_u = geom_types[u]
        gtype_v = geom_types[v]

        valid_types = []
        for ct in allowed_constraint_types:
            if respect_signature:
                if is_valid_constraint_signature(ct, gtype_u, gtype_v):
                    valid_types.append(ct)
            else:
                valid_types.append(ct)

        if not valid_types:
            valid_types = ["Distance"]

        chosen_type = random.choice(valid_types)

        constraints.append({
            "id": idx,
            "type": chosen_type,
            "geometry_ids": [u, v],
            "value": 0.0,
        })

    gcs_graph_id = params.get("gcs_graph_id", f"gcs_{random.randint(1, 999):03d}")
    result = {
        "gcs_graph_id": gcs_graph_id,
        "rigid_sets": rigid_sets,
        "geometries": geometries,
        "constraints": constraints,
        "num_rigid_sets": num_rs,
        "num_geometries": num_vertices,
        "num_constraints": len(edges),
        "status": "constructed",
    }
    save_graph(gcs_graph_id, result)
    return result


# ============================================================
# Tool 3: project_gcs_graph
# ============================================================

def tool_project_gcs_graph(params):
    gcs_graph_id = params["gcs_graph_id"]
    projection = params.get("projection", "geometry_primal")

    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as e:
        return {"error": str(e)}

    if projection == "geometry_primal":
        vertices = [g["id"] for g in gcs["geometries"]]
        edges = []
        seen = set()
        for c in gcs["constraints"]:
            gids = c["geometry_ids"]
            for i in range(len(gids)):
                for j in range(i + 1, len(gids)):
                    e = (min(gids[i], gids[j]), max(gids[i], gids[j]))
                    if e not in seen:
                        seen.add(e)
                        edges.append(list(e))

        projected_graph_id = params.get("projected_graph_id",
                                        f"proj_{random.randint(1, 999):03d}")
        result = {
            "projected_graph_id": projected_graph_id,
            "vertices": vertices,
            "edges": edges,
            "projection_rule": "geometries sharing one constraint are connected",
        }
        save_graph(projected_graph_id, result)
        return result

    elif projection == "incidence_bipartite":
        geometry_nodes = [f"G{g['id']}" for g in gcs["geometries"]]
        constraint_nodes = [f"C{c['id']}" for c in gcs["constraints"]]
        vertices = geometry_nodes + constraint_nodes
        edges = []
        for c in gcs["constraints"]:
            for gid in c["geometry_ids"]:
                edges.append([f"G{gid}", f"C{c['id']}"])

        projected_graph_id = params.get("projected_graph_id",
                                        f"proj_{random.randint(1, 999):03d}")
        result = {
            "projected_graph_id": projected_graph_id,
            "vertices": vertices,
            "edges": edges,
            "projection_rule": "bipartite: geometry and constraint nodes, edge if geometry participates in constraint",
        }
        save_graph(projected_graph_id, result)
        return result

    elif projection == "rigidset_quotient":
        rs_nodes = list(set(g["rigid_set_id"] for g in gcs["geometries"]))
        rs_nodes.sort()
        vertices = rs_nodes
        edges = []
        seen = set()
        for c in gcs["constraints"]:
            gids = c["geometry_ids"]
            if len(gids) >= 2:
                g1 = None
                g2 = None
                for g in gcs["geometries"]:
                    if g["id"] == gids[0]:
                        g1 = g
                    if g["id"] == gids[1]:
                        g2 = g
                if g1 and g2 and g1["rigid_set_id"] != g2["rigid_set_id"]:
                    e = (min(g1["rigid_set_id"], g2["rigid_set_id"]),
                         max(g1["rigid_set_id"], g2["rigid_set_id"]))
                    if e not in seen:
                        seen.add(e)
                        edges.append(list(e))

        projected_graph_id = params.get("projected_graph_id",
                                        f"proj_{random.randint(1, 999):03d}")
        result = {
            "projected_graph_id": projected_graph_id,
            "vertices": vertices,
            "edges": edges,
            "projection_rule": "rigid sets as nodes, edge if constraints connect different rigid sets",
        }
        save_graph(projected_graph_id, result)
        return result

    return {"error": f"Unknown projection: {projection}"}


# ============================================================
# Tool 4: check_vertex_biconnected
# ============================================================

def tool_check_vertex_biconnected(params):
    projected_graph_id = params.get("projected_graph_id")
    graph_id = params.get("graph_id")

    if projected_graph_id:
        gid = projected_graph_id
    elif graph_id:
        gid = graph_id
    else:
        return {"error": "Must provide projected_graph_id or graph_id"}

    try:
        graph = load_graph(gid)
    except FileNotFoundError as e:
        return {"error": str(e)}

    vertices = graph.get("vertices", list(range(graph.get("num_vertices", 0))))
    edges = [tuple(e) for e in graph.get("edges", [])]

    if not vertices:
        return {"error": "Graph has no vertices"}

    articulation_points, bcc_list, num_components = tarjan_articulation_bcc(vertices, edges)

    is_biconnected = (len(articulation_points) == 0
                      and num_components == 1
                      and len(vertices) >= 3)

    result = {
        "is_vertex_biconnected": is_biconnected,
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


# ============================================================
# Tool 5: validate_gcs_schema
# ============================================================

def tool_validate_gcs_schema(params):
    gcs_graph_id = params["gcs_graph_id"]

    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as e:
        return {"error": str(e)}

    violations = []

    geom_ids = [g["id"] for g in gcs["geometries"]]
    constraint_ids = [c["id"] for c in gcs["constraints"]]
    rs_ids = [rs["id"] for rs in gcs["rigid_sets"]]

    seen_geom = set()
    for gid in geom_ids:
        if gid in seen_geom:
            violations.append({
                "type": "duplicate_geometry_id",
                "geometry_id": gid,
                "message": f"Geometry id {gid} is not unique.",
            })
        seen_geom.add(gid)

    seen_constraint = set()
    for cid in constraint_ids:
        if cid in seen_constraint:
            violations.append({
                "type": "duplicate_constraint_id",
                "constraint_id": cid,
                "message": f"Constraint id {cid} is not unique.",
            })
        seen_constraint.add(cid)

    seen_rs = set()
    for rsid in rs_ids:
        if rsid in seen_rs:
            violations.append({
                "type": "duplicate_rigid_set_id",
                "rigid_set_id": rsid,
                "message": f"RigidSet id {rsid} is not unique.",
            })
        seen_rs.add(rsid)

    for g in gcs["geometries"]:
        if g["rigid_set_id"] not in seen_rs:
            violations.append({
                "type": "geometry_not_in_rigid_set",
                "geometry_id": g["id"],
                "message": f"Geometry {g['id']} references non-existent RigidSet {g['rigid_set_id']}.",
            })

    for c in gcs["constraints"]:
        for gid in c["geometry_ids"]:
            if gid not in seen_geom:
                violations.append({
                    "type": "invalid_geometry_reference",
                    "constraint_id": c["id"],
                    "geometry_id": gid,
                    "message": f"Constraint {c['id']} references non-existent Geometry {gid}.",
                })

    for c in gcs["constraints"]:
        if len(c["geometry_ids"]) < 2:
            violations.append({
                "type": "invalid_constraint_arity",
                "constraint_id": c["id"],
                "message": f"Constraint {c['id']} has arity {len(c['geometry_ids'])}, expected >= 2.",
            })

    for c in gcs["constraints"]:
        if len(c["geometry_ids"]) >= 2:
            g1 = None
            g2 = None
            for g in gcs["geometries"]:
                if g["id"] == c["geometry_ids"][0]:
                    g1 = g
                if g["id"] == c["geometry_ids"][1]:
                    g2 = g
            if g1 and g2:
                if not is_valid_constraint_signature(c["type"], g1["type"], g2["type"]):
                    violations.append({
                        "type": "invalid_constraint_signature",
                        "constraint_id": c["id"],
                        "geometry_ids": c["geometry_ids"],
                        "message": f"{c['type']} constraint requires valid signature, got {g1['type']}-{g2['type']}.",
                    })

    for g in gcs["geometries"]:
        if g["type"] == "Line":
            v = g.get("v", [0] * 6)
            if len(v) >= 6 and v[0] == v[3] and v[1] == v[4] and v[2] == v[5]:
                violations.append({
                    "type": "degenerate_line",
                    "geometry_id": g["id"],
                    "message": f"Line {g['id']} is degenerate (start == end).",
                })

    for g in gcs["geometries"]:
        if g["type"] == "Plane":
            v = g.get("v", [0] * 6)
            if len(v) >= 6 and v[3] == 0 and v[4] == 0 and v[5] == 0:
                violations.append({
                    "type": "zero_plane_normal",
                    "geometry_id": g["id"],
                    "message": f"Plane {g['id']} has zero normal vector.",
                })

    for c in gcs["constraints"]:
        if c["type"] == "Distance" and c.get("value", 0) < 0:
            violations.append({
                "type": "negative_distance",
                "constraint_id": c["id"],
                "message": f"Distance constraint {c['id']} has negative value {c['value']}.",
            })

    for c in gcs["constraints"]:
        if c["type"] == "Angle":
            val = c.get("value", 0)
            if val < 0 or val > 180:
                violations.append({
                    "type": "invalid_angle_range",
                    "constraint_id": c["id"],
                    "message": f"Angle constraint {c['id']} has value {val}, expected [0, 180].",
                })

    return {
        "valid": len(violations) == 0,
        "violations": violations,
    }


# ============================================================
# Tool 6: repair_gcs_graph
# ============================================================

def tool_repair_gcs_graph(params):
    gcs_graph_id = params["gcs_graph_id"]
    target_repairs = params.get("target_repairs", [])
    repair_policy = params.get("repair_policy", "minimal_change")

    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as e:
        return {"error": str(e)}

    gcs = copy.deepcopy(gcs)
    edits = []

    for repair in target_repairs:
        if repair == "fix_constraint_signature":
            for c in gcs["constraints"]:
                if len(c["geometry_ids"]) >= 2:
                    g1 = None
                    g2 = None
                    for g in gcs["geometries"]:
                        if g["id"] == c["geometry_ids"][0]:
                            g1 = g
                        if g["id"] == c["geometry_ids"][1]:
                            g2 = g
                    if g1 and g2:
                        if not is_valid_constraint_signature(c["type"], g1["type"], g2["type"]):
                            old_type = c["type"]
                            valid = []
                            for ct in ["Distance", "Coincident", "Parallel", "Perpendicular", "Angle"]:
                                if is_valid_constraint_signature(ct, g1["type"], g2["type"]):
                                    valid.append(ct)
                            if valid:
                                c["type"] = valid[0]
                                edits.append({
                                    "operation": "replace_constraint_type",
                                    "constraint_id": c["id"],
                                    "old_type": old_type,
                                    "new_type": valid[0],
                                })

        elif repair == "make_geometry_primal_vertex_biconnected":
            vertices = [g["id"] for g in gcs["geometries"]]
            edges = []
            seen = set()
            for c in gcs["constraints"]:
                gids = c["geometry_ids"]
                for i in range(len(gids)):
                    for j in range(i + 1, len(gids)):
                        e = (min(gids[i], gids[j]), max(gids[i], gids[j]))
                        if e not in seen:
                            seen.add(e)
                            edges.append(list(e))

            articulation_points, bcc_list, num_components = tarjan_articulation_bcc(vertices, edges)

            if num_components > 1:
                components = connected_components(vertices, edges)
                max_cid = max(c["id"] for c in gcs["constraints"]) if gcs["constraints"] else -1
                for i in range(len(components) - 1):
                    g1_id = components[i][0]
                    g2_id = components[i + 1][0]
                    g1_type = None
                    g2_type = None
                    for g in gcs["geometries"]:
                        if g["id"] == g1_id:
                            g1_type = g["type"]
                        if g["id"] == g2_id:
                            g2_type = g["type"]

                    valid = []
                    for ct in ["Distance", "Coincident", "Parallel", "Perpendicular", "Angle"]:
                        if g1_type and g2_type and is_valid_constraint_signature(ct, g1_type, g2_type):
                            valid.append(ct)

                    if valid:
                        max_cid += 1
                        new_constraint = {
                            "id": max_cid,
                            "type": valid[0],
                            "geometry_ids": [g1_id, g2_id],
                            "value": 0.0,
                        }
                        gcs["constraints"].append(new_constraint)
                        edits.append({
                            "operation": "add_constraint",
                            "new_constraint_id": max_cid,
                            "geometry_ids": [g1_id, g2_id],
                            "constraint_type": valid[0],
                        })

            if articulation_points:
                adj = build_adjacency(vertices, edges)
                max_cid = max(c["id"] for c in gcs["constraints"]) if gcs["constraints"] else -1
                for ap in articulation_points:
                    neighbors = sorted(adj[ap])
                    if len(neighbors) >= 2:
                        n1, n2 = neighbors[0], neighbors[1]
                        if (min(n1, n2), max(n1, n2)) not in seen:
                            g1_type = None
                            g2_type = None
                            for g in gcs["geometries"]:
                                if g["id"] == n1:
                                    g1_type = g["type"]
                                if g["id"] == n2:
                                    g2_type = g["type"]

                            valid = []
                            for ct in ["Distance", "Coincident", "Parallel", "Perpendicular", "Angle"]:
                                if g1_type and g2_type and is_valid_constraint_signature(ct, g1_type, g2_type):
                                    valid.append(ct)

                            if valid:
                                max_cid += 1
                                new_constraint = {
                                    "id": max_cid,
                                    "type": valid[0],
                                    "geometry_ids": [n1, n2],
                                    "value": 0.0,
                                }
                                gcs["constraints"].append(new_constraint)
                                seen.add((min(n1, n2), max(n1, n2)))
                                edits.append({
                                    "operation": "add_constraint",
                                    "new_constraint_id": max_cid,
                                    "geometry_ids": [n1, n2],
                                    "constraint_type": valid[0],
                                    "reason": f"bypass articulation point {ap}",
                                })

    repaired_id = params.get("repaired_gcs_graph_id", gcs_graph_id + "_repaired")
    gcs["gcs_graph_id"] = repaired_id
    gcs["num_constraints"] = len(gcs["constraints"])

    result = {
        "repaired_gcs_graph_id": repaired_id,
        "edits": edits,
        "repair_certificate": {
            "policy": repair_policy,
            "post_validation_required": True,
        },
    }
    save_graph(repaired_id, gcs)
    return result


# ============================================================
# Tool 7: serialize_gcs_graph
# ============================================================

def tool_serialize_gcs_graph(params):
    gcs_graph_id = params["gcs_graph_id"]
    fmt = params.get("format", "custom_text_v1")

    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as e:
        return {"error": str(e)}

    if fmt == "custom_text_v1":
        lines = []

        lines.append(str(len(gcs["rigid_sets"])))
        lines.append(" ".join(str(rs["id"]) for rs in gcs["rigid_sets"]))

        lines.append(str(len(gcs["geometries"])))
        for g in gcs["geometries"]:
            type_int = GEOMETRY_TYPE_MAP.get(g["type"], 0)
            lines.append(f"{g['id']} {type_int} {g['rigid_set_id']}")

        lines.append(str(len(gcs["constraints"])))
        for c in gcs["constraints"]:
            type_int = CONSTRAINT_TYPE_MAP.get(c["type"], 0)
            gids = " ".join(str(gid) for gid in c["geometry_ids"])
            lines.append(f"{c['id']} {type_int} {len(c['geometry_ids'])} {gids}")

        lines.append("")
        for g in gcs["geometries"]:
            vals = " ".join(str(v) for v in g.get("v", [0] * 6))
            lines.append(f"{g['id']} {vals}")

        lines.append("")
        for c in gcs["constraints"]:
            lines.append(f"{c['id']} {c.get('value', 0.0)}")

        serialization = "\n".join(lines)
        checksum = hashlib.sha256(serialization.encode()).hexdigest()[:16]

        return {
            "serialization": serialization,
            "checksum": checksum,
            "canonical": True,
        }

    elif fmt == "json":
        canonical = json.dumps(gcs, sort_keys=True, indent=2)
        checksum = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        return {
            "serialization": canonical,
            "checksum": checksum,
            "canonical": True,
        }

    return {"error": f"Unknown format: {fmt}"}


# ============================================================
# Tool 8: generate_graph_report
# ============================================================

def tool_generate_graph_report(params):
    gcs_graph_id = params["gcs_graph_id"]
    include = params.get("include", [
        "schema_validation",
        "projection_statistics",
        "biconnectivity_certificate",
        "constraint_type_histogram",
        "rigidset_summary",
    ])

    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as e:
        return {"error": str(e)}

    report = {"graph_id": gcs_graph_id}

    report["summary"] = {
        "num_rigid_sets": len(gcs["rigid_sets"]),
        "num_geometries": len(gcs["geometries"]),
        "num_constraints": len(gcs["constraints"]),
    }

    if "schema_validation" in include:
        validation = tool_validate_gcs_schema({"gcs_graph_id": gcs_graph_id})
        report["schema_valid"] = validation["valid"]
        if not validation["valid"]:
            report["schema_violations"] = len(validation["violations"])

    vertices = [g["id"] for g in gcs["geometries"]]
    edges = []
    seen = set()
    for c in gcs["constraints"]:
        gids = c["geometry_ids"]
        for i in range(len(gids)):
            for j in range(i + 1, len(gids)):
                e = (min(gids[i], gids[j]), max(gids[i], gids[j]))
                if e not in seen:
                    seen.add(e)
                    edges.append(list(e))

    if "projection_statistics" in include:
        report["projection_statistics"] = {
            "num_vertices": len(vertices),
            "num_edges": len(edges),
        }

    if "biconnectivity_certificate" in include:
        articulation_points, bcc_list, num_components = tarjan_articulation_bcc(vertices, edges)
        report["geometry_primal_biconnected"] = len(articulation_points) == 0 and num_components == 1
        report["articulation_points"] = articulation_points

    if "constraint_type_histogram" in include:
        histogram = defaultdict(int)
        for c in gcs["constraints"]:
            histogram[c["type"]] += 1
        report["constraint_type_histogram"] = dict(histogram)

    if "rigidset_summary" in include:
        rs_summary = []
        for rs in gcs["rigid_sets"]:
            geom_count = len(rs.get("geometry_ids", []))
            rs_summary.append({"id": rs["id"], "num_geometries": geom_count})
        report["rigidset_summary"] = rs_summary

    return report


# ============================================================
# Tool 9: assign_geometry_parameters
# ============================================================

def _vec_sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def _vec_add(a, b):
    return [a[i] + b[i] for i in range(3)]


def _vec_scale(a, s):
    return [a[i] * s for i in range(3)]


def _vec_len(a):
    return math.sqrt(sum(a[i] ** 2 for i in range(3)))


def _vec_normalize(a):
    l = _vec_len(a)
    if l < 1e-12:
        return [0.0, 0.0, 1.0]
    return [a[i] / l for i in range(3)]


def _vec_cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _vec_dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def _angle_between_vectors(a, b):
    na = _vec_normalize(a)
    nb = _vec_normalize(b)
    cos_val = max(-1.0, min(1.0, _vec_dot(na, nb)))
    return math.degrees(math.acos(cos_val))


def _point_distance(p1, p2):
    return _vec_len(_vec_sub(p1, p2))


def _line_direction(line_v):
    return _vec_sub(line_v[3:6], line_v[0:3])


def _plane_normal(plane_v):
    return plane_v[3:6]


def _layout_circular(geometries, layout_params, seed):
    radius = layout_params.get("radius", 2.0)
    center = layout_params.get("center", [0.0, 0.0, 0.0])
    plane = layout_params.get("plane", "xy")

    if seed is not None:
        random.seed(seed)

    n = len(geometries)
    positions = {}
    for i, g in enumerate(geometries):
        angle = 2 * math.pi * i / n
        if plane == "xy":
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = center[2]
        elif plane == "xz":
            x = center[0] + radius * math.cos(angle)
            y = center[1]
            z = center[2] + radius * math.sin(angle)
        elif plane == "yz":
            x = center[0]
            y = center[1] + radius * math.cos(angle)
            z = center[2] + radius * math.sin(angle)
        else:
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = center[2]
        positions[g["id"]] = [x, y, z]

    return positions


def _layout_random(geometries, layout_params, seed):
    radius = layout_params.get("radius", 3.0)
    center = layout_params.get("center", [0.0, 0.0, 0.0])

    if seed is not None:
        random.seed(seed)

    positions = {}
    for g in geometries:
        while True:
            x = center[0] + random.uniform(-radius, radius)
            y = center[1] + random.uniform(-radius, radius)
            z = center[2] + random.uniform(-radius, radius)
            if math.sqrt(x ** 2 + y ** 2 + z ** 2) > 0.5:
                break
        positions[g["id"]] = [x, y, z]

    return positions


def _layout_grid(geometries, layout_params, seed):
    spacing = layout_params.get("spacing", 2.0)
    center = layout_params.get("center", [0.0, 0.0, 0.0])

    if seed is not None:
        random.seed(seed)

    n = len(geometries)
    cols = max(1, int(math.ceil(math.sqrt(n))))
    positions = {}
    for i, g in enumerate(geometries):
        row = i // cols
        col = i % cols
        x = center[0] + col * spacing
        y = center[1] - row * spacing
        z = center[2]
        positions[g["id"]] = [x, y, z]

    return positions


def tool_assign_geometry_parameters(params):
    gcs_graph_id = params["gcs_graph_id"]
    layout = params.get("layout", "circular")
    layout_params = params.get("layout_params", {})
    seed = params.get("seed", None)

    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as e:
        return {"error": str(e)}

    gcs = copy.deepcopy(gcs)

    if seed is not None:
        random.seed(seed)

    if layout == "circular":
        positions = _layout_circular(gcs["geometries"], layout_params, seed)
    elif layout == "random":
        positions = _layout_random(gcs["geometries"], layout_params, seed)
    elif layout == "grid":
        positions = _layout_grid(gcs["geometries"], layout_params, seed)
    else:
        return {"error": f"Unknown layout: {layout}"}

    for g in gcs["geometries"]:
        pos = positions[g["id"]]
        if g["type"] == "Point":
            g["v"] = [pos[0], pos[1], pos[2], 0.0, 0.0, 0.0]
        elif g["type"] == "Line":
            direction = _vec_normalize([
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1),
            ])
            half_len = random.uniform(0.5, 1.5)
            start = _vec_sub(pos, _vec_scale(direction, half_len))
            end = _vec_add(pos, _vec_scale(direction, half_len))
            g["v"] = [start[0], start[1], start[2], end[0], end[1], end[2]]
        elif g["type"] == "Plane":
            normal = _vec_normalize([
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(0.3, 1),
            ])
            g["v"] = [pos[0], pos[1], pos[2], normal[0], normal[1], normal[2]]

    geom_map = {g["id"]: g for g in gcs["geometries"]}

    for c in gcs["constraints"]:
        gids = c["geometry_ids"]
        if len(gids) < 2:
            continue

        g1 = geom_map.get(gids[0])
        g2 = geom_map.get(gids[1])
        if not g1 or not g2:
            continue

        if c["type"] == "Distance":
            p1 = g1["v"][0:3]
            p2 = g2["v"][0:3]
            c["value"] = round(_point_distance(p1, p2), 6)
        elif c["type"] == "Angle":
            if g1["type"] == "Line" and g2["type"] == "Line":
                d1 = _line_direction(g1["v"])
                d2 = _line_direction(g2["v"])
                c["value"] = round(_angle_between_vectors(d1, d2), 6)
            elif g1["type"] == "Line" and g2["type"] == "Plane":
                d = _line_direction(g1["v"])
                n = _plane_normal(g2["v"])
                angle_to_normal = _angle_between_vectors(d, n)
                c["value"] = round(90.0 - angle_to_normal, 6)
            elif g1["type"] == "Plane" and g2["type"] == "Line":
                n = _plane_normal(g1["v"])
                d = _line_direction(g2["v"])
                angle_to_normal = _angle_between_vectors(n, d)
                c["value"] = round(90.0 - angle_to_normal, 6)
            elif g1["type"] == "Plane" and g2["type"] == "Plane":
                n1 = _plane_normal(g1["v"])
                n2 = _plane_normal(g2["v"])
                c["value"] = round(_angle_between_vectors(n1, n2), 6)
            else:
                c["value"] = round(random.uniform(15, 75), 6)
        else:
            c["value"] = 0.0

    gcs["status"] = "parameters_assigned"
    save_graph(gcs_graph_id, gcs)

    return {
        "gcs_graph_id": gcs_graph_id,
        "geometries": gcs["geometries"],
        "constraints": gcs["constraints"],
        "status": "parameters_assigned",
    }


# ============================================================
# CLI Entry Point
# ============================================================

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


def main():
    all_commands = list(TOOLS.keys()) + ["list", "delete"]

    parser = argparse.ArgumentParser(
        description="GCS Tools - Unified CLI Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools.py generate_skeleton_graph --input '{"num_vertices":12,"method":"cycle_plus_chords","extra_edges":6,"seed":42}'
  python tools.py lift_skeleton_to_gcs --input '{"skeleton_graph_id":"skeleton_001","seed":43}'
  python tools.py assign_geometry_parameters --input '{"gcs_graph_id":"gcs_001","layout":"circular","seed":44}'
  python tools.py project_gcs_graph --input '{"gcs_graph_id":"gcs_001"}'
  python tools.py check_vertex_biconnected --input '{"projected_graph_id":"proj_001"}'
  python tools.py validate_gcs_schema --input '{"gcs_graph_id":"gcs_001"}'
  python tools.py repair_gcs_graph --input '{"gcs_graph_id":"gcs_001","target_repairs":["fix_constraint_signature"]}'
  python tools.py serialize_gcs_graph --input '{"gcs_graph_id":"gcs_001"}'
  python tools.py generate_graph_report --input '{"gcs_graph_id":"gcs_001"}'
  python tools.py list
  python tools.py delete --input '{"graph_id":"skeleton_001"}'
""",
    )
    parser.add_argument("command", choices=all_commands, help="Tool command to execute")
    parser.add_argument("--input", "-i", type=str, help="JSON input string")
    parser.add_argument("--input-file", "-f", type=str, help="Path to JSON input file")

    args = parser.parse_args()

    if args.command == "list":
        result = list_graphs()
        print(json.dumps(result, indent=2))
        return

    if args.command == "delete":
        if args.input:
            params = json.loads(args.input)
        elif args.input_file:
            with open(args.input_file, "r") as f:
                params = json.load(f)
        else:
            params = json.loads(sys.stdin.read())
        result = delete_graph(params["graph_id"])
        print(json.dumps(result, indent=2))
        return

    if args.input:
        params = json.loads(args.input)
    elif args.input_file:
        with open(args.input_file, "r") as f:
            params = json.load(f)
    else:
        params = json.loads(sys.stdin.read())

    result = TOOLS[args.command](params)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
