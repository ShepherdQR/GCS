# GCS System Plan: Test Architecture & App Interface Layer

## Overview

This plan establishes the GCS module test system as an integral part of the system architecture. The test plan lives inside `architecture/test/` alongside the existing module architecture docs. The focus is on **interface testing** — verifying that each module's public API contract is fulfilled correctly.

The plan has two major tracks:
1. **Test Architecture** — test folder structure, scene models, interface test specs per module
2. **App Interface Layer** — the customer-facing API that wraps the internal pipeline, plus its interface test

---

## Part 1: Test Architecture Folder

Create `architecture/test/` as a sibling to the existing module docs. Each module gets a test spec document that defines exactly what interface tests must pass.

```
architecture/
├── architecture.md
├── interface.md
├── core/core.md
├── io/io.md
├── dcm/dcm.md
├── lgs/lgs.md
├── cds/cds.md
└── test/                          ← NEW
    ├── test_architecture.md       ← Test system overview, conventions, fixtures
    ├── core/test_core.md          ← Core interface test spec
    ├── io/test_io.md              ← IO interface test spec
    ├── dcm/test_dcm.md            ← DCM interface test spec
    ├── lgs/test_lgs.md            ← LGS interface test spec
    ├── cds/test_cds.md            ← CDS interface test spec
    └── app/test_app.md            ← App interface test spec
```

### 1.1 Test Conventions

All interface tests follow these conventions:

- **Test naming**: `test_<module>_<what>_<condition>_<expected>`
- **Test structure**: Arrange → Act → Assert
- **Assertion macro**: `GCS_ASSERT(condition, message)` — custom macro, no framework dependency
- **Test runner**: Each module has a `test_<module>.cpp` with a `main()` that runs all tests and reports pass/fail
- **Scene fixtures**: `.txt` graph files stored in `GCS/test/<module>/` directory
- **Test result**: Console output with `[PASS]` / `[FAIL]` per test, summary at end

### 1.2 Scene Fixture Directory

```
GCS/test/
├── core/
│   └── triangle_3p_1rs.txt
├── io/
│   ├── basic_5g_2c.txt
│   └── malformed.txt
├── dcm/
│   ├── single_component.txt
│   └── two_components.txt
├── lgs/
│   ├── well_constrained.txt
│   ├── under_constrained.txt
│   └── over_constrained.txt
├── cds/
│   └── simple_distance.txt
└── app/
    └── full_pipeline.txt
```

---

## Part 2: Interface Test Specifications Per Module

### 2.1 Core Interface Tests

**Module under test**: `gcs::GeometryType`, `gcs::ConstraintType`, `gcs::RigidSet`, `gcs::Geometry`, `gcs::Constraint`, `gcs::Manager`

**Interface contract to verify**:
- Enum values map correctly to integer codes (file format compatibility)
- Structs can be created, populated, and queried
- Manager lookup functions work correctly
- Helper functions return correct values

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

**Scene fixture**: `triangle_3p_1rs.txt`
```
1
0
3
0 0 0
1 0 0
2 0 0
0

0 0 0 0 0 0
1 1 0 0 0 0
2 0 1 0 0 0

```
(1 rigid set, 3 points in RS0, 0 constraints, zero-initialized parameters)

---

### 2.2 IO Interface Tests

**Module under test**: `gcs::io::readGraph`, `gcs::io::dumpGraph`, `gcs::io::printSummary`

