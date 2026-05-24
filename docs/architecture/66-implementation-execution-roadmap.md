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
  - `tests/contracts/contract_tools/contract_tools_contract_tests.cpp`
  - `tests/contracts/module_dependency/module_dependency_contract_tests.cpp`
  - `tests/contracts/quality/cross_module_quality_contract_tests.cpp`

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
12. `done` - split and harden contract tools: fixture provenance,
    invariant checks, dependency audits, golden reports.
13. `done` - add cross-module quality gates and broader negative fixture
    corpus.
14. `done` - replace numeric identity local solve with a dense damped
    Gauss-Newton baseline while preserving numeric report contracts.
15. `done` - add JSON scene reader, schema migration report, JSON round-trip,
    and malformed JSON negative corpus.
16. `done` - promote diagnostics conflict and redundancy candidates from typed
    placeholders into public contract tools.
17. `done` - expand reusable fixture corpus and golden report digests.
18. `done` - promote contract, dependency, fixture, scene, and CLI checks into
    CI-ready quality gates.
19. `done` - connect scene auto explorer promotion packages to public IO,
    kernel, runtime, diagnostics, and viewer gate adapters.
20. `done` - start the scene-generation package split by extracting
    contracts, storage, and public promotion adapters from the CLI facade.
21. `done` - continue the scene-generation package split by extracting
    topology and GCS model helpers while preserving manual generation flow.
22. `done` - extract scene-generation validation and projection helpers with
    focused structured contract tests.
23. `done` - extract scene-generation parameterization and reporting helpers
    with deterministic structured tests.
24. `done` - extract scene-generation repair policy with structured edit-list
    tests.
25. `done` - split scene-generation explorer and promotion orchestration
    from the CLI facade.
26. `done` - contain scene-generation flat store access behind a store
    adapter.
27. `done` - harden promotion public gates from executable smoke toward
    direct public adapters.
28. `done` - reassess and resume solver algorithm deepening in the highest
    leverage C++ module.
29. `done` - synchronize the architecture atlas and tracked visualization
    assets with the current module state.
30. `done` - propagate numeric free/frozen rank dimensions through
    diagnostics rank evidence.
31. `done` - expose preserved rank evidence through runtime/viewer
    projection contracts.
32. `done` - make scene-generation promotion gates consume structured rank
    evidence from public reports.
33. `done` - deepen decomposition separator, boundary projection, and
    SolveDAG evidence.
34. `done` - add boundary-aware post-local-solve diagnostics to session
    runtime command results.
35. `done` - deepen diagnostics conflict and redundancy evidence toward
    smaller responsible sets.
36. `done` - harden numeric robustness around scaling, rank tolerance,
    condition evidence, stopping, and boundary edge cases.
37. `done` - expand reusable fixture and scene corpus for rank, separator,
    boundary, gluing, and promotion scenarios.
38. `done` - expose structured evidence through viewer bridge and GUI
    surfaces.
39. `done` - harden default quality gates for the new rank, promotion, and
    corpus evidence paths.
40. `done` - resynchronize architecture atlas, roadmap, and next-batch
    planning after Steps 31 through 39.
41. `done` - build the integrated feature showcase constraint graph
    as a reusable contract fixture with decomposition, boundary, rank,
    diagnostics, viewer, and quality evidence.
42. `done` - promote the showcase into durable JSON scene artifacts,
    negative diagnostic variants, and atlas/demo-ready metadata.
43. `done` - build the scene-backed showcase atlas/demo projection and
    public report package from the Step 42 scene assets.
44. `done` - harden cross-language JSON scene behavior round-trip between
    C++ IO and Python visualization schemas.
45. `pending` - define and test JSON history/replay compatibility policy for
    current and legacy GUI-authored scenes.

Next registered candidate:

- Complete Step 45 by making saved-scene history/replay compatibility explicit
  across Python GUI authoring, Python replay, and C++ IO boundaries.

Forward plan: `docs/architecture/68-forward-execution-plan-2026-05-24.md`.

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

## Contract Tools Quality Gate Step Plan

Current commit-level scope:

- Extend `gcs.contract_tools` with typed fixture build, invariant check,
  golden report, and dependency audit request/report structures.
- Attach deterministic fixture provenance to reusable model builders, including
  fixture ID, generator name, seed, and schema version.
- Check invariants through public `kernel` validation and context contracts
  only.
- Produce deterministic golden report digests for fixture bundles without
  adding production solver policy.
- Add C++ contract tests for fixture determinism, generated fixture validation,
  invariant failure reports, and forbidden dependency detection.

## Contract Tools Quality Gate Milestone

Implemented scope for the contract tools and module dependency milestone:

- Add `FixtureBuildRequest`, `FixtureProvenance`, `FixtureBundle`,
  `InvariantCheckRequest`, `InvariantReport`, `GoldenReportRequest`,
  `GoldenReport`, `DependencyAuditRequest`, and `DependencyAuditReport` to
  `gcs.contract_tools`.
- Attach fixture ID, generator name, deterministic seed, and schema version to
  reusable fixture bundles.
- Check model/context invariants through public `kernel` contracts.
- Produce deterministic golden report digests from fixture provenance and
  structural counts.
- Add dependency audit rules that reject lower solver modules importing
  runtime, IO, or viewer boundaries.
- Add `tests/contracts/contract_tools/contract_tools_contract_tests.cpp`,
  `tests/contracts/module_dependency/module_dependency_contract_tests.cpp`,
  and their CTest targets.

## Next Milestone

Implement the cross-module quality gate and negative corpus milestone:

- Promote broader negative fixtures for invalid schema, missing IDs,
  unsupported IO, gluing obstruction, and invalid runtime commands.
- Add cross-module contract tests that assert end-to-end report codes and
  state-version behavior across kernel, IO, runtime, diagnostics, and viewer.
- Add golden digest checks for representative command results and scene
  round-trips.
- Keep all scenario data in reusable fixture builders or `fixtures/scene`
  rather than ad hoc test-local models.
- Close the first implementation roadmap batch with a quality summary in this
  document.

## Cross-Module Quality Gate Step Plan

Implemented commit-level scope:

- Add a dedicated cross-module contract suite that exercises reusable negative
  fixtures through public IO, runtime, diagnostics, viewer, and contract-tool
  APIs.
- Assert stable report codes and state-version behavior for invalid models,
  unsupported scene formats, gluing obstructions, and accepted round trips.
