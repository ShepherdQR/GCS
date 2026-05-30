---
experience_id: E006-parallel-agent-pipeline-implementation
source: session-practice
status: candidate-experience
root_cause: n-way-agent-parallelism-for-self-contained-modules
affected_modules:
  - pipelines
  - agentic_dispatch
  - module_contract
  - run.py_integration
promotion_target: candidate-prompt-after-second-confirmation
---

# E006: Parallel Agent Pipeline Implementation

## Thesis

When N modules share an identical outer contract (dataclass shape, `run()`
signature, preset convention, import path), all N can be built by independent
agents dispatched in a single parallel round-trip. The only post-hoc
integration needed is a registry file that lists the modules and a
`__init__.py` that re-exports their public symbols.

## Problem

Building a family of pipeline modules serially forces linear time in N.
Each module spends most of its turn in model inference, not in dependency
resolution. Sequential dispatch also risks drift — later modules may
inadvertently diverge from the contract established by earlier ones, because
the author (human or agent) forgets what convention was settled.

## Lesson

**Parallel dispatch works when each agent's task is fully self-contained and
the shared interface is specified before dispatch, not discovered during
implementation.**

The preconditions that made this work:

1. **Contract first.** Before dispatching, define the shared dataclass
   (`PipelineResult`), the `run() -> PipelineResult` method signature, the
   preset naming convention (`smoke`/`standard`/`full`), and the module
   import path convention (`tools/solver_testing/pipelines/<name>.py`).

2. **One module per agent.** Each agent's prompt specified exactly one file
   to create, with the module's unique domain logic, but referenced the
   shared contract for structure. No agent needed to know about another
   agent's module internals.

3. **Self-contained dependencies.** Each module imports from the shared
   tooling layer (`defect_store`, `runner`, `mutator`, etc.) but never from
   another pipeline module. No intra-pipeline import graph to coordinate.

4. **Integration deferred.** After all agents finished, a single integration
   step created `__init__.py` (re-exports) and `run.py` (PIPELINE_REGISTRY
   with tier, presets, config_keys, estimated_runtime). This step is
   mechanical and small — it only needs the class name and tier from each
   module, not the internals.

5. **Import-verify as gate.** The first validation is `python -c "from
   tools.solver_testing.pipelines import *"`. If every module imports
   cleanly, the contract held. Deeper integration tests (end-to-end with
   GCS.exe) are deferred to a separate phase.

## Evidence

This experience is supported by the 10-pipeline implementation session:

- Task card: `docs/agentic/tasks/2026-05-30-10-pipeline-quality-infrastructure.md`
- Archive: `docs/completed-tasks/2026-05-30-10-pipeline-quality-infrastructure/README.md`

Concrete metrics from the dispatch:

| Metric | Value |
|--------|-------|
| Agents dispatched | 10 (one per pipeline module) |
| Round-trips | 1 (all dispatched in parallel) |
| Lines produced | ~7,800 across 10 files |
| Per-module range | 343--1,116 lines |
| Import check | 40+ symbols, all clean |
| Manual integration | 2 files (`__init__.py`, `run.py`) |
| Contract failures | 0 (no agent diverged from PipelineResult shape) |

The 10 pipeline modules:

| Module | Lines | Tier | Complexity driver |
|--------|-------|------|-------------------|
| `defect_discovery.py` | 677 | P0 | Multi-step workflow (enumerate, mutate, solve, classify, analyze) |
| `regression.py` | 517 | P0 | Baseline comparison with fixture corpus |
| `stability.py` | 946 | P0 | Logspace sweeps across multiple constraint types |
| `diagnostics_cert.py` | 368 | P1 | Known-bad input type catalog with expected error codes |
| `contract_compliance.py` | 674 | P1 | Module boundary audit with import graph traversal |
| `roundtrip.py` | 1116 | P1 | JSON + text serialization with solve-compare |
| `scene_gen.py` | 632 | P2 | Coverage-driven enumeration with gap detection |
| `benchmark.py` | 888 | P2 | Performance measurement with SQLite trend DB |
| `cross_solver_compare.py` | 717 | P2 | External solver harness with ComparisonPoint |
| `repo_audit.py` | 896 | P3 | File classification, stale detection, snapshot |

## When To Use

- Building N > 3 modules that share an identical outer contract
- Each module is independently importable (no circular dependencies)
- The shared interface can be written down in under 20 lines before dispatch
- Integration is mechanical: a registry, an `__init__.py`, or both
- Module count is known and fixed at dispatch time (not discovered iteratively)

## When NOT To Use

- Modules depend on each other's output or design decisions
- The contract itself needs to be discovered through implementation
- Only 1--2 modules are needed (parallel overhead not worth it)
- The modules share mutable state or require a specific build order
- One module's failure would invalidate the whole batch (tight coupling)

## Prompt Template

Save as `templates/parallel-agent-module-prompt.md` and adapt per module.
The template captures the minimum information each agent needs to be
self-sufficient.

## Eval Scaffold

A future gate should present:

1. A shared contract spec (PipelineResult shape, run() signature, preset convention)
2. A list of 4 module names with one-sentence domain descriptions
3. One module description that deliberately omits a field required by the contract

Expected behavior:
- All agents produce modules that import cleanly
- The integration step correctly builds `__init__.py` and registry
- The agent handling the incomplete description either fills the field from
  context or asks for clarification — it does not silently omit it

## Skill Or Agent Decision

Do not promote to skill or agent.

- **Not a skill**: The pattern is an agentic dispatch technique, not a
  domain capability. No steward skill maps to "parallel agent dispatch."
- **Not an agent**: No new institutional agent role emerges. The pattern
  describes how a human or orchestrator dispatches work, not a persistent
  agent that runs autonomously.
- **Candidate prompt only**: After a second successful parallel dispatch
  (different domain, same pattern), promote the prompt template to an
  active skill parameter or orchestrator dispatch rule.

## Promotion Threshold

- Current status: candidate-experience with provisional prompt template.
- Evidence needed for promotion: one more parallel dispatch of N >= 4
  modules in a different problem domain (not pipelines) with zero contract
  failures and clean import gating.
- If a second dispatch succeeds: promote the prompt template to
  `orchestrator` skill dispatch parameters.
- If a second dispatch fails: record the failure mode here as a boundary
  condition and refine the "When NOT To Use" section.

## Operating Invariants

- Contract is written before dispatch, never discovered during implementation.
- Each agent receives exactly one module to build.
- No agent prompt references another agent's module internals.
- Integration step touches only registry and re-export files, never module
  internals.
- First validation gate is import-clean — deeper tests are separate.
- One agent failure does not invalidate other agents' outputs (no tight coupling).
