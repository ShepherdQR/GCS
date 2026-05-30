"""Defect discovery pipeline — unified entry point wrapping enumeration, mutation,
solver execution, defect classification, and analysis into a single runnable pipeline.

Importable as::

    from tools.solver_testing.pipelines.defect_discovery import DefectDiscoveryPipeline

    pipeline = DefectDiscoveryPipeline.from_preset("standard", enumeration_id="my_run")
    result = pipeline.run()
    print(f"Found {result.stats['defects_found']} defects")
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any

# Ensure repo root is on sys.path so that tools.* imports resolve.
_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tools.scene_generation.gcs_scene_generation.enumerator import (
    EnumeratorServices,
    enumerate_scene_space,
)
from tools.scene_generation.gcs_scene_generation.promotion import (
    solver_scene_from_gcs,
)
from tools.scene_generation.gcs_scene_generation.storage import SceneGenerationStore
from tools.solver_testing.analyzer import analyze_and_repair_defects
from tools.solver_testing.defect_store import (
    DefectRecord,
    DefectStore,
    classify_defect,
    make_defect_id,
)
from tools.solver_testing.mutator import MUTATION_STRATEGIES, mutate_constraint_values
from tools.solver_testing.runner import find_solver, run_single

# ---------------------------------------------------------------------------
# Preset definitions
# ---------------------------------------------------------------------------

_PRESET_NAMES = ("smoke", "standard", "full")

_PRESETS: dict[str, dict[str, Any]] = {
    "smoke": {
        "enumeration": {
            "num_geometries": 3,
            "num_constraints": 3,
            "num_rigid_sets": 2,
            "require_biconnected": True,
            "max_graphs": 1,
            "max_seconds": 120.0,
        },
        "mutation": {
            "strategies": ["positive_to_negative", "zero_to_nonzero"],
        },
        "solver": {
            "timeout_seconds": 15.0,
        },
        "run_analysis": False,
    },
    "standard": {
        "enumeration": {
            "num_geometries": 5,
            "num_constraints": 5,
            "num_rigid_sets": 2,
            "require_biconnected": True,
            "max_graphs": 10,
            "max_seconds": 300.0,
        },
        "mutation": {
            "strategies": [
                "positive_to_negative",
                "zero_to_nonzero",
                "angle_out_of_range",
            ],
        },
        "solver": {
            "timeout_seconds": 30.0,
        },
        "run_analysis": True,
    },
    "full": {
        "enumeration": {
            "num_geometries": 5,
            "num_constraints": 5,
            "num_rigid_sets": 3,
            "require_biconnected": True,
            "max_graphs": 100,
            "max_seconds": 1800.0,
        },
        "mutation": {
            "strategies": list(MUTATION_STRATEGIES),
        },
        "solver": {
            "timeout_seconds": 60.0,
        },
        "run_analysis": True,
    },
}

_DEFAULT_STORE_DIR = os.path.join(
    _REPO_ROOT, "tools", "scene_generation", ".store"
)
_DEFAULT_TASK_CARD_DIR = os.path.join(_REPO_ROOT, "docs", "agentic", "tasks")


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class PipelineResult:
    """Structured result from a DefectDiscoveryPipeline run."""

    enumeration_result: dict | None
    """Raw dict returned by :func:`enumerate_scene_space`."""

    defects_found: list[DefectRecord]
    """Every defect record produced during the run."""

    analysis_result: dict | None
    """Output of :func:`analyze_and_repair_defects`, or *None* when skipped."""

    task_card_path: str
    """Absolute path to the generated task-card Markdown file."""

    stats: dict = field(default_factory=dict)
    """Counters: graphs_enumerated, graphs_tested, mutations_generated,
    solves_run, defects_found, original_failures."""

    defect_store_summary: dict = field(default_factory=dict)
    """Summary dict from :meth:`DefectStore.summary` at pipeline completion."""


# ---------------------------------------------------------------------------
# Pipeline class
# ---------------------------------------------------------------------------


class DefectDiscoveryPipeline:
    """Unified defect discovery pipeline.

    Orchestrates four stages:

    1. **Enumerate** — exhaustively (or up to a limit) enumerate valid
       constraint graphs for the requested parameter space.
    2. **Mutate + Solve** — for each graph, run the original through the
       solver, then apply mutation strategies and re-solve.
    3. **Classify + Store** — compare original-vs-mutated results, classify
       each detected defect, and persist to the defect store.
    4. **Analyze** (optional) — run the auto-fix / repair pipeline over
       collected defects.

    Basic usage::

        pipeline = DefectDiscoveryPipeline.from_preset(
            "standard", enumeration_id="defect_2rs_5g_5c"
        )
        result = pipeline.run()

    Custom parameters::

        pipeline = DefectDiscoveryPipeline(
            enumeration_params={"num_geometries": 4, "num_constraints": 4,
                                "num_rigid_sets": 2, "max_graphs": 50},
            mutation_params={"strategies": ["positive_to_negative",
                                            "angle_out_of_range"]},
            solver_params={"timeout_seconds": 20.0},
            enumeration_id="custom_run",
            run_analysis=True,
        )
        result = pipeline.run()
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        enumeration_params: dict[str, Any] | None = None,
        mutation_params: dict[str, Any] | None = None,
        solver_params: dict[str, Any] | None = None,
        *,
        enumeration_id: str = "",
        run_analysis: bool = True,
        store_dir: str | None = None,
        defects_dir: str | None = None,
        task_card_dir: str | None = None,
    ):
        self.enumeration_params = dict(enumeration_params or {})
        self.mutation_params = dict(mutation_params or {})
        self.solver_params = dict(solver_params or {})
        self.enumeration_id = enumeration_id or _default_enumeration_id()
        self.run_analysis_flag = run_analysis
        self.store_dir = store_dir or os.environ.get(
            "GCS_SCENE_GENERATION_STORE_DIR", _DEFAULT_STORE_DIR
        )
        self.task_card_dir = task_card_dir or _DEFAULT_TASK_CARD_DIR
        self._preset_name: str | None = None  # set by from_preset()

        # Ensure enumeration_id propagates into enumeration params
        self.enumeration_params.setdefault("enumeration_id", self.enumeration_id)

        self._store = SceneGenerationStore(self.store_dir)
        self._defect_store = DefectStore(defects_dir)

    @classmethod
    def from_preset(
        cls,
        preset: str,
        enumeration_id: str = "",
        **overrides: Any,
    ) -> "DefectDiscoveryPipeline":
        """Create a pipeline from a named preset.

        Valid presets: ``"smoke"``, ``"standard"``, ``"full"``.

        Individual parameters can be overridden via dotted keys::

            DefectDiscoveryPipeline.from_preset(
                "standard",
                enumeration_id="my_run",
                enumeration__max_graphs=20,
                solver__timeout_seconds=45.0,
            )
        """
        if preset not in _PRESETS:
            raise ValueError(
                f"Unknown preset {preset!r}. Available: {list(_PRESETS)}"
            )

        config = _PRESETS[preset]
        enum_params = dict(config.get("enumeration", {}))
        mut_params = dict(config.get("mutation", {}))
        solv_params = dict(config.get("solver", {}))
        run_analysis = config.get("run_analysis", True)

        # Pull top-level overrides out
        resolved_enumeration_id = enumeration_id
        resolved_store_dir: str | None = overrides.pop("store_dir", None)
        resolved_defects_dir: str | None = overrides.pop("defects_dir", None)
        resolved_task_card_dir: str | None = overrides.pop("task_card_dir", None)

        for key, value in overrides.items():
            if key == "run_analysis":
                run_analysis = bool(value)
            elif key.startswith("enumeration__"):
                enum_params[key.split("__", 1)[1]] = value
            elif key.startswith("mutation__"):
                mut_params[key.split("__", 1)[1]] = value
            elif key.startswith("solver__"):
                solv_params[key.split("__", 1)[1]] = value
            else:
                raise ValueError(
                    f"Unknown override key {key!r}. "
                    f"Use 'enumeration__<param>', 'mutation__<param>', "
                    f"'solver__<param>', or 'run_analysis'."
                )

        instance = cls(
            enumeration_params=enum_params,
            mutation_params=mut_params,
            solver_params=solv_params,
            enumeration_id=resolved_enumeration_id,
            run_analysis=run_analysis,
            store_dir=resolved_store_dir,
            defects_dir=resolved_defects_dir,
            task_card_dir=resolved_task_card_dir,
        )
        instance._preset_name = preset
        return instance

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self) -> PipelineResult:
        """Execute the full pipeline and return a structured result.

        The pipeline is idempotent with respect to enumeration: if an
        enumeration result already exists for *enumeration_id* it is reused
        rather than recomputed.
        """
        stats: dict[str, int] = {
            "graphs_enumerated": 0,
            "graphs_tested": 0,
            "mutations_generated": 0,
            "solves_run": 0,
            "defects_found": 0,
            "original_failures": 0,
        }
        all_defects: list[DefectRecord] = []

        # ---- 1. Enumerate --------------------------------------------------
        print(f"[pipeline] Enumerating scene space: {self.enumeration_id}")
        enum_result = self._run_enumeration()
        graph_ids: list[str] = enum_result.get("graph_ids", [])
        stats["graphs_enumerated"] = len(graph_ids)
        print(f"[pipeline] Enumeration complete: {len(graph_ids)} graphs")

        if not graph_ids:
            print("[pipeline] No graphs enumerated — nothing to test.")
            return PipelineResult(
                enumeration_result=enum_result,
                defects_found=[],
                analysis_result=None,
                task_card_path=self._write_task_card(stats, [], None),
                stats=stats,
                defect_store_summary=self._defect_store.summary(),
            )

        # ---- 2. Locate solver ----------------------------------------------
        solver_command = find_solver(self.solver_params.get("solver_path"))
        if solver_command is None:
            raise RuntimeError(
                "GCS solver not found. Set GCS_EXE environment variable "
                "or build the project."
            )
        timeout = float(self.solver_params.get("timeout_seconds", 30.0))
        seed = int(self.mutation_params.get("seed", 42))

        strategies = self.mutation_params.get("strategies")
        if strategies is None:
            strategies = list(MUTATION_STRATEGIES)
        elif isinstance(strategies, str):
            strategies = [s.strip() for s in strategies.split(",")]

        # Validate strategies
        unknown = [s for s in strategies if s not in MUTATION_STRATEGIES]
        if unknown:
            raise ValueError(
                f"Unknown mutation strategies: {unknown}. "
                f"Available: {list(MUTATION_STRATEGIES)}"
            )

        print(f"[pipeline] Solver:  {solver_command[0]}")
        print(f"[pipeline] Timeout: {timeout}s")
        print(f"[pipeline] Strategies: {strategies}")
        print()

        # ---- 3. Mutate + Solve + Classify ----------------------------------
        for graph_id in graph_ids:
            try:
                gcs = self._store.load_graph(graph_id)
            except FileNotFoundError:
                print(f"  SKIP {graph_id}: not found in store")
                continue

            stats["graphs_tested"] += 1

            # 3a. Solve the original (un-mutated) scene
            public_scene = solver_scene_from_gcs(gcs)
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".gcs.json", delete=False
            ) as f:
                json.dump(public_scene, f)
                orig_scene_path = f.name

            orig_result = run_single(
                orig_scene_path, graph_id, solver_command, timeout
            )
            try:
                os.unlink(orig_scene_path)
            except OSError:
                pass

            if orig_result.status != "solved":
                stats["original_failures"] += 1
                print(
                    f"  {graph_id}: original solve FAILED "
                    f"({orig_result.status}) — skipping mutations"
                )
                continue

            # 3b. Generate mutations
            mutated = mutate_constraint_values(
                gcs, strategies, seed + len(all_defects)
            )
            stats["mutations_generated"] += len(mutated)

            # 3c. Run solver on each mutated scene
            for mut_idx, (mut_gcs, mutation_list) in enumerate(mutated):
                mut_scene = solver_scene_from_gcs(mut_gcs)
                mut_id = f"{graph_id}_m{mut_idx:03d}"
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".gcs.json", delete=False
                ) as f:
                    json.dump(mut_scene, f)
                    mut_scene_path = f.name

                mut_result = run_single(
                    mut_scene_path, mut_id, solver_command, timeout
                )
                stats["solves_run"] += 1
                try:
                    os.unlink(mut_scene_path)
                except OSError:
                    pass

                severity, error_type = classify_defect(orig_result, mut_result)
                if severity == "unknown":
                    continue  # no defect detected for this mutation

                stats["defects_found"] += 1
                defect_id = make_defect_id(
                    self.enumeration_id, graph_id, mut_idx
                )

                orig_values = {
                    str(c["id"]): float(c.get("value", 0.0))
                    for c in gcs.get("constraints", [])
                }
                mut_values = {
                    str(c["id"]): float(c.get("value", 0.0))
                    for c in mut_gcs.get("constraints", [])
                }

                record = DefectRecord(
                    defect_id=defect_id,
                    scene_id=graph_id,
                    original_values=orig_values,
                    mutated_values=mut_values,
                    mutation_strategies=[
                        m.strategy for m in mutation_list
                    ],
                    original_result={
                        "exit_code": orig_result.exit_code,
                        "status": orig_result.status,
                        "stderr": orig_result.stderr[:500],
                        "diagnostics_present": orig_result.diagnostics_present,
                    },
                    mutated_result={
                        "exit_code": mut_result.exit_code,
                        "status": mut_result.status,
                        "stderr": mut_result.stderr[:500],
                        "diagnostics_present": mut_result.diagnostics_present,
                    },
                    error_type=error_type,
                    severity=severity,
                    enumeration_id=self.enumeration_id,
                    created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
                )
                self._defect_store.save(record)
                all_defects.append(record)
                print(
                    f"  DEFECT {defect_id}: {error_type} [{severity}] "
                    f"— {mutation_list[0].strategy} on "
                    f"c{mutation_list[0].constraint_id}"
                )

        # ---- 4. Analyze + Repair (optional) ---------------------------------
        analysis_result: dict | None = None
        if self.run_analysis_flag and all_defects:
            print()
            print("[pipeline] Running defect analysis and auto-repair …")
            analysis_result = analyze_and_repair_defects(
                self._defect_store,
                self._store,
                solver_command,
            )
            print(
                f"[pipeline] Analysis: "
                f"{analysis_result.get('auto_fixed', 0)} auto-fixed, "
                f"{analysis_result.get('auto_fix_verified', 0)} verified, "
                f"{analysis_result.get('requires_developer', 0)} need review"
            )

        # ---- 5. Write task card --------------------------------------------
        task_card_path = self._write_task_card(
            stats, all_defects, analysis_result
        )

        # ---- 6. Defect store snapshot --------------------------------------
        defect_store_summary = self._defect_store.summary()

        # ---- 7. Persist pipeline summary -----------------------------------
        summary_path = os.path.join(
            self._defect_store.store_dir,
            f"pipeline_summary_{self.enumeration_id}.json",
        )
        with open(summary_path, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "enumeration_id": self.enumeration_id,
                    "preset": self.preset_name,
                    "parameters": {
                        "enumeration": self.enumeration_params,
                        "mutation": self.mutation_params,
                        "solver": self.solver_params,
                    },
                    "pipeline_stats": stats,
                },
                fh,
                indent=2,
                sort_keys=True,
            )

        # ---- 8. Report -----------------------------------------------------
        print()
        print("=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"  Graphs enumerated:   {stats['graphs_enumerated']}")
        print(f"  Graphs tested:       {stats['graphs_tested']}")
        print(f"  Original failures:   {stats['original_failures']}")
        print(f"  Mutations generated: {stats['mutations_generated']}")
        print(f"  Solver runs:         {stats['solves_run']}")
        print(f"  Defects found:       {stats['defects_found']}")
        print(f"  Task card:           {task_card_path}")

        return PipelineResult(
            enumeration_result=enum_result,
            defects_found=all_defects,
            analysis_result=analysis_result,
            task_card_path=task_card_path,
            stats=stats,
            defect_store_summary=defect_store_summary,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def preset_name(self) -> str:
        """Return the preset name if created via :meth:`from_preset`, else ``"custom"``."""
        return self._preset_name or "custom"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_enumeration(self) -> dict:
        """Run (or reload) scene-space enumeration.

        If a previous enumeration result exists on disk for
        *enumeration_id* it is reused to avoid recomputation.
        """
        root = self._store.enumeration_root(self.enumeration_id)
        result_path = os.path.join(root, "result.json")
        if os.path.exists(result_path):
            print(f"[pipeline] Reusing existing enumeration at {root}")
            return self._store.read_json_file(result_path)

        services = EnumeratorServices(
            store=self._store,
            save_graph=self._store.save_graph,
            load_graph=self._store.load_graph,
        )
        return enumerate_scene_space(self.enumeration_params, services)

    def _write_task_card(
        self,
        stats: dict[str, int],
        defects: list[DefectRecord],
        analysis_result: dict | None,
    ) -> str:
        """Write a Markdown task card and return its absolute path."""
        os.makedirs(self.task_card_dir, exist_ok=True)
        slug = f"defect-discovery-{self.enumeration_id}"
        task_card_path = os.path.join(self.task_card_dir, f"{slug}.md")

        by_severity: dict[str, int] = {}
        by_error: dict[str, int] = {}
        for d in defects:
            by_severity[d.severity] = by_severity.get(d.severity, 0) + 1
            by_error[d.error_type] = by_error.get(d.error_type, 0) + 1

        def _md_table(rows: list[tuple[str, str]]) -> str:
            if not rows:
                return ""
            header = "| Metric | Value |\n|--------|-------|"
            body = "\n".join(f"| {k} | {v} |" for k, v in rows)
            return f"{header}\n{body}"

        lines: list[str] = [
            f"# Task: Defect Discovery -- {self.enumeration_id}",
            "",
            f"- **Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Preset:** {self.preset_name}",
            f"- **Owner:** gcs-quality-steward",
            f"- **Scope:** solver_testing",
            f"- **Risk:** low",
            "",
            "## Summary",
            "",
            f"Automated defect-discovery pipeline run against enumeration "
            f"`{self.enumeration_id}`.",
            "",
            "## Pipeline Stats",
            "",
            _md_table([
                ("Graphs enumerated", str(stats.get("graphs_enumerated", 0))),
                ("Graphs tested", str(stats.get("graphs_tested", 0))),
                ("Original failures", str(stats.get("original_failures", 0))),
                ("Mutations generated", str(stats.get("mutations_generated", 0))),
                ("Solver runs", str(stats.get("solves_run", 0))),
                ("Defects found", str(stats.get("defects_found", 0))),
            ]),
            "",
            "## Defect Breakdown",
            "",
            "### By Severity",
            "",
        ]

        if by_severity:
            for k, v in sorted(by_severity.items()):
                lines.append(f"- **{k}**: {v}")
        else:
            lines.append("- *(none)*")

        lines.extend(["", "### By Error Type", ""])
        if by_error:
            for k, v in sorted(by_error.items()):
                lines.append(f"- **{k}**: {v}")
        else:
            lines.append("- *(none)*")

        if analysis_result:
            lines.extend([
                "",
                "## Analysis",
                "",
                f"- Auto-fixed: {analysis_result.get('auto_fixed', 0)}",
                f"- Verified: {analysis_result.get('auto_fix_verified', 0)}",
                f"- Requires developer: {analysis_result.get('requires_developer', 0)}",
            ])

        lines.extend([
            "",
            "## Parameters",
            "",
            "```json",
            json.dumps(
                {
                    "enumeration": self.enumeration_params,
                    "mutation": self.mutation_params,
                    "solver": self.solver_params,
                },
                indent=2,
            ),
            "```",
            "",
            "## Artifacts",
            "",
            f"- Defect store: `{self._defect_store.store_dir}`",
            f"- Scene store: `{self.store_dir}`",
            f"- Enumeration root: `{self._store.enumeration_root(self.enumeration_id)}`",
        ])

        with open(task_card_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

        return task_card_path


# ---------------------------------------------------------------------------
# Module helpers
# ---------------------------------------------------------------------------


def _default_enumeration_id() -> str:
    return f"defect_discovery_{int(time.time())}"
