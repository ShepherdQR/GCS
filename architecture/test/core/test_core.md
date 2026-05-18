# Core Interface Test Specification

## Module Under Test

`gcs::GeometryType`, `gcs::ConstraintType`, `gcs::SolveMode`, `gcs::RigidSet`, `gcs::Geometry`, `gcs::Constraint`, `gcs::BehaviorModel`, `gcs::Manager`

## Interface Contract

- Enum values map correctly to integer codes for file compatibility.
- Structs can be created, populated, and queried.
- `Manager` lookup functions work correctly.
- `Manager` has a default behavior model in update mode.
- Helper functions return correct names and DOF values.

## Test Cases

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| C01 | `test_core_enum_geometry_values` | `GeometryType` | Create each enum value | Cast to int | Point=0, Line=1, Plane=2 |
| C02 | `test_core_enum_constraint_values` | `ConstraintType` | Create each enum value | Cast to int | Coincident=0, Parallel=1, Perpendicular=2, Distance=3, Angle=4 |
| C02b | `test_core_enum_solve_mode_values` | `SolveMode` | Create each enum value | Cast to int | Update=0, Drag=1, Simulation=2 |
| C03 | `test_core_geometry_create_point` | `Geometry` | Create point geometry | Access fields | id, type, rigidSetId match |
| C04 | `test_core_geometry_create_line` | `Geometry` | Create line geometry | Access fields | id, type, rigidSetId match |
| C05 | `test_core_geometry_create_plane` | `Geometry` | Create plane geometry | Access fields | id, type, rigidSetId match |
| C06 | `test_core_constraint_create` | `Constraint` | Create distance constraint | Access fields | id, type, geometryIds, value match |
| C07 | `test_core_rigidset_create` | `RigidSet` | Create rigid set | Access fields | id and geometryIds match |
| C08 | `test_core_manager_empty` | `Manager` | Default construct | Check fields | Empty collections and behavior mode Update |
| C09 | `test_core_manager_populate` | `Manager` | Add 2 RS, 3 Geom, 1 Constr | Check sizes | Sizes match counts |
| C10 | `test_core_manager_find_geometry` | `Manager::findGeometry` | Add geometries | `findGeometry(1)` | Returns geometry id=1 |
| C11 | `test_core_manager_find_geometry_missing` | `Manager::findGeometry` | Add geometries | `findGeometry(99)` | Returns `nullptr` |
| C12 | `test_core_manager_find_constraint` | `Manager::findConstraint` | Add constraints | `findConstraint(0)` | Returns constraint id=0 |
| C13 | `test_core_manager_find_rigidset` | `Manager::findRigidSet` | Add rigid sets | `findRigidSet(1)` | Returns RS id=1 |
| C14 | `test_core_helper_typename_geometry` | `typeNameGeometry` | Call with each geometry type | Get string | Point, Line, Plane |
| C15 | `test_core_helper_typename_constraint` | `typeNameConstraint` | Call with each constraint type | Get string | Coincident, Parallel, Perpendicular, Distance, Angle |
| C15b | `test_core_helper_typename_solve_mode` | `typeNameSolveMode` | Call with each solve mode | Get string | Update, Drag, Simulation |
| C16 | `test_core_helper_dof_geometry` | `dofGeometry` | Call with each geometry type | Get int | Point=3, Line=6, Plane=6 |
| C17 | `test_core_helper_dof_removed_constraint` | `dofRemovedConstraint` | Call with each constraint type | Get int | Coincident=3, Parallel=2, Perpendicular=1, Distance=1, Angle=1 |

## Scene Fixture

- `GCS/scene/test/core/triangle_3p_1rs.txt` - 1 rigid set, 3 points in RS0, 0 constraints
