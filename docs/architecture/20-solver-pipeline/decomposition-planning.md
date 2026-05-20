# Decomposition And Planning

## Purpose

The decomposition planner turns a raw constraint graph into a solve strategy.
It is the bridge between combinatorics and numerics, and it gives the solver a
local-to-global semantics by choosing a cover of contexts.

## Structural Layers

1. Incidence graph: constraints as hyperedges over geometric entities.
2. Rigid-set graph: group internal entities and expose external transforms.
3. Component graph: independent connected components.
4. Articulation and biconnected structure: split along separators.
5. Rigidity candidates: detect generically rigid or flexible clusters.
6. Context cover: name subproblems, overlaps, and restriction projections.
7. Solve DAG: order subproblems and shared boundary variables.

## Planner Output

The planner should produce:

- subproblem IDs;
- context IDs and a `CoverPlan`;
- entity and constraint membership;
- boundary variables;
- overlap contexts and boundary projections;
- anchors or gauge-fixing policy;
- expected DOF;
- structural warnings;
- solve order;
- fallback strategy when a preferred decomposition is not supported.

## Cover Rules

The planner must make the local-to-global contract explicit:

- every active entity and constraint belongs to at least one context;
- every shared variable is represented in an overlap context;
- every overlap has a projection from each participating context;
- every context declares whether it is solved independently, used as a boundary,
  or kept only for diagnostics;
- every gauge choice is represented as policy, not hidden inside a numeric task.

The resulting `CoverPlan` is not a solved model. It is a finite description of
which local sections must be produced and how they will be checked for
compatibility.

## Rigidity Principles

Equation count is only a rough necessary condition. The planner should evolve
toward rank-aware and graph-aware reasoning:

- connected components for immediate independence;
- body-bar or body-constraint projections for rigid sets;
- Laman-style tests where applicable for 2D point-distance sketches;
- articulation and SPQR-like decomposition for graph separators;
- numeric rank sampling to detect nongeneric degeneracy;
- explicit unsupported status when theory does not cover a case.

## Planner Boundaries

The planner must not:

- evaluate residuals by itself;
- mutate coordinates;
- print user-facing messages;
- silently drop constraints;
- choose UI behavior.
- decide that incompatible local sections are globally acceptable.

It may ask diagnostics for rank or status information, but its output remains a
plan, not a solved model.
