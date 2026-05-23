"""Generator-local GCS schema validation."""

from __future__ import annotations

import math
from collections import Counter, defaultdict

from .contracts import CONSTRAINT_TYPES, GEOMETRY_TYPES, is_valid_constraint_signature
from .gcs_model import constraint_has_distinct_rigid_sets


def _vec_len(values) -> float:
    return math.sqrt(sum(values[i] * values[i] for i in range(3)))


def validate_gcs_schema(gcs: dict) -> dict:
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
            if not constraint_has_distinct_rigid_sets(constraint, geom_by_id):
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

