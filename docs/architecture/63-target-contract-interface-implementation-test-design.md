# Target Contract Interface, Implementation, And Test Design

## Purpose

This document defines the target interface, implementation, and contract-test
design for the next GCS solver rewrite.

Important: the current C++ interfaces, implementation files, and existing
`tests/gcs_contract_tests.cpp` are not the baseline for this design. They are
temporary scaffolding. Future implementation should be derived from the
architecture in `60-agentic-submodule-design-analysis.md`,
`61-agentic-module-framework.md`, and `62-module-agents.md`, then implemented
as clean C++23 modules.

## Design Thesis

The solver must be designed from contracts outward:

```text
structured input
  -> module-owned typed tool
  -> structured output
  -> typed report / obstruction / trace
  -> contract tests
```

Every module must therefore export three things:

1. Contract types: immutable inputs, outputs, IDs, policies, reports, and
   failure evidence.
2. Narrow service APIs: deterministic operations with explicit side effects.
3. Testable tools: validators, builders, analyzers, and replay hooks that
   contract tests can call without reaching into implementation details.

Implementation details stay hidden in `.cpp` units or non-exported module
partitions. Public APIs must not expose algorithm internals simply because a
test needs them.

## C++23 Module Rules

- New solver code uses C++23 modules.
- Public contracts live in `.cppm` module interfaces.
- Algorithm implementations live in `.cpp` implementation units or private
  module partitions.
- A public module may export sub-contract partitions when the interface becomes
  large, but the stable external vocabulary remains `gcs.<module>`.
- No lower solver module imports `io_adapters`, `viewer_bridge`,
  `session_runtime`, CLI, Python, or GUI code.
- Tests import public modules only.

Recommended physical shape:

```text
src/gcs/<module>/
  <module>.cppm          # public facade and exported contracts
  <module>.cpp           # primary implementation
  detail/*.cpp           # private implementation units if needed
tests/contracts/<module>/
  <module>_contract_tests.cpp
fixtures/contracts/<module>/
  *.gcs.json
  *.expected.json
```

If module partitions are supported reliably by the toolchain:

```text
src/gcs/kernel/kernel.cppm          # export module gcs.kernel
src/gcs/kernel/ids.cppm             # export module gcs.kernel:ids
src/gcs/kernel/reports.cppm         # export module gcs.kernel:reports
src/gcs/kernel/snapshot.cppm        # export module gcs.kernel:snapshot
src/gcs/kernel/validation.cpp       # module gcs.kernel
```

## Common Contract Layer

`gcs.kernel` should own the common contract layer because it is the lowest
mathematical module.

Target types:

```cpp
export module gcs.kernel;

export namespace gcs::kernel {

enum class ReportSeverity { info, warning, error };
enum class StageStatus { ok, warning, error, unsupported };
enum class SolveStatus {
    not_run,
    solved,
    accepted_with_warnings,
    invalid_model,
    under_constrained,
    over_constrained,
    redundant,
    inconsistent,
    numerically_singular,
    unsupported,
    failed,
};

struct ReportCode {
    std::string_view value;
};

struct StableId {
    std::string_view domain;
    std::uint64_t value;
};

struct ReportMessage {
    ReportSeverity severity;
    ReportCode code;
    std::string summary;
    std::vector<StableId> subjects;
};

struct StageReport {
    StableId report_id;
    std::string_view stage;
    StageStatus status;
    std::vector<ReportMessage> messages;
};

template <class Payload>
struct ContractResult {
    Payload payload;
    StageReport report;
};

}
```

Guidance:

- `ReportCode` is a typed value with a stable registry, not an arbitrary
  string.
- `StableId` can be refined into `EntityId`, `ConstraintId`, `ContextId`,
  `RigidSetId`, `StateVersionId`, and `TraceId`.
- `ContractResult<T>` is the default shape for structured module outputs.
- Reports carry machine-readable subjects and short human summaries.
- Long explanations belong in optional detail fields or external trace
  artifacts, not as the only evidence.

## Kernel Target Design

Mission: durable mathematical truth.

Structured inputs:

- `ModelDraft`: mutable construction input before validation.
- `ModelSnapshot`: immutable, versioned, validated domain state.
- `ContextRequest`: request for a whole-model, component, rigid-set,
  subproblem, overlap, or gauge context.
- `StateDelta`: proposed state change against a base version.
- `SnapshotDiffRequest`: deterministic comparison between two snapshots.

