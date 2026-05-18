# GCS System Interface Design

## 1. Overview

This document defines the complete public interface of the GCS (Geometric Constraint Solver) system. It specifies:

- **System-level API**: The top-level facade that orchestrates the full pipeline
- **Module-level API**: Each module's public interface with exact C++ signatures
- **Cross-module data contracts**: How data flows between modules
- **Error handling strategy**: How errors propagate across module boundaries
- **Namespace organization**: C++ namespace structure

---

## 2. Namespace Organization

```
namespace gcs {
    // Core types
    enum class GeometryType { ... };
    enum class ConstraintType { ... };
    struct RigidSet { ... };
    struct Geometry { ... };
    struct Constraint { ... };
    struct Manager { ... };

    // IO
    namespace io {
        void readGraph(Manager& m, const std::string& path);
        void dumpGraph(const Manager& m, const std::string& inputPath);
        void displayGraph(const std::string& graphFile);
        void printSummary(const Manager& m);
    }

    // DCM
    namespace dcm {
        class DecompositionManager { ... };
        struct SubProblem { ... };
        struct DecompositionResult { ... };
    }

    // LGS
    namespace lgs {
        class LocalGeometricSolver { ... };
        struct DOFAnalysis { ... };
        struct StatusReport { ... };
        struct ConstraintViolation { ... };
        enum class ConstraintStatus { ... };
    }

    // CDS
    namespace cds {
        class ConstraintDrivenSolver { ... };
        struct SolverConfig { ... };
        struct SolverReport { ... };
        enum class SolverResult { ... };
        class IConstraintEquation { ... };
    }

    // System facade
    class GCSSystem { ... };
    struct SystemResult { ... };
}
```

---

## 3. System-Level API (Facade)

The `GCSSystem` class provides a high-level interface that orchestrates the full pipeline. Application code should use this facade rather than calling individual modules directly.

### 3.1 GCSSystem Class

```cpp
namespace gcs {

enum class SystemAction {
    AnalyzeOnly,
    Solve,
    SolveAndDisplay
};

struct SystemResult {
    bool success;
    std::string inputPath;
    dcm::DecompositionResult decomposition;
    std::vector<lgs::StatusReport> statusReports;
    std::vector<cds::SolverReport> solverReports;
    lgs::StatusReport globalStatus;
    std::string errorMessage;
};

class GCSSystem {
public:
    GCSSystem();

    SystemResult solve(const std::string& inputPath,
                       SystemAction action = SystemAction::SolveAndDisplay);

    SystemResult analyze(const std::string& inputPath);

    void setSolverConfig(const cds::SolverConfig& config);
    void setVerbose(bool verbose);

    const Manager& manager() const;

private:
    Manager manager_;
    cds::SolverConfig solverConfig_;
    bool verbose_;
};

}
```

### 3.2 Usage Examples

**Full solve with display:**
```cpp
gcs::GCSSystem system;
auto result = system.solve("g1.txt", gcs::SystemAction::SolveAndDisplay);
if (result.success) {
    std::cout << "Solved in " << result.solverReports.size() << " sub-problems\n";
}
```

**Analyze only (no solving):**
```cpp
gcs::GCSSystem system;
auto result = system.analyze("g1.txt");
for (const auto& report : result.statusReports) {
    std::cout << "Sub-problem: " << gcs::lgs::toString(report.overallStatus)
              << " (net DOF=" << report.dofAnalysis.netDOF << ")\n";
}
```

**Custom solver config:**
```cpp
gcs::GCSSystem system;
gcs::cds::SolverConfig config;
config.maxIterations = 500;
config.tolerance = 1e-12;
system.setSolverConfig(config);
auto result = system.solve("g1.txt");
```

### 3.3 Pipeline Implementation

```cpp
SystemResult GCSSystem::solve(const std::string& inputPath, SystemAction action) {
    SystemResult result;
    result.inputPath = inputPath;

    // Step 1: Read
    io::readGraph(manager_, inputPath);
    if (manager_.geometries.empty() && manager_.constraints.empty()) {
        result.success = false;
        result.errorMessage = "Failed to read graph or empty graph";
        return result;
    }

    // Step 2: Decompose
    dcm::DecompositionManager dcm;
    result.decomposition = dcm.decompose(manager_);

    // Step 3: Analyze each sub-problem
    lgs::LocalGeometricSolver lgs;
    for (const auto& sp : result.decomposition.subProblems) {
        result.statusReports.push_back(lgs.analyzeStatus(manager_, sp));
    }
    result.globalStatus = lgs.analyzeStatus(manager_);

    // Step 4: Solve (if requested)
    if (action == SystemAction::Solve || action == SystemAction::SolveAndDisplay) {
        cds::ConstraintDrivenSolver solver(solverConfig_);
        for (auto& sp : result.decomposition.subProblems) {
            auto report = solver.solveSubProblem(manager_, sp);
            result.solverReports.push_back(report);
        }
        // Compose results
        dcm.compose(manager_, result.decomposition.subProblems, ...);
    }

    // Step 5: Display (if requested)
    if (action == SystemAction::SolveAndDisplay) {
        io::dumpGraph(manager_, inputPath);
    }

    result.success = true;
    return result;
}
```

