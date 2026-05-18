# GCS Core

This folder contains the C++ solver core, local scene fixtures, tests, and the lightweight Python visualization package.

## Model

The C++ model is stored in `gcs::Manager`.

Structural model:

- `RigidSet`: groups geometry for rigid-body or sketch-group behavior.
- `Geometry`: point, line, or plane with six numeric parameters.
- `Constraint`: geometric relation plus optional numeric value.

Behavior model:

- `SolveMode::Update`: solve the current constraint graph.
- `SolveMode::Drag`: reserved for interactive movement along remaining DOF.
- `SolveMode::Simulation`: reserved for target-driven motion.
- `fixedGeometryIds`, `drivenGeometryIds`, `targetConstraintIds`: lightweight intent lists for future behavior.

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

Text scenes carry the structural model only. JSON scenes can also carry `behavior` and `history`.

## Module Boundary

- `core`: model and type helpers.
- `io`: scene serialization.
- `dcm`: graph decomposition.
- `lgs`: DOF/status diagnostics.
- `cds`: numeric solving.
- `app`: demo executable facade.
- `gcs_viz`: local graph and geometry visualization.

