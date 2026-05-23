# Module Agents

## Purpose

This document defines the specialist agents that will drive deep design for
each GCS module. These are architecture and maintenance agents, not solver
runtime objects. Their outputs must be structured design reports, implementation
plans, review findings, or eval updates.

## Architecture Steward Agent

Mission: preserve the whole GCS architecture, dependency direction, vocabulary,
and implementation sequence.

Structured input:

- architecture change request;
- affected modules;
- current architecture resources;
- proposed implementation or design delta.

Structured output:

- architecture decision report;
- accepted and rejected changes;
- required module-agent handoffs;
- required docs and tests;
- residual risks.

Tools:

- architecture map reader;
- dependency graph checker;
- C++23 module boundary scanner;
- design-card completeness checker.

Skill definition:

- Skill: `gcs-architecture-steward`.
- Use when changing architecture docs, planning cross-module refactors,
  naming target modules, or reviewing solver/runtime/IO/viewer boundaries.
- Output must name dependency impacts and required verification.

Guardrails:

- Never move UI, IO, CLI, or app lifecycle concerns into lower solver modules.
- Never accept prose-only failure contracts.
- Never allow new solver code to bypass the C++23 module constraint.

Handoffs:

- Hand off module-specific contract detail to the owning module agent.
- Retain final architecture acceptance authority.

Acceptance gates:

- Reading order and dependency graph remain coherent.
- Implementation sequence remains consistent with lower-to-higher dependency
  flow.

## Kernel Contract Agent

Mission: protect durable mathematical truth: stable identity, immutable
snapshots, state versions, contexts, policies, and typed reports.

Structured input:

- `ModelSnapshot`;
- `GeometricEntity`;
- `ConstraintInstance`;
- `ContextSnapshot`;
- `SolveIntent`;
- `UnitsPolicy`;
- `TolerancePolicy`;
- proposed `StateDelta` or validation rule.

Structured output:

- `ModelValidationReport`;
- `SnapshotDiff`;
- typed report-code changes;
- state-version transition design.

Tools:

- ID allocator and duplicate-ID validator;
- snapshot schema validator;
- context coverage validator;
- parameter dimension checker;
- report-code registry;
- deterministic snapshot diff.

Skill definition:

- Skill: `kernel-contract-skill`.
- Use when a change touches identity, model state, contexts, policies, reports,
  or state-version semantics.
- Inspect `domain-contracts.md`, `solver-contracts.md`, and `kernel.cppm`
  before proposing changes.
- Output required tests for lookup, duplicate IDs, context membership, and
  report provenance.

Guardrails:

- Refuse solver strategy, file path, GUI, CLI, or mutable global policy.
- Refuse coordinate mutation without explicit state-version transition.

Handoffs:

- Constraint semantics go to `constraint-semantics-agent`.
- Runtime commit semantics go to `session-runtime-agent`.

Acceptance gates:

- All entities and constraints are addressable by stable IDs.
- Invalid snapshots fail with typed diagnostics.
- Reports carry stable IDs and state versions.

Deep design backlog:

- `ModelValidationInput`;
- `StateDelta`;
- typed parameter schemas;
- report-code registry;
- canonical snapshot diff.

## Constraint Semantics Agent

Mission: own constraint meaning, signatures, parameter schemas, residual
dimensions, residual evaluators, Jacobians, generic DOF effect, and degeneracy
reports.

Structured input:

- `ConstraintValidationInput`;
- `ConstraintDefinition`;
- entity signatures;
- parameter schema;
- optional tolerance and degeneracy context.

Structured output:

- `ConstraintValidationResult`;
- `ResidualEvaluationResult`;
- `JacobianEvaluationResult`;
- `DegeneracyReport`;
- catalog version update.

Tools:

- constraint registry builder;
- signature matcher;
- parameter schema validator;
- residual/Jacobian conformance checker;
- finite-difference checker;
- degeneracy fixture generator.

Skill definition:

- Skill: `constraint-semantics-skill`.
- Use when adding or changing a constraint kind, residual, Jacobian,
  validation rule, or DOF metadata.
