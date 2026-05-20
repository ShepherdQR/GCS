# GCS Architecture Map

## Read Order

Start with `docs/architecture/README.md`. Load only the next file needed:

- Foundations: `docs/architecture/00-foundations/problem-formulation.md`, `docs/architecture/00-foundations/architectural-principles.md`
- System shape: `docs/architecture/10-system/system-topology.md`, `docs/architecture/10-system/current-to-target-map.md`
- Pipeline: `docs/architecture/20-solver-pipeline/pipeline.md`, `decomposition-planning.md`, `numerical-solving.md`
- Contracts: `docs/architecture/30-contracts/domain-contracts.md`, `solver-contracts.md`
- Quality: `docs/architecture/40-quality/verification-strategy.md`

## Target Vocabulary

- `kernel`: durable domain entities, constraints, IDs, tolerances, coordinates.
- `constraint_catalog`: residual definitions, signatures, Jacobians, DOF metadata.
- `incidence_graph`: hypergraph/body graph projections and structural indices.
- `decomposition_planner`: rigidity, clustering, solve ordering, subproblem extraction.
- `diagnostics`: DOF, rank, residual, conflicts, redundancy, reports.
- `numeric_engine`: equation assembly, scaling, damping, convergence reports.
- `session_runtime`: commands, transactions, behavior modes, history, undo.
- `io_adapters`: versioned scene import/export and fixtures.
- `viewer_bridge`: read-only visualization and interaction bridge.

## Current Physical Names

The current implementation is physically staged under target-oriented paths such as `src/gcs/kernel`, `src/gcs/incidence_graph`, `src/gcs/diagnostics`, `src/gcs/numeric_engine`, `src/gcs/io_adapters`, `src/gcs/session_runtime`, and `python/gcs_viz`. Some prototype namespaces and class names still reflect the old implementation; treat those as migration debt.
