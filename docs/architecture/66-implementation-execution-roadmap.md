# Implementation Execution Roadmap

## Purpose

This document persists the implementation order for the C++23 module solver
rewrite. It is the working sequence for turning the target architecture into
contract-tested implementation.

## Execution Principles

- Implement from lower mathematical contracts upward.
- Every module exposes strong structured inputs, structured outputs, typed
  reports, and public contract tests before deeper algorithms are added.
- Keep C++23 module interfaces in `.cppm` files and implementations in `.cpp`
  files.
- Keep lower modules independent of IO, viewer, CLI, Python, GUI, and runtime
  application policy.
- Treat contract tests as the executable expression of the architecture.
- Persist each commit-level step plan in this document before or during the
  step, then update the current and next milestone notes before committing.

## Automation Protocol

For each commit-level step:

1. Read the owning module skill and relevant architecture docs.
2. Persist the step plan in this roadmap.
3. Implement only the module-owned contract and its direct tests or reusable
   fixtures.
4. Put durable tests into `tests/contracts/...`; put reusable models into
   public fixture builders or scene fixture storage instead of leaving them as
   ad hoc local validation data.
5. Run build, CTest, representative CLI fixture, docs validation, inventory
   validation, dependency checks, and diff hygiene.
6. Commit and push.
7. Update this roadmap with the completed scope and the next step.

## Ordered Work

1. **Kernel canonical contracts**
   - Own stable IDs, snapshots, contexts, state versions, policies, common
     reports, deltas, and snapshot diffs.
   - Done when kernel contract tests pass and no legacy `gcs::` kernel API is
     required.

2. **Constraint catalog semantics**
   - Own constraint definitions, catalog versioning, entity signatures,
     parameter schemas, residual dimensions, residual evaluators, Jacobian
     contracts, finite-difference checks, generic DOF metadata, and degeneracy
     reports.
   - Done when valid, invalid, residual-shape, Jacobian-check, and degeneracy
     contract tests pass.

3. **Incidence graph structure**
   - Build incidence hypergraphs, reverse indices, rigid-body projections,
     connected components, malformed-edge reports, deterministic graph dumps,
     and separator-oriented structural reports.
   - Done when components cover all entities exactly once and structural
     reports are deterministic.

4. **Decomposition planner**
   - Build topos-inspired covers, context snapshots, overlaps, boundary
     projections, gauge policies, subproblems, solve DAGs, coverage proofs, and
     unsupported-plan evidence.
   - Done when cover validation, solve-order validation, boundary projection,
     and unsupported-case tests pass.

5. **Numeric engine**
   - Validate numeric tasks, assemble equations through the constraint catalog,
     assemble or approximate Jacobians, apply scaling, estimate rank and
     conditioning, produce local sections, and record iteration evidence.
   - Done when zero-residual, missing-ID, under-constrained, boundary-variable,
     and Jacobian-shape tests pass.

6. **Diagnostics and certification**
   - Explain DOF, rank, residuals, conflicts, redundancy, gluing, gauge
     consistency, obstruction reports, and deterministic status precedence.
   - Done when structural and numeric evidence remain distinct and failed
     gluing produces typed obstruction evidence.

7. **Session runtime**
   - Own command validation, transaction isolation, stage traces, atomic
     commit, rollback, history, replay, undo/redo, and post-commit
     verification.
   - Done when rejected commands preserve state and accepted commands advance
     state version exactly once.

8. **IO adapters**
   - Own schema registry, text and JSON scene loading, canonical writing,
     migrations, parse reports, round-trip diffs, and canonical digests.
   - Done when load-write-load tests preserve stable IDs and write output is
     byte deterministic.

9. **Viewer bridge**
   - Own read-only scene projections, report summaries, diagnostic overlays,
     selected-ID mapping, interaction command drafts, and history projections.
   - Done when identical inputs produce identical viewer projections and all
     interaction drafts validate against runtime contracts.

