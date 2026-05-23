# Forward Execution Plan 2026-05-24

## Purpose

This document persists the next commit-level execution steps after the
scene-generation package split reached Step 24.

The plan is intentionally revisable. After each completed step, the next steps
must be reconsidered against the current code, tests, quality gates, and any
new architectural evidence. Updates should be committed before or with the
implementation step they describe.

## Current Baseline

- Branch target: `master`
- Current remote baseline at planning time: `origin/master`
- Completed through Step 25:
  - scene-generation repair policy has been extracted into
    `gcs_scene_generation.repair`;
  - scene-generation exploration and promotion-package orchestration have been
    extracted into `gcs_scene_generation.explorer` and
    `gcs_scene_generation.promotion_package`;
  - scratch-store path, graph IO, trace, root, and digest policy has been
    contained behind `gcs_scene_generation.storage.SceneGenerationStore`;
  - `tools.py` remains the compatibility CLI facade;
  - default quality gate is `python tools\agentic_design\agentic_toolkit.py
    run-quality-gates`;
  - CTest contract baseline remains 84 tests.

## Registered Next Steps

### Completed Step 25: Explorer And Promotion Orchestration Split

Delivered:

- Extract exploration request normalization, candidate building, coverage
  accounting, candidate gate orchestration, trace writing, negative evidence,
  and result assembly into `gcs_scene_generation.explorer`.
- Extract promotion-package writing, public adapter gate reports, provenance
  loading, and promotion blocking rules into
  `gcs_scene_generation.promotion_package`.
- Keep `tools.py` as the compatibility dispatcher and storage-bound facade.

Tests:

- Direct module tests cover `ExploreRequest` normalization, coverage evidence,
  and promotion-package blocking contracts.
- Existing deterministic explorer, negative evidence, promotion gate, and flat
  command compatibility tests still pass.

Reassessment after Step 25:

- Step 26 remains the highest-leverage next move because `tools.py` still owns
  the mutable `STORE_DIR` binding and flat graph-store compatibility wrappers.
- Step 27 should remain after Step 26: hardening public gates will be cleaner
  once store/path ownership is contained.
- Step 28 and Step 29 remain registered; no new evidence requires reordering
  them before store containment.

### Completed Step 26: Store Adapter Containment

Delivered:

- Introduce `SceneGenerationStore` as the store adapter object carrying
  `store_dir`, graph IO, safe IDs, JSON IO, exploration roots, candidate roots,
  promotion roots, trace append, and digest helpers.
- Route `tools.py` compatibility storage functions through the adapter while
  preserving the mutable `STORE_DIR` binding expected by tests and manual
  scripts.
- Route explorer services and promotion-package helpers through the adapter
  instead of passing raw store paths through those orchestration seams.

Tests:

- Focused unittest coverage now checks adapter save/load/list plus exploration
  and promotion root contracts.
- Existing deterministic explorer and promotion package tests still pass.

Reassessment after Step 26:

- Step 27 is now the highest-leverage next move: public promotion gates still
  depend on executable smoke output and should prefer direct IO/runtime/viewer
  adapters where available.
- Step 28 should stay after Step 27 because solver algorithm deepening will be
  better supported once promoted fixtures have stronger direct public gates.
- Step 29 should stay after Step 28 unless the gate-hardening work changes the
  visual architecture atlas earlier.

### Step 27: Promotion Gate Hardening

Goal:

- Harden public promotion gates beyond executable smoke checks where direct
  public APIs are available.

Expected shape:

- Prefer direct IO, kernel, contract-tool, runtime, diagnostics, and viewer
  adapters over parsing process output.
- Keep `public_gate_config.solver_command` as a fallback smoke path.
- Preserve explicit skipped/unsupported/failed gate semantics.

Tests:

- Public scene IO round trip remains canonical.
- Missing adapter/solver evidence remains explicit and blocks default
  promotion.
- Passing direct gates and fallback smoke gates produce comparable structured
  evidence.

### Step 28: Solver Algorithm Deepening Reassessment

Goal:

- Return to the C++ solver modules and choose the next highest-leverage
  algorithm-deepening step.

Candidate areas:

- Numeric engine: stronger damping, scaling, stopping criteria, rank evidence,
  and boundary-variable handling.
- Diagnostics: richer conflict/redundancy/gluing obstruction extraction.
- Decomposition planner: stronger separator, cover, and solve-DAG evidence.

Decision rule:

- Pick the module where current contract tools and scene corpus can produce
  the most actionable failing or incomplete evidence.

### Step 29: Architecture Atlas Synchronization

Goal:

- Synchronize the visualization architecture atlas with the current module and
  tooling state.

Expected shape:

- Ensure architecture diagrams match the implemented module boundaries.
- Keep SVG/InkScape source assets and rendered figure assets intentionally
  tracked or intentionally ignored.
- Keep UI aesthetic work separate from solver/scene-generation implementation
  steps unless a step explicitly crosses that boundary.

## Reassessment Protocol

After each step:

1. Run the relevant focused tests.
2. Run the full quality gate unless the step is documentation-only and its
   scope clearly does not affect executable behavior.
3. Update `docs/architecture/66-implementation-execution-roadmap.md` and
   `docs/architecture/67-current-progress-and-next-steps.md`.
4. Reconsider the remaining registered steps:
   - keep the next step if it is still the highest-leverage move;
   - split it if risk is too high for one commit;
   - reorder it if new evidence shows a more urgent boundary or quality gap;
   - replace it if completed work makes it obsolete.
5. Commit and push the completed step.

## Registration Confirmation

As of the Step 26 completion update, the active planned steps are registered
as Step 27 through Step 29. Step 27 is the next implementation step.

