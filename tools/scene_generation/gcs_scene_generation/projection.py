"""Projection helpers for generated GCS graphs."""

from __future__ import annotations

from .gcs_model import geometry_map, geometry_primal_edges
from .topology import sort_key, unique_edges


def project_gcs_graph(gcs_graph_id: str, gcs: dict, projection: str, projected_graph_id: str) -> dict:
    geom_by_id = geometry_map(gcs)
    if projection == "geometry_primal":
        vertices = sorted(geom_by_id.keys(), key=sort_key)
        edges = geometry_primal_edges(gcs)
        rule = "geometries sharing one constraint are connected"
    elif projection == "incidence_bipartite":
        vertices = [f"G{gid}" for gid in sorted(geom_by_id.keys(), key=sort_key)]
        vertices.extend(f"C{c['id']}" for c in sorted(gcs.get("constraints", []), key=lambda c: c["id"]))
        edges = []
        for constraint in sorted(gcs.get("constraints", []), key=lambda c: c["id"]):
            for gid in sorted(constraint.get("geometry_ids", []), key=sort_key):
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
        edges = unique_edges(edges)
        rule = "rigid sets as nodes, edge if constraints connect different rigid sets"
    else:
        return {"error": f"Unknown projection: {projection}"}

    return {
        "projected_graph_id": projected_graph_id,
        "source_gcs_graph_id": gcs_graph_id,
        "projection": projection,
        "vertices": vertices,
        "edges": edges,
        "projection_rule": rule,
    }

