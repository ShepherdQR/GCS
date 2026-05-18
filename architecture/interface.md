# GCS System Interface

## Include Layout

The C++ modules use a flat per-module layout. Include paths are resolved from the `GCS/` project directory:

```cpp
#include "core/core.h"
#include "io/io.h"
#include "dcm/dcm.h"
#include "lgs/lgs.h"
#include "cds/cds.h"
#include "app/App.h"
```

## Core

```cpp
namespace gcs {
enum class GeometryType;
enum class ConstraintType;
enum class SolveMode;

struct RigidSet;
struct Geometry;
struct Constraint;
struct BehaviorModel;
struct HistoryAction;
struct Manager;

std::string typeNameGeometry(GeometryType t);
std::string typeNameConstraint(ConstraintType t);
std::string typeNameSolveMode(SolveMode t);
int dofGeometry(GeometryType t);
int dofRemovedConstraint(ConstraintType t);
}
```

## IO

```cpp
namespace gcs::io {
void readGraph(Manager& m, const std::string& path);
void readGraphJSON(Manager& m, const std::string& path);
void dumpGraph(const Manager& m, const std::string& inputPath);
void dumpGraphJSON(const Manager& m, const std::string& inputPath);
void printSummary(const Manager& m);
}
```

## DCM

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

## LGS

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

## CDS

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

`SolverConfig` includes the numeric limits and the current `SolveMode`. The behavior model in `Manager` remains the durable model-level intent; config is per solver run.

## App

```cpp
namespace gcs::app {
class App {
public:
    static App& instance();
    App& loadFile(const std::string& path);
    App& compute();
    App& reset();
    const Manager& manager() const;
};
}
```
