# GCS System Architecture

## 1. System Overview

GCS (Geometric Constraint Solver) is a system that represents geometric entities (points, lines, planes) and the constraints between them (coincident, parallel, perpendicular, distance, angle), then solves for the geometric parameters that satisfy all constraints.

The system follows a **modular pipeline architecture** where data flows through discrete processing stages, each encapsulated in a dedicated module with well-defined interfaces.

## 2. Module Decomposition

The system is decomposed into 5 modules:

```
┌─────────────────────────────────────────────────────────────┐
│                        GCS System                           │
│                                                             │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐        │
│  │ IO  │──▶│Core │──▶│ DCM │──▶│ LGS │──▶│ CDS │        │
│  └─────┘   └─────┘   └─────┘   └─────┘   └─────┘        │
│     │         │          │         │          │             │
│     ▼         ▼          ▼         ▼          ▼             │
│  Serialize  Data     Decompose  Analyze    Solve           │
│  Deserialize Model   Compose   Status     Parameters       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| Module | Full Name | Responsibility |
|--------|-----------|---------------|
| **Core** | Core Data Model | Data structures for geometries, constraints, rigid sets, and the constraint graph |
| **IO** | Input/Output | File parsing, serialization, graph visualization output |
| **DCM** | Decomposition Manager | Graph decomposition into independent sub-problems and composition of results |
| **LGS** | Local Geometric Solver | Constraint status analysis: DOF counting, well/over/under-constrained classification |
| **CDS** | Constraint Driven Solver | Numerical parameter solving using iterative methods (Newton-Raphson) |

## 3. Module Dependency Diagram

```
         ┌──────────┐
         │   IO     │
         └────┬─────┘
              │ reads/writes
              ▼
         ┌──────────┐
         │  Core    │ ◄── All modules depend on Core
         └────┬─────┘
              │ provides data model
              ▼
         ┌──────────┐
         │   DCM    │
         └────┬─────┘
              │ produces sub-problems
              ▼
         ┌──────────┐
         │   LGS    │
         └────┬─────┘
              │ validates status
              ▼
         ┌──────────┐
         │   CDS    │
         └──────────┘
```

**Dependency rules:**
- Core has no dependencies on other GCS modules
- IO depends only on Core
- DCM depends on Core
- LGS depends on Core
- CDS depends on Core and LGS (needs status info for solving strategy)
- No circular dependencies exist

## 4. Data Flow

The primary processing pipeline:

```
Input File (.txt)
      │
      ▼
  ┌─────────┐    Manager (empty)
  │   IO    │───────────────────┐
  │ readGraph│                  │
  └─────────┘                   │
      │                         ▼
      │                   Manager (populated)
      │                         │
      │                    ┌────┴────┐
      │                    │   DCM   │ decompose()
      │                    └────┬────┘
      │                         │
      │                         ▼
      │                  vector<SubProblem>
      │                         │
      │                    ┌────┴────┐
      │                    │   LGS   │ analyzeStatus()
      │                    └────┬────┘
      │                         │
      │                         ▼
      │               vector<SubProblem+Status>
      │                         │
      │                    ┌────┴────┐
      │                    │   CDS   │ solve()
      │                    └────┬────┘
      │                         │
      │                         ▼
      │               vector<SubProblem+SolvedParams>
      │                         │
      │                    ┌────┴────┐
      │                    │   DCM   │ compose()
      │                    └────┬────┘
      │                         │
      │                         ▼
      │                    Manager (solved)
      │                         │
      ▼                    ┌────┴────┐
  ┌─────────┐             │   IO    │ dumpGraph()
  │ Console │◄────────────└─────────┘
  └─────────┘
      │
      ▼
  ┌─────────┐
  │ Browser │ display.html (3D visualization)
  └─────────┘
```

## 5. SOLID Principles Application

| Principle | Application |
|-----------|-------------|
| **SRP** | Each module has a single responsibility: Core=data, IO=serialization, DCM=decomposition, LGS=status, CDS=solving |
| **OCP** | New geometry/constraint types added via class hierarchy without modifying existing solver code |
| **LSP** | All GeometryBase subclasses are interchangeable; all ConstraintBase subclasses are interchangeable |
| **ISP** | Separate interfaces: `ISerializable`, `ISolvable`, `IConstraintEquation` — clients depend only on what they need |
| **DIP** | CDS depends on abstract `IConstraintEquation` interface, not concrete constraint types; DCM depends on abstract graph interface |

## 6. Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | C++17 |
| Build System | MSBuild / Visual Studio 2022 (v143 toolset) |
| Linear Algebra | Custom small matrix class (no external dependency) |
| Visualization | Three.js (web-based, served via Python HTTP server) |
| Testing | Custom lightweight test framework (to be implemented) |

## 7. Directory Structure

```
GCS/
├── architecture/                  ← Architecture documentation
│   ├── architecture.md            ← This file (system overview)
│   ├── interface.md               ← GCS system interface design
│   ├── core/
│   │   └── core.md                ← Core module architecture
│   ├── dcm/
│   │   └── dcm.md                 ← DCM module architecture
│   ├── cds/
│   │   └── cds.md                 ← CDS module architecture
│   ├── lgs/
│   │   └── lgs.md                 ← LGS module architecture
│   └── io/
│       └── io.md                  ← IO module architecture
├── GCS/
│   ├── core/                      ← Core module
│   │   ├── include/gcs/core/
│   │   │   └── types.h            ← GeometryType, ConstraintType enums
│   │   └── src/
│   │       └── core.cpp           ← Core implementation
│   ├── io/                        ← IO module
│   │   ├── include/gcs/io/
│   │   │   └── io.h               ← readGraph, dumpGraph, displayGraph
│   │   └── src/
│   │       └── io.cpp             ← IO implementation
│   ├── dcm/                       ← DCM module
│   │   ├── include/gcs/dcm/
│   │   │   └── dcm.h              ← DecompositionManager
│   │   └── src/
│   │       └── dcm.cpp            ← DCM implementation
│   ├── lgs/                       ← LGS module
│   │   ├── include/gcs/lgs/
│   │   │   └── lgs.h              ← LocalGeometricSolver
│   │   └── src/
│   │       └── lgs.cpp            ← LGS implementation
│   ├── cds/                       ← CDS module
│   │   ├── include/gcs/cds/
│   │   │   └── cds.h              ← ConstraintDrivenSolver
│   │   └── src/
│   │       └── cds.cpp            ← CDS implementation
│   ├── app/                       ← Application entry point
│   │   └── src/
│   │       └── main.cpp           ← Entry point
│   ├── display/                   ← Python display system
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   ├── server.py
│   │   ├── viewer.py
│   │   └── web/
│   │       └── index.html
│   ├── model/                     ← Python data model
│   │   ├── __init__.py
│   │   └── graph.py
│   ├── display.html               ← Legacy web viewer
│   └── g1.txt                     ← Sample input
├── note.md
└── Readme.md
```

## 8. Module Architecture Documents

For detailed architecture of each module, see:

- [System Interface](interface.md) — GCS system-level API and cross-module contracts
- [Core Module](core/core.md) — Data model and class hierarchies
- [DCM Module](dcm/dcm.md) — Decomposition Manager
- [CDS Module](cds/cds.md) — Constraint Driven Solver
- [LGS Module](lgs/lgs.md) — Local Geometric Solver
- [IO Module](io/io.md) — Input/Output
