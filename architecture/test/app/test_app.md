# App Interface Test Specification

## Module Under Test

`gcs::app::App` facade, `gcs::app::IProblem` hierarchy, `gcs::app::translateProblem`

## Interface Contract

- App builder API constructs Manager correctly
- IProblem pure virtual interface can be implemented by customers
- `translateProblem` converts IProblem → Manager correctly
- `loadFile` delegates to `io::readGraph`
- `compute` runs the full pipeline (DCM → LGS → CDS)
- `getTransformation` returns geometry parameters for a rigid set
- `reset` clears all state

## Test Cases

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| A01 | `test_app_add_rigidset` | `App::addRigidSet` | App::instance().addRigidSet(0) | manager().rigidSets | Has RS with id=0 |
| A02 | `test_app_add_geometry` | `App::addGeometry` | addRigidSet(0).addGeometry(0, Point, 0) | manager().geometries | Has Geometry with id=0, type=Point |
| A03 | `test_app_add_geometry_params` | `App::addGeometry` | addGeometry with params {1,2,3,0,0,0} | manager().geometries[0].v | v[0]=1, v[1]=2, v[2]=3 |
| A04 | `test_app_add_constraint` | `App::addConstraint` | addConstraint(0, Distance, {0,1}, 5.0) | manager().constraints | Has Constraint with correct fields |
| A05 | `test_app_builder_chain` | `App::addRigidSet+addGeometry+addConstraint` | Full builder chain | manager() | All 3 collections populated |
| A06 | `test_app_load_file` | `App::loadFile` | Write test file, loadFile(path) | manager() | Manager populated from file |
| A07 | `test_app_compute` | `App::compute` | Build problem, compute() | globalStatus() | StatusReport is populated |
| A08 | `test_app_compute_decomposition` | `App::compute` | Build problem, compute() | decomposition() | DecompositionResult is populated |
| A09 | `test_app_get_transformation` | `App::getTransformation` | Build + compute | getTransformation(rsId) | Returns array<double,6> |
| A10 | `test_app_get_transformation_missing` | `App::getTransformation` | Query non-existent RS | getTransformation(99) | Returns zero-initialized array |
| A11 | `test_app_reset` | `App::reset` | Build problem, reset() | manager() | Manager is empty |
| A12 | `test_app_reset_reuse` | `App::reset` | Build+reset+build again | manager() | New problem loaded correctly |
| A13 | `test_app_iproblem_interface` | `IProblem` | Implement concrete IProblem | Access virtual methods | All virtual methods callable |
| A14 | `test_app_translate_problem` | `translateProblem` | Create concrete IProblem, translate | Manager contents | Match IProblem data |
| A15 | `test_app_load_problem` | `App::loadProblem` | Create IProblem, loadProblem(prob) | manager() | Manager populated from IProblem |
| A16 | `test_app_igeometry_interface` | `IGeometry` | Implement concrete IGeometry | Access virtual methods | id(), type(), rigidSetId(), parameters() work |
| A17 | `test_app_iconstraint_interface` | `IConstraint` | Implement concrete IConstraint | Access virtual methods | id(), type(), geometryIds(), value() work |
| A18 | `test_app_irigidset_interface` | `IRigidSet` | Implement concrete IRigidSet | Access virtual methods | id(), geometryIds() work |

## Scene Fixtures

- `GCS/test/app/full_pipeline.txt` — 3 RS, 5 Geom (3P+1L+1Pl), 2 Constr (1 Coincident + 1 Distance)
