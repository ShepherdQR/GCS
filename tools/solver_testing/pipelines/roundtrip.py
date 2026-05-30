#!/usr/bin/env python3
"""IO Round-Trip Pipeline — verifies scene data survives serialization round-trips.

Usage:
  python tools/solver_testing/pipelines/roundtrip.py --fixtures fixtures/scene/ --formats json,text --solve-check
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Any

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.abspath(os.path.join(TOOL_DIR, "..", ".."))
sys.path.insert(0, REPO_ROOT)

from tools.scene_generation.gcs_scene_generation.contracts import (
    CONSTRAINT_TYPE_MAP,
    GEOMETRY_TYPE_MAP,
)
from tools.solver_testing.runner import SolveResult, find_solver, run_single

# ---------------------------------------------------------------------------
# Reverse type maps for text-format parsing
# ---------------------------------------------------------------------------

INT_TO_GEOMETRY_TYPE: dict[int, str] = {v: k for k, v in GEOMETRY_TYPE_MAP.items()}
INT_TO_CONSTRAINT_TYPE: dict[int, str] = {v: k for k, v in CONSTRAINT_TYPE_MAP.items()}

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class RoundTripResult:
    """Result of a single round-trip test (JSON or text)."""

    passed: bool
    diffs: list[str] = field(default_factory=list)
    format: str = ""

    def __bool__(self) -> bool:
        return self.passed


@dataclass
class SolveCompareResult:
    """Result of comparing solver outputs for original vs round-tripped scenes."""

    passed: bool
    diffs: list[str] = field(default_factory=list)
    original_result: SolveResult | None = None
    roundtripped_result: SolveResult | None = None

    def __bool__(self) -> bool:
        return self.passed


@dataclass
class FixtureRoundTripResult:
    """Per-fixture round-trip results across formats, plus optional solve comparison."""

    fixture_path: str
    scene_id: str
    json_result: RoundTripResult | None = None
    text_result: RoundTripResult | None = None
    solve_result: SolveCompareResult | None = None

    @property
    def all_passed(self) -> bool:
        results = [self.json_result, self.text_result, self.solve_result]
        return all(r is None or bool(r) for r in results)


@dataclass
class RoundTripReport:
    """Aggregated round-trip report across all fixtures."""

    fixture_results: list[FixtureRoundTripResult] = field(default_factory=list)
    aggregate: dict[str, float] = field(default_factory=dict)
    total_fixtures: int = 0
    passed_all: int = 0
    formats_tested: list[str] = field(default_factory=list)
    solve_checked: bool = False

    def summary(self) -> str:
        lines = ["=" * 60, "ROUND-TRIP REPORT", "=" * 60]
        lines.append(f"Fixtures tested:     {self.total_fixtures}")
        lines.append(f"Passed all checks:   {self.passed_all}")
        lines.append(f"Formats tested:      {', '.join(self.formats_tested)}")
        lines.append(f"Solve check:         {'yes' if self.solve_checked else 'no'}")
        lines.append("")
        lines.append("Pass rates by format:")
        for fmt, rate in sorted(self.aggregate.items()):
            status = "OK" if rate == 1.0 else f"FAIL ({rate:.1%})"
            lines.append(f"  {fmt}: {status}")
        if self.solve_checked:
            solve_rate = self.aggregate.get("solve", 0.0)
            status = "OK" if solve_rate == 1.0 else f"FAIL ({solve_rate:.1%})"
            lines.append(f"  solve: {status}")
        lines.append("")
        # List failures
        failures = [fr for fr in self.fixture_results if not fr.all_passed]
        if failures:
            lines.append("Failures:")
            for fr in failures:
                lines.append(f"  {fr.scene_id} ({fr.fixture_path}):")
                for result, label in [
                    (fr.json_result, "json"),
                    (fr.text_result, "text"),
                    (fr.solve_result, "solve"),
                ]:
                    if result is not None and not bool(result):
                        for diff in result.diffs:
                            lines.append(f"    [{label}] {diff}")
        else:
            lines.append("All fixtures passed all checks.")
        lines.append("=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------


def _serialize_to_gcs03_json(scene: dict) -> str:
    """Serialize a gcs-0.3 scene dict to canonical JSON."""
    return json.dumps(scene, indent=2, sort_keys=True)


def _serialize_to_custom_text_v1(scene: dict) -> str:
    """Serialize a gcs-0.3 scene dict to custom_text_v1 format.

    Format:
      N_rigid_sets
      rs_id1 rs_id2 ...
      N_geometries
      geom_id type_int rigid_set_id
      ...
      N_constraints
      constraint_id constraint_type_int num_geoms geom_id1 geom_id2 ...
      <blank>
      geom_id v0 v1 v2 v3 v4 v5
      ...
      <blank>
      constraint_id value
      ...
    """
    rigid_sets = sorted(scene.get("rigid_sets", []), key=lambda rs: int(rs["id"]))
    geometries = sorted(scene.get("geometries", []), key=lambda g: int(g["id"]))
    constraints = sorted(scene.get("constraints", []), key=lambda c: int(c["id"]))

    lines: list[str] = []

    # Rigid sets header
    lines.append(str(len(rigid_sets)))
    lines.append(" ".join(str(int(rs["id"])) for rs in rigid_sets))

    # Geometry header
    lines.append(str(len(geometries)))
    for g in geometries:
        geom_type_int = GEOMETRY_TYPE_MAP.get(g["type"])
        if geom_type_int is None:
            raise ValueError(f"Unknown geometry type: {g['type']}")
        lines.append(
            f"{int(g['id'])} {geom_type_int} {int(g.get('rigid_set_id', 0))}"
        )

    # Constraint header
    lines.append(str(len(constraints)))
    for c in constraints:
        ctype_int = CONSTRAINT_TYPE_MAP.get(c["type"])
        if ctype_int is None:
            raise ValueError(f"Unknown constraint type: {c['type']}")
        geom_ids = [int(gid) for gid in c.get("geometry_ids", [])]
        lines.append(
            f"{int(c['id'])} {ctype_int} {len(geom_ids)} "
            + " ".join(str(gid) for gid in geom_ids)
        )

    # Blank separator
    lines.append("")

    # Geometry parameter values
    for g in geometries:
        v = list(g.get("v", [0.0] * 6))
        v = (v + [0.0] * 6)[:6]
        values_str = " ".join(_format_float(val) for val in v)
        lines.append(f"{int(g['id'])} {values_str}")

    # Blank separator
    lines.append("")

    # Constraint values
    for c in constraints:
        lines.append(f"{int(c['id'])} {_format_float(float(c.get('value', 0.0)))}")

    return "\n".join(lines)


def _format_float(value: float) -> str:
    """Format a float with 12 significant digits (matches tool_serialize_gcs_graph)."""
    return f"{float(value):.12g}"


def _parse_custom_text_v1_to_scene(text: str) -> dict:
    """Parse custom_text_v1 text back into a gcs-0.3 scene dict.

    Returns the parsed scene dict, or raises ValueError on parse failure.
    """
    raw_lines = text.strip().splitlines()
    # Strip trailing empty lines
    while raw_lines and not raw_lines[-1].strip():
        raw_lines.pop()
    lines = [line.strip() for line in raw_lines]

    idx = 0

    # --- Rigid sets ---
    if idx >= len(lines):
        raise ValueError("custom_text_v1: missing rigid set count")
    num_rigid_sets = int(lines[idx])
    idx += 1

    rigid_set_ids: list[int] = []
    if num_rigid_sets > 0:
        if idx >= len(lines):
            raise ValueError("custom_text_v1: missing rigid set IDs line")
        rigid_set_ids = [int(x) for x in lines[idx].split()]
        if len(rigid_set_ids) != num_rigid_sets:
            raise ValueError(
                f"custom_text_v1: expected {num_rigid_sets} rigid set IDs, "
                f"got {len(rigid_set_ids)}"
            )
        idx += 1

    rigid_sets = [{"id": rs_id} for rs_id in rigid_set_ids]

    # --- Geometry header ---
    if idx >= len(lines):
        raise ValueError("custom_text_v1: missing geometry count")
    num_geometries = int(lines[idx])
    idx += 1

    geometries: list[dict] = []
    for _ in range(num_geometries):
        if idx >= len(lines):
            raise ValueError("custom_text_v1: missing geometry header line")
        parts = lines[idx].split()
        if len(parts) < 3:
            raise ValueError(
                f"custom_text_v1: geometry header requires 3 fields, got {len(parts)}"
            )
        geom_id = int(parts[0])
        type_int = int(parts[1])
        rigid_set_id = int(parts[2])
        geom_type = INT_TO_GEOMETRY_TYPE.get(type_int)
        if geom_type is None:
            raise ValueError(
                f"custom_text_v1: unknown geometry type integer {type_int} "
                f"for geometry {geom_id}"
            )
        geometries.append(
            {
                "id": geom_id,
                "type": geom_type,
                "rigid_set_id": rigid_set_id,
                "v": [0.0] * 6,
            }
        )
        idx += 1

    # --- Constraint header ---
    if idx >= len(lines):
        raise ValueError("custom_text_v1: missing constraint count")
    num_constraints = int(lines[idx])
    idx += 1

    constraints: list[dict] = []
    for _ in range(num_constraints):
        if idx >= len(lines):
            raise ValueError("custom_text_v1: missing constraint header line")
        parts = lines[idx].split()
        if len(parts) < 4:
            raise ValueError(
                f"custom_text_v1: constraint header requires at least 4 fields, "
                f"got {len(parts)}"
            )
        constraint_id = int(parts[0])
        type_int = int(parts[1])
        num_geom_ids = int(parts[2])
        geom_ids = [int(x) for x in parts[3 : 3 + num_geom_ids]]
        if len(geom_ids) != num_geom_ids:
            raise ValueError(
                f"custom_text_v1: constraint {constraint_id} declared "
                f"{num_geom_ids} geometry IDs but found {len(geom_ids)}"
            )
        ctype = INT_TO_CONSTRAINT_TYPE.get(type_int)
        if ctype is None:
            raise ValueError(
                f"custom_text_v1: unknown constraint type integer {type_int} "
                f"for constraint {constraint_id}"
            )
        constraints.append(
            {
                "id": constraint_id,
                "type": ctype,
                "geometry_ids": geom_ids,
                "value": 0.0,
            }
        )
        idx += 1

    # --- Blank separator before geometry values ---
    if idx < len(lines) and lines[idx] == "":
        idx += 1

    # --- Geometry values ---
    geom_by_id: dict[int, dict] = {g["id"]: g for g in geometries}
    for _ in range(num_geometries):
        if idx >= len(lines):
            raise ValueError("custom_text_v1: missing geometry values line")
        parts = lines[idx].split()
        if len(parts) < 7:
            raise ValueError(
                f"custom_text_v1: geometry values line requires at least 7 fields "
                f"(id + 6 values), got {len(parts)}"
            )
        geom_id = int(parts[0])
        v = [float(x) for x in parts[1:7]]
        if geom_id in geom_by_id:
            geom_by_id[geom_id]["v"] = v
        else:
            raise ValueError(
                f"custom_text_v1: geometry values for unknown geometry {geom_id}"
            )
        idx += 1

    # --- Blank separator before constraint values ---
    if idx < len(lines) and lines[idx] == "":
        idx += 1

    # --- Constraint values ---
    constraint_by_id: dict[int, dict] = {c["id"]: c for c in constraints}
    for _ in range(num_constraints):
        if idx >= len(lines):
            raise ValueError("custom_text_v1: missing constraint values line")
        parts = lines[idx].split()
        if len(parts) < 2:
            raise ValueError(
                f"custom_text_v1: constraint values line requires at least 2 fields "
                f"(id + value), got {len(parts)}"
            )
        constraint_id = int(parts[0])
        value = float(parts[1])
        if constraint_id in constraint_by_id:
            constraint_by_id[constraint_id]["value"] = value
        else:
            raise ValueError(
                f"custom_text_v1: constraint value for unknown constraint {constraint_id}"
            )
        idx += 1

    return {
        "format_version": "gcs-0.3",
        "state_version": 0,
        "rigid_sets": rigid_sets,
        "geometries": geometries,
        "constraints": constraints,
    }


# ---------------------------------------------------------------------------
# Scene comparison
# ---------------------------------------------------------------------------

_TOLERANCE = 1e-12


def _compare_scenes(original: dict, parsed: dict) -> list[str]:
    """Compare two gcs-0.3 scene dicts, returning list of difference descriptions."""
    diffs: list[str] = []

    orig_geoms = original.get("geometries", [])
    parsed_geoms = parsed.get("geometries", [])
    orig_constraints = original.get("constraints", [])
    parsed_constraints = parsed.get("constraints", [])

    # Geometry count
    if len(orig_geoms) != len(parsed_geoms):
        diffs.append(
            f"geometry count mismatch: {len(orig_geoms)} vs {len(parsed_geoms)}"
        )

    # Constraint count
    if len(orig_constraints) != len(parsed_constraints):
        diffs.append(
            f"constraint count mismatch: {len(orig_constraints)} vs {len(parsed_constraints)}"
        )

    # Build lookup by ID
    orig_geom_by_id = {g["id"]: g for g in orig_geoms}
    parsed_geom_by_id = {g["id"]: g for g in parsed_geoms}
    orig_constraint_by_id = {c["id"]: c for c in orig_constraints}
    parsed_constraint_by_id = {c["id"]: c for c in parsed_constraints}

    # Check all original geometry IDs present in parsed
    for gid in sorted(orig_geom_by_id.keys()):
        if gid not in parsed_geom_by_id:
            diffs.append(f"geometry {gid}: missing in round-tripped scene")
            continue
        og = orig_geom_by_id[gid]
        pg = parsed_geom_by_id[gid]

        # Type
        if og.get("type") != pg.get("type"):
            diffs.append(
                f"geometry {gid}: type mismatch {og.get('type')} vs {pg.get('type')}"
            )

        # Rigid set ID
        if og.get("rigid_set_id") != pg.get("rigid_set_id"):
            diffs.append(
                f"geometry {gid}: rigid_set_id mismatch "
                f"{og.get('rigid_set_id')} vs {pg.get('rigid_set_id')}"
            )

        # Values (v)
        ov = list(og.get("v", [0.0] * 6))
        pv = list(pg.get("v", [0.0] * 6))
        ov = (ov + [0.0] * 6)[:6]
        pv = (pv + [0.0] * 6)[:6]
        for vi in range(6):
            if not _values_close(ov[vi], pv[vi], _TOLERANCE):
                diffs.append(
                    f"geometry {gid}: v[{vi}] mismatch "
                    f"{_format_float(ov[vi])} vs {_format_float(pv[vi])}"
                )

    # Check for extra geometries in parsed
    for gid in sorted(parsed_geom_by_id.keys()):
        if gid not in orig_geom_by_id:
            diffs.append(f"geometry {gid}: extra in round-tripped scene")

    # Check all original constraint IDs present in parsed
    for cid in sorted(orig_constraint_by_id.keys()):
        if cid not in parsed_constraint_by_id:
            diffs.append(f"constraint {cid}: missing in round-tripped scene")
            continue
        oc = orig_constraint_by_id[cid]
        pc = parsed_constraint_by_id[cid]

        # Type
        if oc.get("type") != pc.get("type"):
            diffs.append(
                f"constraint {cid}: type mismatch {oc.get('type')} vs {pc.get('type')}"
            )

        # Geometry IDs
        og_ids = sorted(oc.get("geometry_ids", []))
        pg_ids = sorted(pc.get("geometry_ids", []))
        if og_ids != pg_ids:
            diffs.append(
                f"constraint {cid}: geometry_ids mismatch {og_ids} vs {pg_ids}"
            )

        # Value
        if not _values_close(
            float(oc.get("value", 0.0)), float(pc.get("value", 0.0)), _TOLERANCE
        ):
            diffs.append(
                f"constraint {cid}: value mismatch "
                f"{_format_float(float(oc.get('value', 0.0)))} "
                f"vs {_format_float(float(pc.get('value', 0.0)))}"
            )

    # Check for extra constraints in parsed
    for cid in sorted(parsed_constraint_by_id.keys()):
        if cid not in orig_constraint_by_id:
            diffs.append(f"constraint {cid}: extra in round-tripped scene")

    return diffs


def _values_close(a: float, b: float, tol: float = _TOLERANCE) -> bool:
    """Check two float values are close within tolerance."""
    if math.isfinite(a) and math.isfinite(b):
        return abs(a - b) <= tol
    # Both non-finite: check they're the same kind
    return (math.isnan(a) and math.isnan(b)) or (a == b)


# ---------------------------------------------------------------------------
# Solver output comparison
# ---------------------------------------------------------------------------


def _extract_solve_metrics(result: SolveResult) -> dict[str, Any]:
    """Extract status, rank_estimate, and residual_norm from a SolveResult."""
    metrics: dict[str, Any] = {
        "status": result.status,
        "rank_estimate": None,
        "residual_norm": None,
    }

    # Try to parse stdout as JSON for richer extraction
    try:
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            # rank_estimate
            for path, key in [
                (["rank_estimate"], "rank_estimate"),
                (["summary", "rank_evidence", "rank_estimate"], "rank_estimate"),
                (["rank_evidence", "rank_estimate"], "rank_estimate"),
                (["rank_evidence"], "rank_evidence"),
            ]:
                value = data
                for segment in path:
                    if isinstance(value, dict) and segment in value:
                        value = value[segment]
                    else:
                        value = None
                        break
                if value is not None:
                    metrics["rank_estimate"] = value
                    break

            # residual_norm
            for path in [
                ["residual_norm"],
                ["summary", "residual_norm"],
                ["numeric", "residual_norm"],
                ["diagnostics", "residual_norm"],
            ]:
                value = data
                for segment in path:
                    if isinstance(value, dict) and segment in value:
                        value = value[segment]
                    else:
                        value = None
                        break
                if value is not None:
                    metrics["residual_norm"] = value
                    break
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    # Fallback: text search in stdout
    if metrics["rank_estimate"] is None and result.rank_evidence is not None:
        if isinstance(result.rank_evidence, dict):
            metrics["rank_estimate"] = result.rank_evidence.get(
                "rank_estimate", result.rank_evidence
            )

    return metrics


def _compare_solve_metrics(
    orig_metrics: dict[str, Any], rt_metrics: dict[str, Any]
) -> list[str]:
    """Compare extracted solve metrics, returning list of difference descriptions."""
    diffs: list[str] = []

    # Status must be identical
    if orig_metrics["status"] != rt_metrics["status"]:
        diffs.append(
            f"solve status mismatch: {orig_metrics['status']} vs {rt_metrics['status']}"
        )

    # Rank estimate comparison
    orig_rank = orig_metrics.get("rank_estimate")
    rt_rank = rt_metrics.get("rank_estimate")
    if orig_rank is not None and rt_rank is not None:
        if isinstance(orig_rank, (int, float)) and isinstance(rt_rank, (int, float)):
            if not _values_close(float(orig_rank), float(rt_rank), _TOLERANCE):
                diffs.append(
                    f"rank_estimate mismatch: {_format_float(float(orig_rank))} "
                    f"vs {_format_float(float(rt_rank))}"
                )
        elif orig_rank != rt_rank:
            diffs.append(f"rank_estimate mismatch: {orig_rank} vs {rt_rank}")
    elif orig_rank is not rt_rank:
        diffs.append(
            f"rank_estimate presence mismatch: {orig_rank is not None} vs {rt_rank is not None}"
        )

    # Residual norm comparison
    orig_residual = orig_metrics.get("residual_norm")
    rt_residual = rt_metrics.get("residual_norm")
    if orig_residual is not None and rt_residual is not None:
        if isinstance(orig_residual, (int, float)) and isinstance(
            rt_residual, (int, float)
        ):
            if not _values_close(
                float(orig_residual), float(rt_residual), _TOLERANCE
            ):
                diffs.append(
                    f"residual_norm mismatch: {_format_float(float(orig_residual))} "
                    f"vs {_format_float(float(rt_residual))}"
                )
        elif orig_residual != rt_residual:
            diffs.append(f"residual_norm mismatch: {orig_residual} vs {rt_residual}")
    elif orig_residual is not rt_residual:
        diffs.append(
            f"residual_norm presence mismatch: "
            f"{orig_residual is not None} vs {rt_residual is not None}"
        )

    return diffs


# ---------------------------------------------------------------------------
# Pipeline class
# ---------------------------------------------------------------------------


class RoundTripPipeline:
    """Verifies scene data survives serialization round-trips.

    Tests JSON and custom_text_v1 format round-trips, plus solver result
    equivalence after round-trip.
    """

    def __init__(self, solver_command: list[str] | None = None):
        self._solver_command = solver_command

    @property
    def solver_command(self) -> list[str]:
        if self._solver_command is None:
            self._solver_command = find_solver()
        if self._solver_command is None:
            raise RuntimeError(
                "GCS solver not found. Set GCS_EXE or build the project."
            )
        return self._solver_command

    # --- Individual round-trip methods ---

    def round_trip_json(self, scene: dict) -> RoundTripResult:
        """scene dict -> gcs-0.3 JSON string -> parse back -> compare.

        Checks: geometry count, constraint count, IDs preserved, values equal
        to 1e-12 tolerance.
        """
        diffs: list[str] = []

        try:
            json_str = _serialize_to_gcs03_json(scene)
        except Exception as exc:
            return RoundTripResult(
                passed=False, diffs=[f"JSON serialization error: {exc}"], format="json"
            )

        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as exc:
            return RoundTripResult(
                passed=False, diffs=[f"JSON parse error: {exc}"], format="json"
            )

        if not isinstance(parsed, dict):
            return RoundTripResult(
                passed=False,
                diffs=[f"Parsed JSON is not a dict, got {type(parsed).__name__}"],
                format="json",
            )

        diffs = _compare_scenes(scene, parsed)
        return RoundTripResult(passed=len(diffs) == 0, diffs=diffs, format="json")

    def round_trip_text(self, scene: dict) -> RoundTripResult:
        """scene dict -> custom_text_v1 serialization -> re-parse as gcs-0.3 -> compare.

        The text format uses type integers; verifies correct mapping back.
        """
        diffs: list[str] = []

        try:
            text = _serialize_to_custom_text_v1(scene)
        except Exception as exc:
            return RoundTripResult(
                passed=False,
                diffs=[f"custom_text_v1 serialization error: {exc}"],
                format="text",
            )

        try:
            parsed = _parse_custom_text_v1_to_scene(text)
        except ValueError as exc:
            return RoundTripResult(
                passed=False,
                diffs=[f"custom_text_v1 parse error: {exc}"],
                format="text",
            )

        diffs = _compare_scenes(scene, parsed)
        return RoundTripResult(passed=len(diffs) == 0, diffs=diffs, format="text")

    def round_trip_solve(
        self,
        scene: dict,
        solver_command: list[str] | None = None,
        timeout_seconds: float = 30.0,
    ) -> SolveCompareResult:
        """solve(original JSON) -> solve(round-tripped JSON) -> compare results.

        Compares status, rank_estimate, and residual_norm.
        """
        cmd = solver_command or self.solver_command

        # Write original scene to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gcs.json", delete=False
        ) as f:
            json.dump(scene, f)
            orig_path = f.name

        try:
            # Round-trip the scene through JSON to get the round-tripped version
            rt_result = self.round_trip_json(scene)
            if not rt_result.passed:
                return SolveCompareResult(
                    passed=False,
                    diffs=[
                        f"round-trip JSON failed before solve: {rt_result.diffs}"
                    ],
                )

            # Parse the round-tripped JSON back
            rt_json = _serialize_to_gcs03_json(scene)
            rt_scene = json.loads(rt_json)

            # Write round-tripped scene to temp file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".gcs.json", delete=False
            ) as f:
                json.dump(rt_scene, f)
                rt_path = f.name

            try:
                # Solve original
                scene_id = str(scene.get("scene_id", "original"))
                orig_result = run_single(
                    orig_path, scene_id + "_orig", cmd, timeout_seconds
                )

                # Solve round-tripped
                rt_solve_result = run_single(
                    rt_path, scene_id + "_rt", cmd, timeout_seconds
                )

                # Extract and compare metrics
                orig_metrics = _extract_solve_metrics(orig_result)
                rt_metrics = _extract_solve_metrics(rt_solve_result)
                diffs = _compare_solve_metrics(orig_metrics, rt_metrics)

                return SolveCompareResult(
                    passed=len(diffs) == 0,
                    diffs=diffs,
                    original_result=orig_result,
                    roundtripped_result=rt_solve_result,
                )
            finally:
                try:
                    os.unlink(rt_path)
                except OSError:
                    pass
        finally:
            try:
                os.unlink(orig_path)
            except OSError:
                pass

    # --- Corpus and orchestration ---

    def test_fixture_corpus(
        self,
        fixture_paths: list[str],
        formats: list[str] | None = None,
        solver_command: list[str] | None = None,
        solve_check: bool = False,
        timeout_seconds: float = 30.0,
    ) -> list[FixtureRoundTripResult]:
        """For each fixture file, load as scene, run specified round-trip formats.

        Args:
            fixture_paths: List of file paths to fixture JSON files.
            formats: List of format names to test ('json', 'text'). Default: ['json'].
            solver_command: Solver executable command.
            solve_check: Whether to run solve comparison.
            timeout_seconds: Per-solve timeout.

        Returns:
            List of FixtureRoundTripResult, one per fixture file.
        """
        if formats is None:
            formats = ["json"]

        results: list[FixtureRoundTripResult] = []
        for path in fixture_paths:
            if not os.path.isfile(path):
                continue

            scene_id = os.path.splitext(os.path.basename(path))[0]
            # Handle double extension like .gcs.json
            if scene_id.endswith(".gcs"):
                scene_id = scene_id[:-4]

            try:
                with open(path, "r", encoding="utf-8") as f:
                    scene = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                # Create a failed result for this fixture
                fr = FixtureRoundTripResult(
                    fixture_path=path,
                    scene_id=scene_id,
                )
                if "json" in formats:
                    fr.json_result = RoundTripResult(
                        passed=False,
                        diffs=[f"Failed to load fixture: {exc}"],
                        format="json",
                    )
                if "text" in formats:
                    fr.text_result = RoundTripResult(
                        passed=False,
                        diffs=[f"Failed to load fixture: {exc}"],
                        format="text",
                    )
                if solve_check:
                    fr.solve_result = SolveCompareResult(
                        passed=False,
                        diffs=[f"Failed to load fixture: {exc}"],
                    )
                results.append(fr)
                continue

            fr = FixtureRoundTripResult(fixture_path=path, scene_id=scene_id)

            if "json" in formats:
                fr.json_result = self.round_trip_json(scene)
            if "text" in formats:
                fr.text_result = self.round_trip_text(scene)
            if solve_check:
                fr.solve_result = self.round_trip_solve(
                    scene, solver_command, timeout_seconds
                )

            results.append(fr)

        return results

    def run(
        self,
        fixture_paths: list[str],
        formats: list[str] | None = None,
        solver_command: list[str] | None = None,
        solve_check: bool = False,
        timeout_seconds: float = 30.0,
    ) -> RoundTripReport:
        """Orchestrate full round-trip testing and return aggregated report.

        Args:
            fixture_paths: List of file paths or directory paths containing fixtures.
            formats: Format names to test ('json', 'text'). Default: ['json'].
            solver_command: Solver executable command.
            solve_check: Whether to run solve comparison.
            timeout_seconds: Per-solve timeout.

        Returns:
            RoundTripReport with per-fixture and aggregate results.
        """
        if formats is None:
            formats = ["json"]

        # Resolve directories to file lists
        resolved_paths: list[str] = []
        for path in fixture_paths:
            if os.path.isdir(path):
                for root, _dirs, files in os.walk(path):
                    for fname in sorted(files):
                        if fname.endswith(".json"):
                            resolved_paths.append(os.path.join(root, fname))
            elif os.path.isfile(path):
                resolved_paths.append(path)

        if not resolved_paths:
            report = RoundTripReport(
                formats_tested=list(formats),
                solve_checked=solve_check,
            )
            return report

        fixture_results = self.test_fixture_corpus(
            resolved_paths,
            formats=formats,
            solver_command=solver_command,
            solve_check=solve_check,
            timeout_seconds=timeout_seconds,
        )

        # Compute aggregates
        aggregate: dict[str, float] = {}
        for fmt in formats:
            fmt_results = [
                getattr(fr, f"{fmt}_result")
                for fr in fixture_results
                if getattr(fr, f"{fmt}_result") is not None
            ]
            if fmt_results:
                passed = sum(1 for r in fmt_results if r.passed)
                aggregate[fmt] = passed / len(fmt_results)
            else:
                aggregate[fmt] = 0.0

        if solve_check:
            solve_results = [
                fr.solve_result
                for fr in fixture_results
                if fr.solve_result is not None
            ]
            if solve_results:
                passed = sum(1 for r in solve_results if r.passed)
                aggregate["solve"] = passed / len(solve_results)
            else:
                aggregate["solve"] = 0.0

        total = len(fixture_results)
        passed_all = sum(1 for fr in fixture_results if fr.all_passed)

        return RoundTripReport(
            fixture_results=fixture_results,
            aggregate=aggregate,
            total_fixtures=total,
            passed_all=passed_all,
            formats_tested=list(formats),
            solve_checked=solve_check,
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _collect_fixture_paths(paths: list[str]) -> list[str]:
    """Expand the list of path args into a flat list of .json fixture file paths."""
    result: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for fname in sorted(files):
                    if fname.endswith(".json"):
                        result.append(os.path.join(root, fname))
        elif os.path.isfile(p):
            result.append(p)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="IO Round-Trip Pipeline — verify scene data survives serialization round-trips",
    )
    parser.add_argument(
        "--fixtures",
        nargs="+",
        default=["fixtures/scene/"],
        help="Fixture file paths or directories (default: fixtures/scene/)",
    )
    parser.add_argument(
        "--formats",
        default="json,text",
        help="Comma-separated format names: json,text (default: json,text)",
    )
    parser.add_argument(
        "--solve-check",
        action="store_true",
        default=False,
        help="Also run solver result comparison after round-trip",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Per-solve timeout in seconds (default: 30.0)",
    )
    parser.add_argument(
        "--solver",
        default=None,
        help="Path to GCS solver executable (default: auto-detect)",
    )
    parser.add_argument(
        "--json-output",
        default=None,
        help="Write report as JSON to this file",
    )

    args = parser.parse_args()

    # Resolve fixture paths relative to repo root
    fixture_args = []
    for p in args.fixtures:
        if not os.path.isabs(p):
            p = os.path.join(REPO_ROOT, p)
        fixture_args.append(p)

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    unknown = [f for f in formats if f not in ("json", "text")]
    if unknown:
        print(f"ERROR: Unknown formats: {unknown}. Use json,text.")
        sys.exit(1)

    solver_command = None
    if args.solver:
        solver_command = [args.solver]
    else:
        solver_command = find_solver()
        if solver_command is None:
            print("ERROR: GCS solver not found. Set GCS_EXE, use --solver, or build the project.")
            sys.exit(1)

    pipeline = RoundTripPipeline(solver_command)

    fixture_paths = _collect_fixture_paths(fixture_args)

    print(f"Solver: {solver_command[0]}")
    print(f"Fixtures: {len(fixture_paths)} files")
    print(f"Formats: {formats}")
    print(f"Solve check: {'yes' if args.solve_check else 'no'}")
    print()

    report = pipeline.run(
        fixture_paths=fixture_paths,
        formats=formats,
        solver_command=solver_command,
        solve_check=args.solve_check,
        timeout_seconds=args.timeout,
    )

    print(report.summary())

    if args.json_output:
        output_path = args.json_output
        if not os.path.isabs(output_path):
            output_path = os.path.join(REPO_ROOT, output_path)

        serializable = _report_to_dict(report)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2, sort_keys=True)
        print(f"\nReport saved to: {output_path}")

    # Exit with status code
    if report.passed_all == report.total_fixtures and all(
        v == 1.0 for v in report.aggregate.values()
    ):
        sys.exit(0)
    else:
        sys.exit(1)


def _report_to_dict(report: RoundTripReport) -> dict:
    """Convert a RoundTripReport to a JSON-serializable dict."""
    fixture_dicts = []
    for fr in report.fixture_results:
        fd: dict[str, Any] = {
            "fixture_path": fr.fixture_path,
            "scene_id": fr.scene_id,
        }
        if fr.json_result is not None:
            fd["json"] = {
                "passed": fr.json_result.passed,
                "diffs": fr.json_result.diffs,
            }
        if fr.text_result is not None:
            fd["text"] = {
                "passed": fr.text_result.passed,
                "diffs": fr.text_result.diffs,
            }
        if fr.solve_result is not None:
            fd["solve"] = {
                "passed": fr.solve_result.passed,
                "diffs": fr.solve_result.diffs,
                "original_status": (
                    fr.solve_result.original_result.status
                    if fr.solve_result.original_result
                    else None
                ),
                "roundtripped_status": (
                    fr.solve_result.roundtripped_result.status
                    if fr.solve_result.roundtripped_result
                    else None
                ),
            }
        fixture_dicts.append(fd)

    return {
        "total_fixtures": report.total_fixtures,
        "passed_all": report.passed_all,
        "formats_tested": report.formats_tested,
        "solve_checked": report.solve_checked,
        "aggregate": report.aggregate,
        "fixture_results": fixture_dicts,
    }


if __name__ == "__main__":
    main()
