#!/usr/bin/env python3
"""Unified pipeline runner — list, run, and manage all GCS pipelines.

Usage:
  python tools/solver_testing/pipelines/run.py list
  python tools/solver_testing/pipelines/run.py run <pipeline-id> [--preset NAME] [--config FILE.json]
  python tools/solver_testing/pipelines/run.py info <pipeline-id>
  python tools/solver_testing/pipelines/run.py schedule <pipeline-id>
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

PIPELINE_REGISTRY = {
    "defect-discovery": {
        "id": "defect-discovery",
        "name": "Defect Discovery Pipeline",
        "tier": "P0",
        "class": "DefectDiscoveryPipeline",
        "description": "Enumerate constraint graphs, mutate values, batch-solve, capture defects, classify, and produce task card.",
        "presets": ["smoke", "standard", "full"],
        "config_keys": ["enumeration_id", "num_geometries", "num_constraints", "num_rigid_sets",
                        "require_biconnected", "max_graphs", "strategies", "timeout_seconds"],
        "estimated_runtime": "2min (smoke) / 15min (standard) / 2hr (full)",
    },
    "solver-regression": {
        "id": "solver-regression",
        "name": "Solver Regression Pipeline",
        "tier": "P0",
        "class": "RegressionPipeline",
        "description": "Run solver on fixture corpus, compare against baseline, detect regressions.",
        "config_keys": ["corpus_path", "baseline_path", "tolerance", "solver_command", "timeout"],
        "estimated_runtime": "5min (typical corpus)",
        "default_config": {"corpus_path": "fixtures/scene/basic"},
    },
    "numeric-stability": {
        "id": "numeric-stability",
        "name": "Numeric Stability Pipeline",
        "tier": "P0",
        "class": "StabilityPipeline",
        "description": "Test solver under extreme values — logspace sweeps, near-zero, boundary conditions.",
        "config_keys": ["scene_path", "constraint_index", "sweep_spec", "solver_command", "timeout_seconds"],
        "estimated_runtime": "10min (20-step sweep)",
        "default_config": {"scene_path": "fixtures/scene/json/current_two_point.gcs.json", "constraint_index": 0, "sweep_spec": {"param": "value", "start": 1e-6, "end": 1e6, "steps": 5}},
    },
    "diagnostic-certification": {
        "id": "diagnostic-certification",
        "name": "Diagnostic Certification Pipeline",
        "tier": "P1",
        "class": "DiagnosticsCertPipeline",
        "description": "Verify solver produces correct diagnostics for 6 known-bad input types.",
        "config_keys": ["solver_command", "strict"],
        "estimated_runtime": "2min",
    },
    "contract-compliance": {
        "id": "contract-compliance",
        "name": "Contract Compliance Pipeline",
        "tier": "P1",
        "class": "ContractCompliancePipeline",
        "description": "Audit module import boundaries, stable IDs, tolerance consistency.",
        "config_keys": ["root_path", "checks"],
        "estimated_runtime": "30s",
    },
    "io-round-trip": {
        "id": "io-round-trip",
        "name": "IO Round-Trip Pipeline",
        "tier": "P1",
        "class": "RoundTripPipeline",
        "description": "Verify scene data survives JSON/text serialization round-trips losslessly.",
        "config_keys": ["fixture_paths", "formats", "solver_command", "solve_check", "timeout_seconds"],
        "estimated_runtime": "5min",
        "default_config": {"fixture_paths": ["fixtures/scene/json"]},
    },
    "scene-generation": {
        "id": "scene-generation",
        "name": "Scene Generation Pipeline",
        "tier": "P2",
        "class": "SceneGenPipeline",
        "description": "Coverage-driven fixture generation via exploration + enumeration.",
        "config_keys": ["spec", "budget", "strategies"],
        "estimated_runtime": "10min (typical budget)",
    },
    "performance-benchmark": {
        "id": "performance-benchmark",
        "name": "Performance Benchmark Pipeline",
        "tier": "P2",
        "class": "BenchmarkPipeline",
        "description": "Measure solver performance, store in SQLite trend DB, detect regressions.",
        "config_keys": ["corpus_path", "db_path", "solver_command", "warmup", "runs", "threshold"],
        "estimated_runtime": "15min (typical corpus)",
        "default_config": {"corpus_path": "fixtures/scene/basic", "db_path": "out/benchmark_trend.db"},
    },
    "cross-solver-compare": {
        "id": "cross-solver-compare",
        "name": "Cross-Solver Compare Pipeline",
        "tier": "P2",
        "class": "CrossSolverComparePipeline",
        "description": "Compare GCS solver results against external solvers on shared benchmarks.",
        "config_keys": ["benchmark_dir", "external_spec_path", "solver_command", "timeout_seconds"],
        "estimated_runtime": "10min",
        "default_config": {"benchmark_dir": "fixtures/scene/basic", "external_spec_path": "fixtures/benchmark/external_solver_spec.json"},
    },
    "repository-audit": {
        "id": "repository-audit",
        "name": "Repository Audit Pipeline",
        "tier": "P3",
        "class": "RepoAuditPipeline",
        "description": "Classify files, check directory conventions, detect stale artifacts, collect snapshot.",
        "config_keys": ["root", "max_age_days"],
        "estimated_runtime": "30s",
    },
}


def _get_pipeline_class(pipeline_id: str):
    info = PIPELINE_REGISTRY[pipeline_id]
    module = importlib.import_module("tools.solver_testing.pipelines")
    return getattr(module, info["class"])


def cmd_list(args):
    """List all registered pipelines."""
    print()
    print("GCS Pipeline Registry")
    print("=" * 70)
    for tier in ["P0", "P1", "P2", "P3"]:
        tier_pipelines = [(pid, info) for pid, info in PIPELINE_REGISTRY.items() if info["tier"] == tier]
        if not tier_pipelines:
            continue
        tier_names = {"P0": "Core Solver Quality", "P1": "Contracts & Diagnostics",
                      "P2": "Scene & Performance", "P3": "Governance & Audit"}
        print(f"\n  Tier {tier} — {tier_names[tier]}")
        print(f"  {'─' * 60}")
        for pid, info in tier_pipelines:
            preset_str = f" [presets: {', '.join(info['presets'])}]" if info.get("presets") else ""
            print(f"  {pid}")
            print(f"    {info['description']}")
            print(f"    Runtime: ~{info['estimated_runtime']}{preset_str}")
    print()
    print("Commands:")
    print("  python tools/solver_testing/pipelines/run.py run <id>")
    print("  python tools/solver_testing/pipelines/run.py run <id> --preset smoke")
    print("  python tools/solver_testing/pipelines/run.py run <id> --config config.json")
    print("  python tools/solver_testing/pipelines/run.py info <id>")
    print()


def cmd_run(args):
    """Run a pipeline by ID."""
    pipeline_id = args.pipeline_id
    if pipeline_id not in PIPELINE_REGISTRY:
        print(f"Unknown pipeline: {pipeline_id}")
        print(f"Available: {', '.join(PIPELINE_REGISTRY)}")
        sys.exit(1)

    info = PIPELINE_REGISTRY[pipeline_id]
    pipeline_cls = _get_pipeline_class(pipeline_id)

    # Determine config: start from registry defaults, then overlay --config file
    config = dict(info.get("default_config", {}))
    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            config.update(json.load(f))

    print()
    print(f"Running: {info['name']} ({pipeline_id})")
    print(f"Tier: {info['tier']}  |  Est. runtime: {info['estimated_runtime']}")
    print("=" * 70)

    started = time.monotonic()

    try:
        # Handle presets
        if args.preset and hasattr(pipeline_cls, "from_preset"):
            pipeline = pipeline_cls.from_preset(args.preset, **config)
            result = pipeline.run()
        elif pipeline_id == "defect-discovery":
            pipeline = pipeline_cls(**config)
            result = pipeline.run()
        elif pipeline_id == "diagnostic-certification":
            pipeline = pipeline_cls()
            result = pipeline.run(**config)
        elif pipeline_id == "numeric-stability":
            pipeline = pipeline_cls()
            result = pipeline.run(**config)
        elif pipeline_id == "contract-compliance":
            pipeline = pipeline_cls()
            root_path = config.pop("root_path", ".")
            checks = config.pop("checks", None)
            result = pipeline.run(root_path, checks)
        elif pipeline_id == "repository-audit":
            pipeline = pipeline_cls()
            root = config.pop("root", ".")
            max_age_days = config.pop("max_age_days", 90)
            result = pipeline.run(root, max_age_days)
        elif pipeline_id == "scene-generation":
            pipeline = pipeline_cls()
            spec = config.pop("spec", {})
            budget = config.pop("budget", {"max_candidates": 100})
            strategies = config.pop("strategies", ["explore", "enumerate"])
            result = pipeline.run(spec, budget, strategies)
        elif pipeline_id == "performance-benchmark":
            pipeline = pipeline_cls()
            result = pipeline.run(**config)
        elif pipeline_id == "solver-regression":
            pipeline = pipeline_cls()
            result = pipeline.run(**config)
        elif pipeline_id == "io-round-trip":
            pipeline = pipeline_cls()
            result = pipeline.run(**config)
        elif pipeline_id == "cross-solver-compare":
            pipeline = pipeline_cls()
            result = pipeline.run(**config)
        else:
            pipeline = pipeline_cls()
            result = pipeline.run(**config)

        elapsed = time.monotonic() - started
        print(f"\nPipeline completed in {elapsed:.1f}s")
        if hasattr(result, "summary"):
            print(result.summary())
        elif isinstance(result, dict):
            print(json.dumps(result, indent=2, default=str)[:2000])

    except Exception as exc:
        elapsed = time.monotonic() - started
        print(f"\nPipeline FAILED after {elapsed:.1f}s: {exc}")
        sys.exit(1)


def cmd_info(args):
    """Show detailed info about a pipeline."""
    pipeline_id = args.pipeline_id
    if pipeline_id not in PIPELINE_REGISTRY:
        print(f"Unknown pipeline: {pipeline_id}")
        sys.exit(1)

    info = PIPELINE_REGISTRY[pipeline_id]
    pipeline_cls = _get_pipeline_class(pipeline_id)

    print()
    print(f"{info['name']} ({pipeline_id})")
    print("=" * 60)
    print(f"Tier:        {info['tier']}")
    print(f"Class:       {info['class']}")
    print(f"Runtime:     {info['estimated_runtime']}")
    print(f"Description: {info['description']}")
    print()

    if info.get("presets"):
        print("Presets:")
        for preset in info["presets"]:
            print(f"  --preset {preset}")
        print()

    print("Config keys:")
    for key in info.get("config_keys", []):
        print(f"  {key}")
    print()

    print("Run examples:")
    pid = pipeline_id
    if info.get("presets"):
        print(f"  python tools/solver_testing/pipelines/run.py run {pid} --preset {info['presets'][0]}")
    print(f"  python tools/solver_testing/pipelines/run.py run {pid} --config {pid}-config.json")
    print()

    # Show plan path
    plan_path = f"docs/agentic/pipelines/{pid}/development-plan.md"
    if os.path.exists(os.path.join(REPO_ROOT, plan_path)):
        print(f"Development plan: {plan_path}")
    print()


def cmd_schedule(args):
    """Print scheduling instructions for a pipeline."""
    pipeline_id = args.pipeline_id
    if pipeline_id not in PIPELINE_REGISTRY:
        print(f"Unknown pipeline: {pipeline_id}")
        sys.exit(1)

    info = PIPELINE_REGISTRY[pipeline_id]
    print()
    print(f"Scheduling: {info['name']} ({pipeline_id})")
    print("=" * 60)
    print()
    print("Method 1 — Claude Code Scheduled Task (recommended):")
    print(f'  /schedule-task create \\')
    print(f'    --task-id {pipeline_id}-daily \\')
    print(f'    --cron "17 3 * * *" \\')
    print(f'    --prompt "Run the {pipeline_id} pipeline with default config. Report results."')
    print()
    print("Method 2 — Direct CLI via cron / Task Scheduler:")
    if info.get("presets"):
        print(f'  python tools/solver_testing/pipelines/run.py run {pipeline_id} --preset {info["presets"][0]}')
    else:
        print(f'  python tools/solver_testing/pipelines/run.py run {pipeline_id} --config {pipeline_id}-config.json')
    print()
    print("Method 3 — Manual via Claude Code skill:")
    print(f"  Ask Claude: 'run the {pipeline_id} pipeline'")
    print()


def main():
    parser = argparse.ArgumentParser(description="GCS Unified Pipeline Runner")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all registered pipelines")

    run_parser = sub.add_parser("run", help="Run a pipeline")
    run_parser.add_argument("pipeline_id", help="Pipeline ID")
    run_parser.add_argument("--preset", help="Preset name (smoke/standard/full)")
    run_parser.add_argument("--config", help="JSON config file path")

    info_parser = sub.add_parser("info", help="Show pipeline details")
    info_parser.add_argument("pipeline_id", help="Pipeline ID")

    sched_parser = sub.add_parser("schedule", help="Show scheduling instructions")
    sched_parser.add_argument("pipeline_id", help="Pipeline ID")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "info":
        cmd_info(args)
    elif args.command == "schedule":
        cmd_schedule(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
