# C++23 Module Solver Architecture

## Purpose

This document records the first implementation shape for the topos-inspired
GCS rewrite. It is the C++ realization of the architecture in
`00-foundations/`, `10-system/`, `20-solver-pipeline/`, and `30-contracts/`.

The implementation must use C++23 modules. Public module interfaces live in
`.cppm` files, implementation units live in `.cpp` files, and CMake must list
module interface files in a `CXX_MODULES` file set. New solver code should not
fall back to legacy header-first architecture unless this document is updated.

## Implementation Thesis

The C++ solver is not a monolithic numeric engine. It is a contract pipeline:

```text
ModelSnapshot
  -> IncidenceIndices
  -> CoverPlan
  -> NumericTask*
  -> LocalSection*
  -> GluingReport
  -> CommandResult
```

Decomposition is cover selection. Numeric solving produces local sections.
Assembly is gluing. Runtime commit is allowed only after diagnostics produce an
accepted gluing report or an explicit obstruction.

## Module Layout

```text
src/gcs/kernel
src/gcs/constraint_catalog
src/gcs/incidence_graph
src/gcs/decomposition_planner
src/gcs/numeric_engine
src/gcs/diagnostics
src/gcs/session_runtime
src/gcs/io_adapters
src/gcs/viewer_bridge
src/gcs/tools
apps/gcs_cli
tests
```

## Subsystem Contracts

| Module | Structured input | Structured output | Basic tools |
| --- | --- | --- | --- |
| `kernel` | Domain constructors and snapshots. | Stable IDs, snapshots, contexts, reports. | Lookup, naming, DOF helpers, whole-model context builder. |
| `constraint_catalog` | `ConstraintValidationInput`. | `ConstraintValidationResult`. | Built-in definitions, signature checks, generic DOF lookup. |
| `incidence_graph` | `IncidenceInput`. | `IncidenceIndices`. | Entity incidence, connected components. |
| `decomposition_planner` | `PlannerInput`. | `PlannerOutput`. | `CoverPlan`, subproblems, gauge policy, solve order. |
| `numeric_engine` | `NumericTask`. | `NumericReport`. | Local section construction, rank/residual placeholder metrics. |
| `diagnostics` | `DiagnosticInput`, `GluingInput`. | `DiagnosticOutput`, `GluingReport`. | DOF analysis, obstruction creation, local-section gluing. |
| `session_runtime` | `Command`. | `CommandResult`. | End-to-end orchestration and state-version commit. |
| `io_adapters` | `SceneLoadRequest`. | `SceneLoadResult`. | Text scene loading and summaries. |
| `viewer_bridge` | `ModelSnapshot`, `CommandResult`. | `SnapshotSummary`. | Read-only reporting projections. |
| `tools` | Test/developer requests. | Deterministic sample snapshots. | Minimal scene builders. |

The table above records the first implementation skeleton. The detailed design
standard is now governed by:

- `docs/architecture/60-agentic-submodule-design-analysis.md`;
- `docs/architecture/61-agentic-module-framework.md`;
- `docs/architecture/62-module-agents.md`.
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`.

Before expanding a module beyond the skeleton, define or update its structured
input contracts, structured output contracts, module tools, core agent, core
skill, guardrails, trace events, and eval gates. The implementation remains
C++23-module-first: public interfaces stay in `.cppm`, implementation units
stay in `.cpp`, and CMake tracks module interfaces through `CXX_MODULES`.

## Required Implementation Order

1. Define `kernel` immutable model, IDs, state versions, contexts, boundaries,
   reports, and helper functions.
2. Build `constraint_catalog` so residual and DOF semantics are centralized.
3. Build `incidence_graph` with entity incidence and connected components.
4. Build `decomposition_planner`; initially it may emit only whole-model or
   connected-component covers.
5. Build `numeric_engine` as a local-section producer behind `NumericTask`.
6. Build `diagnostics` with DOF classification, gluing, and obstruction
   reports.
7. Build `session_runtime` as the only full command orchestrator.
8. Keep `io_adapters`, `viewer_bridge`, CLI, and tests as consumers of public
   contracts.

## GTest Strategy

Tests use GoogleTest style and should validate contracts, not internal solver
implementation details. CMake should follow `third-party-policy.md`: first look
for an installed `GTest` package, then optionally use `third_party/googletest`,
then use opt-in `FetchContent` only when requested. Fetching GoogleTest is
opt-in to keep dependencies minimal and avoid surprising network access during
normal builds.

The initial tests cover:

- stable kernel IDs and model lookup;
- constraint-catalog validation;
- incidence/decomposition cover generation;
- runtime solve command producing a gluing report.

## Non-Goals For This Skeleton

- Full nonlinear solving.
- Full JSON scene compatibility.
- Specialized construction solvers.
- UI behavior.
- Restoring legacy `dcm`, `lgs`, `cds`, or singleton `App` APIs.
