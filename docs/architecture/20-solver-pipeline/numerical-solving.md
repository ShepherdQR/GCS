# Numerical Solving

## Purpose

The numeric engine solves prepared equation systems on local parameter spaces.
It is replaceable: a simple dense baseline, a sparse backend, or a future
construction-based solver should all fit behind the same task/report contract.
Under the local-to-global architecture, each numeric task computes a local
section over one context. It does not decide whether that section glues with
other local sections.

## Prepared Solve Task

A solve task should include:

- immutable problem snapshot;
- context ID and context boundary metadata;
- active entity IDs;
- active constraint IDs;
- active boundary variables and overlap projections;
- gauge-fixing or anchor policy;
- parameterization policy;
- tolerance policy;
- scaling policy;
- initial state vector;
- requested solve mode;
- maximum iterations and trust-region limits.

## Engine Responsibilities

The numeric engine owns:

- residual assembly;
- Jacobian assembly or approximation;
- scaling;
- damping and trust-region logic;
- manifold-aware update application;
- convergence tests;
- iteration trace;
- proposal generation.

It does not own:

- model identity;
- graph decomposition;
- overlap compatibility or global gluing;
- user command semantics;
- file IO;
- visualization;
- final transaction commit.

## Report Metrics

Each numeric report should include:

- result code;
- residual norm before and after;
- step norm;
- rank estimate;
- condition estimate when available;
- active tolerance values;
- iteration count;
- accepted or rejected steps;
- constraints with largest residual;
- entities with largest update;
- failure cause.

## Manifold Update Rule

The engine should apply updates through entity-specific retraction operations:

```text
x_next = retract(x_current, delta)
```

This lets points, directions, lines, planes, rotations, and rigid transforms use
representations appropriate to their geometry while preserving one solver
contract.

## Acceptance Rule

A numeric result is only a proposal. The global pipeline accepts it only when
post-solve diagnostics verify the requested constraints and when the report is
compatible with the user command policy.