**Interface contract to verify**:
- `readGraph` correctly parses all sections of the file format
- `readGraph` handles missing/invalid files gracefully
- `dumpGraph` produces output that can be re-read (round-trip)
- `printSummary` produces console output without crashing

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| IO01 | `test_io_read_valid_file` | `readGraph` | Write valid test file to disk | readGraph(m, path) | Manager has correct RS/Geom/Constr counts and values |
| IO02 | `test_io_read_missing_file` | `readGraph` | Use non-existent path | readGraph(m, "nonexistent.txt") | Manager remains empty, no crash |
| IO03 | `test_io_read_rigidsets` | `readGraph` | File with 3 rigid sets | readGraph(m, path) | m.rigidSets.size()==3, ids match |
| IO04 | `test_io_read_geometry_types` | `readGraph` | File with Point, Line, Plane | readGraph(m, path) | Each geometry has correct GeometryType |
| IO05 | `test_io_read_geometry_params` | `readGraph` | File with non-zero params | readGraph(m, path) | g.v[0..5] match file values |
| IO06 | `test_io_read_constraint_types` | `readGraph` | File with all 5 constraint types | readGraph(m, path) | Each constraint has correct ConstraintType |
| IO07 | `test_io_read_constraint_values` | `readGraph` | File with constraint values | readGraph(m, path) | c.value matches file values |
| IO08 | `test_io_read_constraint_geometry_ids` | `readGraph` | File with multi-geometry constraints | readGraph(m, path) | c.geometryIds match file |
| IO09 | `test_io_dump_round_trip` | `readGraph` + `dumpGraph` | Read file → dump → read dump | Compare 2 Managers | Same topology, params, values |
| IO10 | `test_io_dump_empty_path` | `dumpGraph` | Pass empty string | dumpGraph(m, "") | Returns immediately, no file created |
| IO11 | `test_io_print_summary` | `printSummary` | Populate Manager | printSummary(m) | No crash (output to stdout) |

**Scene fixture**: `basic_5g_2c.txt` (same format as g1.txt — 3 RS, 5 Geom, 2 Constr)
**Scene fixture**: `malformed.txt` (truncated file for error handling test)

---

### 2.3 DCM Interface Tests

**Module under test**: `gcs::dcm::DecompositionManager::decompose`, `gcs::dcm::DecompositionManager::extractSubProblem`

**Interface contract to verify**:
- `decompose` returns correct number of connected components
- Each SubProblem contains the correct geometry/constraint/rigid set IDs
- Single-component graphs produce one SubProblem
- Multi-component graphs produce multiple SubProblems
- `extractSubProblem` correctly identifies constraints within a geometry subset

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| D01 | `test_dcm_decompose_empty` | `decompose` | Empty Manager | decompose(m) | subProblems.size()==0 |
| D02 | `test_dcm_decompose_single_geometry` | `decompose` | 1 geometry, 0 constraints | decompose(m) | 1 sub-problem with 1 geometry |
| D03 | `test_dcm_decompose_two_disconnected` | `decompose` | 2 geometries, 0 constraints, different RS | decompose(m) | 2 sub-problems |
| D04 | `test_dcm_decompose_two_connected` | `decompose` | 2 geometries, 1 constraint | decompose(m) | 1 sub-problem with 2 geometries |
| D05 | `test_dcm_decompose_chain` | `decompose` | 5 geometries in chain (4 constraints) | decompose(m) | 1 sub-problem with 5 geometries |
| D06 | `test_dcm_decompose_two_components` | `decompose` | 2 pairs connected, pairs disconnected | decompose(m) | 2 sub-problems |
| D07 | `test_dcm_decompose_rigidset_grouping` | `decompose` | 2 geometries in same RS, no constraint | decompose(m) | Same RS → same sub-problem |
| D08 | `test_dcm_decompose_result_counts` | `decompose` | Known graph | decompose(m) | totalGeometries, totalConstraints match Manager |
| D09 | `test_dcm_decompose_is_single_component` | `decompose` | Connected vs disconnected graphs | decompose(m) | isSingleComponent flag correct |
| D10 | `test_dcm_decompose_subproblem_ids` | `decompose` | Multi-component graph | decompose(m) | Sub-problem IDs are sequential (0,1,2,...) |
| D11 | `test_dcm_decompose_subproblem_constraints` | `decompose` | Graph with constraints | decompose(m) | Each constraint assigned to correct sub-problem |
| D12 | `test_dcm_extract_subproblem` | `extractSubProblem` | Manager + geometry subset | extractSubProblem(m, ids) | SubProblem contains correct constraint IDs |

**Scene fixture**: `single_component.txt` — 3 points, 3 distance constraints, 1 RS (fully connected triangle)
**Scene fixture**: `two_components.txt` — 2 independent pairs: (P0,P1 + Distance) and (P2,P3 + Distance), 2 RS

---

