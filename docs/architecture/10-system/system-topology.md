# System Topology

## Target Modules

```text
kernel
  |
  +-- constraint_catalog
  +-- incidence_graph
  |     |
  |     +-- decomposition_planner
  |
  +-- diagnostics
  |     |
  |     +-- decomposition_planner
  |
  +-- numeric_engine
  |     |
  |     +-- constraint_catalog
  |
  +-- session_runtime
        |
        +-- io_adapters
        +-- viewer_bridge
```

This drawing shows conceptual dependencies. Implementations may split headers,
packages, or libraries differently, but the direction must remain stable:
lower mathematical layers do not call UI, IO, app lifecycle, or visualization.

## Responsibilities

| Module | Responsibility |
| --- | --- |
| `kernel` | Typed entities, constraints, IDs, parameter state, units, tolerances. |
| `constraint_catalog` | Residual definitions, Jacobians, dimension metadata, validation rules. |
| `incidence_graph` | Hypergraph projections, connected components, structural indices. |
| `decomposition_planner` | Rigidity analysis, clustering, ordering, subproblem extraction. |
| `diagnostics` | DOF/rank/status/residual/conflict/redundancy analysis. |
| `numeric_engine` | Equation assembly, scaling, damping, manifold updates, convergence reports. |
| `session_runtime` | User intent, commands, transactions, history, orchestration. |
| `io_adapters` | Versioned import/export, fixture loading, reproducible serialization. |
| `viewer_bridge` | Observability and interaction bridge; never owns solver truth. |

## Dependency Rules

- `kernel` depends only on the standard runtime and small math primitives.
- `constraint_catalog` depends on `kernel`.
- `incidence_graph` depends on `kernel`.
- `decomposition_planner` depends on `kernel`, `incidence_graph`, and selected
  diagnostic primitives.
- `numeric_engine` depends on `kernel` and `constraint_catalog`; it consumes
  planner output but does not own planning policy.
- `diagnostics` may consume graph, planner, and numeric reports; it should not
  mutate coordinates.
- `session_runtime` is the orchestration layer and may call all domain services.
- `io_adapters` and `viewer_bridge` are boundary modules. They must not be
  imported by lower solver layers.
- `apps/gcs_cli` stays a thin executable shell and must not grow solver policy.
- `python/gcs_viz` consumes exported model snapshots, histories, and reports; it
  must not own durable solver truth.

## Physical Layout Mapping

The target topology maps directly to the repository layout:

- `src/gcs/kernel`
- `src/gcs/constraint_catalog` when residual/Jacobian catalog work begins
- `src/gcs/incidence_graph`
- `src/gcs/decomposition_planner` when structural planning work begins
- `src/gcs/diagnostics`
- `src/gcs/numeric_engine`
- `src/gcs/session_runtime`
- `src/gcs/io_adapters`
- `apps/gcs_cli`
- `python/gcs_viz`
- `fixtures/scene`

## Core Data Flow

```text
input scene or runtime command
  -> io_adapters / session_runtime
  -> kernel model validation
  -> incidence_graph indices
  -> decomposition_planner solve plan
  -> diagnostics pre-solve classification
  -> numeric_engine prepared tasks
  -> diagnostics post-solve verification
  -> session_runtime transaction commit
  -> viewer_bridge / io_adapters output
```

## Non-Goals For The Solver Core

The solver core should not contain:

- windowing or UI state;
- file path conventions;
- console formatting;
- application singleton state;
- visualization color or layout policy;
- mutable global tolerances;
- hidden fallback behavior that changes mathematical meaning.

These concerns can exist in boundary modules or applications, but never inside
the mathematical kernel or solver engines.
