# CDS Interface Test Specification

## Module Under Test

`gcs::cds::ConstraintDrivenSolver::solve`, `gcs::cds::ConstraintDrivenSolver::solveSubProblem`, `gcs::cds::ConstraintDrivenSolver::setConfig`

## Interface Contract

- `solve` decomposes and iterates over sub-problems.
- `solveSubProblem` returns a `SolverReport` with valid fields.
- LGS owns structural under/over-constrained diagnostics; CDS returns a numeric result report.
- `setConfig` affects solver behavior.
- `SolverConfig` carries numeric limits and solve mode.
- `SolverReport` fields are populated correctly.

## Test Cases

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| CD01 | `test_cds_solve_returns_report` | `solve` | Populated Manager | `solve(m)` | SolverReport has valid result enum |
| CD02 | `test_cds_solve_subproblem_returns_report` | `solveSubProblem` | Manager + SubProblem | `solveSubProblem(m, sp)` | SolverReport has valid result enum |
| CD03 | `test_cds_solve_under_constrained` | `solveSubProblem` | Under-constrained sub-problem | `solveSubProblem(m, sp)` | Returns a valid non-crashing result |
| CD04 | `test_cds_report_iterations` | `solveSubProblem` | Any Manager | `solveSubProblem(m, sp)` | `iterationsUsed >= 0` |
| CD05 | `test_cds_report_residuals` | `solveSubProblem` | Any Manager | `solveSubProblem(m, sp)` | residual fields are non-negative |
| CD06 | `test_cds_config_default` | `SolverConfig` | Default construct | Check fields | maxIterations=100, tolerance=1e-8, dampingFactor=1.0, mode=Update |
| CD07 | `test_cds_config_custom` | `setConfig` | Set custom config | `config()` | Returns custom maxIterations, tolerance, and mode |
| CD08 | `test_cds_config_affects_solve` | `setConfig` | Set maxIterations=1 | `solve(m)` | `iterationsUsed <= 1` |
| CD09 | `test_cds_result_to_string` | `toString` | Each SolverResult enum | `toString(result)` | Non-empty string for each |
| CD10 | `test_cds_solve_empty_manager` | `solve` | Empty Manager | `solve(m)` | Returns report without crashing |

## Scene Fixtures

- `GCS/scene/test/cds/simple_distance.txt` - 2 Points + 1 Distance constraint (under-constrained, 5 DOF)
