# Proposal: Use LGS Spanning-Tree Modeling In GCS

Date: 2026-05-25

Scope: This proposal maps the LGS spanning-tree modeling method from `docs/research/papers/LGS/ershov.pdf` into the current GCS architecture. It is a plan proposal, not an implementation record.

## Thesis

Adopt the LGS spanning-tree method as an optional decomposition-planner strategy for rigid-set subproblems:

```text
rigid-set graph
  -> pattern match rigid-set pair constraints
  -> maximum-weight spanning tree
  -> relative parameterization plan
  -> closure residual numeric task
  -> diagnostics verify all constraints
```

The method should not bypass GCS local-to-global contracts. It should produce ordinary project vocabulary: `CoverPlan`, `BoundaryProjection`, `SolveDag`, `GaugePolicy`, numeric reports, and obstruction reports.

## Architecture Placement

| Module | New responsibility |
| --- | --- |
| `incidence_graph` | Build deterministic rigid-set pair graph and group constraints by rigid-set pair. |
| `constraint_catalog` | Declare which constraint patterns can be absorbed by relative parameterization. |
| `decomposition_planner` | Choose the maximum-weight spanning tree, orient it, name tree-edge contexts, closure constraints, and unsupported cases. |
| `numeric_engine` | Assemble reduced residual equations over relative free parameters rather than over all entity coordinates. |
| `diagnostics` | Revalidate excluded tree constraints, closure residuals, rank evidence, and naturality/gauge consistency. |
| `session_runtime` | Commit only after numeric and diagnostic acceptance; expose tree-plan evidence in stage reports. |

The strategy depends on `kernel`, `incidence_graph`, `constraint_catalog`, and selected diagnostic hints. It must not import UI, IO, viewer, CLI, or app lifecycle code.

## Proposed Public Vocabulary

These names are design candidates for later implementation:

```cpp
struct SpanningTreePattern {
    PatternId id;
    std::vector<ConstraintKind> constraint_kinds;
    std::vector<GeometryKind> child_roles;
    int removed_rotational_dof;
    int removed_translational_dof;
    bool orientation_sensitive;
    bool canonical_position_required;
};

struct RigidSetPairPatternMatch {
    RigidSetId parent_candidate;
    RigidSetId child_candidate;
    std::vector<ConstraintId> absorbed_constraint_ids;
    std::vector<ConstraintId> closure_constraint_ids;
    PatternId pattern_id;
    int weight;
    bool supported;
    std::string unsupported_code;
};

struct RigidSetSpanningTreePlan {
    std::vector<RigidSetId> nodes;
    std::vector<RigidSetTreeEdge> tree_edges;
    std::vector<ConstraintId> closure_constraint_ids;
    std::vector<ConstraintId> absorbed_constraint_ids;
    StageReport pattern_report;
};
```

These do not need to be the final type names. The invariant is more important: the planner must explicitly name absorbed constraints and closure constraints.

## Planner Flow

1. Build a rigid-set graph from `IncidenceIndices` and `RigidBodyGraph`.
2. Group all constraints by unordered rigid-set pair.
3. For each pair, ask the constraint catalog for the strongest supported pattern.
4. Create weighted candidate edges where weight equals removed DOF.
5. Choose a deterministic maximum-weight spanning forest over the requested solve scope.
6. Orient each tree from a root rigid set selected by `GaugePolicy`.
7. Emit:
   - tree-edge contexts;
   - closure context for non-tree constraints;
   - `BoundaryProjection` records from child to parent/root/closure contexts;
   - `SolveDag` edges from parent-dependent parameterizations to closure solve;
   - `UnsupportedPlanReport` if no safe pattern set exists.

For disconnected rigid-set graphs, the output should be a forest. Each component needs its own gauge/root policy.

## Numeric Flow

The numeric engine receives a reduced task:

- active variables: free relative parameters on tree edges plus any root/gauge variables left by policy;
- active equations: closure constraints and any unsupported constraints that must remain residualized;
- excluded equations: tree-edge constraints with pattern proof;
- parameterization: `rigid-set-relative-spanning-tree-v1`;
- boundary variables: fixed entities or rigid sets from solve intent.

Residual and Jacobian evaluation must be explicit about this transform chain:

```text
root rigid-set state
  -> child relative transform
  -> descendant transform composition
  -> primitive object positions
  -> constraint residuals
```

The first implementation can use finite differences for reduced parameters. Analytic Jacobians should be a later optimization.

## Diagnostics Flow

Diagnostics should treat the spanning-tree plan as evidence, not as a proof by itself.

Required diagnostic checks:

- every absorbed tree constraint is named and pattern-supported;
- every non-tree constraint appears in the closure residual set;
- no active constraint disappears from both sets;
- rank evidence reports reduced free dimension and original full dimension separately;
- tree-edge constraints are re-evaluated after solve for tolerance compliance;
- closure residuals are reported per constraint;
- unsupported canonical-position or pattern cases return `unsupported`, not silent fallback;
- gauge/root choices are explicit and stable.

