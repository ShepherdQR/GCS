# Agentic Submodule Design Analysis

Research snapshot: 2026-05-23.

## Purpose

This report audits whether the current GCS rewrite modules have detailed
designs that are strong enough for the next implementation phase. It also
records the AI-era design obligations we will use for every module:
structured inputs, structured outputs, module-owned tools, module-owned
agents, module-owned skills, guardrails, traces, and eval gates.

The conclusion is clear: the current architecture has a strong topological
shape and a useful C++23 module skeleton, but most modules are still at
contract-skeleton maturity. The next design step is to make each module
machine-checkable: public C++ structs first, optional JSON/schema at IO
boundaries, deterministic tools, typed reports, and module-specific agents
that can produce testable design and implementation plans.

## Research Basis

- [OpenAI Agents SDK agents](https://openai.github.io/openai-agents-python/agents/)
  defines agents around instructions, tools, handoffs, guardrails, lifecycle
  hooks, and structured outputs.
- [OpenAI Agents SDK tools](https://openai.github.io/openai-agents-python/tools/)
  treats tools as explicit action surfaces, including local runtime tools and
  agents-as-tools.
- [OpenAI Agents SDK guardrails](https://openai.github.io/openai-agents-python/guardrails/)
  separates input, output, and tool guardrails, which maps directly to GCS
  contract validation.
- [OpenAI Agents SDK tracing](https://openai.github.io/openai-agents-python/tracing/)
  makes tool calls, handoffs, guardrails, and custom events observable.
- [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
  motivates strict schema-adherent outputs. In GCS, the primary schema is the
  exported C++23 contract type; JSON Schema is a boundary representation.
- [MCP tools](https://modelcontextprotocol.io/specification/draft/server/tools)
  formalizes tool input and output schemas, structured tool content, explicit
  errors, and explicit handles for stateful workflows.
- [MCP resources](https://modelcontextprotocol.io/specification/draft/server/resources)
  models durable context as addressable resources, which maps to architecture
  docs, fixtures, reports, and traces.
- [MCP prompts](https://modelcontextprotocol.io/specification/draft/server/prompts)
  treats reusable prompts as structured, user-selectable workflows. GCS skills
  should serve that role for repeatable module work.
- [Anthropic effective agents](https://www.anthropic.com/engineering/building-effective-agents)
  recommends starting with the simplest workable workflow and increasing
  agentic complexity only where it pays for itself.
- [Anthropic agent evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
  emphasizes task suites, stable environments, traces, and error analysis for
  multi-turn tool-using agents.

## Detailed Design Standard

Each GCS module is considered detailed only when it has all of the following:

1. Mission, non-goals, ownership boundary, and dependency direction.
2. Strong structured input contracts with version, identity, tolerance, and
   precondition fields where relevant.
3. Strong structured output contracts with status, evidence, typed diagnostics,
   stable IDs, state versions, and no prose-only failures.
4. Status and error taxonomy, including precedence when multiple failures are
   present.
5. Public deterministic tools, each with typed input, typed output, explicit
   side-effect policy, and test fixtures.
6. A core module agent with instructions, owned decisions, refused decisions,
   guardrails, handoffs, trace obligations, and acceptance gates.
7. A module skill definition that tells future Codex runs when to use the
   module agent, what resources to read, what checks to run, and what outputs
   to produce.
8. Evals and tests that assert contracts rather than implementation internals.
9. Trace and replay artifacts that make important decisions inspectable.
10. Evolution policy for schema migration, compatibility, and third-party
    dependencies if the module touches boundaries.

## Maturity Scale

| Level | Meaning |
| --- | --- |
| L0 | Module name exists but no real contract. |
| L1 | C++23 module skeleton and basic structs exist. |
| L2 | Structured inputs and outputs exist for the main path. |
| L3 | Full detailed design exists: tools, agent, skill, guardrails, tests, traces. |
| L4 | Implementation and tests satisfy the detailed design. |

## Current Maturity Summary

| Module | Current maturity | Reason |
| --- | --- | --- |
| `kernel` | L2 | Durable structs exist, but validation, report taxonomy, ID policy, and deltas are incomplete. |
| `constraint_catalog` | L1-L2 | Validation metadata exists, but residual/Jacobian/provider contracts are missing. |
| `incidence_graph` | L1-L2 | Entity incidence and components exist, but the hypergraph and structural indices are incomplete. |
| `decomposition_planner` | L1 | A cover skeleton exists, but overlaps, boundaries, gauge, DAG, and fallback policy are placeholders. |
| `numeric_engine` | L1 | `NumericTask` and `NumericReport` exist, but solving is an identity local-section placeholder. |
| `diagnostics` | L1-L2 | DOF and gluing reports exist, but conflict, redundancy, status precedence, and projection-aware gluing are missing. |
| `session_runtime` | L2 | The command pipeline exists, but transaction isolation, replay, undo, and dependency injection are missing. |
| `io_adapters` | L1 | Text loading and summaries exist, but schema registry, JSON, migration, and typed parse errors are absent. |
| `viewer_bridge` | L1 | Read-only summary exists, but projection, overlay, interaction draft, and history contracts are absent. |
| `tools` | L1 | Sample model builders exist, but tool contracts, provenance, fixture generation, and audits are missing. |
| `tests / quality` | L1 | GTest smoke tests exist, but negative corpus, IO round-trips, numeric robustness, and dependency gates are missing. |
| `third_party` | L2 | Policy exists, but registry metadata, adapters, license/SBOM gates, and version reconciliation are incomplete. |

## Cross-Module Findings

- The architecture already separates mathematical truth from IO, UI, and app
  lifecycle. That boundary should not move.
- Every module needs a typed `Input`, `Output`, `Report`, and `Failure` surface.
  Free-form strings are acceptable only as human-readable supplements.
- The topos-inspired vocabulary is useful when it names contracts:
  `ContextSnapshot`, `CoverPlan`, `BoundaryProjection`, `LocalSection`,
  `GluingReport`, and `ObstructionReport`.
- The solver needs a report taxonomy before the implementation gets deeper.
  Otherwise diagnostics, runtime, viewer, CLI, and tests will drift.
- Agentic design should be a maintenance and design overlay, not a runtime
  dependency of the solver core.
- Manager-style orchestration is the default: the architecture steward or
  session runtime agent calls specialist module agents as tools. Handoffs are
  reserved for work that a specialist fully owns.
- Structured outputs in GCS mean exported C++23 contract structs first. JSON
  schemas should be generated or mirrored only at IO, tool, trace, and agent
  boundaries.

## Kernel

Current design: `kernel` owns stable IDs, immutable snapshots, model state,
contexts, boundaries, policies, local sections, proposed states, and reports.
It is the correct lowest layer.

Required detailed design additions:

- Formal `ModelValidationInput` and `ModelValidationReport`.
- ID allocator and duplicate-ID validation policy.
- Typed `ParameterBlock` schema or dimensional wrappers.
- Explicit `StateDelta` and state-version transition contract.
- Context coverage and membership validator.
- Report-code registry with stable machine codes.
- Snapshot diff and canonical equality tools.

Immediate acceptance gates:

- Duplicate IDs, missing IDs, invalid context membership, and invalid parameter
  dimensions fail with typed reports.
- Lower modules do not import higher modules.
- Every report references a base `StateVersionId` when state is involved.

## Constraint Catalog

Current design: `constraint_catalog` centralizes constraint definitions,
validation, arity, generic DOF, and residual dimension metadata.

Required detailed design additions:

- Residual evaluator and Jacobian provider contracts.
- Entity signature model beyond generic arity.
- Constraint parameter schemas instead of a single `double`.
- Degeneracy report contract.
- Catalog versioning and compatibility policy.
- Finite-difference checker and residual/Jacobian conformance tests.

Immediate acceptance gates:

- Each constraint kind declares arity, entity signatures, parameter schema,
  residual dimension, generic DOF effect, degeneracy cases, and evaluator
  availability.
- Invalid references and same-rigid-set errors are typed and stable.

## Incidence Graph

Current design: `incidence_graph` builds entity incidence and connected
components from a snapshot.

Required detailed design additions:

- First-class entity-constraint hypergraph.
- Constraint reverse index.
- Rigid-set/body graph.
- Articulation, biconnected, and separator reports.
- Malformed-edge quarantine strategy.
- Deterministic graph dump for debugging and tests.

Immediate acceptance gates:

- Components cover every entity exactly once.
- Missing entity references produce typed errors.
- Planner consumes only public `IncidenceIndices` and structural reports.

## Decomposition Planner

Current design: `decomposition_planner` emits a basic cover, subproblems,
solve steps, and gauge policy.

Required detailed design additions:

- Coverage verifier.
- Overlap and `BoundaryProjection` builder.
- Explicit gauge selector.
- Solve DAG with cycle checks.
- Fallback/unsupported strategy.
- Rigidity, separator, and rank-aware planning inputs.

Immediate acceptance gates:

- Every planned solve covers requested entities and constraints.
- Shared variables are represented through overlap contexts and boundary
  projections.
- Unsupported decomposition returns a structured `Unsupported` report.

## Numeric Engine

Current design: `numeric_engine` accepts `NumericTask` and returns
`NumericReport`, but the implementation is an identity local-section producer.

Required detailed design additions:

- `initial_state`, scaling, parameterization, Jacobian policy, and linear
  solver policy fields.
- Constraint residual assembler.
- Analytic and finite-difference Jacobian paths.
- Rank and conditioning estimator.
- Manifold retraction/update abstraction.
- Per-constraint residuals and largest-update reports.
- Iteration trace schema.

Immediate acceptance gates:

- A task with missing IDs fails before iteration.
- A successful report names context, base state version, residuals, rank,
  condition estimate, iteration count, and convergence reason.
- Numeric output is a proposal, never a durable commit.

## Diagnostics

Current design: `diagnostics` provides DOF reports, rank placeholders, residual
reports, obstruction reports, and local-section gluing.

Required detailed design additions:

- Explicit diagnostic phases: pre-solve, post-local-solve, gluing,
  verification.
- Status precedence matrix.
- Conflict and redundancy set contracts.
- Boundary projection comparator.
- Gauge consistency checker.
- Obstruction minimization strategy.
- Residual recomputation per constraint.

Immediate acceptance gates:

- Failed gluing always returns an `ObstructionReport`.
- Structural DOF and numeric rank evidence remain separate.
- Reports contain stable IDs, not only text.

## Session Runtime

Current design: `session_runtime` owns command orchestration and state-version
commit.

Required detailed design additions:

- Command preconditions and transaction policy.
- Atomic snapshot/journal and rollback report.
- Dependency injection for planner, numeric, diagnostics, IO, and viewer
  adapters.
- Command trace and replay artifact.
- Undo/redo history event model.
- Post-commit verification stage.
- No pre-acceptance mutation of durable runtime state.

Immediate acceptance gates:

- Rejected commands preserve previous durable geometry and state version.
- Numeric success is insufficient without accepted diagnostics and gluing.
- Every stage appends a structured report.

## IO Adapters

Current design: `io_adapters` can load a simple text scene and summarize a
snapshot.

Required detailed design additions:

- Scene schema registry with explicit version.
- JSON/text canonical serializer.
- Migration runner and migration report.
- Typed parse, validation, and compatibility errors.
- Round-trip diff and canonical digest tools.
- Fixture linter and corpus loader.

Immediate acceptance gates:

- Load-write-load equality for canonical fixtures.
- Deterministic byte output.
- No lower solver module imports IO.

## Viewer Bridge

Current design: `viewer_bridge` produces snapshot and command summaries.

Required detailed design additions:

- `ViewerProjectionRequest`.
- `ViewerSceneProjection` with stable IDs and state version.
- `DiagnosticOverlay`.
- `InteractionCommandDraft`.
- `HistoryFrameProjection`.
- Selection/hit-test mapping tools.

Immediate acceptance gates:

- Projection is deterministic for identical snapshot and reports.
- UI edits become runtime commands.
- Viewer never owns durable solver truth.

## Contract Tools

Current design: `gcs.contract_tools` builds minimal deterministic sample
snapshots.

Required detailed design additions:

- `FixtureBuildRequest`.
- `InvariantCheckRequest`.
- `CorpusGenerationRequest`.
- `DependencyAuditRequest`.
- Fixture provenance metadata.
- Golden report writer.
- Module dependency scanner.
- A long-term move to a separate support/test target.

Immediate acceptance gates:

- Generated snapshots validate through public contracts.
- Tools are deterministic under fixed seeds.
- Production solver policy does not live in test utilities.

## Tests And Quality

Current design: GTest smoke tests exercise the basic contract pipeline.

Required detailed design additions:

- Negative and obstruction corpus.
- IO round-trip tests.
- Viewer projection tests.
- Numeric robustness and tolerance oracle.
- Module dependency gate.
- Clang/Ninja/C++23 module CI matrix.
- Report-level regression artifacts.

Immediate acceptance gates:

- Build and `ctest` pass on supported presets.
- Failure fixtures produce typed obstruction reports.
- Tests assert public contracts, not private implementation details.

## Third-Party Governance

Current design: `third-party-policy.md` defines dependency preference order,
GoogleTest strategy, and binary/DLL rules.

Required detailed design additions:

- Third-party metadata registry.
- `ThirdPartyRequest` and `ThirdPartyDecision` records.
- CMake adapter targets under a dedicated adapter layer.
- License and SBOM audit gate.
- Version reconciliation for installed GTest 1.17.0 versus opt-in fallback
  tags.
- Offline configure test.

Immediate acceptance gates:

- Test-only dependencies do not link into production targets.
- Installed packages are preferred before vendored or fetched dependencies.
- Every dependency has version, license, scope, provider, and update procedure.
