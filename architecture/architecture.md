# GCS System Architecture

## Overview

GCS (Geometric Constraint Solver) represents geometric entities and constraints, decomposes the constraint graph, analyzes constraint status, and solves parameters with a C++ solver core.

The visual entry point is the desktop/TUI launcher at `GCS/start_tui.bat`.

## Modules

| Module | Responsibility |
|--------|----------------|
| `core` | Shared data model: geometry, constraint, rigid set, manager, type helpers |
| `io` | Read/write graph files and print summaries |
| `dcm` | Decompose the graph into independent sub-problems |
| `lgs` | Analyze DOF and constraint status |
| `cds` | Numerically solve constraint-driven sub-problems |
| `app` | Application facade and C++ executable entry point |
| `gcs_viz` | Python visual interface launched by `start_tui.bat` |

## Dependencies

```text
core
  ^
  |
  +-- io
  +-- dcm
        ^
        |
        +-- lgs
              ^
              |
              +-- cds

app depends on core, io, dcm, lgs, and cds.
gcs_viz calls the compiled GCS.exe through engine_bridge.py.
```

Rules:

- `core` does not depend on other GCS modules.
- `io` depends only on `core`.
- `dcm` depends only on `core`.
- `lgs` depends on `core` and `dcm`.
- `cds` depends on `core`, `dcm`, and `lgs`.
- `app` orchestrates the full pipeline.

## Data Flow

```text
scene/*.txt
   -> io::readGraph
   -> Manager
   -> dcm::DecompositionManager
   -> lgs::LocalGeometricSolver
   -> cds::ConstraintDrivenSolver
   -> io::dumpGraph / io::printSummary
```

## Directory Structure

```text
GCS/
  GCS.sln
  README.md
  architecture/
  GCS/
    app/
      App.h
      App.cpp
      main.cpp
    core/
      types.h
      core.h
      core.cpp
    io/
      io.h
      io.cpp
    dcm/
      dcm.h
      dcm.cpp
    lgs/
      lgs.h
      lgs.cpp
    cds/
      cds.h
      cds.cpp
    gcs_viz/
    scene/
    test/
    start_tui.bat
```

Each C++ module is intentionally flat: headers and implementation files live directly inside the module directory.

## Build Output

Generated files are kept out of source folders:

```text
build/bin/<Platform>/<Configuration>/
build/obj/<Project>/<Platform>/<Configuration>/
build/obj/tests/<Platform>/<Configuration>/
```

`build/` is ignored by Git.
