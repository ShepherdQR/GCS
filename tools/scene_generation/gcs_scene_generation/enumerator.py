"""Exhaustive constraint-graph enumeration for small fixed-parameter spaces.

Unlike the sampling-based explorer, this module enumerates *all* valid
constraint graphs for a given (num_geometries, num_constraints, num_rigid_sets)
configuration, subject to geometry-primal biconnectivity, distinct rigid-set
constraints, and valid constraint signatures.
"""

from __future__ import annotations

import itertools
import json
import math
import os
import time
from collections import Counter
from dataclasses import dataclass
from typing import Callable

from . import gcs_model, parameterization
from .contracts import CONSTRAINT_TYPES, GEOMETRY_TYPES, is_valid_constraint_signature
from .storage import SceneGenerationStore, safe_store_id, sha256_text
from .topology import tarjan_articulation_bcc


@dataclass(frozen=True)
class EnumeratorServices:
    store: SceneGenerationStore
    save_graph: Callable[[str, dict], None]
    load_graph: Callable[[str], dict]


def _canonical_edge(u, v):
    return (min(u, v), max(u, v))


def _geometry_type_assignments(num_geometries: int, allowed_types: list[str]):
    """Yield all tuples of length num_geometries assigning types from allowed_types."""
    for types in itertools.product(allowed_types, repeat=num_geometries):
        yield types


def _rigid_set_partitions(num_geometries: int, num_rigid_sets: int):
    """Yield all tuples assigning each geometry to a rigid set (non-empty sets)."""
    all_assignments = list(itertools.product(range(num_rigid_sets), repeat=num_geometries))
    for assignment in all_assignments:
        used = set(assignment)
        if len(used) == num_rigid_sets:
            yield assignment


def _cross_rigid_set_pairs(rs_assignment: tuple, num_geometries: int):
    """Return sorted list of (u, v) where u < v and rs[u] != rs[v]."""
    pairs = []
    for u in range(num_geometries):
        for v in range(u + 1, num_geometries):
            if rs_assignment[u] != rs_assignment[v]:
                pairs.append((u, v))
    return pairs


def _edge_subsets(cross_pairs: list, num_constraints: int):
    """Yield all subsets of cross_pairs with exactly num_constraints edges."""
    for subset in itertools.combinations(cross_pairs, num_constraints):
        yield list(subset)


def _valid_constraint_types(gtype1: str, gtype2: str, allowed_constraints: list[str]):
    """Return constraint types valid for this geometry pair signature."""
    result = []
    for ctype in allowed_constraints:
        if is_valid_constraint_signature(ctype, gtype1, gtype2):
            result.append(ctype)
    return result


def _is_vertex_biconnected(vertices: list[int], edges: list[tuple]) -> bool:
    if len(vertices) < 3:
        return False
    edge_list = [[u, v] for u, v in edges]
    articulation_points, _, num_components = tarjan_articulation_bcc(vertices, edge_list)
    return num_components == 1 and not articulation_points


def _is_connected(vertices: list[int], edges: list[tuple]) -> bool:
    if len(vertices) < 2:
        return True
    edge_list = [[u, v] for u, v in edges]
    _, _, num_components = tarjan_articulation_bcc(vertices, edge_list)
    return num_components == 1


def _constraint_canonical_key(gcs: dict) -> str:
    """Deterministic key for deduplication based on sorted constraint structure."""
    geometries = sorted(gcs.get("geometries", []), key=lambda g: g["id"])
    geom_types = tuple(g["type"] for g in geometries)
    rs_map = tuple(g.get("rigid_set_id") for g in geometries)

    constraints = sorted(gcs.get("constraints", []), key=lambda c: c["id"])
    constraint_sigs = []
    for c in constraints:
        gids = tuple(sorted(c.get("geometry_ids", [])))
        ctype = c.get("type")
        constraint_sigs.append((gids, ctype))
    constraint_sigs.sort()

    canonical = json.dumps({"geom_types": geom_types, "rs_map": rs_map, "constraints": constraint_sigs}, sort_keys=True)
    return sha256_text(canonical)


