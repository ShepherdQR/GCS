#!/usr/bin/env python3
"""Scene Generation Pipeline — orchestrates exploration and enumeration for
coverage-driven scene generation.

Exploration (sampling) and enumeration (exhaustive) strategies are run against
a coverage specification.  The pipeline compares results against targets and
reports gaps so subsequent runs can be directed at under-covered categories.

Usage:
  python tools/solver_testing/pipelines/scene_gen.py --coverage coverage_targets.json --budget max_candidates=500
  python tools/solver_testing/pipelines/scene_gen.py --coverage targets.json --strategies explore,enumerate --output report.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(TOOL_DIR, "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.scene_generation.gcs_scene_generation.contracts import (
    CONSTRAINT_TYPES,
    GEOMETRY_TYPES,
)
from tools.scene_generation.gcs_scene_generation.enumerator import (
    EnumeratorServices,
    enumerate_scene_space,
)
from tools.scene_generation.gcs_scene_generation.explorer import (
    ExplorerServices,
    explore_scene_space,
)
from tools.scene_generation.gcs_scene_generation.storage import SceneGenerationStore
from tools.scene_generation.tools import (
    tool_assign_geometry_parameters,
    tool_check_vertex_biconnected,
    tool_generate_graph_report,
    tool_generate_skeleton_graph,
    tool_lift_skeleton_to_gcs,
    tool_project_gcs_graph,
    tool_serialize_gcs_graph,
    tool_validate_gcs_schema,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_STORE_DIR = os.environ.get(
    "GCS_SCENE_GENERATION_STORE_DIR",
    os.path.join(REPO_ROOT, "tools", "scene_generation", ".store"),
)

# Smallest vertex count that can be vertex-biconnected.
MIN_BICONNECTED_VERTICES = 3
# Reasonable enumeration ceiling — exhaustive search explodes above this.
MAX_ENUM_GEOMETRIES = 8


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class CoverageSpec:
    """Parsed coverage targets specifying how many scenes of each category
    the pipeline should attempt to generate."""

    geometry_types: dict[str, int] = field(default_factory=dict)
    constraint_types: dict[str, int] = field(default_factory=dict)
    rigid_set_counts: dict[str, int] = field(default_factory=dict)
    topology: dict[str, int] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return not any(
            [
                self.geometry_types,
                self.constraint_types,
                self.rigid_set_counts,
                self.topology,
            ]
        )


@dataclass
class Gap:
    """A single coverage gap — a target not yet met by generated output."""

    category: str
    target_count: int
    current_count: int

    @property
    def missing(self) -> int:
        return max(0, self.target_count - self.current_count)


@dataclass
class SceneGenReport:
    """Aggregate result from a scene-generation pipeline run."""

    exploration_results: dict | None = None
    enumeration_results: list[dict] | None = None
    gaps: list[Gap] = field(default_factory=list)

    @property
    def all_gaps_satisfied(self) -> bool:
        return all(g.missing <= 0 for g in self.gaps)

    def summary(self) -> str:
        return self.gap_summary()

    def gap_summary(self) -> str:
        lines = ["COVERAGE GAPS"]
        if not self.gaps:
            lines.append("  (no targets defined)")
            return "\n".join(lines)
        for g in self.gaps:
            flag = "  OK" if g.missing <= 0 else "MISS"
            lines.append(
                f"  {flag}  {g.category:50s}  target={g.target_count:>5d}  current={g.current_count:>5d}  missing={g.missing:>5d}"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# SceneGenPipeline
# ---------------------------------------------------------------------------


class SceneGenPipeline:
    """Orchestrates scene-generation exploration and enumeration strategies.

    Reuses existing tool functions from ``tools.scene_generation`` via direct
    Python imports — no subprocess calls.
    """

    def __init__(self, store_dir: str | None = None):
        self._store = SceneGenerationStore(store_dir or DEFAULT_STORE_DIR)

    # ------------------------------------------------------------------
    # Service construction
    # ------------------------------------------------------------------

    def _make_explorer_services(self) -> ExplorerServices:
        """Build an ExplorerServices wired to the local store and tool functions."""
        store = self._store
        return ExplorerServices(
            store=store,
            generate_skeleton_graph=tool_generate_skeleton_graph,
            lift_skeleton_to_gcs=tool_lift_skeleton_to_gcs,
            assign_geometry_parameters=tool_assign_geometry_parameters,
            validate_gcs_schema=tool_validate_gcs_schema,
            project_gcs_graph=tool_project_gcs_graph,
            check_vertex_biconnected=tool_check_vertex_biconnected,
            generate_graph_report=tool_generate_graph_report,
            serialize_gcs_graph=tool_serialize_gcs_graph,
            load_graph=store.load_graph,
            save_graph=store.save_graph,
            # Promotion and public gates are deferred to explicit promote
            # commands; the pipeline focuses on generation coverage.
            promote_candidate=None,
            public_adapter_gates=None,
        )

    def _make_enumerator_services(self) -> EnumeratorServices:
        """Build an EnumeratorServices wired to the local store."""
        return EnumeratorServices(
            store=self._store,
            save_graph=self._store.save_graph,
            load_graph=self._store.load_graph,
        )

    # ------------------------------------------------------------------
    # 1. define_coverage_targets
    # ------------------------------------------------------------------

    @staticmethod
    def define_coverage_targets(spec: dict) -> CoverageSpec:
        """Parse a coverage specification dict into a ``CoverageSpec``.

        Expected format::

            {
              "geometry_types":   {"Point": 10, "Line": 10, "Plane": 10},
              "constraint_types": {"Distance": 15, "Coincident": 10, ...},
              "rigid_set_counts": {"2": 20, "3": 15},
              "topology":         {"biconnected": 30, "connected": 10}
            }
        """
        return CoverageSpec(
            geometry_types=_normalize_count_dict(spec.get("geometry_types", {})),
            constraint_types=_normalize_count_dict(spec.get("constraint_types", {})),
            rigid_set_counts=_normalize_count_dict(spec.get("rigid_set_counts", {})),
            topology=_normalize_count_dict(spec.get("topology", {})),
        )

    # ------------------------------------------------------------------
    # 2. run_exploration
    # ------------------------------------------------------------------

    def run_exploration(self, spec: CoverageSpec, budget: dict) -> dict:
        """Run a single exploration (sampling) pass.

        Derives exploration parameters from *spec* and *budget*, then calls
        ``explore_scene_space``.  Returns the result dict written by the
        explorer.
        """
        params = _exploration_params(spec, budget)
        return explore_scene_space(params, self._make_explorer_services())

    # ------------------------------------------------------------------
    # 3. run_enumeration
    # ------------------------------------------------------------------

    def run_enumeration(self, spec: CoverageSpec, budget: dict) -> list[dict]:
        """Run enumeration (exhaustive) passes over small parameter spaces.

        Iterates over (num_geometries, num_constraints, num_rigid_sets)
        combinations derived from *spec*.  Each combination is enumerated
        independently via ``enumerate_scene_space``.

        Returns a list of result dicts, one per enumerated parameter set.
        """
        results: list[dict] = []

        rigid_set_counts = _rigid_set_range(spec)
        geometry_types = list(spec.geometry_types) if spec.geometry_types else list(GEOMETRY_TYPES)
        constraint_types_list = list(spec.constraint_types) if spec.constraint_types else list(CONSTRAINT_TYPES)

        max_graphs = int(budget.get("max_candidates", 500))
        max_seconds = float(budget.get("max_seconds", 0.0))
        seed = int(budget.get("seed", 0))
        require_biconnected = _biconnected_requested(spec)

        total_accepted = 0
        stopped = False

        for num_geometries in range(MIN_BICONNECTED_VERTICES, MAX_ENUM_GEOMETRIES + 1):
            if stopped:
                break
            for num_rigid_sets in rigid_set_counts:
                if stopped:
                    break
                if num_rigid_sets >= num_geometries:
                    # Must have at least one edge crossing rigid sets per
                    # constraint; skip configurations that cannot produce
                    # cross-rigid-set edges.
                    continue

                # Enumerate every reachable constraint count for this pair.
                min_constraints = max(MIN_BICONNECTED_VERTICES, num_rigid_sets)
                max_constraints = min(num_geometries, num_geometries * (num_geometries - 1) // 2)
                for num_constraints in range(min_constraints, max_constraints + 1):
                    if stopped:
                        break

                    remaining_budget = max_graphs - total_accepted if max_graphs > 0 else None
                    if remaining_budget is not None and remaining_budget <= 0:
                        stopped = True
                        break

                    params = {
                        "enumeration_id": f"scene_gen_enum_{num_geometries}g_{num_constraints}c_{num_rigid_sets}rs",
                        "num_geometries": num_geometries,
                        "num_constraints": num_constraints,
                        "num_rigid_sets": num_rigid_sets,
                        "geometry_types": geometry_types,
                        "constraint_types": constraint_types_list,
                        "seed": seed + num_geometries * 100 + num_constraints,
                        "max_graphs": remaining_budget,
                        "max_seconds": max_seconds,
                        "require_biconnected": require_biconnected,
                    }
                    result = enumerate_scene_space(params, self._make_enumerator_services())
                    results.append(result)
                    total_accepted += len(result.get("graph_ids", []))

        return results

    # ------------------------------------------------------------------
    # 4. coverage_gap_analysis
    # ------------------------------------------------------------------

    @staticmethod
    def coverage_gap_analysis(
        current_results: dict,
        targets: CoverageSpec,
    ) -> list[Gap]:
        """Compare generated output against targets and return a list of ``Gap`` objects.

        *current_results* is a dict with optional keys ``"exploration"`` and
        ``"enumeration"`` holding the raw outputs of the respective strategies.
        """
        gaps: list[Gap] = []

        # --- accumulate current counts ---
        current_geometry: Counter[str] = Counter()
        current_constraint: Counter[str] = Counter()
        current_rigid_sets: Counter[str] = Counter()
        current_biconnected = 0

        # Exploration contribution
        explore: dict | None = current_results.get("exploration")
        if explore:
            histograms = explore.get("coverage", {}).get("histograms", {})
            for gtype, count in histograms.get("geometry_types", {}).items():
                current_geometry[gtype] += count
            for ctype, count in histograms.get("constraint_types", {}).items():
                current_constraint[ctype] += count
            for rs, count in histograms.get("rigid_set_counts", {}).items():
                current_rigid_sets[rs] += count
            current_biconnected += len(explore.get("accepted_candidates", []))

        # Enumeration contribution
        enum_list: list[dict] = current_results.get("enumeration") or []
        for enum_result in enum_list:
            graphs = enum_result.get("graphs", [])
            for graph in graphs:
                for gtype, count in graph.get("geometry_types", {}).items():
                    current_geometry[gtype] += count
                for ctype, count in graph.get("constraint_types", {}).items():
                    current_constraint[ctype] += count
                current_rigid_sets[str(graph.get("num_rigid_sets", 0))] += 1
            current_biconnected += len(graphs)

        # --- typed-target categories ---
        for category_name, targets_dict, current_counter in [
            ("geometry_types", targets.geometry_types, current_geometry),
            ("constraint_types", targets.constraint_types, current_constraint),
            ("rigid_set_counts", targets.rigid_set_counts, current_rigid_sets),
        ]:
            for key, target in sorted(targets_dict.items()):
                current = current_counter.get(key, 0)
                gaps.append(
                    Gap(
                        category=f"{category_name}:{key}",
                        target_count=target,
                        current_count=current,
                    )
                )

        # --- topology targets ---
        for topo_key, target in sorted(targets.topology.items()):
            current = 0
            if topo_key == "biconnected":
                current = current_biconnected
            elif topo_key == "connected":
                # "connected" is a superset — enumerate tracks biconnected
                # which implies connected.  We report the same count.
                current = current_biconnected
            gaps.append(
                Gap(
                    category=f"topology:{topo_key}",
                    target_count=target,
                    current_count=current,
                )
            )

        return gaps

    # ------------------------------------------------------------------
    # 5. run
    # ------------------------------------------------------------------

    def run(
        self,
        spec: dict,
        budget: dict | None = None,
        strategies: list[str] | None = None,
    ) -> SceneGenReport:
        """Execute the full pipeline: parse targets, run strategies, analyze gaps.

        Args:
            spec: Coverage specification dict (see ``define_coverage_targets``).
            budget: Optional budget dict with keys like ``max_candidates``,
                    ``max_accepts``, ``max_seconds``, ``seed``.
            strategies: List of strategy names to execute.  Defaults to
                        ``["explore", "enumerate"]``.

        Returns:
            A ``SceneGenReport`` with results from each strategy and the gap list.
        """
        budget = dict(budget or {})
        strategies = list(strategies or ["explore", "enumerate"])

        targets = self.define_coverage_targets(spec)

        exploration_results = None
        enumeration_results = None

        if "explore" in strategies:
            exploration_results = self.run_exploration(targets, budget)

        if "enumerate" in strategies:
            enumeration_results = self.run_enumeration(targets, budget)

        current = {
            "exploration": exploration_results,
            "enumeration": enumeration_results,
        }
        gaps = self.coverage_gap_analysis(current, targets)

        return SceneGenReport(
            exploration_results=exploration_results,
            enumeration_results=enumeration_results,
            gaps=gaps,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _normalize_count_dict(raw: dict) -> dict[str, int]:
    """Convert all values in *raw* to ints, dropping non-positive entries."""
    result: dict[str, int] = {}
    for key, value in raw.items():
        try:
            v = int(value)
        except (TypeError, ValueError):
            continue
        if v > 0:
            result[str(key)] = v
    return result


def _rigid_set_range(spec: CoverageSpec) -> list[int]:
    """Return the list of rigid-set counts to enumerate from *spec*."""
    if spec.rigid_set_counts:
        return sorted({int(k) for k in spec.rigid_set_counts})
    return [2, 3]


def _biconnected_requested(spec: CoverageSpec) -> bool:
    """Return True when biconnected topology is the primary target."""
    topo = spec.topology
    biconnected = topo.get("biconnected", 0)
    connected = topo.get("connected", 0)
    # If only "connected" is set (and biconnected is 0), we can relax.
    if connected > 0 and biconnected == 0:
        return False
    return True


def _exploration_params(spec: CoverageSpec, budget: dict) -> dict:
    """Build the params dict for ``explore_scene_space`` from *spec* and *budget*."""
    exploration_id = budget.get("exploration_id", "scene_gen_explore")
    seed = int(budget.get("seed", 0))

    # Geometry types: use spec keys, fall back to all known types.
    geom_types = list(spec.geometry_types) if spec.geometry_types else list(GEOMETRY_TYPES)
    constraint_types = list(spec.constraint_types) if spec.constraint_types else list(CONSTRAINT_TYPES)
    rigid_set_counts = _rigid_set_range(spec)

    # Coverage goals derived from what the spec targets.
    coverage_goals: list[str] = []
    if spec.geometry_types:
        coverage_goals.append("all_geometry_types")
    if spec.constraint_types:
        coverage_goals.append("all_constraint_types")
    if spec.rigid_set_counts:
        coverage_goals.append("mixed_rigid_sets")
    if spec.topology.get("biconnected", 0) > 0:
        coverage_goals.append("biconnected_geometry_primal")
    if not coverage_goals:
        coverage_goals = [
            "all_geometry_types",
            "all_constraint_types",
            "mixed_rigid_sets",
            "biconnected_geometry_primal",
            "invalid_signature_negative_case",
            "same_rigid_set_negative_case",
        ]

    return {
        "exploration_id": exploration_id,
        "seed": seed,
        "budget": {
            "max_candidates": int(budget.get("max_candidates", 500)),
            "max_accepts": int(budget.get("max_accepts", 50)),
            "max_seconds": float(budget.get("max_seconds", 0.0)),
        },
        "topology_policy": {
            "vertex_counts": [3, 4, 5, 6, 7, 8],
            "methods": ["cycle_plus_chords", "ear_decomposition"],
            "extra_edge_values": [0, 1, 2, 3],
            "require_vertex_biconnected": True,
        },
        "gcs_policy": {
            "geometry_types": geom_types,
            "constraint_types": constraint_types,
            "rigid_set_counts": rigid_set_counts,
            "require_cross_rigid_set_constraints": True,
        },
        "parameter_policy": {
            "layouts": ["circular", "grid", "random"],
            "avoid_degenerate_geometry": True,
            "value_tolerance": 1e-9,
        },
        "coverage_goals": coverage_goals,
        "gate_profile": "local_only",
        "write_policy": {
            "store": "scratch",
            "keep_rejected": True,
            "promote": False,
        },
        "allow_unsupported_gates": False,
    }


# ---------------------------------------------------------------------------
# Budget string parsing
# ---------------------------------------------------------------------------


def parse_budget(budget_str: str) -> dict:
    """Parse a comma-separated ``key=value`` budget string into a dict.

    Example: ``"max_candidates=500,max_accepts=50,seed=42"``
    """
    budget: dict = {}
    for part in budget_str.split(","):
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            budget[key.strip()] = value.strip()
    return budget


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scene Generation Pipeline — coverage-driven exploration and enumeration.",
    )
    parser.add_argument(
        "--coverage",
        required=True,
        help="Path to a coverage-targets JSON file.",
    )
    parser.add_argument(
        "--budget",
        default="max_candidates=500",
        help=(
            "Budget string: comma-separated key=value pairs.  "
            "Supported keys: max_candidates, max_accepts, max_seconds, seed, exploration_id."
        ),
    )
    parser.add_argument(
        "--strategies",
        default="explore,enumerate",
        help="Comma-separated strategy names: explore, enumerate (default: both).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write the JSON report to this file instead of stdout.",
    )
    parser.add_argument(
        "--gap-only",
        action="store_true",
        help="Print only the gap analysis summary to stdout.",
    )
    args = parser.parse_args()

    # --- load coverage spec ---
    coverage_path = os.path.abspath(args.coverage)
    if not os.path.exists(coverage_path):
        print(f"ERROR: coverage file not found: {coverage_path}", file=sys.stderr)
        sys.exit(1)
    with open(coverage_path, "r", encoding="utf-8") as fh:
        spec = json.load(fh)

    # --- parse budget ---
    budget = parse_budget(args.budget)

    # --- parse strategies ---
    strategies = [s.strip() for s in args.strategies.split(",") if s.strip()]
    valid_strategies = {"explore", "enumerate"}
    unknown = [s for s in strategies if s not in valid_strategies]
    if unknown:
        print(f"ERROR: unknown strategies: {unknown}. Valid: {sorted(valid_strategies)}", file=sys.stderr)
        sys.exit(2)

    # --- run ---
    pipeline = SceneGenPipeline()
    report = pipeline.run(spec, budget, strategies)

    # --- output ---
    output_data = {
        "exploration_results": report.exploration_results,
        "enumeration_results": report.enumeration_results,
        "gaps": [
            {
                "category": g.category,
                "target_count": g.target_count,
                "current_count": g.current_count,
                "missing": g.missing,
            }
            for g in report.gaps
        ],
    }

    if args.output:
        output_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(output_data, fh, indent=2, sort_keys=True, default=str)
        print(f"Report saved to: {output_path}")

    if args.gap_only:
        print(report.gap_summary())
    elif not args.output:
        print(json.dumps(output_data, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