### 2.4 LGS Interface Tests

**Module under test**: `gcs::lgs::LocalGeometricSolver::analyzeDOF`, `gcs::lgs::LocalGeometricSolver::analyzeStatus`, `gcs::lgs::LocalGeometricSolver::isWellConstrained`

**Interface contract to verify**:
- `analyzeDOF` returns correct geometry DOF, constraint removed DOF, and net DOF
- `analyzeStatus` classifies constraint status correctly (well/under/over)
- DOF values per geometry type are correct (Point=3, Line=6, Plane=6)
- DOF removed per constraint type are correct
- RigidSet-aware DOF counting works
- `isWellConstrained` shortcut matches `analyzeStatus` result

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| L01 | `test_lgs_dof_single_point` | `analyzeDOF` | 1 Point, 0 constraints | analyzeDOF(m) | geometryDOF=3, constraintRemovedDOF=0, netDOF=3 |
| L02 | `test_lgs_dof_single_line` | `analyzeDOF` | 1 Line, 0 constraints | analyzeDOF(m) | geometryDOF=6, netDOF=6 |
| L03 | `test_lgs_dof_single_plane` | `analyzeDOF` | 1 Plane, 0 constraints | analyzeDOF(m) | geometryDOF=6, netDOF=6 |
| L04 | `test_lgs_dof_two_points_distance` | `analyzeDOF` | 2 Points + Distance | analyzeDOF(m) | geometryDOF=6, constraintRemovedDOF=1, netDOF=5 |
| L05 | `test_lgs_dof_two_points_coincident` | `analyzeDOF` | 2 Points + Coincident | analyzeDOF(m) | geometryDOF=6, constraintRemovedDOF=3, netDOF=3 |
| L06 | `test_lgs_status_well_constrained` | `analyzeStatus` | 3 Points + 3 Distances in 1 RS | analyzeStatus(m) | overallStatus==WellConstrained |
| L07 | `test_lgs_status_under_constrained` | `analyzeStatus` | 2 Points, 0 constraints | analyzeStatus(m) | overallStatus==UnderConstrained |
| L08 | `test_lgs_status_over_constrained` | `analyzeStatus` | 2 Points + Coincident + Distance | analyzeStatus(m) | overallStatus==OverConstrained or OverConstrainedConsistent |
| L09 | `test_lgs_dof_with_subproblem` | `analyzeDOF(m, sp)` | Manager + SubProblem | analyzeDOF(m, sp) | DOF counts for sub-problem only |
| L10 | `test_lgs_status_with_subproblem` | `analyzeStatus(m, sp)` | Manager + SubProblem | analyzeStatus(m, sp) | Status for sub-problem only |
| L11 | `test_lgs_is_well_constrained` | `isWellConstrained` | Well-constrained Manager | isWellConstrained(m) | Returns true |
| L12 | `test_lgs_is_not_well_constrained` | `isWellConstrained` | Under-constrained Manager | isWellConstrained(m) | Returns false |
| L13 | `test_lgs_status_report_summary` | `analyzeStatus` | Any Manager | analyzeStatus(m) | summaryText is non-empty |
| L14 | `test_lgs_status_report_consistency` | `analyzeStatus` | Over-constrained consistent | analyzeStatus(m) | isConsistent==true |
| L15 | `test_lgs_dof_rigidset_aware` | `analyzeDOF` | 2 Points in same RS + 1 Distance | analyzeDOF(m) | geometryDOF=6 (RS DOF), netDOF=5 |

**Scene fixture**: `well_constrained.txt` — 3 Points in 1 RS + 3 Distance constraints (net DOF=0)
**Scene fixture**: `under_constrained.txt` — 3 Points in 1 RS + 1 Distance constraint (net DOF>0)
**Scene fixture**: `over_constrained.txt` — 2 Points in 1 RS + Coincident + Distance (net DOF<0)

---

### 2.5 CDS Interface Tests

**Module under test**: `gcs::cds::ConstraintDrivenSolver::solve`, `gcs::cds::ConstraintDrivenSolver::solveSubProblem`, `gcs::cds::ConstraintDrivenSolver::setConfig`

