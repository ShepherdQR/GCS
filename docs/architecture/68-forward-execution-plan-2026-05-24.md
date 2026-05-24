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
- Completed through Step 38:
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
  - session runtime now exposes `RankEvidenceProjection` records, and viewer
    overlays/summaries project rank evidence without requiring UI or promotion
    consumers to inspect numeric reports directly;
  - scene-generation promotion gates now consume structured rank evidence from
    public runtime/viewer reports through a dedicated `rank_evidence` gate;
  - decomposition planning now exposes a typed `SolveDag` whose edges explain
    boundary-projection dependencies from local component solves to aggregation
    contexts;
  - session runtime now records post-local-solve diagnostic reports as
    transaction stages and rank projections prefer diagnostics-owned evidence;
  - diagnostics residual conflicts now name both unsatisfied constraints and
    entity subjects, and redundancy evidence now prefers exact duplicate
    constraint signatures before broad over-constrained candidates;
  - numeric convergence now uses max-absolute residual tolerance while
    residual norms remain report evidence, and condition estimates are
    suppressed for singular free-Jacobian evidence;
  - contract-tools fixture corpus now includes reusable boundary-frozen,
    tolerance-edge, and separator-chain fixtures in addition to existing
    redundant, inconsistent, singular, and gluing-obstruction scenarios;
  - viewer bridge overlays and summaries now expose structured residual,
    conflict, redundancy, and obstruction evidence in addition to rank
    evidence;
  - `tools.py` remains the compatibility CLI facade;
  - default quality gate is `python tools\agentic_design\agentic_toolkit.py
    run-quality-gates`;
  - CTest contract baseline is 100 tests.

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

### Completed Step 31: Runtime And Viewer Rank Evidence Projection

Goal:

- Make full/free/frozen rank evidence visible through command summaries,
  viewer overlays, or another public boundary projection without requiring UI
  or promotion tools to inspect numeric internals directly.

Decision:

- Use `session_runtime` as the public projection boundary for this step.
  `runtime::project_rank_evidence` currently builds from existing numeric
  rank-condition reports, while viewer bridge consumes only the runtime
  projection. Step 34 can later switch the projection source to post-local
  diagnostics without changing UI or promotion consumers.

Delivered:

- Add `runtime::RankEvidenceProjection` with local report index, source,
  context ID, result status, full/free/frozen variable dimensions, residual
  dimension, rank, nullity, under/over/singular flags, and condition evidence.
- Add `runtime::project_rank_evidence(const CommandResult&)`.
- Extend `viewer::DiagnosticOverlay` and `viewer::SnapshotSummary` with
  structured rank evidence.
- Add detailed overlay items with code `viewer.rank_evidence` for human-facing
  review while preserving structured fields as the contract source.
- Keep solver math, diagnostics status precedence, transaction semantics, and
  durable state mutation behavior unchanged.

Tests:

- `SessionRuntimeContract.ProjectsRankEvidenceFromAcceptedCommandResult`
  verifies accepted command results expose rank evidence through the runtime
  projection.
- `ViewerBridgeContract.OverlayProjectsBoundaryFrozenRankEvidence` verifies
  full/free/frozen/nullity evidence reaches viewer overlay and command
  summary projections for a boundary-frozen task.
- Focused Session Runtime and Viewer Bridge CTest suites pass.

Reassessment after Step 31:

- Step 32 remains the next highest-leverage move. Promotion gates can now
  consume the public `RankEvidenceProjection` shape instead of inventing a
  private parser over numeric reports.
- Step 34 should remain after Step 33 unless Step 32 exposes a gap that
  requires post-local diagnostics before promotion can validate rank evidence
  robustly.

### Completed Step 32: Promotion Gate Uses Rank Evidence

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

Decision:

- Add an explicit `rank_evidence` gate. This keeps `runtime_smoke` and
  `diagnostics_evidence` semantics stable while making rank proof visible as a
  first-class promotion artifact.
- Treat missing rank evidence in a structured runtime report as `skipped`
  rather than blocking old reports. Treat malformed rank evidence as `failed`
  because supplied evidence must not be accepted if it violates the public
  projection contract.

Delivered:

- Add rank-evidence discovery for public paths such as `rank_evidence`,
  `viewer_overlay.rank_evidence`, `diagnostic_overlay.rank_evidence`,
  `snapshot_summary.rank_evidence`, and `command_summary.rank_evidence`.
- Validate `RankEvidenceProjection` integer fields, boolean flags,
  full/free/frozen dimension consistency, rank bounds, nullity bounds, and
  condition-estimate shape.
