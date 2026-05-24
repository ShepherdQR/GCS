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
- Completed through Step 28:
  - scene-generation repair policy has been extracted into
    `gcs_scene_generation.repair`;
  - scene-generation exploration and promotion-package orchestration have been
    extracted into `gcs_scene_generation.explorer` and
    `gcs_scene_generation.promotion_package`;
  - scratch-store path, graph IO, trace, root, and digest policy has been
    contained behind `gcs_scene_generation.storage.SceneGenerationStore`;
  - promotion public gates now prefer structured runtime/diagnostics reports
    before executable smoke fallback;
  - numeric rank/nullity evidence is computed over free Jacobian columns after
    declared boundary variables are frozen, while full variable dimension and
    frozen dimension remain visible in the public report;
  - `tools.py` remains the compatibility CLI facade;
  - default quality gate is `python tools\agentic_design\agentic_toolkit.py
    run-quality-gates`;
  - CTest contract baseline is 85 tests.

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

### Completed Step 27: Promotion Gate Hardening

Delivered:

- Add `public_gate_config.runtime_report` and
  `public_gate_config.runtime_report_path` support for structured runtime and
  diagnostics evidence.
- Keep existing executable smoke behavior as fallback when no structured
  runtime report is provided.
- Preserve existing gate IDs (`runtime_smoke`, `diagnostics_evidence`) while
  changing evidence preference from stdout parsing to structured reports where
  available.
- Keep explicit failed/unsupported semantics for fallback smoke gates.

Tests:

- Direct package tests verify structured runtime evidence passes runtime and
  diagnostics gates even when the fallback executable is missing.
- Existing missing-solver blocking tests still cover fallback unsupported
  behavior.

Reassessment after Step 27:

- Step 28 is now the highest-leverage next move: scene generation and
  promotion evidence are strong enough to return to solver algorithm
  deepening.
- Step 29 should remain after Step 28 so the atlas reflects both the solver
  algorithm step and the completed generation/promotion boundaries.

### Completed Step 28: Numeric Free-Column Rank Evidence

Decision:

- The highest-leverage solver-deepening move was in `gcs.numeric_engine`.
  Decomposition planning already had cover/order evidence, while numeric rank
  evidence still estimated rank and nullity over the full Jacobian even when
  boundary variables were frozen.

Delivered:

- Extend `RankConditionReport` with `free_variable_dimension` and
  `frozen_variable_dimension`.
- Estimate rank, nullity, under-constrained evidence, over-constrained
  evidence, singular evidence, and condition evidence from the Jacobian columns
  that are actually free under the task boundary policy.
- Preserve `variable_dimension` as the full active variable dimension so
  downstream diagnostics can distinguish model shape from numeric solve
  degrees of freedom.
- Add numeric contract coverage for boundary-frozen rank evidence.

Tests:

- Focused `NumericEngineContract` CTest suite passes with 13 tests.
- Full quality gate remains the pre-push validation command.

Reassessment after Step 28:

- Step 29 is now the highest-leverage next move. The solver, scene-generation,
  promotion, and numeric evidence boundaries changed enough that the
  architecture atlas should be synchronized before starting the next algorithm
  batch.
- No new evidence requires inserting another solver implementation step before
  the atlas synchronization.

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

As of the Step 28 completion update, the active planned step is Step 29.
Step 29 is the next implementation step.