- Use `gcs.contract_tools` fixture provenance instead of test-local ad hoc
  model construction wherever possible.
- Register the suite as a CTest quality gate and record it in the bootstrap
  contract suite inventory.
- Close the first roadmap batch with a concise implementation quality summary.

## Cross-Module Quality Gate Milestone

Implemented scope for the cross-module quality gate and negative corpus
milestone:

- Add `tests/contracts/quality/cross_module_quality_contract_tests.cpp` and
  the `gcs_cross_module_quality_contract_tests` CTest target.
- Verify invalid model rollback propagates the stable
  `kernel.missing_entity` report code from kernel validation through session
  runtime stage reports without advancing state version.
- Strengthen `gcs.session_runtime` so execution runs kernel model validation
  before constraint catalog validation, then records a separate
  `constraint_validation` stage for catalog-specific failures.
- Verify unsupported JSON scene loading reports typed
  `io.schema.unsupported_read` parse evidence.
- Verify projection-aware gluing obstruction evidence flows into viewer
  diagnostic overlays as `gluing.boundary_projection_mismatch`.
- Verify canonical text round-trip, accepted runtime solve, and viewer
  projection all agree on stable IDs and state version.
- Verify negative fixture provenance is attached to invariant reports through
  `gcs.contract_tools`.

## First Implementation Batch Summary

The first commit-level implementation batch is complete. It established
contract-tested C++23 module skeletons from kernel through constraint catalog,
incidence graph, decomposition planner, numeric engine, diagnostics, session
runtime, IO adapters, viewer bridge, contract tools, dependency audits, and
cross-module quality gates.

Second algorithm-deepening batch queue:

- `done` - Replace baseline numeric local solve with an iterative damped solve while
  preserving residual, Jacobian, rank, boundary, and trace contracts.
- `done` - Add a real JSON parser and migration pipeline behind the existing IO schema
  and parse-report contracts.
- `done` - Deepen diagnostics conflict/redundancy minimization behind the existing
  typed conflict, redundancy, obstruction, and status-precedence contracts.
- `done` - Expand reusable negative, singular, redundant, inconsistent, and migration
  fixture corpora with golden report digests.
- `done` - Promote contract, dependency, fixture, and scene checks into CI-ready quality
  gates.

## CI-Ready Quality Gate Step Plan

Implemented commit-level scope:

- Add `run-quality-gates` to `tools/agentic_design/agentic_toolkit.py` as the
  single pre-push and CI entry point.
- Include agentic documentation validation, inventory validation, skill
  validation, and C++23 module dependency checks in the default gate.
- Include Python scene-generation explorer tests in the default gate so scene
  search and promotion evidence do not drift outside CTest.
- Include CMake configure/build, full CTest, explicit `ContractToolsContract`
  fixture-corpus tests, and a representative CLI smoke fixture.
- Add `scripts/run_quality_gates.cmd` and `scripts/run_quality_gates.ps1`
  wrappers for local Windows use.
- Document the quality gate contract in
  `docs/architecture/69-ci-ready-quality-gates.md`.

## CI-Ready Quality Gate Milestone

Implemented scope for Step 18:

- The repository now has one deterministic quality-gate command:
  `python tools\agentic_design\agentic_toolkit.py run-quality-gates`.
- The command reports each gate with stable IDs, durations, exit codes, and a
  final pass/fail summary.
- The gate stops on first failure by default and supports
  `--continue-on-failure` for CI diagnostics.
- Split-job and debug usage can skip agentic, Python, build, CTest, or CLI
  gates explicitly, while the default remains the merge-quality path.

## Scene Promotion Public Gate Step Plan

Implemented commit-level scope:

- Convert generated GCS candidate graphs into public `gcs-0.3` scene JSON
  artifacts during promotion.
- Replace unsupported promotion placeholders with concrete gate records for
  scene IO round trip, kernel-shape validation, runtime smoke,
  diagnostics-output evidence, and viewer projection.
- Allow tests and CI to inject `public_gate_config.solver_command` while local
  use defaults to `GCS_EXE` or `out/build/clang-ninja/GCS.exe`.
- Write `public_scene.gcs.json` into promotion packages and copy that public
  scene into fixtures when fixture promotion is requested.
- Extend scene-generation tests with deterministic fake-solver promotion
  checks so public adapter behavior remains covered without requiring a local
  C++ build inside the Python unit test.

## Scene Promotion Public Gate Milestone

Implemented scope for Step 19:

- `promote_candidate` can now produce promotion packages with all public gates
  passing when a solver command is available.
- Missing solver commands are explicit runtime/diagnostic gate evidence instead
  of generic unsupported placeholders.
- Promotion packages now carry both the generator-native `scene.json` and the
  solver-facing `public_scene.gcs.json`.

## Scene Generation Package Split Step Plan

Implemented commit-level scope:

- Keep `tools/scene_generation/tools.py` as the CLI facade and compatibility
  command registry.
- Add `gcs_scene_generation.contracts` for generated graph constants, public
  type maps, signature validation, and shared failure taxonomy.
- Add `gcs_scene_generation.storage` for safe IDs, deterministic JSON IO,
  scratch-store paths, trace append, and digest helpers.
- Add `gcs_scene_generation.promotion` for public `gcs-0.3` scene conversion,
  public kernel-shape validation, solver command normalization, and runtime
  smoke execution.
- Add package-boundary unit coverage so the split is validated through
  structured inputs and outputs rather than only through file placement.

## Scene Generation Package Split Milestone

Implemented scope for Step 20:

- The monolithic scene-generation file no longer owns the stable contracts,
  storage, or public promotion adapter logic directly.
- Existing CLI commands and tests remain compatible through facade wrappers.
- The remaining split target is now narrower: topology, GCS lift, validation,
  projection, parameterization, reporting, and explorer orchestration.

## Scene Generation Topology/Model Split Step Plan

Implemented commit-level scope:

- Add `gcs_scene_generation.topology` for deterministic edge
  canonicalization, adjacency, connected components, and Tarjan
  articulation/biconnected-component evidence.
- Add `gcs_scene_generation.gcs_model` for geometry-primal edge derivation,
  rigid-set rebuilding, geometry maps, rigid-set invariant checks, graph
  coloring, and rigid-set assignment.
- Keep `tools.py` as the CLI facade with compatibility wrappers for the moved
  helpers.
