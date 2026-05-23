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
- Completed through Step 24:
  - scene-generation repair policy has been extracted into
    `gcs_scene_generation.repair`;
  - `tools.py` remains the compatibility CLI facade;
  - default quality gate is `python tools\agentic_design\agentic_toolkit.py
    run-quality-gates`;
  - CTest contract baseline remains 84 tests.

## Registered Next Steps

### Step 25: Explorer And Promotion Orchestration Split

Goal:

- Extract exploration request normalization, candidate building, coverage
  accounting, gate orchestration, trace writing, promotion-package writing, and
  promotion blocking rules from `tools.py`.

Expected shape:

- Add `gcs_scene_generation.explorer` for exploration request/result,
  candidate provenance, coverage scoring, negative evidence, and trace
  orchestration.
- Add a package-level promotion orchestration helper when it can be split
  cleanly without changing the command surface.
- Keep `tools.py` as the compatibility dispatcher and storage-bound facade.

Tests:

- Stable `ExploreRequest -> ExploreResult` output for a fixed seed.
- Candidate provenance and artifact IDs remain stable.
- Negative evidence preserves typed rejection reason codes.
- Promotion package replay/blocking remains deterministic.

### Step 26: Store Adapter Containment

Goal:

- Reduce remaining direct `.store` path knowledge in `tools.py` and package
  helpers.

Expected shape:

- Introduce a small store adapter object or module functions that carry
  `store_dir`, graph IO, exploration roots, promotion roots, and trace append.
- Keep flat compatibility reads/writes working.
- Keep generated `.store` data scratch-only unless explicit fixture promotion
  is requested.

Tests:

- Alternate `GCS_SCENE_GENERATION_STORE_DIR` remains deterministic.
- Flat command compatibility still works.
- Exploration and promotion package paths remain stable.

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

As of this document, the active planned steps are registered as Step 25 through
Step 29. Step 25 is the next implementation step.

