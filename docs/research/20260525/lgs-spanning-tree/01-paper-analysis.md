# LGS Spanning-Tree Modeling Paper Analysis

Date: 2026-05-25

Scope: This report analyzes `docs/research/papers/LGS/ershov.pdf`, the 2007 paper "Spanning-tree modeling method for geometric constraint satisfaction problem" by Alexey Ershov, Alexey Kiselev, and Eugene Rukoleev. It focuses on the spanning-tree method used in LGS 3D and its relevance to GCS local-to-global solving.

## Executive Summary

The paper proposes a hybrid between history-based CAD modeling and variational constraint solving. Its key move is to choose a spanning tree over rigid-set constraints, absorb those tree-edge constraints into relative transformation parameterizations, and leave only the non-tree cycle-closure constraints as nonlinear equations.

The method is not just graph decomposition. It is a variable-reduction and equation-reduction technique for 3D rigid-set solving. Tree constraints become constructive relative coordinates; closure constraints remain variational equations.

The core optimization is a maximum-weight spanning tree over a rigid-body constraint graph. Edge weights represent how many degrees of freedom a matched constraint pattern removes. The chosen tree maximizes the amount of constraint satisfaction handled by parameterization instead of residual equations.

LGS 3D makes this practical through a finite catalog of spanning-tree patterns and canonical positions. Patterns state which relative transformation variables are fixed by a constraint or small set of constraints. Canonical positions and naturality rules choose constant transforms so zero free variables correspond to a solution close to the original sketch.

The reported performance gain is substantial in the paper's test base: reduced average variables/equations, lower total solve time, and better success rates. The authors also warn, indirectly but clearly, that the method depends on pattern coverage, parameterization choices, rotation order, and canonical-position existence.

For GCS, the paper should be treated as a planner/numeric parameterization strategy, not as a replacement for diagnostics, gluing, or generic residual solving.

## Source Register

| Source | Used For | Confidence |
| --- | --- | --- |
| `docs/research/papers/LGS/ershov.pdf`, pp. 75-89 | Primary paper: method, formulas, pattern examples, results | High |
| `docs/architecture/README.md` | Target GCS module vocabulary and local-to-global thesis | High |
| `docs/architecture/20-solver-pipeline/decomposition-planning.md` | Planner ownership of covers, boundaries, solve DAG, unsupported plans | High |
| `docs/architecture/30-contracts/solver-contracts.md` | Planner, numeric, gluing, runtime contract boundaries | High |
| `docs/architecture/90-references/lgs.md` | Existing project interpretation of LGS decomposition-plus-specialization | Medium |
| `src/gcs/decomposition_planner/decomposition_planner.cppm` | Current planner output surface | High |
| `src/gcs/incidence_graph/incidence_graph.cppm` | Current rigid-body graph and incidence surfaces | High |
| `src/gcs/numeric_engine/numeric_engine.cppm` | Current numeric task/report surface | High |

## Paper Context

The paper starts from a CAD modeling tension:

- History-based parametric modeling is simple and naturally tree-structured, but it cannot handle cyclic dependencies well and struggles with underdefined models.
- Variational modeling is expressive and lets users add or remove constraints freely, but it requires solving a nonlinear system after edits and can become slow.

The authors position spanning-tree modeling as a way to keep the expressive power of variational constraints while recovering some efficiency and naturality from hierarchical modeling. LGS 2D and LGS 3D already solved variational design problems, but some industrial models exposed performance problems; the spanning-tree method was introduced into LGS 3D to reduce those costs.

The paper is explicitly about 3D rigid-set solving. Instead of solving directly for all primitive object coordinates, LGS 3D represents complex 3D objects as rigid sets and solves for transformations of those rigid sets.

## Mathematical Core

### Rigid-Set Transform Variables

LGS 3D models a rigid-set movement as a rotation plus translation:

```text
X_new = R * X_old + T
```

