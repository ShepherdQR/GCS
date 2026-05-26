# GCS Narrative-Line Audit And Development Plan

Date: 2026-05-26
Scope: Current GCS repository narrative completeness, based on local
architecture docs, agentic operating-layer docs, prior 2026-05-24 agentic-SE
reports, and the 2026-05-26 external AI organization research bundle.

## Executive Summary

GCS has a strong internal engineering narrative:

- the mathematical problem is framed as local-to-global geometric constraint
  solving;
- the target architecture separates kernel, constraint catalog, incidence
  graph, planner, diagnostics, numeric engine, session runtime, IO, and viewer;
- the repo has a serious agentic-SE operating layer with task cards,
  completed-task archives, quality gates, institutional agents, and experience
  records;
- evidence culture is unusually strong: contract tests, fixture corpora,
  replay evidence, visual QA, repository audit, and quality-gate docs all
  exist.

The gaps are not primarily "more docs." The gaps are integration and outward
narrative:

1. GCS needs a single narrative map connecting solver science, product/user
   value, agentic-SE operating model, governance, metrics, and public
   demonstration.
2. The product/user narrative is weaker than the internal architecture
   narrative.
3. The metrics and telemetry narrative is still emerging.
4. The agentic organization story exists in many artifacts, but it is not yet
   summarized as a coherent project identity.
5. Release, onboarding, distribution, and external benchmark/comparison
   narratives remain underdeveloped.

## Source Register

| Local source | Used for | Confidence |
| --- | --- | --- |
| `README.md` | Repository layout, build, testing, viewer entry points | High |
| `docs/current-model.md` | Current model, text format, module boundaries | High |
| `docs/architecture/README.md` | Architecture source of truth and reading order | High |
| `docs/architecture/10-system/current-to-target-map.md` | Current-to-target module mapping | High |
| `docs/architecture/66-implementation-execution-roadmap.md` | Implementation step sequence and next solver work | High |
| `docs/architecture/67-current-progress-and-next-steps.md` | Progress and near-term architectural context | Medium |
| `docs/architecture/68-agentic-se-lifecycle-self-evolution.md` | Full-lifecycle agentic-SE design | High |
| `docs/architecture/69-ci-ready-quality-gates.md` | Quality-gate contract | High |
| `docs/agentic/README.md` | Agentic operating-layer file map and boundaries | High |
| `docs/agentic/lifecycle-runbook.md` | Request-to-push lifecycle | High |
| `docs/agentic/agile-pdca-roadmap.md` | Agentic-SE phase progress and PDCA queue | High |
| `docs/agentic/ai-governance-next-actions.md` | PR audit and diagnostics governance roadmap | High |
| `docs/research/20260524/agentic-se-dimensions-metrics-research-report.md` | Prior dimension model | High |
| `docs/research/20260524/agentic-se-gcs-progress-and-development-plan.md` | Prior GCS agentic-SE maturity assessment | High |

## Current Narrative Lines

### 1. Mathematical And Scientific Solver Narrative

Status: strong but internally focused.

Current story:

- GCS is not merely a UI or least-squares problem.
- It is a layered local-to-global problem over semantic model, incidence
  structure, nonlinear equations, planning, numeric solving, diagnostics, and
  gluing.
- Solver output should include coordinates plus certificate-like evidence:
  rank, residual, conditioning, degrees of freedom, conflicts, redundancy, and
  obstruction reports.

Evidence:

- `docs/architecture/README.md`
- `docs/architecture/00-foundations/`
- `docs/architecture/20-solver-pipeline/`
- `docs/architecture/30-contracts/`

Gap:

- The research/product "why this matters" narrative is less visible than the
  internal architecture narrative.

Development plan:

- Add a concise "GCS scientific thesis" page or section that explains why
  certificate-like solver evidence matters for users, not only modules.
- Connect local-to-global semantics to demonstrable scenarios and user-facing
  diagnostics.

### 2. Module Contract Architecture Narrative

Status: very strong.

Current story:

- The repository has target vocabulary: `kernel`, `constraint_catalog`,
  `incidence_graph`, `decomposition_planner`, `diagnostics`,
  `numeric_engine`, `session_runtime`, `io_adapters`, and `viewer_bridge`.
- Lower mathematical layers must not depend on viewer, IO, CLI, process launch,
  or agentic infrastructure.
- Public behavior should be expressed as stable IDs, snapshots, proposed
  deltas, reports, and contract tests.

Evidence:

- `docs/architecture/README.md`
- `docs/architecture/10-system/current-to-target-map.md`
- `.codex/skills/gcs-*-steward/SKILL.md`

