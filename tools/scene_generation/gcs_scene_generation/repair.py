"""Repair policy for generated GCS candidate graphs."""

from __future__ import annotations

import copy
import random

from .contracts import CONSTRAINT_TYPE_PREFERENCE, is_valid_constraint_signature
from .gcs_model import (
    assign_rigid_sets_for_edges,
    constraint_has_distinct_rigid_sets,
    geometry_map,
    geometry_primal_edges,
    rebuild_rigid_sets,
)
from .topology import canonical_edge, sort_key, tarjan_articulation_bcc, unique_edges


def first_valid_constraint_type(g1: dict, g2: dict, allowed=None) -> str | None:
    allowed_set = set(allowed or CONSTRAINT_TYPE_PREFERENCE)
    for ctype in CONSTRAINT_TYPE_PREFERENCE:
        if ctype in allowed_set and is_valid_constraint_signature(ctype, g1["type"], g2["type"]):
            return ctype
    return None


def repair_gcs_graph(
    original: dict,
    target_repairs: list[str],
    repair_policy: str,
    seed,
    repaired_gcs_graph_id: str,
) -> dict:
    gcs = copy.deepcopy(original)
    edits = []

    def finish() -> dict:
        gcs["gcs_graph_id"] = repaired_gcs_graph_id
        gcs["num_geometries"] = len(gcs.get("geometries", []))
        gcs["num_constraints"] = len(gcs.get("constraints", []))
        gcs["status"] = "repaired"
        return {
            "repaired_gcs_graph_id": repaired_gcs_graph_id,
            "edits": edits,
            "repair_certificate": {"policy": repair_policy, "post_validation_required": True},
            "_repaired_graph": gcs,
        }

    def recolor_for_edges(required_edges, reason: str):
        vertices = sorted([g["id"] for g in gcs.get("geometries", [])], key=sort_key)
        current_count = max(1, len(gcs.get("rigid_sets", [])))
        colors, actual_count, expanded = assign_rigid_sets_for_edges(
            vertices,
            unique_edges(required_edges),
            current_count,
            random.Random(seed),
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
        rebuild_rigid_sets(gcs, actual_count)
        return before

    if "fix_constraint_signature" in target_repairs:
        geom_by_id = geometry_map(gcs)
        for constraint in gcs.get("constraints", []):
            gids = constraint.get("geometry_ids", [])
            if len(gids) < 2 or gids[0] not in geom_by_id or gids[1] not in geom_by_id:
                continue
            g1 = geom_by_id[gids[0]]
            g2 = geom_by_id[gids[1]]
            if not is_valid_constraint_signature(constraint.get("type"), g1.get("type"), g2.get("type")):
                new_type = first_valid_constraint_type(g1, g2)
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
        geom_by_id = geometry_map(gcs)
        needs_recolor = any(
            not constraint_has_distinct_rigid_sets(constraint, geom_by_id)
            for constraint in gcs.get("constraints", [])
            if len(constraint.get("geometry_ids", [])) >= 2
        )
        if needs_recolor:
            try:
                recolor_for_edges(geometry_primal_edges(gcs), "constraints_connect_distinct_rigid_sets")
            except ValueError as exc:
                return {"error": str(exc)}

    if "make_geometry_primal_vertex_biconnected" in target_repairs:
        vertices = sorted([g["id"] for g in gcs.get("geometries", [])], key=sort_key)
        if len(vertices) < 3:
            return {"error": "At least 3 geometries are required for vertex biconnectivity"}
        existing_edges = geometry_primal_edges(gcs)
        articulation_points, _, num_components = tarjan_articulation_bcc(vertices, existing_edges)
        if num_components == 1 and not articulation_points:
            return finish()
        cycle_edges = [[vertices[i], vertices[(i + 1) % len(vertices)]] for i in range(len(vertices))]
        required_edges = unique_edges(existing_edges + cycle_edges)
        try:
            recolor_for_edges(required_edges, "make_geometry_primal_vertex_biconnected")
        except ValueError as exc:
            return {"error": str(exc)}
        geom_by_id = geometry_map(gcs)
        existing = {canonical_edge(u, v) for u, v in existing_edges}
        next_id = max([c["id"] for c in gcs.get("constraints", [])], default=-1) + 1
        for u, v in cycle_edges:
            edge_key = canonical_edge(u, v)
            if edge_key in existing:
                continue
            g1 = geom_by_id[u]
            g2 = geom_by_id[v]
            ctype = first_valid_constraint_type(g1, g2)
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

    return finish()