def _build_gcs_graph(
    graph_id: str,
    geom_types: tuple,
    rs_assignment: tuple,
    edges: list,
    constraint_types_per_edge: list,
    num_rigid_sets: int,
):
    """Build a GCS graph dict from enumeration parameters."""
    geometries = []
    for i, (gtype, rs_id) in enumerate(zip(geom_types, rs_assignment)):
        geometries.append({
            "id": i,
            "type": gtype,
            "rigid_set_id": rs_id,
            "v": [0.0] * 6,
        })

    constraints = []
    for idx, (edge, ctypes) in enumerate(zip(edges, constraint_types_per_edge)):
        u, v = edge
        constraints.append({
            "id": idx,
            "type": ctypes,
            "geometry_ids": [u, v],
            "value": 0.0,
        })

    gcs = {
        "gcs_graph_id": graph_id,
        "rigid_sets": [],
        "geometries": geometries,
        "constraints": constraints,
        "num_geometries": len(geometries),
        "num_constraints": len(constraints),
        "status": "enumerated",
    }
    gcs_model.rebuild_rigid_sets(gcs, num_rigid_sets)
    return gcs


def _parameterize_and_validate(services, gcs_graph_id: str, gcs: dict, rng_seed: int) -> tuple[dict, bool, str]:
    """Assign geometry parameters and validate schema. Returns (gcs, valid, reason)."""
    import random
    rng = random.Random(rng_seed)
    try:
        gcs = parameterization.assign_geometry_parameters(gcs, "circular", {}, rng)
    except ValueError as exc:
        return gcs, False, f"parameterization_failed: {exc}"

    return gcs, True, "ok"


