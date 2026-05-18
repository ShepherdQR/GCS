# CDS Module

## Purpose

`cds` is the constraint-driven numerical leaf solver. It receives a `Manager`, optionally a decomposed sub-problem, and a solver configuration. It may mutate geometry in the active sub-problem and returns a compact `SolverReport`.

## Files

```text
GCS/cds/cds.h
GCS/cds/cds.cpp
```

## Interface

```cpp
namespace gcs::cds {
struct SolverConfig;
enum class SolverResult;
struct SolverReport;

class ConstraintDrivenSolver {
public:
    explicit ConstraintDrivenSolver(const SolverConfig& config = SolverConfig{});
    SolverReport solve(Manager& m);
    SolverReport solveSubProblem(Manager& m, const dcm::SubProblem& sp);
    void setConfig(const SolverConfig& config);
    const SolverConfig& config() const;
};
}
```

## Notes

- `cds` depends on `core` and `dcm`.
- `cds` should not own file IO, UI, or application lifecycle.
- `cds` should keep verbose numeric tracing behind `SolverConfig::verbose`.
- The current implementation is intentionally retained as a replaceable baseline; future specialized solvers can sit behind the same report-oriented interface.
- The module is intentionally flat: `cds.h` and `cds.cpp` live directly under `GCS/cds/`.
- Tests use text model fixtures in `GCS/scene/test/cds/`; reusable models live under `GCS/scene/`.