**Interface contract to verify**:
- `solve` decomposes and iterates over sub-problems
- `solveSubProblem` returns a SolverReport with valid fields
- Under-constrained problems return `InconsistentConstraints` or `MaxIterationsReached`
- `setConfig` affects solver behavior
- `SolverReport` fields are populated correctly

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| CD01 | `test_cds_solve_returns_report` | `solve` | Populated Manager | solve(m) | SolverReport has valid result enum |
| CD02 | `test_cds_solve_subproblem_returns_report` | `solveSubProblem` | Manager + SubProblem | solveSubProblem(m, sp) | SolverReport has valid result enum |
| CD03 | `test_cds_solve_under_constrained` | `solveSubProblem` | Under-constrained sub-problem | solveSubProblem(m, sp) | result==InconsistentConstraints or MaxIterationsReached |
| CD04 | `test_cds_report_iterations` | `solveSubProblem` | Any Manager | solveSubProblem(m, sp) | iterationsUsed >= 0 |
| CD05 | `test_cds_report_residuals` | `solveSubProblem` | Any Manager | solveSubProblem(m, sp) | initialResidual >= 0, finalResidual >= 0 |
| CD06 | `test_cds_config_default` | `SolverConfig` | Default construct | Check fields | maxIterations=100, tolerance=1e-8, dampingFactor=1.0 |
| CD07 | `test_cds_config_custom` | `setConfig` | Set custom config | config() | Returns the custom config |
| CD08 | `test_cds_config_affects_solve` | `setConfig` | Set maxIterations=1 | solve(m) | iterationsUsed <= 1 |
| CD09 | `test_cds_result_to_string` | `toString` | Each SolverResult enum | toString(result) | Non-empty string for each |
| CD10 | `test_cds_solve_empty_manager` | `solve` | Empty Manager | solve(m) | Returns report (no crash) |

**Scene fixture**: `simple_distance.txt` — 2 Points + 1 Distance constraint (under-constrained, 5 DOF)

---

### 2.6 App Interface Tests

**Module under test**: `gcs::app::App` facade, `gcs::app::IProblem` hierarchy, `gcs::app::translateProblem`

**Interface contract to verify**:
- App builder API constructs Manager correctly
- IProblem pure virtual interface can be implemented by customers
- `translateProblem` converts IProblem → Manager correctly
- `loadFile` delegates to `io::readGraph`
- `compute` runs the full pipeline (DCM → LGS → CDS)
- `getTransformation` returns geometry parameters for a rigid set
- `reset` clears all state

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

**Scene fixture**: `full_pipeline.txt` — 3 RS, 5 Geom (3P+1L+1Pl), 2 Constr (1 Coincident + 1 Distance)

---

## Part 3: App Interface Layer Design

### 3.1 Interface Object Hierarchy (Customer Level)

Pure virtual base classes that define the contract for how customers formalize a GCS problem:

```cpp
namespace gcs::app {

struct IGeometry {
    virtual ~IGeometry() = default;
    virtual int id() const = 0;
    virtual GeometryType type() const = 0;
    virtual int rigidSetId() const = 0;
    virtual std::array<double, 6> parameters() const = 0;
};

struct IConstraint {
    virtual ~IConstraint() = default;
    virtual int id() const = 0;
    virtual ConstraintType type() const = 0;
    virtual const std::vector<int>& geometryIds() const = 0;
    virtual double value() const = 0;
};

struct IRigidSet {
    virtual ~IRigidSet() = default;
    virtual int id() const = 0;
    virtual const std::vector<int>& geometryIds() const = 0;
};

struct IProblem {
    virtual ~IProblem() = default;
    virtual const std::vector<std::unique_ptr<IRigidSet>>& rigidSets() const = 0;
    virtual const std::vector<std::unique_ptr<IGeometry>>& geometries() const = 0;
    virtual const std::vector<std::unique_ptr<IConstraint>>& constraints() const = 0;
};

} // namespace gcs::app
```

**Design rationale**:
- Pure virtual = customers must implement all methods, ensuring complete problem definition
- `IProblem` aggregates `IGeometry`, `IConstraint`, `IRigidSet` — mirrors the internal Manager structure
- `std::unique_ptr` in `IProblem` vectors enables polymorphic ownership
- The interface is decoupled from internal `Manager` — customers never see `double v[6]` or flat structs

