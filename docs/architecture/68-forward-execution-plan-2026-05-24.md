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

Completion summary:

- The roadmap, current-progress document, forward plan, and Step 1-40 report
  now agree that Steps 1 through 40 are complete.
- The architecture atlas embeds Figure 71 as the Step 1-40
  evidence-boundary reporting figure and documents its deterministic rebuild
  command.
- The Figure 71 generator and layout controls are checked in with the SVG
  asset regenerated from the current report.
- The visual taste guide is part of the architecture index and records the
  durable standard for diagrams, reports, GUI surfaces, and showcase visuals.
- The module maturity lens reflects the implemented L2 public evidence path
  across target modules.

Reassessment after Step 40:

- The Step 1-40 batch is closed.
- The integrated feature showcase constraint graph is now the next
  high-leverage candidate. It should be promoted through the scene or fixture
  corpus with structured expectations and should demonstrate the full public
  evidence chain.

### Step 41: Integrated Feature Showcase Constraint Graph

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

Candidate commit-level slices:

1. Define the showcase graph contract and fixture expectations in
   `gcs.contract_tools`.
2. Carry fixed solve-intent entities into planner/runtime boundary variables.
3. Add positive showcase fixture coverage for decomposition, boundary-frozen
   rank, post-local diagnostics, viewer projection, and corpus summary.
4. Reassess whether JSON scene promotion and a negative diagnostic variant
   should be split into Step 42.
5. Add viewer or atlas projection evidence for reporting and demo use after
   the executable fixture is stable.

Exit criteria:

- The showcase graph is committed in the fixture/scene corpus with structured
  expectations.
- It demonstrates the Step 31 through Step 40 evidence path without requiring
  private implementation inspection.

Completion summary:

- Fixed solve-intent entities now flow into planner subproblem boundary
  variables and therefore into runtime numeric tasks.
- `gcs.contract_tools` exposes a deterministic integrated showcase fixture
  with two local components, a fixed point-distance chain, and mixed
  point/plane/line evidence.
- GTest coverage checks planner boundary propagation, showcase fixture
  provenance, viewer boundary-frozen rank projection, residual evidence, and
  inclusion in the public evidence-chain gate.

Reassessment after Step 41:

- The positive executable C++ showcase path is stable.
- Step 42 should promote this fixture into JSON scene/demo artifacts and add a
  negative diagnostic variant for residual conflict or gluing obstruction.

### Step 42: Showcase Scene Promotion And Negative Variant

Goal:

- Turn the executable showcase fixture into durable scene-facing demo assets.

Expected shape:

- A JSON scene or generated-scene promotion package for the positive showcase.
- A negative variant that demonstrates residual conflict or gluing
  obstruction without breaking the positive path.
- Metadata and tests that make the scene/demo artifacts reproducible.

Detailed plan:

- Decide whether to extend JSON `solve_intent` support or store fixed-boundary
  expectations in companion metadata.
- Produce a positive showcase scene artifact from the C++ fixture or scene
  generation tooling.
- Produce one negative diagnostic variant with structured expectations.
- Add scene or tool tests that load the artifacts and check stable IDs,
  geometry/constraint counts, and expected evidence.
- Add or update atlas/demo projection assets only after the scene artifacts
  are stable.

Execution decision:

- Extend JSON behavior support now. `behavior.fixed_geometry_ids` is the
  durable scene-facing carrier for `ModelSnapshot.solve_intent.fixed_entity_ids`.
- Use companion metadata for provenance, evidence expectations, and demo
  routing only. Metadata must not be the sole place that records solver
  behavior.

Commit-level work items:

- Add JSON read/write support for behavior fields in the C++ IO adapter.
- Add kernel validation report codes for missing fixed/driven entities and
  missing target constraints.
- Add a positive integrated showcase scene and a negative missing-fixed-entity
  variant under `fixtures/scene/showcase/`.
- Add contract tests that load both artifacts and verify stable counts,
  solve-intent IDs, and structured rejection.
- Extend the default quality gate with a showcase CLI smoke and the new
  public scene/IO sentinels.

Exit criteria:

- Showcase scene artifacts are committed with structured metadata.
- Positive and negative variants are both covered by deterministic tests.
- The atlas/demo path can reference the showcase without private C++ fixture
  inspection.

Completion summary:

- JSON scene IO now round-trips `behavior` into
  `ModelSnapshot.solve_intent`.
- Kernel validation now rejects missing or duplicate fixed, driven, and target
  solve-intent references with stable report codes.
- `fixtures/scene/showcase/` contains the positive integrated showcase scene,
  a missing-fixed-entity negative variant, metadata, and a manifest.
- Contract tests cover behavior round-trip, positive scene loading, and
  negative behavior rejection.
- The public evidence-chain gate and CLI smoke path include the showcase scene.

Reassessment after Step 42:

- The public scene assets are stable enough for atlas/demo projection work.
- Rendering should now be driven from the scene file and metadata, not from
  hard-coded graph reconstruction in a documentation script.

### Step 43: Scene-Backed Showcase Atlas And Demo Report

Goal:

- Produce a public showcase projection and report package from the Step 42
  scene assets.

Expected shape:

- A deterministic visualization/report artifact under the architecture atlas
  or showcase fixture directory.
- A small renderer or adapter that reads the public JSON scene/metadata and
  emits an inspectable SVG/Markdown report.
- Contract or tool tests that verify the artifact references the public scene
  IDs and expected evidence.

Detailed plan:

- Inspect the current architecture visualization tool and decide whether to
  extend it or add a dedicated showcase-scene renderer.
- Read `fixtures/scene/showcase/integrated_feature_showcase.gcs.json` and
  metadata as the source of truth.
- Emit a compact scene-backed SVG/report that labels fixed geometry, local
  components, oriented constraints, residual evidence, and the negative
  validation boundary.
- Add Python tool tests or XML/schema checks for deterministic output.
- Update atlas and progress documents, then reassess the next implementation
  step.

Execution decision:

- Add a dedicated showcase-scene renderer. Figure 71 remains the Step 1-40
  evidence-boundary map; Figure 72 should be sourced directly from the public
  showcase JSON scene and metadata.
- Keep the renderer dependency-free and deterministic so it can run inside the
  default quality gate.

Exit criteria:

- The showcase projection can be regenerated from public scene assets.
- The artifact is referenced from the architecture atlas or fixture README.
- Validation covers deterministic rendering and source-scene provenance.

Completion summary:

- Added `tools/architecture_visualization/render_showcase_scene.py` as a
  dependency-free public-scene renderer.
- Generated Figure 72 and the showcase scene report from
  `fixtures/scene/showcase/integrated_feature_showcase.gcs.json` and metadata.
- Updated the architecture atlas with Figure 72, generated assets, source
  files, and rebuild command.
- Added Python renderer tests for scene loading, negative metadata evidence,
  deterministic SVG content, XML validity, and output writing.
- Added the renderer unittest to the default quality gate sequence.

Reassessment after Step 43:

- The showcase can now be inspected without C++ fixture internals.
- Python visualization schema compatibility is now the next risk because
  Python authoring and C++ loading must agree on `gcs-0.3` behavior fields.

### Step 44: Cross-Language Scene Behavior Compatibility

Goal:

- Prove and harden C++/Python agreement for JSON scene behavior intent.

Expected shape:

- Python-side tests for writing `gcs-0.3` scenes with `behavior`.
- C++ or tool-level checks that public JSON scenes use the same field names
  and intent semantics.
- Documentation for legacy `format_version: 1` saved GUI scenes versus current
  `gcs-0.3` public scenes.

Detailed plan:

- Inspect Python `gcs_viz.algebra` serialization and existing saved GUI JSON
  fixtures.
- Add Python tests for `BehaviorModel` and `GCSGraph.to_dict()` using
  `gcs-0.3` format/version fields.
- If feasible, add a small cross-language fixture or report check that
  confirms C++-loadable behavior field names from Python output.
- Update scene behavior documentation and quality gate expectations.
- Reassess whether GUI replay/history migration should become the next step.

Exit criteria:

- Python-authored current scenes preserve fixed, driven, and target behavior
  intent in the same schema consumed by C++.
- Legacy GUI scene status is documented without silently changing its meaning.
- The default quality gate covers the Python scene behavior contract.

Completion summary:

- Added `fixtures/scene/json/python_behavior_roundtrip.gcs.json` as a
  Python-authored-shape current scene with `behavior`, `history`, and
  rigid-set `geometry_ids`.
- Added `IoAdaptersContract.LoadsPythonAuthoredJsonBehaviorScene` to prove C++
  IO maps Python field names into `ModelSnapshot.solve_intent`.
- Added `tests/tools/test_gcs_viz_algebra.py` for current schema emission,
  behavior/history read-write preservation, and legacy saved-scene
  normalization.
- Added `python.gcs_viz_algebra` to the default quality gate.
- Updated scene model documentation and quality-gate docs.

Reassessment after Step 44:

- Current behavior intent is aligned across Python and C++.
- The remaining schema boundary is history: Python owns saved construction and
  replay history today, while C++ IO loads solver structure and behavior but
  does not preserve history in `ModelSnapshot`.

### Step 45: JSON History And Replay Compatibility Policy

Goal:

- Make saved-scene history/replay ownership explicit and testable.

Expected shape:

- Python tests for replaying saved `history` actions from current and legacy
  GUI-authored scenes.
- Documentation that distinguishes solver-owned `behavior` from
  replay-owned `history`.
- Optional C++ IO tests proving history can be tolerated as metadata without
  corrupting solver structure.

Detailed plan:

- Inspect `python/gcs_viz/viewer_bridge.py` replay helpers and saved history
  fixtures.
- Add Python replay tests for `AddRigidSet`, `AddGeometry`, `AddConstraint`,
  `UpdateConstraint`, and `Solve` marker tolerance.
- Document that current C++ `ModelSnapshot` does not persist history and that
  C++ loaders must tolerate history fields as non-solver metadata.
- Add or update a fixture if the existing saved scenes do not cover the needed
  replay actions.
- Reassess whether future C++ history projection support belongs in
  `session_runtime` or a separate IO replay contract.

Exit criteria:

- Python replay reconstructs expected topology from current saved history.
- Legacy saved scenes remain readable and their history policy is explicit.
- The default quality gate covers the replay compatibility contract.

Completion summary:

- Added Python replay tests for prefix reconstruction, construction actions,
  `UpdateConstraint`, non-mutating `Solve` markers, unknown-action rejection,
  and legacy saved-scene replay.
- Made `python/gcs_viz/viewer_bridge.py` lazy-load visualization functions so
  history replay helpers do not require heavy rendering dependencies.
- Added `python.gcs_viz_history_replay` to the default quality gate.
- Updated domain/current-model and quality-gate docs to distinguish
  solver-owned `behavior` from Python-owned scene `history`.

Reassessment after Step 45:

- Scene construction replay is covered on the Python side.
- Runtime command history and scene construction history are still separate
  concepts; their projection boundary should be specified before adding any
  C++ history export.

### Step 46: Runtime Replay Export Boundary

Status: done.

Goal:

- Define how C++ runtime history events relate to scene-embedded construction
  history.

Expected shape:

- A documented boundary between `session_runtime` command history and JSON
  scene `history`.
- Contract tests or tool tests proving runtime history projections do not
  masquerade as scene construction actions.
- A clear path for future replay/export without corrupting saved scenes.

Detailed plan:

- Inspect `src/gcs/session_runtime` history event structures and
  `viewer_bridge` history frame projection.
- Decide whether runtime history export belongs to `session_runtime`,
  `viewer_bridge`, or `io_adapters`.
- Add a contract test that runtime command history is projectable as report
  evidence without writing scene construction `history`.
- Update architecture docs and quality gates if a new public projection is
  introduced.
- Reassess whether UI history replay should consume runtime history frames in
  a later step.

Exit criteria:

- Runtime command history and scene construction history have distinct
  contract names and ownership.
- Tests cover the chosen projection boundary.
- Future export work has a documented owner and non-goal list.