---

## 4. Core Module Interface

### 4.1 types.h

```cpp
#pragma once

namespace gcs {

enum class GeometryType {
    Point = 0,
    Line = 1,
    Plane = 2
};

enum class ConstraintType {
    Coincident = 0,
    Parallel = 1,
    Perpendicular = 2,
    Distance = 3,
    Angle = 4
};

}
```

### 4.2 core.h

```cpp
#pragma once

#include "types.h"
#include <vector>
#include <string>
#include <array>

namespace gcs {

struct RigidSet {
    int id;
    std::vector<int> geometryIds;
};

struct Geometry {
    int id;
    GeometryType type;
    int rigidSetId;
    double v[6];

    const Geometry* findGeometry(int id) const;
    Geometry* findGeometry(int id);
};

struct Constraint {
    int id;
    ConstraintType type;
    std::vector<int> geometryIds;
    double value;
};

struct Manager {
    std::vector<RigidSet> rigidSets;
    std::vector<Geometry> geometries;
    std::vector<Constraint> constraints;

    RigidSet* findRigidSet(int id);
    const RigidSet* findRigidSet(int id) const;
    Geometry* findGeometry(int id);
    const Geometry* findGeometry(int id) const;
    Constraint* findConstraint(int id);
    const Constraint* findConstraint(int id) const;
    std::vector<Geometry*> geometriesInRigidSet(int rigidSetId);
};

std::string typeNameGeometry(GeometryType t);
std::string typeNameConstraint(ConstraintType t);
int dofGeometry(GeometryType t);
int dofRemovedConstraint(ConstraintType t);

}
```

---

## 5. IO Module Interface

### 5.1 io.h

```cpp
#pragma once

#include "core.h"
#include <string>

namespace gcs {
namespace io {

void readGraph(Manager& m, const std::string& path);
void dumpGraph(const Manager& m, const std::string& inputPath);
void displayGraph(const std::string& graphFile);
void printSummary(const Manager& m);

}
}
```

### 5.2 Interface Contract

| Function | Input | Output | Side Effects | Error Handling |
|----------|-------|--------|-------------|----------------|
| `readGraph` | File path | Populates Manager | None | Prints to stderr, returns with empty/partial Manager |
| `dumpGraph` | Manager + input path | Writes `_graph.txt` file | Creates file, may launch browser | Returns early if path empty or file creation fails |
| `displayGraph` | Graph file name | None | Launches browser process | No error handling (system call) |
| `printSummary` | Manager | None | Writes to stdout | None |

---

## 6. DCM Module Interface

### 6.1 dcm.h

```cpp
#pragma once

#include "core.h"
#include <vector>
#include <unordered_map>
#include <unordered_set>

namespace gcs {
namespace dcm {

struct SubProblem {
    int id;
    std::vector<int> geometryIds;
    std::vector<int> constraintIds;
    std::vector<int> rigidSetIds;
};

struct DecompositionResult {
    std::vector<SubProblem> subProblems;
    int totalGeometries;
    int totalConstraints;
    bool isSingleComponent;
};

class DecompositionManager {
public:
    DecompositionManager() = default;

    DecompositionResult decompose(const Manager& m);

    Manager compose(const Manager& original,
                    const std::vector<SubProblem>& solvedSubProblems);

    SubProblem extractSubProblem(const Manager& m,
                                 const std::vector<int>& geometryIds) const;

private:
    void buildAdjacencyList(const Manager& m);
    std::vector<std::vector<int>> findConnectedComponents();
    std::vector<int> bfsComponent(int startGeomId);

    std::unordered_map<int, std::vector<int>> adjacencyList_;
    std::unordered_set<int> visited_;
};

}
}
```

### 6.2 Interface Contract

