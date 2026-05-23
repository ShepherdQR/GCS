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

## Next Milestone

Implement the incidence graph structure milestone:

- `IncidenceHypergraph` and deterministic hyperedge IDs.
- Entity and constraint reverse indices.
- Rigid-set/body graph projection.
- Connected-component coverage proof.
- Malformed edge quarantine reports.
- Canonical graph dump.
- `tests/contracts/incidence_graph/incidence_graph_contract_tests.cpp`.