def enumerate_scene_space(params: dict, services) -> dict:
    """Enumerate all valid constraint graphs for fixed parameters.

    Required params:
        enumeration_id, num_geometries, num_constraints, num_rigid_sets
    Optional:
        geometry_types (default all), constraint_types (default all),
        seed (default 0), max_graphs (default 10000), max_seconds (default 0=unlimited),
        require_biconnected (default True, set False for connectivity-only)
    """
    store: SceneGenerationStore = services.store
    enumeration_id = safe_store_id(params.get("enumeration_id", f"enum_{int(time.time())}"), "enumeration_id")
    num_geometries = int(params.get("num_geometries", 5))
    num_constraints = int(params.get("num_constraints", 5))
    num_rigid_sets = int(params.get("num_rigid_sets", 2))
    allowed_geom_types = list(params.get("geometry_types", list(GEOMETRY_TYPES)))
    allowed_constraint_types = list(params.get("constraint_types", list(CONSTRAINT_TYPES)))
    seed = int(params.get("seed", 0))
    max_graphs = int(params.get("max_graphs", 10000))
    max_seconds = float(params.get("max_seconds", 0.0))
    require_biconnected = bool(params.get("require_biconnected", True))

    unknown_geom = [g for g in allowed_geom_types if g not in GEOMETRY_TYPES]
    if unknown_geom:
        return {"status": "failed", "reason_code": "invalid_request", "error": f"Unknown geometry types: {unknown_geom}"}
    unknown_constraints = [c for c in allowed_constraint_types if c not in CONSTRAINT_TYPES]
    if unknown_constraints:
        return {"status": "failed", "reason_code": "invalid_request", "error": f"Unknown constraint types: {unknown_constraints}"}
    if num_geometries < 3:
        return {"status": "failed", "reason_code": "invalid_request", "error": "num_geometries must be >= 3 for biconnectivity"}

    root = store.enumeration_root(enumeration_id)
    os.makedirs(root, exist_ok=True)
    store.write_json_file(os.path.join(root, "request.json"), params)

    vertices = list(range(num_geometries))
    seen_hashes = set()
    accepted = []
    stats = Counter()
    start_time = time.monotonic()
    graph_index = 0

    geom_type_list = list(_geometry_type_assignments(num_geometries, allowed_geom_types))
    rs_partition_list = list(_rigid_set_partitions(num_geometries, num_rigid_sets))

    total_combos = len(geom_type_list) * len(rs_partition_list)
    combo_index = 0

    for geom_types in geom_type_list:
        for rs_assignment in rs_partition_list:
            combo_index += 1
            if max_graphs > 0 and len(accepted) >= max_graphs:
                break
            if max_seconds > 0.0 and (time.monotonic() - start_time) >= max_seconds:
                break

            cross_pairs = _cross_rigid_set_pairs(rs_assignment, num_geometries)
            if len(cross_pairs) < num_constraints:
                stats["skipped_insufficient_cross_pairs"] += 1
                continue

            for edge_subset in _edge_subsets(cross_pairs, num_constraints):
                if max_graphs > 0 and len(accepted) >= max_graphs:
                    break
                if max_seconds > 0.0 and (time.monotonic() - start_time) >= max_seconds:
                    break

                stats["edge_subsets_checked"] += 1

                if require_biconnected:
                    if not _is_vertex_biconnected(vertices, edge_subset):
                        stats["skipped_not_biconnected"] += 1
                        continue
                else:
                    if not _is_connected(vertices, edge_subset):
                        stats["skipped_not_connected"] += 1
                        continue

                valid_ctypes_per_edge = []
                for u, v in edge_subset:
                    ctypes = _valid_constraint_types(geom_types[u], geom_types[v], allowed_constraint_types)
                    if not ctypes:
                        break
                    valid_ctypes_per_edge.append(ctypes)

                if len(valid_ctypes_per_edge) != num_constraints:
                    stats["skipped_no_valid_constraint_type"] += 1
                    continue

                for ctype_combo in itertools.product(*valid_ctypes_per_edge):
                    if max_graphs > 0 and len(accepted) >= max_graphs:
                        break

                    graph_id = f"{enumeration_id}_g{graph_index:06d}"
                    graph_index += 1
                    stats["graphs_constructed"] += 1

                    gcs = _build_gcs_graph(
                        graph_id, geom_types, rs_assignment,
                        list(edge_subset), list(ctype_combo), num_rigid_sets,
                    )

                    canonical_key = _constraint_canonical_key(gcs)
                    if canonical_key in seen_hashes:
                        stats["skipped_duplicate"] += 1
                        continue
                    seen_hashes.add(canonical_key)

                    gcs, param_ok, param_reason = _parameterize_and_validate(
                        services, graph_id, gcs, seed + graph_index,
                    )
                    if not param_ok:
                        stats["skipped_parameterization_failed"] += 1
                        continue

                    store.save_graph(graph_id, gcs)
                    accepted.append({
                        "graph_id": graph_id,
                        "num_geometries": num_geometries,
                        "num_constraints": num_constraints,
                        "num_rigid_sets": num_rigid_sets,
                        "geometry_types": dict(Counter(geom_types)),
                        "constraint_types": dict(Counter(ctype_combo)),
                        "canonical_key": canonical_key,
                    })
                    stats["accepted"] += 1

        if max_graphs > 0 and len(accepted) >= max_graphs:
            break
        if max_seconds > 0.0 and (time.monotonic() - start_time) >= max_seconds:
            break

    elapsed = time.monotonic() - start_time
    stop_reason = "exhausted"
    if max_graphs > 0 and len(accepted) >= max_graphs:
        stop_reason = "max_graphs"
    elif max_seconds > 0.0 and elapsed >= max_seconds:
        stop_reason = "max_seconds"

    result = {
        "enumeration_id": enumeration_id,
        "status": "completed" if accepted else "no_graphs_enumerated",
        "stop_reason": stop_reason,
        "parameters": {
            "num_geometries": num_geometries,
            "num_constraints": num_constraints,
            "num_rigid_sets": num_rigid_sets,
            "require_biconnected": require_biconnected,
            "geometry_types": allowed_geom_types,
            "constraint_types": allowed_constraint_types,
        },
        "summary": {
            "total_combos": total_combos,
            "graphs_constructed": stats["graphs_constructed"],
            "accepted": len(accepted),
            "duplicates_discarded": stats["skipped_duplicate"],
            "biconnectivity_rejected": stats.get("skipped_not_biconnected", 0),
            "connectivity_rejected": stats.get("skipped_not_connected", 0),
            "parameterization_rejected": stats["skipped_parameterization_failed"],
            "other_rejected": stats["skipped_insufficient_cross_pairs"] + stats["skipped_no_valid_constraint_type"],
        },
        "elapsed_seconds": round(elapsed, 3),
        "graph_ids": [a["graph_id"] for a in accepted],
        "graphs": accepted,
    }
    store.write_json_file(os.path.join(root, "result.json"), result)
    return result