| Function | Input | Output | Side Effects | Complexity |
|----------|-------|--------|-------------|-----------|
| `decompose` | Manager (const) | DecompositionResult | None | O(V+E) |
| `compose` | Original Manager + solved sub-problems | New Manager | None | O(V) |
| `extractSubProblem` | Manager + geometry IDs | SubProblem | None | O(V+C) |

---

## 7. LGS Module Interface

### 7.1 lgs.h

```cpp
#pragma once

#include "core.h"
#include "dcm.h"
#include <vector>
#include <string>

namespace gcs {
namespace lgs {

enum class ConstraintStatus {
    WellConstrained,
    UnderConstrained,
    OverConstrained,
    OverConstrainedConsistent
};

std::string toString(ConstraintStatus status);

struct DOFAnalysis {
    int geometryDOF;
    int constraintRemovedDOF;
    int netDOF;
    ConstraintStatus status;
};

struct ConstraintViolation {
    int constraintId;
    double residual;
    double tolerance;
    bool satisfied;
};

struct StatusReport {
    ConstraintStatus overallStatus;
    DOFAnalysis dofAnalysis;
    std::vector<ConstraintViolation> violations;
    bool isConsistent;
    std::string summaryText;
};

class LocalGeometricSolver {
public:
    LocalGeometricSolver() = default;

    DOFAnalysis analyzeDOF(const Manager& m) const;
    DOFAnalysis analyzeDOF(const Manager& m, const dcm::SubProblem& sp) const;

    StatusReport analyzeStatus(const Manager& m) const;
    StatusReport analyzeStatus(const Manager& m, const dcm::SubProblem& sp) const;

    std::vector<ConstraintViolation> checkSatisfaction(
        const Manager& m,
        double tolerance = 1e-6) const;

    bool isWellConstrained(const Manager& m) const;
    bool isUnderConstrained(const Manager& m) const;
    bool isOverConstrained(const Manager& m) const;

private:
    int computeGeometryDOF(const Manager& m, const dcm::SubProblem& sp) const;
    int computeConstraintRemovedDOF(const Manager& m, const dcm::SubProblem& sp) const;
    ConstraintStatus classifyStatus(int netDOF) const;
    double computeConstraintResidual(const Manager& m, const Constraint& c) const;
};

}
}
```

### 7.2 Interface Contract

| Function | Input | Output | Side Effects | Notes |
|----------|-------|--------|-------------|-------|
| `analyzeDOF` | Manager (const) | DOFAnalysis | None | Fast: O(G+C) |
| `analyzeStatus` | Manager (const) | StatusReport | None | Includes DOF + consistency |
| `checkSatisfaction` | Manager (const) + tolerance | vector<ConstraintViolation> | None | Evaluates constraint residuals |
| `isWellConstrained` | Manager (const) | bool | None | Shortcut for status check |

---

## 8. CDS Module Interface

### 8.1 cds.h

```cpp
#pragma once

#include "core.h"
#include "lgs.h"
#include "dcm.h"
#include <vector>
#include <string>

namespace gcs {
namespace cds {

struct SolverConfig {
    int maxIterations = 100;
    double tolerance = 1e-8;
    double dampingFactor = 1.0;
    bool verbose = false;
};

enum class SolverResult {
    Converged,
    Diverged,
    MaxIterationsReached,
    SingularJacobian,
    InconsistentConstraints
};

std::string toString(SolverResult result);

struct SolverReport {
    SolverResult result;
    int iterationsUsed;
    double initialResidual;
    double finalResidual;
    std::vector<double> residualHistory;
};

class ConstraintDrivenSolver {
public:
    explicit ConstraintDrivenSolver(const SolverConfig& config = SolverConfig{});

    SolverReport solve(Manager& m);
    SolverReport solveSubProblem(Manager& m, const dcm::SubProblem& sp);

    void setConfig(const SolverConfig& config);
    const SolverConfig& config() const;

private:
    std::vector<double> computeResiduals(const Manager& m, const dcm::SubProblem& sp);
    std::vector<std::vector<double>> computeJacobian(
        const Manager& m, const dcm::SubProblem& sp);
    bool updateParameters(Manager& m, const dcm::SubProblem& sp,
                          const std::vector<double>& delta);
    double computeTotalResidual(const std::vector<double>& residuals);

    SolverConfig config_;
};

}
}
```

### 8.2 Interface Contract

| Function | Input | Output | Side Effects | Notes |
|----------|-------|--------|-------------|-------|
| `solve` | Manager (mutable) | SolverReport | Modifies Manager parameters | Solves all sub-problems |
| `solveSubProblem` | Manager (mutable) + SubProblem | SolverReport | Modifies geometry parameters | Solves one sub-problem |
| `setConfig` | SolverConfig | None | Updates config | Affects next solve call |

