# Core Module

## Purpose

`core` owns the shared C++ model used by every solver module. It deliberately separates structural data from behavior intent.

## Files

```text
GCS/core/types.h
GCS/core/core.h
GCS/core/core.cpp
```

## Key Types

```cpp
namespace gcs {
enum class GeometryType { Point, Line, Plane };
enum class ConstraintType { Coincident, Parallel, Perpendicular, Distance, Angle };
enum class SolveMode { Update, Drag, Simulation };

struct RigidSet;
struct Geometry;
struct Constraint;
struct BehaviorModel;
struct HistoryAction;
struct Manager;
}
```

## Model Split

Structural model:

- `RigidSet`: grouping boundary for rigid-body or sketch-group behavior.
- `Geometry`: solver-facing entity parameters.
- `Constraint`: relation between geometry IDs plus optional numeric value.

Behavior model:

- `SolveMode::Update`: recompute positions to satisfy constraints.
- `SolveMode::Drag`: move selected geometry along remaining DOF.
- `SolveMode::Simulation`: move toward target constraints while preserving other constraints.
- `fixedGeometryIds`, `drivenGeometryIds`, and `targetConstraintIds`: lightweight intent lists for future interactive behavior.

## Rules

- `core` depends only on the C++ standard library.
- Other modules include it with `#include "core/core.h"`.
- `types.h` stays separate so enum definitions can remain lightweight.
- `core` does not own UI state, file paths, or numeric solver state.
