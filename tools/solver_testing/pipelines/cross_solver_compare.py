#!/usr/bin/env python3
"""Cross-Solver Compare Pipeline.

Compares GCS solver results against external solvers on shared benchmark sets.
Produces agreement statistics and comparison reports.

Usage:
  python tools/solver_testing/pipelines/cross_solver_compare.py \
      --benchmark fixtures/benchmark/ \
      --external external_solver.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any, Callable

# Ensure the solver_testing package is importable.
_TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.abspath(os.path.join(_TOOL_DIR, "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tools.solver_testing.runner import SolveResult, _parse_solver_output, find_solver, run_single


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ExternalSolverSpec:
    """Specification for an external solver to compare against.

    Attributes:
        name: Human-readable solver name (e.g. "solvespace-cli").
        command: Executable + args template.  ``{}`` is replaced with the
            input file path at runtime.
        input_converter_name: Key of the registered InputConverter to use.
        output_parser_name: Key of the registered OutputParser to use.
        source_citation: URL or reference for provenance tracking.
    """

    name: str
    command: list[str]
    input_converter_name: str
    output_parser_name: str
    source_citation: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> ExternalSolverSpec:
        return cls(
            name=str(d["name"]),
            command=[str(arg) for arg in d["command"]],
            input_converter_name=str(d["input_converter"]),
            output_parser_name=str(d["output_parser"]),
            source_citation=str(d.get("source_citation", "")),
        )

    @classmethod
    def from_json_path(cls, path: str) -> ExternalSolverSpec:
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


@dataclass
class ComparisonPoint:
    """Result of comparing a single scene across two solvers.

    Attributes:
        scene_id: Identifier for the scene (file stem).
        gcs_status: Status string from the GCS SolveResult.
        external_status: Status string from the external SolveResult.
        agree: True when both solvers agree (both solved or both failed).
        details: Optional supplementary information (durations, exit codes, etc.).
    """

    scene_id: str
    gcs_status: str
    external_status: str
    agree: bool
    details: dict = field(default_factory=dict)


@dataclass
class ComparisonReport:
    """Aggregate report produced by a full corpus comparison.

    Attributes:
        benchmark_dir: Absolute path to the benchmark directory.
        external_solver_name: Name from the ExternalSolverSpec.
        total_scenes: Number of scenes compared.
        agreement_rate: Fraction of scenes where both solvers agreed.
        gcs_only_count: Scenes solved by GCS but not by the external solver.
        external_only_count: Scenes solved by the external solver but not by GCS.
        comparison_points: Per-scene ComparisonPoint list.
        timestamp: ISO-8601 timestamp when the report was generated.
    """

    benchmark_dir: str
    external_solver_name: str
    total_scenes: int
    agreement_rate: float
    gcs_only_count: int
    external_only_count: int
    comparison_points: list = field(default_factory=list)
    timestamp: str = ""


# ---------------------------------------------------------------------------
# Converter helpers
# ---------------------------------------------------------------------------


def _format_float(value: Any) -> str:
    """Format a numeric value for the custom_text_v1 format."""
    return f"{float(value):.12g}"


def _convert_identity(scene_dict: dict) -> str:
    """Pass-through: return the scene as pretty-printed JSON."""
    return json.dumps(scene_dict, indent=2, sort_keys=True) + "\n"


def _convert_gcs_custom_text(scene_dict: dict) -> str:
    """Convert a gcs-0.3 scene dict to the custom_text_v1 wire format.

    The custom_text_v1 format is the text format consumed by GCS.exe natively.
    Layout::

        <num_rigid_sets>
        <rs_id> [<rs_id> ...]
        <num_geometries>
        <geom_id> <type_int> <rigid_set_id>   (one per geometry)
        <num_constraints>
        <cid> <type_int> <arity> <gid> [<gid> ...]   (one per constraint)
        <blank line>
        <geom_id> <v0> <v1> <v2> <v3> <v4> <v5>   (one per geometry)
        <blank line>
        <cid> <value>   (one per constraint)
    """
    rigid_sets = sorted(scene_dict.get("rigid_sets", []), key=lambda rs: int(rs.get("id", 0)))
    geometries = sorted(scene_dict.get("geometries", []), key=lambda g: int(g.get("id", 0)))
    constraints = sorted(scene_dict.get("constraints", []), key=lambda c: int(c.get("id", 0)))

    lines: list[str] = []

    # Header
    lines.append(str(len(rigid_sets)))
    if rigid_sets:
        lines.append(" ".join(str(rs["id"]) for rs in rigid_sets))

    lines.append(str(len(geometries)))
    for geom in geometries:
        gtype = int(geom.get("type", 0))
        rs_id = int(geom.get("rigid_set_id", 0))
        lines.append(f"{geom['id']} {gtype} {rs_id}")

    lines.append(str(len(constraints)))
    for constraint in constraints:
        ctype = int(constraint.get("type", 0))
        gids = [int(gid) for gid in constraint.get("geometry_ids", [])]
        gids_str = " ".join(str(gid) for gid in gids)
        lines.append(f"{constraint['id']} {ctype} {len(gids)} {gids_str}")

    # Parameter / value block
    lines.append("")
    for geom in geometries:
        v = [float(x) for x in geom.get("v", [0.0] * 6)]
        v = (v + [0.0] * 6)[:6]
        values_str = " ".join(_format_float(x) for x in v)
        lines.append(f"{geom['id']} {values_str}")

    lines.append("")
    for constraint in constraints:
        value = float(constraint.get("value", 0.0))
        lines.append(f"{constraint['id']} {_format_float(value)}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Parser helpers
# ---------------------------------------------------------------------------


def _parse_gcs_stdout(stdout: str, stderr: str) -> SolveResult:
    """Parse GCS.exe stdout using the existing runner.py parser.

    Returns a SolveResult with status set from the parsed output.
    """
    parsed = _parse_solver_output(stdout)
    return SolveResult(
        scene_id="",  # caller fills in
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        duration_ms=0,
        status=parsed.get("status", "unknown"),
        rank_evidence=parsed.get("rank_evidence"),
        diagnostics_present=parsed.get("diagnostics_present", False),
        error_summary=(stderr[:200] if stderr else ""),
    )


def _parse_generic_status(stdout: str, stderr: str) -> SolveResult:
    """Parse solver output looking for generic solved/failed indicators.

    Checks the combined stdout+stderr for keywords.  Intended as a
    lowest-common-denominator parser for third-party solvers.
    """
    combined = (stdout + "\n" + stderr).lower()
    if any(kw in combined for kw in ("solved", "accepted", "solution found", "ok")):
        status = "solved"
    elif any(kw in combined for kw in ("failed", "error", "unsatisfiable", "inconsistent")):
        status = "failed"
    else:
        status = "unknown"
    return SolveResult(
        scene_id="",
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        duration_ms=0,
        status=status,
        error_summary=(stderr[:200] if stderr else ""),
    )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


class CrossSolverComparePipeline:
    """Compare GCS results against an external solver on a shared benchmark corpus.

    Typical usage::

        pipeline = CrossSolverComparePipeline()
        report = pipeline.run("fixtures/benchmark/", "external_solver.json", None)
        print(f"Agreement rate: {report.agreement_rate:.1%}")
    """

    def __init__(self) -> None:
        self.input_converters: dict[str, Callable[[dict], str]] = {}
        self.output_parsers: dict[str, Callable[[str, str], SolveResult]] = {}
        self._register_defaults()

    # -- registry ----------------------------------------------------------

    def register_converter(self, name: str, fn: Callable[[dict], str]) -> None:
        """Register an input converter function.

        Args:
            name: Key used to reference this converter in ExternalSolverSpec.
            fn: ``(scene_dict: dict) -> str`` — converts a gcs-0.3 scene dict
                into the solver-specific input format.
        """
        self.input_converters[name] = fn

    def register_parser(self, name: str, fn: Callable[[str, str], SolveResult]) -> None:
        """Register an output parser function.

        Args:
            name: Key used to reference this parser in ExternalSolverSpec.
            fn: ``(stdout: str, stderr: str) -> SolveResult`` — parses solver
                output into a :class:`SolveResult`.
        """
        self.output_parsers[name] = fn

    def _register_defaults(self) -> None:
        """Populate the built-in converter and parser registries."""
        self.register_converter("identity", _convert_identity)
        self.register_converter("gcs_custom_text", _convert_gcs_custom_text)
        self.register_parser("gcs_stdout", _parse_gcs_stdout)
        self.register_parser("generic_status", _parse_generic_status)

    # -- comparison --------------------------------------------------------

    @staticmethod
    def compare_single(gcs_result: SolveResult, external_result: SolveResult) -> ComparisonPoint:
        """Compare two SolveResult objects for a single scene.

        Agreement is defined as both solvers reporting ``"solved"`` or both
        reporting a non-solved status.

        Args:
            gcs_result: SolveResult from GCS.
            external_result: SolveResult from the external solver.

        Returns:
            ComparisonPoint with agreement determination.
        """
        gcs_ok = gcs_result.status == "solved"
        ext_ok = external_result.status == "solved"
        agree = gcs_ok == ext_ok

        scene_id = gcs_result.scene_id or external_result.scene_id
        return ComparisonPoint(
            scene_id=scene_id,
            gcs_status=gcs_result.status,
            external_status=external_result.status,
            agree=agree,
            details={
                "gcs_exit_code": gcs_result.exit_code,
                "gcs_duration_ms": gcs_result.duration_ms,
                "external_exit_code": external_result.exit_code,
                "external_duration_ms": external_result.duration_ms,
                "gcs_diagnostics_present": gcs_result.diagnostics_present,
            },
        )

    # -- corpus execution --------------------------------------------------

    def _scene_files(self, benchmark_dir: str) -> list[tuple[str, str]]:
        """Return ``[(abs_path, scene_id), ...]`` for scorable files.

        Includes ``*.gcs.json``, ``*.txt``, and ``*.json`` files, excluding
        manifest / metadata files.
        """
        entries: list[tuple[str, str]] = []
        seen_ids: set[str] = set()
        exclusions = {"manifest", "metadata"}

        for fname in sorted(os.listdir(benchmark_dir)):
            fpath = os.path.join(benchmark_dir, fname)
            if not os.path.isfile(fpath):
                continue

            # Determine the scene id and whether this file is scorable.
            scene_id: str | None = None
            if fname.endswith(".gcs.json"):
                scene_id = fname[: -len(".gcs.json")]
            elif fname.endswith(".txt"):
                scene_id = fname[: -len(".txt")]
            elif fname.endswith(".json"):
                base = fname[: -len(".json")]
                # Skip obvious non-scene files.
                if any(excl in base.lower() for excl in exclusions):
                    continue
                scene_id = base
            else:
                continue

            if scene_id in seen_ids:
                # Prefer .gcs.json over .json, and .txt over both when duplicates exist.
                continue
            seen_ids.add(scene_id)
            entries.append((os.path.abspath(fpath), scene_id))

        return entries

    @staticmethod
    def _load_scene_dict(scene_path: str) -> dict:
        """Load a scene file into a gcs-0.3 dict, regardless of format.

        Supports:
        - ``.gcs.json`` / ``.json``: direct load.
        - ``.txt``: parsed via :func:`read_graph_file` from the algebra module,
          then converted to dict via ``to_dict()``.
        """
        if scene_path.endswith(".json"):
            with open(scene_path, "r", encoding="utf-8") as f:
                return json.load(f)

        # Text format — use the algebra module's parser.
        from python.gcs_viz.algebra import read_graph_file

        graph = read_graph_file(scene_path)
        return graph.to_dict()

    def _run_external(
        self,
        converted_input: str,
        spec: ExternalSolverSpec,
        scene_id: str,
        timeout_seconds: float = 60.0,
    ) -> SolveResult:
        """Run an external solver on the converted input and parse its output.

        Args:
            converted_input: The scene file content in the external solver's format.
            spec: ExternalSolverSpec describing command, parser, etc.
            scene_id: Scene identifier for the result.
            timeout_seconds: Per-run timeout.

        Returns:
            SolveResult with the external solver's outcome.
        """
        parser = self.output_parsers.get(spec.output_parser_name)
        if parser is None:
            return SolveResult(
                scene_id=scene_id,
                exit_code=-3,
                stdout="",
                stderr=f"Unknown output parser: {spec.output_parser_name}",
                duration_ms=0,
                status="crash",
            )

        # Write converted input to a temp file so the external solver can read it.
        suffix = ".txt"
        if spec.input_converter_name == "identity":
            suffix = ".json"
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, delete=False, encoding="utf-8"
        )
        try:
            tmp.write(converted_input)
            tmp.close()

            # Build the command, substituting {} with the temp file path.
            command = [tmp.name if arg == "{}" else arg for arg in spec.command]

            started = time.monotonic()
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            duration_ms = int((time.monotonic() - started) * 1000)

            result = parser(completed.stdout, completed.stderr)
            result.scene_id = scene_id
            result.exit_code = completed.returncode
            result.duration_ms = duration_ms
            return result

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
        except FileNotFoundError:
            return SolveResult(
                scene_id=scene_id,
                exit_code=-4,
                stdout="",
                stderr=f"External solver command not found: {spec.command[0]}",
                duration_ms=0,
                status="crash",
            )
        except Exception as exc:
            return SolveResult(
                scene_id=scene_id,
                exit_code=-2,
                stdout="",
                stderr=str(exc),
                duration_ms=0,
                status="crash",
            )
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass

    def compare_corpus(
        self,
        benchmark_dir: str,
        external_spec: ExternalSolverSpec,
        solver_command: list[str] | None = None,
        timeout_seconds: float = 60.0,
    ) -> ComparisonReport:
        """Run GCS and the external solver on every scene in *benchmark_dir*.

        Args:
            benchmark_dir: Directory containing scene files (``.gcs.json``,
                ``.txt``, ``.json``).
            external_spec: Specification for the external solver.
            solver_command: GCS solver command.  Auto-detected when ``None``.
            timeout_seconds: Per-solve timeout for each solver.

        Returns:
            ComparisonReport with per-scene comparisons and aggregate statistics.
        """
        if solver_command is None:
            solver_command = find_solver()
        if solver_command is None:
            raise RuntimeError(
                "GCS solver not found. Set GCS_EXE or build the project."
            )

        converter = self.input_converters.get(external_spec.input_converter_name)
        if converter is None:
            raise ValueError(
                f"Unknown input converter: {external_spec.input_converter_name}. "
                f"Registered: {list(self.input_converters)}"
            )
        if external_spec.output_parser_name not in self.output_parsers:
            raise ValueError(
                f"Unknown output parser: {external_spec.output_parser_name}. "
                f"Registered: {list(self.output_parsers)}"
            )

        scene_entries = self._scene_files(benchmark_dir)
        if not scene_entries:
            print(f"Warning: no scorable scene files found in {benchmark_dir}")

        comparison_points: list[ComparisonPoint] = []
        gcs_only_count = 0
        external_only_count = 0

        for scene_path, scene_id in scene_entries:
            # 1. GCS solve on the original scene file.
            gcs_result = run_single(scene_path, scene_id, solver_command, timeout_seconds)

            # 2. Load scene dict, convert, and run external solver.
            try:
                scene_dict = self._load_scene_dict(scene_path)
            except Exception as exc:
                # If we cannot load/convert the scene, record as a crash for external.
                external_result = SolveResult(
                    scene_id=scene_id,
                    exit_code=-5,
                    stdout="",
                    stderr=f"Scene load/conversion error: {exc}",
                    duration_ms=0,
                    status="crash",
                )
            else:
                converted = converter(scene_dict)
                external_result = self._run_external(
                    converted, external_spec, scene_id, timeout_seconds
                )

            # 3. Compare.
            point = self.compare_single(gcs_result, external_result)
            comparison_points.append(point)

            # 4. Update divergence counts.
            if gcs_result.status == "solved" and external_result.status != "solved":
                gcs_only_count += 1
            elif external_result.status == "solved" and gcs_result.status != "solved":
                external_only_count += 1

            print(
                f"  {scene_id}: GCS={gcs_result.status}  "
                f"ext({external_spec.name})={external_result.status}  "
                f"agree={point.agree}"
            )

        total = len(comparison_points)
        agreement_rate = (
            sum(1 for p in comparison_points if p.agree) / total if total else 0.0
        )

        return ComparisonReport(
            benchmark_dir=os.path.abspath(benchmark_dir),
            external_solver_name=external_spec.name,
            total_scenes=total,
            agreement_rate=agreement_rate,
            gcs_only_count=gcs_only_count,
            external_only_count=external_only_count,
            comparison_points=comparison_points,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )

    # -- top-level entry point ------------------------------------------------

    def run(
        self,
        benchmark_dir: str,
        external_spec_path: str,
        solver_command: list[str] | None = None,
        timeout_seconds: float = 60.0,
    ) -> ComparisonReport:
        """Load an external solver spec from JSON and run the full comparison.

        Args:
            benchmark_dir: Directory containing scene files.
            external_spec_path: Path to an external solver spec JSON file.
            solver_command: GCS solver command (auto-detected when ``None``).
            timeout_seconds: Per-solve timeout for each solver.

        Returns:
            ComparisonReport with aggregate statistics and per-scene details.
        """
        if not os.path.isdir(benchmark_dir):
            raise ValueError(f"benchmark_dir does not exist or is not a directory: {benchmark_dir}")
        if not os.path.isfile(external_spec_path):
            raise FileNotFoundError(f"External solver spec not found: {external_spec_path}")

        external_spec = ExternalSolverSpec.from_json_path(external_spec_path)
        print(f"External solver: {external_spec.name}")
        print(f"  Command:       {' '.join(external_spec.command)}")
        print(f"  Converter:     {external_spec.input_converter_name}")
        print(f"  Parser:        {external_spec.output_parser_name}")
        if external_spec.source_citation:
            print(f"  Citation:      {external_spec.source_citation}")
        print()

        return self.compare_corpus(
            benchmark_dir=benchmark_dir,
            external_spec=external_spec,
            solver_command=solver_command,
            timeout_seconds=timeout_seconds,
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Cross-Solver Compare Pipeline — compare GCS against external solvers.",
    )
    parser.add_argument(
        "--benchmark",
        required=True,
        help="Path to benchmark directory containing scene files.",
    )
    parser.add_argument(
        "--external",
        required=True,
        dest="external_spec_path",
        help="Path to external solver spec JSON file.",
    )
    parser.add_argument(
        "--solver",
        default=None,
        help="GCS solver executable path (auto-detected when omitted).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Per-solve timeout in seconds (default: 60).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write the ComparisonReport as JSON.",
    )
    args = parser.parse_args(argv)

    solver_command = [args.solver] if args.solver else find_solver()

    pipeline = CrossSolverComparePipeline()
    report = pipeline.run(
        benchmark_dir=args.benchmark,
        external_spec_path=args.external_spec_path,
        solver_command=solver_command,
        timeout_seconds=args.timeout,
    )

    # Print summary.
    print()
    print("=" * 60)
    print("CROSS-SOLVER COMPARISON REPORT")
    print("=" * 60)
    print(f"Benchmark:            {report.benchmark_dir}")
    print(f"External solver:      {report.external_solver_name}")
    print(f"Total scenes:         {report.total_scenes}")
    print(f"Agreement rate:       {report.agreement_rate:.1%}")
    print(f"GCS-only solved:      {report.gcs_only_count}")
    print(f"External-only solved: {report.external_only_count}")
    print(f"Timestamp:            {report.timestamp}")
    print()

    # Per-scene detail for any disagreements.
    disagreements = [p for p in report.comparison_points if not p.agree]
    if disagreements:
        print(f"Disagreements ({len(disagreements)}):")
        for point in disagreements:
            print(
                f"  {point.scene_id}: "
                f"GCS={point.gcs_status}  "
                f"ext={point.external_status}"
            )
        print()

    # Optionally write JSON output.
    if args.output:
        output_data = {
            "benchmark_dir": report.benchmark_dir,
            "external_solver_name": report.external_solver_name,
            "total_scenes": report.total_scenes,
            "agreement_rate": report.agreement_rate,
            "gcs_only_count": report.gcs_only_count,
            "external_only_count": report.external_only_count,
            "timestamp": report.timestamp,
            "comparison_points": [
                {
                    "scene_id": p.scene_id,
                    "gcs_status": p.gcs_status,
                    "external_status": p.external_status,
                    "agree": p.agree,
                    "details": p.details,
                }
                for p in report.comparison_points
            ],
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, sort_keys=True)
        print(f"Report written to: {args.output}")


if __name__ == "__main__":
    main()
