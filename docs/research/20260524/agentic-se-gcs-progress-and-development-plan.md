# GCS Agentic-SE Progress Assessment And Development Plan

Snapshot date: 2026-05-24.

This report applies the dimension model from
`docs/research/20260524/agentic-se-dimensions-metrics-research-report.md` to
the current GCS repository. It focuses on the agentic software-engineering
operating layer, not on replacing the solver roadmap.

## Current Baseline

The GCS repository already has an unusually strong agentic-SE substrate:

- target architecture vocabulary and module boundaries are documented under
  `docs/architecture/`;
- local project skills exist for kernel, constraint catalog, incidence graph,
  decomposition planning, diagnostics, numeric engine, session runtime, IO,
  viewer bridge, contract tools, scene generation, UI, figures, quality, and
  third-party governance;
- `docs/agentic/` contains task-card, execution-plan, evidence, trace,
  experience, eval, lifecycle, near-term, and long-term operating artifacts;
- `tools/agentic_design/agentic_toolkit.py` validates docs, module inventory,
  skills, dependency boundaries, task cards, completed-task reports, closure
  scores, and quality-gate command composition;
- the C++ implementation roadmap is complete through Step 46, with Step 47
  registered as deterministic runtime replay evidence export tooling;
- CTest currently discovers 111 contract tests in the existing
  `out/build/clang-ninja` tree;
- focused agentic validation passed for docs, module inventory, skills, and
  C++ module dependency boundaries;
- the quality-gate contract includes build, CTest, fixture corpus, public
  evidence-chain sentinels, Python tool tests, and CLI smoke tests.

Worktree note: this assessment found existing modified and untracked files
under `docs/agentic/`, especially institutional-agent artifacts. This report
does not overwrite or normalize those files.

## Evidence Collected

Local commands run for this assessment:

```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
ctest --test-dir out\build\clang-ninja -N
```

Results:

- `validate-docs`: passed.
- `validate-inventory`: passed.
- `validate-skills`: passed.
- `check-dependencies`: passed.
- `ctest -N`: 111 tests discovered after allowing CTest to write its temporary
  test log.

Repository artifact counts observed:

| Artifact | Count |
| --- | ---: |
| `docs/agentic/tasks/*.md` including task README | 4 |
| completed-task archive directories | 11 |
| experience library entries | 2 |
| institutional-agent directories plus templates directory | 5 |
| project `.codex/skills` directories | 19 |
| contract-test `.cpp` files under `tests/contracts` | 13 |

## Dimension Progress Scorecard

Score legend:

- 1 = mostly absent
- 2 = present but ad hoc
- 3 = usable but under-sampled
- 4 = strong and repeatable
- 5 = mature, measured, and hard to regress

| Dimension | Score | Current Progress | Main Gap |
| --- | ---: | --- | --- |
| Strategic task portfolio | 3 | Long-term and near-term plans exist; Step 47 is registered with a concrete next goal. | No quantitative task portfolio or value taxonomy yet. |
| Lifecycle discipline | 3 | Task templates, lifecycle runbook, PDCA roadmap, task-card validator, completed-report validator, and closure scorer exist. | Too few real high-risk tasks have completed the full card-to-archive loop. |
| Repository knowledge and memory | 4 | Architecture map, module inventory, skills, runbooks, evals, and experience templates are present. | Staleness and contradiction checks are not yet measured as a routine dashboard. |
| Architecture and contracts | 5 | Target modules, public contracts, dependency direction, typed reports, fixtures, and 111 tests form a strong substrate. | Future semantic changes still require strict discipline to avoid bypassing contracts. |
| Harness and tools | 4 | Agentic toolkit and quality-gate wrapper provide deterministic local commands. | Full gate execution cost, flake data, and failure taxonomy are not yet tracked over time. |
| Agent orchestration and skills | 3 | 19 local skills and module-agent docs exist; architecture steward routing is clear. | Institutional agents are still becoming verifiable; routing accuracy is not measured. |
| Verification and evals | 4 | CTest, public evidence-chain sentinels, Python tool tests, CLI smokes, eval seeds, and review rubrics exist. | Agent evals are seed-level and need real negative cases from observed failures. |
| Security and governance | 3 | Human-gate rules, dependency policy, and third-party governance skill exist. | Skill-security review and permission escalation metrics are not yet first-class. |
| Observability and evidence | 4 | Runtime stage traces, report evidence, replay boundary, evidence bundles, and closure archives exist. | A single metrics dashboard is missing. |
| Learning and self-evolution | 3 | Experience library and promotion concepts exist; two experience entries are present. | Promotion decisions are not yet tracked as a measured queue. |
| Delivery metrics | 2 | Quality gates and roadmap updates exist. | DORA-style lead time, rework rate, change failure, and recovery metrics are not collected. |
| Product and visual evidence surfaces | 3 | UI design-system roadmap, figure pipeline, showcase scene, and visual QA tools exist. | Token unification, screenshot/contrast/overflow gates, and GUI consumption are pending. |