Structured outputs:

- `ModelValidationReport`.
- `ContextValidationReport`.
- `ModelSnapshot`.
- `ContextSnapshot`.
- `SnapshotDiff`.
- `StateDeltaValidationReport`.

Target public API:

```cpp
export namespace gcs::kernel {

ContractResult<ModelSnapshot> make_snapshot(ModelDraft draft);
ContractResult<ModelValidationReport> validate_model(const ModelSnapshot& snapshot);
ContractResult<ContextSnapshot> make_context(const ModelSnapshot& snapshot,
                                             ContextRequest request);
ContractResult<ContextValidationReport> validate_context(const ModelSnapshot& snapshot,
                                                         const ContextSnapshot& context);
ContractResult<SnapshotDiff> diff_snapshots(const ModelSnapshot& before,
                                            const ModelSnapshot& after);
ContractResult<StateDeltaValidationReport> validate_delta(const ModelSnapshot& base,
                                                          const StateDelta& delta);

}
```

Implementation responsibilities:

- ID allocation and duplicate detection.
- Schema/version validation.
- Parameter dimension and unit validation.
- Rigid-set membership validation.
- Context membership and coverage validation.
- State delta version and entity-state validation.
- Canonical diff and equality logic.

Contract tests:

- `kernel_ids_are_stable_after_snapshot_creation`.
- `kernel_rejects_duplicate_ids`.
- `kernel_rejects_missing_entity_references`.
- `kernel_rejects_invalid_parameter_dimensions`.
- `kernel_whole_context_covers_all_snapshot_members`.
- `kernel_state_delta_requires_matching_base_version`.
- `kernel_snapshot_diff_is_deterministic`.

## Constraint Catalog Target Design

Mission: own constraint semantics.

Structured inputs:

- `ConstraintDefinitionRequest`.
- `ConstraintValidationRequest`.
- `ResidualEvaluationRequest`.
- `JacobianEvaluationRequest`.
- `DegeneracyProbeRequest`.

Structured outputs:

- `ConstraintDefinition`.
- `ConstraintValidationReport`.
- `ResidualEvaluationResult`.
- `JacobianEvaluationResult`.
- `DegeneracyReport`.
- `CatalogVersionReport`.

Target public API:

```cpp
export namespace gcs::constraints {

const ConstraintCatalog& builtin_catalog();
ContractResult<ConstraintValidationReport> validate_constraint(
    const ConstraintCatalog& catalog,
    const kernel::ModelSnapshot& snapshot,
    kernel::ConstraintId constraint_id);
ContractResult<ResidualEvaluationResult> evaluate_residual(
    const ConstraintCatalog& catalog,
    ResidualEvaluationRequest request);
ContractResult<JacobianEvaluationResult> evaluate_jacobian(
    const ConstraintCatalog& catalog,
    JacobianEvaluationRequest request);
ContractResult<JacobianCheckReport> check_jacobian(
    const ConstraintCatalog& catalog,
    FiniteDifferenceCheckRequest request);

}
```

Implementation responsibilities:

- Constraint registry and versioning.
- Entity signature matching.
- Parameter schema validation.
- Residual shape validation.
- Analytic Jacobian provider dispatch.
- Finite-difference fallback and check tool.
- Degenerate geometry classification.

Contract tests:

- `catalog_declares_every_builtin_constraint`.
- `catalog_rejects_invalid_arity`.
- `catalog_rejects_invalid_entity_signature`.
- `catalog_rejects_invalid_parameter_schema`.
- `catalog_reports_residual_dimension`.
- `catalog_residual_dimension_matches_output_vector`.
- `catalog_analytic_jacobian_matches_finite_difference`.
- `catalog_reports_degenerate_geometry`.

## Incidence Graph Target Design

Mission: deterministic structural facts.

Structured inputs:

- `HypergraphBuildRequest`.
- `RigidGraphBuildRequest`.
- `StructuralQueryRequest`.
- `GraphDumpRequest`.

Structured outputs:

- `IncidenceHypergraph`.
- `EntityIncidenceIndex`.
- `ConstraintIncidenceIndex`.
- `RigidBodyGraph`.
- `ConnectedComponents`.
- `SeparatorReport`.
- `StructuralReport`.
- `GraphDump`.

Target public API:

```cpp
export namespace gcs::graph {

ContractResult<IncidenceHypergraph> build_hypergraph(
    const kernel::ModelSnapshot& snapshot,
    HypergraphBuildOptions options);
ContractResult<IncidenceIndices> build_indices(
    const IncidenceHypergraph& hypergraph);
ContractResult<RigidBodyGraph> build_rigid_body_graph(
    const kernel::ModelSnapshot& snapshot,
    const IncidenceHypergraph& hypergraph);
ContractResult<SeparatorReport> find_separators(
    const IncidenceHypergraph& hypergraph,
    SeparatorOptions options);
ContractResult<GraphDump> dump_graph(const IncidenceHypergraph& hypergraph,
                                     GraphDumpRequest request);

}
```

Implementation responsibilities:

- Entity-constraint hypergraph construction.
- Reverse incidence indices.
- Component, articulation, and biconnected decomposition.
- Rigid-set/body graph projection.
- Malformed edge quarantine with typed evidence.
- Deterministic ordering and graph dump formatting.

Contract tests:

- `graph_builds_hyperedges_for_constraints`.
- `graph_reverse_index_names_all_constraints_per_entity`.
- `graph_components_cover_each_entity_once`.
- `graph_reports_missing_entity_reference`.
- `graph_rigid_body_projection_is_deterministic`.
- `graph_separator_report_is_stable`.
- `graph_dump_is_canonical`.

## Decomposition Planner Target Design

Mission: choose the local-to-global cover.

Structured inputs:

- `PlanningRequest`.
- `PlanningOptions`.
- `StructuralHints`.
- `DiagnosticHints`.
- `CapabilityProfile`.

Structured outputs:

- `PlanningResult`.
- `CoverPlan`.
- `ContextSnapshot[]`.
- `BoundaryProjection[]`.
- `Subproblem[]`.
- `SolveDag`.
- `SolveDagValidationReport`.
- `GaugePolicy`.
- `UnsupportedPlanReport`.

Target public API:

```cpp
export namespace gcs::planning {

ContractResult<PlanningResult> plan_decomposition(
    const kernel::ModelSnapshot& snapshot,
    const graph::IncidenceIndices& indices,
    PlanningRequest request);
ContractResult<CoverValidationReport> validate_cover(
    const kernel::ModelSnapshot& snapshot,
    const CoverPlan& cover);
ContractResult<SolveDagValidationReport> validate_solve_dag(
    const PlannerOutput& output);

}
```

Implementation responsibilities:

- Whole-model, connected-component, rigid-cluster, and separator-based covers.
- Boundary projection creation.
- Gauge policy selection.
- Solve DAG construction and cycle detection.
- Coverage proof and unsupported-case evidence.
- Rank and diagnostic hint consumption without owning diagnostics.

Contract tests:

- `planner_whole_model_cover_covers_all_requested_ids`.
- `planner_component_cover_keeps_components_disjoint`.
- `planner_overlap_contexts_have_boundary_projections`.
- `planner_solve_dag_is_acyclic`.
- `planner_solve_dag_explains_boundary_projection_dependencies`.
- `planner_gauge_policy_is_explicit`.
- `planner_returns_unsupported_for_unknown_capability_gap`.
- `planner_output_is_deterministic`.

## Numeric Engine Target Design

Mission: produce local sections with numeric evidence.

Structured inputs:

- `NumericTask`.
- `NumericOptions`.
- `InitialState`.
- `ScalingPolicy`.
- `ParameterizationPolicy`.
- `JacobianPolicy`.
- `LinearSolverPolicy`.
- `TracePolicy`.

Structured outputs:

- `NumericReport`.
- `LocalSection`.
- `ResidualReport`.
- `JacobianReport`.
- `RankConditionReport`.
- `IterationTrace`.
- `NumericFailureReport`.

Target public API:

```cpp
export namespace gcs::numeric {

ContractResult<NumericTaskValidationReport> validate_task(
    const NumericTask& task);
ContractResult<EquationAssembly> assemble_equations(
    const NumericTask& task,
    const constraints::ConstraintCatalog& catalog);
ContractResult<NumericReport> solve_local(
    const NumericTask& task,
    const constraints::ConstraintCatalog& catalog,
    NumericOptions options);
ContractResult<JacobianCheckReport> check_task_jacobian(
    const NumericTask& task,
    const constraints::ConstraintCatalog& catalog,
    FiniteDifferenceCheckOptions options);

}
```