### 3.2 Bridge Function (Customer → Internal)

```cpp
namespace gcs::app {

void translateProblem(const IProblem& problem, Manager& m);

} // namespace gcs::app
```

This function:
1. Clears the Manager
2. Iterates `problem.rigidSets()` → creates `RigidSet` structs in Manager
3. Iterates `problem.geometries()` → creates `Geometry` structs, fills `v[6]` from `parameters()`
4. Iterates `problem.constraints()` → creates `Constraint` structs
5. Populates `RigidSet::geometryIds` based on geometry-to-RS assignments

### 3.3 App Facade API

```cpp
namespace gcs::app {

class App {
public:
    static App& instance();

    App& addRigidSet(int id);
    App& addGeometry(int id, GeometryType type, int rigidSetId,
                     const std::array<double, 6>& params = {0,0,0,0,0,0});
    App& addConstraint(int id, ConstraintType type,
                       const std::vector<int>& geomIds, double value = 0.0);

    App& loadProblem(const IProblem& problem);
    App& loadFile(const std::string& path);

    App& compute();

    const std::array<double, 6>& getTransformation(int rigidSetId) const;
    const Manager& manager() const;
    const dcm::DecompositionResult& decomposition() const;
    const lgs::StatusReport& globalStatus() const;
    const std::vector<cds::SolverReport>& solverReports() const;

    App& reset();

private:
    App() = default;
    Manager manager_;
    dcm::DecompositionResult decomp_;
    lgs::StatusReport globalStatus_;
    std::vector<cds::SolverReport> solverReports_;
    std::unordered_map<int, std::array<double, 6>> transformations_;
    bool computed_ = false;
};

} // namespace gcs::app
```

**Design rationale**:
- Singleton: one App instance per process (matches current main.cpp usage pattern)
- Builder pattern: fluent API (`addRigidSet().addGeometry().addConstraint()`)
- Three input modes: builder API, IProblem object, or file path
- `compute()` runs full pipeline: DCM → LGS → CDS
- `getTransformation(rsId)` returns the 6-DOF transformation (position + orientation) of a rigid set
- `reset()` allows reusing the App instance

### 3.4 File Layout

```
GCS/app/
├── include/gcs/app/
│   └── App.h              ← IGeometry, IConstraint, IRigidSet, IProblem, App, translateProblem
└── src/
    └── App.cpp            ← Implementation of App + translateProblem
```

---

## Part 4: Test Implementation

### 4.1 Test Infrastructure

A lightweight test framework in a single header:

```cpp
// GCS/test/test_framework.h
#pragma once
#include <iostream>
#include <string>

static int g_tests_run = 0;
static int g_tests_passed = 0;

#define GCS_ASSERT(cond, msg) do { \
    g_tests_run++; \
    if (cond) { \
        g_tests_passed++; \
        std::cout << "[PASS] " << msg << "\n"; \
    } else { \
        std::cerr << "[FAIL] " << msg << " at " << __FILE__ << ":" << __LINE__ << "\n"; \
    } \
} while(0)

#define GCS_ASSERT_EQ(a, b, msg) GCS_ASSERT((a) == (b), msg)
#define GCS_ASSERT_NE(a, b, msg) GCS_ASSERT((a) != (b), msg)
#define GCS_ASSERT_GT(a, b, msg) GCS_ASSERT((a) > (b), msg)
#define GCS_ASSERT_LT(a, b, msg) GCS_ASSERT((a) < (b), msg)

#define GCS_TEST_SUMMARY() do { \
    std::cout << "\n=== " << g_tests_passed << "/" << g_tests_run << " tests passed ===\n"; \
    return (g_tests_passed == g_tests_run) ? 0 : 1; \
} while(0)
```

### 4.2 Test Files