## Key Diagnosis

GCS is strongest in contract architecture, solver evidence, and deterministic
quality gates. It is less mature in quantitative process telemetry and
agentic-loop sampling. The project has designed the lifecycle well, but the
lifecycle has not yet been proven across enough high-risk implementation
tasks.

The next phase should avoid inventing more process vocabulary. The right move
is to run the existing lifecycle on Step 47, measure it, and use the resulting
friction to harden validators, evals, dashboards, and institutional agents.

## Target State

GCS should aim for this operating state:

1. Every non-trivial task starts with a task card or explicit chat-only
   exception.
2. Every high-risk task has an execution plan, human gate, owning skill, and
   acceptance gates before edits.
3. Every implementation task ends with executable evidence, residual risk, and
   a discoverable archive.
4. Every repeated agent failure becomes either no action or a concrete
   promotion candidate: skill, doc, eval, fixture, test, tool, or architecture
   rule.
5. The default quality gate stays deterministic, while dashboards track gate
   health, review burden, and lifecycle completion.
6. Institutional agents become verifiable packages with templates, examples,
   prompts, and refusal-oriented evals.
7. Scheduled automations may observe and propose, but not silently mutate
   solver semantics or protected branches.

## Development Plan

### Phase 0: Baseline Metrics Dashboard

Timebox: 1-3 days.

Goal: make the current process measurable before adding stricter gates.

Deliverables:

- `docs/agentic/metrics-dashboard.md` or equivalent dashboard page.
- A baseline table for lifecycle, quality, architecture, security,
  orchestration, learning, and delivery metrics.
- A short rule for when dashboard updates are required.

Initial metrics:

| Metric | Starting Baseline | 30-Day Target |
| --- | --- | --- |
| Task-card coverage for non-trivial tasks | Manual inspection only | 80% or explicit exception |
| High-risk human-gate compliance | Rule exists | 100% |
| Completed archive discoverability | 11 archives, cross-link quality not fully measured | 90% indexed and linked |
| Closure score usage | Tool exists | Used on next 3 non-trivial closures |
| Agentic validation pass rate | Current focused checks passed | Keep 100% on mainline docs/tool changes |
| CTest discovered tests | 111 | Non-decreasing unless explained |
| Experience promotion decisions | Ad hoc | Every new experience has a promotion decision |
| Permission escalation log | Tool/session-level only | Summarized in completed-task evidence for high-risk work |

Acceptance gates:

```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

### Phase 1: Prove The Lifecycle On Step 47

Timebox: next high-risk implementation cycle.

Goal: use Step 47 runtime replay evidence export as the first serious
high-risk lifecycle sample after the Step 46 drift reconciliation.

Required setup:

- Create a task card before touching runtime/export code.
- Mark risk as high if the work touches runtime history, report evidence,
  viewer projections, CLI export, or scene replay boundaries.
- Use `gcs-session-runtime-steward` as the primary specialist.
- Add `gcs-viewer-bridge-steward`, `gcs-io-adapter-steward`, and
  `gcs-quality-steward` only if their boundaries are actually touched.

Step 47 implementation acceptance:

- Runtime replay evidence exports as deterministic report evidence.
- Export does not write or masquerade as JSON scene `history`.
- Contract tests cover deterministic ordering, missing command or empty
  history handling, artifact kind, report-evidence flag, and state-version
  ranges.
- Viewer or CLI projection ownership is documented.
- Completed-task archive links task card, changed files, commands, skipped
  checks, and residual risk.
- PDCA roadmap receives an Act update.

Suggested checks:

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<step-47-task>.md
ctest --test-dir out\build\clang-ninja -R "SessionRuntimeContract|ViewerBridgeContract" --output-on-failure --no-tests=error
python tools\agentic_design\agentic_toolkit.py run-quality-gates
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\<step-47-archive>\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\<step-47-archive>\README.md --min-score 30
```

