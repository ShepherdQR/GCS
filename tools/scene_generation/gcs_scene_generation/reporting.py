"""Machine-readable graph reports for generated GCS graphs."""

from __future__ import annotations

from collections import Counter

from .gcs_model import geometry_primal_edges
from .topology import sort_key, tarjan_articulation_bcc
from .validation import validate_gcs_schema


def generate_graph_report(gcs_graph_id: str, gcs: dict, include: list[str]) -> dict:
    vertices = sorted([g["id"] for g in gcs.get("geometries", [])], key=sort_key)
    edges = geometry_primal_edges(gcs)
    report = {
        "graph_id": gcs_graph_id,
        "summary": {
            "num_rigid_sets": len(gcs.get("rigid_sets", [])),
            "num_geometries": len(gcs.get("geometries", [])),
            "num_constraints": len(gcs.get("constraints", [])),
        },
    }

    if "schema_validation" in include:
        validation = validate_gcs_schema(gcs)
        report["schema_valid"] = validation.get("valid", False)
        report["schema_violations"] = validation.get("violations", [])
        report["rigid_set_invariant_valid"] = not any(
            v.get("type") == "constraint_same_rigid_set" for v in validation.get("violations", [])
        )

    if "projection_statistics" in include:
        report["projection_statistics"] = {
            "num_vertices": len(vertices),
            "num_edges": len(edges),
            "projection": "geometry_primal",
        }

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

