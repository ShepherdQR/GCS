# DCM Module

## Purpose

`dcm` decomposes a constraint graph into connected sub-problems.

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
- Reusable sample models live under `GCS/scene/`, including `GCS/scene/basic/g1.txt`.
