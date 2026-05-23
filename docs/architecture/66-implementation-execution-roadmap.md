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