### Phase 2: Opt-In Lifecycle Artifact Gates

Timebox: 1-2 weeks after Step 47 closure.

Goal: make task cards and completed-task reports checkable without breaking
legacy artifacts.

Deliverables:

- `--include-task-cards` or path-scoped validation mode for quality gates.
- `--include-completed-reports` or path-scoped completed-report validation.
- Unit tests for valid cards, missing fields, high-risk without human gate,
  placeholder text, invalid owner, and empty evidence.
- Legacy archive exemption or migration policy.

Acceptance metrics:

| Metric | Target |
| --- | --- |
| New task-card validation coverage | 100% for new high-risk cards |
| New completed-report validation coverage | 100% for new non-trivial archives |
| Legacy archive breakage | 0 default-gate failures |
| Validator unit coverage | Valid, invalid, and placeholder cases covered |

### Phase 3: Independent Review And Eval Growth

Timebox: 2-4 weeks.

Goal: stop relying on author-agent self-confidence.

Deliverables:

- Review checklist by task type connected to `docs/agentic/evals/review-rubrics.md`.
- At least three E001 closure-score samples from real tasks.
- One negative eval for false completion, missing evidence, or archive
  pollution.
- One module-agent eval generated from a real Step 47 or later review finding.

Acceptance metrics:

| Metric | Target |
| --- | --- |
| High-risk independent review coverage | 100% |
| Closure reports scored | 3 real tasks |
| Negative evals from real misses | At least 1 |
| Review finding recurrence | Downward trend after promotion |

### Phase 4: Learning And Experience Promotion Queue

Timebox: 1 month.

Goal: turn repeated agent friction into durable improvements.

Deliverables:

- Experience promotion board with states: observed, candidate, promoted,
  rejected, superseded.
- Promotion criteria for skill, fixture, contract test, architecture doc,
  tool, or no action.
- Before/after evidence requirement for any promoted lesson.
- A monthly cleanup rule for stale or unvalidated experience records.

Acceptance metrics:

| Metric | Target |
| --- | --- |
| High-severity escape capture | 100% |
| Repeated omission capture | 100% after second occurrence |
| Promotions with before/after evidence | 100% |
| Rule inflation without evidence | 0 |

### Phase 5: Institutional Agents Become Verifiable

Timebox: 1-2 months.

Goal: make standing agents useful institutions, not decorative role prose.

Priority agents:

- `001-bladesmith-quench-forge`: experience distillation and promotion
  candidate extraction.
- `002-tailor-stitch-timeline`: chronology, resumption context, and task
  sequence integrity.
- `003-atelier-steward-calibrate-review`: UI/design convention review.
- `004-art-director-frame-judge`: visual artifact review.

Required package per promoted institutional agent:

- role README;
- invocation prompt;
- one template;
- one real filled example;
- one refusal-oriented eval;
- explicit boundaries and non-goals.

Acceptance metrics:

| Metric | Target |
| --- | --- |
| Promoted role packages with evals | 100% |
| Examples based on real artifacts | 100% |
| Unsupported generalization refusal eval | Present for memory/experience roles |
| Invented chronology refusal eval | Present for timeline role |

### Phase 6: Bounded Automations

Timebox: after at least three clean lifecycle closures.

Goal: add monitors that observe and propose without silently changing solver
semantics.

Candidate automations:

- roadmap sync monitor;
- CI triage monitor;
- fixture drift monitor;
- dependency and forbidden-import audit;
- stale task-card/archive link monitor;
- experience promotion reminder.

Rules:

- Automations write reports or proposed task cards.
- Automations do not merge, push, rewrite history, add dependencies, or mutate
  solver semantics without human approval.
- Networked and dependency-fetching behavior remains permissioned.

Acceptance metrics:

| Metric | Target |
| --- | --- |
| Automation findings with actionable owner | 90% |
| False-positive rate | Reviewed monthly |
| Silent semantic mutation | 0 |
| Human approval for high-risk actions | 100% |

