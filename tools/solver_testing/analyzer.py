"""Defect analyzer — classification, repair strategy mapping, auto-fix, verification.

Conservative auto-fix policy: only applies mathematically unambiguous fixes
(abs, wrap, clamp). Everything else is flagged for developer review.
"""

from __future__ import annotations

import copy
import math
import os
from dataclasses import dataclass

from .defect_store import DefectRecord, DefectStore, classify_defect
from .mutator import Mutation
from .runner import SolveResult, find_solver, run_single
from tools.scene_generation.gcs_scene_generation.contracts import (
    CONSTRAINT_TYPES,
    FAILURE_REASON_CODES,
    is_valid_constraint_signature,
)
from tools.scene_generation.gcs_scene_generation.promotion import (
    solver_scene_from_gcs,
    write_public_scene,
)
from tools.scene_generation.gcs_scene_generation.storage import SceneGenerationStore


@dataclass
class RepairResult:
    defect_id: str
    repaired: bool
    auto_fix_applied: bool
    strategy: str
    description: str
    verified: bool = False
    verification_output: str = ""
    recommended_action: str = ""  # for developer: suggested fix approach


# ---------------------------------------------------------------------------
# Error → Repair strategy mapping
# ---------------------------------------------------------------------------

REPAIR_STRATEGIES = {
    "negative_distance": {
        "auto_fix": True,
        "description": "Distance value must be non-negative. Apply abs().",
        "apply": "_repair_negative_distance",
    },
    "invalid_angle_range": {
        "auto_fix": True,
        "description": "Angle value should be in [0, pi]. Wrap to range.",
        "apply": "_repair_angle_range",
    },
    "degenerate_geometry": {
        "auto_fix": True,
        "description": "Perturb geometry parameters to avoid degeneracy.",
        "apply": "_repair_degenerate_geometry",
    },
    "solver_crash": {
        "auto_fix": False,
        "description": "Solver crashed. Likely a C++ bug — needs developer investigation.",
        "recommended_action": "Investigate solver crash with attached scene. Check for null dereference, unhandled edge case, or memory error.",
    },
    "solver_timeout": {
        "auto_fix": False,
        "description": "Solver timed out. May indicate infinite loop or pathological convergence.",
        "recommended_action": "Profile solver on this scene. Check iteration bounds and convergence criteria.",
    },
    "solver_failed": {
        "auto_fix": False,
        "description": "Solver failed with unknown error. Review solver output for details.",
        "recommended_action": "Run solver manually on the scene to inspect full output. Check constraint consistency.",
    },
    "diagnostics_lost": {
        "auto_fix": False,
        "description": "Diagnostics present in original but missing in mutated result.",
        "recommended_action": "Review whether the mutation caused diagnostics pipeline to skip. May be benign.",
    },
    "diagnostics_appeared": {
        "auto_fix": False,
        "description": "Diagnostics appeared in mutated result but not in original.",
        "recommended_action": "Likely benign — mutation triggered additional diagnostic checks.",
    },
}


def _repair_negative_distance(gcs_graph: dict, defect: DefectRecord) -> tuple[dict, str]:
    """Fix: take absolute value of negative distance constraints."""
    repaired = copy.deepcopy(gcs_graph)
    for constraint in repaired.get("constraints", []):
        cid_str = str(constraint["id"])
        if cid_str in defect.mutated_values and constraint.get("type") == "Distance":
            value = constraint["value"]
            if isinstance(value, (int, float)) and value < 0:
                constraint["value"] = abs(value)
                return repaired, f"Applied abs() to constraint {constraint['id']}: {value} -> {constraint['value']}"
    return repaired, "No negative distance values found to repair"


def _repair_angle_range(gcs_graph: dict, defect: DefectRecord) -> tuple[dict, str]:
    """Fix: wrap angle values to [0, pi]."""
    repaired = copy.deepcopy(gcs_graph)
    for constraint in repaired.get("constraints", []):
        cid_str = str(constraint["id"])
        if cid_str in defect.mutated_values and constraint.get("type") == "Angle":
            value = constraint["value"]
            if isinstance(value, (int, float)):
                wrapped = value % math.pi
                if wrapped < 0:
                    wrapped += math.pi
                if abs(wrapped - value) > 1e-9:
                    constraint["value"] = round(wrapped, 12)
                    return repaired, f"Wrapped angle constraint {constraint['id']}: {value} -> {constraint['value']}"
    return repaired, "No out-of-range angle values found to repair"