10. **Contract tools and quality gates**
    - Own deterministic fixture generation, invariant checks, golden reports,
      dependency audits, fixture provenance, and CI-ready contract suites.
    - Done when dependency gates, negative fixture corpora, and golden report
      tooling are executable from public contracts.

## Current Bootstrap State

- `gcs.kernel` is canonical.
- Existing upper modules compile against `gcs::kernel` contracts.
- Bootstrap contract suites:
  - `tests/contracts/kernel/kernel_contract_tests.cpp`
  - `tests/contracts/constraint_catalog/constraint_catalog_contract_tests.cpp`
  - `tests/contracts/pipeline/pipeline_contract_tests.cpp`
  - `tests/contracts/incidence_graph/incidence_graph_contract_tests.cpp`
  - `tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp`
  - `tests/contracts/numeric_engine/numeric_engine_contract_tests.cpp`
  - `tests/contracts/diagnostics/diagnostics_contract_tests.cpp`
  - `tests/contracts/session_runtime/session_runtime_contract_tests.cpp`
  - `tests/contracts/io_adapters/io_adapters_contract_tests.cpp`
  - `tests/contracts/viewer_bridge/viewer_bridge_contract_tests.cpp`

## Commit-Level Step Queue

Status legend: `done`, `in_progress`, `pending`.

1. `done` - canonicalize `gcs.kernel` and migrate upper modules.
2. `done` - deepen `gcs.constraint_catalog` contracts and tests.
3. `done` - upgrade `gcs.incidence_graph` to hypergraph, reverse
   indices, rigid-body graph, malformed-edge reports, canonical graph dumps,
   reusable fixture builders, and incidence contract tests.
4. `done` - validate and enrich `gcs.decomposition_planner` cover plans,
   boundary projections, coverage proof, solve order, and planner contract
   tests.
5. `done` - add numeric task validation and equation assembly through the
   constraint catalog.
6. `done` - add numeric residual/Jacobian/rank reports and baseline local
   solve tests.
7. `done` - add diagnostics DOF/rank/residual/status precedence
   contracts.
8. `done` - add projection-aware gluing obstruction and
   conflict/redundancy diagnostics.
9. `done` - harden session runtime transaction, rollback, stage trace, and
   replay contracts.
10. `done` - add IO schema registry, canonical text/JSON path, parse
    reports, round-trip diff, and fixture tests.
11. `done` - add viewer projection, diagnostic overlay, interaction draft,
    and history projection contracts.
12. `in_progress` - split and harden contract tools: fixture provenance,
    invariant checks, dependency audits, golden reports.
13. `pending` - add cross-module quality gates and broader negative fixture
    corpus.

## Constraint Catalog Milestone

Implemented scope for the constraint catalog semantics milestone:

- `ConstraintCatalog` and catalog version.
- `ConstraintDefinition` with entity signature and scalar parameter schema.
- Structured `ConstraintValidationReport`.
- `ResidualEvaluationRequest` and `ResidualEvaluationResult`.
- `JacobianEvaluationRequest` and `JacobianEvaluationResult`.
- `DegeneracyProbeRequest` and `DegeneracyReport`.
- `FiniteDifferenceCheckRequest` and `JacobianCheckReport`.
- `tests/contracts/constraint_catalog/constraint_catalog_contract_tests.cpp`.

## Incidence Graph Milestone

Implemented scope for the incidence graph structure milestone:

- `IncidenceHypergraph` and deterministic hyperedge IDs.
- Entity and constraint reverse indices.
- Rigid-set/body graph projection.
- Connected-component coverage proof.
- Malformed edge quarantine reports.
- Canonical graph dump.
- Reusable graph fixture builders in the model/test support surface.
- `tests/contracts/incidence_graph/incidence_graph_contract_tests.cpp`.

## Decomposition Planner Milestone

Implemented scope for the decomposition planner milestone:

