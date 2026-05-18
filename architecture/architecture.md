# GCS System Architecture

## Overview

GCS (Geometric Constraint Solver) is a small C++ solver core with a local Python visualization layer. The design follows the useful parts of commercial GCS components: keep the constraint model independent from UI, split structural data from solve behavior, decompose before numeric solving, and return diagnostics as first-class output.

The commercial reference notes live in `architecture/reference/`.

## Model Split

| Model | Contents | Why it exists |
| --- | --- | --- |
| Structural model | `RigidSet`, `Geometry`, `Constraint`, stored in `Manager` | Describes what the constraint graph is |
| Behavior model | solve mode, fixed/driven geometry, target constraints | Describes what the user wants the solver to do |

The current implementation is intentionally small: points, lines, planes, five constraint types, rigid sets, and update-style solving. Dragging and simulation modes are represented as behavior intent so the architecture can grow without pushing UI gestures into the numeric solver.

## Modules

| Module | Responsibility |
|--------|----------------|
| `core` | Shared structural model, behavior model, type helpers |
| `io` | Read/write reproducible text/JSON scenes and print summaries |
| `dcm` | Structural graph decomposition; future home for planning/classification passes |
| `lgs` | DOF/status/violation diagnostics before and after solving |
| `cds` | Numeric leaf solver for prepared sub-problems |
| `app` | Thin demo orchestration facade and C++ executable entry point |
| `gcs_viz` | Local lightweight graph/DOF visualization launched by `start_tui.bat` |

## Dependencies

```text
core
  +-- io
  +-- dcm
  +-- lgs
  +-- cds

lgs depends on core and dcm.
cds depends on core and dcm.
app depends on core, io, dcm, lgs, and cds.
gcs_viz calls the compiled GCS.exe through engine_bridge.py.
```

Rules:

- `core` owns model types and depends only on the C++ standard library.
- `io` does not run solving logic.
- `dcm` does not run numeric solving.
- `lgs` diagnoses status and residuals; it does not mutate geometry.
- `cds` may mutate geometry inside the active sub-problem; it returns a report.
- `app` is not a long-term domain model. It is a small executable/demo facade.
- `gcs_viz` is a viewer/controller for local demos, not the owner of solver state.

## Data Flow

```text
scene/*.txt or scene/*.json
   -> io::readGraph / io::readGraphJSON
   -> Manager(structure + behavior)
   -> dcm::DecompositionManager
   -> lgs::LocalGeometricSolver pre-solve diagnostics
   -> cds::ConstraintDrivenSolver sub-problem solve
   -> lgs::LocalGeometricSolver post-solve diagnostics
   -> io::dumpGraph / io::printSummary
   -> gcs_viz graph and DOF behavior views
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

## Near-Term Architecture Decisions

- Keep `Manager` as the canonical in-memory graph.
- Keep `RigidSet` first-class. Future 3D assembly work should diagnose and solve set transforms, not only raw geometry coordinates.
- Keep the current numeric solver as a replaceable leaf implementation.
- Keep visualization local, small, and graph-oriented for showing constraint graph behavior.
- Do not add a heavyweight CAD editor, free-form geometry stack, 2D auto-constraint inference, or equation network until decomposition and diagnostics are reliable.

## Build Output

Generated files are kept out of source folders:

```text
build/bin/<Platform>/<Configuration>/
build/obj/<Project>/<Platform>/<Configuration>/
build/obj/tests/<Platform>/<Configuration>/
```

`build/` is ignored by Git.