- Output residual dimension, parameter schema, degeneracy cases, and tests.

Guardrails:

- Refuse ad hoc residuals inside `numeric_engine`.
- Refuse planner-specific DOF hacks when the catalog owns the semantics.

Handoffs:

- Numeric convergence questions go to `numeric-engine-agent`.
- Model identity questions go to `kernel-contract-agent`.

Acceptance gates:

- Each constraint kind has arity, signatures, parameter schema, residual
  dimension, evaluator policy, and finite-difference coverage.

Deep design backlog:

- residual provider interface;
- analytic Jacobian interface;
- parameter schema registry;
- degeneracy taxonomy;
- catalog versioning.

## Incidence Structure Agent

Mission: turn immutable snapshots into deterministic structural facts:
hypergraphs, reverse indices, rigid-set graphs, components, separators, and
debug dumps.

Structured input:

- `IncidenceInput`;
- `ModelSnapshot`;
- validation reports;
- graph build options.

Structured output:

- `IncidenceIndices`;
- `ConstraintIncidence`;
- `RigidSetGraph`;
- component and separator reports;
- structural `StageReport`.

Tools:

- hypergraph builder;
- reverse index builder;
- rigid-set graph builder;
- connected-component engine;
- articulation and biconnected decomposition;
- graph dump generator;
- malformed-edge quarantine reporter.

Skill definition:

- Skill: `incidence-structure-skill`.
- Use when graph projections, structural indices, component logic, or planner
  inputs change.
- Output deterministic ordering rules and structural invariant tests.

Guardrails:

- Refuse coordinate mutation.
- Refuse planner policy or numeric rank interpretation.

Handoffs:

- Cover decisions go to `decomposition-planning-agent`.
- Invalid model semantics go to `kernel-contract-agent`.

Acceptance gates:

- Components cover all entities exactly once.
- Missing references produce typed errors.
- Structural dumps are deterministic.

Deep design backlog:

- entity-constraint hypergraph;
- constraint reverse index;
- rigid-set graph;
- articulation/biconnected reports;
- graph dump format.

## Decomposition Planning Agent

Mission: choose valid local-to-global covers, overlaps, boundary projections,
gauge policy, subproblems, solve DAG, and unsupported/fallback reports.

Structured input:

- `PlannerInput`;
- `ModelSnapshot`;
- `IncidenceIndices`;
- `SolveIntent`;
- diagnostic, rigidity, and rank hints.

Structured output:

- `PlannerOutput`;
- `CoverPlan`;
- `ContextSnapshot[]`;
- `BoundaryProjection[]`;
- `Subproblem[]`;
- `SolveStep[]`;
- `GaugePolicy`;
- structural report.

Tools:

- coverage verifier;
- boundary projection builder;
- gauge-policy selector;
- solve DAG builder;
- cycle checker;
- expected DOF estimator;
- connected-component cover planner;
- separator planner;
- fallback strategy selector.

Skill definition:

- Skill: `decomposition-planning-skill`.
- Use when cover semantics, solve ordering, gauge, boundaries, or unsupported
  decomposition behavior changes.
- Output coverage proof, overlap proof, gauge rationale, and tests.

Guardrails:

- Refuse numeric solving.
- Refuse runtime commit decisions.
- Refuse covers that do not explain shared boundary variables.

Handoffs:

- Structural facts go to `incidence-structure-agent`.
- Gluing semantics go to `diagnostics-certification-agent`.

Acceptance gates:

- Every active entity and constraint is covered.
- Overlaps have boundary projections.
- Solve order is a valid DAG.
- Unsupported cases are typed.

Deep design backlog:

- real overlap context generation;
- boundary projection schema;
- gauge selection;
- solve DAG;
- rigidity and separator planning.

## Numeric Engine Agent

Mission: produce local sections with numeric evidence for a declared context.
It does not plan covers, glue sections, mutate durable state, or accept
commands.

Structured input:

- `NumericTask`;
- `ModelSnapshot`;
- `ContextSnapshot`;
- active variables and equations;
- boundary variables;
- `GaugePolicy`;
- `TolerancePolicy`;
- `SolveLimits`;
- initial state, scaling policy, Jacobian policy, linear solver policy.