- Add a manual generation-path test covering generate, lift, parameterize,
  validate, project, and biconnectivity after the split.

## Scene Generation Topology/Model Split Milestone

Implemented scope for Step 21:

- Topology algorithms no longer live directly in the CLI facade.
- GCS rigid-set/model helper logic no longer lives directly in the CLI facade.
- The remaining split target is validation, projection, parameterization,
  reporting, and explorer orchestration.

## Scene Generation Validation/Projection Split Step Plan

Implemented commit-level scope:

- Add `gcs_scene_generation.validation` for generator-local schema validation:
  IDs, references, signatures, arity, degeneracy, scalar ranges, and rigid-set
  memberships.
- Add `gcs_scene_generation.projection` for geometry-primal,
  incidence-bipartite, and rigid-set quotient projection builders.
- Keep `tools.py` as the CLI facade with compatibility wrappers around the
  moved validation and projection helpers.
- Add focused tests for invalid signature evidence and projection shape
  contracts.

## Scene Generation Validation/Projection Split Milestone

Implemented scope for Step 22:

- Validation and projection algorithms no longer live directly in the CLI
  facade.
- Tests cover direct structured module input/output plus the existing command
  facade paths.
- The remaining split target is parameterization, reporting, and explorer
  orchestration.

## Scene Generation Parameterization/Reporting Split Step Plan

Implemented commit-level scope:

- Add `gcs_scene_generation.parameterization` for deterministic layout
  positions, geometry vectors, distance values, and angle values.
- Add `gcs_scene_generation.reporting` for graph summaries, validation
  summaries, projection statistics, biconnectivity evidence, histograms, and
  rigid-set summaries.
- Keep `tools.py` as the CLI facade with compatibility wrappers around the
  moved parameterization and reporting helpers.
- Add deterministic tests for parameter assignment and report summaries.

## Scene Generation Parameterization/Reporting Split Milestone

Implemented scope for Step 23:

- Parameterization and reporting algorithms no longer live directly in the CLI
  facade.
- Direct module tests cover deterministic structured input/output behavior.
- The remaining split target is explorer orchestration and repair policy.

## Scene Generation Repair Split Step Plan

Implemented commit-level scope:

- Add `gcs_scene_generation.repair` for generated-candidate repair policy:
  constraint-signature replacement, deterministic rigid-set recoloring,
  biconnectivity repair, and structured edit lists.
- Keep `tools.py` as the CLI facade with a compatibility wrapper around
  `repair_gcs_graph`.
- Add focused tests for direct repair module input/output, including stable
  edit evidence and post-repair validation.

## Scene Generation Repair Split Milestone

Implemented scope for Step 24:

- Repair policy no longer lives directly in the CLI facade.
- Repair outputs carry a structured `edits` list and a repaired graph payload
  consumed by the facade for storage.
- This left explorer orchestration and promotion orchestration as the next
  split target, which was addressed in Step 25.

## Scene Generation Explorer And Promotion Split Milestone

Implemented scope for Step 25:

- `gcs_scene_generation.explorer` now owns structured exploration request
  normalization, candidate construction, candidate gate orchestration,
  deterministic coverage scoring, negative evidence, trace writing, and
  `ExploreResult` assembly.
- `gcs_scene_generation.promotion_package` now owns public adapter gate
  reports, candidate provenance loading, promotion-package assembly, blocking
  status rules, and promotion artifact writing.
- `tools.py` remains the CLI dispatcher and compatibility facade over package
  modules instead of being the owner of explorer or promotion-package policy.
- Direct package-boundary tests now cover explorer request/coverage contracts
  and promotion blocking contracts, while existing deterministic explorer and
  promotion command tests continue to pass.

Reassessment after Step 25:

- Step 26 remains store adapter containment because `tools.py` still carries
  flat graph-store wrappers and the mutable `STORE_DIR` compatibility binding.
- Step 27 remains promotion gate hardening, intentionally after store
  containment so direct public adapters do not inherit scattered path policy.
- Steps 28 and 29 remain registered after Step 26 and Step 27 unless the store
  adapter work exposes a higher-priority solver or atlas gap.

## Scene Generation Store Adapter Milestone

Implemented scope for Step 26:

- `gcs_scene_generation.storage.SceneGenerationStore` now owns scratch-store
  path policy, graph IO, safe IDs, JSON IO, exploration roots, candidate roots,
  promotion roots, trace append, and digest helpers.
- `tools.py` compatibility storage functions now route through the adapter
  while preserving the mutable `STORE_DIR` binding required by existing tests
  and manual scripts.
- `gcs_scene_generation.explorer` and
  `gcs_scene_generation.promotion_package` now consume the adapter instead of
  raw store paths at their orchestration seams.
- Focused unittest coverage now checks adapter save/load/list behavior and
  stable exploration/promotion root contracts.

Reassessment after Step 26:

- Step 27 is now promotion gate hardening because executable smoke output is
  still the weakest public evidence boundary.
- Step 28 remains solver algorithm deepening after gate hardening so promoted
  fixtures and adapter evidence can support stronger algorithm work.
- Step 29 remains architecture atlas synchronization after the implementation
  boundaries stabilize, unless Step 27 changes the viewer-facing map earlier.

## Scene Generation Promotion Gate Hardening Milestone

Implemented scope for Step 27:

- `gcs_scene_generation.promotion_package` now accepts structured runtime
  evidence through `public_gate_config.runtime_report` and
  `public_gate_config.runtime_report_path`.
- Public promotion gates prefer structured runtime and diagnostics evidence for
  `runtime_smoke` and `diagnostics_evidence` before falling back to executable
  smoke output.
- Existing fallback behavior through `public_gate_config.solver_command`,
  `GCS_EXE`, and the default built `GCS.exe` remains available with explicit
  skipped/unsupported/failed semantics.
- Focused unittest coverage verifies structured runtime evidence passes public
  gates even when the fallback executable is missing.

Reassessment after Step 27:

- Step 28 is now solver algorithm deepening reassessment because
  scene-generation evidence, store ownership, and promotion gates are stable
  enough to feed stronger solver work.
- Step 29 remains architecture atlas synchronization after the next solver
  algorithm move, unless Step 28 changes only documentation and the atlas can
  be synchronized immediately afterward.

## Numeric Free-Column Rank Evidence Step Plan

Implemented commit-level scope for Step 28:

- Reassess the current solver algorithm surface across decomposition planner,
  diagnostics, and numeric engine.
