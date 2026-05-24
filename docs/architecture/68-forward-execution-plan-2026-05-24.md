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
- Completed through Step 30:
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
  - the visualization architecture atlas and generated Figure 1 assets now
    show scene-generation promotion boundaries, contract tools, and
    free/frozen numeric rank evidence;
  - diagnostics rank reports preserve numeric full/free/frozen rank
    dimensions from `numeric::RankConditionReport`;
  - `tools.py` remains the compatibility CLI facade;
  - default quality gate is `python tools\agentic_design\agentic_toolkit.py
    run-quality-gates`;
  - CTest contract baseline is 86 tests.

## Execution Cadence Contract

For Steps 31 through 40, each commit-level step must follow this cadence:

1. Execute only the current registered step unless new evidence makes it
   unsafe or obsolete.
2. Add or update durable contract tests, scene fixtures, generated scenes, or
   quality-gate checks whenever the step introduces executable behavior.
3. After implementation and validation, persist a completed-step summary in
   this document with delivered changes, tests, and reassessment.
4. Update `docs/architecture/66-implementation-execution-roadmap.md` and
   `docs/architecture/67-current-progress-and-next-steps.md`.
5. Reconsider all remaining steps before starting the next step:
   - keep the next step if it remains highest leverage;
   - split it if the blast radius is too large;
   - reorder it if boundary evidence exposes a more urgent gap;
   - replace it if completed work makes it obsolete.
6. Commit and push at every clean, validated commit boundary.

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

### Completed Step 29: Architecture Atlas Synchronization

Delivered:

- Synchronize the Mermaid architecture atlas with current C++ module
  boundaries, contract tools, scene-generation package boundaries, promotion
  gates, and numeric free-column rank evidence.
- Add an explicit scene-generation and promotion tooling diagram covering the
  CLI facade, package modules, `SceneGenerationStore`, public scene artifacts,
  and public IO/runtime/diagnostics/viewer gates.
- Document intentionally tracked Figure 1 review artifacts separately from the
  canonical generated SVG assets.
- Update the Figure 1 renderer, layout tokens, and generated SVG assets so the
  residual/rank panel distinguishes full variables, free columns, frozen
  columns, and nullity.

Tests:

- `python tools\architecture_visualization\render_gcs_figure1.py --fixture
  fixtures\scene\saved\triangle_003_graph.json --out-dir
  docs\architecture\70-visualization\assets`
- XML parse checks for the main Figure 1 SVG and residual/rank panel SVG.
- `python tools\agentic_design\agentic_toolkit.py validate-docs`
- `python tools\agentic_design\agentic_toolkit.py run-quality-gates`

Reassessment after Step 29:

- Step 30 should propagate the new free/frozen numeric rank evidence into
  diagnostics reports. The numeric engine now exposes the right fields, but
  diagnostics still reports only the legacy numeric variable dimension.
- Decomposition separator deepening remains useful after diagnostics can
  preserve the new rank evidence end to end.

### Completed Step 30: Diagnostics Free/Frozen Rank Propagation

Delivered:

- Extend diagnostics rank reporting so downstream runtime, viewer, and
  promotion evidence can distinguish full active variables from free and frozen
  numeric solve dimensions.
- Add `numeric_free_variable_dimension` and
  `numeric_frozen_variable_dimension` to `diagnostics::RankReport`.
- Populate those fields from `numeric::RankConditionReport`.
- Add diagnostics contract coverage using a boundary-frozen numeric task.
- Keep status precedence unchanged.

Tests:

- Focused `DiagnosticsContract` CTest suite.
- Full quality gate remains the pre-push validation command.

Reassessment after Step 30:

- Step 31 should expose preserved rank evidence through runtime/viewer
  projection contracts. Numeric and diagnostics now preserve the evidence, but
  boundary consumers still need a public projection path.
- Decomposition separator deepening remains useful after rank evidence is
  visible at runtime/viewer/promotion boundaries.

