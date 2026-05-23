# GCS Agentic SE Lifecycle And Self-Evolution Design

Research snapshot: 2026-05-24.

## Purpose

The GCS repository has passed the skeleton stage: architecture vocabulary,
C++23 module boundaries, module-specific skills, contract tests, and the first
algorithm-deepening work are already in place. The next engineering practice
question is no longer whether an agent can write code. It is how to make the
whole software-engineering lifecycle agentic without losing mathematical
correctness, reviewability, or human control.

This document designs the full-lifecycle agentic operating model for GCS:

- turn product, research, architecture, implementation, tests, review, release,
  and maintenance into explicit agent-callable workflows;
- make self-evolution possible through versioned knowledge, traces, evals,
  skills, and quality gates;
- keep the agentic layer as a design, maintenance, and CI overlay, never as a
  runtime dependency of the C++ solver core.

## External Best-Practice Synthesis

The current frontier practice across AI software-engineering companies
converges on a few stable patterns.

| Source | Observed practice | GCS design implication |
| --- | --- | --- |
| [OpenAI Codex launch](https://openai.com/index/introducing-codex/) | Run each coding task in an isolated repo environment; give the agent build/test commands and repository instructions; require terminal/test evidence before review. | Every GCS agent task must have a task card, allowed workspace, required checks, and evidence bundle. |
| [OpenAI Codex full-lifecycle update](https://openai.com/index/codex-for-almost-everything/) | Move agents beyond coding into PR review, browser/UI inspection, automations, memory, repeatable work, and long-running continuation. | GCS should model agent work as persistent lifecycle automations: triage, design, implementation, fixture growth, CI repair, and postmortem learning. |
| [OpenAI harness engineering](https://openai.com/index/harness-engineering/) | Agent-first teams shift human work toward environment design, intent specification, feedback loops, knowledge stores, and checked-in execution plans. | GCS needs an in-repo agentic knowledge store and execution-plan format, not ad hoc chats. |
| [Anthropic Claude Code workflows](https://code.claude.com/docs/en/common-workflows) | Use read-only plan mode for complex edits, then approve implementation after review. | GCS architecture and solver changes should begin with a plan artifact before code edits. |
| [Anthropic Claude Code security](https://code.claude.com/docs/en/security) | Default to read-only permissions and request approval for edits, tests, commands, and sensitive operations. | GCS agents should have explicit permission modes and stage-specific tool allowlists. |
| [Anthropic enterprise deployment guidance](https://code.claude.com/docs/en/third-party-integrations) | Invest in repository-level memory files with architecture, build commands, and contribution rules. | GCS skills and docs become durable shared memory; repeated failures should update skills or evals. |
| [GitHub Copilot coding-agent best practices](https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results) | Good task descriptions, repo custom instructions, and agent-runnable build/test validation produce better PRs. | GCS issue/task templates must be written as executable prompts with acceptance gates. |
| [Google secure AI agents](https://research.google/pubs/an-introduction-to-googles-approach-for-secure-ai-agents/) | Secure agents need human controllers, limited powers, and observable actions/plans. | GCS autonomy must be bounded by controller, capability, and observability contracts. |
| [Google agent-scaling research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) | Multi-agent systems help parallelizable tasks but can degrade sequential reasoning; centralized orchestration contains error propagation better than independent parallel agents. | GCS should use architecture-steward orchestration by default and parallelize only decomposable module tasks. |
| [Google ReasoningBank](https://research.google/blog/reasoningbank-enabling-agents-to-learn-from-experience/) | Agents improve when successful and failed trajectories are distilled into reusable strategic memory. | GCS self-evolution should learn from failures, not just successful PRs. |
| [Cognition SWE-1.5](https://cognition.ai/blog/swe-1-5) | Strong coding-agent environments combine classical tests, code-quality rubrics, agentic end-to-end grading, dogfooding, and reward-hardening against grader loopholes. | GCS quality must mix CTest, contract rubrics, agent review, and adversarial negative fixtures. |
| [Cognition Devin 2025 review](https://cognition.ai/blog/devin-annual-performance-review-2025) | Agents are powerful at scale but still need clear requirements and strong documentation for ambiguous work. | GCS should treat ambiguity as a planning failure: clarify, narrow, or route to human review. |
| [Cognition Devin 2.2](https://cognition.ai/blog/introducing-devin-2-2) | More autonomous agents self-test, self-review, auto-fix, and provide inspectable end-to-end evidence. | GCS agents should include self-verification before human review, but not self-merge. |
| [Cursor agent best practices](https://cursor.com/blog/agent-best-practices) | Start with plans, keep rules focused, check rules into git, and update them when the agent repeats mistakes. | GCS skill evolution should be lightweight, versioned, and driven by repeated observed errors. |

## Design Thesis

Agentic SE for GCS should be a control system around the solver project:

```text
human intent
  -> structured task card
  -> architecture steward planning
  -> specialist module agents
  -> deterministic tools and tests
  -> review and merge gates
  -> traces, postmortems, and learned rules
  -> improved skills, fixtures, evals, and docs
```

The solver remains a deterministic C++23 system. Agents are allowed to inspect,
design, implement, test, review, document, and automate around it. They are not
allowed to become hidden runtime policy.

## Operating Principles

1. **Humans define intent and risk; agents execute bounded workflows.**
   Autonomy increases only after the task is scoped, the owning module is
   identified, and the verification gate is known.

2. **Contracts are the agent interface.** GCS already treats stable IDs,
   snapshots, reports, fixtures, and C++23 module APIs as durable truth. Agent
   prompts, tools, and traces must point back to those contracts instead of
   inventing parallel semantics.

3. **Evidence beats confidence.** An agent result is incomplete without build
   output, CTest output, changed-file summary, report-code impact, and residual
   risk.

4. **Plan before high-risk edits.** Architecture, solver semantics, numeric
   behavior, IO schema, and quality-gate changes need a checked-in plan or task
   card before implementation.

5. **Use a manager architecture by default.** `gcs-architecture-steward`
   coordinates. Module agents own narrow specialist decisions. Parallel agents
   are used only when tasks are separable by module or artifact.

6. **Memory is curated, not hidden.** Durable agent memory lives in docs,
   skills, task cards, execution plans, and eval fixtures. Private or invisible
   memory may speed interaction, but it is not authoritative.

7. **Self-evolution must be falsifiable.** A proposed improvement to skills,
   tools, fixtures, or architecture must include a before/after failure mode and
   an eval or quality gate that can catch regression.

8. **Autonomy is permissioned.** Agents may propose changes broadly. They may
   execute only within explicit filesystem, command, network, dependency, and
   merge boundaries.

## Target Agentic SE Architecture

```text
docs/architecture + docs/agentic + fixtures + tests
  -> intent intake
      -> task cards
      -> risk classification
      -> ownership routing
  -> planning layer
      -> architecture steward
      -> module specialist agents
      -> checked-in execution plans
  -> implementation layer
      -> branch/worktree task sessions
      -> module skills
      -> deterministic scaffolding tools
  -> verification layer
      -> build/CTest/CLI gates
      -> fixture corpus and golden reports
      -> dependency audits
      -> agentic code review
  -> release and maintenance layer
      -> PR evidence bundles
      -> CI triage
      -> regression reproduction
      -> scheduled audits
  -> learning layer
      -> traces and postmortems
      -> experience records
      -> skill/rule updates
      -> new evals and fixtures
```

### Durable Artifact Layout

The following paths should become the durable agentic substrate:

```text
docs/agentic/
  README.md
  task-card-template.md
  execution-plan-template.md
  trace-schema.md
  experience-record-template.md
  eval-rubric.md
  lifecycle-runbook.md

docs/agentic/tasks/
  <date>-<slug>.md

docs/agentic/experience/
  <date>-<source>-<slug>.md

docs/agentic/evals/
  module-agent-evals.md
  review-rubrics.md

tools/agentic_design/
  agentic_toolkit.py
  module_inventory.json
```

The existing `.codex/skills/gcs-*` skills remain the operational playbooks.
The new `docs/agentic` layer records cross-lifecycle process, task memory, and
evolution records.

## Lifecycle Design

### 1. Intent Intake

Every non-trivial request is converted into a task card before implementation.
The task card is both a human-readable plan and an agent-readable prompt.

Required fields:

```yaml
task_id: 2026-05-24-agentic-se-example
request: <human intent>
scope: architecture | implementation | test | fixture | CI | docs | release
risk: low | medium | high
owning_agent: gcs-architecture-steward
specialist_agents:
  - gcs-numeric-engine-steward
affected_contracts:
  - NumericReport
  - IterationTrace
required_evidence:
  - build
  - ctest
  - agentic_toolkit validate-docs
  - dependency audit
human_gate:
  required: true
  reason: numeric semantics change
```

Routing rules:

- Architecture docs, module boundaries, dependency direction:
  `gcs-architecture-steward`.
- Module contracts, reports, and semantics: owning module skill.
- Tests, fixtures, CI, golden reports: `gcs-quality-steward` plus module owner.
- Scene schema and serialization: `gcs-io-adapter-steward`.
- GUI/viewer projection: `gcs-viewer-bridge-steward`.
- Third-party dependency changes: `gcs-third-party-governance-steward`.

### 2. Research And Architecture

The architecture steward first classifies the work:

- durable architecture rule;
- local implementation step;
- contract mismatch;
- missing fixture/eval;
- repeated agent failure that should update a skill;
- unsupported idea that should be refused or deferred.

For high-risk work, the agent must produce an execution plan with:

- base docs and source files read;
- affected module contracts;
- dependency-direction impact;
- exact edit sequence;
- verification commands;
- rollback or revert strategy;
- open questions and human decisions.

Plans are short-lived for small tasks and checked into `docs/agentic/tasks/`
for multi-step work.

### 3. Implementation

Implementation agents operate in branch/worktree-scoped sessions. Each session
must:

- load the relevant GCS skill and architecture documents;
- touch only files in the task scope;
- preserve unrelated dirty user changes;
- keep solver semantics in C++23 modules, not in scripts or UI;
- add or update contract tests when behavior changes;
- keep deterministic tools standard-library-first unless governance approves a
  dependency.

Patch output must include:

- changed files and contract impact;
- generated or edited fixtures;
- test commands run;
- failures and mitigations;
- residual risks.

### 4. Verification

GCS verification should combine four gates:

| Gate | Purpose | Example |
| --- | --- | --- |
| Classical executable tests | Objective correctness | `scripts\build_clang_ninja.cmd`, `ctest` |
| Contract/rubric review | Maintainability and architecture fit | module ownership, stable IDs, report-code evidence |
| Agentic review | Independent critique and regression search | reviewer agent reads diff and tests without editing |
| Adversarial fixtures | Reward-hardening against shallow passes | invalid schema, singular solve, gluing obstruction |

Minimum local gate for implementation tasks:

```bat
scripts\build_clang_ninja.cmd
ctest --test-dir out\build\clang-ninja --output-on-failure
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

Documentation-only changes should run the agentic design validators when they
touch architecture or skill surfaces.

### 5. Review And Merge

PR review becomes a two-layer process:

1. **Agent self-review before PR.**
   The authoring agent re-reads its own diff, checks task-card acceptance
   gates, and fixes obvious omissions.

2. **Independent review before merge.**
   A review agent or human reviewer checks:
   - contract drift;
   - missing negative tests;
   - hidden UI/IO/runtime dependency in lower modules;
   - report-code instability;
   - fixture determinism;
   - suspicious broad edits;
   - whether the task should update a skill or eval.

Agents may propose review fixes. They should not self-approve or self-merge
high-risk solver changes.

### 6. Release, CI, And Maintenance

CI should become a first-class agent workspace, not only a pass/fail signal.

Planned automations:

- **CI triage agent:** monitors failed checks, classifies failure, links to
  suspected module, proposes a task card.
- **Fixture drift agent:** detects changed golden digests and asks whether the
  semantic change is expected.
- **Dependency audit agent:** checks forbidden imports and third-party metadata.
- **Roadmap sync agent:** compares completed commits with
  `66-implementation-execution-roadmap.md` and current progress notes.
- **Regression reproducer:** turns user-reported failures into minimal fixtures.

Each automation must write evidence into `docs/agentic/experience/` or a PR
comment, not silently mutate architecture.

### 7. Learning And Self-Evolution

GCS self-evolution is a disciplined loop:

```text
observe failure or repeated friction
  -> create experience record
  -> classify root cause
  -> propose one of: skill update, doc update, fixture, tool, test, contract
  -> implement with evidence
  -> verify the new gate catches the old failure
  -> promote the lesson into durable memory
```

Experience record fields:

```yaml
experience_id: 2026-05-24-ci-gluing-obstruction-missed
source: ci | human-review | agent-error | production-use | research
symptom: <what failed>
root_cause: missing_context | weak_skill | missing_fixture | flaky_tool | ambiguous_task | contract_gap
affected_modules:
  - diagnostics
  - decomposition_planner
lesson: <generalizable rule>
proposed_promotion:
  type: skill | fixture | contract_test | architecture_doc | tool
validation:
  before: <old failure escaped>
  after: <new gate catches it>
```

Promotion tiers:

| Tier | Artifact | When to use |
| --- | --- | --- |
| T0 | Experience note | Single observed issue; not yet generalized. |
| T1 | Task template or checklist update | Repeated planning or review omission. |
| T2 | Skill update | Repeated module-agent mistake. |
| T3 | Fixture or contract test | Behavior should never regress. |
| T4 | Architecture rule | Durable dependency, semantic, or ownership rule. |
| T5 | Tool or CI gate | The check can be automated deterministically. |

This avoids turning every anecdote into a permanent rule while still letting
the project accumulate real engineering memory.

## Agent Roles

### Lifecycle Orchestrator

Owns end-to-end task routing, task-card completeness, risk level, required
human gates, and final evidence bundle.

Initial implementation can be the existing `gcs-architecture-steward` plus a
new lifecycle runbook. A separate physical skill is only needed once the
workflow becomes repetitive enough.

### Architecture Steward

Already defined by `gcs-architecture-steward`. It retains final authority over
module ownership, dependency direction, and durable architecture updates.

### Module Specialist Agents

Already mapped in `62-module-agents.md` and `.codex/skills/gcs-*`. They own
narrow semantic design and implementation checks for:

- `kernel`;
- `constraint_catalog`;
- `incidence_graph`;
- `decomposition_planner`;
- `numeric_engine`;
- `diagnostics`;
- `session_runtime`;
- `io_adapters`;
- `viewer_bridge`;
- `contract_tools`;
- quality gates;
- third-party governance.

### Quality And Evals Agent

Owns:

- CTest/contract suite shape;
- negative fixture corpus;
- golden report digests;
- agent-review rubrics;
- CI-ready quality scripts;
- eval tasks for module agents.

### Memory Curator

Owns experience promotion. It refuses to update skills or architecture unless
the lesson is supported by trace evidence and a repeatable validation path.

### Release And CI Agent

Owns scheduled checks, failed-CI triage, roadmap drift detection, and release
evidence collection. It proposes changes but should not merge.

## Tooling Roadmap

The existing `tools/agentic_design/agentic_toolkit.py` is the right seed. It
should be expanded in stages.

### Near-Term Commands

```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

### Add Next

```bat
python tools\agentic_design\agentic_toolkit.py new-task-card --module numeric_engine --slug damped-solve-regression
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md
python tools\agentic_design\agentic_toolkit.py collect-evidence --build-dir out\build\clang-ninja
python tools\agentic_design\agentic_toolkit.py new-experience-record --from-ci <log>
python tools\agentic_design\agentic_toolkit.py validate-experience docs\agentic\experience\<record>.md
python tools\agentic_design\agentic_toolkit.py suggest-skill-update docs\agentic\experience\<record>.md
python tools\agentic_design\agentic_toolkit.py run-quality-gates
```

`run-quality-gates` should become the standard pre-push command. It should
wrap build, CTest, docs validation, inventory validation, dependency checks,
fixture corpus checks, and representative CLI runs.

## Quality Model

GCS should grade agentic work on both output correctness and process quality.

| Dimension | Metric | Target |
| --- | --- | --- |
| Build health | build pass rate on agent PRs | trend upward |
| Test health | CTest pass rate and flaky-test count | pass, low flake |
| Contract quality | changed behavior with matching contract tests | near 100% |
| Diagnostic quality | failures include stable report IDs and subjects | near 100% |
| Review quality | independent review findings per PR | decline over time |
| Self-evolution | repeated mistakes converted to skill/eval/tool updates | steady |
| Autonomy safety | high-risk tasks with explicit human gate | 100% |
| Lead time | task-card to merged PR time | measured, not blindly minimized |
| Regression capture | user/CI failures converted to fixtures | high |

Do not optimize only for number of PRs. For a solver, the meaningful objective
is verified semantic progress per unit of review burden.

## Security And Control Boundaries

Agentic autonomy must be limited by default:

- No agent may introduce a third-party dependency without a
  `ThirdPartyDecision`.
- No lower solver module may import IO, viewer, CLI, Python GUI, app lifecycle,
  process launch, or agentic infrastructure.
- No agent may hide a runtime semantic change in documentation, fixture data,
  or UI code.
- No automation may push directly to protected branches.
- No scheduled job may run networked dependency fetches unless explicitly
  approved and recorded.
- No memory update is authoritative unless committed to repository-visible docs,
  skills, fixtures, tests, or tool metadata.
- No agent-authored code is accepted without executable evidence or a recorded
  reason why the evidence is unavailable.

## Implementation Phases

### Phase 0: Current Baseline

Already present:

- target architecture docs;
- module-specific skills;
- C++23 module skeleton and contract tests;
- `tools/agentic_design` inventory and validation tools;
- roadmap and current progress notes;
- contract-tested modules through solver pipeline, IO, viewer bridge, and
  quality gates.

### Phase 1: Lifecycle Substrate

Add:

- `docs/agentic/` templates and runbook;
- task-card validator;
- evidence bundle schema;
- experience-record template;
- `run-quality-gates` wrapper;
- README links from architecture docs.

Done when a new solver task can be represented as a task card and validated
before implementation.

### Phase 2: Agentic Execution Loop

Add:

- task-card-to-plan workflow;
- module-agent execution reports;
- independent agent-review rubric;
- fixture/golden digest promotion workflow;
- CI triage task-card generator.

Done when common implementation tasks can move from request to PR with
consistent evidence and review artifacts.

### Phase 3: Self-Evolution Loop

Add:

- experience records generated from failed CI, review findings, and repeated
  agent mistakes;
- skill-update suggestions from experience records;
- eval fixtures for module-agent planning and review;
- scheduled architecture and dependency audits.

Done when repeated failure patterns produce durable repo updates that prevent
recurrence.

### Phase 4: Bounded Autonomy

Add:

- scheduled automations for roadmap sync, CI triage, fixture drift, and
  dependency audits;
- parallel specialist-agent runs for decomposable module tasks;
- stricter quality scoring over agent PRs;
- human approval policies by risk class.

Done when GCS can maintain its docs, tests, fixtures, and routine repairs with
agent assistance while preserving human approval for semantic changes.

## Immediate GCS Backlog

1. Create `docs/agentic/README.md` and templates for task cards, execution
   plans, traces, experience records, and eval rubrics.
2. Extend `agentic_toolkit.py` with `validate-task-card`.
3. Add `run-quality-gates` as a single local command wrapping build, CTest,
   architecture validation, inventory validation, and dependency checks.
4. Add an evidence bundle schema that every agent PR can attach or summarize.
5. Define an independent agent-review rubric for architecture, contract,
   numeric, IO, viewer, fixture, and dependency changes.
6. Create the first three module-agent eval tasks:
   - detect forbidden dependency direction;
   - identify missing negative fixture for a report-code change;
   - classify ambiguous numeric behavior as needing human gate.
7. Add experience records for the next real CI failure or review correction.
8. Promote repeated review findings into skill updates only after the second
   recurrence or after a high-severity escape.
9. Add CI-ready quality scripts once Step 18 in the implementation roadmap
   begins.
10. After the quality scripts stabilize, create scheduled automations for CI
    triage and roadmap drift detection.

## Definition Of Done

GCS has achieved full-lifecycle agentic SE when:

- every non-trivial task starts from a validated task card;
- every high-risk task has a checked-in plan or explicit human approval;
- every behavior change has contract tests or a recorded exception;
- every agent-authored PR has executable evidence and residual-risk notes;
- every repeated agent failure is either rejected as noise or promoted into a
  skill, tool, fixture, eval, or architecture update;
- scheduled automations can triage routine failures without mutating solver
  semantics directly;
- the C++ solver core remains free of agentic runtime dependencies;
- humans still own product intent, architecture acceptance, dependency policy,
  and final merge decisions.

## Core Conclusion

The right self-evolving GCS is not an uncontrolled code-writing loop. It is a
repository that steadily improves its own instructions, contracts, tests,
fixtures, and tools as agents and humans encounter real work. The project
should evolve like a solver: propose local sections, check compatibility,
explain obstructions, and only then commit a globally verified state.
