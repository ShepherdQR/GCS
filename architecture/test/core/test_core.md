# Core Interface Test Specification

## Module Under Test

`gcs::GeometryType`, `gcs::ConstraintType`, `gcs::RigidSet`, `gcs::Geometry`, `gcs::Constraint`, `gcs::Manager`

## Interface Contract

- Enum values map correctly to integer codes (file format compatibility)
- Structs can be created, populated, and queried
- Manager lookup functions work correctly
- Helper functions return correct values

## Test Cases

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| C01 | `test_core_enum_geometry_values` | `GeometryType` | Create each enum value | Cast to int | Point=0, Line=1, Plane=2 |
| C02 | `test_core_enum_constraint_values` | `ConstraintType` | Create each enum value | Cast to int | Coincident=0, Parallel=1, Perpendicular=2, Distance=3, Angle=4 |
| C03 | `test_core_geometry_create_point` | `Geometry` | Create Geometry with type=Point | Access fields | id, type, rigidSetId, v[0..5] match |
| C04 | `test_core_geometry_create_line` | `Geometry` | Create Geometry with type=Line | Access fields | id, type, rigidSetId, v[0..5] match |
| C05 | `test_core_geometry_create_plane` | `Geometry` | Create Geometry with type=Plane | Access fields | id, type, rigidSetId, v[0..5] match |
| C06 | `test_core_constraint_create` | `Constraint` | Create Constraint of each type | Access fields | id, type, geometryIds, value match |
| C07 | `test_core_rigidset_create` | `RigidSet` | Create RigidSet | Access fields | id, geometryIds match |
| C08 | `test_core_manager_empty` | `Manager` | Create default Manager | Check sizes | rigidSets=0, geometries=0, constraints=0 |
| C09 | `test_core_manager_populate` | `Manager` | Add 2 RS, 3 Geom, 1 Constr | Check sizes | sizes match counts |
| C10 | `test_core_manager_find_geometry` | `Manager::findGeometry` | Add 3 geometries (id 0,1,2) | findGeometry(1) | Returns pointer to geometry with id=1 |
| C11 | `test_core_manager_find_geometry_missing` | `Manager::findGeometry` | Add geometries (id 0,1) | findGeometry(99) | Returns nullptr |
| C12 | `test_core_manager_find_constraint` | `Manager::findConstraint` | Add 2 constraints (id 0,1) | findConstraint(0) | Returns pointer to constraint with id=0 |
| C13 | `test_core_manager_find_rigidset` | `Manager::findRigidSet` | Add 2 rigid sets (id 0,1) | findRigidSet(1) | Returns pointer to RS with id=1 |
| C14 | `test_core_helper_typename_geometry` | `typeNameGeometry` | Call with each GeometryType | Get string | "Point", "Line", "Plane" |
| C15 | `test_core_helper_typename_constraint` | `typeNameConstraint` | Call with each ConstraintType | Get string | "Coincident", "Parallel", "Perpendicular", "Distance", "Angle" |
| C16 | `test_core_helper_dof_geometry` | `dofGeometry` | Call with each GeometryType | Get int | Point=3, Line=6, Plane=6 |
| C17 | `test_core_helper_dof_removed_constraint` | `dofRemovedConstraint` | Call with each ConstraintType | Get int | Coincident=3, Parallel=2, Perpendicular=1, Distance=1, Angle=1 |

## Scene Fixture

`GCS/test/core/triangle_3p_1rs.txt` — 1 rigid set, 3 points in RS0, 0 constraints
