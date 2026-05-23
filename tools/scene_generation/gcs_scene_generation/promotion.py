"""Public promotion adapters for generated GCS candidates."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time

from .contracts import CONSTRAINT_TYPE_MAP, GEOMETRY_TYPE_MAP
from .storage import safe_store_id, sha256_text, write_json_file


def canonical_public_scene_text(scene: dict) -> str:
    return json.dumps(scene, indent=2, sort_keys=True) + "\n"


def public_scene_root(store_dir: str) -> str:
    return os.path.join(store_dir, "public_scenes")


def public_scene_path(store_dir: str, public_scene_id: str) -> str:
    filename = f"{safe_store_id(public_scene_id, 'public_scene_id')}.gcs.json"
    return os.path.join(public_scene_root(store_dir), filename)


def solver_scene_from_gcs(gcs: dict) -> dict:
    rigid_set_ids = sorted({int(rs["id"]) for rs in gcs.get("rigid_sets", [])})
    scene = {
        "format_version": "gcs-0.3",
        "state_version": 0,
        "rigid_sets": [{"id": rigid_set_id} for rigid_set_id in rigid_set_ids],
        "geometries": [],
        "constraints": [],
    }
    for geometry in sorted(gcs.get("geometries", []), key=lambda item: int(item["id"])):
        values = list(geometry.get("v", []))
        values = (values + [0.0] * 6)[:6]
        scene["geometries"].append(
            {
                "id": int(geometry["id"]),
                "type": GEOMETRY_TYPE_MAP[geometry["type"]],
                "rigid_set_id": int(geometry.get("rigid_set_id", 0)),
                "v": [float(value) for value in values],
            }
        )
    for constraint in sorted(gcs.get("constraints", []), key=lambda item: int(item["id"])):
        scene["constraints"].append(
            {
                "id": int(constraint["id"]),
                "type": CONSTRAINT_TYPE_MAP[constraint["type"]],
                "geometry_ids": [int(gid) for gid in constraint.get("geometry_ids", [])],
                "value": float(constraint.get("value", 0.0)),
            }
        )
    return scene


def write_public_scene(store_dir: str, gcs_graph_id: str, gcs: dict) -> dict:
    scene = solver_scene_from_gcs(gcs)
    public_scene_id = f"{gcs_graph_id}_public_scene"
    scene_path = public_scene_path(store_dir, public_scene_id)
    write_json_file(scene_path, scene)
    canonical = canonical_public_scene_text(scene)
    return {
        "public_scene_id": public_scene_id,
        "path": scene_path,
        "scene": scene,
        "digest": sha256_text(canonical),
        "entity_count": len(scene["geometries"]),
        "constraint_count": len(scene["constraints"]),
    }


def validate_public_scene_kernel(scene: dict) -> tuple[bool, list[dict]]:
    issues = []
    rigid_set_ids = {item.get("id") for item in scene.get("rigid_sets", [])}
    geometry_ids = set()
    for geometry in scene.get("geometries", []):
        geometry_id = geometry.get("id")
        if geometry_id in geometry_ids:
            issues.append({"code": "kernel.duplicate_entity", "entity_id": geometry_id})
        geometry_ids.add(geometry_id)
        if geometry.get("type") not in set(GEOMETRY_TYPE_MAP.values()):
            issues.append({"code": "kernel.invalid_geometry_kind", "entity_id": geometry_id})
        if geometry.get("rigid_set_id") not in rigid_set_ids:
            issues.append({"code": "kernel.missing_rigid_set", "entity_id": geometry_id})
        values = geometry.get("v", [])
        if len(values) != 6 or not all(isinstance(value, (int, float)) for value in values):
            issues.append({"code": "kernel.invalid_parameter_vector", "entity_id": geometry_id})

    constraint_ids = set()
    for constraint in scene.get("constraints", []):
        constraint_id = constraint.get("id")
        if constraint_id in constraint_ids:
            issues.append({"code": "kernel.duplicate_constraint", "constraint_id": constraint_id})
        constraint_ids.add(constraint_id)
        if constraint.get("type") not in set(CONSTRAINT_TYPE_MAP.values()):
            issues.append({"code": "kernel.invalid_constraint_kind", "constraint_id": constraint_id})
        for geometry_id in constraint.get("geometry_ids", []):
            if geometry_id not in geometry_ids:
                issues.append(
                    {
                        "code": "kernel.missing_entity",
                        "constraint_id": constraint_id,
                        "entity_id": geometry_id,
                    }
                )
        if not isinstance(constraint.get("value", 0.0), (int, float)):
            issues.append({"code": "kernel.invalid_constraint_value", "constraint_id": constraint_id})
    return not issues, issues


def normalize_solver_command(public_gate_config: dict | None, default_gcs_exe: str) -> list[str]:
    config = public_gate_config or {}
    command = config.get("solver_command")
    if isinstance(command, list) and command:
        return [str(part) for part in command]
    if isinstance(command, str) and command:
        return [command]
    executable = config.get("gcs_exe") or os.environ.get("GCS_EXE") or default_gcs_exe
    return [str(executable)]


def command_available(command: list[str]) -> bool:
    if not command:
        return False
    executable = command[0]
    if os.path.isabs(executable) or os.path.sep in executable:
        return os.path.exists(executable)
    return shutil.which(executable) is not None


def trim_lines(text: str, limit: int = 40) -> list[str]:
    return text.splitlines()[:limit]


def run_solver_smoke(scene_path: str, public_gate_config: dict | None, repo_root: str, default_gcs_exe: str) -> dict:
    command = normalize_solver_command(public_gate_config, default_gcs_exe)
    if not command_available(command):
        return {
            "available": False,
            "command": command,
            "exit_code": None,
            "stdout_lines": [],
            "stderr_lines": [f"Solver command is not available: {command[0]}"],
        }
    timeout_seconds = float((public_gate_config or {}).get("timeout_seconds", 20.0))
    started = time.monotonic()
    completed = subprocess.run(
        [*command, scene_path],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return {
        "available": True,
        "command": command,
        "exit_code": completed.returncode,
        "duration_ms": int((time.monotonic() - started) * 1000),
        "stdout_lines": trim_lines(completed.stdout),
        "stderr_lines": trim_lines(completed.stderr),
    }

