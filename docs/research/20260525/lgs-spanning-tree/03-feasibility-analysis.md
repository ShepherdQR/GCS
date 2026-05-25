# Feasibility Analysis: LGS Spanning-Tree Modeling For GCS

Date: 2026-05-25

Scope: This feasibility report evaluates whether and how GCS should adopt the spanning-tree modeling method described in `docs/research/papers/LGS/ershov.pdf`.

## Bottom Line

The method is feasible for GCS as a staged, contract-first planner strategy. It is not feasible as an immediate drop-in numeric backend.

The safest adoption path is:

1. first implement tree-plan evidence and unsupported reports;
2. then add a very small pattern catalog;
3. only then introduce reduced relative-parameter numeric tasks.

The strongest reason to adopt the method is not raw speed alone. It gives GCS a concrete way to turn local-to-global planning into a smaller, more explainable numeric problem for rigid-set models with many pairwise constraints and cycles.

## Fit With Current GCS Architecture

GCS already has the right high-level slots:

- `incidence_graph` can produce structural facts and rigid-body graph projections.
- `decomposition_planner` already owns covers, subproblems, boundary projections, solve order, solve DAG, gauge policy, and unsupported reports.
- `numeric_engine` already exposes `NumericTask`, active variables/equations, boundary variables, residual reports, rank/condition reports, and iteration traces.
- `diagnostics` and `session_runtime` already have architecture-level responsibility for gluing, obstruction reports, and commit decisions.

This is a good architectural fit because the LGS method needs exactly those separations. It needs graph selection, parameterization, residual assembly, rank diagnostics, and final verification to remain distinct.

## Current Gaps

| Gap | Impact | Feasibility |
| --- | --- | --- |
| No explicit spanning-tree plan contracts | The method cannot be audited or tested yet | Easy to medium |
| Pattern catalog does not describe relative parameterization patterns | Cannot safely absorb constraints into tree edges | Medium |
| Kernel entity parameters are still generic and small | Full 3D rigid-transform semantics are not mature | Medium to hard |
| Numeric engine uses default manifold retraction and current residual assembly | Reduced transform-chain residuals are not implemented | Hard |
| Canonical-position rules are pattern-specific | Requires careful geometry design and tests | Hard |
| Naturality is not yet a first-class report concept | Solver may jump or choose poor initial reduced variables | Medium |
| Euler-angle-like parameterization can be singular/order-sensitive | Could cause fragile behavior | Hard unless quarantined |

## Feasibility Matrix

| Dimension | Rating | Reason |
| --- | --- | --- |
| Architecture compatibility | High | GCS local-to-global contracts match the method's needs. |
| Contract-only implementation | High | The planner can record maximum spanning forest evidence before numeric changes. |
| Small pattern catalog | Medium | Current constraint kinds are few, but safe canonical rules need design. |
| Full LGS-style 3D support | Low to medium | The paper relies on a mature 3D rigid-set solver and many patterns. |
| Performance improvement potential | Medium | Likely on cyclic rigid-set fixtures; unproven on current small fixture set. |
| Diagnostic clarity | High | The method naturally separates absorbed constraints from closure constraints. |
| Numeric risk | Medium to high | Reduced equations are smaller but more complex to evaluate and differentiate. |
| Maintenance cost | Medium | Pattern growth can become large unless versioned and tested. |

## Deep Technical Assessment

### Why The Method Is Attractive

The method gives the planner a principled way to reduce nonlinear problem size. Current GCS architecture already treats decomposition as cover selection and numeric solving as local section production. A spanning-tree parameterization can make a local section smaller by removing variables that tree-edge constraints already determine.

It also improves explainability. A solve report can say:

- these constraints were absorbed by pattern `P`;
- these constraints closed cycles and were solved numerically;
- this root/gauge choice fixed the component;
- these unsupported patterns prevented reduction.

That is very aligned with GCS's evidence-first design.

### Why It Is Not A Quick Win

The paper's method is built on mature LGS 3D assumptions:

- rigid sets are the main solve variables;
- transformations are first-class;
- a catalog of geometric patterns exists;
- canonical positions and special cases are known;
- residuals and gradients over transform chains are supported.

GCS has some of these concepts but not all of the implementation depth. The current planner mostly covers whole models or connected components. The current numeric task surface is rich enough to host the idea, but the actual reduced transform-chain solving is not present.

The correct first implementation is therefore not "make it faster." It is "make the plan explicit and testable."

### Core Correctness Risk

The biggest correctness risk is accidentally dropping constraints.

In the paper, a tree-edge constraint can be omitted from the residual system only because the parameterization guarantees it for all free variables. GCS must preserve that same invariant. If the pattern proof is missing, partial, directionally wrong, or numerically fragile, the constraint must remain a residual equation.

This calls for a conservative rule:

```text
unsupported pattern => closure residual or UnsupportedPlanReport
supported pattern + validated canonical transform => absorbed tree constraint
```

No other state should exist.