The paper represents rotation as a composition of rotations around coordinate axes, with variables `alpha`, `beta`, and `gamma`, and translation as `Tx`, `Ty`, and `Tz`. This yields six variables per free rigid-set transform.

For spanning-tree modeling, the child rigid set is not parameterized independently. It is parameterized relative to a parent rigid set:

```text
T_child = T_parent o L o P(alpha, beta, gamma, Tx, Ty, Tz) o F
```

`P` is the variable relative transform. `L` and `F` are constant transforms chosen through canonical-position and naturality rules.

### Tree Edges As Constraint-Satisfying Parameterizations

The main idea is that a constraint between two rigid sets often removes some of the six relative degrees of freedom. If the parent-child edge has a known pattern, GCS does not need all six variables for the child. Some variables can be fixed by construction, and the corresponding constraints do not need residual equations.

Example from the paper: a plane parallelism constraint between two parts leaves one rotational and three translational degrees of freedom. The relative transform can therefore use only four variables instead of six. A plane-plane distance example can reduce to three variables, such as `alpha`, `Ty`, and `Tz`.

The paper's crucial property is bidirectional: for a supported pattern, all free-variable values satisfy the tree constraint, and every allowed relative placement can be represented by some assignment of the free variables.

### Maximum-Weight Spanning Tree

The algorithm builds a multigraph:

- vertices are rigid sets;
- edges are constraints between objects belonging to different rigid sets;
- edge weights encode removed degrees of freedom;
- multiple constraints between the same rigid-set pair are pattern-matched as a group.

After pattern matching, the multigraph is compressed into a weighted graph. A maximum-weight spanning tree is selected. The tree is "maximum" because larger weight means more DOF removed, fewer free variables, and fewer generated equations.

Tree-edge constraints are automatically satisfied by relative parameterization. Non-tree constraints are not ignored. They become cycle-closure equations and are solved numerically.

This is the important completeness claim at the modeling level: all constraints are still represented. The tree constraints are represented constructively; cycle closures are represented as residual equations.

### Pattern Catalog

The paper uses predefined spanning-tree patterns. Each pattern:

- matches one or more constraints between two rigid sets;
- identifies which relative transformation variables can be fixed;
- has a weight equal to the sum of removed degrees of freedom;
- provides enough canonical-position rules to generate parametric transforms.

The paper reports 6 single patterns and 17 double patterns implemented in LGS 3D at the time. Single examples include point coincidence, line coincidence, plane-plane distance, parallelism, point-line coincidence when the child is a point, and sphere coincidence. Double examples include pairs of line-line coincidences, pairs of plane-plane distances, and combinations such as line coincidence plus plane distance.

Pattern coverage is finite and engineering-driven. The paper says several dozen powerful and generic patterns were enough in practice, not that the catalog is universal.

### Canonical Positions

Canonical positions are how LGS turns a geometric relation into fixed variables. A constrained object is moved into a standard frame, often with a canonical direction vector and anchor point. Then the remaining allowed transformations have a simple variable form.

For a plane-plane distance constraint, the parent and child planes are placed in canonical positions separated by the desired distance. The remaining valid child transforms become rotations and translations that preserve the distance.

The constant transforms `F` and `L` move the child into and out of this canonical frame. They are chosen not only for correctness but also for naturality.

### Naturality

Naturality means the final placement should remain close to the sketch or initial configuration when possible. The paper uses this to choose among many possible `L` and `F` transforms.

The practical payoff is twofold:

- If the tree constraints are already satisfied in the initial state, zero free variables should keep the objects unmoved.
- The nonlinear solver receives better starting points because tree-edge satisfaction is already embedded in the initial parameterization.

This maps strongly to current GCS concerns about preserving user intent, avoiding surprising jumps, and exposing gauge choices explicitly.

### Reduced Equation Generation

After the tree and pattern parameterizations are selected, LGS generates equations only for remaining constraints. These equations are evaluated on parametric transformations, not directly on independent object coordinates.