Gap:

- Some prototype names and implementation details may still trail the target
  vocabulary.

Development plan:

- Keep migration debt visible through current-to-target mapping.
- For every new feature, require owner, target module, public report surface,
  and contract-test evidence.

### 3. Implementation Roadmap Narrative

Status: strong but large and difficult to absorb.

Current story:

- The implementation roadmap records many step milestones and planned next
  solver capabilities, including replay evidence, fixture library gate,
  damped numeric solve, JSON scene IO, diagnostics conflict/redundancy, and
  decomposition planner work.

Evidence:

- `docs/architecture/66-implementation-execution-roadmap.md`
- `docs/architecture/71-step-1-40-execution-report.md`
- `docs/architecture/79-step-41-46-execution-report.md`
- `docs/architecture/80-step-1-46-execution-overview.md`

Gap:

- The roadmap is rich but not easily consumable as a strategic story. A future
  agent can follow it, but a new executive or technical reviewer may not see
  the main arcs quickly.

Development plan:

- Create a one-page "roadmap arcs" summary:
  1. kernel/contracts,
  2. graph/planning,
  3. diagnostics/numeric,
  4. runtime/replay,
  5. IO/fixtures,
  6. viewer/evidence workbench,
  7. agentic-SE governance.
- Keep detailed steps in the existing roadmap.

### 4. Fixture, Scene, And Counterexample Narrative

Status: strong and strategically valuable.

Current story:

- GCS treats generated scenes, verification fixtures, milestone scenes, and
  counterexamples as evidence assets.
- Failing-but-interesting scenes can be preserved as counterexamples rather
  than discarded.
- Scene generation tools support exploration, repair, promotion packages, and
  fixture library gates.

Evidence:

- `tools/scene_generation/`
- `fixtures/scene/generated/`
- `fixtures/scene/milestone/`
- `fixtures/scene/counterexamples/`
- `docs/research/graph-generation/study-note.md`

Gap:

- The fixture corpus could be narrated as a "scientific testbench" for both
  solver progress and agentic process, not only as files.

Development plan:

- Add corpus maturity levels: smoke, verification, generated, milestone,
  counterexample, showcase, benchmark candidate.
- Tie each corpus level to acceptance checks and report evidence.

### 5. Runtime, History, And Replay Evidence Narrative

Status: strong and becoming a differentiator.

Current story:

- The session runtime owns commands, behavior modes, transactions, history,
  undo/redo, replay, and post-commit verification.
- Replay evidence creates an audit trail for solver behavior and viewer
  projection.

Evidence:

- `src/gcs/session_runtime/`
- `python/gcs_viz/event_store.py`
- `docs/agentic/agile-pdca-roadmap.md` Step 47-50 history
- completed-task archives around runtime replay evidence.

Gap:

- The narrative could more explicitly connect replay evidence to external AI
  organization practice: auditability, observability, and agent trust.

Development plan:

- Present replay evidence as the GCS equivalent of agentic organization audit
  logs.
- Use it as a public demo: user action, runtime command, report evidence,
  viewer projection, saved artifact.

### 6. Agentic-SE Operating Layer Narrative

Status: very strong internally.

Current story:

- `docs/agentic` is the executable operating layer for task cards, plans,
  evidence, traces, evals, lifecycle, governance, permissions, PR audits,
  nightly diagnostics, institutional agents, and completed-task closure.
- The solver core must remain free of agentic infrastructure.

Evidence:

- `docs/agentic/README.md`
- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/task-to-archive-checklist.md`
- `docs/agentic/agile-pdca-roadmap.md`
- `docs/agentic/institutional-agents/`

Gap:

- The layer is extensive; its strategic purpose should be summarized as a
  compact "GCS as agentic organization" narrative.

Development plan:

- Add an "agentic organization map" that links task lifecycle, skills,
  institutional agents, quality gates, and completed archives.
- Keep the current detailed docs as operational manuals.

### 7. Quality Gate And Evidence Narrative

Status: strong.

Current story:

- `run-quality-gates` wraps docs validation, inventory validation, skill
  validation, dependency checks, build, CTest, Python tests, CLI smokes,
  fixture checks, and optional agentic artifact gates.
- Broad legacy validation is intentionally not default without migration
  policy.

Evidence:

- `docs/architecture/69-ci-ready-quality-gates.md`
- `scripts/run_quality_gates.*`
- `tools/agentic_design/agentic_toolkit.py`
- `tests/contracts/`
- `tests/tools/`

Gap:

- Gate health is not yet a visible dashboard with trend metrics.

Development plan:

- Add a lightweight metrics dashboard:
  gate pass rate, discovered tests, focused-test usage, validation failures,
  skipped checks, task-card coverage, archive scores, review findings.

### 8. UI, Viewer, And Scientific Figure Narrative

Status: strong but split across many artifacts.

Current story:

- The local Python viewer is evolving toward a Solver Evidence Workbench.
- The project has UI tokens, visual QA tools, screenshot baselines,
  architecture figures, and scientific figure production workflows.

Evidence:

- `python/gcs_viz/`
- `docs/architecture/70-visualization/`
- `docs/architecture/72-ui-aesthetic-roadmap.md`
- `docs/architecture/92-gcs-ui-architecture-adjustment-record.md`
- `tools/ui_qa/`
- `tools/architecture_visualization/`

Gap:

- The UI story should be tied more directly to solver evidence and user
  decision support, not only aesthetic and figure production.

Development plan:

- Frame the viewer as "evidence-first interaction": geometry, constraints,
  diagnostics, replay, report, and export.
- Keep visual polish subordinate to evidence clarity.

### 9. Institutional-Agent And Learning Narrative

Status: promising, but still maturing.

Current story:

- Institutional agents such as Bladesmith, Tailor, Atelier Steward, and Art
  Director are standing roles for memory, chronology, convention fit, and
  visual review.
- Experience records can become promoted skills, tools, evals, or templates.

Evidence:

- `docs/agentic/institutional-agents/`
- `docs/agentic/experience/`
- completed-task archives with forging/timeline examples.

Gap:

- These agents risk being perceived as poetic role cards unless their outputs
  are tied to evals, refusal behavior, examples, and measurable reuse.

Development plan:

- Maintain "promoted only with template, example, refusal eval, and boundary"
  policy.
- Track whether institutional-agent outputs reduce recurrence of mistakes.

### 10. Git, Worktree, And PR Governance Narrative

Status: strong and practical.

Current story:

- Local checkout, worktree, branch, PR, and human governance boundaries are
  explicit.
- Machine-readable PR audit and nightly diagnostics are part of active
  governance.

Evidence:

- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/git-session-branch-plan-2026-05-26.md`
- `docs/agentic/pr-audit-governance.md`
- `docs/agentic/agent-permission-policy.md`
- `tools/repository_audit/`

Gap:

- Governance is strong for repo operations. It is less explicitly connected to
  broader AI organization security patterns such as data classification and the
  lethal trifecta.

Development plan:

- Add an agent-permission threat matrix:
  private data, untrusted content, outbound communication, filesystem writes,
  branch actions, dependency/network actions.

### 11. Product, User, And Market Narrative

Status: underdeveloped.

Current story:

- The repo states what GCS is and how to build/test/view it.
- It does not yet foreground target users, use cases, product promises, or
  external positioning.

Evidence:

- `README.md`
- `docs/current-model.md`
- UI workbench architecture docs.

Gap:

- A future collaborator can understand the architecture faster than they can
  understand who the system is for.

Development plan:

- Add a product/user brief:
  target users, jobs-to-be-done, core workflows, must-not-fail properties,
  demo scenarios, and non-goals.
- Consider separate narratives for:
  research prototype,
  local solver workbench,
  educational geometry/constraint tool,
  agentic-SE showcase.

### 12. Release, Packaging, And Onboarding Narrative

Status: partial.

Current story:

- Build, testing, and Python viewer instructions exist.
- There are scripts and quality gates.

Gap:

- There is not yet a polished "new contributor path" or "release path."
- The repo has many advanced artifacts, which can overwhelm first-time readers.

Development plan:

- Add a 20-minute onboarding path:
  build, run CLI smoke, open viewer, inspect one fixture, run one focused test,
  read one architecture map.
- Add release readiness milestones:
  local demo, fixture corpus, CLI contract, viewer workbench, docs bundle.

## Completeness Matrix

| Narrative line | Current completeness | Main next move |
| --- | --- | --- |
| Scientific solver thesis | Strong | Add user-facing why and demo connection |
| Module contracts | Very strong | Keep enforcing target vocabulary |
| Implementation roadmap | Strong | Add one-page roadmap arcs |
| Fixture/corpus evidence | Strong | Define corpus maturity ladder |
| Replay/runtime evidence | Strong | Present as auditability differentiator |
| Agentic-SE lifecycle | Very strong | Summarize as one agentic organization map |
| Quality gates | Strong | Add metrics dashboard |
| UI/evidence workbench | Strong but split | Tie UI to solver evidence story |
| Institutional agents | Promising | Require evals and reuse metrics |
| Git/PR governance | Strong | Add permission threat matrix |
| Product/user story | Weak | Add product/user brief |
| Release/onboarding | Partial | Add new-contributor and release paths |
| External benchmark/comparison | Weak | Add comparison corpus and positioning |
| Business/open-source strategy | Weak | Decide audience and distribution model |

