# Defect Discovery Skill

```yaml
# .claude/skills/defect-discovery.md
---
name: defect-discovery
description: >
  Run the GCS defect discovery pipeline: enumerate constraint graphs for a
  fixed parameter space, mutate constraint values, batch-solve with GCS.exe,
  capture and classify defects, analyze and auto-fix where possible, and
  produce a task card with repair recommendations.
version: v1
owner: gcs-cpp-solver-maintainer
specialist: gcs-constraint-semantics-steward
---

# Defect Discovery Pipeline Skill

## Purpose

Systematic solver defect discovery through constraint-graph enumeration
and constraint-value mutation testing.

## When to Invoke

- User asks to "find solver defects", "test solver robustness",
  "run defect discovery", "mutation test the solver"
- User provides specific enumeration parameters (N geometries, M constraints,
  K rigid sets) and wants a defect report
- After solver C++ changes that need regression-like stress testing
- Periodic (nightly/weekly) solver quality gate runs

## Required Context

This skill runs a multi-step pipeline. Before starting, confirm:
1. GCS.exe is built and available at `out/build/clang-ninja/GCS.exe`
   (or set `GCS_EXE` env var)
2. Python 3.11+ with stdlib only (no external deps needed)
3. The enumeration parameter space fits in reasonable time
   (rule of thumb: ≤200 graphs for interactive, ≤2000 for scheduled)

## Pipeline Steps

### Step 1 — Enumeration
Run `tools/scene_generation/tools.py enumerate_scene_space` with the
specified parameters. If 0 graphs are produced (e.g., 2RS biconnected
limitation), report the finding and offer to relax `require_biconnected`.

### Step 2 — Find Solvable Graphs
Batch-test enumerated graphs with GCS.exe. Skip graphs that fail original
solve. Report the solvable fraction.

### Step 3 — Mutation Testing
For each solvable graph, apply the specified mutation strategies. Run
the solver on each mutated copy. Classify results as defects where the
original solved but the mutated copy failed or crashed.

### Step 4 — Defect Analysis
Run `tools/solver_testing/analyzer.py` functions to classify defects
and apply auto-fixes for mathematically unambiguous cases (negative
distance → abs, angle out of range → wrap, degenerate geometry → perturb).

### Step 5 — Task Card
Create a task card via `agentic_toolkit.py new-task-card` summarizing:
- Number of graphs enumerated, solvable fraction
- Defect breakdown by error type and severity
- Auto-fixes applied (with verification status)
- Items requiring developer attention

## Parameters

See `docs/agentic/pipelines/defect-discovery/parameters.md` for the full
parameter schema. Key parameters the user may specify:

```
enumeration_id    — unique ID (auto-generated if omitted)
num_geometries    — default 5
num_constraints   — default 5
num_rigid_sets    — default 2
require_biconnected — default true
max_graphs        — default 200 (enumeration), 20 (pipeline)
strategies        — default "positive_to_negative,zero_to_nonzero,angle_out_of_range"
timeout_seconds   — default 10
```

## Output

A task card at `docs/agentic/tasks/<date>-defect-discovery-<id>.md`
with human gate enabled. Defect records persist in
`tools/solver_testing/.defects/` for subsequent analysis.

## Post-Run

After the pipeline completes, the user should:
1. Review the task card
2. For `gluing_boundary_mismatch` defects: investigate decomposition stability
3. For auto-fixed defects: verify the fix makes semantic sense
4. Archive the task card when defects are resolved
