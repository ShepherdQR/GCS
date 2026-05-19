# GCS Architecture Map

## Read Order

Start with `architecture/README.md`. Load only the next file needed:

- Foundations: `architecture/00-foundations/problem-formulation.md`, `architecture/00-foundations/architectural-principles.md`
- System shape: `architecture/10-system/system-topology.md`, `architecture/10-system/current-to-target-map.md`
- Pipeline: `architecture/20-solver-pipeline/pipeline.md`, `decomposition-planning.md`, `numerical-solving.md`
- Contracts: `architecture/30-contracts/domain-contracts.md`, `solver-contracts.md`
- Quality: `architecture/40-quality/verification-strategy.md`

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

## Current Names

The current implementation still uses `core`, `io`, `dcm`, `lgs`, `cds`, `app`, and `gcs_viz`. Keep current names when making small maintenance changes. Use target vocabulary for new architecture documents or rewrite planning.
