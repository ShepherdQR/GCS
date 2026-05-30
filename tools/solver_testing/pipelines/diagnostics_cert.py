#!/usr/bin/env python3
"""Diagnostic Certification Pipeline.

Verifies solver produces correct diagnostic output for known-bad inputs.
Constructs scenes with specific errors and asserts the solver reports
expected error codes.

Usage:
  python tools/solver_testing/pipelines/diagnostics_cert.py [--strict]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Any

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.abspath(os.path.join(TOOL_DIR, "..", ".."))
sys.path.insert(0, REPO_ROOT)

from tools.scene_generation.gcs_scene_generation.promotion import solver_scene_from_gcs
from tools.solver_testing.runner import find_solver, run_single


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class CertResult:
    """Single diagnostic certification result."""

    scene_id: str
    passed: bool
    expected: str
    actual: str
    solver_output: str = ""


@dataclass
class CertReport:
    """Aggregate certification report."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    results: list[CertResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Alternate diagnostic code map
# ---------------------------------------------------------------------------

_ALTERNATE_CODES: dict[str, list[str]] = {
    "constraint.invalid_parameter_value": ["invalidmodel", "invalid_parameter_value"],
    "InvalidModel": ["invalidmodel", "invalid_parameter_value"],
    "degenerate": ["degenerate", "invalidmodel"],
    "NumericallySingular": ["numericallysingular", "over_constrained", "under_constrained"],
}


def _extract_code_from_output(combined: str) -> str:
    """Extract the best diagnostic code match from combined solver output."""
    lower = combined.lower()
    # Ordered by specificity — most specific first
    candidates = [
        ("constraint.invalid_parameter_value", "invalid_parameter_value"),
        ("InvalidModel", "invalidmodel"),
        ("NumericallySingular", "numericallysingular"),
        ("over_constrained", "over_constrained"),
        ("under_constrained", "under_constrained"),
        ("degenerate", "degenerate"),
    ]
    for label, token in candidates:
        if token in lower:
            return label
    return "unknown"


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


