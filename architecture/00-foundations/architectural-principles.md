# Architectural Principles

## Separate Semantics From Coordinates

The domain model defines what a point, line, rigid set, constraint, and solve
intent mean. The numeric representation defines how they are parameterized for
one solve. These are not the same layer.

Rules:

- Entity identity is stable across solves.
- Coordinates are versioned state, not identity.
- Constraint semantics live in a catalog, not in ad hoc solver branches.
- Tolerances and units are explicit policy objects.

## Make Reports First Class

Every major stage returns a report:

- validation report;
- decomposition report;
- structural status report;
- numeric solve report;
- final verification report.

Reports are part of the API, not debug strings. They must carry entity IDs,
constraint IDs, status codes, metrics, and enough provenance to reproduce the
decision.

## Plan Before Solving

A top-tier GCS should not throw the whole system into one numeric loop by
default. It should:

1. validate the model;
2. build incidence structures;
3. decompose connected and rigid components;
4. classify generic DOF and possible singularities;
5. choose a solve schedule;
6. solve leaves with the numeric engine;
7. assemble and verify globally.

## Respect Degeneracy

Degenerate geometry is normal in CAD and sketching:

- coincident points;
- parallel lines;
- zero-length segments;
- nearly singular angle constraints;
- symmetric configurations;
- redundant dimensions.

Degeneracy must be represented explicitly through status and rank diagnostics,
not hidden as a generic solver failure.

## Keep Boundaries Narrow

Modules should exchange typed inputs and reports. They should not share mutable
global state, UI objects, file paths, or console output.

The only layer allowed to orchestrate a full user command is `session_runtime`.
The only layer allowed to mutate active coordinates is a transaction approved by
the runtime and executed by the numeric engine.

## Prefer Replaceable Engines

The architecture should allow a simple baseline solver, a sparse solver, a
symbolic/geometric construction solver, and a future commercial-grade numeric
engine to sit behind the same contracts. The correct abstraction is not
"Newton method"; it is "prepared solve task in, certificate-bearing report out."
