# LGS Interface Test Specification

## Module Under Test

`gcs::lgs::LocalGeometricSolver::analyzeDOF`, `gcs::lgs::LocalGeometricSolver::analyzeStatus`, `gcs::lgs::LocalGeometricSolver::isWellConstrained`

## Interface Contract

- `analyzeDOF` returns correct geometry DOF, constraint removed DOF, and net DOF
- `analyzeStatus` classifies constraint status correctly (well/under/over)
- DOF values per geometry type are correct (Point=3, Line=6, Plane=6)
- DOF removed per constraint type are correct
- RigidSet-aware DOF counting works
- `isWellConstrained` shortcut matches `analyzeStatus` result

## Test Cases

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

## Scene Fixtures

- `GCS/test/lgs/well_constrained.txt` — 3 Points in 1 RS + 3 Distance constraints (net DOF=0)
- `GCS/test/lgs/under_constrained.txt` — 3 Points in 1 RS + 1 Distance constraint (net DOF>0)
- `GCS/test/lgs/over_constrained.txt` — 2 Points in 1 RS + Coincident + Distance (net DOF<0)