- `CoverValidationReport` and cover coverage proof.
- Component-to-root boundary projection construction.
- Explicit solve-order validation.
- Planner unsupported-case report carrier.
- Planner contract tests under
  `tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp`.

## Next Milestone

Implement the numeric task validation and equation assembly milestone:

- `NumericTaskValidationReport`.
- `EquationAssembly` built through `gcs.constraint_catalog`.
- Per-constraint residual blocks and Jacobian shape reports.
- Missing active entity/constraint negative tests.
- Boundary-variable immutability checks.
- Numeric contract tests under
  `tests/contracts/numeric_engine/numeric_engine_contract_tests.cpp`.

## Numeric Assembly Milestone

Implemented scope for the numeric task validation and equation assembly
milestone:

- Add `NumericTaskValidationReport` and validate active variables, active
  equations, context membership, boundary variables, solve limits, tolerances,
  and state-version alignment.
- Add `EquationAssembly` with variable ordering, residual ordering, residual
  vector, per-constraint residual blocks, and dimension totals.
- Assemble residuals through `gcs.constraint_catalog`, preserving typed report
  evidence from the catalog.
- Keep `solve_local` as a non-iterating baseline local-section producer, but
  make it consume task validation and equation assembly evidence.
- Add `tests/contracts/numeric_engine/numeric_engine_contract_tests.cpp` with
  valid assembly, missing entity, missing constraint, boundary-variable, and
  identity-solve evidence tests.

## Numeric Report Milestone Target

Implement the numeric report and baseline local solve milestone:

- Per-constraint residual reports in `NumericReport`.
- Jacobian block-shape report in `EquationAssembly`.
- Rank and condition report fields with deterministic estimates.
- Boundary variable non-mutation evidence.
- Replayable iteration trace summary for the baseline solve.

## Numeric Report Step Plan

Current commit-level scope:

- Extend `gcs.numeric_engine` public contracts with residual, Jacobian,
  rank/condition, boundary, and iteration trace report structures.
- Assemble Jacobian blocks through `gcs.constraint_catalog` and map them into
  the active-variable column order declared by `NumericTask`.
- Estimate rank and conditioning deterministically from the assembled Jacobian
  without introducing a solver backend dependency.
- Keep the baseline local solve non-iterating, but make its report replayable:
  initial residual, final residual, step norm, accepted flag, and local section
  provenance must be visible in structured output.
- Add contract tests for Jacobian dimensions, rank/condition evidence,
  boundary non-mutation, and trace replayability under
  `tests/contracts/numeric_engine/numeric_engine_contract_tests.cpp`.

## Numeric Report Milestone

Implemented scope for the numeric report and baseline local solve milestone:

- Add structured `ResidualReport`, `JacobianReport`, `RankConditionReport`,
  `BoundaryVariableReport`, and `IterationTrace` carriers to
  `gcs.numeric_engine`.
- Assemble finite-difference Jacobian blocks through `gcs.constraint_catalog`
  and scatter them into the active-variable column order declared by
  `NumericTask`.
- Estimate rank, nullity, under-constrained evidence, singular evidence, and
  condition evidence deterministically from the assembled Jacobian.
- Preserve the baseline identity local section while reporting initial/final
  residuals, per-constraint residual metrics, boundary non-mutation, and a
  replayable trace.
- Add `make_unsatisfied_two_point_distance_model` to `gcs.contract_tools` as a
  reusable negative residual fixture.
- Extend `tests/contracts/numeric_engine/numeric_engine_contract_tests.cpp`
  with Jacobian shape, nonzero residual metric, rank/condition, boundary, and
  trace assertions.

## Next Milestone

Implement the diagnostics DOF/rank/residual/status precedence milestone:

- Promote numeric residual blocks into diagnostic residual analysis.
- Keep structural DOF, structural rank, and numeric rank as distinct evidence.
- Add deterministic status precedence across invalid, inconsistent,
  singular, under-constrained, over-constrained, warning, and solved states.
