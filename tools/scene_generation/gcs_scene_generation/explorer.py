"""Scene-space exploration orchestration for generated GCS candidates."""

from __future__ import annotations

import copy
import os
import random
import time
from collections import Counter
from dataclasses import dataclass
from typing import Callable

from . import gcs_model
from .contracts import CONSTRAINT_TYPES, FAILURE_REASON_CODES, GEOMETRY_TYPES, is_valid_constraint_signature
from .promotion_package import make_gate
from .storage import SceneGenerationStore, safe_store_id, sha256_text


@dataclass(frozen=True)
class ExplorerServices:
    store: SceneGenerationStore
    generate_skeleton_graph: Callable[[dict], dict]
    lift_skeleton_to_gcs: Callable[[dict], dict]
    assign_geometry_parameters: Callable[[dict], dict]
    validate_gcs_schema: Callable[[dict], dict]
    project_gcs_graph: Callable[[dict], dict]
    check_vertex_biconnected: Callable[[dict], dict]
    generate_graph_report: Callable[[dict], dict]
    serialize_gcs_graph: Callable[[dict], dict]
    load_graph: Callable[[str], dict]
    save_graph: Callable[[str, dict], None]
    promote_candidate: Callable[[dict], dict] | None = None
    public_adapter_gates: Callable[[str, dict, str, bool, dict | None], list[dict]] | None = None


def as_int_list(value, default: list[int]) -> list[int]:
    if value is None:
        return list(default)
    if isinstance(value, int):
        return [int(value)]
    return [int(item) for item in value]


def as_str_list(value, default: list[str]) -> list[str]:
    if value is None:
        return list(default)
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def extra_edge_values(value) -> list[int]:
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


def default_exploration_request(params: dict) -> dict:
    seed = int(params.get("seed", 0))
    exploration_id = safe_store_id(params.get("exploration_id", f"exploration_{seed}"), "exploration_id")
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
            "vertex_counts": as_int_list(topology_policy.get("vertex_counts"), [3, 4, 5, 8]),
            "methods": as_str_list(topology_policy.get("methods"), ["cycle_plus_chords", "ear_decomposition"]),
            "extra_edge_values": extra_edge_values(topology_policy.get("extra_edge_range")),
            "require_vertex_biconnected": bool(topology_policy.get("require_vertex_biconnected", True)),
        },
        "gcs_policy": {
            "geometry_types": as_str_list(gcs_policy.get("geometry_types"), list(GEOMETRY_TYPES)),
            "constraint_types": as_str_list(gcs_policy.get("constraint_types"), list(CONSTRAINT_TYPES)),
            "rigid_set_counts": as_int_list(gcs_policy.get("rigid_set_counts"), [2, 3]),
            "require_cross_rigid_set_constraints": bool(gcs_policy.get("require_cross_rigid_set_constraints", True)),
        },
        "parameter_policy": {
            "layouts": as_str_list(parameter_policy.get("layouts"), ["circular", "grid", "random"]),
            "avoid_degenerate_geometry": bool(parameter_policy.get("avoid_degenerate_geometry", True)),
            "value_tolerance": float(parameter_policy.get("value_tolerance", 1e-9)),
        },
        "coverage_goals": as_str_list(
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


def candidate_seed(seed: int, candidate_index: int, offset: int) -> int:
    return (int(seed) * 100_003 + candidate_index * 101 + offset) % 2_147_483_647


def rng(seed) -> random.Random:
    return random.Random(seed)


def geometry_distribution(geometry_types: list[str]) -> dict:
    if not geometry_types:
        return {}
    weight = 1.0 / len(geometry_types)
    return {gtype: weight for gtype in geometry_types}


def endpoint_signature(g1: dict, g2: dict) -> str:
    return "-".join(sorted([g1.get("type", "?"), g2.get("type", "?")]))


def candidate_record(gcs: dict, report: dict, gates: list[dict], serialization: dict, variant: str) -> dict:
    geom_by_id = gcs_model.geometry_map(gcs)
    geometry_hist = Counter(g.get("type") for g in gcs.get("geometries", []))
    constraint_hist = Counter(c.get("type") for c in gcs.get("constraints", []))
    signature_hist = Counter()
    for constraint in gcs.get("constraints", []):
        gids = constraint.get("geometry_ids", [])
        if len(gids) >= 2 and gids[0] in geom_by_id and gids[1] in geom_by_id:
            signature_hist[endpoint_signature(geom_by_id[gids[0]], geom_by_id[gids[1]])] += 1
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
        "digest": sha256_text(serialization.get("serialization", "")),
    }