---

## 9. Cross-Module Data Contracts

### 9.1 Data Flow Summary

```
IO.readGraph() → Manager (populated)
                       │
                       ▼
              DCM.decompose(Manager) → DecompositionResult { vector<SubProblem> }
                       │
                       ▼
              LGS.analyzeStatus(Manager, SubProblem) → StatusReport
                       │
                       ▼
              CDS.solveSubProblem(Manager, SubProblem) → SolverReport
                       │                       │
                       │    Manager is mutated with solved parameters
                       ▼
              DCM.compose(Manager, SubProblems) → Manager (solved)
                       │
                       ▼
              IO.dumpGraph(Manager) → file + browser
```

### 9.2 Key Contracts

| Contract | Enforced By |
|----------|------------|
| Manager is populated before DCM/LGS/CDS | GCSSystem pipeline order |
| SubProblem geometry IDs are valid Manager indices | DCM.decompose() guarantees this |
| SubProblem constraint IDs reference constraints within the sub-problem | DCM.decompose() guarantees this |
| LGS must analyze before CDS solves | GCSSystem pipeline order |
| CDS modifies Manager geometry parameters in-place | CDS.solveSubProblem() contract |
| IO does not modify Manager topology | IO.dumpGraph() takes const Manager& |

### 9.3 Ownership Rules

| Data | Owner | Lifetime |
|------|-------|----------|
| Manager | GCSSystem (or caller) | Entire pipeline |
| SubProblem | DecompositionResult | Until compose() |
| StatusReport | Caller | After analyzeStatus() returns |
| SolverReport | Caller | After solve() returns |

---

## 10. Error Handling Strategy

### 10.1 Error Categories

| Category | Example | Handling |
|----------|---------|----------|
| **IO Error** | File not found, parse error | Print to stderr, return early |
| **Data Error** | Invalid geometry ID, missing parameter | Print to stderr, return early |
| **Solver Error** | Singular Jacobian, divergence | Return SolverReport with error status |
| **Status Error** | Over-constrained, inconsistent | Return StatusReport with error status |

### 10.2 Error Propagation

```
IO Error → readGraph returns with partial/empty Manager
           ↓
           GCSSystem checks Manager, returns SystemResult with errorMessage

Solver Error → solveSubProblem returns SolverReport with error result
               ↓
               GCSSystem collects all reports, returns SystemResult

Status Error → analyzeStatus returns StatusReport with error status
               ↓
               GCSSystem decides whether to proceed with solving
```

### 10.3 Future: Exception Strategy (Phase 2+)

```cpp
namespace gcs {

class GCSError : public std::runtime_error {
public:
    explicit GCSError(const std::string& what) : std::runtime_error(what) {}
};

class IOError : public GCSError { using GCSError::GCSError; };
class ParseError : public IOError { using IOError::IOError; };
class SolverError : public GCError { using GCError::GCError; };
class SingularJacobianError : public SolverError { using SolverError::SolverError; };

}
```

---

## 11. Include Dependency Graph

```
types.h           ← No dependencies
    │
    ▼
core.h            ← Includes types.h
    │
    ├──────────────────────┐
    ▼                      ▼
io.h                dcm.h           ← Both include core.h
                         │
                         ▼
                    lgs.h           ← Includes core.h, dcm.h
                         │
                         ▼
                    cds.h           ← Includes core.h, lgs.h, dcm.h
                         │
                         ▼
                 gcs_system.h      ← Includes all above
```

**Rule**: No circular includes. A module may only include headers from modules it depends on (per the dependency diagram in architecture.md).

---

## 12. C++ Header File Layout per Module

Each module folder follows this structure:

```
module_name/
├── include/gcs/module_name/
│   └── module_name.h      ← Public header (the only include clients need)
└── src/
    └── module_name.cpp     ← Implementation
```

Clients include like this:
```cpp
#include "gcs/core/types.h"     // Core types
#include "gcs/io/io.h"          // IO functions
#include "gcs/dcm/dcm.h"        // DCM classes
#include "gcs/lgs/lgs.h"        // LGS classes
#include "gcs/cds/cds.h"        // CDS classes
```

The include path is set to the module's `include/` directory. Since all modules use `gcs/` as the top-level include prefix, and each module adds its own `include/` to the include path, the resolution works correctly:

- `core/include/` → resolves `gcs/core/types.h`
- `io/include/` → resolves `gcs/io/io.h`
- `dcm/include/` → resolves `gcs/dcm/dcm.h`
- etc.
