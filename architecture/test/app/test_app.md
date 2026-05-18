# App Interface Test Specification

## Module Under Test

`gcs::app::App` facade

## Interface Contract

- App builder API constructs `Manager` correctly.
- `loadFile` resets the previous model and delegates to `io::readGraph` or `io::readGraphJSON`.
- `compute` runs the demo pipeline: DCM decomposition, CDS solving, then LGS status reporting.
- `getTransformation` returns geometry parameters for a rigid set.
- `reset` clears all state.

## Test Cases

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| A01 | `test_app_add_rigidset` | `App::addRigidSet` | `App::instance().addRigidSet(0)` | `manager().rigidSets` | Has RS with id=0 |
| A02 | `test_app_add_geometry` | `App::addGeometry` | `addRigidSet(0).addGeometry(0, Point, 0)` | `manager().geometries` | Has geometry with id=0, type=Point |
| A03 | `test_app_add_geometry_params` | `App::addGeometry` | Add geometry with params `{1,2,3,0,0,0}` | `manager().geometries[0].v` | `v[0]=1`, `v[1]=2`, `v[2]=3` |
| A04 | `test_app_add_constraint` | `App::addConstraint` | `addConstraint(0, Distance, {0,1}, 5.0)` | `manager().constraints` | Has constraint with correct fields |
| A05 | `test_app_builder_chain` | Builder methods | Full builder chain | `manager()` | All three collections populated |
| A06 | `test_app_load_file` | `App::loadFile` | Load fixture path | `manager()` | Manager populated from file |
| A07 | `test_app_compute` | `App::compute` | Build problem, compute | `globalStatus()` | Status report is populated |
| A08 | `test_app_compute_decomposition` | `App::compute` | Build problem, compute | `decomposition()` | Decomposition result is populated |
| A09 | `test_app_get_transformation` | `App::getTransformation` | Build and compute | `getTransformation(rsId)` | Returns `array<double,6>` |
| A10 | `test_app_get_transformation_missing` | `App::getTransformation` | Query missing RS | `getTransformation(99)` | Returns zero-initialized array |
| A11 | `test_app_reset` | `App::reset` | Build problem, reset | `manager()` | Manager is empty |
| A12 | `test_app_reset_reuse` | `App::reset` | Build, reset, build again | `manager()` | New problem loaded correctly |

## Scene Fixtures

- `GCS/scene/test/app/full_pipeline.txt` - 3 RS, 5 Geom (3P+1L+1Pl), 2 Constr (1 Coincident + 1 Distance)