Structured output:

- `NumericReport`;
- `LocalSection`;
- `ProposedState`;
- per-constraint residuals;
- rank and condition estimates;
- iteration trace;
- failure cause.

Tools:

- task validator;
- residual assembler;
- Jacobian assembler;
- finite-difference checker;
- parameter scaling tool;
- manifold retraction tool;
- dense baseline least-squares solver;
- sparse solver adapter;
- rank/conditioning estimator;
- residual sorter;
- numeric replay harness.

Skill definition:

- Skill: `numeric-engine-skill`.
- Use when local solving, residual assembly, Jacobian, scaling, rank,
  conditioning, or numeric trace contracts change.
- Output a local-section report and no runtime commit claim.

Guardrails:

- Refuse global acceptance decisions.
- Refuse hidden fallback that changes mathematical meaning.
- Refuse residual definitions not owned by `constraint_catalog`.

Handoffs:

- Constraint evaluator questions go to `constraint-semantics-agent`.
- Failure classification goes to `diagnostics-certification-agent`.

Acceptance gates:

- Missing IDs fail before iteration.
- Successful reports include residuals, rank, condition, iteration count, and
  base state version.
- Boundary variables are explicit and not silently rewritten.

Deep design backlog:

- initial-state schema;
- scaling and solver policies;
- residual/Jacobian assembly;
- manifold retraction;
- per-constraint residual reports;
- iteration trace schema.

## Diagnostics Certification Agent

Mission: explain and certify structural, numeric, and local-to-global status:
under-constraint, over-constraint, redundancy, conflict, singularity,
inconsistency, gluing failure, and accepted verification.

Structured input:

- `DiagnosticInput`;
- `GluingInput`;
- `ModelSnapshot`;
- optional `ContextSnapshot`;
- optional `NumericReport`;
- `CoverPlan`;
- `BoundaryProjection[]`;
- `LocalSection[]`;
- tolerance and gauge policy.

Structured output:

- `DiagnosticOutput`;
- `DofReport`;
- `RankReport`;
- `ResidualReport`;
- `GluingReport`;
- `ObstructionReport`;
- `ConflictSet[]`;
- `RedundancySet[]`;
- status precedence trace.

Tools:

- DOF analyzer;
- structural rank estimator;
- numeric rank reconciler;
- residual evaluator;
- boundary projection comparator;
- gauge consistency checker;
- conflict set minimizer;
- redundancy detector;
- obstruction classifier;
- status precedence resolver.

Skill definition:

- Skill: `diagnostics-certification-skill`.
- Use when failure explanation, gluing, obstruction, rank/DOF evidence, or
  report taxonomy changes.
- Output the smallest known evidence set and required negative tests.

Guardrails:

- Refuse durable state mutation.
- Refuse numeric iteration policy.
- Refuse accepting failed gluing.

Handoffs:

- Local residual evidence goes to `numeric-engine-agent`.
- Boundary construction questions go to `decomposition-planning-agent`.

Acceptance gates:

- Failed gluing produces an obstruction.
- Status precedence is deterministic.
- Structural and numeric evidence remain distinct.

Deep design backlog:

- diagnostic phase enum;
- status precedence matrix;
- conflict/redundancy sets;
- projection-aware gluing;
- gauge checks;
- obstruction minimization.

## Session Runtime Agent

Mission: own command workflow, transaction isolation, orchestration, history,
replay, acceptance, rollback, and durable state-version advancement.

Structured input:

- `Command`;
- `CommandId`;
- `CommandKind`;
- `SolveIntent`;
- command preconditions;
- current `ModelSnapshot`;
- tool handles for planner, numeric, diagnostics, IO, and viewer adapters.

Structured output:

- `CommandResult`;
- transaction ID;
- previous and new state versions;
- stage reports;
- planner, numeric, diagnostic, and gluing reports;
- rollback reason;
- replay artifact;
- history event.

Tools:

- command validator;
- transaction snapshot/journal;
- pipeline orchestrator;
- stage trace collector;
- runtime guardrail checker;
- commit/rollback tool;
- undo/redo store;
- dependency-injected module adapters;
- command-result formatter;
- replay harness.

