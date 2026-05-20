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

The current implementation is physically staged under target-oriented paths such
as `src/gcs/kernel`, `src/gcs/incidence_graph`, `src/gcs/diagnostics`,
`src/gcs/numeric_engine`, `src/gcs/io_adapters`, `src/gcs/session_runtime`,
`python/gcs_viz`, and `tools/scene_generation`. Some prototype namespaces and
class names still reflect the old implementation; treat those as migration
debt.

## Boundary Decision Checklist

Before creating or moving code, answer:

- Which target module owns the durable truth?
- Is this code computing solver meaning, orchestrating a command, adapting IO, or only viewing a snapshot?
- Does a lower mathematical layer gain a dependency on UI, file paths, process launch, or local app state?
- Is the contract expressed as stable IDs, snapshots, deltas, reports, or explicit runtime commits?
- Is this a durable architecture rule that should update `docs/architecture/`, or a local implementation cleanup?

## Python Viewer Mapping

- `python/gcs_viz/algebra.py` mirrors scene/model structures for local tooling;
  keep it compatible with C++ IO when persistence changes.
- `python/gcs_viz/visualizer.py` is renderer policy, not solver truth.
- `python/gcs_viz/platform_gui.py` is application orchestration, not target
  `session_runtime`.
- A Python `viewer_bridge` or facade may be introduced as a read-only boundary
  over snapshots, histories, and reports. Do not let it own solver mutation.
- Temporary GUI history recording is acceptable during prototyping, but durable
  command semantics belong in `session_runtime`.

## Generation Tool Mapping

- `tools/scene_generation` is research and fixture-generation tooling, not a
  solver runtime layer.
- Generated `.store` data is scratch until explicitly promoted to
  `fixtures/scene`.
- Generator validation and repair reports may inform fixtures and diagnostics,
  but generator policy should not leak into the solver core.