def _repair_degenerate_geometry(gcs_graph: dict, defect: DefectRecord) -> tuple[dict, str]:
    """Fix: apply small perturbation to geometry parameters to escape degeneracy."""
    import random
    rng = random.Random(42)
    repaired = copy.deepcopy(gcs_graph)
    eps = 1e-4
    for geometry in repaired.get("geometries", []):
        v = geometry.get("v", [])
        if all(abs(x) < 1e-9 for x in v):
            for i in range(len(v)):
                v[i] = round(rng.uniform(-eps, eps), 12)
            return repaired, f"Perturbed zero-vector geometry {geometry['id']}"
        gtype = geometry.get("type")
        if gtype == "Line":
            if all(abs(x) < 1e-9 for x in v[3:6]):
                v[3] = round(rng.uniform(-eps, eps), 12)
                v[4] = round(rng.uniform(-eps, eps), 12)
                v[5] = round(1.0 + rng.uniform(-eps, eps), 12)
                return repaired, f"Perturbed zero-direction Line geometry {geometry['id']}"
        elif gtype == "Plane":
            if all(abs(x) < 1e-9 for x in v[3:6]):
                v[3] = round(rng.uniform(-eps, eps), 12)
                v[4] = round(rng.uniform(-eps, eps), 12)
                v[5] = round(1.0 + rng.uniform(-eps, eps), 12)
                return repaired, f"Perturbed zero-normal Plane geometry {geometry['id']}"
    return repaired, "No degenerate geometries found to repair"


def analyze_defect(defect: DefectRecord) -> RepairResult:
    """Analyze a defect and determine repair strategy."""
    error_type = defect.error_type
    strategy_info = REPAIR_STRATEGIES.get(error_type)

    if strategy_info is None:
        return RepairResult(
            defect_id=defect.defect_id,
            repaired=False,
            auto_fix_applied=False,
            strategy="unknown",
            description=f"No repair strategy for error type '{error_type}'",
            recommended_action="Manual investigation required.",
        )

    if not strategy_info["auto_fix"]:
        return RepairResult(
            defect_id=defect.defect_id,
            repaired=False,
            auto_fix_applied=False,
            strategy=error_type,
            description=strategy_info["description"],
            recommended_action=strategy_info.get("recommended_action", "Manual investigation required."),
        )

    return RepairResult(
        defect_id=defect.defect_id,
        repaired=False,
        auto_fix_applied=True,
        strategy=error_type,
        description=strategy_info["description"],
    )


def apply_repair(gcs_graph: dict, defect: DefectRecord) -> tuple[dict, str]:
    """Apply auto-fix to a GCS graph based on defect error type."""
    strategy_info = REPAIR_STRATEGIES.get(defect.error_type)
    if strategy_info is None or not strategy_info.get("auto_fix"):
        return gcs_graph, "No auto-fix available"

    method_name = strategy_info["apply"]
    method_map = {
        "_repair_negative_distance": _repair_negative_distance,
        "_repair_angle_range": _repair_angle_range,
        "_repair_degenerate_geometry": _repair_degenerate_geometry,
    }
    repair_fn = method_map.get(method_name)
    if repair_fn is None:
        return gcs_graph, f"Repair function '{method_name}' not found"

    return repair_fn(gcs_graph, defect)


def verify_repair(
    repaired_gcs: dict,
    gcs_graph_id: str,
    store: SceneGenerationStore,
    solver_command: list[str] | None = None,
) -> tuple[bool, str]:
    """Verify a repair by running the solver on the repaired scene."""
    if solver_command is None:
        solver_command = find_solver()
    if solver_command is None:
        return False, "Solver not available for verification"

    import tempfile
    public_scene = solver_scene_from_gcs(repaired_gcs)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".gcs.json", delete=False) as f:
        import json
        json.dump(public_scene, f)
        tmp_path = f.name

    try:
        result = run_single(tmp_path, gcs_graph_id, solver_command)
        ok = result.status == "solved" and result.exit_code == 0
        return ok, f"exit={result.exit_code} status={result.status} stderr={result.stderr[:100]}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def analyze_and_repair_defects(
    defect_store: DefectStore,
    gcs_store: SceneGenerationStore,
    solver_command: list[str] | None = None,
) -> dict:
    """Full analysis + repair pipeline over all defects in a store.

    Returns summary dict with counts and per-defect repair results.
    """
    all_defects = defect_store.list_all()
    results = {
        "total": len(all_defects),
        "auto_fixed": 0,
        "auto_fix_verified": 0,
        "requires_developer": 0,
        "defects": [],
    }

    for entry in all_defects:
        defect = DefectRecord.from_dict(entry)
        analysis = analyze_defect(defect)

        defect_result = {
            "defect_id": defect.defect_id,
            "error_type": defect.error_type,
            "severity": defect.severity,
            "can_auto_fix": analysis.auto_fix_applied,
            "repaired": False,
            "verified": False,
            "repair_description": "",
            "recommended_action": analysis.recommended_action,
        }

        if analysis.auto_fix_applied:
            try:
                gcs = gcs_store.load_graph(defect.scene_id)
            except FileNotFoundError:
                defect_result["repair_description"] = "Scene not found in store"
                results["defects"].append(defect_result)
                continue

            repaired_gcs, repair_msg = apply_repair(gcs, defect)
            defect_result["repair_description"] = repair_msg

            verified, verify_msg = verify_repair(
                repaired_gcs, defect.scene_id, gcs_store, solver_command,
            )
            defect_result["repaired"] = verified
            defect_result["verified"] = verified
            defect_result["verification_output"] = verify_msg

            if verified:
                gcs_store.save_graph(defect.scene_id, repaired_gcs)
                results["auto_fix_verified"] += 1
            results["auto_fixed"] += 1
        else:
            results["requires_developer"] += 1

        results["defects"].append(defect_result)

    return results