Completed summary:

- `gcs.session_runtime` now names runtime command replay artifacts as
  `ReplayArtifactKind::runtime_transaction_trace`.
- Runtime `HistoryEvent`, `ReplayReport`, and viewer
  `HistoryFrameProjection` outputs mark these artifacts as report evidence and
  not scene construction history entries.
- New `SessionRuntimeContract` and `ViewerBridgeContract` coverage proves
  runtime replay projections do not masquerade as scene `history` actions.
- The public evidence-chain CTest selection includes the replay-boundary
  contract tests.
- Future export work is assigned to runtime/viewer report evidence unless an
  explicit IO migration converts traces into stable scene action payloads.

Reassessment after Step 46:

- Runtime replay and scene replay are now separate public domains.
- The highest-leverage next step is to package runtime replay evidence in a
  deterministic report/export tool so traces can be consumed by diagnostics,
  CLI, or GUI code without corrupting saved scenes.

### Step 47: Runtime Replay Evidence Export Package

Goal:

- Build a deterministic runtime replay evidence export path on top of the
  Step 46 boundary.

Expected shape:

- A structured export contract for command transaction traces, frame
  projections, report codes, state versions, and stage ordering.
- Tooling or CLI-facing report output that can be regenerated deterministically
  from runtime history.
- Tests proving the export contains runtime replay evidence while leaving JSON
  scene `history` untouched.

Detailed plan:

- Inspect existing CLI/report surfaces and choose whether the first export
  belongs in `session_runtime`, `viewer_bridge`, or a test-support/report tool.
- Define a compact structured export DTO that includes command ID, artifact
  kind, report-evidence flag, state-version range, status, and ordered stages.
- Add contract or tool tests for deterministic ordering, missing-command
  handling, and no scene-history writes.
- Update quality-gate sentinels if a new public export test is introduced.
- Reassess whether GUI replay should consume this report export or continue to
  use scene construction `history` for topology reconstruction.

Exit criteria:

- Runtime replay evidence can be exported or summarized deterministically.
- The export contract preserves the Step 46 separation from scene construction
  history.
- The next consumer path, CLI or GUI, is documented with a clear owner.

Completed summary:

- Added `RuntimeReplayEvidenceStage` and `RuntimeReplayEvidenceExport` to
  `gcs.session_runtime`.
- Added `SessionRuntime::export_replay_evidence(ReplayRequest)` as a
  deterministic runtime report export over stored command history.
- The export includes command ID, artifact kind, report-evidence flag,
  scene-history flag, state-version range, command status, commit/rollback
  flags, ordered stages, and stable report codes.
- Missing commands produce a deterministic rejected report with
  `runtime.replay_missing_command`.
- New `SessionRuntimeContract` coverage proves deterministic export behavior
  and preserves the separation from JSON scene `history`.
- The module inventory and target contract design now list
  `RuntimeReplayEvidenceExport` as a session-runtime structured output.

Reassessment after Step 47:

- Runtime replay evidence has a structured in-process export contract.
- The next risk is consumption: CLI, GUI, or report tooling needs a stable way
  to ask for this evidence without turning runtime traces into scene
  construction history.

### Step 48: Runtime Replay Evidence Consumer Path

Goal:

- Connect the deterministic runtime replay evidence export to a consumer-facing
  report path.

Expected shape:

- A CLI, viewer-facing, or report-adapter path that can request the export for
  a command and present stable report evidence.
- Tests proving the consumer path preserves `runtime_transaction_trace` report
  semantics.
- No JSON scene schema or saved-scene `history` behavior change.

Detailed plan:

- Inspect existing CLI, viewer bridge, and report output surfaces.
- Choose the smallest consumer path that exercises
  `SessionRuntime::export_replay_evidence` without adding scene IO ownership.
- Add deterministic output or projection tests for command ID, artifact kind,
  state versions, ordered stages, and report codes.
- Reassess whether GUI replay should consume runtime evidence reports or keep
  using scene construction `history` for topology reconstruction.

Exit criteria:

- A public consumer can observe runtime replay evidence without private runtime
  inspection.
