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

Keep text fixtures valid for C++ and Python parsers.

## JSON Scene Format

JSON scenes may include:

- `format_version`
- `rigid_sets`
- `geometries`
- `constraints`
- `behavior`
- `history`

The C++ implementation lives in
`src/gcs/io_adapters/io_adapters.cpp` and
`src/gcs/kernel/kernel.cppm`. The Python implementation lives in
`python/gcs_viz/algebra.py`.

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

Each action stores an explicit `payload` object. Replayers should tolerate
`Solve` as a marker when they are only reconstructing topology.

## Expected Payload Shapes

- `AddRigidSet`: `{"id": int}`
- `RemoveRigidSet`: `{"id": int}`
- `AddGeometry`: `{"id": int, "type": int, "rigid_set_id": int, "v": [number, ...]}`
- `RemoveGeometry`: `{"id": int}`
- `AddConstraint`: `{"id": int, "type": int, "geometry_ids": [int, ...], "value": number}`
- `RemoveConstraint`: `{"id": int}`
- `UpdateConstraint`: `{"id": int, "value": number}`
- `Solve`: `{}`

## Compatibility Checklist

- Text fixtures still load when JSON-only fields are added.
- JSON scenes round-trip stable IDs, geometry parameters, constraint values,
  behavior fields, and history arrays.
- C++ `io_adapters` and Python `gcs_viz.algebra` agree on field names and enum
  integer values.
- Replay code can skip `Solve` markers and unknown future actions without
  corrupting the reconstructed topology.
- Saved scenes contain no absolute local paths or display-only state.