## Implementation Phases

### Phase 0: Research Artifact

Deliverables:

- paper analysis report;
- GCS adoption proposal;
- feasibility analysis.

Status: this folder is the phase-0 artifact.

### Phase 1: Contract-Only Planner Extension

Goal: represent the method without changing numeric solving.

Work:

- add rigid-set pair grouping to `incidence_graph` or expose it through existing `RigidBodyGraph`;
- add contract structs for pattern matches and spanning-tree plans;
- add deterministic maximum-weight spanning forest builder;
- add planner output evidence that names absorbed and closure constraints;
- return `unsupported` unless all required parameterization details are available.

Tests:

- deterministic edge grouping;
- maximum-weight tree tie-breaking;
- every constraint is either absorbed or closure;
- disconnected graphs produce a forest;
- unsupported pattern returns structured report.

### Phase 2: Pattern Catalog V0

Goal: support a deliberately small set of safe patterns.

Candidate v0 patterns should be chosen from the current GCS constraint and geometry vocabulary:

- `distance` between supported point/plane-like roles if a robust canonical transform exists;
- `parallel` for supported line/plane roles;
- `coincident` for supported point/line/plane pairs where child direction is safe.

The exact v0 set should be smaller than the paper's LGS catalog. Start with patterns that can be tested against simple fixtures and have no ambiguous canonical-position branch.

Tests:

- pattern signatures reject wrong arity and geometry kinds;
- same-rigid-set constraints do not become tree edges;
- child-direction-sensitive patterns produce deterministic orientation;
- unsupported canonical position is surfaced.

### Phase 3: Reduced Numeric Task Prototype

Goal: assemble and solve a reduced residual system.

Work:

- introduce a transform-chain evaluator for rigid-set relative parameters;
- map reduced variables to descendant primitive object positions;
- assemble residuals for closure constraints through `constraint_catalog`;
- finite-difference Jacobian over reduced parameters;
- include full/free/frozen dimensions in `RankConditionReport`.

Tests:

- simple two-rigid-set tree edge has fewer variables than Cartesian baseline;
- triangle/cycle fixture keeps non-tree closure constraint residualized;
- absorbed constraints revalidate after solve;
- boundary variables remain frozen.

### Phase 4: Naturality And Gauge Policy

Goal: make initial guesses and gauge behavior user-respectful.

Work:

- choose root rigid sets deterministically, preferably from fixed or anchored solve intent;
- set zero relative variables to mean "stay close to current sketch" when tree constraints are already satisfied;
- report when naturality cannot be guaranteed;
- add gauge consistency checks.

Tests:

- initially satisfied tree constraints produce zero-change initial reduced state;
- root choice is deterministic;
- fixed entities propagate into boundary variables;
- gauge policy is explicit in reports.

### Phase 5: Empirical Gate

Goal: decide whether the method earns a production path.

Work:

- create a fixture corpus with chain, cycle, disconnected, over-constrained, under-constrained, and unsupported cases;
- compare variable count, residual dimension, iterations, solve time, success status, and diagnostic quality;
- keep the existing numeric path as fallback with an explicit reason.

Exit criteria:

- reduced task consistently lowers variable/residual dimensions on supported fixtures;
- all constraints are verified after solve;
- unsupported fixtures are typed and deterministic;
- no lower module imports boundary modules;
- `ctest` contract suites pass.

## Acceptance Gates

1. No constraint may vanish. Each active constraint is absorbed with pattern evidence or remains a residual equation.
2. Absorbed constraints require a named, supported pattern.
3. Tree orientation and tie-breaking must be deterministic.
4. Root and gauge choices must be explicit.
5. Reduced numeric reports must preserve original full dimension, reduced free dimension, frozen dimension, residual dimension, rank, and condition evidence when valid.
6. Diagnostics must re-check tree constraints and closure constraints after solve.
7. Unsupported cases must be reported before numeric solving, not discovered as mysterious numeric failure.

## Non-Goals

- Do not implement the full LGS 3D pattern catalog immediately.
- Do not expose Euler-angle implementation details as permanent public API.
- Do not replace graph decomposition, SPQR-style planning, or diagnostics with this method.
- Do not claim the spanning tree proves global constructibility.
- Do not commit state from a reduced solve without ordinary runtime diagnostics and gluing verification.

## Recommended Next Task Card

Create a contract-only task:

```text
Title: Rigid-set spanning-tree plan contracts

Goal:
Add deterministic planner-side evidence for a rigid-set maximum-weight spanning
forest, including pattern matches, absorbed constraints, closure constraints,
and unsupported reports. Do not change numeric solving yet.

Affected modules:
incidence_graph, decomposition_planner, constraint_catalog, contract tests.

Definition of done:
Contract tests prove deterministic tree selection, no dropped constraints,
structured unsupported reports, and unchanged current component-cover behavior.
```