- Choose the module with the clearest incomplete evidence behind an existing
  public contract.
- Extend numeric rank/condition evidence so declared boundary variables are
  treated as frozen degrees of freedom instead of active rank columns.
- Preserve full active variable dimension in `RankConditionReport`, while also
  reporting free and frozen variable dimensions.
- Add contract tests that make boundary-frozen rank/nullity evidence explicit.

## Numeric Free-Column Rank Evidence Milestone

Implemented scope for Step 28:

- `gcs.numeric_engine` now derives a free-column set from
  `NumericTask.boundary_variables` and the assembled active-variable ordering.
- `RankConditionReport` reports `variable_dimension`,
  `free_variable_dimension`, and `frozen_variable_dimension`.
- Rank, nullity, under-constrained evidence, over-constrained evidence,
  singular evidence, and condition evidence are computed from the free-column
  Jacobian actually solved by the local numeric task.
- Full variable dimension remains available for downstream diagnostics that
  need model-shape evidence separate from solve degrees of freedom.
- `NumericEngineContract.RankEvidenceUsesOnlyFreeBoundaryColumns` verifies the
  boundary-frozen rank contract.

Reassessment after Step 28:

- Step 29 is now architecture atlas synchronization. The implemented module
  boundaries have changed across scene-generation orchestration, store
  containment, promotion gates, and numeric evidence; the atlas should be made
  current before the next algorithm-deepening batch.
- Decomposition and diagnostics remain viable future algorithm-deepening
  candidates, but no new evidence requires inserting them before the atlas
  synchronization step.

## Architecture Atlas Synchronization Step Plan

Implemented commit-level scope for Step 29:

- Synchronize the Mermaid architecture atlas with the current C++ module
  topology, contract tools, scene-generation package split, store adapter,
  promotion gates, and numeric free/frozen rank evidence.
- Keep canonical generated SVG assets separate from intentionally tracked
  review artifacts.
- Update the deterministic Figure 1 renderer instead of manually editing SVG
  evidence text.
- Regenerate the main Figure 1 SVG and residual/rank panel SVG from the
  canonical saved scene fixture.
- Validate docs, SVG XML parseability, and the full quality gate before
  committing.

## Architecture Atlas Synchronization Milestone

Implemented scope for Step 29:

- `docs/architecture/70-visualization/gcs-architecture-atlas.md` now names
  `contract_tools`, scene-generation promotion gates, `SceneGenerationStore`,
  public scene artifacts, and free/frozen numeric rank evidence.
- The atlas adds a dedicated scene-generation and promotion tooling diagram.
- `docs/architecture/70-visualization/svg-editing-workflow.md` documents
  canonical SVG outputs separately from tracked review artifacts and adds the
  free/frozen rank-card acceptance check.
- `tools/architecture_visualization/render_gcs_figure1.py` now renders the
  rank card using full variables, free columns, frozen columns, and nullity.
- Figure 1 generated assets are refreshed from
  `fixtures/scene/saved/triangle_003_graph.json`.

Reassessment after Step 29:

- Step 30 is diagnostics free/frozen rank propagation. Numeric evidence is now
  correctly produced and visualized, but diagnostics must preserve that
  evidence in its public rank report before viewer/runtime/promotion consumers
  can rely on it end to end.
- Decomposition separator and solve-DAG deepening should wait until the rank
  evidence vocabulary is consistent across numeric and diagnostics.

## Diagnostics Free/Frozen Rank Propagation Step Plan

Implemented commit-level scope for Step 30:

- Extend `gcs.diagnostics::RankReport` with free and frozen numeric variable
  dimensions while preserving the existing full numeric variable dimension.
- Populate the diagnostics rank report from
  `numeric::RankConditionReport.variable_dimension`,
  `free_variable_dimension`, and `frozen_variable_dimension`.
- Add a diagnostics contract test that uses a boundary-frozen numeric task and
  verifies diagnostics preserves rank, full/free/frozen dimensions, nullity,
  and under-constrained evidence.
- Keep status precedence behavior unchanged.

## Diagnostics Free/Frozen Rank Propagation Milestone

Implemented scope for Step 30:

- `diagnostics::RankReport` now carries
  `numeric_free_variable_dimension` and
  `numeric_frozen_variable_dimension`.
- `diagnostics::diagnose` preserves numeric full/free/frozen dimensions from
  the numeric engine instead of collapsing all rank evidence to full active
  variables.
- Diagnostics contract coverage now includes
  `DiagnosticsContract.PropagatesBoundaryFrozenNumericRankEvidence`.
- Solver contract docs now state that diagnostics rank reports keep structural
  evidence and numeric full/free/frozen evidence separate.

Reassessment after Step 30:

- Step 31 is runtime/viewer rank evidence projection. Numeric and diagnostics
  now preserve the evidence, but command summaries and viewer overlays still
  need a public projection path so UI, promotion gates, and review tooling can
  consume the richer rank report without inspecting numeric internals.
- Decomposition separator and solve-DAG deepening remain queued after the
  public evidence path is visible at the boundary.

## Runtime And Viewer Rank Evidence Projection Step Plan

Implemented commit-level scope for Step 31:

- Add a public runtime rank-evidence projection over command results instead
  of forcing UI or promotion consumers to read numeric-engine internals.
- Preserve full variable dimension, free variable dimension, frozen variable
  dimension, residual dimension, rank, nullity, under/over/singular flags, and
  condition evidence in the projection.
- Extend viewer diagnostic overlays and command summaries to carry the runtime
  projection as structured output.
- Add accepted runtime and boundary-frozen viewer contract tests.
- Keep numeric solving, diagnostics status precedence, transaction semantics,
  and durable state mutation unchanged.

## Runtime And Viewer Rank Evidence Projection Milestone

Implemented scope for Step 31:

- `runtime::RankEvidenceProjection` is now the public boundary shape for rank
  evidence.
- `runtime::project_rank_evidence(const CommandResult&)` projects evidence
  from command results and records the source as
  `runtime.numeric_rank_condition_report`.
- `viewer::DiagnosticOverlay` and `viewer::SnapshotSummary` now include
  structured rank evidence, and detailed overlays include
  `viewer.rank_evidence` items for human review.
- Session runtime contract coverage verifies accepted command rank evidence.
- Viewer bridge contract coverage verifies boundary-frozen full/free/frozen
  rank evidence through overlays and summaries.

Reassessment after Step 31:

- Step 32 is promotion gate rank evidence consumption. The public projection
  shape now exists, so promotion-package gates should parse that shape rather
  than introducing private numeric-report parsing.
- Step 33 remains decomposition separator and SolveDAG deepening after the
  promotion boundary consumes the new evidence.
- Step 34 remains boundary-aware runtime diagnostics, where the same public
  rank projection can later be backed by post-local diagnostics.

## Promotion Gate Rank Evidence Step Plan

Implemented commit-level scope for Step 32:

- Extend scene-generation promotion-package public gates with a first-class
  `rank_evidence` gate.
- Accept the Step 31 public `RankEvidenceProjection` shape from structured
  runtime or viewer reports.
- Validate full/free/frozen dimensions, residual dimension, rank, nullity,
  under/over/singular flags, and condition evidence shape.
- Preserve existing runtime smoke and diagnostics evidence gate semantics.
- Keep executable smoke fallback for environments without structured runtime
  reports.

## Promotion Gate Rank Evidence Milestone

Implemented scope for Step 32:

- `gcs_scene_generation.promotion_package` now discovers rank evidence from
  public paths such as `rank_evidence`, `viewer_overlay.rank_evidence`,
  `diagnostic_overlay.rank_evidence`, `snapshot_summary.rank_evidence`, and
  `command_summary.rank_evidence`.
- The `rank_evidence` gate reports structured evidence count, source path,
  copied projection records, and validation issues.
- Missing rank evidence in a structured runtime report is recorded as a
  skipped non-blocking gate.
- Malformed supplied rank evidence fails with `rank_evidence_failed`.
- Python scene-generation tests cover pass, skipped, and failed rank-evidence
  gate paths.

Reassessment after Step 32:

- Step 33 is decomposition separator and SolveDAG deepening. Rank evidence now
  reaches promotion boundaries, so planner evidence can deepen without leaving
  promotion blind to the solver's rank state.
- Step 34 remains boundary-aware post-local runtime diagnostics so the rank
  projection can later consume diagnostics-owned evidence.
- Step 35 remains diagnostics conflict/redundancy deepening after runtime has
  richer post-local diagnostic stages.

## Decomposition SolveDAG Evidence Step Plan

Implemented commit-level scope for Step 33:

- Add typed SolveDAG structures to `gcs.decomposition_planner`.
- Derive DAG edges from public `BoundaryProjection` records so component
  subproblems explicitly feed the root aggregation context.
- Preserve existing cover and solve-order contracts while adding a richer DAG
  validation surface.
- Add accepted and negative contract tests for boundary dependency evidence.
- Keep residual evaluation, numeric iteration, gluing acceptance, and runtime
  commit policy outside the planner.

## Decomposition SolveDAG Evidence Milestone

Implemented scope for Step 33:

- `PlannerOutput` now carries `SolveDag`.
- `SolveDagNode` distinguishes local solve nodes from aggregation contexts.
- `SolveDagEdge` names source context, target context, projection ID, boundary
  entity IDs, and boundary constraint IDs.
- `validate_solve_dag` verifies known contexts, known nodes, projection/cover
  consistency, acyclic order, and subproblem coverage.
- Decomposition planner contract coverage now includes accepted DAG boundary
  dependencies and a rejected backward dependency case.

Reassessment after Step 33:

- Step 34 is boundary-aware runtime diagnostics. Runtime should now expose
  post-local diagnostic evidence as a transaction stage so public projections
  can eventually consume diagnostics-owned rank and residual reports.
- Separator/articulation algorithms remain useful but can be deepened after
  runtime carries richer post-local evidence.
- Step 35 remains diagnostics conflict/redundancy deepening after Step 34.

## Boundary-Aware Runtime Diagnostics Step Plan

Implemented commit-level scope for Step 34:

- Add a post-local diagnostic carrier to `gcs.session_runtime`.
- Run diagnostics after each successful local numeric solve and before gluing.
- Record post-local diagnostics in transaction stage traces.
- Make runtime rank evidence projection prefer diagnostics-owned rank reports.
- Preserve transaction isolation and rollback before durable commit for
  blocking post-local diagnostic statuses.

## Boundary-Aware Runtime Diagnostics Milestone

Implemented scope for Step 34:

- `CommandResult` now carries `post_local_diagnostics`.
- Each `PostLocalDiagnosticReport` names the local report index, context ID,
  and `diagnostics::DiagnosticOutput`.
- The runtime records `post_local_diagnostics` stage entries between
  `numeric_solve` and `gluing`.
- `runtime::project_rank_evidence` now prefers
  `runtime.post_local_diagnostics.rank_report` and falls back to raw numeric
  rank reports only when post-local diagnostics are absent.
- Session runtime contract coverage verifies post-local residual/rank evidence
  and the expanded stage trace.

Reassessment after Step 34:

- Step 35 completed diagnostics conflict/redundancy deepening. Runtime now
  exposes post-local diagnostics, and diagnostics can name smaller
  responsible sets through public reports.
- Step 36 remains numeric robustness after diagnostics has richer conflict and
  redundancy contracts.
- Step 37 remains fixture/corpus expansion after the next diagnostics and
  numeric evidence changes clarify which fixtures are durable.

## Diagnostics Conflict And Redundancy Deepening Step Plan

Implemented commit-level scope for Step 35:

- Extend `ConflictSearchRequest` and `RedundancySearchRequest` with the model
  snapshot needed to resolve subject IDs from public diagnostic reports.
- Enrich residual conflict candidates so `diagnostics.residual_conflict`
  names both the unsatisfied constraint and the owning entity IDs.
- Add exact duplicate constraint-signature detection as a smaller redundancy
  candidate before broad over-constrained context fallback.
- Preserve `diagnostics.overconstrained_redundancy_candidate` for structural
  or numeric over-constrained evidence.
- Keep gluing obstruction conflicts on the gluing path and keep status
  precedence unchanged.

## Diagnostics Conflict And Redundancy Deepening Milestone

Implemented scope for Step 35:

- Residual conflict evidence now maps from numeric residual blocks through
  `ModelSnapshot` to stable constraint and entity subjects.
- Redundant distance-pair fixtures now produce
  `diagnostics.redundant_duplicate_distance` without needing an
  over-constrained rank/DOF condition.
- Over-constrained duplicate-distance fixtures still expose the broader
  `diagnostics.overconstrained_redundancy_candidate` evidence, preserving
  existing corpus expectations.
