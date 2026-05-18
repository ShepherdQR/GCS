# Core Module Architecture

## Module Name

**Core** — GCS Core Data Model

## Module Purpose

The Core module defines the fundamental data structures that represent a geometric constraint problem. It provides:

- **Geometry** entities: Point, Line, Plane — the geometric primitives that form the constraint graph
- **Constraint** entities: Coincident, Parallel, Perpendicular, Distance, Angle — the relationships between geometries
- **RigidSet**: A group of geometries that move as a rigid body
- **Manager**: The top-level container that holds the entire constraint graph
- **Type enumerations**: `GeometryType`, `ConstraintType` — type-safe replacements for magic numbers

The Core module is the **foundation** of the system. All other modules (IO, DCM, LGS, CDS) depend on Core, and Core depends on no other GCS module.

## Module Interface

### Header Files

```
include/gcs/types.h    ← GeometryType, ConstraintType enums
include/gcs/core.h     ← RigidSet, Geometry, Constraint, Manager, helper functions
```

### Key Types

```cpp
enum class GeometryType { Point = 0, Line = 1, Plane = 2 };
enum class ConstraintType { Coincident = 0, Parallel = 1, Perpendicular = 2, Distance = 3, Angle = 4 };

struct RigidSet {
    int id;
    std::vector<int> geometryIds;
};

struct Geometry {
    int id;
    GeometryType type;
    int rigidSetId;
    double v[6];
};

struct Constraint {
    int id;
    ConstraintType type;
    std::vector<int> geometryIds;
    double value;
};

struct Manager {
    std::vector<RigidSet> rigidSets;
    std::vector<Geometry> geometries;
    std::vector<Constraint> constraints;
};
```

### Helper Functions

```cpp
std::string typeNameGeometry(GeometryType t);
std::string typeNameConstraint(ConstraintType t);
```

### Future Class Hierarchy (Phase 2)

```cpp
class GeometryBase {
public:
    int id;
    int rigidSetId;
    virtual ~GeometryBase() = default;
    virtual GeometryType type() const = 0;
    virtual int dof() const = 0;
    virtual std::array<double, 6> getParams() const = 0;
    virtual void setParams(const std::array<double, 6>& p) = 0;
};

class PointGeometry : public GeometryBase {
    double x, y, z;
    GeometryType type() const override { return GeometryType::Point; }
    int dof() const override { return 3; }
};

class LineGeometry : public GeometryBase {
    double x1, y1, z1, x2, y2, z2;
    GeometryType type() const override { return GeometryType::Line; }
    int dof() const override { return 6; }
};

class PlaneGeometry : public GeometryBase {
    double x, y, z, nx, ny, nz;
    GeometryType type() const override { return GeometryType::Plane; }
    int dof() const override { return 6; }
};
```

```cpp
class ConstraintBase {
public:
    int id;
    std::vector<int> geometryIds;
    virtual ~ConstraintBase() = default;
    virtual ConstraintType type() const = 0;
    virtual int removedDof() const = 0;
    virtual double value() const { return 0.0; }
    virtual void setValue(double v) {}
};

class CoincidentConstraint : public ConstraintBase {
    ConstraintType type() const override { return ConstraintType::Coincident; }
    int removedDof() const override { return 3; }
};

class ParallelConstraint : public ConstraintBase {
    ConstraintType type() const override { return ConstraintType::Parallel; }
    int removedDof() const override { return 2; }
};

class PerpendicularConstraint : public ConstraintBase {
    ConstraintType type() const override { return ConstraintType::Perpendicular; }
    int removedDof() const override { return 1; }
};

class DistanceConstraint : public ConstraintBase {
    double dist;
    ConstraintType type() const override { return ConstraintType::Distance; }
    int removedDof() const override { return 1; }
    double value() const override { return dist; }
};

class AngleConstraint : public ConstraintBase {
    double angle;
    ConstraintType type() const override { return ConstraintType::Angle; }
    int removedDof() const override { return 1; }
    double value() const override { return angle; }
};
```

## Module Implementation

### Current State (Phase 1 — Complete)

- Flat structs with `GeometryType`/`ConstraintType` enum fields
- `double v[6]` parameter array for geometry values
- `typeNameGeometry()` and `typeNameConstraint()` inline helper functions
- No virtual dispatch, no heap allocation — simple and efficient

### Planned Evolution (Phase 2)

- Introduce `GeometryBase` / `ConstraintBase` abstract base classes
- Use `std::unique_ptr<GeometryBase>` in Manager for polymorphic storage
- Add `dof()` and `removedDof()` virtual methods for LGS integration
- Factory functions for creating geometry/constraint objects from type codes

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `double v[6]` for parameters | Uniform storage simplifies serialization; all geometry types fit in 6 doubles |
| Enum class instead of int | Type safety prevents invalid type codes; compiler-enforced |
| Flat structs in Phase 1 | Simplicity first; no virtual dispatch overhead; easy to understand |
| Class hierarchy in Phase 2 | OCP compliance; new types added without modifying existing code |
| `unique_ptr` in Manager | Polymorphic ownership; automatic memory management; no raw pointers |