- Add a dedicated `rank_evidence` gate with structured evidence, issue lists,
  and stable reason codes.
- Preserve executable smoke fallback when no structured runtime report is
  supplied.

Tests:

- Python scene-generation tests cover structured rank evidence passing through
  promotion gates.
- Python scene-generation tests cover missing rank evidence as a skipped
  non-blocking gate.
- Python scene-generation tests cover malformed rank evidence as a failed
  gate.

Reassessment after Step 32:

- Step 33 is now the next highest-leverage move. Rank evidence is visible at
  runtime, viewer, and promotion boundaries, so planner separator/SolveDAG
  deepening can proceed with a stronger evidence chain.
- Step 34 remains useful after Step 33: runtime should still add post-local
  diagnostics so the rank projection can eventually be backed by diagnostics
  rather than raw numeric reports.

### Completed Step 33: Decomposition Separator And Solve-DAG Deepening

Goal:

- Deepen `gcs.decomposition_planner` from coverage/order validation toward
  stronger separator, boundary projection, and SolveDAG evidence.

Expected shape:

- Strengthen separator detection or articulation/biconnected evidence where it
  directly improves context cover quality.
- Make solve ordering explain boundary dependencies and unsupported plan
  causes.
- Keep planner policy separate from numeric solve iteration.

Decision:

- Deepen the SolveDAG and boundary-dependency evidence first. Incidence-level
  articulation or biconnected separator algorithms remain valuable, but the
  immediate public gap was that component boundary projections had no typed
  dependency graph explaining how local solves feed aggregation.

Delivered:

- Add `SolveDagNode`, `SolveDagEdge`, and `SolveDag` to
  `gcs.decomposition_planner`.
- Extend `PlannerOutput` with `solve_dag`.
- Derive DAG edges directly from `BoundaryProjection` records so component
  subproblems point to the root aggregation context through stable projection
  IDs and boundary subject IDs.
- Add `SolveDagValidationReport` and `validate_solve_dag`.
- Validate DAG node coverage, edge node references, projection-to-cover
  consistency, acyclic topological order, and subproblem coverage.

Tests:

- `DecompositionPlannerContract.SolveDagExplainsBoundaryProjectionDependencies`
  verifies component boundary projections are visible as deterministic DAG
  edges.
- `DecompositionPlannerContract.SolveDagValidationRejectsBackwardDependency`
  verifies backward/cyclic dependency evidence is rejected with a stable report
  code.
- Focused Decomposition Planner CTest suite passes with 9 tests.

Reassessment after Step 33:

- Step 34 is now the highest-leverage next move. Runtime still carries raw
  numeric reports and pre-solve diagnostics, while Step 31 and Step 33 have
  made public projections richer; runtime should now add post-local diagnostic
  evidence as a transaction stage.
- Incidence-level separator or biconnected reports remain queued for a later
  planner/graph batch once post-local diagnostics are in place.

### Completed Step 34: Boundary-Aware Runtime Diagnostics Pass

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

Delivered:

- Add `PostLocalDiagnosticReport` to `gcs.session_runtime`.
- Extend `CommandResult` with `post_local_diagnostics`.
- Run `diagnostics::diagnose` with phase `post_local_solve` after each
  successful local numeric solve.
- Record `post_local_diagnostics` as a transaction stage before gluing.
- Preserve rollback semantics: blocking post-local diagnostic statuses roll
  back before durable commit.
- Update `runtime::project_rank_evidence` so rank projection prefers
  diagnostics-owned post-local rank reports and only falls back to numeric
  reports for older/manual command results.

Tests:

- `SessionRuntimeContract.PostLocalDiagnosticsPreserveNumericEvidence` verifies
  post-local diagnostics preserve numeric residual and rank evidence.
- Existing runtime stage-trace and rank-projection contract tests now cover the
  `post_local_diagnostics` stage and diagnostics-owned rank source.
- Focused Session Runtime CTest suite passes with 7 tests.

Reassessment after Step 34:

- Step 35 was kept as the next highest-leverage move. Runtime now carried
  post-local diagnostic evidence, so diagnostics conflict/redundancy deepening
  could operate on a better public handoff path.
- Viewer and promotion already consume rank projections; they do not need to
  move before the diagnostics conflict/redundancy batch.

### Completed Step 35: Diagnostics Conflict And Redundancy Deepening

Goal:

- Improve diagnostics from broad conflict/redundancy candidates toward smaller
  and more explainable responsible sets.

Expected shape:

- Minimize residual conflicts when evidence allows stable smaller constraint
  sets.