The paper notes a tradeoff:

- each remaining equation can be more expensive to evaluate because it may require transformations along a tree path;
- the overall system is smaller, and the nonlinear solve is dominated by cubic linear-system costs, so reducing variables/equations is beneficial;
- transformations and partial derivatives can be computed efficiently by processing tree vertices from root to leaves.

## Experimental Evidence

The paper reports tests over 3120 cases, with 14 large industrial-style cases.

Compared with 6-variable Cartesian modeling:

| Test group | Method | Avg. variables | Avg. equations | Total time sec | Success rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Main base | 6-variable Cartesian | 8.48 | 7.12 | 695.05 | 95.10% |
| Big cases | 6-variable Cartesian | 29.57 | 37.25 | 242.02 | 71.43% |
| Main base | Spanning-tree | 5.46 | 3.04 | 187.13 | 97.52% |
| Big cases | Spanning-tree | 16.46 | 18.25 | 115.12 | 78.57% |

After plugging spanning-tree modeling into the full LGS solver:

| Test group | Before/after | Total time sec | Success rate |
| --- | --- | ---: | ---: |
| Main base | Before | 77.90 | 98.55% |
| Big cases | Before | 478.18 | 85.71% |
| Main base | After | 52.78 | 99.16% |
| Big cases | After | 235.98 | 92.85% |

The paper is careful that LGS also uses other decomposition, simplification, and nonlinear acceleration methods. So the result should be read as strong practical evidence, not a clean isolated theorem that spanning-tree modeling alone guarantees those gains in every solver.

## Limitations And Hidden Complexity

### Pattern Coverage

The method depends on a pattern catalog. Unsupported constraint combinations cannot safely be absorbed into tree parameterizations. They must remain residual equations or produce an unsupported report.

### Canonical-Position Failure

The paper gives counterexamples where a suitable canonical position does not exist for the chosen parameterization. Point-line incidence with the line as child is one example. The authors suggest changing the parameterization or using an alternate transform form.

### Rotation-Order Sensitivity

For line-plane distance, the order of rotations can break the desired invariant unless canonical axes are chosen carefully. This is a warning against naive Euler-angle parameterization in GCS.

### Directionality

Some patterns are child-direction sensitive. A pattern may work when the child is a point but not when the child is a line or plane. Therefore the planner must choose oriented tree edges, not just undirected graph edges.

### Numerics Still Matter

The method does not eliminate nonlinear solving. It reduces the residual system by construction, then solves the remaining cycle constraints. Rank, conditioning, convergence, and gluing diagnostics remain necessary.

## Distinction From Other Tree Methods

This paper's spanning tree should not be confused with tree-decomposable graph theory or SPQR/tree decompositions:

- Tree-decomposable methods recursively break a constraint graph into constructible clusters.
- The LGS spanning-tree method chooses a tree over rigid-set relationships for relative parameterization.
- The tree is not a proof that the whole model is constructible.
- Non-tree constraints are precisely where residual equations and cycle consistency live.

This distinction matters for GCS because the architecture already separates incidence structure, decomposition planning, numeric solving, diagnostics, and gluing. The LGS method belongs at the boundary between planning and numeric parameterization.

## Implications For GCS

The paper supports a GCS strategy named something like `rigid_set_spanning_tree_parameterization`, but only under explicit contracts:

- the incidence layer must expose a deterministic rigid-body graph grouped by rigid-set pairs;
- the constraint catalog must own pattern semantics, DOF effects, and unsupported cases;
- the decomposition planner must choose the tree, orient edges, prove coverage, and name closure constraints;
- the numeric engine must solve reduced residual equations over free relative parameters;
- diagnostics must re-check all constraints and report tree-pattern failures, closure residuals, and rank evidence separately;
- the runtime must commit only after global verification.

The best reading is: spanning-tree modeling can be a powerful planner-selected parameterization for supported rigid-set subproblems. It should not become hidden solver policy.