class DiagnosticsCertPipeline:
    """Diagnostic certification pipeline for known-bad inputs.

    Builds a negative corpus of scenes with specific errors, runs each
    through the solver, and checks that the expected diagnostic codes
    appear in the solver output.
    """

    @staticmethod
    def build_negative_corpus() -> list[tuple[dict, str]]:
        """Generate minimal scenes with specific errors.

        Each scene is a GCS dict (geometry/constraint type names as strings)
        paired with an expected diagnostic code substring.

        Returns:
            list of (scene_dict, expected_diagnostic_code)
        """
        corpus: list[tuple[dict, str]] = []

        # 1. negative_distance: 2 Points, 2 RS, 1 Distance constraint with value=-1.0
        corpus.append(({
            "_name": "negative_distance",
            "rigid_sets": [{"id": 0}, {"id": 1}],
            "geometries": [
                {"id": 0, "type": "Point", "rigid_set_id": 0,
                 "v": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
                {"id": 1, "type": "Point", "rigid_set_id": 1,
                 "v": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
            ],
            "constraints": [
                {"id": 0, "type": "Distance", "geometry_ids": [0, 1], "value": -1.0},
            ],
        }, "constraint.invalid_parameter_value"))

        # 2. invalid_angle: 2 Lines, 2 RS, 1 Angle constraint with value=7.0 (>pi)
        corpus.append(({
            "_name": "invalid_angle",
            "rigid_sets": [{"id": 0}, {"id": 1}],
            "geometries": [
                {"id": 0, "type": "Line", "rigid_set_id": 0,
                 "v": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0]},
                {"id": 1, "type": "Line", "rigid_set_id": 1,
                 "v": [0.0, 0.0, 0.0, 0.0, 1.0, 0.0]},
            ],
            "constraints": [
                {"id": 0, "type": "Angle", "geometry_ids": [0, 1], "value": 7.0},
            ],
        }, "InvalidModel"))

        # 3. degenerate_line: 2 Lines in different RS, 1 Parallel constraint.
        #    One Line has direction=[0,0,0].
        corpus.append(({
            "_name": "degenerate_line",
            "rigid_sets": [{"id": 0}, {"id": 1}],
            "geometries": [
                {"id": 0, "type": "Line", "rigid_set_id": 0,
                 "v": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0]},
                {"id": 1, "type": "Line", "rigid_set_id": 1,
                 "v": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},  # zero direction
            ],
            "constraints": [
                {"id": 0, "type": "Parallel", "geometry_ids": [0, 1], "value": 0.0},
            ],
        }, "degenerate"))

        # 4. degenerate_plane: 2 Planes, 1 Parallel constraint.
        #    One Plane has normal=[0,0,0].
        corpus.append(({
            "_name": "degenerate_plane",
            "rigid_sets": [{"id": 0}, {"id": 1}],
            "geometries": [
                {"id": 0, "type": "Plane", "rigid_set_id": 0,
                 "v": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0]},
                {"id": 1, "type": "Plane", "rigid_set_id": 1,
                 "v": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},  # zero normal
            ],
            "constraints": [
                {"id": 0, "type": "Parallel", "geometry_ids": [0, 1], "value": 0.0},
            ],
        }, "degenerate"))

        # 5. over_constrained: 2 Points, 2 RS, 5 Distance constraints
        #    (more constraints than DOFs).
        corpus.append(({
            "_name": "over_constrained",
            "rigid_sets": [{"id": 0}, {"id": 1}],
            "geometries": [
                {"id": 0, "type": "Point", "rigid_set_id": 0,
                 "v": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
                {"id": 1, "type": "Point", "rigid_set_id": 1,
                 "v": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
            ],
            "constraints": [
                {"id": 0, "type": "Distance", "geometry_ids": [0, 1], "value": 1.0},
                {"id": 1, "type": "Distance", "geometry_ids": [0, 1], "value": 2.0},
                {"id": 2, "type": "Distance", "geometry_ids": [0, 1], "value": 1.5},
                {"id": 3, "type": "Distance", "geometry_ids": [0, 1], "value": 0.5},
                {"id": 4, "type": "Distance", "geometry_ids": [0, 1], "value": 3.0},
            ],
        }, "NumericallySingular"))

        # 6. under_constrained: 4 Points in 2 RS, only 2 constraints.
        corpus.append(({
            "_name": "under_constrained",
            "rigid_sets": [{"id": 0}, {"id": 1}],
            "geometries": [
                {"id": 0, "type": "Point", "rigid_set_id": 0,
                 "v": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
                {"id": 1, "type": "Point", "rigid_set_id": 0,
                 "v": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
                {"id": 2, "type": "Point", "rigid_set_id": 1,
                 "v": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0]},
                {"id": 3, "type": "Point", "rigid_set_id": 1,
                 "v": [1.0, 1.0, 0.0, 0.0, 0.0, 0.0]},
            ],
            "constraints": [
                {"id": 0, "type": "Distance", "geometry_ids": [0, 1], "value": 1.0},
                {"id": 1, "type": "Distance", "geometry_ids": [2, 3], "value": 1.0},
            ],
        }, "NumericallySingular"))

        return corpus

    @staticmethod
    def certify_scene(
        scene: dict,
        expected_code: str,
        solver_command: list[str],
    ) -> CertResult:
        """Serialize scene to gcs-0.3 JSON, solve, and check for expected
        diagnostic code in solver output.

        Args:
            scene: GCS-format scene dict (string type keys).
            expected_code: Diagnostic code substring expected in output.
            solver_command: Solver executable and arguments.

        Returns:
            CertResult with pass/fail and extracted diagnostics.
        """
        solver_scene = solver_scene_from_gcs(scene)
        scene_id = scene.get("_name", "unnamed")

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gcs.json", delete=False
        ) as f:
            json.dump(solver_scene, f)
            scene_path = f.name

        try:
            result = run_single(scene_path, scene_id, solver_command)
            combined = (result.stdout + " " + result.stderr).lower()

            # Build the set of acceptable codes for this scene
            acceptable = {expected_code.lower()}
            acceptable.update(
                alt.lower() for alt in _ALTERNATE_CODES.get(expected_code, [])
            )

            matched = None
            for code in acceptable:
                if code in combined:
                    matched = code
                    break

            actual = matched or _extract_code_from_output(combined)
            passed = matched is not None

            return CertResult(
                scene_id=scene_id,
                passed=passed,
                expected=expected_code,
                actual=actual,
                solver_output=combined[:1000],
            )
        finally:
            try:
                os.unlink(scene_path)
            except OSError:
                pass

    @staticmethod
    def certify_corpus(
        corpus: list[tuple[dict, str]],
        solver_command: list[str],
    ) -> CertReport:
        """Certify every scene in the corpus.

        Args:
            corpus: List of (scene_dict, expected_code) from build_negative_corpus.
            solver_command: Solver executable and arguments.

        Returns:
            CertReport with aggregate pass/fail counts and per-scene details.
        """
        report = CertReport(total=len(corpus))
        for scene, expected_code in corpus:
            result = DiagnosticsCertPipeline.certify_scene(
                scene, expected_code, solver_command
            )
            report.results.append(result)
            if result.passed:
                report.passed += 1
            else:
                report.failed += 1
        return report

    @staticmethod
    def run(solver_command: list[str] | None = None) -> CertReport:
        """Build corpus, certify all scenes, print results.

        Args:
            solver_command: Solver executable and arguments. Auto-detected if None.

        Returns:
            CertReport with aggregate results.
        """
        if solver_command is None:
            solver_command = find_solver()
        if solver_command is None:
            print("ERROR: GCS solver not found. Set GCS_EXE or build the project.")
            sys.exit(1)

        print(f"Solver: {solver_command[0]}")
        print()

        corpus = DiagnosticsCertPipeline.build_negative_corpus()
        report = DiagnosticsCertPipeline.certify_corpus(corpus, solver_command)

        print("=" * 60)
        print("DIAGNOSTIC CERTIFICATION REPORT")
        print("=" * 60)
        print(f"Total:  {report.total}")
        print(f"Passed: {report.passed}")
        print(f"Failed: {report.failed}")
        print()

        for r in report.results:
            status = "PASS" if r.passed else "FAIL"
            print(f"  [{status}] {r.scene_id}")
            print(f"         expected: {r.expected}")
            print(f"         actual:   {r.actual}")
            if not r.passed:
                output_preview = r.solver_output[:200].replace("\n", " ")
                print(f"         output:   {output_preview}")
            print()

        return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diagnostic Certification Pipeline"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero if any certification fails",
    )
    args = parser.parse_args()

    report = DiagnosticsCertPipeline.run()

    if args.strict and report.failed > 0:
        print(
            f"ERROR: {report.failed} certification(s) failed in strict mode."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
