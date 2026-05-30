"""Batch solver execution and output parsing."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SolveResult:
    scene_id: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    status: str  # "solved", "failed", "timeout", "crash"
    rank_evidence: dict | None = None
    diagnostics_present: bool = False
    error_summary: str = ""


def find_solver(default_path: str | None = None) -> list[str] | None:
    """Find the GCS solver executable. Returns command list or None."""
    candidates = []
    if default_path and os.path.exists(default_path):
        candidates.append(default_path)
    candidates.append(os.path.join(
        os.path.dirname(__file__), "..", "..", "out", "build", "clang-ninja",
        "GCS.exe" if os.name == "nt" else "GCS",
    ))
    env_exe = os.environ.get("GCS_EXE")
    if env_exe:
        candidates.insert(0, env_exe)

    for candidate in candidates:
        candidate = os.path.abspath(candidate)
        if os.path.exists(candidate):
            return [candidate]
    return None


def _parse_solver_output(stdout: str) -> dict[str, Any]:
    """Extract structured info from solver stdout."""
    result: dict[str, Any] = {
        "status": "unknown",
        "diagnostics_present": False,
        "rank_evidence": None,
    }

    output_lower = stdout.lower()
    if "accepted" in output_lower or "solved" in output_lower:
        result["status"] = "solved"
    elif "failed" in output_lower or "error" in output_lower:
        result["status"] = "failed"

    if "diagnostics" in output_lower and "status:" in output_lower:
        result["diagnostics_present"] = True

    if "rank" in output_lower:
        result["rank_evidence"] = {"present": True, "source": "stdout_text"}

    try:
        data = json.loads(stdout)
        if isinstance(data, dict):
            result["status"] = str(data.get("status", result["status"]))
            result["diagnostics_present"] = bool(data.get("diagnostics"))
            for path in ["rank_evidence", "summary.rank_evidence"]:
                value = data
                for key in path.split("."):
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = None
                        break
                if value is not None:
                    result["rank_evidence"] = value
                    break
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    return result


def run_single(scene_path: str, scene_id: str, solver_command: list[str], timeout_seconds: float = 30.0) -> SolveResult:
    """Run solver once on a single scene file."""
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [*solver_command, scene_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        duration_ms = int((time.monotonic() - started) * 1000)
        parsed = _parse_solver_output(completed.stdout)

        if completed.returncode == 0:
            status = parsed.get("status", "solved")
        else:
            status = "crash" if completed.returncode < 0 else "failed"

        return SolveResult(
            scene_id=scene_id,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration_ms=duration_ms,
            status=status,
            rank_evidence=parsed.get("rank_evidence"),
            diagnostics_present=parsed.get("diagnostics_present", False),
            error_summary=completed.stderr[:200] if completed.stderr else "",
        )
    except subprocess.TimeoutExpired:
        duration_ms = int((time.monotonic() - started) * 1000)
        return SolveResult(
            scene_id=scene_id,
            exit_code=-1,
            stdout="",
            stderr=f"Timeout after {timeout_seconds}s",
            duration_ms=duration_ms,
            status="timeout",
        )
    except Exception as exc:
        duration_ms = int((time.monotonic() - started) * 1000)
        return SolveResult(
            scene_id=scene_id,
            exit_code=-2,
            stdout="",
            stderr=str(exc),
            duration_ms=duration_ms,
            status="crash",
        )


def batch_solve(
    scene_paths: list[tuple[str, str]],
    solver_command: list[str] | None = None,
    timeout_seconds: float = 30.0,
) -> list[SolveResult]:
    """Run solver on multiple scene files.

    Args:
        scene_paths: list of (scene_path, scene_id) tuples
        solver_command: solver executable command
        timeout_seconds: per-scene timeout

    Returns:
        list of SolveResult, one per scene
    """
    if solver_command is None:
        solver_command = find_solver()
    if solver_command is None:
        raise RuntimeError(
            "GCS solver not found. Set GCS_EXE or build the project."
        )

    results = []
    for scene_path, scene_id in scene_paths:
        result = run_single(scene_path, scene_id, solver_command, timeout_seconds)
        results.append(result)
    return results