Skill definition:

- Skill: `session-runtime-skill`.
- Use when commands, behavior modes, transactions, history, undo/redo,
  orchestration, or replay changes.
- Output atomicity proof and rollback tests.

Guardrails:

- Refuse partial durable mutation on rejected commands.
- Refuse accepting numeric success without diagnostic/gluing acceptance.
- Refuse hidden pipeline stages without trace entries.

Handoffs:

- Math and structure decisions go to specialist module agents.
- IO persistence questions go to `io-adapter-agent`.

Acceptance gates:

- Rejections preserve prior state version and geometry.
- Accepted commands advance state version only after verification.
- Every command returns a complete stage trace.

Deep design backlog:

- command preconditions;
- transaction journal;
- dependency injection;
- replay artifact;
- undo/redo history;
- post-commit verification.

## IO Adapter Agent

Mission: own versioned scene intake/export, fixture compatibility, schema
migration, canonical serialization, and parse/validation reporting.

Structured input:

- `SceneLoadRequest`;
- `SceneWriteRequest`;
- `SceneNormalizeRequest`;
- `SceneMigrationRequest`;
- schema version;
- format, path, units, tolerance, compatibility mode.

Structured output:

- `SceneLoadResult`;
- `SceneWriteResult`;
- `SceneValidationReport`;
- `SceneMigrationReport`;
- canonical serialization digest;
- typed parse errors.

Tools:

- schema registry;
- canonical text and JSON serializer;
- migration runner;
- fixture linter;
- round-trip diff;
- corpus loader;
- digest generator.

Skill definition:

- Skill: `io-adapter-skill`.
- Use when scene formats, fixtures, serialization, migration, or round-trip
  compatibility changes.
- Output schema version impact and round-trip tests.

Guardrails:

- Refuse lower solver imports from IO.
- Refuse hidden schema repair without a migration report.
- Refuse non-deterministic serialization.

Handoffs:

- Semantic validation goes to `kernel-contract-agent`.
- Fixture behavior goes to `quality-agent`.

Acceptance gates:

- Load-write-load equality passes.
- Deterministic byte output.
- Typed parse and migration errors include stable IDs when available.

Deep design backlog:

- schema registry;
- JSON support;
- migration reports;
- canonical digest;
- typed parse errors;
- corpus tests.

## Viewer Bridge Agent

Mission: project solver truth into read-only GUI/API summaries, diagnostic
overlays, interaction drafts, and history frames without owning durable truth.

Structured input:

- `ViewerProjectionRequest`;
- `ModelSnapshot`;
- `CommandResult`;
- selected IDs;
- projection mode;
- diagnostic verbosity;
- interaction intent.

Structured output:

- `ViewerSceneProjection`;
- `SnapshotSummary`;
- `DiagnosticOverlay`;
- `InteractionCommandDraft`;
- `HistoryFrameProjection`.

Tools:

- projection builder;
- report summarizer;
- diagnostic overlay generator;
- selection mapper;
- hit-test mapper;
- command-draft validator.

Skill definition:

- Skill: `viewer-bridge-skill`.
- Use when GUI/API projections, overlays, selection, interaction drafts, or
  history replay views change.
- Output deterministic projection tests and runtime-command validation.

Guardrails:

- Refuse durable state mutation.
- Refuse private solver guesses for visual status.
- Refuse UI edits that bypass runtime commands.

Handoffs:

- Command validity goes to `session-runtime-agent`.
- Diagnostic status mapping goes to `diagnostics-certification-agent`.

Acceptance gates:

- Identical snapshot and reports produce identical projections.
- Projected IDs resolve in kernel.
- Interaction drafts validate as runtime commands.

Deep design backlog:

- scene projection contract;
- diagnostic overlay model;
- interaction draft contract;
- hit-test mapping;
- history frame projection.

## Contract Tools Agent

Mission: curate deterministic developer and test utilities that turn
architecture claims into reproducible fixtures, invariant checks, and audits.

Structured input:

- `FixtureBuildRequest`;
- `InvariantCheckRequest`;
- `CorpusGenerationRequest`;
- `DependencyAuditRequest`;
- deterministic seed;
- expected status manifest.

Structured output:

- `ModelSnapshot`;
- `ContextSnapshot`;
- `ToolReport`;
- fixture bundle;
- golden report;
- module dependency report.

Tools:

- sample scene builders;
- invariant checker;
- fixture generator;
- golden report writer;
- module dependency scanner;
- CLI harness.

Skill definition:

- Skill: `contract-tools-skill`.
- Use when adding fixtures, developer utilities, invariant checks, or
  architecture audits.
- Output provenance metadata and deterministic replay steps.

Guardrails:

- Refuse production solver policy in test-only helpers.
- Refuse nondeterministic fixtures without explicit seed.

Handoffs:

- Scene semantics go to `io-adapter-agent`.
- Test gating goes to `quality-agent`.

Acceptance gates:

- Generated snapshots validate through public contracts.
- Fixtures are deterministic.
- Tests consume tools through public modules.

Deep design backlog:

- fixture provenance;
- invariant checker;
- corpus generator;
- dependency scanner;
- split support target from production library.

## Quality Agent

Mission: convert architecture rules into executable contract tests, fixture
corpora, regression artifacts, and CI gates.

Structured input:

- fixture set;
- `ModelSnapshot`;
- runtime commands;
- expected `SolveStatus`;
- tolerance policy;
- expected report IDs and statuses.

Structured output:

- GTest/CTest result;
- diagnostic snapshot;
- IO round-trip report;
- numeric robustness report;
- coverage or sanitizer summary;
- missing-test risk report.

Tools:

- GoogleTest;
- CTest;
- fixture linter;
- IO round-trip tester;
- numeric tolerance oracle;
- module dependency checker;
- CI matrix runner.

Skill definition:

- Skill: `quality-agent-skill`.
- Use when contract tests, negative cases, fixture corpora, CI, or regression
  reports change.
- Output tests tied to public contracts and residual risks.

Guardrails:

- Refuse implementation-internal assertions when a public contract can be
  asserted.
- Refuse treating skipped dependency setup as a quality pass.

Handoffs:

- Dependency failures go to `third-party-governance-agent`.
- Module-specific missing tests go to the owning module agent.

Acceptance gates:

- Build passes.
- `ctest` passes.
- Negative fixtures produce typed obstructions.
- Reports name relevant stable IDs.

Deep design backlog:

- obstruction corpus;
- IO round-trip suite;
- viewer projection suite;
- numeric robustness suite;
- dependency gate;
- CI matrix.

## Third-Party Governance Agent

Mission: govern dependency scope, licensing, reproducibility, ABI/runtime
compatibility, CMake adapter targets, and offline build behavior.

Structured input:

- `ThirdPartyRequest`;
- dependency name;
- version or tag;
- upstream URL;
- license;
- scope;
- provider order;
- build options;
- exposed CMake targets;
- update procedure.

Structured output:

- `ThirdPartyDecision`;
- metadata record;
- CMake adapter target;
- license/audit report;
- provider fallback test result.

Tools:

- CMake package adapter;
- metadata validator;
- license scanner;
- version pin checker;
- ABI/runtime compatibility checker;
- offline configure test.

Skill definition:

- Skill: `third-party-governance-skill`.
- Use when adding, updating, vendoring, fetching, or linking third-party code.
- Output provider order, license, scope, exposed targets, and offline behavior.

Guardrails:

- Refuse test-only dependencies in production targets.
- Refuse network fetches as default behavior.
- Refuse global include/library leaks.

Handoffs:

- Test dependency behavior goes to `quality-agent`.
- Build-system impacts go to `architecture-steward-agent`.

Acceptance gates:

- Offline configure succeeds with installed or vendored dependencies.
- License and version metadata exists.
- CMake exposes narrow imported or alias targets.

Deep design backlog:

- third-party metadata registry;
- CMake adapter layer;
- GTest 1.17.0 installed-package reconciliation;
- license/SBOM audit gate;
- provider fallback tests.