### Step 31: Runtime And Viewer Rank Evidence Projection

Goal:

- Make full/free/frozen rank evidence visible through command summaries,
  viewer overlays, or another public boundary projection without requiring UI
  or promotion tools to inspect numeric internals directly.

Expected shape:

- Decide whether the source of truth is post-local-solve diagnostics or a
  viewer projection over existing runtime numeric reports.
- Add a small public summary/projection contract for rank evidence.
- Cover accepted and boundary-frozen evidence paths with contract tests.
- Keep solver math and diagnostic status precedence unchanged.

Detailed plan:

- Inspect `runtime::CommandResult`, `viewer::DiagnosticOverlay`,
  `viewer::SnapshotSummary`, and promotion gate report consumers.
- Choose the smallest public boundary contract that preserves full/free/frozen
  rank evidence without making viewer code interpret numeric internals.
- Prefer a viewer/runtime summary structure that can be built from
  `diagnostics::RankReport` or existing runtime numeric reports.
- Add contract coverage for accepted solve evidence and boundary-frozen rank
  evidence.
- Persist the Step 31 summary and then reassess whether Step 32 should consume
  the new projection directly or first require post-local-solve diagnostics in
  runtime.

Exit criteria:

- Boundary consumers can read full variable dimension, free variable
  dimension, frozen variable dimension, residual dimension, rank, nullity, and
  under/over/singular flags through a public runtime/viewer projection.
- Full quality gate passes.

### Step 32: Promotion Gate Uses Rank Evidence

Goal:

- Make scene-generation promotion gates consume structured rank evidence from
  public runtime/viewer/diagnostics reports instead of relying only on
  executable smoke success or loose stdout evidence.

Expected shape:

- Extend promotion-package gate records with rank evidence fields when a
  structured runtime report is available.
- Validate full/free/frozen/nullity evidence for promoted scenes where the
  evidence exists.
- Keep executable smoke as fallback for environments without structured
  reports.

Detailed plan:

- Inspect `gcs_scene_generation.promotion_package` structured runtime report
  parsing and existing public gate IDs.
- Add a rank-evidence parser that accepts the Step 31 boundary projection.
- Preserve current `runtime_smoke` and `diagnostics_evidence` gate IDs unless
  a new explicit `rank_evidence` gate is clearer.
- Add Python unit tests for structured report pass, missing evidence fallback,
  and unsupported evidence shape.
- Persist Step 32 summary and reassess the solver algorithm queue.

Exit criteria:

- Promotion packages can prove rank evidence through structured public reports.
- Existing smoke fallback remains explicit and tested.

### Step 33: Decomposition Separator And Solve-DAG Deepening

Goal:

- Deepen `gcs.decomposition_planner` from coverage/order validation toward
  stronger separator, boundary projection, and SolveDAG evidence.

Expected shape:

- Strengthen separator detection or articulation/biconnected evidence where it
  directly improves context cover quality.
- Make solve ordering explain boundary dependencies and unsupported plan
  causes.
- Keep planner policy separate from numeric solve iteration.

Detailed plan:

- Inspect incidence graph component/BCC evidence and current planner
  `CoverPlan`, `Subproblem`, `BoundaryProjection`, and solve order contracts.
- Add a focused contract for a graph where separator structure should produce
  a stable boundary projection or solve-order dependency.
- Add or promote a reusable fixture if test-local construction would hide the
  graph semantics.
- Persist Step 33 summary and reassess diagnostics/runtime follow-up needs.

Exit criteria:

- Planner output exposes stronger separator or SolveDAG evidence through
  deterministic public contracts.
- Contract tests cover both accepted and unsupported/degraded plan evidence.

### Step 34: Boundary-Aware Runtime Diagnostics Pass

Goal:

- Add post-local-solve diagnostic evidence to `session_runtime` so command
  results carry structured rank/residual evidence rather than only pre-solve
  diagnostics and raw numeric reports.

Expected shape:

