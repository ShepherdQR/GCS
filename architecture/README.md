# GCS Architecture

This directory is the architectural source of truth for the next GCS rewrite.
It is intentionally organized by reasoning order, not by the current source
tree. The current implementation can still inform examples, but it must not
define the next design by accident.

## Reading Order

1. `00-foundations/`
   - `problem-formulation.md`: the mathematical problem GCS solves.
   - `architectural-principles.md`: invariants that shape every module.
2. `10-system/`
   - `system-topology.md`: target module topology and dependency rules.
   - `current-to-target-map.md`: how the existing module names map to the
     rewrite architecture.
3. `20-solver-pipeline/`
   - `pipeline.md`: end-to-end solve flow.
   - `decomposition-planning.md`: graph and rigidity planning.
   - `numerical-solving.md`: nonlinear numerical solve architecture.
4. `30-contracts/`
   - `domain-contracts.md`: durable data model and identity contracts.
   - `solver-contracts.md`: planner, diagnostics, and numeric engine contracts.
5. `40-quality/`
   - `verification-strategy.md`: tests, scenario corpus, and correctness gates.
6. `90-references/`
   - Commercial and research notes used as background material.

## Target Thesis

Geometric constraint solving is not primarily a UI problem or a least-squares
problem. It is a layered problem over:

- a semantic domain model with stable identity;
- a combinatorial incidence and rigidity structure;
- a family of nonlinear equations on manifolds;
- a planning problem that chooses solvable substructures;
- a numerical problem that must report rank, residual, and conditioning;
- a diagnostic problem that explains under-constraint, over-constraint,
  redundancy, conflict, and failure.

The architecture therefore separates model, graph, planner, diagnostics,
numeric engine, runtime, IO, and visualization. A solver run should produce not
only coordinates, but also a certificate-like report that explains what was
solved, what remains free, what is inconsistent, and how reliable the result is.

## Target Directory Vocabulary

The rewrite should prefer these conceptual module names:

| Target name | Meaning |
| --- | --- |
| `kernel` | Domain entities, constraints, units, tolerances, coordinates, IDs. |
| `constraint_catalog` | Equation semantics and analytic Jacobian providers. |
| `incidence_graph` | Hypergraph/body graph projections and structural indices. |
| `decomposition_planner` | Rigidity, clustering, ordering, and solve scheduling. |
| `diagnostics` | DOF, rank, residual, conflict, redundancy, and reports. |
| `numeric_engine` | Equation assembly and manifold-aware nonlinear solving. |
| `session_runtime` | Commands, behavior modes, transactions, history, undo. |
| `io_adapters` | Versioned scene import/export and reproducible fixtures. |
| `viewer_bridge` | Read-only visualization and interaction bridge. |

The current C++ folder names may remain until the rewrite begins. These
architecture documents define the desired shape.
