#!/usr/bin/env python3
"""End-to-end defect discovery pipeline: enumerate → mutate → solve → analyze → report.

Usage:
  python tools/solver_testing/pipeline.py --enumeration <id> [--max-graphs N] [--strategies s1,s2]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(TOOL_DIR, "..", ".."))
sys.path.insert(0, REPO_ROOT)

from tools.scene_generation.gcs_scene_generation import storage as scene_storage
from tools.scene_generation.gcs_scene_generation.promotion import (
    solver_scene_from_gcs,
    write_public_scene,
)
from tools.solver_testing.defect_store import (
    DefectRecord,
    DefectStore,
    classify_defect,
    make_defect_id,
)
from tools.solver_testing.mutator import MUTATION_STRATEGIES, mutate_constraint_values
from tools.solver_testing.runner import SolveResult, find_solver, run_single

STORE_DIR = os.environ.get(
    "GCS_SCENE_GENERATION_STORE_DIR",
    os.path.join(REPO_ROOT, "tools", "scene_generation", ".store"),
)


def main():
    parser = argparse.ArgumentParser(description="Defect discovery pipeline")
    parser.add_argument("--enumeration", required=True, help="Enumeration ID")
    parser.add_argument("--max-graphs", type=int, default=10, help="Max graphs to test")
    parser.add_argument("--strategies", default="positive_to_negative,zero_to_nonzero,angle_out_of_range", help="Comma-separated mutation strategies")
    parser.add_argument("--timeout", type=float, default=30.0, help="Per-solve timeout")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    store = scene_storage.SceneGenerationStore(STORE_DIR)
    defect_store = DefectStore()
    solver_command = find_solver()
    if solver_command is None:
        print("ERROR: GCS solver not found. Set GCS_EXE or build the project.")
        sys.exit(1)
    print(f"Solver: {solver_command[0]}")

    # Load enumeration result
    result_path = os.path.join(store.enumeration_root(args.enumeration), "result.json")
    if not os.path.exists(result_path):
        print(f"ERROR: Enumeration '{args.enumeration}' not found at {result_path}")
        sys.exit(1)

    with open(result_path) as f:
        enum_result = json.load(f)

    graph_ids = enum_result.get("graph_ids", [])[:args.max_graphs]
    print(f"Enumeration: {args.enumeration}")
    print(f"Graphs available: {len(enum_result.get('graph_ids', []))}, testing: {len(graph_ids)}")
    print(f"Strategies: {args.strategies}")
    print(f"Parameters: {json.dumps(enum_result.get('parameters', {}))}")
    print()

    strategies = [s.strip() for s in args.strategies.split(",")]
    unknown = [s for s in strategies if s not in MUTATION_STRATEGIES]
    if unknown:
        print(f"ERROR: Unknown strategies: {unknown}")
        print(f"Available: {list(MUTATION_STRATEGIES)}")
        sys.exit(1)

    all_defects = []
    stats = {"graphs_tested": 0, "mutations_generated": 0, "solves_run": 0, "defects_found": 0, "original_failures": 0}

    for graph_id in graph_ids:
        try:
            gcs = store.load_graph(graph_id)
        except FileNotFoundError:
            print(f"  SKIP {graph_id}: not found")
            continue

        stats["graphs_tested"] += 1

        # Solve original first
        public_scene = solver_scene_from_gcs(gcs)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".gcs.json", delete=False) as f:
            json.dump(public_scene, f)
            orig_scene_path = f.name

        orig_result = run_single(orig_scene_path, graph_id, solver_command, args.timeout)
        try:
            os.unlink(orig_scene_path)
        except OSError:
            pass

        if orig_result.status != "solved":
            stats["original_failures"] += 1
            print(f"  {graph_id}: original solve FAILED ({orig_result.status}) — skipping mutations")
            continue

        # Generate mutations
        mutated = mutate_constraint_values(gcs, strategies, args.seed + len(all_defects))
        stats["mutations_generated"] += len(mutated)

        for mut_idx, (mut_gcs, mutation_list) in enumerate(mutated):
            mut_scene = solver_scene_from_gcs(mut_gcs)
            mut_id = f"{graph_id}_m{mut_idx:03d}"
            with tempfile.NamedTemporaryFile(mode="w", suffix=".gcs.json", delete=False) as f:
                json.dump(mut_scene, f)
                mut_scene_path = f.name

            mut_result = run_single(mut_scene_path, mut_id, solver_command, args.timeout)
            stats["solves_run"] += 1
            try:
                os.unlink(mut_scene_path)
            except OSError:
                pass

            severity, error_type = classify_defect(orig_result, mut_result)
            if severity == "unknown":
                continue  # No defect detected

            stats["defects_found"] += 1
            defect_id = make_defect_id(args.enumeration, graph_id, mut_idx)
            orig_values = {str(c["id"]): float(c.get("value", 0.0)) for c in gcs.get("constraints", [])}
            mut_values = {str(c["id"]): float(c.get("value", 0.0)) for c in mut_gcs.get("constraints", [])}

            record = DefectRecord(
                defect_id=defect_id,
                scene_id=graph_id,
                original_values=orig_values,
                mutated_values=mut_values,
                mutation_strategies=[m.strategy for m in mutation_list],
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
                enumeration_id=args.enumeration,
                created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            )
            defect_store.save(record)
            all_defects.append(record)
            print(f"  DEFECT {defect_id}: {error_type} [{severity}] — {mutation_list[0].strategy} on c{mutation_list[0].constraint_id}")

    print()
    print("=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Graphs tested:         {stats['graphs_tested']}")
    print(f"Original failures:     {stats['original_failures']}")
    print(f"Mutations generated:   {stats['mutations_generated']}")
    print(f"Solver runs:           {stats['solves_run']}")
    print(f"Defects found:         {stats['defects_found']}")
    print()

    # Defect breakdown
    by_severity = {}
    by_error = {}
    for d in all_defects:
        by_severity[d.severity] = by_severity.get(d.severity, 0) + 1
        by_error[d.error_type] = by_error.get(d.error_type, 0) + 1

    print("By severity:")
    for k, v in sorted(by_severity.items()):
        print(f"  {k}: {v}")
    print("By error type:")
    for k, v in sorted(by_error.items()):
        print(f"  {k}: {v}")
    print()

    # Defect store summary
    dsum = defect_store.summary()
    print(f"Total in defect store: {dsum['total_defects']}")
    print()

    # Save pipeline summary
    summary_path = os.path.join(defect_store.store_dir, f"pipeline_summary_{args.enumeration}.json")
    with open(summary_path, "w") as f:
        json.dump({
            "enumeration_id": args.enumeration,
            "parameters": enum_result.get("parameters", {}),
            "pipeline_stats": stats,
            "defect_breakdown": {"by_severity": by_severity, "by_error_type": by_error},
            "graph_finding": "2RS/5G/5C produces 0 biconnected graphs (bipartite limitation); 3RS/5G/5C is viable",
        }, f, indent=2, sort_keys=True)
    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