- Improve redundancy evidence for over-constrained contexts without changing
  status precedence accidentally.
- Preserve gluing obstruction conflicts separately from residual conflicts.

Decision:

- Keep status precedence out of redundancy detection for this step. The change
  improves report evidence, while solved/under/over/inconsistent precedence
  remains governed by existing DOF, rank, numeric result, and residual
  evidence.
- Use the existing reusable redundant distance-pair fixture rather than adding
  another ad hoc diagnostics-only model.

Delivered:

- Extend `ConflictSearchRequest` with `ModelSnapshot` so residual conflict
  search can resolve entity subjects from numeric residual blocks.
- Extend `RedundancySearchRequest` with `ModelSnapshot` so redundancy search
  can compare constraint signatures inside the requested context.
- Enrich `diagnostics.residual_conflict` with both constraint IDs and owning
  entity IDs.
- Add deterministic exact duplicate constraint detection and emit
  `diagnostics.redundant_duplicate_distance` for duplicate distance
  signatures.
- Preserve broad `diagnostics.overconstrained_redundancy_candidate` evidence
  when structural or numeric over-constrained reports support it.
- Preserve gluing obstruction conflict evidence separately from residual
  conflicts.

Tests:

- `DiagnosticsContract.PromotesNumericResidualBlocks` now asserts residual
  conflict entity IDs.
- `DiagnosticsContract.RedundancyCandidatesPreferExactDuplicateConstraints`
  covers duplicate distance redundancy with the reusable contract-tools
  fixture.
- Focused diagnostics and contract-tools CTest suites pass.

Reassessment after Step 35:

- Step 36 is now the highest-leverage next move. Diagnostics can name smaller
  responsible sets, so numeric robustness should improve the rank, condition,
  residual, and stopping evidence those reports depend on.
- Step 37 should remain fixture/corpus expansion after Step 36 clarifies which
  numeric edge cases deserve durable reusable fixtures.
- Step 38 remains viewer/GUI evidence surface work after diagnostics and
  numeric evidence contracts settle further.

### Completed Step 36: Numeric Robustness Batch

Goal:

- Harden dense numeric baseline behavior around scaling, rank tolerance,
  condition evidence, stopping criteria, and boundary/frozen-column edge cases.

Expected shape:

- Improve numeric report reliability without adding an external linear algebra
  dependency.
- Preserve `NumericTask`, `NumericReport`, and `RankConditionReport`
  contracts.
- Keep local solve proposals separate from runtime commit decisions.

Decision:

- Keep the public numeric report shapes unchanged and harden interpretation
  first. The highest immediate risk was not a missing solver backend, but
  report semantics that could disagree with diagnostics tolerance handling or
  publish misleading condition evidence for rank-deficient systems.

Delivered:

- Add a max-absolute residual convergence check so multiple residual blocks
  that are each within tolerance do not fail only because the Euclidean norm
  aggregates above tolerance.
- Preserve residual norm as trend evidence in `NumericReport` and
  `IterationTrace`.
- Suppress `condition_estimate_available` when the effective free Jacobian is
  numerically singular.
- Preserve `NumericTask`, `NumericReport`, `RankConditionReport`, and runtime
  commit semantics.

Tests:

- `NumericEngineContract.ConvergesWhenEachResidualIsWithinTolerance` covers
  the tolerated multi-residual stopping criterion.
- `NumericEngineContract.SingularRankDoesNotPublishFiniteConditionEstimate`
  covers rank-deficient condition evidence suppression.
- Focused numeric CTest suite passes with 15 tests.

Reassessment after Step 36:

- Step 37 is now the highest-leverage next move. The solver has stronger
  residual and rank-condition semantics, so reusable fixture and scene corpus
  expansion should capture boundary-frozen, rank-deficient, separator,
  gluing-obstruction, and promotion-positive or promotion-negative scenarios.
- Step 38 should remain viewer/GUI evidence surface work after the corpus gives
  UI and overlay contracts richer public examples.
- Step 39 remains quality gate hardening after new corpus evidence is in place.

### Completed Step 37: Fixture And Scene Corpus Expansion

Goal:

- Expand reusable model and scene evidence for boundary-frozen,
  rank-deficient, separator, gluing-obstruction, and promotion-positive or
  promotion-negative scenarios.

Expected shape:

- Add reusable fixtures through `gcs.contract_tools` or scene fixture storage.
- Add golden/report digest coverage where stable.
- Avoid leaving one-off validation data outside tests or scene repositories.

Decision:

- Expand `gcs.contract_tools` first rather than adding loose scene files. The
  immediate gap was reusable model-level evidence for numeric, diagnostics,
  decomposition, and later viewer contracts; generated-scene promotion can
  build on these fixtures later.

