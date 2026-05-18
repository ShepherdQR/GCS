# CDS Module

## Purpose

`cds` is the constraint-driven numerical solver.

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

- `cds` depends on `core`, `dcm`, and `lgs`.
- The module is intentionally flat: `cds.h` and `cds.cpp` live directly under `GCS/cds/`.
- Tests use text model fixtures in `GCS/scene/test/cds/`; reusable models live under `GCS/scene/`.