- Add conflict/redundancy placeholders that are typed now and algorithmically
  deepened in the following diagnostics step.
- Add diagnostics contract tests under
  `tests/contracts/diagnostics/diagnostics_contract_tests.cpp`.

## Diagnostics Certification Step Plan

Current commit-level scope:

- Extend `gcs.diagnostics` with explicit diagnostic phases, DOF requests,
  residual analysis requests, status precedence inputs, and typed precedence
  traces.
- Preserve structural and numeric evidence as separate fields: structural DOF
  and rank come from model/context shape, while numeric rank, nullity,
  condition, and residual blocks come from `NumericReport`.
- Resolve final diagnostic status through a deterministic precedence function
  instead of incidental branch order.
- Add typed `ConflictSet` and `RedundancySet` placeholders so later
  certification algorithms can fill stable subject IDs without reshaping the
  public contract.
- Add `tests/contracts/diagnostics/diagnostics_contract_tests.cpp` and keep the
  tests focused on public structured reports.

## Diagnostics Certification Milestone

Implemented scope for the diagnostics DOF/rank/residual/status precedence
milestone:

- Add `DiagnosticPhase`, `DofAnalysisRequest`, `ResidualAnalysisRequest`,
  `StatusPrecedenceInput`, and `StatusPrecedenceTrace` to `gcs.diagnostics`.
- Reconcile structural DOF/rank separately from numeric rank, nullity,
  singularity, condition evidence, and residual blocks.
- Promote numeric residual blocks into `diagnostics::ResidualReport` and mark
  unsatisfied constraints without hiding the source numeric report.
- Resolve final diagnostic status through deterministic precedence evidence
  instead of incidental branch order.
- Add typed `ConflictSet` and `RedundancySet` placeholders for the next
  certification algorithms.
- Add `tests/contracts/diagnostics/diagnostics_contract_tests.cpp` and the
  `gcs_diagnostics_contract_tests` CTest target.

## Next Milestone

Implement the projection-aware gluing obstruction milestone:

- Compare local sections through declared `BoundaryProjection` records instead
  of only merging duplicate entity states.
- Produce `BoundaryAgreementReport` evidence per projection.
- Return typed obstruction reports with smallest known projection, context,
  entity, and constraint subjects when gluing fails.
- Populate conflict/redundancy placeholder structures for projection-level
  failures where possible.
- Extend diagnostics contract tests for compatible overlaps, mismatched
  overlap projections, and stable obstruction subject IDs.

## Projection-Aware Gluing Step Plan

Current commit-level scope:

- Extend `gcs.diagnostics` gluing contracts with per-projection
  `BoundaryAgreementReport` evidence.
- Compare local sections through declared `BoundaryProjection` records,
  including source/target context IDs, projected entity IDs, projected
  constraint IDs, boundary residuals, and compatibility.
- Keep existing duplicate-state merge checks, but report projection failures as
  typed obstructions with stable projection, context, entity, and constraint
  subjects.
- Populate gluing-level conflict placeholders for boundary mismatches so the
  next diagnostics step can minimize conflict sets without changing contracts.
- Add contract tests for compatible projected overlaps and mismatched projected
  overlaps under `tests/contracts/diagnostics/diagnostics_contract_tests.cpp`.

## Projection-Aware Gluing Milestone

Implemented scope for the projection-aware gluing obstruction milestone:

- Add `BoundaryAgreementReport` to `gcs.diagnostics` and attach per-projection
  evidence to `GluingReport`.
- Extend `OverlapStatus` with source and target context IDs.
- Add projection IDs to `ObstructionReport` so failed gluing can name the
  concrete boundary projection that failed.
- Compare local sections through declared `BoundaryProjection` records and
  compute boundary residuals per projected overlap.
- Return `gluing.boundary_projection_mismatch` with projection, context,
  entity, and constraint subjects when a projected overlap fails.
