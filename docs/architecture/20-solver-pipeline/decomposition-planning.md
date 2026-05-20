# Decomposition And Planning

## Purpose

The decomposition planner turns a raw constraint graph into a solve strategy.
It is the bridge between combinatorics and numerics.

## Structural Layers

1. Incidence graph: constraints as hyperedges over geometric entities.
2. Rigid-set graph: group internal entities and expose external transforms.
3. Component graph: independent connected components.
4. Articulation and biconnected structure: split along separators.
5. Rigidity candidates: detect generically rigid or flexible clusters.
6. Solve DAG: order subproblems and shared boundary variables.

## Planner Output

The planner should produce:

- subproblem IDs;
- entity and constraint membership;
- boundary variables;
- anchors or gauge-fixing policy;
- expected DOF;
- structural warnings;
- solve order;
- fallback strategy when a preferred decomposition is not supported.

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

It may ask diagnostics for rank or status information, but its output remains a
plan, not a solved model.