### Pattern-Catalog Risk

The paper implemented 6 single and 17 double patterns in LGS 3D. That number is small enough to be tractable but large enough to show the real work is in geometry semantics, not in maximum spanning tree selection.

For GCS, pattern definitions should live near `constraint_catalog`, because they depend on constraint meaning, entity signatures, residual dimension, generic DOF effect, degeneracy, and supported evaluator policy.

Do not bury pattern rules in `decomposition_planner`. The planner should choose among declared capabilities; it should not own geometric truth.

### Parameterization Risk

The paper uses rotations around axes. It also shows rotation-order and canonical-position problems. This is a warning that GCS should avoid making Euler-angle order a durable public contract.

A safer approach:

- keep public contract names abstract, such as `relative_transform_parameterization`;
- allow implementation to start with a simple finite-difference local coordinate chart;
- report chart singularity or unsupported canonical position explicitly;
- leave room for Lie-group or quaternion-based internals later.

### Naturality Risk

Naturality is not just aesthetic. It affects convergence because it determines the starting point for the reduced nonlinear system.

For GCS, naturality should become reportable:

- root rigid set chosen from fixed/anchored intent when possible;
- zero reduced variables correspond to the current sketch when tree constraints already hold;
- if not possible, report `planner.naturality_not_guaranteed`;
- diagnostics distinguish "mathematically valid but moved far" from "nearby natural solution."

### Diagnostic Risk

A reduced parameterization can make failures harder to explain if the system only reports reduced variables. GCS should keep both views:

- original entity and constraint IDs for user/reporting;
- reduced variable IDs for numeric evidence;
- mapping between tree-edge parameter blocks and rigid-set/entity subjects.

This preserves viewer and report compatibility.

## Recommended Feasibility Decision

Proceed, but only with phased gates.

### Adopt Now

Adopt these ideas immediately at design/report level:

- maximum-weight rigid-set spanning forest as a planner strategy;
- pattern-supported absorbed constraints;
- closure constraints as residual equations;
- explicit unsupported cases;
- naturality as a gauge/initialization concern.

### Defer

Defer these until contract tests exist:

- actual reduced nonlinear solving;
- analytic Jacobians for transform chains;
- broad pattern catalog;
- claims of performance improvement.

### Refuse For Now

Do not:

- replace existing residual solving with spanning-tree modeling globally;
- absorb constraints without pattern proof;
- use hidden fallback from reduced solve to full solve without a report;
- conflate LGS spanning-tree modeling with tree-decomposable constructibility.

## Minimal Viable Experiment

The smallest useful experiment is a planner-only contract suite:

1. Build a model with three rigid sets in a cycle.
2. Add constraints so two edges are pattern-supported and one edge closes a cycle.
3. Verify the planner chooses the two strongest tree edges.
4. Verify the closure constraint remains in the residual set.
5. Verify every active constraint appears exactly once in absorbed or closure evidence.
6. Verify unsupported patterns are reported before numeric solve.

This experiment can be done without new numeric solving and would immediately strengthen planner correctness.

## Success Metrics

For the first numeric prototype, measure:

- full variable dimension vs reduced variable dimension;
- full residual dimension vs closure residual dimension;
- number of absorbed constraints with pattern proof;
- maximum closure residual after solve;
- maximum revalidated absorbed-constraint residual after solve;
- rank/nullity in full and reduced views;
- solve iterations and time;
- unsupported-case rate;
- number of diagnostic reports with stable subject IDs.

The method should graduate only if it improves at least dimensionality and diagnostic clarity first. Speed can be a later criterion after correctness is stable.

## Risk Register

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Constraint accidentally omitted | High | Exhaustive absorbed/closure partition tests; post-solve revalidation. |
| Unsupported pattern silently approximated | High | Structured `UnsupportedPlanReport`; no hidden fallback. |
| Canonical transform wrong for child orientation | High | Direction-sensitive pattern tests and report subjects. |
| Euler-angle singularity/order sensitivity | Medium to high | Abstract public parameterization contract; singularity reports; future Lie-group internals. |
| Pattern catalog grows chaotically | Medium | Versioned catalog entries, fixtures per pattern, finite-difference checks. |
| Reduced residuals become hard to debug | Medium | Preserve mapping from reduced variables to rigid sets, entities, and constraints. |
| Performance gains do not appear on current fixtures | Medium | Treat first win as correctness/evidence; build industrial-style fixture corpus later. |
| User-facing solution becomes less natural | Medium | Natural initial values, root/gauge policy, movement-distance reports. |

## Final Recommendation

The method is worth adopting as a GCS planner capability because it turns a known LGS industrial optimization into explicit local-to-global contracts. It fits the target architecture better than it would fit a monolithic solver.

The next concrete step should be contract-only: add a rigid-set spanning-tree plan and tests that prove deterministic tree selection, absorbed/closure constraint partitioning, and unsupported-case reporting. Only after that should GCS attempt reduced transform-chain numeric solving.
