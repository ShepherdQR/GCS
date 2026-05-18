# CDS Reference Architecture

## Product Boundary

CDS here refers to Spatial's Constraint Design Solver. Public material positions it as a geometric constraint solver SDK for both 2D and 3D models. Its scope covers sketch recalculation, assembly component positioning, under/over-constrained analysis, rigid sets, joints, expressions, interactive manipulation, simulation-style solving, debugging, replay, and a graphical display environment.

Sources:

- Spatial CDS product page: https://www.spatial.com/solutions/3d-modeling/constraint-design-solver
- Spatial CDS data sheet search result: https://www.spatial.com/hubfs/_DATASHEETS/2021/2021_Spatial_Data%20Sheet_Constraint%20Design%20Solver.pdf

## Key Design

CDS is designed as an embeddable SDK, not as an end-user CAD application. The host application supplies the user workflow, geometry kernel, persistence, and display; CDS supplies a solver-facing model and a self-contained C++ API.

Its main architecture signal is the explicit separation between model structure and solve behavior:

- Structure: 2D/3D geometric objects, dimensional constraints, logical constraints, rigid sets, joints, patterns, expressions, conditions, chirality controls.
- Behavior: update mode, interactive dragging mode, and simulation mode.
- Diagnostics: under-constrained and over-constrained analysis, conflicting constraint feedback, debugging, replay, scripting, and display tooling.
- Runtime: high-performance, flexible, thread-safe solving for application integration.

The solver core is described as a non-linear simultaneous equation solver, but the product surface is broader than a numeric method. The commercial value comes from the API contract around model setup, behavior modes, diagnostics, and interactive repeatability.

## Design Lessons For Us

Keep `core` as a solver-facing model, not as UI state. The model must expose structural data and behavior intent separately:

- `StructureModel`: rigid sets, geometries, constraints, parameters.
- `BehaviorModel`: solve mode, fixed/driven objects, target constraints, interaction intent.

Keep `cds` focused on numeric solving. It should consume a prepared sub-problem and behavior intent, then return a report. It should not own files, UI, or application lifecycle.

Add diagnostics as first-class output. A useful solver reports whether a solve failed because the model is under-defined, over-defined, singular, conflicting, or simply not converged.

Keep the visualization local and small. CDS has display/debug aids, but not as the product center. For this project, the right equivalent is a lightweight graph and DOF behavior viewer.

## What We Should Not Copy Yet

Do not build full 2D/3D object coverage, joints, chirality, equations, replay scripting, or a debug display framework now. The architecture should leave room for them, but the implementation should stay small enough to reason about.