- The consumer path keeps runtime replay reports separate from JSON scene
  construction history.
- Any CLI or viewer output has deterministic contract coverage.

Completed summary:

- Added `ReplayEvidenceSummary` and `ReplayEvidenceStageSummary` to
  `gcs.viewer_bridge`.
- Added `summarize_replay_evidence` and `format_replay_evidence_summary` as a
  read-only report adapter over `RuntimeReplayEvidenceExport`.
- Added `GCS.exe --replay-evidence` so the CLI can print runtime replay
  evidence for the solved command.
- Added `ViewerBridgeContract.ReplayEvidenceSummaryPreservesRuntimeReportBoundary`.
- Extended `ctest.public_evidence_chain` with the replay evidence export and
  summary sentinel tests.
- Added `cli.replay_evidence_basic_scene` to the default quality gate.

Reassessment after Step 48:

- Runtime replay evidence is now observable through a public CLI/report path.
- The path remains runtime/viewer report evidence and does not change scene IO
  or JSON scene `history`.
- The next implementation choice should be made deliberately: GUI-facing
  projection, saved report artifact, or diagnostics integration.

### Step 49: Runtime Replay Evidence Next Consumer Decision

Goal:

- Choose and design the next runtime replay evidence consumer after the CLI
  path has proven stable.

Expected shape:

- A short implementation step that either adds a GUI-facing projection, a saved
  report artifact, or a diagnostics-facing integration.
- Clear non-goals for JSON scene `history` unless an explicit migration is
  chosen.
- Tests proving the new consumer preserves runtime report semantics.

Detailed plan:

- Inspect CLI replay-evidence output and viewer bridge summary tests.
- Decide whether the next consumer is GUI, saved report, or diagnostics based
  on the most useful review workflow.
- Add the smallest consumer contract and focused tests.
- Reassess whether the consumer should join the public evidence-chain quality
  gate.

Exit criteria:

- The next consumer direction is implemented or explicitly deferred with
  rationale.
- Runtime replay reports remain separate from scene construction history.
- The public evidence path remains deterministic.

Completed summary:

- Chose the saved report artifact as the next runtime replay evidence
  consumer.
- Added `ReplayEvidenceReportArtifact` to `gcs.viewer_bridge`.
- Added `build_replay_evidence_report_artifact` and
  `format_replay_evidence_report_json`.
- Added `GCS.exe --save-replay-evidence <path>` for explicit saved report
  workflows.
- Added
  `ViewerBridgeContract.ReplayEvidenceReportArtifactIsDeterministicAndSceneHistoryFree`.
- Extended the public evidence-chain CTest selection and default CLI quality
  gate with the saved replay report artifact path.

Reassessment after Step 49:

- The saved report artifact is useful for review and CI because it is explicit
  and deterministic.
- It remains outside scene IO and does not redefine JSON scene `history`.
- GUI or diagnostics integration should wait until a real review workflow
  needs a richer consumer.

### Step 50: Replay Evidence Report Workflow Review

Goal:

- Decide whether saved replay evidence reports should feed GUI review,
  diagnostics packaging, or remain CLI/report artifacts only.

Expected shape:

- A short review or implementation step based on the saved Step 49 report
  artifact.
- No scene schema or JSON `history` changes unless a separate migration task is
  explicitly approved.

Detailed plan:

- Inspect saved replay evidence report output from representative fixtures.
- Identify whether reviewers need GUI overlay affordances, diagnostics
  packaging, or only a durable report artifact.
- Add the smallest consumer contract if a new public surface is justified.

Exit criteria:

- The next consumer direction is selected with rationale.
- Any added consumer preserves runtime report semantics.
- JSON scene construction history remains separate.

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

As of the Step 49 update:

- Steps 1 through 40 are registered in
  `docs/architecture/66-implementation-execution-roadmap.md`.
- Steps 1 through 49 have completed-step summaries in the roadmap and current
  progress documents.
- Steps 31 through 50 are detailed in this forward plan with goal, expected
  shape, detailed plan, and exit criteria.
- Step 50 is registered as the next runtime replay evidence report workflow
  review step.

