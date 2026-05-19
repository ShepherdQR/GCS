# Scene Behavior Contract

## Text Scene Format

Text scenes carry structural graph data:

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

Keep text fixtures valid for existing parser tests.

## JSON Scene Format

JSON scenes may include:

- `format_version`
- `rigid_sets`
- `geometries`
- `constraints`
- `behavior`
- `history`

The C++ implementation lives in `GCS/io/io.cpp` and `GCS/core/core.h`. The Python implementation lives in `GCS/gcs_viz/algebra.py`.

## History Actions

Current action names should remain stable unless a migration is added:

- `AddRigidSet`
- `AddGeometry`
- `AddConstraint`
- `RemoveRigidSet`
- `RemoveGeometry`
- `RemoveConstraint`
- `UpdateConstraint`
- `Solve`

Each action stores an explicit `payload` object. Replayers should tolerate `Solve` as a marker when they are only reconstructing topology.