- Populate gluing-level `ConflictSet` evidence for boundary mismatches.
- Extend diagnostics contract tests with compatible and mismatched projection
  scenarios.

## Next Milestone

Implement the session runtime transaction and replay milestone:

- Introduce runtime command precondition reports and transaction traces.
- Ensure rejected commands preserve state and accepted commands advance state
  version exactly once.
- Record stage traces with pre-solve, planner, numeric, diagnostics, gluing,
  commit, and rollback phases.
- Add history and replay skeletons based on public command/result contracts.
- Add session runtime contract tests under
  `tests/contracts/session_runtime/session_runtime_contract_tests.cpp`.

## Session Runtime Transaction Step Plan

Current commit-level scope:

- Extend `gcs.session_runtime` with command validation, transaction trace,
  rollback report, history event, and replay report structures.
- Run commands against an isolated transaction snapshot; mutate durable
  `current_snapshot_` only at the commit gate after numeric solving and gluing
  have accepted.
- Record a deterministic stage trace for command validation, model validation,
  incidence indexing, planning, pre-solve diagnostics, numeric solves, gluing,
  commit, and rollback.
- Preserve command history as public replay data and provide a replay query by
  `CommandId`.
- Add contract tests under
  `tests/contracts/session_runtime/session_runtime_contract_tests.cpp` for
  invalid command rollback, accepted command version advancement, stage trace
  completeness, and replay.

## Session Runtime Transaction Milestone

Implemented scope for the session runtime transaction and replay milestone:

- Add `CommandValidationReport`, `StageTraceEntry`, `TransactionTrace`,
  `RollbackReport`, `HistoryEvent`, `ReplayRequest`, and `ReplayReport` to
  `gcs.session_runtime`.
- Refactor command execution to use an isolated transaction snapshot and commit
  to durable `current_snapshot_` only after validated planning, numeric
  solving, diagnostics, and gluing acceptance.
- Record deterministic stage trace entries for command validation, model
  validation, incidence indexing, planning, pre-solve diagnostics, numeric
  solves, gluing, commit, and rollback.
- Preserve command history with transaction traces and expose replay by
  `CommandId`.
- Add `tests/contracts/session_runtime/session_runtime_contract_tests.cpp` and
  the `gcs_session_runtime_contract_tests` CTest target.

## Next Milestone

Implement the IO schema registry and canonical round-trip milestone:

- Add explicit scene schema registry and format/version metadata.
- Return structured parse and validation reports rather than string-only load
  failures.
- Provide canonical text and JSON write paths with deterministic digests.
- Add round-trip diff reports for load-write-load fixture checks.
- Add IO adapter contract tests under
  `tests/contracts/io_adapters/io_adapters_contract_tests.cpp`.

## IO Adapter Schema Step Plan

Current commit-level scope:

- Extend `gcs.io_adapters` with scene format metadata, schema registry
  descriptors, typed parse issues, validation reports, migration reports,
  canonical digests, and round-trip diff reports.
- Preserve the legacy text scene format and route the writer through one
  deterministic canonical text serializer.
- Add a deterministic canonical JSON serializer path without adding a JSON
  dependency; JSON loading can remain explicitly unsupported until the migration
  parser milestone.
- Report unsupported JSON loading through typed parse issues instead of
  string-only errors.
- Add contract tests under
  `tests/contracts/io_adapters/io_adapters_contract_tests.cpp` for current text
  fixture loading, JSON rejection evidence, byte determinism, digest stability,
  and load-write-load equivalence.

## IO Adapter Schema Milestone

Implemented scope for the IO schema registry and canonical round-trip
milestone:

- Add `SceneFormat`, `CompatibilityMode`, `SceneSchemaDescriptor`,
  `SceneSchemaRegistry`, `ParseIssue`, `SceneValidationReport`,
  `SceneMigrationReport`, `CanonicalDigest`, and `RoundTripDiffReport` to
  `gcs.io_adapters`.
