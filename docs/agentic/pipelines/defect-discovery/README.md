# Defect Discovery Pipeline (DDP)

**Pipeline ID**: `defect-discovery`
**Version**: v1
**Status**: active
**Owner**: gcs-cpp-solver-maintainer
**Specialist**: gcs-constraint-semantics-steward

## Purpose

Systematically enumerate constraint graphs for a fixed parameter space, mutate
constraint values, batch-solve with the GCS solver, capture solver failures as
structured defect records, classify and analyze defects, and produce a task card
with repair recommendations.

## Pipeline Flow

```
Enumeration → Mutation → Batch Solve → Defect Classification → Analysis → Task Card
     │            │           │               │                  │            │
     v            v           v               v                  v            v
  .store/     mutated     SolveResult     DefectRecord      RepairResult   task.md
  enumerations/ copies     per scene      .defects/         per defect
```

### Step 1 — Enumeration
Exhaustively enumerate all valid constraint graphs for given
(num_geometries, num_constraints, num_rigid_sets). Applies geometry-primal
biconnectivity (or connectivity) filter, constraint signature validation,
canonical deduplication, and parameterization.

**Tool**: `tools/scene_generation/tools.py enumerate_scene_space`
**Module**: `tools/scene_generation/gcs_scene_generation/enumerator.py`

### Step 2 — Mutation
For each solvable graph, apply constraint-value mutation strategies
(negation, scaling, perturbation, extreme values, angle range violation).
Each strategy targets specific constraint types based on semantic validity.

**Module**: `tools/solver_testing/mutator.py`

### Step 3 — Batch Solve
Serialize each scene to `gcs-0.3` JSON, invoke GCS.exe, parse stdout/stderr
into structured `SolveResult` records.

**Module**: `tools/solver_testing/runner.py`

### Step 4 — Defect Classification
Compare original vs mutated `SolveResult`. Classify severity (crash,
wrong_result, diagnostic_only) and error type (negative_distance,
gluing_boundary_mismatch, numerically_singular, etc.).

**Module**: `tools/solver_testing/defect_store.py`

### Step 5 — Analysis
Map error types to repair strategies. Auto-fix mathematically unambiguous
cases (abs for negative distance, wrap for angle range, perturbation for
degenerate geometry). Flag complex failures for developer review.

**Module**: `tools/solver_testing/analyzer.py`

### Step 6 — Task Card
Create a task card summarizing defects found, fixes applied, and items
awaiting developer attention. Uses `agentic_toolkit.py new-task-card`.

## Input Parameters

See [parameters.md](parameters.md) for the full parameter schema.

## Output Artifacts

| Artifact | Location |
|----------|----------|
| Enumerated graphs | `tools/scene_generation/.store/enumerations/<id>/` |
| Defect records | `tools/solver_testing/.defects/` |
| Pipeline summary | `tools/solver_testing/.defects/pipeline_summary_<id>.json` |
| Task card | `docs/agentic/tasks/<date>-<slug>.md` |

## Invocation

```bash
# Full pipeline
python tools/solver_testing/pipeline.py \
  --enumeration defect_2rs_5g_5c \
  --max-graphs 20 \
  --strategies "positive_to_negative,epsilon_perturb,extreme_value" \
  --timeout 10

# Enumeration only
python tools/scene_generation/tools.py enumerate_scene_space \
  --input '{"enumeration_id":"my_enum","num_geometries":5,"num_constraints":5,"num_rigid_sets":2,"require_biconnected":false,"max_graphs":200}'
```

## Historical Runs

| Date | Enumeration | Graphs | Defects | Key Finding |
|------|------------|--------|---------|-------------|
| 2026-05-30 | defect_discovery_3rs_5g_5c | 200 | 5 | 3RS is viable; 2RS impossible for biconnected |
| 2026-05-30 | defect_2rs_5g_5c | 200 (2 solvable) | 40 | gluing_boundary_mismatch from epsilon perturbation |