Delivered:

- Add `FixtureKind::boundary_frozen_distance` and fixture class
  `boundary_frozen` with solve-intent fixed entity hints.
- Add `FixtureKind::tolerated_multi_residual_distance` and fixture class
  `tolerance_edge` for max-absolute residual stopping evidence.
- Add `FixtureKind::separator_chain_distance` and fixture class `separator`
  for a three-point chain with a stable shared separator entity.
- Promote the Step 36 tolerated multi-residual model from a numeric-test local
  helper into the public fixture builder.
- Increase the default generated fixture corpus from 10 to 13 bundles.

Tests:

- `ContractToolsContract.BoundaryFrozenFixtureCarriesSolveIntentHint`.
- `ContractToolsContract.ToleratedResidualFixtureExercisesMaxAbsStopping`.
- `ContractToolsContract.SeparatorChainFixtureNamesSharedSeparatorEntity`.
- Focused contract-tools and numeric CTest suites pass.

Reassessment after Step 37:

- Step 38 is now the highest-leverage next move. The corpus now contains
  boundary-frozen, tolerance-edge, separator, redundancy, singular, and gluing
  cases, so viewer and GUI evidence surfaces can be built against public
  examples.
- Step 39 should remain quality gate hardening after viewer evidence surfaces
  settle.
- Step 40 remains atlas and roadmap resynchronization for the close of this
  implementation batch.

### Completed Step 38: Viewer And GUI Evidence Surface

Goal:

- Make rank, residual, gluing, obstruction, conflict, and boundary mismatch
  evidence visible to viewer/GUI consumers through stable viewer-bridge
  contracts.

Expected shape:

- Extend viewer projections or overlays with structured evidence instead of
  prose-only messages.
- Keep Python GUI as a consumer of public viewer/runtime contracts, not a
  solver-truth owner.

Decision:

- Stabilize the C++ viewer bridge contract before touching Python GUI code.
  GUI can consume the structured projection later without becoming a solver
  truth owner.

Delivered:

- Add `ConstraintResidualProjection` and `ResidualEvidenceProjection` for
  post-local residual reports.
- Add `ResponsibilityEvidenceProjection` for conflict, redundancy, and
  obstruction subject sets.
- Extend `DiagnosticOverlay` and `SnapshotSummary` with residual, conflict,
  redundancy, and obstruction evidence arrays.
- Add public projection helpers for residual, conflict, redundancy, and
  obstruction evidence.
- Preserve existing overlay message items and add detailed `viewer.*_evidence`
  items for human-facing review.

Tests:

- `ViewerBridgeContract.OverlayProjectsResidualAndConflictEvidence`.
- `ViewerBridgeContract.OverlayProjectsRedundancyEvidence`.
- `ViewerBridgeContract.OverlayProjectsGluingObstructionEvidence`.
- Focused viewer bridge CTest suite passes with 9 tests.

Reassessment after Step 38:

- Step 39 is now the highest-leverage next move. Rank, diagnostics,
  promotion, corpus, and viewer evidence paths are public, so deterministic
  affordable checks should move into the default quality gate where useful.
- Step 40 remains atlas and roadmap resynchronization after quality gate
  behavior is finalized.

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

Completion summary:

- `run-quality-gates` command construction is now a unit-tested structured
  tools contract.
- The default gate includes `python.agentic_toolkit` for command ordering and
  skip-flag composition.
- The default CTest phase includes `ctest.public_evidence_chain`, a named
  sentinel over numeric rank/residual robustness, diagnostics promotion and
  redundancy evidence, runtime projection evidence, viewer overlay evidence,
  and reusable corpus fixtures.
- The existing full CTest and `ctest.fixture_corpus` gates remain the broad
  and corpus-specific quality boundaries.

Reassessment after Step 39:

- Step 40 is now the only remaining registered step in this batch.
- The architecture atlas, Step 1-40 report, roadmap, and current-progress
  documents should be resynchronized with the hardened gate vocabulary before
  opening the integrated showcase-graph work.

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

As of the Step 39 update:

- Steps 1 through 40 are registered in
  `docs/architecture/66-implementation-execution-roadmap.md`.
- Steps 1 through 39 have completed-step summaries in the roadmap and current
  progress documents.
- Steps 31 through 40 are detailed in this forward plan with goal, expected
  shape, detailed plan, and exit criteria.
- A post-Step-40 candidate is registered for an integrated feature showcase
  constraint graph.
- Step 40 is the next implementation step.

