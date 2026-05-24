"""Stable contracts for generated GCS graph and public scene artifacts."""

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

FAILURE_REASON_CODES = {
    "invalid_request",
    "budget_exhausted",
    "unknown_geometry_type",
    "unknown_constraint_type",
    "invalid_constraint_signature",
    "constraint_same_rigid_set",
    "degenerate_line",
    "zero_plane_normal",
    "negative_distance",
    "invalid_angle_range",
    "topology_not_connected",
    "topology_has_articulation",
    "io_round_trip_failed",
    "kernel_validation_failed",
    "runtime_smoke_failed",
    "diagnostics_evidence_failed",
    "rank_evidence_failed",
    "rank_evidence_missing",
    "viewer_projection_failed",
    "promotion_gate_unsupported",
    "no_coverage_gain",
    "search_exhausted",
}


def is_valid_constraint_signature(ctype: str, gtype1: str, gtype2: str) -> bool:
    signatures = VALID_CONSTRAINT_SIGNATURES.get(ctype, set())
    return (gtype1, gtype2) in signatures or (gtype2, gtype1) in signatures