- Diagnostics contract coverage now includes residual conflict entity IDs and
  exact duplicate distance redundancy evidence.
- Contract test baseline increased to 92 CTest-discovered GTest cases.

Reassessment after Step 35:

- Step 36 completed the first numeric robustness batch. Diagnostics can now
  rely on max-absolute residual convergence semantics and condition evidence
  that is not published for singular free Jacobians.
- Step 37 should remain next because fixture/corpus expansion can now capture
  the strengthened residual and rank-condition edge cases as reusable models
  or scenes.
- Step 38 remains viewer/GUI evidence surface work after diagnostics and
  numeric evidence contracts settle further.

## Numeric Robustness Step Plan

Implemented commit-level scope for Step 36:

- Align numeric convergence with diagnostics residual tolerance by checking
  maximum absolute residual values rather than Euclidean residual norm alone.
- Preserve residual norm as report and iteration-trace trend evidence.
- Suppress finite condition estimates when rank evidence shows the effective
  free Jacobian is rank deficient.
- Add deterministic numeric contract coverage for tolerated multi-residual
  stopping and singular-rank condition suppression.
- Keep `NumericTask`, `NumericReport`, and `RankConditionReport` public shapes
  unchanged.

## Numeric Robustness Milestone

Implemented scope for Step 36:

- `numeric::solve_local` now treats a task as converged when every residual
  value is within the active residual tolerance, avoiding false failures for
  multiple individually tolerated residual blocks.
- `RankConditionReport.condition_estimate_available` is false for singular
  effective free Jacobian evidence, even when a partial pivot ratio could be
  computed.
- Numeric engine contract coverage now includes
  `NumericEngineContract.ConvergesWhenEachResidualIsWithinTolerance` and
  `NumericEngineContract.SingularRankDoesNotPublishFiniteConditionEstimate`.
- Contract test baseline increased to 94 CTest-discovered GTest cases.

Reassessment after Step 36:

- Step 37 completed fixture/corpus expansion for boundary-frozen rank,
  max-absolute residual tolerance, and separator-chain structure. These
  examples are now reusable through `gcs.contract_tools`.
- Step 38 remains viewer/GUI evidence surface work after the corpus gives UI
  and overlay contracts richer examples.
- Step 39 remains quality gate hardening after the new corpus evidence is in
  place.

## Fixture And Scene Corpus Expansion Step Plan

Implemented commit-level scope for Step 37:

- Add reusable `FixtureKind` entries for boundary-frozen distance,
  tolerated multi-residual distance, and separator-chain distance scenarios.
- Add fixture classes for `boundary_frozen`, `tolerance_edge`, and
  `separator`.
- Encode boundary-frozen solve intent through `ModelSnapshot.solve_intent`
  fixed entity IDs so numeric tests can construct boundary-variable tasks
  from public fixture data.
- Promote the Step 36 tolerated multi-residual model from a test-local helper
  into `gcs.contract_tools`.
- Extend corpus golden summaries and contract-tool tests for the new fixture
  classes.

## Fixture And Scene Corpus Expansion Milestone

Implemented scope for Step 37:

- `make_boundary_frozen_distance_model` returns a valid distance model with a
  fixed-entity solve-intent hint for boundary-frozen rank evidence tests.
- `make_tolerated_multi_residual_distance_model` returns a two-component
  model whose residual norm exceeds tolerance while every residual block's
  max absolute value is within tolerance.
- `make_separator_chain_distance_model` returns a three-point chain where the
  middle entity is the stable separator subject shared by adjacent distance
  constraints.
- Default generated fixture corpus size increased from 10 to 13 bundles.
- Contract-tool coverage now verifies boundary-frozen solve hints, tolerated
  residual stopping evidence, and separator-chain subject structure.
- Contract test baseline increased to 97 CTest-discovered GTest cases.

Reassessment after Step 37:

- Step 38 completed viewer evidence surface expansion. Viewer overlays and
  summaries can now expose residual, conflict, redundancy, and obstruction
  evidence as structured projections rather than only message strings.
- Step 39 should remain quality gate hardening after viewer evidence surfaces
  stabilize.
- Step 40 remains atlas and roadmap resynchronization for the close of the
  Step 31 through Step 39 batch.

## Viewer Evidence Surface Step Plan

Implemented commit-level scope for Step 38:

- Extend `DiagnosticOverlay` and `SnapshotSummary` with structured residual,
  conflict, redundancy, and obstruction evidence projections.
- Project residual evidence from post-local diagnostics, including per
  constraint residual values, max absolute values, tolerances, and
  satisfaction flags.
- Project conflict and redundancy responsibility sets from pre-solve,
  post-local diagnostics, and gluing reports.
- Project obstruction evidence from command and gluing obstruction reports.
- Keep Python GUI untouched until it can consume the stable viewer bridge
  contract in a separate small change.

## Viewer Evidence Surface Milestone

Implemented scope for Step 38:

- Added `ConstraintResidualProjection`, `ResidualEvidenceProjection`, and
  `ResponsibilityEvidenceProjection` to `gcs.viewer_bridge`.
- Added public projection helpers:
  `project_residual_evidence`, `project_conflict_evidence`,
  `project_redundancy_evidence`, and `project_obstruction_evidence`.
- Detailed overlays now include `viewer.residual_evidence`,
  `viewer.conflict_evidence`, `viewer.redundancy_evidence`, and
  `viewer.obstruction_evidence` items while preserving existing status and
  rank items.
- Viewer bridge contract coverage now checks residual/conflict projection,
  duplicate redundancy projection, and gluing obstruction projection.
- Contract test baseline increased to 100 CTest-discovered GTest cases.

Reassessment after Step 38:

- Step 39 is now the highest-leverage next move. Rank, diagnostics,
  promotion, corpus, and viewer evidence paths are now public and should be
  protected by deterministic default quality gates where affordable.
- Step 40 remains atlas and roadmap resynchronization after quality gate
  behavior is finalized.

## Quality Gate Hardening Step Plan

Implemented commit-level scope:

- Refactor `run-quality-gates` command construction into a pure, unit-tested
  command sequence so the gate itself has a stable tools contract.
- Add `python.agentic_toolkit` to the default quality gate to protect that
  command sequence.
- Keep full CTest as the broad contract boundary, and add a named
  `ctest.public_evidence_chain` sentinel for the Step 31-38 public evidence
  path.