- Run diagnostics after local numeric solves when local numeric reports are
  available.
- Preserve transaction semantics: failed diagnostics must not commit durable
  state unless policy explicitly accepts warnings.
- Avoid duplicating numeric report interpretation in runtime.

Detailed plan:

- Inspect current runtime solve stages and where numeric reports are collected.
- Add a post-local-solve diagnostics field or summary to `CommandResult`.
- Record a stage trace entry for post-local diagnostics.
- Add runtime contract tests for accepted solve diagnostics and failed or
  boundary-frozen diagnostic evidence.
- Persist Step 34 summary and reassess viewer/promotion consumption.

Exit criteria:

- `CommandResult` exposes post-local diagnostics through public contracts.
- Accepted and rejected command paths preserve state-version semantics.

### Step 35: Diagnostics Conflict And Redundancy Deepening

Goal:

- Improve diagnostics from broad conflict/redundancy candidates toward smaller
  and more explainable responsible sets.

Expected shape:

- Minimize residual conflicts when evidence allows stable smaller constraint
  sets.
- Improve redundancy evidence for over-constrained contexts without changing
  status precedence accidentally.
- Preserve gluing obstruction conflicts separately from residual conflicts.

Detailed plan:

- Inspect current `find_conflicts`, `find_redundancies`, fixture corpus, and
  golden report evidence.
- Add contract tests for at least one residual conflict minimization case and
  one redundancy evidence case.
- Prefer reusable contract-tools fixtures over ad hoc local model construction.
- Persist Step 35 summary and reassess numeric robustness needs.

Exit criteria:

- Diagnostics names smaller stable subject sets where current evidence supports
  it.
- Existing obstruction and status-precedence contracts remain stable.

### Step 36: Numeric Robustness Batch

Goal:

- Harden dense numeric baseline behavior around scaling, rank tolerance,
  condition evidence, stopping criteria, and boundary/frozen-column edge cases.

Expected shape:

- Improve numeric report reliability without adding an external linear algebra
  dependency.
- Preserve `NumericTask`, `NumericReport`, and `RankConditionReport`
  contracts.
- Keep local solve proposals separate from runtime commit decisions.

Detailed plan:

- Inspect residual/Jacobian assembly, damping, trust radius, rank tolerance,
  and condition estimate code paths.
- Add focused fixtures for near-singular, scaled, and boundary-frozen cases.
- Update contract tests before or with implementation so robustness claims are
  executable.
- Persist Step 36 summary and reassess scene corpus expansion.

Exit criteria:

- Numeric robustness improvements are covered by deterministic contract tests.
- Diagnostics receives stable rank/condition evidence for the new cases.

### Step 37: Fixture And Scene Corpus Expansion

Goal:

- Expand reusable model and scene evidence for boundary-frozen,
  rank-deficient, separator, gluing-obstruction, and promotion-positive or
  promotion-negative scenarios.

Expected shape:

- Add reusable fixtures through `gcs.contract_tools` or scene fixture storage.
- Add golden/report digest coverage where stable.
- Avoid leaving one-off validation data outside tests or scene repositories.

Detailed plan:

- Inventory existing contract-tools fixture kinds and scene-generation outputs.
- Add only fixtures that support current or immediately next contract tests.
- Promote generated scenes through public gates when they enter fixture
  storage.
- Persist Step 37 summary and reassess quality gate hardening.

Exit criteria:

- New fixtures are reusable, documented by expectations, and covered by tests.
- Scene corpus supports the next solver/decomposition/diagnostics steps.

### Step 38: Viewer And GUI Evidence Surface

Goal:

- Make rank, residual, gluing, obstruction, conflict, and boundary mismatch
  evidence visible to viewer/GUI consumers through stable viewer-bridge
  contracts.

Expected shape:

- Extend viewer projections or overlays with structured evidence instead of
  prose-only messages.
- Keep Python GUI as a consumer of public viewer/runtime contracts, not a
  solver-truth owner.

