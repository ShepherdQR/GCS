# DCM Interface Test Specification

## Module Under Test

`gcs::dcm::DecompositionManager::decompose`, `gcs::dcm::DecompositionManager::extractSubProblem`

## Interface Contract

- `decompose` returns correct number of connected components
- Each SubProblem contains the correct geometry/constraint/rigid set IDs
- Single-component graphs produce one SubProblem
- Multi-component graphs produce multiple SubProblems
- `extractSubProblem` correctly identifies constraints within a geometry subset

## Test Cases

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

## Scene Fixtures

- `GCS/test/dcm/single_component.txt` — 3 points, 3 distance constraints, 1 RS (fully connected triangle)
- `GCS/test/dcm/two_components.txt` — 2 independent pairs: (P0,P1 + Distance) and (P2,P3 + Distance), 2 RS
