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
5. `in_progress` - add numeric task validation and equation assembly through the
   constraint catalog.
6. `pending` - add numeric residual/Jacobian/rank reports and baseline local
   solve tests.
7. `pending` - add diagnostics DOF/rank/residual/status precedence contracts.
8. `pending` - add projection-aware gluing obstruction and conflict/redundancy
   diagnostics.
9. `pending` - harden session runtime transaction, rollback, stage trace, and
   replay contracts.
10. `pending` - add IO schema registry, canonical text/JSON path, parse
    reports, round-trip diff, and fixture tests.
11. `pending` - add viewer projection, diagnostic overlay, interaction draft,
    and history projection contracts.
12. `pending` - split and harden contract tools: fixture provenance,
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