- Keep the existing `ctest.fixture_corpus` gate as the explicit corpus
  boundary.
- Document the hardened gate sequence and acceptance contract.

Implemented scope:

- `ctest.public_evidence_chain` selects numeric free/frozen rank and
  max-absolute residual tests, diagnostics residual/rank promotion and
  duplicate-redundancy tests, runtime rank/post-local diagnostic projection
  tests, viewer overlay evidence tests, and contract-tool corpus fixture
  tests.
- `python.agentic_toolkit` asserts default gate ordering and skip-flag
  composition without invoking build or CTest.
- The default gate remains deterministic and affordable; slow exploratory
  generation remains outside the default path.

Reassessment after Step 39:

- The Step 31 through Step 38 evidence chain is now protected by both the full
  contract suite and a named sentinel gate.
- Step 40 is the next highest-leverage move: resynchronize atlas, roadmap,
  maturity lens, and next-batch planning against the hardened gate behavior.

## Architecture Atlas And Roadmap Resynchronization Step Plan

Implemented commit-level scope:

- Reconcile the roadmap, current-progress archive, forward plan, and Step
  1-40 report after the Step 31-39 public evidence batch.
- Add Figure 71 to the architecture atlas as the Step 1-40
  evidence-boundary reporting figure.
- Promote the visual taste guide into the architecture index and align the
  Figure 71 generator with the Step 40 closure state.
- Update the module maturity lens so the implemented public evidence path is
  reflected as L2 across target modules.
- Register the integrated feature showcase constraint graph as the next
  candidate now that quality gates and atlas vocabulary are stable.

Implemented scope:

- `docs/architecture/70-visualization/gcs-architecture-atlas.md` now embeds
  Figure 71, documents its rebuild command, and names its source documents.
- `tools/architecture_visualization/render_gcs_figure71.py` renders the Step
  36-40 band as an evidence-closure horizon once all steps are complete.
- `docs/architecture/73-gcs-visual-taste-guide.md` defines the durable visual
  quality standard for diagrams, reports, GUI surfaces, and showcase visuals.
- `docs/architecture/71-step-1-40-execution-report.md` and this roadmap are
  synchronized to Step 40 completion.

Reassessment after Step 40:

- Steps 1 through 40 are now registered, summarized, and closed in the
  roadmap/reporting documents.
- The next high-leverage implementation step is the integrated feature
  showcase constraint graph. It should enter the fixture or generated-scene
  corpus with structured expectations rather than remain a manual demo.

## Integrated Feature Showcase Step Plan

Implemented commit-level scope:

- Carry `SolveIntent.fixed_entity_ids` into planner subproblem boundary
  variables when those entities are active in a local context.
- Add a reusable integrated showcase fixture in `gcs.contract_tools`.
- Make the fixture exercise multiple rigid sets, multiple local components,
  a separator-like distance chain, oriented constraints, boundary-frozen rank
  evidence, post-local diagnostics, and viewer overlay projection.
- Add focused GTest coverage for fixture provenance, planner boundary
  propagation, runtime/viewer rank evidence, and the default corpus summary.
- Reassess after the C++ fixture exists whether JSON scene promotion and atlas
  rendering should be a separate Step 42.

Exit criteria:

- The showcase fixture is deterministic and available through public
  contract-tool APIs.
- Runtime/viewer evidence for the fixture shows frozen boundary dimensions and
  multiple local reports.
- The fixture is covered by GTest and the full quality gate.

Implemented scope:

- `decomposition_planner` now carries fixed solve-intent entities into local
  subproblem `boundary_variables` when active.
- `gcs.contract_tools` now exposes `FixtureKind::integrated_feature_showcase`
  and `make_integrated_feature_showcase_model()`.
- The showcase fixture includes two local components: a fixed point-distance
  chain and a mixed point/plane/line component with distance and
  perpendicular evidence.
- Default contract-tool corpus size is now 14 fixture bundles.
- `ctest.public_evidence_chain` now includes the showcase sentinel tests.

Reassessment after Step 41:

- The positive executable showcase path is stable in C++ contracts and viewer
  projection.
- Step 42 should promote the showcase into durable JSON scene fixtures,
  negative diagnostic variants, and atlas/demo projection artifacts.

## Showcase Scene Promotion Step Plan

Commit-level scope:

- Extend current `gcs-0.3` JSON scene IO so `behavior.fixed_geometry_ids`,
  `behavior.driven_geometry_ids`, and `behavior.target_constraint_ids`
  round-trip into `ModelSnapshot.solve_intent`.
- Add kernel validation for solve-intent references so scene files with stale
  fixed/driven/target IDs produce structured report codes instead of silently
  entering the runtime.
- Promote the integrated showcase into durable positive and negative scene
  fixtures with companion metadata.
- Add C++ contract tests for JSON behavior round-trip, positive showcase scene
  loading, and negative fixed-entity rejection.
- Add the positive showcase CLI smoke and new scene/IO sentinel tests to the
  default quality gate.

Step 42 working decision:

- Fixed-boundary expectations belong in the JSON `behavior` model, not only in
  companion metadata, because they are runtime solve intent rather than display
  annotation.
- Companion metadata should describe provenance and expected public evidence;
  it should not be the only carrier of solver behavior.

Implemented scope:

- `gcs.io_adapters` now writes and reads JSON `behavior` as
  `ModelSnapshot.solve_intent`.
- `gcs.kernel` validates fixed, driven, and target solve-intent references
  and emits stable report codes for missing or duplicate IDs.
- `fixtures/scene/showcase/` now contains a positive integrated showcase JSON
  scene, a missing-fixed-entity negative variant, metadata files, and a
  manifest.
- C++ contract tests cover JSON behavior round-trip, showcase scene load, and
  negative behavior rejection.
- The default quality gate now includes kernel/IO showcase sentinels and a
  showcase JSON CLI smoke.

Reassessment after Step 42:

- The showcase is no longer only a private C++ fixture; it is now a durable
  scene asset with executable positive and negative evidence.
- Step 43 should use these public scene assets to produce the atlas/demo
  projection and report package without reading private contract-tool
  internals.

## Scene-Backed Showcase Atlas Step Plan

Implemented scope:

- Added a dedicated dependency-free renderer,
  `tools/architecture_visualization/render_showcase_scene.py`, that reads the
  public showcase JSON scene and metadata.
