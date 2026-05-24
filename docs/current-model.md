# GCS Core

This folder contains the C++ solver core, local scene fixtures, tests, and the lightweight Python visualization package.

## Model

The C++ model is stored as immutable `gcs::kernel::ModelSnapshot` values
during solver execution.

Structural model:

- `RigidSet`: groups geometry for rigid-body or sketch-group behavior.
- `Geometry`: point, line, or plane with six numeric parameters.
- `Constraint`: geometric relation plus optional numeric value.

Constraint incidence rule:

- Constraint endpoints must reference geometries from different rigid sets.
  Same-rigid-set endpoints are invalid model data because the rigid set already
  represents one body-level parameter block.

Behavior model:

- `SolveMode::Update`: solve the current constraint graph.
- `SolveMode::Drag`: reserved for interactive movement along remaining DOF.
- `SolveMode::Simulation`: reserved for target-driven motion.
- `fixed_geometry_ids`, `driven_geometry_ids`, `target_constraint_ids` in JSON
  `behavior`: scene-facing intent lists that map to
  `ModelSnapshot.solve_intent`.

## Text Scene Format

```text
numRigidSets
rigidSetId...
numGeometries
geometryId geometryType rigidSetId
...
numConstraints
constraintId constraintType numConnectedGeometries geometryId...
...

geometryId v0 v1 v2 v3 v4 v5
...

constraintId value
...
```

Text scenes carry the structural model only. JSON scenes can also carry
`behavior` and `history`; current C++ IO treats `behavior` as solver input and
validates that every fixed, driven, or target ID resolves inside the scene.
Python `gcs_viz.algebra` writes current public JSON scenes with
`format_version: "gcs-0.3"` and the same behavior field names consumed by C++.
Older GUI-saved scenes with `format_version: 1` remain readable by Python and
are normalized to the current public shape when rewritten.

History policy:

- `behavior` is solver input and is loaded by C++ into `ModelSnapshot.solve_intent`.
- `history` is GUI/replay metadata owned by Python viewer tooling today.
- C++ JSON IO tolerates `history` fields but does not persist them in
  `ModelSnapshot`.
- Python `viewer_bridge.build_history_graph` replays supported construction
  actions and treats `Solve` as a non-mutating marker.

## Module Boundary

- `core`: model and type helpers.
- `io`: scene serialization.
- `dcm`: graph decomposition.
- `lgs`: DOF/status diagnostics.
- `cds`: numeric solving.
- `app`: demo executable facade.
- `python/gcs_viz`: local graph and geometry visualization.
