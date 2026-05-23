# Agentic Module Framework

## Purpose

This document optimizes the overall GCS architecture by adding an agentic
design overlay above the C++23 module solver. The overlay does not become a
solver runtime dependency. It is a design, maintenance, review, and evaluation
system that keeps each module's contracts strong and implementable.

The runtime solver remains a C++23 module pipeline. The agentic overlay gives
future work a disciplined way to ask: who owns this decision, what structured
input did they receive, what structured output did they produce, which tools
were allowed, which skill guided the work, which guardrails constrained it,
and which eval proves the result?

## Optimized Architecture

```text
architecture_steward_agent
  -> module design resources
  -> module specialist agents
       -> module tools
       -> module skills
       -> module eval suites
  -> accepted architecture updates
  -> C++23 module implementation tasks
```

The C++23 solver dependency graph is unchanged:

```text
kernel
  -> constraint_catalog
  -> incidence_graph
       -> decomposition_planner
  -> diagnostics
  -> numeric_engine
  -> session_runtime
       -> io_adapters
       -> viewer_bridge
```

The overlay has a strict rule: agents, skills, prompts, traces, and eval
harnesses may inspect solver modules and produce design or implementation
tasks, but lower solver modules must never import agentic infrastructure.

## Contract Pyramid

1. Runtime truth: exported C++23 module contracts.
2. Boundary truth: schemas for IO, tools, traces, and replay artifacts.
3. Design truth: architecture docs and module design cards.
4. Agent truth: module-specific instructions, tool permissions, guardrails,
   handoffs, and structured output expectations.
5. Quality truth: GTest/CTest, fixture corpora, traces, and regression reports.

Structured output means the most local typed contract available. In solver
code, that is an exported C++ struct. At external boundaries, it can be a JSON
schema or another explicit schema that mirrors the C++ contract.

## Standard Module Design Card

Every module must eventually maintain this design card:

```yaml
module_name: gcs.<module>
owner_agent: <module-agent-name>
mission: <what the module owns>
non_goals:
  - <decisions the module must refuse>
structured_inputs:
  - name: <InputContract>
    fields: <stable IDs, versions, tolerances, options>
structured_outputs:
  - name: <OutputContract>
    fields: <status, evidence, typed reports, IDs>
status_model:
  accepted: <meaning>
  rejected: <meaning>
  warnings: <meaning>
tools:
  - name: <deterministic-tool>
    input: <ToolInput>
    output: <ToolOutput>
    side_effects: none | explicit
skills:
  - name: <module-skill>
    use_when: <trigger>
guardrails:
  - <must refuse or validate>
handoffs:
  - target: <other-agent>
    when: <condition>
trace_events:
  - <event emitted for review/replay>
evals:
  - <contract test or agent eval>
backlog:
  - <next detail or implementation obligation>
```

## Required Agent Output

Every module agent must produce a structured design report, not only prose:

```yaml
module: <name>
decision_type: design | implementation_plan | review | eval_update
base_resources:
  - <doc or source path>
inputs_reviewed:
  - <contract names>
outputs_changed:
  - <contract names>
accepted_changes:
  - <change>
rejected_changes:
  - reason: <guardrail or dependency violation>
required_tests:
  - <test or eval>
handoff_requests:
  - target_agent: <agent>
    reason: <why ownership belongs there>
residual_risks:
  - <risk>
```

This mirrors modern structured-output practice while keeping GCS grounded in
its own C++ contracts.

## Guardrails

Global guardrails apply to all module agents:

- Do not weaken stable identity, immutable snapshot semantics, or state-version
  provenance.
- Do not add UI, file path, CLI, Python GUI, or app lifecycle policy to lower
  solver modules.
- Do not let numeric success imply runtime commit.
- Do not replace typed reports with free-form messages.
- Do not introduce hidden fallback behavior that changes mathematical meaning.
- Do not use third-party dependencies without scope, license, provider, and
  version records.
- Do not bypass C++23 modules for new solver code.

## Handoff Policy

Use manager-style orchestration by default. The architecture steward agent or
session runtime agent remains in control and calls specialist agents as tools.

Use handoff only when:

- one specialist owns the full decision;
- the handoff input is typed and narrow;
- the expected output is a module design report;
- the receiving agent has clear guardrails and eval gates.

Examples:

- `decomposition-planning-agent` hands a residual/Jacobian question to
  `constraint-semantics-agent`.
- `session-runtime-agent` hands a gluing certificate question to
  `diagnostics-certification-agent`.
- `io-adapter-agent` hands dependency-source questions to
  `third-party-governance-agent`.

## Tool Policy

Module tools should follow these rules:

- Tool input and output are typed.
- Tool output includes machine-readable `structuredContent` equivalents when
  exposed outside C++.
- Tool side effects are absent by default and explicit when needed.
- Stateful tools return explicit opaque handles instead of relying on implicit
  session state.
- Tools return typed execution errors that an agent can recover from.
- Tool names use stable module vocabulary, not implementation nicknames.

## Skill Policy

A GCS module skill is a durable playbook. It must define:

- trigger conditions;
- resources to inspect first;
- allowed tools;
- module invariants;
- typical edits or design artifacts;
- verification steps;
- outputs expected from the agent.

Skills are not substitutes for architecture docs. They are repeatable
operating procedures that help future agents follow the architecture.

## Trace And Eval Policy

Each important module decision should be replayable through:

- source resource list;
- agent design report;
- tool calls and tool outputs;
- accepted/rejected changes;
- required tests;
- resulting GTest/CTest or fixture report.

Agent evals should use small stable tasks first:

- design review tasks against known bad proposals;
- implementation-plan tasks with expected module ownership;
- contract-test generation tasks;
- regression triage tasks with trace evidence.

## Optimized Implementation Sequence

1. `kernel`: add validation, report taxonomy, ID policy, context validation,
   and state delta design.
2. `constraint_catalog`: add signatures, parameter schemas,
   residual/Jacobian provider contracts, and degeneracy reports.
3. `incidence_graph`: add hypergraph, reverse index, rigid-set graph, and
   structural dumps.
4. `decomposition_planner`: add cover verification, overlaps,
   boundary projections, gauge policy, solve DAG, and fallback reports.
5. `numeric_engine`: add initial-state, scaling, Jacobian, linear solver,
   rank/condition, manifold update, and iteration trace contracts.
6. `diagnostics`: add phases, precedence matrix, conflict/redundancy sets,
   projection-aware gluing, gauge checks, and obstruction minimization.
7. `session_runtime`: add transaction isolation, rollback, command traces,
   dependency injection, undo/redo, replay, and post-commit verification.
8. `io_adapters`: add schema registry, canonical serialization, migration,
   typed parse errors, round-trip diffs, and fixture lints.
9. `viewer_bridge`: add scene projections, diagnostic overlays, command
   drafts, hit testing, and history frames.
10. `tools`, `tests`, and `third_party`: add fixture generation, invariant
    checks, dependency audits, GTest/CTest gates, and metadata registry.

This order preserves the existing dependency direction: durable truth first,
semantic meaning second, structural planning third, numeric and diagnostic
evidence fourth, runtime commitment fifth, boundaries last.

## Architecture Acceptance Gates

The overall architecture is ready for deeper implementation only when:

- each module has a design card;
- each module has at least one core agent and one core skill definition;
- every public module path has structured input and output contracts;
- every failure path has typed status and report evidence;
- every module has deterministic tools or a documented reason for having none;
- every module has at least one GTest/CTest or agent-eval gate;
- `docs/architecture/README.md` points to the active design source of truth;
- `system-topology.md` documents that the agentic layer is a design overlay.
