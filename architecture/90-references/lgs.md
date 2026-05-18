# LGS Reference Architecture

## Product Boundary

LGS refers to LEDAS Geometric Solver. Public material describes LGS 2D and LGS 3D as commercial geometric constraint solver components for sketching, direct 3D modeling, assembly design, and motion analysis. LEDAS later sold LGS IP rights to Bricsys, now part of Hexagon.

Sources:

- LEDAS 3D Modeling expertise page: https://ledas.com/en/expertise/3d-modeling/
- LEDAS "Five Constraint Solvers" article: https://ledas.com/post/848-ledas-has-developed-five-constraint-solvers/
- LGS 1.0 release article: https://ledas.com/news/1-ledas-launches-first-release-of-its-2d-geometric-solver-solution-lgs-and-announces-forthcoming-3d-geometric-solver/
- LGS 2D profile management article: https://ledas.com/news/152-ledas-adds-profile-management-to-lgs-2d-constraint-solver/
- "LGS: Geometric Constraint Solver" abstract: https://www.researchgate.net/publication/220810323_LGS_Geometric_Constraint_Solver

## Key Design

The strongest public architecture signal for LGS is decomposition plus specialization:

- Decompose the initial problem into simpler problems.
- Map each instance to a class of problems.
- Apply a specialized algorithm to each class.
- Maintain an extensible hierarchy of problem classes.
- Combine decomposition, algebraic methods, computational methods, and numerical algorithms.

Public LEDAS material also emphasizes:

- A highly optimized in-house non-linear solver.
- Geometric decomposition methods.
- Heuristics tuned against thousands of industrial tests.
- Rigid sets.
- Over-defined diagnostics.
- Ability to solve over-constrained but consistent cases.
- Partial solutions for inconsistent cases.
- Natural behavior, meaning solutions should stay close to the initial configuration when possible.
- C-style APIs and wrappers for integration across host applications.
- Bounded geometry as first-class objects, such as segments and arcs modeled as edges with dependent underlying objects.

This suggests a solver architecture with a rich internal representation, a planning/decomposition stage, a classifier, a library of specialized solvers, a numerical fallback, and strong test/replay support.

## Design Lessons For Us

Our current `dcm` should be treated as the beginning of a planner, not the whole decomposition story. Connected components are only the first pass. The next passes should classify sub-problems by rigidity, DOF, constraint signatures, and whether they are suitable for specialized or numeric solving.

Our current `lgs` should own structural diagnostics. It should detect well/under/over status, consistency, violations, and eventually conflicting or redundant constraints before `cds` tries numerical movement.

Our current `cds` should stay replaceable. LGS-like architecture assumes multiple algorithms over time; therefore `cds` should be a leaf solver behind a small report-oriented interface.

## What We Should Not Copy Yet

Do not build a hierarchy of specialized solvers prematurely. Start by making the planner and diagnostics explicit, then add specialized cases only where tests prove they reduce complexity.

