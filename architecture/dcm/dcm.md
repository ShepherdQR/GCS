# DCM Module

## Purpose

`dcm` decomposes the structural constraint graph into sub-problems. Today it performs connected-component decomposition over geometry, constraints, and rigid-set grouping. Long-term it is the planning layer where rigidity, dependency, and specialized-problem classification can be added before numerical solving.

## Files

```text
GCS/dcm/dcm.h
GCS/dcm/dcm.cpp
```

## Interface

```cpp
namespace gcs::dcm {
struct SubProblem;
struct DecompositionResult;

class DecompositionManager {
public:
    DecompositionResult decompose(const Manager& m);
    SubProblem extractSubProblem(const Manager& m,
                                 const std::vector<int>& geometryIds) const;
};
}
```

## Notes

- `dcm` depends on `core`.
- Decomposition is based on graph connected components.
- `dcm` should not mutate geometry or run numeric iterations.
- Connected components are only the first planning pass; keep the interface report-oriented so richer classification can be added later.
- Reusable sample models live under `GCS/scene/`, including `GCS/scene/basic/g1.txt`.