- Generated `figure72-gcs-integrated-showcase-scene.svg` and
  `showcase-scene-report.md` under the architecture atlas.
- Updated the atlas to reference Figure 72 and its regeneration command.
- Added Python renderer tests that load public scene IDs, validate negative
  metadata evidence, parse generated SVG XML, and check deterministic SVG
  rendering.
- Added the showcase-scene renderer test to the default quality gate.

Reassessment after Step 43:

- The showcase is now public at three layers: executable scene, generated
  atlas figure, and Markdown evidence report.
- Step 44 should harden cross-language scene behavior compatibility because
  Python visualization now writes `gcs-0.3` behavior fields while legacy saved
  GUI fixtures still include older JSON shape.

## Cross-Language Scene Behavior Step Plan

Implemented scope:

- Added a Python-authored-shape `gcs-0.3` JSON fixture with `behavior`,
  `history`, and rigid-set `geometry_ids` fields.
- Added C++ IO contract coverage proving that fixture loads and maps
  `mode`, `fixed_geometry_ids`, `driven_geometry_ids`, and
  `target_constraint_ids` into `ModelSnapshot.solve_intent`.
- Added Python `gcs_viz.algebra` tests for current JSON schema emission,
  behavior/history write-read preservation, and legacy saved-scene
  normalization to current public shape.
- Added the Python scene-schema algebra test to the default quality gate.
- Updated current-model and quality-gate docs to record the cross-language
  behavior contract.

Reassessment after Step 44:

- Scene-facing behavior intent is now covered by both Python and C++ tests.
- The remaining compatibility risk is history/replay: Python preserves saved
  construction history, while C++ scene IO currently treats history as
  non-solver metadata. Step 45 should make that policy explicit and tested.

## Damped Numeric Local Solve Step Plan

Implemented commit-level scope:

- Replace the identity local-section placeholder with a dense damped
  Gauss-Newton baseline that uses residuals and Jacobians assembled through
  `gcs.constraint_catalog`.
- Add a damping parameter to `SolveLimits` and validate it through the numeric
  task contract.
- Freeze declared boundary variables during local updates while still reporting
  before/after boundary evidence.
- Apply a trust-region clamp and short damping line search without adding an
  external linear algebra dependency.
- Preserve `NumericReport`, `ResidualReport`, `RankConditionReport`,
  `BoundaryVariableReport`, and `IterationTrace` as the structured output
  surface.
- Update diagnostics residual-promotion tests to use an explicit zero-iteration
  non-converged numeric report rather than relying on a solver that should now
  converge the reusable unsatisfied fixture.

## Damped Numeric Local Solve Milestone

Implemented scope for the first algorithm-deepening milestone:

- `numeric::solve_local` now iterates on a transaction-local model snapshot,
  computes damped normal-equation steps, clamps the step to the declared trust
  radius, and accepts only residual-reducing trial states.
- The reusable unsatisfied two-point distance fixture now converges to residual
  tolerance and records accepted `damped_gauss_newton` trace entries.
- Zero-residual fixtures still return a replayable two-entry trace:
  `initial` then `converged`.
- Non-converged tasks return `numeric.local_section.failed` with preserved
  residual evidence for diagnostics.
- Numeric contract coverage now includes accepted damped steps and convergence
  from a nonzero residual fixture.
- Diagnostics coverage now separates numeric residual-promotion behavior from
  successful convergence by using an explicit zero-iteration numeric task.

## JSON Scene IO Step Plan

Implemented commit-level scope:

- Promote JSON scene loading from an unsupported placeholder into a readable
  schema path for canonical `gcs-0.3` JSON scenes.
- Add a bounded in-repo JSON parser for the canonical scene subset:
  objects, arrays, strings, numbers, and `null`, with typed parse issues and
  source positions.
- Add explicit `gcs-0.2` to `gcs-0.3` migration behavior under
  `CompatibilityMode::migration_allowed`.
- Preserve deterministic `canonical_json`, stable IDs, state version,
  geometry parameters, constraint entity references, and constraint values
  across JSON load and JSON round-trip.
- Add current, legacy, and malformed JSON fixtures under `fixtures/scene/json`.
- Update cross-module quality gates to assert malformed JSON parse evidence
  now that JSON is a supported readable format.

## JSON Scene IO Milestone

Implemented scope for the JSON schema and migration milestone:

- `gcs.io_adapters` now reads canonical JSON scenes and validates them through
  kernel model validation before accepting the load.
- The schema registry marks `gcs-0.3` JSON as readable and writable.
- Legacy `gcs-0.2` fixtures using `schema_version`, `parameters`, and
  `entity_ids` migrate to `gcs-0.3` only when migration compatibility is
  explicitly requested.
- Malformed JSON reports typed parser issues such as `io.json.parse_error`,
  `io.json.object`, or `io.json.array`.
- `io::round_trip` supports both text and JSON formats with stable canonical
  digests.
- Contract test count increased to 79, covering current JSON load, legacy
  migration, malformed JSON, JSON round-trip, and cross-module parse evidence.

## Diagnostics Conflict And Redundancy Step Plan

Implemented commit-level scope:

- Add public `ConflictSearchRequest` and `RedundancySearchRequest` contracts
  to `gcs.diagnostics`.
- Add `find_conflicts` to promote residual out-of-tolerance evidence into
  constraint-level `ConflictSet` candidates with stable report codes.
- Add `find_redundancies` to promote structural or numeric
  over-constrained evidence into context-level `RedundancySet` candidates.
- Wire conflict and redundancy candidates into `diagnose` output without
  changing status precedence ownership.
- Keep failed gluing obstruction conflict evidence intact and separate from
  post-local-solve residual conflicts.
- Extend diagnostics contract tests for residual conflict candidates and
  over-constrained redundancy candidates.

## Diagnostics Conflict And Redundancy Milestone

Implemented scope for the first diagnostics-certification deepening milestone:

- Residual diagnostics now produce `diagnostics.residual_conflict` candidate
  sets naming the unsatisfied constraint IDs.
- Over-constrained structural/rank evidence now produces
  `diagnostics.overconstrained_redundancy_candidate` sets naming the
  context's constraint IDs.
- `DiagnosticOutput.conflict_sets` and `DiagnosticOutput.redundancy_sets` are
  populated from public diagnostic tools rather than remaining passive
  placeholders.
- Contract test count increased to 80, covering residual conflicts,
  redundancy candidates, and prior gluing obstruction conflicts.

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
