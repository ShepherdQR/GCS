# Verification Strategy

## Quality Thesis

A geometric constraint solver is correct only when it returns the right state
and the right explanation. Tests must therefore cover both coordinates and
diagnostics.

## Test Layers

| Layer | Purpose |
| --- | --- |
| Kernel tests | Identity, typing, units, tolerance, serialization invariants. |
| Constraint tests | Residuals, Jacobians, degeneracy warnings, DOF metadata. |
| Graph tests | Incidence projections, components, separators, rigid groups. |
| Planner tests | Subproblem extraction, gauge policy, solve order, unsupported cases. |
| Numeric tests | Convergence, rank, residual reduction, iteration status. |
| Diagnostic tests | Under/over/well/inconsistent/redundant classifications. |
| Pipeline tests | End-to-end command result and report consistency. |
| Regression fixtures | Real scenes and previously failing cases. |

## Scenario Corpus

Fixtures should be organized by mathematical behavior:

```text
fixtures/
  minimal/
  well_constrained/
  under_constrained/
  over_constrained/
  redundant/
  inconsistent/
  singular/
  decomposable/
  rigid_sets/
  interaction_modes/
  regression/
```

The current `fixtures/scene/` directory seeds this corpus during the rewrite.

## Acceptance Gates

A solver result should be accepted by tests only when:

- final residuals are within tolerance;
- free DOF classification matches expectation;
- over-constraint or redundancy is reported when expected;
- result is deterministic under fixed configuration;
- reports identify relevant entity and constraint IDs;
- serialization round-trips without losing identity.

## Numeric Robustness Tests

Numerical tests should include:

- scaled scenes;
- near-degenerate configurations;
- poor initial guesses;
- redundant equations;
- disconnected components;
- anchor/gauge variants;
- randomized perturbations around known solutions.

## Documentation Tests

Architecture examples should become executable fixtures when the rewrite starts.
Every architectural claim about a class of scene should eventually map to a
scenario test.
