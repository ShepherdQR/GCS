# Problem Formulation

## Mathematical Object

A geometric constraint system is a typed constraint satisfaction problem on a
product of manifolds:

```text
state x in M = M_1 x M_2 x ... x M_n
constraints f_j(x[S_j], p_j) = 0
objective min 1/2 || W f(x) ||^2 when exact satisfaction is not reached
```

Each geometric entity owns a parameter manifold. A point in 2D is Euclidean;
a line, plane, rigid body, or frame may live on a quotient or Lie group
representation. The architecture must not assume every entity is just a flat
vector, even when early implementations store coordinates that way.

## Gauge And Degrees Of Freedom

Constraint status is meaningful only after accounting for gauge freedom.
Examples:

- An unconstrained 2D sketch has global translation and rotation freedom.
- A rigid set has an internal shape and an external transform.
- A subproblem may be well constrained modulo an anchor frame.

The status of a system is determined by both structural rank and numeric rank:

```text
free_dof = dim(tangent_space) - rank(J) - gauge_dof
```

Counting equations is a useful pre-filter, never a proof. The solver must
distinguish generic structural behavior from a specific degenerate numeric
configuration.

## Graph View

The combinatorial shadow of the problem is an incidence hypergraph:

```text
geometry vertices V
constraint hyperedges E
rigid/group vertices R
dependency projections P
```

Useful projections include geometry-constraint incidence, body-constraint
graphs, connected components, biconnected components, articulation structure,
and future SPQR-like decompositions for 2D rigidity planning.

## Numeric View

The numeric engine sees a local least-squares or root-finding problem:

```text
r(x) = [f_1(x), ..., f_m(x)]
J(x) = dr/dx
solve J dx = -r with trust, damping, scaling, and constraints on updates
```

The architecture must expose residual norm, step norm, rank estimate,
conditioning, active tolerances, iteration history, and failure cause. A
coordinate update without these diagnostics is not an acceptable solver result.

## Diagnostic View

The user does not only need an answer; they need an explanation. The system
must classify at least:

- well constrained;
- under constrained;
- over constrained;
- redundantly constrained;
- inconsistent;
- numerically singular;
- structurally decomposable;
- not currently supported.

These classifications should be attached to stable entity and constraint IDs so
that UI, tests, and logs can explain the same event in different forms.