Implementation responsibilities:

- Task validation.
- Residual assembly through the constraint catalog.
- Analytic or finite-difference Jacobian assembly.
- Scaling and damping.
- Dense damped Gauss-Newton baseline with trust-region step clamp until a
  sparse or external backend is introduced through the same contracts.
- Manifold retraction and update.
- Convergence policy based on max absolute residual value, with residual norm
  retained as report and trace evidence.
- Rank and conditioning estimation over the free Jacobian columns that remain
  after boundary-variable policy is applied, while preserving full and frozen
  variable dimensions as report evidence.
- Condition evidence suppression for rank-deficient free Jacobians.
- Boundary variable handling.
- Iteration trace recording.

Contract tests:

- `numeric_rejects_missing_active_entity`.
- `numeric_rejects_missing_active_constraint`.
- `numeric_assembly_dimensions_match_catalog`.
- `numeric_zero_residual_fixture_converges`.
- `numeric_reports_underconstrained_rank`.
- `numeric_rank_evidence_uses_only_free_boundary_columns`.
- `numeric_reports_condition_estimate`.
- `numeric_does_not_publish_condition_estimate_for_singular_rank`.
- `numeric_converges_when_each_residual_is_within_tolerance`.
- `numeric_boundary_variables_are_not_silently_mutated`.
- `numeric_trace_is_replayable`.

## Diagnostics Target Design

Mission: explain and certify solve status.

Structured inputs:

- `DiagnosticRequest`.
- `DiagnosticPhase`.
- `DofAnalysisRequest`.
- `ResidualAnalysisRequest`.
- `GluingRequest`.
- `ConflictSearchRequest`, carrying `ModelSnapshot` plus `ResidualReport` so
  residual conflicts can be projected to entity subjects.
- `RedundancySearchRequest`, carrying `ModelSnapshot`, `ContextSnapshot`,
  `DofReport`, and `RankReport` so duplicate signatures and over-constrained
  evidence remain separate.

Structured outputs:

- `DiagnosticReport`.
- `DofReport`.
- `RankReport`.
- `ResidualReport`.
- `BoundaryAgreementReport`.
- `GluingReport`.
- `ConflictSet[]`.
- `RedundancySet[]`.
- `ObstructionReport`.
- `StatusPrecedenceTrace`.

Target public API:

```cpp
export namespace gcs::diagnostics {

ContractResult<DofReport> analyze_dof(DofAnalysisRequest request);
ContractResult<ResidualReport> analyze_residuals(ResidualAnalysisRequest request);
ContractResult<GluingReport> glue_sections(GluingRequest request);
ContractResult<std::vector<ConflictSet>> find_conflicts(ConflictSearchRequest request);
ContractResult<std::vector<RedundancySet>> find_redundancies(RedundancySearchRequest request);
ContractResult<DiagnosticReport> diagnose(DiagnosticRequest request);
ContractResult<StatusPrecedenceTrace> resolve_status(
    std::span<const StageReport> reports,
    StatusPrecedencePolicy policy);

}
```

Implementation responsibilities:

- Pre-solve structural diagnostics.
- Post-local-solve numeric diagnostics.
- Rank evidence propagation from numeric reports, preserving full active
  variables, free solve variables, and frozen boundary variables separately.
- Projection-aware boundary comparison.
- Gauge consistency checks.
- Conflict and redundancy search.
- Residual conflict and over-constrained redundancy candidate generation.
- Residual conflict subject minimization to unsatisfied constraints and their
  owning entities.
- Exact duplicate constraint redundancy detection before broad context-level
  over-constrained fallback.
- Obstruction classification and minimization.
- Deterministic status precedence.

Contract tests:

- `diagnostics_distinguishes_structural_dof_from_numeric_rank`.
- `diagnostics_accepts_compatible_local_sections`.
- `diagnostics_rejects_mismatched_boundary_projection`.
- `diagnostics_returns_obstruction_for_failed_gluing`.
- `diagnostics_minimal_conflict_names_stable_ids`.
- `diagnostics_status_precedence_is_deterministic`.
- `diagnostics_redundancy_report_is_structured`.
- `diagnostics_redundancy_prefers_exact_duplicate_constraints`.
- `diagnostics_propagates_boundary_frozen_numeric_rank_evidence`.

## Session Runtime Target Design

Mission: command workflow and atomic commit.

Structured inputs:

- `RuntimeCommand`.
- `CommandPreconditions`.
- `TransactionPolicy`.
- `RuntimeServices`.
- `ReplayRequest`.

Structured outputs:

- `CommandResult`.
- `TransactionTrace`.
- `HistoryEvent`.
- `RollbackReport`.
- `ReplayReport`.
- `RankEvidenceProjection`.
- `PostLocalDiagnosticReport`.
- `PostCommitVerificationReport`.

Target public API:

```cpp
export namespace gcs::runtime {

class SessionRuntime {
public:
    explicit SessionRuntime(RuntimeServices services, kernel::ModelSnapshot initial);

    const kernel::ModelSnapshot& current_snapshot() const;
    ContractResult<CommandResult> execute(RuntimeCommand command);
    ContractResult<ReplayReport> replay(ReplayRequest request) const;
    ContractResult<HistoryView> history(HistoryQuery query) const;

private:
    class Transaction;
};

std::vector<RankEvidenceProjection> project_rank_evidence(
    const CommandResult& result);

}
```

Implementation responsibilities:

- Command validation.
- Kernel model validation before any constraint, planning, numeric, or viewer
  boundary work.
- Constraint catalog validation as its own recorded transaction stage after
  kernel validation succeeds.
- Dependency-injected planner, numeric, diagnostics, IO, and viewer adapters.
- Transaction snapshot and journal.
- Stage trace collection.
- Public rank-evidence projection for command summaries, viewer overlays, and
  promotion gates.
- Post-local diagnostic report collection before gluing.
- Atomic commit and rollback.
- Undo/redo history.
- Replay artifact generation.
- Post-commit verification.

Contract tests:

- `runtime_rejects_invalid_command_without_mutating_snapshot`.
- `runtime_stops_before_planning_when_kernel_validation_fails`.
- `runtime_stops_before_solving_when_planning_fails`.
- `runtime_stops_before_commit_when_numeric_fails`.
- `runtime_stops_before_commit_when_gluing_fails`.
- `runtime_accepted_command_advances_state_version_once`.
- `runtime_projects_rank_evidence_from_accepted_command_result`.
- `runtime_post_local_diagnostics_preserve_numeric_evidence`.
- `runtime_replay_reconstructs_stage_trace`.
- `runtime_undo_redo_preserves_history_order`.

## IO Adapters Target Design

Mission: versioned scene intake/export and fixture reproducibility.

Structured inputs:

- `SceneLoadRequest`.
- `SceneWriteRequest`.
- `SceneNormalizeRequest`.
- `SceneMigrationRequest`.
- `SceneRoundTripRequest`.

Structured outputs:

- `SceneLoadResult`.
- `SceneWriteResult`.
- `SceneValidationReport`.
- `SceneMigrationReport`.
- `RoundTripDiffReport`.
- `CanonicalDigest`.

Target public API:

```cpp
export namespace gcs::io {

ContractResult<SceneLoadResult> load_scene(SceneLoadRequest request,
                                           const SceneSchemaRegistry& schemas);
ContractResult<SceneWriteResult> write_scene(SceneWriteRequest request,
                                             const SceneSchemaRegistry& schemas);
ContractResult<SceneMigrationReport> migrate_scene(SceneMigrationRequest request,
                                                   const SceneSchemaRegistry& schemas);
ContractResult<RoundTripDiffReport> round_trip(SceneRoundTripRequest request);

}
```

Implementation responsibilities:

- Schema registry.
- Canonical text and JSON serializer.
- Bounded JSON reader for the canonical scene subset, with typed parse errors
  and no mandatory third-party JSON dependency.
- Explicit migration pipeline.
- Typed parse errors.
- Deterministic digest.
- Fixture linter and corpus loader.

Contract tests:

- `io_loads_current_schema_fixture`.
- `io_rejects_unknown_required_field`.
- `io_migrates_old_schema_with_report`.
- `io_write_is_byte_deterministic`.
- `io_load_write_load_preserves_stable_ids`.
- `io_round_trip_diff_names_changed_subjects`.

## Viewer Bridge Target Design

Mission: read-only projection for GUI/API consumers.

Structured inputs:

- `ViewerProjectionRequest`.
- `DiagnosticOverlayRequest`.
- `InteractionDraftRequest`.
- `HistoryFrameRequest`.

Structured outputs:

- `ViewerSceneProjection`.
- `DiagnosticOverlay`.
- `InteractionCommandDraft`.
- `HistoryFrameProjection`.
- `SnapshotSummary` with public rank, residual, conflict, redundancy, and
  obstruction evidence projections.

Target public API:

```cpp
export namespace gcs::viewer {

ContractResult<ViewerSceneProjection> project_scene(ViewerProjectionRequest request);
ContractResult<DiagnosticOverlay> build_overlay(DiagnosticOverlayRequest request);
ContractResult<InteractionCommandDraft> draft_command(InteractionDraftRequest request);
ContractResult<HistoryFrameProjection> project_history_frame(HistoryFrameRequest request);

}
```

Implementation responsibilities:

- Stable ID projection.
- Diagnostic overlay mapping from reports.
- Runtime rank-evidence projection mapping into overlays and summaries.
- Post-local residual evidence projection mapping into overlays and summaries.
- Conflict, redundancy, and obstruction responsibility evidence mapping into
  overlays and summaries.
- Selection and hit-test mapping.
- Interaction-to-runtime-command drafting.
- History frame projection.

Contract tests:

- `viewer_projection_is_deterministic`.
- `viewer_projection_contains_state_version`.
- `viewer_overlay_derives_status_from_reports`.
- `viewer_overlay_projects_boundary_frozen_rank_evidence`.
- `viewer_overlay_projects_residual_and_conflict_evidence`.
- `viewer_overlay_projects_redundancy_evidence`.
- `viewer_overlay_projects_gluing_obstruction_evidence`.
- `viewer_command_draft_validates_against_runtime_contract`.
- `viewer_history_frame_resolves_stable_ids`.

## Contract Tools Target Design

Mission: deterministic support for tests and architecture audits.

Structured inputs:

- `FixtureBuildRequest`.
- `InvariantCheckRequest`.
- `CorpusGenerationRequest`.
- `GoldenReportRequest`.
- `DependencyAuditRequest`.

Structured outputs:

- `FixtureBundle`.
- `InvariantReport`.
- `GeneratedCorpus`.
- `GoldenReport`.
- `DependencyAuditReport`.

Target public API:

```cpp
export namespace gcs::contract_tools {

ContractResult<FixtureBundle> build_fixture(FixtureBuildRequest request);
ContractResult<InvariantReport> check_invariants(InvariantCheckRequest request);
ContractResult<GeneratedCorpus> generate_corpus(CorpusGenerationRequest request);
ContractResult<GoldenReport> write_golden_report(GoldenReportRequest request);
ContractResult<DependencyAuditReport> audit_module_dependencies(DependencyAuditRequest request);

}
```

Implementation responsibilities:

- Deterministic fixture generation.
- Fixture provenance metadata.
- Reusable fixture classes for boundary-frozen rank evidence,
  tolerance-edge residual stopping, separator-chain decomposition structure,
  redundant rank-deficient equations, and gluing obstruction scenarios.
- Invariant checking through public contracts.
- Golden report generation.
- Module dependency scanning.
- No production solver policy.

Contract tests:

- `tools_fixture_generation_is_seed_deterministic`.
- `tools_generated_fixture_passes_kernel_validation`.
- `tools_invariant_report_names_all_failures`.
- `tools_boundary_frozen_fixture_carries_solve_intent_hint`.
- `tools_tolerated_residual_fixture_exercises_max_abs_stopping`.
- `tools_separator_chain_fixture_names_shared_separator_entity`.
- `tools_dependency_audit_rejects_forbidden_imports`.

## Contract Test Architecture

The current monolithic smoke test file is replaced by contract suites that
import public C++23 modules only. The current bootstrap suites are:

```text
tests/contracts/kernel/kernel_contract_tests.cpp
tests/contracts/constraint_catalog/constraint_catalog_contract_tests.cpp
tests/contracts/incidence_graph/incidence_graph_contract_tests.cpp
tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp
tests/contracts/numeric_engine/numeric_engine_contract_tests.cpp
tests/contracts/diagnostics/diagnostics_contract_tests.cpp
tests/contracts/session_runtime/session_runtime_contract_tests.cpp
tests/contracts/io_adapters/io_adapters_contract_tests.cpp
tests/contracts/viewer_bridge/viewer_bridge_contract_tests.cpp
tests/contracts/contract_tools/contract_tools_contract_tests.cpp
tests/contracts/module_dependency/module_dependency_contract_tests.cpp
tests/contracts/quality/cross_module_quality_contract_tests.cpp
tests/contracts/pipeline/pipeline_contract_tests.cpp
```

