# Commercial GCS Summary

## Common Architecture Pattern

The mainstream commercial solvers studied here are CDS, D-Cubed 2D DCM, D-Cubed 3D DCM, and LGS. Their public details point to the same broad architecture:

1. The solver is an embeddable component. The CAD application owns UI, persistence, geometry kernel integration, and product workflow.
2. The solver consumes an abstract constraint model. It does not need to own the full CAD document.
3. Structural model and behavior model are separate. Entities and constraints describe what exists; update, drag, simulation, fixed objects, driven objects, and target values describe what the user is asking the solver to do.
4. Decomposition happens before heavy numeric solving. A mature solver decomposes sparse graphs, classifies sub-problems, applies special cases, and then uses numerical solving where needed.
5. Diagnostics are part of the core product. Under-defined, over-defined, conflicting, redundant, consistent-overdefined, singular, and partial-solution states matter as much as "converged."
6. Rigid sets are first-class in 3D. Assembly solving is about transforming bodies while preserving internal shape.
7. Interactive naturalness is an explicit behavior goal. Good solvers minimize unnecessary movement and keep results close to the user's initial model.
8. Test and replay infrastructure are essential. Industrial solvers are tuned through large generated and real-world suites.

## Our Architecture Direction

The project should stay small, local, and demonstrable, but its boundaries should mirror the commercial pattern:

| Layer | Responsibility |
| --- | --- |
| `core` | Structural model plus behavior model: rigid sets, geometry, constraints, solve mode, fixed/driven/target intent |
| `io` | Text/JSON serialization for reproducible scenes and lightweight demos |
| `dcm` | Structural decomposition and future planning/classification hooks |
| `lgs` | DOF/status/violation diagnostics before and after solving |
| `cds` | Numeric leaf solver for prepared sub-problems |
| `app` | Thin orchestration facade for demo executable, not long-term model ownership |
| `gcs_viz` | Local lightweight graph/DOF behavior visualization |

## Decisions

Keep:

- `Manager` as the structural graph container.
- `RigidSet`, `Geometry`, and `Constraint` as first-class model objects.
- A separate behavior model that can express update, drag, and simulation-like intent.
- The Python visualization layer as a local, light inspection tool.
- The current numeric code temporarily, because it is useful as a leaf solver and test harness even if it is not the final algorithm.

Change now:

- Document commercial solver lessons under `docs/architecture/90-references/`.
- Make behavior intent explicit in `core`.
- Keep noisy numeric debug output behind `SolverConfig::verbose`.
- Treat `app` as a demo orchestration layer instead of a core architecture layer.

Delete or avoid:

- Avoid a heavyweight CAD editor or web UI at this stage.
- Avoid making visualization the owner of solver state.
- Avoid adding full 2D sketch inference, free-form geometry, kinematics, or equations before the graph behavior is stable.
- Avoid app-specific abstract model wrappers unless an external integration actually needs them.
