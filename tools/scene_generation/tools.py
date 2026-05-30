#!/usr/bin/env python3
"""GCS scene-generation tools.

Entry point:
    python tools.py <command> --input '<json>'

`tools.py` is the compatibility CLI facade. Stable contracts, storage rules,
and promotion adapters live under `gcs_scene_generation/` so later modules can
be split without changing command names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOL_DIR not in sys.path:
    sys.path.insert(0, TOOL_DIR)

from gcs_scene_generation import contracts as scene_contracts
from gcs_scene_generation import enumerator as enumerator_module
from gcs_scene_generation import explorer as explorer_module
from gcs_scene_generation import gcs_model
from gcs_scene_generation import parameterization
from gcs_scene_generation import projection as projection_adapters
from gcs_scene_generation import promotion as promotion_adapters
from gcs_scene_generation import promotion_package
from gcs_scene_generation import reporting
from gcs_scene_generation import repair as repair_module
from gcs_scene_generation import storage as scene_storage
from gcs_scene_generation import topology
from gcs_scene_generation import validation as validation_adapters

REPO_ROOT = os.path.abspath(os.path.join(TOOL_DIR, "..", ".."))
STORE_DIR = os.environ.get(
    "GCS_SCENE_GENERATION_STORE_DIR",
    os.path.join(TOOL_DIR, ".store"),
)
DEFAULT_GCS_EXE = os.path.join(
    REPO_ROOT,
    "out",
    "build",
    "clang-ninja",
    "GCS.exe" if os.name == "nt" else "GCS",
)

GEOMETRY_TYPES = scene_contracts.GEOMETRY_TYPES
CONSTRAINT_TYPES = scene_contracts.CONSTRAINT_TYPES
CONSTRAINT_TYPE_PREFERENCE = scene_contracts.CONSTRAINT_TYPE_PREFERENCE
VALID_CONSTRAINT_SIGNATURES = scene_contracts.VALID_CONSTRAINT_SIGNATURES
GEOMETRY_TYPE_MAP = scene_contracts.GEOMETRY_TYPE_MAP
CONSTRAINT_TYPE_MAP = scene_contracts.CONSTRAINT_TYPE_MAP
FAILURE_REASON_CODES = scene_contracts.FAILURE_REASON_CODES
is_valid_constraint_signature = scene_contracts.is_valid_constraint_signature


# ---------------------------------------------------------------------------
# Stable storage
# ---------------------------------------------------------------------------


def _store_adapter() -> scene_storage.SceneGenerationStore:
    return scene_storage.SceneGenerationStore(STORE_DIR)


def _store_path(graph_id: str) -> str:
    return _store_adapter().store_path(graph_id)


def save_graph(graph_id: str, data: dict) -> None:
    _store_adapter().save_graph(graph_id, data)


def load_graph(graph_id: str) -> dict:
    return _store_adapter().load_graph(graph_id)


def list_graphs() -> list[dict]:
    return _store_adapter().list_graphs()


def delete_graph(graph_id: str) -> dict:
    return _store_adapter().delete_graph(graph_id)


def _safe_store_id(value: str, field_name: str = "id") -> str:
    return _store_adapter().safe_store_id(value, field_name)


def _write_json_file(path: str, data: dict | list) -> None:
    _store_adapter().write_json_file(path, data)


def _read_json_file(path: str) -> dict:
    return _store_adapter().read_json_file(path)


def _exploration_root(exploration_id: str) -> str:
    return _store_adapter().exploration_root(exploration_id)


def _enumeration_root(enumeration_id: str) -> str:
    return _store_adapter().enumeration_root(enumeration_id)


def _promotion_root(promotion_id: str) -> str:
    return _store_adapter().promotion_root(promotion_id)


def _candidate_slot(candidate_id: str) -> str:
    return _store_adapter().candidate_slot(candidate_id)


def _candidate_root(exploration_id: str, candidate_id: str) -> str:
    return _store_adapter().candidate_root(exploration_id, candidate_id)


def _append_trace(trace_path: str, event: dict) -> None:
    _store_adapter().append_trace(trace_path, event)


def _sha256_text(text: str) -> str:
    return _store_adapter().sha256_text(text)


# ---------------------------------------------------------------------------
# Generic graph helpers
# ---------------------------------------------------------------------------


def _sort_key(value):
    return topology.sort_key(value)


def _canonical_edge(u, v):
    return topology.canonical_edge(u, v)


def _unique_edges(edges) -> list[list]:
    return topology.unique_edges(edges)


def build_adjacency(vertices, edges) -> dict:
    return topology.build_adjacency(vertices, edges)


def connected_components(vertices, edges) -> list[list]:
    return topology.connected_components(vertices, edges)


def tarjan_articulation_bcc(vertices, edges) -> tuple[list, list[dict], int]:
    return topology.tarjan_articulation_bcc(vertices, edges)


def _geometry_primal_edges(gcs: dict) -> list[list[int]]:
    return gcs_model.geometry_primal_edges(gcs)


def _generated_id(prefix: str, rng: random.Random) -> str:
    return f"{prefix}_{rng.randint(1, 999):03d}"


def _rng(seed) -> random.Random:
    return random.Random(seed)


# ---------------------------------------------------------------------------
# GCS model helpers
# ---------------------------------------------------------------------------


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
    gcs_model.rebuild_rigid_sets(gcs, num_rigid_sets)


def _geometry_map(gcs: dict) -> dict:
    return gcs_model.geometry_map(gcs)


def _constraint_has_distinct_rigid_sets(constraint: dict, geom_by_id: dict) -> bool:
    return gcs_model.constraint_has_distinct_rigid_sets(constraint, geom_by_id)


def _graph_coloring(vertices, edges, requested_colors: int, rng: random.Random, randomize: bool = False) -> dict | None:
    return gcs_model.graph_coloring(vertices, edges, requested_colors, rng, randomize)


def _assign_rigid_sets_for_edges(
    vertices,
    edges,
    requested_count: int,
    rng: random.Random,
    assignment: str,
    allow_new_rigid_sets: bool,
) -> tuple[dict, int, bool]:
    return gcs_model.assign_rigid_sets_for_edges(
        vertices,
        edges,
        requested_count,
        rng,
        assignment,
        allow_new_rigid_sets,
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

    projected_graph_id = params.get("projected_graph_id", _generated_id("proj", rng))
    result = projection_adapters.project_gcs_graph(gcs_graph_id, gcs, projection, projected_graph_id)
    if "error" in result:
        return result
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

    return validation_adapters.validate_gcs_schema(gcs)


# ---------------------------------------------------------------------------
# Command: repair_gcs_graph
# ---------------------------------------------------------------------------


def tool_repair_gcs_graph(params: dict) -> dict:
    gcs_graph_id = params["gcs_graph_id"]
    target_repairs = params.get("target_repairs", [])
    policy_name = params.get("repair_policy", "minimal_change")

    try:
        original = load_graph(gcs_graph_id)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    repaired_id = params.get("repaired_gcs_graph_id", f"{gcs_graph_id}_repaired")
    result = repair_module.repair_gcs_graph(
        original,
        list(target_repairs),
        repair_policy=policy_name,
        seed=params.get("seed"),
        repaired_gcs_graph_id=repaired_id,
    )
    if "error" in result:
        return result
    repaired_graph = result.pop("_repaired_graph")
    save_graph(repaired_id, repaired_graph)
    return result


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

    return reporting.generate_graph_report(gcs_graph_id, gcs, include)


def tool_assign_geometry_parameters(params: dict) -> dict:
    gcs_graph_id = params["gcs_graph_id"]
    layout = params.get("layout", "circular")
    layout_params = params.get("layout_params", {})
    rng = _rng(params.get("seed"))

    try:
        gcs = load_graph(gcs_graph_id)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    try:
        gcs = parameterization.assign_geometry_parameters(gcs, layout, layout_params, rng)
    except ValueError as exc:
        return {"error": str(exc)}

    save_graph(gcs_graph_id, gcs)
    return {
        "gcs_graph_id": gcs_graph_id,
        "status": "parameters_assigned",
        "num_geometries": len(gcs.get("geometries", [])),
        "num_constraints": len(gcs.get("constraints", [])),
    }


# ---------------------------------------------------------------------------
# Command: explore_scene_space
# ---------------------------------------------------------------------------


def _make_explorer_services() -> explorer_module.ExplorerServices:
    return explorer_module.ExplorerServices(
        store=_store_adapter(),
        generate_skeleton_graph=tool_generate_skeleton_graph,
        lift_skeleton_to_gcs=tool_lift_skeleton_to_gcs,
        assign_geometry_parameters=tool_assign_geometry_parameters,
        validate_gcs_schema=tool_validate_gcs_schema,
        project_gcs_graph=tool_project_gcs_graph,
        check_vertex_biconnected=tool_check_vertex_biconnected,
        generate_graph_report=tool_generate_graph_report,
        serialize_gcs_graph=tool_serialize_gcs_graph,
        load_graph=load_graph,
        save_graph=save_graph,
        promote_candidate=tool_promote_candidate,
        public_adapter_gates=_public_adapter_gates,
    )


def _as_int_list(value, default: list[int]) -> list[int]:
    return explorer_module.as_int_list(value, default)


def _as_str_list(value, default: list[str]) -> list[str]:
    return explorer_module.as_str_list(value, default)


def _extra_edge_values(value) -> list[int]:
    return explorer_module.extra_edge_values(value)


def _default_exploration_request(params: dict) -> dict:
    return explorer_module.default_exploration_request(params)


def _candidate_seed(seed: int, candidate_index: int, offset: int) -> int:
    return explorer_module.candidate_seed(seed, candidate_index, offset)


def _geometry_distribution(geometry_types: list[str]) -> dict:
    return explorer_module.geometry_distribution(geometry_types)


def _endpoint_signature(g1: dict, g2: dict) -> str:
    return explorer_module.endpoint_signature(g1, g2)


def _candidate_record(gcs: dict, report: dict, gates: list[dict], serialization: dict, variant: str) -> dict:
    return explorer_module.candidate_record(gcs, report, gates, serialization, variant)


def _make_gate(gate_id: str, status: str, reason_code: str | None = None, evidence=None, artifact_ids=None) -> dict:
    return promotion_package.make_gate(gate_id, status, reason_code, evidence, artifact_ids)


def _canonical_public_scene_text(scene: dict) -> str:
    return promotion_adapters.canonical_public_scene_text(scene)


def _public_scene_root() -> str:
    return promotion_adapters.public_scene_root(_store_adapter().store_dir)


def _public_scene_path(public_scene_id: str) -> str:
    return promotion_adapters.public_scene_path(_store_adapter().store_dir, public_scene_id)


def _solver_scene_from_gcs(gcs: dict) -> dict:
    return promotion_adapters.solver_scene_from_gcs(gcs)


def _write_public_scene(gcs_graph_id: str) -> dict:
    gcs = load_graph(gcs_graph_id)
    return promotion_adapters.write_public_scene(_store_adapter().store_dir, gcs_graph_id, gcs)


def _validate_public_scene_kernel(scene: dict) -> tuple[bool, list[dict]]:
    return promotion_adapters.validate_public_scene_kernel(scene)


def _normalize_solver_command(public_gate_config: dict | None) -> list[str]:
    return promotion_adapters.normalize_solver_command(public_gate_config, DEFAULT_GCS_EXE)


def _command_available(command: list[str]) -> bool:
    return promotion_adapters.command_available(command)


def _trim_lines(text: str, limit: int = 40) -> list[str]:
    return promotion_adapters.trim_lines(text, limit)


def _run_solver_smoke(scene_path: str, public_gate_config: dict | None) -> dict:
    return promotion_adapters.run_solver_smoke(scene_path, public_gate_config, REPO_ROOT, DEFAULT_GCS_EXE)


def _runtime_public_gates(smoke: dict, unavailable_status: str) -> list[dict]:
    return promotion_package.runtime_public_gates(smoke, unavailable_status)


def _public_adapter_gates(gcs_graph_id: str,
                          projection: dict,
                          gate_profile: str,
                          allow_unsupported: bool,
                          public_gate_config: dict | None) -> list[dict]:
    return promotion_package.public_adapter_gates(
        _store_adapter(),
        REPO_ROOT,
        DEFAULT_GCS_EXE,
        gcs_graph_id,
        load_graph(gcs_graph_id),
        projection,
        gate_profile,
        allow_unsupported,
        public_gate_config,
    )


def _run_candidate_gates(gcs_graph_id: str,
                         projection_id: str,
                         gate_profile: str,
                         allow_unsupported: bool = False,
                         public_gate_config: dict | None = None) -> tuple[list[dict], dict, dict, dict]:
    return explorer_module.run_candidate_gates(
        _make_explorer_services(),
        gcs_graph_id,
        projection_id,
        gate_profile,
        allow_unsupported,
        public_gate_config,
    )


def _first_violation_reason(validation: dict) -> str:
    return explorer_module.first_violation_reason(validation)


def _topology_failure_reason(biconnectivity: dict) -> str:
    return explorer_module.topology_failure_reason(biconnectivity)


def _candidate_failure_reason(gates: list[dict]) -> str:
    return explorer_module.candidate_failure_reason(gates)


def _coverage_from_records(accepted_records: list[dict], rejected_records: list[dict], request: dict) -> dict:
    return explorer_module.coverage_from_records(accepted_records, rejected_records, request)


def _candidate_score(record: dict, before_coverage: dict, after_coverage: dict) -> float:
    return explorer_module.candidate_score(record, before_coverage, after_coverage)


def _save_candidate_artifacts(exploration_id: str, candidate_id: str, artifacts: dict, provenance: dict, report: dict, projection: dict) -> None:
    explorer_module.save_candidate_artifacts(
        _make_explorer_services(),
        exploration_id,
        candidate_id,
        artifacts,
        provenance,
        report,
        projection,
    )


def _invalid_constraint_type_for(g1: dict, g2: dict) -> str | None:
    return explorer_module.invalid_constraint_type_for(g1, g2)


def _make_negative_candidate(base_gcs_id: str, negative_gcs_id: str, variant: str) -> dict:
    return explorer_module.make_negative_candidate(_make_explorer_services(), base_gcs_id, negative_gcs_id, variant)


def _build_positive_candidate(request: dict, candidate_index: int, combo: dict) -> tuple[dict, dict, dict, dict, dict, list[dict]]:
    return explorer_module.build_positive_candidate(_make_explorer_services(), request, candidate_index, combo)


def _build_candidate_combos(request: dict) -> list[dict]:
    return explorer_module.build_candidate_combos(request)


def tool_explore_scene_space(params: dict) -> dict:
    return explorer_module.explore_scene_space(params, _make_explorer_services())


def tool_enumerate_scene_space(params: dict) -> dict:
    """Enumerate all valid constraint graphs for fixed small parameters."""
    services = enumerator_module.EnumeratorServices(
        store=_store_adapter(),
        save_graph=save_graph,
        load_graph=load_graph,
    )
    return enumerator_module.enumerate_scene_space(params, services)


# ---------------------------------------------------------------------------
# Command: promote_candidate
# ---------------------------------------------------------------------------


def _load_candidate_provenance(exploration_id: str, candidate_id: str) -> dict:
    return promotion_package.load_candidate_provenance(_store_adapter(), exploration_id, candidate_id)


def tool_promote_candidate(params: dict) -> dict:
    try:
        exploration_id = _safe_store_id(params["exploration_id"], "exploration_id")
        candidate_id = _safe_store_id(params["candidate_id"], "candidate_id")
        promotion_id = _safe_store_id(params.get("promotion_id", f"{candidate_id}_promotion"), "promotion_id")
    except (KeyError, ValueError) as exc:
        return {"status": "failed", "reason_code": "invalid_request", "error": str(exc)}

    gate_profile = params.get("gate_profile", "promotion")
    allow_unsupported = bool(params.get("allow_unsupported_gates", False))
    copy_to_fixtures = bool(params.get("copy_to_fixtures", False))
    public_gate_config = dict(params.get("public_gate_config", {}))
    if "gcs_exe" in params:
        public_gate_config["gcs_exe"] = params["gcs_exe"]
    if "solver_command" in params:
        public_gate_config["solver_command"] = params["solver_command"]

    try:
        provenance = _load_candidate_provenance(exploration_id, candidate_id)
        gcs_graph_id = provenance["artifacts"]["gcs_graph_id"]
        if not os.path.exists(_store_path(gcs_graph_id)):
            nested_gcs_path = os.path.join(_candidate_root(exploration_id, candidate_id), "gcs.json")
            if os.path.exists(nested_gcs_path):
                save_graph(gcs_graph_id, _read_json_file(nested_gcs_path))
        projection_id = f"{candidate_id}_promotion_geom_primal"
        gates, report, projection, json_serialization = _run_candidate_gates(
            gcs_graph_id,
            projection_id,
            gate_profile,
            allow_unsupported,
            public_gate_config,
        )
        text_serialization = tool_serialize_gcs_graph({"gcs_graph_id": gcs_graph_id, "format": "custom_text_v1"})
        public_scene = _solver_scene_from_gcs(load_graph(gcs_graph_id))
    except Exception as exc:
        return {"status": "failed", "reason_code": "invalid_request", "error": str(exc)}

    package = promotion_package.build_promotion_package(
        promotion_id,
        exploration_id,
        candidate_id,
        gcs_graph_id,
        provenance,
        report,
        gates,
        json_serialization,
        text_serialization,
        public_scene,
    )
    status = package["status"]
    reason_code = package["reason_code"]
    root = promotion_package.write_promotion_artifacts(
        _store_adapter(),
        promotion_id,
        package,
        projection,
        load_graph(gcs_graph_id),
        public_scene,
    )

    copied_fixture_path = None
    if copy_to_fixtures and status == "promotion_package_written":
        fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fixtures", "scene", "generated"))
        copied_fixture_path = os.path.join(fixture_dir, f"{candidate_id}.gcs.json")
        _write_json_file(copied_fixture_path, public_scene)
    elif copy_to_fixtures and status != "promotion_package_written":
        package["copy_to_fixtures_blocked"] = True
        _write_json_file(os.path.join(root, "package.json"), package)

    return {
        "promotion_id": promotion_id,
        "status": status,
        "reason_code": reason_code,
        "package_id": promotion_id,
        "copied_fixture_path": copied_fixture_path,
        "known_unsupported_gates": package["known_unsupported_gates"],
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
    "explore_scene_space": tool_explore_scene_space,
    "enumerate_scene_space": tool_enumerate_scene_space,
    "promote_candidate": tool_promote_candidate,
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
  python tools.py explore_scene_space --input '{"exploration_id":"demo_explore","seed":45}'
  python tools.py promote_candidate --input '{"exploration_id":"demo_explore","candidate_id":"demo_explore_c0000","gate_profile":"local_only"}'
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