def first_violation_reason(validation: dict) -> str:
    violations = validation.get("violations", [])
    if not violations:
        return "invalid_request"
    reason = violations[0].get("type", "invalid_request")
    return reason if reason in FAILURE_REASON_CODES else "invalid_request"


def topology_failure_reason(biconnectivity: dict) -> str:
    if int(biconnectivity.get("num_connected_components") or 0) != 1:
        return "topology_not_connected"
    if biconnectivity.get("articulation_points"):
        return "topology_has_articulation"
    return "topology_has_articulation"


def candidate_failure_reason(gates: list[dict]) -> str:
    for gate in gates:
        if gate["status"] == "failed":
            reason = gate.get("reason_code") or "invalid_request"
            return reason if reason in FAILURE_REASON_CODES else "invalid_request"
    for gate in gates:
        if gate["status"] == "unsupported":
            return "promotion_gate_unsupported"
    return "invalid_request"


def run_candidate_gates(
    services: ExplorerServices,
    gcs_graph_id: str,
    projection_id: str,
    gate_profile: str,
    allow_unsupported: bool = False,
    public_gate_config: dict | None = None,
) -> tuple[list[dict], dict, dict, dict]:
    validation = services.validate_gcs_schema({"gcs_graph_id": gcs_graph_id})
    projection = services.project_gcs_graph(
        {
            "gcs_graph_id": gcs_graph_id,
            "projection": "geometry_primal",
            "projected_graph_id": projection_id,
        }
    )
    biconnectivity = services.check_vertex_biconnected({"projected_graph_id": projection_id})
    report = services.generate_graph_report({"gcs_graph_id": gcs_graph_id})
    serialization = services.serialize_gcs_graph({"gcs_graph_id": gcs_graph_id, "format": "json"})

    gates = [
        make_gate(
            "local_schema_validation",
            "passed" if validation.get("valid") else "failed",
            None if validation.get("valid") else first_violation_reason(validation),
            {"violations": validation.get("violations", [])},
            [gcs_graph_id],
        ),
        make_gate(
            "geometry_primal_projection",
            "passed" if "error" not in projection else "failed",
            projection.get("error"),
            {"num_vertices": len(projection.get("vertices", [])), "num_edges": len(projection.get("edges", []))},
            [projection_id],
        ),
        make_gate(
            "geometry_primal_biconnectivity",
            "passed" if biconnectivity.get("is_vertex_biconnected") else "failed",
            None if biconnectivity.get("is_vertex_biconnected") else topology_failure_reason(biconnectivity),
            {
                "articulation_points": biconnectivity.get("articulation_points", []),
                "num_connected_components": biconnectivity.get("num_connected_components"),
            },
            [projection_id],
        ),
        make_gate(
            "canonical_serialization",
            "passed" if serialization.get("canonical") else "failed",
            None if serialization.get("canonical") else serialization.get("error", "serialization_failed"),
            {"checksum": serialization.get("checksum"), "format": serialization.get("format")},
            [gcs_graph_id],
        ),
    ]

    if gate_profile in {"local_plus_public_smoke", "promotion"}:
        if services.public_adapter_gates is None:
            gates.append(
                make_gate(
                    "public_adapter_gates",
                    "unsupported",
                    "promotion_gate_unsupported",
                    {"message": "No public adapter gate runner was provided."},
                    [gcs_graph_id],
                )
            )
        else:
            gates.extend(
                services.public_adapter_gates(
                    gcs_graph_id,
                    projection,
                    gate_profile,
                    allow_unsupported,
                    public_gate_config,
                )
            )
    return gates, report, projection, serialization


def coverage_from_records(accepted_records: list[dict], rejected_records: list[dict], request: dict) -> dict:
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


def candidate_score(record: dict, before_coverage: dict, after_coverage: dict) -> float:
    before_goals = set(before_coverage.get("satisfied_goals", []))
    after_goals = set(after_coverage.get("satisfied_goals", []))
    new_goals = len(after_goals - before_goals)
    geometry_diversity = len(record.get("geometry_types", {}))
    constraint_diversity = len(record.get("constraint_types", {}))
    simplicity = 1.0 / max(1, int(record.get("num_constraints", 1)))
    return round(new_goals * 10.0 + geometry_diversity + constraint_diversity + simplicity, 6)