- Preserve legacy text scene loading while reporting parse and schema failures
  through typed `ParseIssue` records.
- Route text writing through deterministic `canonical_text` serialization and
  expose deterministic `canonical_json` serialization without adding a C++ JSON
  dependency.
- Add stable FNV-1a canonical digests for serialized scene bytes.
- Add in-memory text round-trip diff checks that preserve stable entity and
  constraint IDs.
- Add `tests/contracts/io_adapters/io_adapters_contract_tests.cpp` and the
  `gcs_io_adapters_contract_tests` CTest target.

## Next Milestone

Implement the viewer bridge projection and interaction contract milestone:

- Add read-only scene projection contracts with state version, entity,
  constraint, and context summaries.
- Project diagnostic overlays from command results, including obstruction,
  residual, boundary, and status evidence.
- Add interaction command draft validation against runtime command contracts.
- Add history frame projection from runtime history and replay traces.
- Add viewer bridge contract tests under
  `tests/contracts/viewer_bridge/viewer_bridge_contract_tests.cpp`.

## Viewer Bridge Projection Step Plan

Current commit-level scope:

- Extend `gcs.viewer_bridge` with read-only scene projection, diagnostic
  overlay, interaction command draft, and history frame projection contracts.
- Project stable IDs, state version, entity parameters, constraints, selected
  IDs, and status without mutating solver state.
- Derive overlay status and messages from `CommandResult`, stage reports, and
  obstruction reports only.
- Draft solve interactions as `runtime::Command` values and validate them
  through `runtime::validate_command`.
- Add contract tests under
  `tests/contracts/viewer_bridge/viewer_bridge_contract_tests.cpp` for
  deterministic projection, state version, overlay mapping, command draft
  validity, and history frame stage resolution.

## Viewer Bridge Projection Milestone

Implemented scope for the viewer bridge projection and interaction milestone:

- Add `ViewerProjectionRequest`, `ViewerSceneProjection`,
  `DiagnosticOverlayRequest`, `DiagnosticOverlay`, `InteractionDraftRequest`,
  `InteractionCommandDraft`, `HistoryFrameRequest`, and
  `HistoryFrameProjection` to `gcs.viewer_bridge`.
- Project model schema, state version, stable entity IDs, constraint IDs,
  selected IDs, parameters, and counts without mutating solver state.
- Derive diagnostic overlays from `CommandResult`, stage reports, and
  obstruction reports.
- Draft solve interactions as `runtime::Command` values and validate them
  through `runtime::validate_command`.
- Project runtime history events into read-only history frames.
- Add `tests/contracts/viewer_bridge/viewer_bridge_contract_tests.cpp` and the
  `gcs_viewer_bridge_contract_tests` CTest target.

## Next Milestone

Implement the contract tools and quality gate milestone:

- Add fixture provenance metadata to reusable fixture builders.
- Add invariant check reports over model validity, context coverage, dependency
  boundaries, and deterministic serialization.
- Add golden report or digest writer contracts for stable test artifacts.
- Promote module dependency audit outputs into C++/script quality gates.
- Add contract tools tests under
  `tests/contracts/contract_tools/contract_tools_contract_tests.cpp` and
  module dependency tests under
  `tests/contracts/module_dependency/module_dependency_contract_tests.cpp`.

## Decomposition Planner Step Plan

Current commit-level scope:

- Extend `gcs.decomposition_planner` with `CoverValidationReport`,
  `SolveOrderValidationReport`, and `UnsupportedPlanReport`.
- Validate that cover contexts reference existing entities, constraints, and
  rigid sets.
- Validate that every model entity and constraint is covered by at least one
  context.
- Emit component-to-root boundary projections for connected-component covers.
- Validate that solve-order entries are deterministic, strictly ordered, and
  point at known subproblem contexts.
- Add reusable assertions through
  `tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp`.
