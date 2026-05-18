# LGS Module

## Purpose

`lgs` analyzes local geometric constraint status: degrees of freedom, under-constrained cases, over-constrained cases, and residual violations.

## Files

```text
GCS/lgs/lgs.h
GCS/lgs/lgs.cpp
```

## Interface

```cpp
namespace gcs::lgs {
enum class ConstraintStatus;
struct DOFAnalysis;
struct ConstraintViolation;
struct StatusReport;

class LocalGeometricSolver {
public:
    DOFAnalysis analyzeDOF(const Manager& m) const;
    DOFAnalysis analyzeDOF(const Manager& m, const dcm::SubProblem& sp) const;
    StatusReport analyzeStatus(const Manager& m) const;
    StatusReport analyzeStatus(const Manager& m, const dcm::SubProblem& sp) const;
    std::vector<ConstraintViolation> checkSatisfaction(
        const Manager& m,
        double tolerance = 1e-6) const;
    bool isWellConstrained(const Manager& m) const;
};
}
```

## Notes

- `lgs` depends on `core` and `dcm`.
- It does not perform file IO.
- It returns reports instead of launching UI behavior.