```
GCS/test/
├── test_framework.h
├── core/
│   ├── triangle_3p_1rs.txt
│   └── test_core.cpp
├── io/
│   ├── basic_5g_2c.txt
│   ├── malformed.txt
│   └── test_io.cpp
├── dcm/
│   ├── single_component.txt
│   ├── two_components.txt
│   └── test_dcm.cpp
├── lgs/
│   ├── well_constrained.txt
│   ├── under_constrained.txt
│   ├── over_constrained.txt
│   └── test_lgs.cpp
├── cds/
│   ├── simple_distance.txt
│   └── test_cds.cpp
└── app/
    ├── full_pipeline.txt
    └── test_app.cpp
```

Each `test_<module>.cpp` is a standalone console application with its own `main()`.

---

## Part 5: Architecture Test Documents

Each module gets a test spec markdown file under `architecture/test/`:

| Document | Content |
|----------|---------|
| `test_architecture.md` | Test system overview, conventions, fixture format, how to run tests |
| `core/test_core.md` | Core interface test spec (C01-C17) |
| `io/test_io.md` | IO interface test spec (IO01-IO11) |
| `dcm/test_dcm.md` | DCM interface test spec (D01-D12) |
| `lgs/test_lgs.md` | LGS interface test spec (L01-L15) |
| `cds/test_cds.md` | CDS interface test spec (CD01-CD10) |
| `app/test_app.md` | App interface test spec (A01-A18) |

---

## Execution Order

1. Create `architecture/test/` folder structure with test spec markdown files
2. Create scene fixture `.txt` files in `GCS/test/<module>/`
3. Create `test_framework.h`
4. Create `App.h` (interface objects + facade)
5. Create `App.cpp` (implementation)
6. Create `test_core.cpp`, `test_io.cpp`, `test_dcm.cpp`, `test_lgs.cpp`, `test_cds.cpp`, `test_app.cpp`
7. Update `GCS.vcxproj` with new include paths and source files
8. Build and verify compilation
9. Run tests and verify all pass

---

## File Creation Summary

| # | File | Purpose |
|---|------|---------|
| 1 | `architecture/test/test_architecture.md` | Test system overview |
| 2 | `architecture/test/core/test_core.md` | Core interface test spec |
| 3 | `architecture/test/io/test_io.md` | IO interface test spec |
| 4 | `architecture/test/dcm/test_dcm.md` | DCM interface test spec |
| 5 | `architecture/test/lgs/test_lgs.md` | LGS interface test spec |
| 6 | `architecture/test/cds/test_cds.md` | CDS interface test spec |
| 7 | `architecture/test/app/test_app.md` | App interface test spec |
| 8 | `GCS/test/test_framework.h` | Lightweight test macros |
| 9 | `GCS/test/core/triangle_3p_1rs.txt` | Core scene fixture |
| 10 | `GCS/test/io/basic_5g_2c.txt` | IO scene fixture |
| 11 | `GCS/test/io/malformed.txt` | IO error handling fixture |
| 12 | `GCS/test/dcm/single_component.txt` | DCM single component fixture |
| 13 | `GCS/test/dcm/two_components.txt` | DCM two component fixture |
| 14 | `GCS/test/lgs/well_constrained.txt` | LGS well-constrained fixture |
| 15 | `GCS/test/lgs/under_constrained.txt` | LGS under-constrained fixture |
| 16 | `GCS/test/lgs/over_constrained.txt` | LGS over-constrained fixture |
| 17 | `GCS/test/cds/simple_distance.txt` | CDS solver fixture |
| 18 | `GCS/test/app/full_pipeline.txt` | App full pipeline fixture |
| 19 | `GCS/app/include/gcs/app/App.h` | Interface objects + App facade |
| 20 | `GCS/app/src/App.cpp` | App implementation |
| 21 | `GCS/test/core/test_core.cpp` | Core interface test |
| 22 | `GCS/test/io/test_io.cpp` | IO interface test |
| 23 | `GCS/test/dcm/test_dcm.cpp` | DCM interface test |
| 24 | `GCS/test/lgs/test_lgs.cpp` | LGS interface test |
| 25 | `GCS/test/cds/test_cds.cpp` | CDS interface test |
| 26 | `GCS/test/app/test_app.cpp` | App interface test |
| 27 | `GCS/GCS.vcxproj` | Updated build config |