Detailed plan:

- Inspect `viewer_bridge`, Python `gcs_viz`, and history/replay UI boundaries.
- Add or refine viewer contract tests before GUI consumption.
- Update Python GUI only if the public bridge contract is ready and the change
  stays small.
- Persist Step 38 summary and reassess CI/quality gates.

Exit criteria:

- Viewer bridge exposes structured evidence that can drive UI without parsing
  free-form text.
- GUI changes, if any, are covered by local behavior or bridge tests.

### Step 39: Quality Gate Hardening

Goal:

- Promote new rank projection, diagnostics, promotion evidence, and scene
  corpus checks into the default quality gate where useful.

Expected shape:

- Add only gates that are deterministic and affordable for the default local
  path.
- Keep slow exploratory generation outside the default gate unless explicitly
  requested.

Detailed plan:

- Inspect `tools\agentic_design\agentic_toolkit.py run-quality-gates` and
  recent test additions.
- Add focused CTest, Python, scene, or report checks that protect the new
  contracts.
- Update `docs/architecture/69-ci-ready-quality-gates.md` if gate behavior
  changes.
- Persist Step 39 summary and reassess atlas synchronization.

Exit criteria:

- Default quality gate catches rank projection, promotion evidence, and corpus
  regressions relevant to Steps 31 through 38.

### Step 40: Architecture Atlas And Roadmap Resynchronization

Goal:

- Resynchronize diagrams, roadmap, and current-progress documents after the
  Step 31 through Step 39 implementation batch.

Expected shape:

- Update Mermaid atlas, Figure 1 if needed, module maturity lens, and roadmap
  status.
- Keep visual/editorial changes separate from solver behavior unless a diagram
  generator needs semantic updates.

Detailed plan:

- Compare implemented module boundaries and evidence paths against the
  architecture atlas and roadmap.
- Regenerate Figure 1 only if the structural/evidence vocabulary changed.
- Archive or summarize the completed Step 31 through Step 39 batch.
- Register the next algorithm batch based on current evidence.

Exit criteria:

- Docs, diagrams, roadmap, and current implementation agree.
- The next batch is registered with clear commit-level steps.

### Post-Step-40 Candidate: Integrated Feature Showcase Constraint Graph

Goal:

- Build a moderately complex constraint graph that demonstrates the completed
  feature chain across decomposition, boundary variables, free/frozen rank
  evidence, diagnostics, promotion gates, viewer projection, and quality gates.

Expected shape:

- A reusable scene or generated-scene promotion package, not a one-off manual
  scratch file.
- Multiple rigid sets and at least one meaningful separator or overlap.
- Boundary-frozen variables that make full/free/frozen rank evidence visible.
- A mix of satisfied constraints, rank/DOF evidence, and at least one optional
  negative variant for gluing obstruction or residual conflict.
- Viewer/atlas-ready projection so the graph can be used as a demonstration
  artifact after Step 40.

Detailed plan:

- Start from the Step 37 fixture/corpus expansion output or generate a new
  candidate through `tools/scene_generation`.
- Promote it through public IO/runtime/diagnostics/viewer gates.
- Add a contract or scene test that checks the showcase graph exercises the
  intended evidence surface.
- Render or document the graph through the viewer/atlas path after Step 40
  completes.

Exit criteria:

- The showcase graph is committed in the fixture/scene corpus with structured
  expectations.
- It demonstrates the Step 31 through Step 40 evidence path without requiring
  private implementation inspection.

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

As of the Step 31-40 planning update:

- Steps 1 through 40 are registered in
  `docs/architecture/66-implementation-execution-roadmap.md`.
- Steps 1 through 30 have completed-step summaries in the roadmap and current
  progress documents.
- Steps 31 through 40 are detailed in this forward plan with goal, expected
  shape, detailed plan, and exit criteria.
- A post-Step-40 candidate is registered for an integrated feature showcase
  constraint graph.
- Step 31 is the next implementation step.

