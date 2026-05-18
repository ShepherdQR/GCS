# CDS Interface Test Specification

## Module Under Test

`gcs::cds::ConstraintDrivenSolver::solve`, `gcs::cds::ConstraintDrivenSolver::solveSubProblem`, `gcs::cds::ConstraintDrivenSolver::setConfig`

## Interface Contract

- `solve` decomposes and iterates over sub-problems
- `solveSubProblem` returns a SolverReport with valid fields
- Under-constrained problems return `InconsistentConstraints` or `MaxIterationsReached`
- `setConfig` affects solver behavior
- `SolverReport` fields are populated correctly

## Test Cases

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

## Scene Fixtures

- `GCS/test/cds/simple_distance.txt` — 2 Points + 1 Distance constraint (under-constrained, 5 DOF)
