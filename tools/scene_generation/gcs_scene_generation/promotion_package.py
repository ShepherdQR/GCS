"""Promotion package and public-gate orchestration helpers."""

from __future__ import annotations

import json
import os

from . import promotion
from .storage import candidate_root, promotion_root, read_json_file, sha256_text, write_json_file


def make_gate(gate_id: str, status: str, reason_code: str | None = None, evidence=None, artifact_ids=None) -> dict:
    return {
        "gate_id": gate_id,
        "status": status,
        "reason_code": reason_code,
        "evidence": evidence or {},
        "artifact_ids": artifact_ids or [],
        "duration_ms": 0,
    }


def runtime_public_gates(smoke: dict, unavailable_status: str) -> list[dict]:
    if not smoke.get("available"):
        evidence = {
            "command": smoke.get("command", []),
            "stderr_lines": smoke.get("stderr_lines", []),
            "message": "Set GCS_EXE or public_gate_config.solver_command to enable CLI public gates.",
        }
        return [
            make_gate("runtime_smoke", unavailable_status, "runtime_smoke_failed", evidence),
            make_gate("diagnostics_evidence", unavailable_status, "diagnostics_evidence_failed", evidence),
        ]

    runtime_passed = smoke.get("exit_code") == 0
    output = "\n".join(smoke.get("stdout_lines", []) + smoke.get("stderr_lines", []))
    diagnostics_passed = runtime_passed and "diagnostics" in output and "Status:" in output
    return [
        make_gate(
            "runtime_smoke",
            "passed" if runtime_passed else "failed",
            None if runtime_passed else "runtime_smoke_failed",
            smoke,
        ),
        make_gate(
            "diagnostics_evidence",
            "passed" if diagnostics_passed else "failed",
            None if diagnostics_passed else "diagnostics_evidence_failed",
            {
                "status_line_present": "Status:" in output,
                "diagnostics_line_present": "diagnostics" in output,
                "stdout_lines": smoke.get("stdout_lines", []),
                "stderr_lines": smoke.get("stderr_lines", []),
            },
        ),
    ]


def public_adapter_gates(
    store_dir: str,
    repo_root: str,
    default_gcs_exe: str,
    gcs_graph_id: str,
    gcs: dict,
    projection: dict,
    gate_profile: str,
    allow_unsupported: bool,
    public_gate_config: dict | None,
) -> list[dict]:
    public_scene = promotion.write_public_scene(store_dir, gcs_graph_id, gcs)
    scene_text = promotion.canonical_public_scene_text(public_scene["scene"])
    round_trip = json.loads(scene_text)
    round_trip_digest = sha256_text(promotion.canonical_public_scene_text(round_trip))
    kernel_valid, kernel_issues = promotion.validate_public_scene_kernel(round_trip)
    unavailable_status = "skipped" if gate_profile == "local_plus_public_smoke" or allow_unsupported else "unsupported"
    smoke = promotion.run_solver_smoke(public_scene["path"], public_gate_config, repo_root, default_gcs_exe)

    gates = [
        make_gate(
            "scene_io_round_trip",
            "passed" if round_trip_digest == public_scene["digest"] else "failed",
            None if round_trip_digest == public_scene["digest"] else "io_round_trip_failed",
            {
                "public_scene_id": public_scene["public_scene_id"],
                "path": public_scene["path"],
                "digest": public_scene["digest"],
                "round_trip_digest": round_trip_digest,
                "entity_count": public_scene["entity_count"],
                "constraint_count": public_scene["constraint_count"],
            },
            [public_scene["public_scene_id"]],
        ),
        make_gate(
            "kernel_validation",
            "passed" if kernel_valid else "failed",
            None if kernel_valid else "kernel_validation_failed",
            {"issues": kernel_issues},
            [public_scene["public_scene_id"]],
        ),
        make_gate(
            "viewer_projection",
            "passed" if "error" not in projection else "failed",
            None if "error" not in projection else "viewer_projection_failed",
            {
                "num_vertices": len(projection.get("vertices", [])),
                "num_edges": len(projection.get("edges", [])),
            },
            [projection.get("graph_id") or projection.get("projected_graph_id") or "geometry_primal"],
        ),
    ]
    gates.extend(runtime_public_gates(smoke, unavailable_status))
    return gates


def load_candidate_provenance(store_dir: str, exploration_id: str, candidate_id: str) -> dict:
    path = os.path.join(candidate_root(store_dir, exploration_id, candidate_id), "provenance.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Candidate '{candidate_id}' not found for exploration '{exploration_id}'")
    return read_json_file(path)


def promotion_status_from_gates(gates: list[dict]) -> tuple[str, str | None]:
    blocking_gate = next((gate for gate in gates if gate["status"] in {"failed", "unsupported"}), None)
    if blocking_gate is None:
        return "promotion_package_written", None
    return "promotion_blocked", blocking_gate.get("reason_code") or "promotion_gate_unsupported"


def build_promotion_package(
    promotion_id: str,
    exploration_id: str,
    candidate_id: str,
    gcs_graph_id: str,
    provenance: dict,
    report: dict,
    gates: list[dict],
    json_serialization: dict,
    text_serialization: dict,
    public_scene: dict,
) -> dict:
    status, reason_code = promotion_status_from_gates(gates)
    return {
        "promotion_id": promotion_id,
        "status": status,
        "reason_code": reason_code,
        "source": {
            "exploration_id": exploration_id,
            "candidate_id": candidate_id,
            "gcs_graph_id": gcs_graph_id,
        },
        "candidate_provenance": provenance,
        "local_validation_report": report,
        "gate_reports": gates,
        "canonical_serialization": {
            "json_checksum": json_serialization.get("checksum"),
            "text_checksum": text_serialization.get("checksum"),
            "json_digest": sha256_text(json_serialization.get("serialization", "")),
            "text_digest": sha256_text(text_serialization.get("serialization", "")),
            "public_scene_digest": sha256_text(promotion.canonical_public_scene_text(public_scene)),
        },
        "fixture_metadata_proposal": {
            "fixture_id": candidate_id,
            "generator": "tools.scene_generation.explore_scene_space",
            "schema": "scene-generation-promotion-v1",
        },
        "known_unsupported_gates": [gate["gate_id"] for gate in gates if gate["status"] == "unsupported"],
    }


def write_promotion_artifacts(
    store_dir: str,
    promotion_id: str,
    package: dict,
    projection: dict,
    scene: dict,
    public_scene: dict,
) -> str:
    root = promotion_root(store_dir, promotion_id)
    write_json_file(os.path.join(root, "package.json"), package)
    write_json_file(os.path.join(root, "geometry_primal.json"), projection)
    write_json_file(os.path.join(root, "scene.json"), scene)
    write_json_file(os.path.join(root, "public_scene.gcs.json"), public_scene)
    return root