## Development Plan

### Phase 0: Narrative Map

Timebox: 1-2 days.

Deliverable:

- `docs/architecture/95-gcs-narrative-map.md` or equivalent.

Contents:

- one-page project story;
- narrative-line matrix;
- source links to existing docs;
- current gaps;
- next documents to create.

Acceptance:

- A new reviewer can understand how solver, evidence, UI, agentic-SE, and
  governance connect without reading 30 files.

### Phase 1: Product/User Brief

Timebox: 2-4 days.

Deliverable:

- `docs/product/gcs-product-brief.md` or `docs/architecture/96-gcs-product-user-brief.md`.

Contents:

- target users;
- jobs-to-be-done;
- first demo workflow;
- must-not-fail properties;
- solver evidence requirements;
- non-goals.

Acceptance:

- Each future UI or solver milestone can say which user workflow it improves.

### Phase 2: Metrics Dashboard

Timebox: 2-5 days.

Deliverable:

- `docs/agentic/metrics-dashboard.md`.

Contents:

- task-card coverage;
- completed archive coverage and score;
- quality-gate pass/fail;
- CTest discovered count;
- focused tests run;
- review findings;
- permission escalations;
- experience promotion decisions.

Acceptance:

- The dashboard can be updated after each non-trivial task in under five
  minutes.

### Phase 3: Capability Ladder And Demo Ladder

Timebox: 1-2 weeks.

Deliverables:

- solver capability ladder;
- fixture corpus maturity ladder;
- public demo ladder.

Contents:

- from basic scene parse to full evidence workbench;
- from smoke fixture to counterexample and benchmark candidate;
- from CLI-only demo to viewer replay/export demo.

Acceptance:

- The roadmap can be read as increasing user-visible capability, not only
  internal steps.

### Phase 4: Agentic Organization Integration

Timebox: 2-4 weeks.

Deliverable:

- a compact GCS agentic organization operating map.

Contents:

- task lifecycle;
- worktree and branch governance;
- institutional-agent registry;
- skills and steward routing;
- quality gates and evals;
- evidence and learning loop;
- permission threat matrix.

Acceptance:

- The project can explain itself as an agentic organization prototype with
  boundaries, not just as a solver repo using AI.

### Phase 5: External Positioning And Onboarding

Timebox: 2-6 weeks.

Deliverables:

- new contributor path;
- demo script;
- comparison/benchmark plan;
- public-facing README upgrade.

Acceptance:

- A technically strong outsider can build, run, inspect evidence, and
  understand the project's thesis in one sitting.

## Priority Backlog

| Priority | Task | Output |
| ---: | --- | --- |
| 1 | Write narrative map | One-page connective tissue across all narrative lines |
| 2 | Write product/user brief | Target users, workflows, promises, non-goals |
| 3 | Add metrics dashboard | Agentic-SE and quality trend baseline |
| 4 | Add permission threat matrix | AI governance tied to concrete capabilities |
| 5 | Define corpus maturity ladder | Fixture story becomes scientific testbench story |
| 6 | Define demo ladder | Solver evidence becomes visible to users |
| 7 | Build onboarding path | New contributor can run and understand GCS quickly |
| 8 | Add external benchmark/comparison plan | GCS positioned against academic/commercial solvers |

## Strategic Recommendation

GCS should now shift from artifact accumulation to narrative compression.

The project has enough depth. The next strategic move is to make the depth
legible:

```text
GCS solves geometric constraints by producing evidence-rich local-to-global
reports, and it builds itself through an evidence-rich agentic organization.
```

That sentence should become the organizing spine. Every future plan should say
which side it advances:

- better solver evidence;
- better user-facing workbench;
- better corpus and benchmarks;
- better agentic organization;
- better governance and learning.

## Open Questions

- Should the product/user brief live under `docs/architecture/` or a new
  `docs/product/` boundary?
- Which audience is primary for the next public-facing narrative: solver
  researchers, CAD/constraint developers, local visualization users, or
  agentic-SE practitioners?
- Should the metrics dashboard become part of the default completed-task
  archive checklist, or remain a periodic review artifact?
