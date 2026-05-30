#!/usr/bin/env python3
"""Numeric Stability Pipeline — tests solver under extreme numerical conditions.

Measures condition numbers, rank stability, and residual growth when constraint
values sweep across extreme ranges, geometries are perturbed to near-degenerate
configurations, and ill-conditioned configurations are constructed.

Usage:
  python tools/solver_testing/pipelines/stability.py --scene PATH --constraint 0 --sweep logspace --range 1e-12,1e12 --steps 20
  python tools/solver_testing/pipelines/stability.py --scene PATH --constraint 0 --sweep near_zero
  python tools/solver_testing/pipelines/stability.py --scene PATH --constraint 0 --sweep boundaries
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.abspath(os.path.join(TOOL_DIR, ".."))
sys.path.insert(0, REPO_ROOT)

from tools.scene_generation.gcs_scene_generation.contracts import (
    CONSTRAINT_TYPE_MAP,
    GEOMETRY_TYPE_MAP,
)
from tools.scene_generation.gcs_scene_generation.promotion import (
    solver_scene_from_gcs,
)
from tools.solver_testing.runner import find_solver, run_single

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EPS = 1e-12
_CONSTRAINT_TYPE_NAMES: Dict[int, str] = {v: k for k, v in CONSTRAINT_TYPE_MAP.items()}
_GEOMETRY_TYPE_NAMES: Dict[int, str] = {v: k for k, v in GEOMETRY_TYPE_MAP.items()}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class StabilityPoint:
    """A single data point from a stability sweep."""

    value: float
    status: str
    exit_code: int
    rank_estimate: Optional[int] = None
    condition_estimate: Optional[float] = None
    residual_norm: Optional[float] = None
    duration_ms: int = 0


@dataclass
class StabilityAnalysis:
    """Result of analyzing a set of stability points."""

    condition_trend: str  # increasing | decreasing | stable | oscillating | insufficient_data
    condition_trend_slope: Optional[float] = None
    rank_drops: List[int] = field(default_factory=list)
    failure_boundary: Optional[int] = None
    failure_boundary_value: Optional[float] = None
    min_condition: Optional[float] = None
    max_condition: Optional[float] = None
    points_count: int = 0
    failure_count: int = 0


@dataclass
class StabilityResult:
    """Full result of a stability pipeline run."""

    scene_path: str
    constraint_index: int
    constraint_type: str
    sweep_spec: Dict[str, Any]
    points: List[StabilityPoint]
    analysis: StabilityAnalysis
    solver_command: List[str]
    duration_ms: int = 0


# ---------------------------------------------------------------------------
# Value sweep generation
# ---------------------------------------------------------------------------


def _logspace(start: float, end: float, steps: int) -> List[float]:
    """Generate logarithmically spaced values (no numpy dependency).

    Uses math.log10 / math.pow to match numpy-style logspace semantics.
    """
    if steps <= 0:
        return []
    if steps == 1:
        return [start]
    log_start = math.log10(start)
    log_end = math.log10(end)
    result: List[float] = []
    for i in range(steps):
        log_val = log_start + (log_end - log_start) * i / (steps - 1)
        result.append(math.pow(10.0, log_val))
    return result


def _resolve_constraint_type(constraint: dict) -> str:
    """Resolve constraint type to a string name regardless of input format."""
    ctype = constraint.get("type")
    if isinstance(ctype, str):
        return ctype
    if isinstance(ctype, int):
        return _CONSTRAINT_TYPE_NAMES.get(ctype, "Unknown")
    return "Unknown"


def generate_value_sweep(constraint: dict, range_spec: dict) -> List[float]:
    """Generate test values for a constraint value sweep.

    Args:
        constraint: The constraint dict (from public scene or GCS graph).
        range_spec: Dict with keys:
            - type: "logspace" | "near_zero" | "boundaries" | "linear"
            - start, end, steps (for logspace and linear)
            - epsilon (for near_zero)

    Returns:
        List of float values to test.

    Sweep types:
        logspace:  Logarithmically spaced values from start to end in N steps.
                   Uses math.log10/math.pow (no numpy dependency).
        near_zero: [0, epsilon, 2*epsilon, 4*epsilon, 8*epsilon]
                   where epsilon defaults to 1e-12.
        boundaries: Values at schema-defined min/max boundaries.
                    0 for Distance, 0 and pi for Angle, -1/0/1 for others.
        linear:    Linearly spaced values from start to end in N steps.
    """
    sweep_type = range_spec.get("type", "logspace")

    if sweep_type == "logspace":
        start = float(range_spec.get("start", 1e-12))
        end = float(range_spec.get("end", 1e12))
        steps = int(range_spec.get("steps", 20))
        return _logspace(start, end, steps)

    elif sweep_type == "near_zero":
        eps = float(range_spec.get("epsilon", EPS))
        return [0.0, eps, 2 * eps, 4 * eps, 8 * eps]

    elif sweep_type == "boundaries":
        ctype = _resolve_constraint_type(constraint)
        if ctype == "Distance":
            return [0.0, EPS, 1e-6, 1e-3, 1.0, 10.0, 100.0]
        elif ctype == "Angle":
            return [0.0, EPS, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi - EPS, math.pi]
        else:
            # Coincident, Parallel, Perpendicular — binary/structural constraints
            # that still carry a value field; test around zero
            return [-1.0, 0.0, 1.0]

    elif sweep_type == "linear":
        start = float(range_spec.get("start", 0.0))
        end = float(range_spec.get("end", 1.0))
        steps = int(range_spec.get("steps", 10))
        if steps <= 1:
            return [start]
        result: List[float] = []
        for i in range(steps):
            result.append(start + (end - start) * i / (steps - 1))
        return result

    else:
        raise ValueError(f"Unknown sweep type: {sweep_type!r}")


# ---------------------------------------------------------------------------
# Geometry perturbation generation
# ---------------------------------------------------------------------------


def _resolve_geometry_type(geometry: dict) -> str:
    """Resolve geometry type to a string name regardless of input format."""
    gtype = geometry.get("type")
    if isinstance(gtype, str):
        return gtype
    if isinstance(gtype, int):
        return _GEOMETRY_TYPE_NAMES.get(gtype, "Point")
    return "Point"


def generate_geometry_perturbations(geometry: dict) -> Dict[str, dict]:
    """Generate perturbed geometry vectors for stability testing.

    Produces near-degenerate or ill-conditioned geometry variants that probe
    solver robustness.

    Args:
        geometry: A geometry dict with 'type' (int or str) and 'v' (list of 6 floats).

    Returns:
        Dict mapping perturbation name to a copy of the geometry dict with the
        perturbed 'v' vector. Keys:
          - zero_direction:  Set direction/normal components (indices 3,4,5) to 0.
                             Produces a degenerate Line or Plane.
          - coincident_points: For a Point, move its position to the origin (0,0,0).
                               Useful for testing coincident-point tolerance.
          - parallel_direction: For Line or Plane, align direction/normal to the
                                X-axis (1,0,0) as a canonical reference.
    """
    gtype = _resolve_geometry_type(geometry)
    v = list(geometry.get("v", [0.0] * 6))

    perturbations: Dict[str, dict] = {}

    # --- zero_direction: set direction/normal components to zero ---
    zero_dir_geom = copy.deepcopy(geometry)
    zd_v = list(zero_dir_geom.get("v", v))
    if gtype in ("Line", "Plane"):
        # Direction/normal occupies indices 3,4,5
        zd_v[3] = 0.0
        zd_v[4] = 0.0
        zd_v[5] = 0.0
    zero_dir_geom["v"] = zd_v
    perturbations["zero_direction"] = zero_dir_geom

    # --- coincident_points: place a Point at the origin ---
    if gtype == "Point":
        coincident_geom = copy.deepcopy(geometry)
        coincident_geom["v"] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        perturbations["coincident_points"] = coincident_geom

    # --- parallel_direction: align direction/normal to canonical X-axis ---
    if gtype in ("Line", "Plane"):
        parallel_geom = copy.deepcopy(geometry)
        pv = list(parallel_geom.get("v", v))
        # Position stays; direction/normal becomes (1,0,0)
        pv[3] = 1.0
        pv[4] = 0.0
        pv[5] = 0.0
        parallel_geom["v"] = pv
        perturbations["parallel_direction"] = parallel_geom

    return perturbations


# ---------------------------------------------------------------------------
# Solver output parsing helpers
# ---------------------------------------------------------------------------

_FLOAT_RE = re.compile(r"[\d.eE+\-]+")


def _first_float_after_keyword(text: str, keyword: str) -> Optional[float]:
    """Extract the first float value appearing on a line that mentions *keyword*."""
    for line in text.splitlines():
        if keyword in line.lower():
            match = _FLOAT_RE.search(line)
            if match:
                try:
                    return float(match.group())
                except ValueError:
                    pass
    return None


def _first_int_after_keyword(text: str, keyword: str) -> Optional[int]:
    """Extract the first integer value appearing on a line that mentions *keyword*."""
    for line in text.splitlines():
        if keyword in line.lower():
            match = re.search(r"\d+", line)
            if match:
                try:
                    return int(match.group())
                except ValueError:
                    pass
    return None


# ---------------------------------------------------------------------------
# Stability solve
# ---------------------------------------------------------------------------


def stability_solve(
    scene: dict,
    value_sweep: List[float],
    constraint_index: int,
    solver_command: List[str],
    timeout_seconds: float = 30.0,
) -> List[StabilityPoint]:
    """Run solver for each test value, modifying the specified constraint.

    For each value in *value_sweep*, creates a copy of the scene with the
    target constraint's value replaced, writes a temporary file, invokes the
    solver, and collects the result.

    Args:
        scene: The public scene dict (format_version gcs-0.3+).
        value_sweep: List of float values to test, one solve per value.
        constraint_index: Index into scene["constraints"] to modify.
        solver_command: Solver executable command list.
        timeout_seconds: Per-solve timeout in seconds.

    Returns:
        List of StabilityPoint, one per test value, in the same order as
        *value_sweep*.
    """
    points: List[StabilityPoint] = []

    for i, value in enumerate(value_sweep):
        modified = copy.deepcopy(scene)
        constraints = modified.get("constraints", [])
        if constraint_index < len(constraints):
            constraints[constraint_index]["value"] = value

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gcs.json", delete=False
        ) as fh:
            json.dump(modified, fh)
            temp_path = fh.name

        scene_id = f"stability_c{constraint_index}_v{i:04d}"
        result = run_single(temp_path, scene_id, solver_command, timeout_seconds)

        try:
            os.unlink(temp_path)
        except OSError:
            pass

        points.append(
            StabilityPoint(
                value=value,
                status=result.status,
                exit_code=result.exit_code,
                rank_estimate=_first_int_after_keyword(result.stdout, "rank"),
                condition_estimate=_first_float_after_keyword(
                    result.stdout, "condition"
                ),
                residual_norm=_first_float_after_keyword(
                    result.stdout, "residual"
                ),
                duration_ms=result.duration_ms,
            )
        )

    return points


# ---------------------------------------------------------------------------
# Stability analysis
# ---------------------------------------------------------------------------


def _finite_condition_pairs(
    points: List[StabilityPoint],
) -> List[tuple]:
    """Return (index, condition_estimate) for points with finite condition."""
    result: List[tuple] = []
    for i, p in enumerate(points):
        if p.condition_estimate is not None and math.isfinite(p.condition_estimate):
            result.append((i, p.condition_estimate))
    return result


def analyze_stability(points: List[StabilityPoint]) -> StabilityAnalysis:
    """Analyze stability sweep results for degradation patterns.

    Detects three classes of numeric stability issues:

    1. **condition_trend**: Fits a simple linear regression to the sequence of
       condition estimates and classifies the trend as increasing, decreasing,
       stable, or oscillating (frequent sign changes).

    2. **rank_drops**: Identifies indices where the rank estimate decreases
       relative to the previous finite estimate, indicating a structural
       change in the constraint system.

    3. **failure_boundary**: Locates the first index where ``status != "solved"``,
       marking the practical limit of numerical stability for the sweep.

    Args:
        points: StabilityPoint list from ``stability_solve``.

    Returns:
        StabilityAnalysis with trend, drops, and boundary information.
    """
    # --- condition trend ---
    cond_pairs = _finite_condition_pairs(points)
    cond_values = [c for _, c in cond_pairs]

    condition_trend = "insufficient_data"
    condition_trend_slope: Optional[float] = None

    if len(cond_values) >= 3:
        n = len(cond_values)
        x_mean = (n - 1) / 2.0
        y_mean = sum(cond_values) / n
        num = sum(
            (i - x_mean) * (c - y_mean) for i, c in enumerate(cond_values)
        )
        den = sum((i - x_mean) ** 2 for i in range(n))
        if den > 0:
            slope = num / den
            condition_trend_slope = slope
            normalized_slope = slope / y_mean if y_mean != 0 else slope

            direction_changes = 0
            prev_diff = None
            for j in range(1, len(cond_values)):
                diff = cond_values[j] - cond_values[j - 1]
                if prev_diff is not None and diff * prev_diff < 0:
                    direction_changes += 1
                if diff != 0:
                    prev_diff = diff

            if direction_changes >= max(1, len(cond_values) // 3):
                condition_trend = "oscillating"
            elif abs(normalized_slope) < 0.01:
                condition_trend = "stable"
            elif slope > 0:
                condition_trend = "increasing"
            else:
                condition_trend = "decreasing"

    # --- rank drops ---
    rank_drops: List[int] = []
    prev_rank: Optional[int] = None
    for i, p in enumerate(points):
        if p.rank_estimate is not None:
            if prev_rank is not None and p.rank_estimate < prev_rank:
                rank_drops.append(i)
            prev_rank = p.rank_estimate

    # --- failure boundary ---
    failure_boundary: Optional[int] = None
    failure_boundary_value: Optional[float] = None
    for i, p in enumerate(points):
        if p.status != "solved":
            failure_boundary = i
            failure_boundary_value = p.value
            break

    # --- min / max condition ---
    min_condition = min(cond_values) if cond_values else None
    max_condition = max(cond_values) if cond_values else None

    failure_count = sum(1 for p in points if p.status != "solved")

    return StabilityAnalysis(
        condition_trend=condition_trend,
        condition_trend_slope=condition_trend_slope,
        rank_drops=rank_drops,
        failure_boundary=failure_boundary,
        failure_boundary_value=failure_boundary_value,
        min_condition=min_condition,
        max_condition=max_condition,
        points_count=len(points),
        failure_count=failure_count,
    )


# ---------------------------------------------------------------------------
# Scene loading
# ---------------------------------------------------------------------------


def _load_scene(scene_path: str) -> dict:
    """Load a scene file, converting from GCS graph format if needed.

    Detects format by checking for a ``format_version`` key (public scene)
    vs. a ``gcs_graph_id`` or ``graph_id`` key (GCS graph).
    """
    with open(scene_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    # Public scene already has format_version
    if "format_version" in data and str(data.get("format_version", "")).startswith(
        "gcs-"
    ):
        return data

    # Assume GCS graph format — convert via solver_scene_from_gcs
    return solver_scene_from_gcs(data)


# ---------------------------------------------------------------------------
# Sweep spec builder
# ---------------------------------------------------------------------------


def _parse_range_str(range_str: str, steps: int) -> Dict[str, Any]:
    """Parse a comma-separated range string like '1e-12,1e12'."""
    parts = range_str.split(",")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid range spec: {range_str!r}. Expected 'start,end'"
        )
    return {"start": float(parts[0]), "end": float(parts[1]), "steps": steps}


def _build_sweep_spec(args: argparse.Namespace) -> Dict[str, Any]:
    """Build sweep specification dict from parsed CLI arguments."""
    spec: Dict[str, Any] = {"type": args.sweep}

    if args.sweep == "logspace":
        parsed = _parse_range_str(args.range or "1e-12,1e12", args.steps)
        spec.update(parsed)
    elif args.sweep == "near_zero":
        if args.range:
            spec["epsilon"] = float(args.range.split(",")[0])
    elif args.sweep == "linear":
        parsed = _parse_range_str(args.range or "0,1", args.steps)
        spec.update(parsed)

    return spec


# ---------------------------------------------------------------------------
# Main run orchestration
# ---------------------------------------------------------------------------


def run(
    scene_path: str,
    constraint_index: int,
    sweep_spec: dict,
    solver_command: Optional[List[str]] = None,
    timeout_seconds: float = 30.0,
) -> StabilityResult:
    """Orchestrate a full numeric stability pipeline run.

    Loads the scene, generates the value sweep for the target constraint,
    runs the solver at each sweep point, analyzes the collected data, and
    returns a complete ``StabilityResult``.

    Args:
        scene_path: Path to scene JSON file (public scene or GCS graph).
        constraint_index: Index into the constraints list to sweep.
        sweep_spec: Value sweep specification (see ``generate_value_sweep``).
        solver_command: Solver executable command list; auto-detected if None.
        timeout_seconds: Per-solve timeout in seconds.

    Returns:
        StabilityResult with all data points and analysis.

    Raises:
        FileNotFoundError: If *scene_path* does not exist.
        RuntimeError: If the GCS solver cannot be found.
        ValueError: If *constraint_index* is out of range.
    """
    started = time.monotonic()

    if solver_command is None:
        solver_command = find_solver()
    if solver_command is None:
        raise RuntimeError(
            "GCS solver not found. Set GCS_EXE, pass solver_command, or build the project."
        )

    if not os.path.exists(scene_path):
        raise FileNotFoundError(f"Scene file not found: {scene_path}")

    scene = _load_scene(scene_path)
    constraints = scene.get("constraints", [])

    if constraint_index < 0 or constraint_index >= len(constraints):
        raise ValueError(
            f"Constraint index {constraint_index} out of range "
            f"(0..{len(constraints) - 1})"
        )

    constraint = constraints[constraint_index]
    ctype = _resolve_constraint_type(constraint)

    # Generate sweep values
    sweep_values = generate_value_sweep(constraint, sweep_spec)

    # Run stability solves
    points = stability_solve(
        scene, sweep_values, constraint_index, solver_command, timeout_seconds
    )

    # Analyze results
    analysis = analyze_stability(points)

    duration_ms = int((time.monotonic() - started) * 1000)

    return StabilityResult(
        scene_path=os.path.abspath(scene_path),
        constraint_index=constraint_index,
        constraint_type=ctype,
        sweep_spec=sweep_spec,
        points=points,
        analysis=analysis,
        solver_command=solver_command,
        duration_ms=duration_ms,
    )


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------


def format_stability_report(result: StabilityResult) -> str:
    """Format a human-readable stability report string."""
    lines: List[str] = []
    sep = "=" * 70
    minor = "-" * 70

    lines.append(sep)
    lines.append("NUMERIC STABILITY PIPELINE REPORT")
    lines.append(sep)
    lines.append(f"Scene:            {result.scene_path}")
    lines.append(
        f"Constraint:       #{result.constraint_index} ({result.constraint_type})"
    )
    lines.append(f"Sweep type:       {result.sweep_spec.get('type')}")
    if result.sweep_spec.get("type") in ("logspace", "linear"):
        lines.append(
            f"Range:            {result.sweep_spec.get('start'):.1e} to "
            f"{result.sweep_spec.get('end'):.1e}"
        )
        lines.append(f"Steps:            {result.sweep_spec.get('steps')}")
    lines.append(f"Solver:           {' '.join(result.solver_command)}")
    lines.append(f"Total duration:   {result.duration_ms} ms")
    lines.append("")

    a = result.analysis
    lines.append(minor)
    lines.append("STABILITY ANALYSIS")
    lines.append(minor)
    lines.append(f"Points tested:    {a.points_count}")
    lines.append(f"Failures:         {a.failure_count}")
    lines.append(f"Condition trend:  {a.condition_trend}")
    if a.condition_trend_slope is not None:
        lines.append(f"  Slope:          {a.condition_trend_slope:.6f}")
    if a.min_condition is not None:
        lines.append(f"  Min condition:  {a.min_condition:.2e}")
    if a.max_condition is not None:
        lines.append(f"  Max condition:  {a.max_condition:.2e}")
    if a.rank_drops:
        lines.append(f"Rank drops at:    {a.rank_drops}")
    else:
        lines.append("Rank drops:       none detected")
    if a.failure_boundary is not None:
        lines.append(
            f"Failure boundary: index {a.failure_boundary} "
            f"(value={a.failure_boundary_value:.6e})"
        )
    else:
        lines.append("Failure boundary: none (all solves succeeded)")
    lines.append("")

    # Data table
    lines.append(minor)
    header = (
        f"{'#':>4} {'Value':>14} {'Status':>10} {'Exit':>5} "
        f"{'Rank':>6} {'Condition':>14} {'Residual':>14} {'T(ms)':>8}"
    )
    lines.append(header)
    lines.append(minor)
    for i, p in enumerate(result.points):
        cond_s = f"{p.condition_estimate:.4e}" if p.condition_estimate is not None else "N/A"
        res_s = f"{p.residual_norm:.4e}" if p.residual_norm is not None else "N/A"
        rank_s = str(p.rank_estimate) if p.rank_estimate is not None else "N/A"
        lines.append(
            f"{i:>4} {p.value:>14.6e} {p.status:>10} {p.exit_code:>5} "
            f"{rank_s:>6} {cond_s:>14} {res_s:>14} {p.duration_ms:>8}"
        )
    lines.append(minor)
    lines.append("")

    # Findings
    lines.append(minor)
    lines.append("FINDINGS")
    lines.append(minor)
    if a.condition_trend == "increasing":
        lines.append(
            "WARNING: Condition number increases monotonically with value. "
            "The problem may become ill-conditioned at extreme values."
        )
    if a.condition_trend == "oscillating":
        lines.append(
            "NOTE: Condition number oscillates across the sweep range. "
            "This may indicate nonlinear sensitivity to the parameter."
        )
    if a.rank_drops:
        lines.append(
            f"WARNING: {len(a.rank_drops)} rank drop(s) detected. "
            "The system may lose effective constraints at these values."
        )
    if a.failure_boundary is not None:
        lines.append(
            f"NOTE: Solver failures begin at value "
            f"{a.failure_boundary_value:.6e} (index {a.failure_boundary}). "
            "This marks the practical stability limit for this constraint."
        )
    if (
        a.condition_trend in ("stable", "decreasing", "insufficient_data")
        and not a.rank_drops
        and a.failure_boundary is None
    ):
        lines.append(
            "PASS: No stability issues detected across the sweep range."
        )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------


def stability_result_to_dict(result: StabilityResult) -> dict:
    """Serialize a StabilityResult to a JSON-safe dict."""
    return {
        "scene_path": result.scene_path,
        "constraint_index": result.constraint_index,
        "constraint_type": result.constraint_type,
        "sweep_spec": result.sweep_spec,
        "analysis": {
            "condition_trend": result.analysis.condition_trend,
            "condition_trend_slope": result.analysis.condition_trend_slope,
            "rank_drops": result.analysis.rank_drops,
            "failure_boundary": result.analysis.failure_boundary,
            "failure_boundary_value": result.analysis.failure_boundary_value,
            "min_condition": result.analysis.min_condition,
            "max_condition": result.analysis.max_condition,
            "points_count": result.analysis.points_count,
            "failure_count": result.analysis.failure_count,
        },
        "points": [
            {
                "value": p.value,
                "status": p.status,
                "exit_code": p.exit_code,
                "rank_estimate": p.rank_estimate,
                "condition_estimate": p.condition_estimate,
                "residual_norm": p.residual_norm,
                "duration_ms": p.duration_ms,
            }
            for p in result.points
        ],
        "duration_ms": result.duration_ms,
    }


# ---------------------------------------------------------------------------
# StabilityPipeline class (canonical entry point)
# ---------------------------------------------------------------------------


class StabilityPipeline:
    """Numeric Stability Pipeline for testing solver under extreme conditions.

    Provides the canonical class-based interface. All methods are also
    available as module-level functions for direct use.

    Usage::

        pipeline = StabilityPipeline()
        sweep = pipeline.generate_value_sweep(constraint, {"type": "logspace", ...})
        points = pipeline.stability_solve(scene, sweep, 0, solver_cmd)
        analysis = pipeline.analyze_stability(points)
        result = pipeline.run("scene.json", 0, {"type": "logspace", ...})
    """

    @staticmethod
    def generate_value_sweep(constraint: dict, range_spec: dict) -> List[float]:
        """Generate test values for a constraint value sweep.

        See :func:`generate_value_sweep` for full documentation.
        """
        return generate_value_sweep(constraint, range_spec)

    @staticmethod
    def generate_geometry_perturbations(geometry: dict) -> Dict[str, dict]:
        """Generate perturbed geometry vectors for stability testing.

        See :func:`generate_geometry_perturbations` for full documentation.
        """
        return generate_geometry_perturbations(geometry)

    @staticmethod
    def stability_solve(
        scene: dict,
        value_sweep: List[float],
        constraint_index: int,
        solver_command: List[str],
        timeout_seconds: float = 30.0,
    ) -> List[StabilityPoint]:
        """Run solver for each test value, modifying the specified constraint.

        See :func:`stability_solve` for full documentation.
        """
        return stability_solve(
            scene, value_sweep, constraint_index, solver_command, timeout_seconds
        )

    @staticmethod
    def analyze_stability(points: List[StabilityPoint]) -> StabilityAnalysis:
        """Analyze stability sweep results for degradation patterns.

        See :func:`analyze_stability` for full documentation.
        """
        return analyze_stability(points)

    @staticmethod
    def run(
        scene_path: str,
        constraint_index: int,
        sweep_spec: dict,
        solver_command: Optional[List[str]] = None,
        timeout_seconds: float = 30.0,
    ) -> StabilityResult:
        """Orchestrate a full numeric stability pipeline run.

        See :func:`run` for full documentation.
        """
        return run(
            scene_path, constraint_index, sweep_spec, solver_command, timeout_seconds
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Numeric Stability Pipeline — test solver under extreme numerical conditions.",
    )
    parser.add_argument(
        "--scene",
        required=True,
        help="Path to scene JSON file (public scene or GCS graph format).",
    )
    parser.add_argument(
        "--constraint",
        type=int,
        required=True,
        help="Index of the constraint to sweep (0-based).",
    )
    parser.add_argument(
        "--sweep",
        default="logspace",
        choices=["logspace", "near_zero", "boundaries", "linear"],
        help="Sweep type (default: logspace).",
    )
    parser.add_argument(
        "--range",
        default=None,
        help="Value range as 'start,end' (e.g. '1e-12,1e12'). "
        "For logspace/linear sweeps this sets the range. "
        "For near_zero the first value is used as epsilon.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=20,
        help="Number of sweep steps for logspace/linear (default: 20).",
    )
    parser.add_argument(
        "--solver",
        default=None,
        help="Path to solver executable (auto-detected if omitted).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Per-solve timeout in seconds (default: 30).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of a human-readable report.",
    )
    args = parser.parse_args()

    # Resolve solver command
    solver_command: Optional[List[str]] = None
    if args.solver:
        solver_command = [args.solver]
    else:
        solver_command = find_solver()
    if solver_command is None:
        print(
            "ERROR: GCS solver not found. Set GCS_EXE, use --solver, or build the project.",
            file=sys.stderr,
        )
        sys.exit(1)

    sweep_spec = _build_sweep_spec(args)

    try:
        result = run(
            scene_path=args.scene,
            constraint_index=args.constraint,
            sweep_spec=sweep_spec,
            solver_command=solver_command,
            timeout_seconds=args.timeout,
        )
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(stability_result_to_dict(result), indent=2, sort_keys=True))
    else:
        print(format_stability_report(result))

    # Exit non-zero on significant stability issues
    a = result.analysis
    if a.condition_trend == "increasing" and a.rank_drops:
        sys.exit(2)
    if a.failure_count > len(result.points) // 2:
        sys.exit(2)


if __name__ == "__main__":
    main()
