# Core Module

## Purpose

`core` owns the shared C++ data model used by every solver module.

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

struct RigidSet;
struct Geometry;
struct Constraint;
struct HistoryAction;
struct Manager;
}
```

## Rules

- `core` depends only on the C++ standard library.
- Other modules include it with `#include "core/core.h"`.
- `types.h` stays separate so enum definitions can remain lightweight.