def save_candidate_artifacts(
    services: ExplorerServices,
    exploration_id: str,
    candidate_id: str,
    artifacts: dict,
    provenance: dict,
    report: dict,
    projection: dict,
) -> None:
    root = services.store.candidate_root(exploration_id, candidate_id)
    services.store.write_json_file(os.path.join(root, "provenance.json"), provenance)
    services.store.write_json_file(os.path.join(root, "report.json"), report)
    services.store.write_json_file(os.path.join(root, "geometry_primal.json"), projection)
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
            services.store.write_json_file(os.path.join(root, f"{file_role}.json"), services.load_graph(graph_id))
        except FileNotFoundError:
            pass


def invalid_constraint_type_for(g1: dict, g2: dict) -> str | None:
    for ctype in CONSTRAINT_TYPES:
        if not is_valid_constraint_signature(ctype, g1.get("type"), g2.get("type")):
            return ctype
    return None


def make_negative_candidate(services: ExplorerServices, base_gcs_id: str, negative_gcs_id: str, variant: str) -> dict:
    base = services.load_graph(base_gcs_id)
    gcs = copy.deepcopy(base)
    gcs["gcs_graph_id"] = negative_gcs_id
    gcs["status"] = variant
    geom_by_id = gcs_model.geometry_map(gcs)
    if variant == "invalid_signature_negative_case":
        for constraint in sorted(gcs.get("constraints", []), key=lambda c: c["id"]):
            gids = constraint.get("geometry_ids", [])
            if len(gids) < 2 or gids[0] not in geom_by_id or gids[1] not in geom_by_id:
                continue
            invalid = invalid_constraint_type_for(geom_by_id[gids[0]], geom_by_id[gids[1]])
            if invalid:
                constraint["type"] = invalid
                services.save_graph(negative_gcs_id, gcs)
                return gcs
    elif variant == "same_rigid_set_negative_case":
        for constraint in sorted(gcs.get("constraints", []), key=lambda c: c["id"]):
            gids = constraint.get("geometry_ids", [])
            if len(gids) < 2 or gids[0] not in geom_by_id or gids[1] not in geom_by_id:
                continue
            geom_by_id[gids[1]]["rigid_set_id"] = geom_by_id[gids[0]]["rigid_set_id"]
            gcs_model.rebuild_rigid_sets(gcs)
            services.save_graph(negative_gcs_id, gcs)
            return gcs
    raise ValueError(f"Could not create negative candidate variant {variant}")


