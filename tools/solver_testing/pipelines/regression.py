"""Solver Regression Pipeline.

Runs the solver on a fixture corpus, compares results against a stored
baseline, and detects regressions (previously-solvable scenes now fail,
or output changes beyond tolerance).

Usage as CLI:
  python tools/solver_testing/pipelines/regression.py --corpus PATH --baseline PATH --tolerance 1e-6
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.abspath(os.path.join(TOOL_DIR, "..", ".."))
sys.path.insert(0, REPO_ROOT)

from tools.solver_testing.runner import SolveResult, find_solver, run_single


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Regression:
    """A single regression detected during comparison."""
    scene_id: str
    baseline_status: str
    current_status: str
    change_type: str          # "status_changed" | "rank_changed" | "residual_grew" | "new_scene"
    baseline_rank: int | None = None
    current_rank: int | None = None
    baseline_residual: float | None = None
    current_residual: float | None = None
    detail: str = ""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_numeric_fields(stdout: str) -> dict[str, Any]:
    """Extract rank_estimate and residual_norm from solver JSON stdout.

    Tries direct top-level keys, then common nested containers
    (summary, diagnostics, solver_output).
    """
    result: dict[str, Any] = {
        "rank_estimate": None,
        "residual_norm": None,
    }
    try:
        data = json.loads(stdout)
        if not isinstance(data, dict):
            return result
    except (json.JSONDecodeError, ValueError, TypeError):
        return result

    # --- Direct top-level keys ---
    for key in ("rank_estimate", "rankEstimate", "rank"):
        val = data.get(key)
        if isinstance(val, (int, float)):
            result["rank_estimate"] = int(val)
            break

    for key in ("residual_norm", "residualNorm", "residual", "residual_max"):
        val = data.get(key)
        if isinstance(val, (int, float)):
            result["residual_norm"] = float(val)
            break

    # --- Nested containers ---
    for container_key in ("summary", "diagnostics", "solver_output"):
        container = data.get(container_key)
        if not isinstance(container, dict):
            continue

        if result["rank_estimate"] is None:
            for key in ("rank_estimate", "rankEstimate", "rank"):
                val = container.get(key)
                if isinstance(val, (int, float)):
                    result["rank_estimate"] = int(val)
                    break

        if result["residual_norm"] is None:
            for key in ("residual_norm", "residualNorm", "residual", "residual_max"):
                val = container.get(key)
                if isinstance(val, (int, float)):
                    result["residual_norm"] = float(val)
                    break

        if result["rank_estimate"] is not None and result["residual_norm"] is not None:
            break

    return result


def _result_to_baseline_entry(result: SolveResult) -> dict[str, Any]:
    """Convert a SolveResult into the per-scene dict stored in a baseline."""
    numeric = _extract_numeric_fields(result.stdout)
    return {
        "status": result.status,
        "exit_code": result.exit_code,
        "rank_estimate": numeric["rank_estimate"],
        "residual_norm": numeric["residual_norm"],
    }


def _git_describe() -> str:
    """Return ``git describe`` for solver-version provenance."""
    try:
        completed = subprocess.run(
            ["git", "describe", "--always", "--dirty", "--tags"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=REPO_ROOT,
        )
        return completed.stdout.strip() if completed.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class RegressionPipeline:
    """Solver regression detection pipeline.

    Orchestrates loading a fixture corpus, batch-solving every scene,
    comparing results against a stored JSON baseline, and saving updated
    baselines.
    """

    def __init__(self) -> None:
        self._solver_command: list[str] | None = None

    # ------------------------------------------------------------------
    # Step 1 — load fixture corpus
    # ------------------------------------------------------------------

    @staticmethod
    def load_fixture_corpus(path: str) -> list[tuple[str, str]]:
        """Scan *path* for ``.txt`` / ``.json`` scene files.

        Returns:
            list of ``(scene_path, scene_id)`` where *scene_id* is the
            filename without its extension.
        """
        if not os.path.isdir(path):
            raise ValueError(f"Corpus path is not a directory: {path}")

        scenes: list[tuple[str, str]] = []
        for entry in sorted(os.listdir(path)):
            full = os.path.join(path, entry)
            if not os.path.isfile(full):
                continue
            if entry.endswith((".txt", ".json")):
                scene_id = os.path.splitext(entry)[0]
                scenes.append((full, scene_id))
        return scenes

    # ------------------------------------------------------------------
    # Step 2 — load baseline
    # ------------------------------------------------------------------

    @staticmethod
    def load_baseline(baseline_path: str) -> dict[str, Any]:
        """Load a JSON baseline file.

        Returns:
            dict with keys ``baseline_id``, ``created_at``,
            ``solver_version``, and ``results`` (dict of scene_id ->
            per-scene entry).
        """
        with open(baseline_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ------------------------------------------------------------------
    # Step 3 — solve corpus
    # ------------------------------------------------------------------

    def solve_corpus(
        self,
        scenes: list[tuple[str, str]],
        solver_command: list[str] | None = None,
        timeout: float = 30.0,
    ) -> list[SolveResult]:
        """Batch-solve all scenes, reusing ``run_single`` from
        :mod:`tools.solver_testing.runner`.

        Args:
            scenes: list of ``(scene_path, scene_id)`` tuples.
            solver_command: solver executable + args.  Auto-detected when
                *None*.
            timeout: per-scene timeout in seconds.
        """
        cmd = solver_command or self._solver_command or find_solver()
        if cmd is None:
            raise RuntimeError(
                "GCS solver not found. Set GCS_EXE or build the project."
            )
        self._solver_command = cmd

        results: list[SolveResult] = []
        total = len(scenes)
        for idx, (scene_path, scene_id) in enumerate(scenes):
            result = run_single(scene_path, scene_id, cmd, timeout)
            results.append(result)
            print(
                f"  [{idx + 1}/{total}] {scene_id}: {result.status} "
                f"({result.duration_ms}ms)"
            )
        return results

    # ------------------------------------------------------------------
    # Step 4 — compare results
    # ------------------------------------------------------------------

    @staticmethod
    def compare_results(
        current: list[SolveResult],
        baseline: dict[str, Any],
        tolerance: float = 1e-6,
    ) -> list[Regression]:
        """Compare the current solve results against a loaded baseline.

        Returns:
            list of :class:`Regression` objects, one per detected change.
            An empty list means no regressions.
        """
        baseline_results: dict[str, dict] = baseline.get("results", {})
        current_by_id: dict[str, SolveResult] = {r.scene_id: r for r in current}
        regressions: list[Regression] = []

        for scene_id, cur in current_by_id.items():
            bl = baseline_results.get(scene_id)

            # --- new scene (not in baseline) ---
            if bl is None:
                cur_numeric = _extract_numeric_fields(cur.stdout)
                regressions.append(Regression(
                    scene_id=scene_id,
                    baseline_status="(none)",
                    current_status=cur.status,
                    change_type="new_scene",
                    current_rank=cur_numeric["rank_estimate"],
                    current_residual=cur_numeric["residual_norm"],
                    detail="Scene not present in baseline",
                ))
                continue

            bl_status = bl.get("status", "unknown")
            bl_rank = bl.get("rank_estimate")
            bl_residual = bl.get("residual_norm")

            cur_numeric = _extract_numeric_fields(cur.stdout)
            cur_rank = cur_numeric["rank_estimate"]
            cur_residual = cur_numeric["residual_norm"]

            # --- status change ---
            if cur.status != bl_status:
                regressions.append(Regression(
                    scene_id=scene_id,
                    baseline_status=bl_status,
                    current_status=cur.status,
                    change_type="status_changed",
                    baseline_rank=bl_rank,
                    current_rank=cur_rank,
                    baseline_residual=bl_residual,
                    current_residual=cur_residual,
                    detail=f"Status changed: {bl_status} -> {cur.status}",
                ))
                continue  # skip rank/residual checks when status already changed

            # --- rank / residual: only meaningful when both solved ---
            if cur.status == "solved" and bl_status == "solved":
                if (bl_rank is not None and cur_rank is not None
                        and bl_rank != cur_rank):
                    regressions.append(Regression(
                        scene_id=scene_id,
                        baseline_status=bl_status,
                        current_status=cur.status,
                        change_type="rank_changed",
                        baseline_rank=bl_rank,
                        current_rank=cur_rank,
                        baseline_residual=bl_residual,
                        current_residual=cur_residual,
                        detail=f"Rank changed: {bl_rank} -> {cur_rank}",
                    ))

                if (bl_residual is not None and cur_residual is not None
                        and cur_residual > bl_residual + tolerance):
                    regressions.append(Regression(
                        scene_id=scene_id,
                        baseline_status=bl_status,
                        current_status=cur.status,
                        change_type="residual_grew",
                        baseline_rank=bl_rank,
                        current_rank=cur_rank,
                        baseline_residual=bl_residual,
                        current_residual=cur_residual,
                        detail=(
                            f"Residual grew: {bl_residual:.2e} -> "
                            f"{cur_residual:.2e} "
                            f"(delta={cur_residual - bl_residual:.2e})"
                        ),
                    ))

        return regressions

    # ------------------------------------------------------------------
    # Step 5 — save baseline
    # ------------------------------------------------------------------

    @staticmethod
    def save_baseline(results: list[SolveResult], path: str) -> None:
        """Save current results as a new baseline JSON file.

        The output matches the baseline format:
        ``{"baseline_id", "created_at", "solver_version", "results": {...}}``
        """
        results_dict: dict[str, dict] = {}
        for r in results:
            results_dict[r.scene_id] = _result_to_baseline_entry(r)

        baseline: dict[str, Any] = {
            "baseline_id": "v1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "solver_version": _git_describe(),
            "results": results_dict,
        }

        out_dir = os.path.dirname(path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2, sort_keys=True)

    # ------------------------------------------------------------------
    # Orchestrate
    # ------------------------------------------------------------------

    def run(
        self,
        corpus_path: str,
        baseline_path: str | None = None,
        tolerance: float = 1e-6,
        solver_command: list[str] | None = None,
    ) -> dict[str, Any]:
        """Orchestrate the full regression pipeline.

        1. Load fixture corpus.
        2. Batch-solve every scene.
        3. Compare against baseline (when *baseline_path* exists).
        4. Save current results as the new baseline.

        Args:
            corpus_path: directory containing ``.txt`` / ``.json`` scenes.
            baseline_path: path to the baseline JSON.  Read for
                comparison if it exists; new baseline is always written
                here.  Defaults to ``<corpus_path>/baseline.json``.
            tolerance: numeric tolerance for residual comparison.
            solver_command: solver executable command (auto-detected if
                omitted).

        Returns:
            A summary dict with keys ``scenes_tested``,
            ``regressions_found``, ``regressions``, ``results``.
        """
        print("=" * 60)
        print("SOLVER REGRESSION PIPELINE")
        print("=" * 60)

        # Resolve baseline path
        bp = baseline_path or os.path.join(corpus_path, "baseline.json")

        # 1 — Load corpus
        print(f"\n[1/4] Loading fixture corpus from: {corpus_path}")
        scenes = self.load_fixture_corpus(corpus_path)
        print(f"  Found {len(scenes)} scenes")
        if not scenes:
            print("  WARNING: No scene files found.")
            return {
                "scenes_tested": 0,
                "regressions_found": 0,
                "regressions": [],
                "results": [],
            }

        # 2 — Solve
        timeout_s = float(os.environ.get("GCS_SOLVE_TIMEOUT", "30"))
        print(f"\n[2/4] Solving {len(scenes)} scenes (timeout={timeout_s}s)...")
        results = self.solve_corpus(scenes, solver_command, timeout_s)
        solved = sum(1 for r in results if r.status == "solved")
        print(f"  Solved: {solved}/{len(results)}")

        # 3 — Compare
        regressions: list[Regression] = []
        if os.path.exists(bp):
            print(f"\n[3/4] Comparing against baseline: {bp}")
            baseline = self.load_baseline(bp)
            print(
                f"  Baseline: {baseline.get('baseline_id', '?')} "
                f"({baseline.get('solver_version', '?')}), "
                f"{len(baseline.get('results', {}))} entries"
            )
            regressions = self.compare_results(results, baseline, tolerance)
            print(f"  Regressions detected: {len(regressions)}")
            for reg in regressions:
                print(f"    [{reg.change_type}] {reg.scene_id}: {reg.detail}")
        else:
            print(f"\n[3/4] No baseline at '{bp}' — skipping comparison")

        # 4 — Save baseline
        print(f"\n[4/4] Saving baseline to: {bp}")
        self.save_baseline(results, bp)
        print(f"  Saved {len(results)} entries")

        # Summary
        print("\n" + "=" * 60)
        print("PIPELINE SUMMARY")
        print("=" * 60)
        print(f"Scenes tested:     {len(results)}")
        print(f"Solved:            {solved}/{len(results)}")
        print(f"Regressions found: {len(regressions)}")
        if regressions:
            by_type: dict[str, int] = {}
            for r in regressions:
                by_type[r.change_type] = by_type.get(r.change_type, 0) + 1
            print("By change type:")
            for ct, count in sorted(by_type.items()):
                print(f"  {ct}: {count}")
        print()

        return {
            "scenes_tested": len(results),
            "regressions_found": len(regressions),
            "regressions": regressions,
            "results": results,
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point for the regression pipeline.

    Example::

        python tools/solver_testing/pipelines/regression.py \\
            --corpus fixtures/scene/basic \\
            --baseline fixtures/scene/basic/baseline.json \\
            --tolerance 1e-6
    """
    parser = argparse.ArgumentParser(
        description="Solver Regression Pipeline — detect regressions "
                    "in solver output across a fixture corpus.",
    )
    parser.add_argument(
        "--corpus", required=True,
        help="Path to fixture corpus directory (.txt / .json scene files).",
    )
    parser.add_argument(
        "--baseline",
        help="Path to baseline JSON file.  Read for comparison if it "
             "exists; always written with current results.  "
             "Defaults to <corpus>/baseline.json.",
    )
    parser.add_argument(
        "--tolerance", type=float, default=1e-6,
        help="Numeric tolerance for residual comparison (default: 1e-6).",
    )
    parser.add_argument(
        "--solver",
        help="Path to GCS solver executable (auto-detected if omitted).",
    )
    parser.add_argument(
        "--timeout", type=float, default=30.0,
        help="Per-scene solve timeout in seconds (default: 30).",
    )
    args = parser.parse_args()

    solver_command = None
    if args.solver:
        solver_command = [os.path.abspath(args.solver)]

    if "GCS_SOLVE_TIMEOUT" not in os.environ:
        os.environ["GCS_SOLVE_TIMEOUT"] = str(args.timeout)

    pipeline = RegressionPipeline()
    summary = pipeline.run(
        corpus_path=os.path.abspath(args.corpus),
        baseline_path=os.path.abspath(args.baseline) if args.baseline else None,
        tolerance=args.tolerance,
        solver_command=solver_command,
    )

    if summary["regressions_found"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