## Module Test

### Unit Tests

| Test | Description |
|------|-------------|
| `test_types_enum_values` | Verify GeometryType and ConstraintType enum values match file format codes |
| `test_geometry_creation` | Create Geometry structs with each type, verify fields |
| `test_constraint_creation` | Create Constraint structs with each type, verify fields |
| `test_manager_empty` | Create empty Manager, verify zero sizes |
| `test_manager_populate` | Add rigid sets, geometries, constraints to Manager |
| `test_type_name_helpers` | Verify typeNameGeometry/typeNameConstraint return correct strings |
| `test_geometry_hierarchy` (Phase 2) | Verify polymorphic behavior of GeometryBase subclasses |
| `test_constraint_hierarchy` (Phase 2) | Verify polymorphic behavior of ConstraintBase subclasses |
| `test_dof_values` (Phase 2) | Verify dof() returns correct values for each geometry type |
| `test_removed_dof` (Phase 2) | Verify removedDof() returns correct values for each constraint type |

### Integration Tests

| Test | Description |
|------|-------------|
| `test_round_trip` | Create Manager → serialize → deserialize → verify equality |

## Module Performance

### Performance Characteristics

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Create Geometry | O(1) | Stack allocation, no heap |
| Create Manager | O(1) | Empty vectors |
| Add geometry to Manager | O(1) amortized | Vector push_back |
| Find geometry by ID | O(n) | Linear search; use map for O(1) in Phase 2 |
| Access geometry params | O(1) | Direct array access |

### Performance Targets

- Manager with 10,000 geometries: < 1ms to construct
- Parameter access: < 10ns per access
- Memory footprint: ~100 bytes per geometry, ~80 bytes per constraint

### Optimization Opportunities (Future)

- Replace linear ID lookups with `std::unordered_map<int, size_t>` index
- Use memory pool allocation for geometry/constraint objects
- Cache DOF computations in Manager

## Module Scalability

### Data Scalability

| Scale | Geometries | Constraints | Expected Performance |
|-------|-----------|-------------|---------------------|
| Small | < 100 | < 50 | Instant |
| Medium | 100 - 10,000 | 50 - 5,000 | < 100ms |
| Large | 10,000 - 1,000,000 | 5,000 - 500,000 | < 10s |
| Very Large | > 1,000,000 | > 500,000 | Requires decomposition (DCM) |

### Scalability Strategy

- Core data structures use `std::vector` for cache-friendly contiguous storage
- No global state — multiple Manager instances can coexist
- Phase 2 class hierarchy enables type-erased storage for heterogeneous collections

## Module Maintainability

### Code Organization

- `types.h` — Pure enum definitions, no dependencies
- `core.h` — Data structures and inline helpers, depends only on `types.h` and standard library
- Clear separation between type definitions and data structures

### Maintainability Practices

- All types are value-semantic (copyable, movable)
- No hidden state or side effects
- Inline helpers are trivially correct and testable
- Enum classes prevent invalid value creation

### Code Metrics Target

| Metric | Target |
|--------|--------|
| Cyclomatic complexity | < 5 per function |
| Lines of code | < 200 (types.h + core.h) |
| Header dependencies | < 5 per file |

## Module Extensibility

### Adding a New Geometry Type

1. Add new enum value to `GeometryType` (e.g., `Circle = 3`)
2. Add case to `typeNameGeometry()`
3. In Phase 2: Create new `CircleGeometry : public GeometryBase` class
4. No changes needed in DCM, LGS, or CDS if they use the abstract interface

### Adding a New Constraint Type

1. Add new enum value to `ConstraintType` (e.g., `Tangent = 5`)
2. Add case to `typeNameConstraint()`
3. In Phase 2: Create new `TangentConstraint : public ConstraintBase` class
4. CDS needs a new constraint equation implementation (expected extension point)

### Extension Points

| Extension Point | Mechanism |
|----------------|-----------|
| New geometry type | Add to GeometryType enum + create subclass |
| New constraint type | Add to ConstraintType enum + create subclass + implement equation |
| New parameter layout | Override getParams/setParams in geometry subclass |
| Custom serialization | Add new IO adapter without modifying Core |

## Module Reusability

### Reuse Scenarios

| Scenario | How Core Supports It |
|----------|---------------------|
| Different solver algorithms | Core provides data model only; solver is a separate module |
| Different input formats | IO module handles format specifics; Core is format-agnostic |
| Embedded in CAD application | Core has no UI or IO side effects; pure data model |
| Unit testing | All types are value-semantic; easy to construct test fixtures |
| Export to other tools | Manager data can be traversed and converted to any format |

### Reusability Principles

- **No IO coupling**: Core does not include `<fstream>` or `<iostream>`
- **No algorithm coupling**: Core has no solve/decompose methods
- **No platform coupling**: Core uses only C++ standard library
- **Self-contained**: Core depends only on `<vector>`, `<string>`, `<array>`