Target test layout:

```text
tests/contracts/kernel/kernel_contract_tests.cpp
tests/contracts/constraint_catalog/constraint_catalog_contract_tests.cpp
tests/contracts/incidence_graph/incidence_graph_contract_tests.cpp
tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp
tests/contracts/numeric_engine/numeric_engine_contract_tests.cpp
tests/contracts/diagnostics/diagnostics_contract_tests.cpp
tests/contracts/session_runtime/session_runtime_contract_tests.cpp
tests/contracts/io_adapters/io_adapters_contract_tests.cpp
tests/contracts/viewer_bridge/viewer_bridge_contract_tests.cpp
tests/contracts/contract_tools/contract_tools_contract_tests.cpp
tests/contracts/module_dependency/module_dependency_contract_tests.cpp
tests/contracts/quality/cross_module_quality_contract_tests.cpp
```

Test principles:

- Tests import public C++23 modules only.
- Tests assert structured contracts, not private implementation details.
- Cross-module suites assert report-code propagation, state-version behavior,
  and boundary projection evidence across public modules only.
- Negative cases are first-class.
- Every failure test asserts a stable report code and stable subject IDs.
- Numeric tests use tolerance policies and report evidence, not exact incidental
  iteration traces.
- Golden files are canonical JSON report snapshots, not prose logs.
- Each suite has CTest labels: `contract`, module name, and risk category.

Recommended CMake shape:

```cmake
add_executable(gcs_kernel_contract_tests
  tests/contracts/kernel/kernel_contract_tests.cpp
)
target_link_libraries(gcs_kernel_contract_tests
  PRIVATE gcs_solver GTest::gtest_main
)
gtest_discover_tests(gcs_kernel_contract_tests
  PROPERTIES LABELS "contract;kernel"
)
```

GoogleTest remains test-only and follows `third-party-policy.md`: installed
package first, vendored source second, opt-in FetchContent only when explicitly
enabled.

## Contract Fixture Strategy

Fixture directory:

```text
fixtures/contracts/
  kernel/
  constraints/
  graph/
  planning/
  numeric/
  diagnostics/
  runtime/
  io/
  viewer/
```

Each fixture bundle includes:

- `input.gcs.json`;
- `expected_report.gcs.json`;
- `metadata.json` with schema version, deterministic seed, module owner,
  expected status, and relevant stable IDs.

Fixture classes:

- minimal valid model;
- duplicate identity;
- missing references;
- isolated components;
- shared-boundary cover;
- valid zero-residual solve;
- under-constrained solve;
- over-constrained solve;
- redundant constraint;
- inconsistent constraints;
- singular numeric case;
- gluing obstruction;
- schema migration case;
- viewer projection case.

## Implementation Sequence From This Design

1. Delete current C++ skeleton and monolithic tests when the replacement branch
   starts.
2. Create the target module directory layout and empty C++23 module facades.
3. Implement `gcs.kernel` common contract layer and kernel contract tests.
4. Implement `gcs.constraint_catalog` definitions, schemas, residual/Jacobian
   contracts, and tests.
5. Implement `gcs.incidence_graph` hypergraph and structural tests.
6. Implement `gcs.decomposition_planner` cover contracts and tests.
7. Implement `gcs.numeric_engine` equation assembly and local solve contracts.
8. Implement `gcs.diagnostics` proof and obstruction contracts.
9. Implement `gcs.session_runtime` transaction orchestration and replay.
10. Implement `gcs.io_adapters`, `gcs.viewer_bridge`, and support tools.
11. Add cross-module contract suites and dependency gates.

The implementation should not carry over temporary public APIs unless they
match this target design.

## Definition Of Done

A module is ready for implementation only when:

- its structured input and output contracts are named;
- its report codes are registered;
- its tools have typed input/output and side-effect policy;
- its core agent and skill are defined in `62-module-agents.md`;
- its contract test suite is named;
- its fixtures and expected reports are planned;
- its dependency direction is explicitly checked.

A module implementation is done only when:

- C++23 module interface and implementation compile;
- contract tests pass;
- negative cases produce typed reports;
- traces or golden reports are replayable;
- no lower module imports forbidden boundary modules;
- docs and tests agree on public contract names.
