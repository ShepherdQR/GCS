# GCS Architecture

This directory is the architectural source of truth for the next GCS rewrite.
It lives under `docs/architecture/` and is intentionally organized by reasoning
order, not by historical source order. Background research notes live under
`docs/research/`.

## Reading Order

1. `00-foundations/`
   - `problem-formulation.md`: the mathematical problem GCS solves.
   - `topos-semantic-model.md`: local-to-global semantics for decomposition,
     gluing, gauge, and diagnostic obstructions.
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
6. `50-implementation/`
   - `cpp23-module-solver-architecture.md`: C++23 module implementation
     layout, contracts, rollout order, and minimal gtest strategy.
   - `third-party-policy.md`: dependency governance, vendoring layout,
     binary/DLL rules, and GoogleTest integration policy.
7. Agentic detailed design overlay
   - `60-agentic-submodule-design-analysis.md`: current module maturity,
     detailed-design requirements, and missing module obligations.
   - `61-agentic-module-framework.md`: architecture-level agent/skill/tool
     framework and optimized implementation order.
   - `62-module-agents.md`: specialist module agents, skills, tools,
     guardrails, handoffs, and deep-design backlogs.
   - `63-target-contract-interface-implementation-test-design.md`: target
     C++23 module interfaces, implementation boundaries, and contract-test
     suites derived from the detailed design rather than current scaffolding.
   - `64-physical-agent-skill-catalog.md`: physical `.codex/skills` mapping
     for module-specific agent/skill operating procedures.
   - `65-agentic-implementation-tooling.md`: shared agent-callable scripts for
     validating module designs, skills, dependency boundaries, and scaffolding
     C++23 modules or contract tests.
   - `68-agentic-se-lifecycle-self-evolution.md`: full-lifecycle agentic
     software-engineering operating model, including task intake, planning,
     implementation, verification, review, CI, learning, and GCS
     self-evolution.
   - `69-ci-ready-quality-gates.md`: Step 18 quality-gate contract for local
     pre-push and CI execution.
   - `71-step-1-40-execution-report.md`: reporting-oriented summary of Step 1
     through Step 40 status, core deliverables, evidence, and next batch.
   - `79-step-41-46-execution-report.md`: reporting-oriented summary of Step
     41 through Step 50 showcase, scene behavior, history, replay-boundary,
     and saved-report workflow work.
   - `80-step-1-46-execution-overview.md`: combined Step 1 through Step 50
     briefing map and Figure 73 regeneration notes.
8. Visualization and aesthetic system
   - `70-visualization/gcs-architecture-atlas.md`: architecture diagrams and
     visual grammar for the target GCS shape.
   - `72-ui-aesthetic-roadmap.md`: phased visual refinement plan for the local
     Python viewer.
   - `73-gcs-visual-taste-guide.md`: canonical taste guide for GCS diagrams,
     reports, GUI surfaces, and showcase visuals.
   - `74-scientific-figure-production-paradigm.md`: target production pipeline
     for publication-quality, auto-laid-out, QA-checked project and research
     figures; full research notes are stored under
     `docs/research/20260524/scientific-figure-production-paradigm/`.
   - `75-ui-design-system-conventions.md`: named UI design system conventions
     for GCS taste, tokens, evidence grammar, figure production, visual QA, and
     art-direction review.
   - `76-ui-design-system-execution-plan.md`: phased execution plan and
     step-by-step commit/replanning protocol for implementing the GCS UI design
     system.
   - `92-gcs-ui-architecture-adjustment-record.md`: 2026-05-25 adjustment that
     reframes the local viewer target as a GCS Solver Evidence Workbench.
   - `94-repository-audit-statistics-architecture.md`: 2026-05-25 repository
     audit/statistics architecture for reproducible file, LOC, module,
     fixture, documentation, and evidence-growth reporting.
   - `95-gcs-narrative-map.md`: active narrative-line maturity map connecting
     solver evidence, product/user value, agentic-SE, governance, metrics, and
     external positioning.
   - `96-fixture-corpus-maturity-ladder.md`: active fixture corpus maturity
     ladder for smoke, verification, generated, milestone, counterexample,
     showcase, and benchmark-candidate scenes.
   - `97-external-solver-comparison-and-benchmark-plan.md`: researcher-facing
     comparison plan for SolveSpace, FreeCAD Sketcher, Siemens D-Cubed, and
     future GCS benchmark levels.
   - `98-benchmark-candidate-selection-criteria.md`: promotion criteria for
     moving scenes from observed examples to benchmark candidates and frozen
     benchmark fixtures.
   - `99-narrative-map-third-stage-development-plan.md`: seven-step plan and
     execution status for turning the researcher evidence route into an
     auditable research workbench narrative.
   - `benchmarks/b1-diagnostic-classification/`: first B1 expected-output
     files consumed by the D2 diagnostic classifier.
   - `benchmarks/external-baseline-feasibility-matrix.md`: current feasibility
     split between local executable, source/documentation, and commercial
     external baselines.
   - `benchmarks/b2-microbenchmark-candidate-review.md`: B1-to-B2 candidate
     decisions for the first research microbenchmark set.
9. `90-references/`
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
numeric engine, runtime, IO, and visualization. Its organizing semantic is
local-to-global: decomposition produces a cover of local contexts, numeric
engines propose local sections, assembly glues compatible sections into a
global state, and diagnostics explain obstructions when gluing fails. A solver
run should produce not only coordinates, but also a certificate-like report
that explains what was solved, what remains free, what is inconsistent, and how
reliable the result is.

The agentic design overlay turns this architecture into repeatable work:
each module owns strong structured inputs and outputs, typed tools, a core
agent, a core skill, guardrails, traces, and eval gates. The overlay is a
design and maintenance system; it is not a runtime dependency of the solver
core.

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

## Physical Repository Layout

The repository now uses the target vocabulary for its physical layout:

- `src/gcs/kernel`
- `src/gcs/constraint_catalog` when equation catalog work begins
- `src/gcs/incidence_graph`
- `src/gcs/decomposition_planner` when planner work begins
- `src/gcs/diagnostics`
- `src/gcs/numeric_engine`
- `src/gcs/session_runtime`
- `src/gcs/io_adapters`
- `python/gcs_viz` as the current viewer application
- `apps/gcs_cli` as the thin executable shell
- `fixtures/scene` as the scenario corpus seed

Some source files still contain prototype class and namespace names from the
old implementation. Treat those names as migration debt, not as architecture.

## Semantic Vocabulary

Topos theory informs the architecture through practical names:

| Term | Meaning |
| --- | --- |
| `ContextSnapshot` | Immutable local view of model state, variables, and constraints. |
| `CoverPlan` | Planner-selected family of contexts that covers a solve request. |
| `BoundaryProjection` | Restriction from a context to an overlap or shared boundary. |
| `LocalSection` | Numeric or construction proposal over one context. |
| `GluingReport` | Compatibility and assembly result for local sections. |
| `ObstructionReport` | Explanation for failed gluing, non-uniqueness, or singularity. |

These terms should shape contracts and reports. They do not require solver
modules to expose category-theory terminology in everyday APIs.