### Phase 7: Delivery And Productivity Telemetry

Timebox: start lightweight collection immediately; mature over 2-3 months.

Goal: pair agent speed with stability and review load.

Track:

- change lead time from task-card creation to archive/merge;
- deployment or release frequency if releases become formal;
- failed gate recovery time;
- change fail rate or rework rate;
- review findings per task;
- reviewer minutes for agent-authored changes;
- percentage of tasks needing human clarification after start;
- task reopen rate after "complete" claim.

Guidance:

- Do not compare unlike workstreams in one metric.
- Do not set vanity targets such as "more PRs."
- Prefer trend review every two weeks.

## Priority Backlog

| Priority | Work Item | Owner | Output |
| ---: | --- | --- | --- |
| 1 | Create metrics dashboard baseline | architecture steward + agentic toolkit owner | Dashboard page with starting values |
| 2 | Run Step 47 through full lifecycle | session runtime steward | Task card, implementation, tests, archive, roadmap update |
| 3 | Add task-to-archive cross-link checklist | lifecycle owner | Runbook/checklist update and one checked example |
| 4 | Define low-risk chat-only criteria | lifecycle owner | Entry-criteria table |
| 5 | Validate first two or three archives with E001 | review/learning owner | Scored closure notes |
| 6 | Add opt-in task-card/completed-report gates | contract tools steward | Toolkit commands and tests |
| 7 | Add one negative closure eval | learning owner | Eval that fails on false completion or weak evidence |
| 8 | Promote institutional agents 001 and 002 with evals | institutional-agent owner | Template, prompt, example, refusal eval |
| 9 | Add permission/security evidence checklist | third-party/security steward | Completed-task evidence checklist |
| 10 | Start lightweight DORA-style telemetry | lifecycle owner | Biweekly metrics summary |

## Risk Register

| Risk | Why It Matters | Mitigation |
| --- | --- | --- |
| Process vocabulary outpaces real use | More docs can hide that the lifecycle is under-sampled. | Force Step 47 through the loop before adding broad new process. |
| High-risk tasks bypass task cards | Agent work becomes hard to review or resume. | Make human-gate compliance a guardrail metric. |
| Institutional agents become decorative | Role cards without evals create false confidence. | Require examples and refusal evals before promotion. |
| Quality gates become too expensive | Agents may skip verification or batch too much. | Keep focused gates first and full gate at commit boundary. |
| Public benchmark thinking leaks into local acceptance | Benchmark success may not predict GCS correctness. | Local contract tests, fixtures, and review remain authoritative. |
| Experience records inflate into rules | Too many rules make agents brittle. | Require repeat evidence or high severity before skill/doc promotion. |
| Automation overreach | Scheduled agents may mutate important state without context. | Observe-and-propose default; human gates for high-risk actions. |

## 30-Day Success Criteria

By the end of the next 30 days, the agentic-SE program should be able to show:

- Step 47 or another high-risk task completed through task card, plan,
  implementation, evidence, archive, and roadmap update.
- At least one dashboard snapshot with lifecycle, quality, security,
  orchestration, learning, and delivery metrics.
- At least three completed-task reports scored with the closure heuristic.
- One real negative eval added from a review finding or weak closure.
- Task-card and completed-report validation available as opt-in path-scoped
  gates.
- Institutional agents 001 and 002 each have at least one real example and one
  refusal-oriented eval.

## 90-Day Success Criteria

By the end of 90 days:

- High-risk task-card and human-gate compliance is 100%.
- New non-trivial completed-task archives are indexed and cross-linked.
- Repeated workflow mistakes consistently produce experience records.
- At least two promoted lessons include before/after evidence through a skill,
  eval, fixture, test, tool, or architecture update.
- A lightweight review dashboard tracks review findings, gate failures, and
  rework.
- At least one bounded automation observes project drift and proposes action
  without mutating solver semantics.

## Final Recommendation

Do not start by adding more agents. Start by making the existing lifecycle
observable, then prove it on Step 47. GCS already has a strong contract-tested
solver substrate; the agentic-SE priority is now operational maturity:
measured lifecycle closure, independent review, security-aware permissions,
and a disciplined learning loop that changes the repository only when evidence
justifies it.