def build_positive_candidate(
    services: ExplorerServices,
    request: dict,
    candidate_index: int,
    combo: dict,
) -> tuple[dict, dict, dict, dict, dict, list[dict]]:
    exploration_id = request["exploration_id"]
    candidate_id = f"{exploration_id}_c{candidate_index:04d}"
    skeleton_id = f"{candidate_id}_skel"
    gcs_id = f"{candidate_id}_gcs"
    projection_id = f"{candidate_id}_geom_primal"
    seed = request["seed"]
    seed_path = {
        "exploration_seed": seed,
        "topology_seed": candidate_seed(seed, candidate_index, 1),
        "lift_seed": candidate_seed(seed, candidate_index, 2),
        "parameter_seed": candidate_seed(seed, candidate_index, 3),
    }

    skeleton = services.generate_skeleton_graph(
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

    lift = services.lift_skeleton_to_gcs(
        {
            "skeleton_graph_id": skeleton_id,
            "gcs_graph_id": gcs_id,
            "seed": seed_path["lift_seed"],
            "geometry_type_policy": {
                "allowed_types": request["gcs_policy"]["geometry_types"],
                "distribution": geometry_distribution(request["gcs_policy"]["geometry_types"]),
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

    assigned = services.assign_geometry_parameters(
        {
            "gcs_graph_id": gcs_id,
            "layout": combo["layout"],
            "seed": seed_path["parameter_seed"],
        }
    )
    if "error" in assigned:
        raise ValueError(assigned["error"])

    gates, report, projection, serialization = run_candidate_gates(
        services,
        gcs_id,
        projection_id,
        request["gate_profile"],
        request["allow_unsupported_gates"],
        request.get("public_gate_config", {}),
    )
    gcs = services.load_graph(gcs_id)
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
        "digest": sha256_text(serialization.get("serialization", "")),
    }
    return gcs, report, projection, serialization, provenance, gates


def build_candidate_combos(request: dict) -> list[dict]:
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
    rng(request["seed"]).shuffle(combos)
    return combos


def explore_scene_space(params: dict, services: ExplorerServices) -> dict:
    try:
        request = default_exploration_request(params)
    except ValueError as exc:
        return {"status": "failed", "reason_code": "invalid_request", "error": str(exc)}

    exploration_id = request["exploration_id"]
    root = services.store.exploration_root(exploration_id)
    trace_path = os.path.join(root, "trace.jsonl")
    os.makedirs(root, exist_ok=True)
    if os.path.exists(trace_path):
        os.remove(trace_path)
    services.store.write_json_file(os.path.join(root, "request.json"), request)

    accepted = []
    accepted_records = []
    rejected = []
    rejected_records = []
    attempted = 0
    event_index = 0
    start = time.monotonic()
    stop_reason = "search_exhausted"
    combos = build_candidate_combos(request)

    def trace(event_type: str, candidate_id: str | None, payload: dict) -> None:
        nonlocal event_index
        event = {
            "event_index": event_index,
            "event_type": event_type,
            "candidate_id": candidate_id,
            "payload": payload,
        }
        event_index += 1
        services.store.append_trace(trace_path, event)

    def should_stop() -> str | None:
        if len(accepted) >= request["budget"]["max_accepts"]:
            return "max_accepts"
        if attempted >= request["budget"]["max_candidates"]:
            return "max_candidates"
        max_seconds = request["budget"]["max_seconds"]
        if max_seconds > 0.0 and (time.monotonic() - start) >= max_seconds:
            return "max_seconds"
        return None

    for combo in combos:
        reason = should_stop()
        if reason:
            stop_reason = reason
            break

        candidate_index = attempted
        candidate_id = f"{exploration_id}_c{candidate_index:04d}"
        attempted += 1
        trace("candidate_started", candidate_id, {"combo": combo})
        try:
            gcs, report, projection, serialization, provenance, gates = build_positive_candidate(services, request, candidate_index, combo)
            record = candidate_record(gcs, report, gates, serialization, "positive")
            before_coverage = coverage_from_records(accepted_records, rejected_records, request)
            candidate_after = accepted_records + [record] if record["schema_valid"] and record["geometry_primal_biconnected"] else accepted_records
            after_coverage = coverage_from_records(candidate_after, rejected_records, request)
            score = candidate_score(record, before_coverage, after_coverage)
            provenance["reports"] = {"graph_report": report, "gates": gates}
            save_candidate_artifacts(services, exploration_id, candidate_id, provenance["artifacts"], provenance, report, projection)
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
                reason_code = candidate_failure_reason(record["gates"]) if not record["schema_valid"] else "no_coverage_gain"
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
            current_coverage = coverage_from_records(accepted_records, rejected_records, request)
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
                make_negative_candidate(services, provenance["artifacts"]["gcs_graph_id"], negative_gcs_id, variant)
                gates, negative_report, negative_projection, negative_serialization = run_candidate_gates(
                    services,
                    negative_gcs_id,
                    negative_projection_id,
                    request["gate_profile"],
                    request["allow_unsupported_gates"],
                    request.get("public_gate_config", {}),
                )
                reason_code = candidate_failure_reason(gates)
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
                    "digest": sha256_text(negative_serialization.get("serialization", "")),
                }
                if request["write_policy"]["keep_rejected"]:
                    save_candidate_artifacts(
                        services,
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

    coverage = coverage_from_records(accepted_records, rejected_records, request)
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
        if services.promote_candidate is None:
            result["promotion_results"] = [
                {
                    "candidate_id": candidate["candidate_id"],
                    "status": "promotion_blocked",
                    "reason_code": "promotion_gate_unsupported",
                    "error": "No promotion service was provided.",
                }
                for candidate in accepted
            ]
        else:
            result["promotion_results"] = [
                services.promote_candidate(
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
    services.store.write_json_file(os.path.join(root, "result.json"), result)
    trace("exploration_finished", None, {"status": status, "stop_reason": stop_reason, "summary": result["summary"]})
    return result
