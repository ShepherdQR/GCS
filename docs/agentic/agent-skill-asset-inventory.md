# GCS Agent & Skill Asset Inventory

Status: active
Date: 2026-05-28
Purpose: Single-source inventory of every agent and skill, their maturity,
coverage gaps, near-term development targets, and future candidates.

---

## 1. Current Inventory

### 1.1 Institutional Agents (`.claude/agents/`)

14 agents total — 4 institutional (promoted/seed), 9 candidates, 1 README.

| ID | Agent | Maturity | Evidence Package | Score | Domain |
| --- | --- | --- | --- | ---: | --- |
| I001 | [bladesmith-quench-forge](../../.claude/agents/bladesmith-quench-forge.md) | **Promoted** | `001-bladesmith-quench-forge/` — prompt, template, refusal eval, 20+ examples | 10/10 | Experience extraction, reusable lessons |
| I002 | [tailor-stitch-timeline](../../.claude/agents/tailor-stitch-timeline.md) | Practiced, promoted seed | `002-tailor-stitch-timeline/` — prompt, template, refusal eval, 4 timeline examples | 8/10 | Multi-session timeline maintenance |
| I003 | [atelier-steward-calibrate-review](../../.claude/agents/atelier-steward-calibrate-review.md) | Seed | `003-atelier-steward-calibrate-review/` — prompt, template, refusal eval, 1 example | 6/10 | UI/figure convention compliance review |
| I004 | [art-director-frame-judge](../../.claude/agents/art-director-frame-judge.md) | Seed | `004-art-director-frame-judge/` — prompt, template, refusal eval, 2 examples | 6/10 | Visual hierarchy, taste, readability review |
| — | [acceptance-officer](../../.claude/agents/acceptance-officer.md) | Candidate | Prompt written; needs gate template, refusal eval | — | Independent evidence review before task completion |
| — | [bookkeeper](../../.claude/agents/bookkeeper.md) | Candidate | Prompt written; needs budget ledger template | — | Token/cost/value budget tracking |
| — | [collation-officer](../../.claude/agents/collation-officer.md) | Candidate | Prompt written; needs consistency report template | — | Cross-read docs/code/tests for contradictions |
| — | [gardener](../../.claude/agents/gardener.md) | Candidate | Prompt written; needs maintenance record template | — | Small friction, technical debt, batch maintenance |
| — | [night-watch](../../.claude/agents/night-watch.md) | Candidate | Prompt written; full pipeline spec exists; needs real nightly run | — | Nightly CI/quality/task/drift patrol |
| — | [governance-sentinel](../../.claude/agents/governance-sentinel.md) | Candidate | Prompt written; needs review template, refusal eval | — | Permission, PR audit, automation governance |
| — | [demo-producer](../../.claude/agents/demo-producer.md) | Candidate | Prompt written; needs demo-package template, command-transcript standard | — | Product demo creation and refresh |
| — | [benchmark-scout](../../.claude/agents/benchmark-scout.md) | Candidate | Prompt written; needs comparison criteria, source-citation standard | — | External solver comparison, benchmark evaluation |
| — | [release-shepherd](../../.claude/agents/release-shepherd.md) | Candidate | Prompt written; needs release checklist, distribution non-goals | — | Release readiness and packaging |

### 1.2 Agent Maturity Pipeline

```
Candidate (9)  ──→  Seed (2)  ──→  Practiced (1)  ──→  Promoted (1)  ──→  Institutional (0)
                   I003, I004       I002               I001
```

**Bottleneck**: 9 agents at Candidate with no clear promotion path. Only 2 have
reached Seed. No agent has reached Institutional.

### 1.3 Skills (`.claude/skills/`)

25 skills total. 20 have `.codex/skills/` counterparts; 5 are Claude Code-only.

#### Solver Core (8)

| Skill | Domain | `.codex` counterpart |
| --- | --- | :---: |
| [gcs-architecture-steward](.claude/skills/gcs-architecture-steward/SKILL.md) | Cross-module architecture, dependency direction, vocabulary | yes |
| [gcs-kernel-contract-steward](.claude/skills/gcs-kernel-contract-steward/SKILL.md) | Stable IDs, ModelSnapshot, StateDelta, report codes | yes |
| [gcs-constraint-semantics-steward](.claude/skills/gcs-constraint-semantics-steward/SKILL.md) | Constraint definitions, evaluators, Jacobians, degeneracy | yes |
| [gcs-incidence-structure-steward](.claude/skills/gcs-incidence-structure-steward/SKILL.md) | Hypergraphs, connectivity, articulation, structural projections | yes |
| [gcs-decomposition-planning-steward](.claude/skills/gcs-decomposition-planning-steward/SKILL.md) | Cover plans, boundary projections, solve DAGs | yes |
| [gcs-numeric-engine-steward](.claude/skills/gcs-numeric-engine-steward/SKILL.md) | Local solves, residuals, Jacobians, numeric traces | yes |
| [gcs-diagnostics-certification-steward](.claude/skills/gcs-diagnostics-certification-steward/SKILL.md) | DOF, rank, residual, gluing, obstruction evidence | yes |
| [gcs-session-runtime-steward](.claude/skills/gcs-session-runtime-steward/SKILL.md) | Commands, transactions, history, undo/redo | yes |

#### Boundary and Integration (6)

| Skill | Domain | `.codex` counterpart |
| --- | --- | :---: |
| [gcs-io-adapter-steward](.claude/skills/gcs-io-adapter-steward/SKILL.md) | Scene schemas, serialization, migrations, round-trips | yes |
| [gcs-viewer-bridge-steward](.claude/skills/gcs-viewer-bridge-steward/SKILL.md) | Scene projection, diagnostic overlays, interaction commands | yes |
| [gcs-scene-behavior-steward](.claude/skills/gcs-scene-behavior-steward/SKILL.md) | Scene formats, JSON, history replay, IO compatibility | yes |
| [gcs-cpp-solver-maintainer](.claude/skills/gcs-cpp-solver-maintainer/SKILL.md) | src/gcs, CMake, CLI, C++23 module boundaries | yes |
| [gcs-python-gui-builder](.claude/skills/gcs-python-gui-builder/SKILL.md) | tkinter, matplotlib, viewer bridge, GUI behavior | yes |
| [gcs-scene-generation-engineer](.claude/skills/gcs-scene-generation-engineer/SKILL.md) | Synthetic graphs, validation, repair, fixture promotion | yes |

#### Quality and Governance (6)

| Skill | Domain | `.codex` counterpart |
| --- | --- | :---: |
| [gcs-quality-steward](.claude/skills/gcs-quality-steward/SKILL.md) | Contract tests, CTest, negative fixtures, CI matrix | yes |
| [gcs-contract-tools-steward](.claude/skills/gcs-contract-tools-steward/SKILL.md) | Fixture builders, invariant checkers, golden reports | yes |
| [gcs-third-party-governance-steward](.claude/skills/gcs-third-party-governance-steward/SKILL.md) | Dependencies, licensing, CMake adapters, SBOM | yes |
| [gcs-ui-design-steward](.claude/skills/gcs-ui-design-steward/SKILL.md) | Visual tokens, design-system conventions, visual QA | yes |
| [gcs-ui-qa-steward](.claude/skills/gcs-ui-qa-steward/SKILL.md) | Theme tokens, contrast ratios, GUI static analysis, headless render | **no** — Claude-only |
| [gcs-scientific-figure-producer](.claude/skills/gcs-scientific-figure-producer/SKILL.md) | Figure specs, semantic composition, visual QA | yes |

#### Audit and Demo (3)

| Skill | Domain | `.codex` counterpart |
| --- | --- | :---: |
| [gcs-repository-audit-steward](.claude/skills/gcs-repository-audit-steward/SKILL.md) | File classification, snapshots, diffs, trend reports | **no** — Claude-only |
| [gcs-token-audit-steward](.claude/skills/gcs-token-audit-steward/SKILL.md) | Session token/cost tracking, BEI scoring, trend reports | **no** — Claude-only |
| [gcs-product-demo-steward](.claude/skills/gcs-product-demo-steward/SKILL.md) | Smoke tests, diagnostic classification, replay evidence | **no** — Claude-only |

#### Process (2)

| Skill | Domain | `.codex` counterpart |
| --- | --- | :---: |
| [session-close-orchestrator](.claude/skills/session-close-orchestrator/SKILL.md) | Unified session close pipeline — sequences all close steps | **no** — Claude-only |
| [task-scoped-session-closer](.claude/skills/task-scoped-session-closer/SKILL.md) | Task archives, evidence bundles, commit/push handoff | yes |

---

## 2. Coverage Map

### 2.1 Domain Coverage by Skill

```
Solver architecture    ████████████████  gcs-architecture-steward
Kernel contracts       ████████████████  gcs-kernel-contract-steward
Constraint semantics   ████████████████  gcs-constraint-semantics-steward
Incidence structure    ████████████████  gcs-incidence-structure-steward
Decomposition planning ████████████████  gcs-decomposition-planning-steward
Numeric engine         ████████████████  gcs-numeric-engine-steward
Diagnostics            ████████████████  gcs-diagnostics-certification-steward
Session runtime        ████████████████  gcs-session-runtime-steward
IO adapters            ████████████████  gcs-io-adapter-steward
Viewer bridge          ████████████████  gcs-viewer-bridge-steward
Scene behavior         ████████████████  gcs-scene-behavior-steward
C++ solver             ████████████████  gcs-cpp-solver-maintainer
Python GUI             ████████████████  gcs-python-gui-builder
Scene generation       ████████████████  gcs-scene-generation-engineer
Quality gates          ████████████████  gcs-quality-steward
Contract tools         ████████████████  gcs-contract-tools-steward
Third-party gov        ████████████████  gcs-third-party-governance-steward
UI design              ████████████████  gcs-ui-design-steward + gcs-ui-qa-steward
Scientific figures     ████████████████  gcs-scientific-figure-producer
Repository audit       ████████████████  gcs-repository-audit-steward
Token audit            ████████████████  gcs-token-audit-steward
Product demo           ████████████████  gcs-product-demo-steward
Session close          ████████████████  session-close-orchestrator + task-scoped-session-closer
```

### 2.2 Thin Spots (skill coverage exists but is weak)

| Domain | Current state | Gap |
| --- | --- | --- |
| **Benchmark execution** | `benchmark-scout` agent is candidate; architecture plan exists at `docs/architecture/97-*.md`; 2 microbenchmarks seeded | No active skill to run, curate, or promote benchmarks into fixtures |
| **Release management** | `release-shepherd` agent is candidate; `release-readiness-checklist.md` exists | No active skill; R1 shipped without institutional release owner |
| **Git/branch governance** | Candidate skill `git-session-branch-steward` exists in `docs/agentic/experience/003-*/` but never promoted to `.claude/skills/` | Skill is prototyped but inactive; agent is prototyped but not in `.claude/agents/` |
| **CI/CD operations** | `gcs-quality-steward` covers CI matrix; `night-watch` covers nightly patrol | No dedicated skill for CI troubleshooting, pipeline maintenance, or platform-specific build issues |
| **Governance enforcement** | `governance-sentinel` is candidate; 8 eval candidates defined (E-GOV-001 through 008), most at L1-L2 | No agent at seed+; no eval at L4+ (default gate) |

### 2.3 Agent-to-Skill Cross-Reference

| Agent | Primary skills it works with |
| --- | --- |
| I001 Bladesmith | task-scoped-session-closer, session-close-orchestrator, gcs-token-audit-steward |
| I002 Tailor | task-scoped-session-closer, gcs-repository-audit-steward |
| I003 Atelier Steward | gcs-ui-design-steward, gcs-scientific-figure-producer, gcs-ui-qa-steward |
| I004 Art Director | gcs-scientific-figure-producer, gcs-ui-design-steward |
| Acceptance Officer | task-scoped-session-closer, gcs-quality-steward |
| Bookkeeper | gcs-token-audit-steward, gcs-repository-audit-steward |
| Collation Officer | gcs-architecture-steward, all solver-core skills |
| Gardener | gcs-repository-audit-steward, all skills (cross-cutting) |
| Night-Watch | gcs-quality-steward, gcs-repository-audit-steward, gcs-scene-generation-engineer |
| Governance Sentinel | gcs-third-party-governance-steward |
| Demo Producer | gcs-product-demo-steward, gcs-scientific-figure-producer |
| Benchmark Scout | (no active benchmark skill — see gap) |
| Release Shepherd | gcs-product-demo-steward, gcs-quality-steward |

### 2.4 Operating-Layer Coverage

From `agentic-organization-operating-map.md`:

| Layer | Owner (skill or agent) | Coverage |
| --- | --- | :---: |
| Intent and portfolio | gcs-architecture-steward | Covered |
| Workspace boundary | task-scoped-session-closer | Covered |
| Context and memory | I002 Tailor, gcs-repository-audit-steward | Covered |
| Execution roles | 20 domain steward skills | Covered |
| Evidence gates | gcs-quality-steward | Covered |
| Governance and permissions | governance-sentinel (candidate) | **Thin** |
| Review and archive | task-scoped-session-closer, session-close-orchestrator | Covered |
| Learning and promotion | I001 Bladesmith, I002 Tailor | Covered |

---

## 3. Near-Term Development Candidates

These are the items that should be developed **next**, ranked by urgency.
Each has an existing prototype, plan, or clear trigger.

### 3.1 Promote git-session-branch-steward to Active Skill

**Status**: Candidate skill exists at `docs/agentic/experience/003-git-session-branch-governance/skills/git-session-branch-steward/SKILL.md`. Candidate agent exists at `docs/agentic/experience/003-git-session-branch-governance/agents/git-session-steward.md`.

**Why now**: The lifecycle runbook (Step 0) already requires workspace/branch decisions. The permission policy classifies `git_write` as human-authorized. A dedicated skill would prevent the most common agentic governance failure mode (pushing unrelated dirty files).

**What's needed**:
- Move `SKILL.md` to `.claude/skills/git-session-branch-steward/SKILL.md`
- Move agent to `.claude/agents/git-session-steward.md` (or merge with existing governance-sentinel)
- Write `docs/agentic/git-session-registry.md`
- Create refusal eval: refuse to push when unrelated ahead commits exist on master

**Estimated effort**: 1 session.

### 3.2 Promote I003 Atelier Steward to Practiced

**Status**: Seed with 1 real example (Figure 72 convention-fit review). Score 6/10.

**Why now**: The UI design system execution plan (`docs/architecture/76-ui-design-system-execution-plan.md`) and aesthetic plan documentation are active. Multiple UI changes are in flight. The Atelier Steward should review at least 2 more rendered artifacts before promotion.

**What's needed**:
- 2 more real convention-fit reviews on live rendered UI or figures
- Each review must name the governing convention and step

**Estimated effort**: 2-3 sessions (accumulate organically).

### 3.3 Promote I004 Art Director to Practiced

**Status**: Seed with 2 examples (Figure 72 reviews). Score 6/10.

**Why now**: Same rationale as I003. Visual artifacts are being produced. The Art Director needs more rendered-artifact evidence.

**What's needed**:
- 1-2 more visual reviews on live rendered surfaces (not source text)
- Strengthen refusal behavior evidence

**Estimated effort**: 2-3 sessions (accumulate organically).

### 3.4 Develop Benchmark Skill

**Status**: No skill exists. `benchmark-scout` agent is candidate. Architecture plan at `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md`. Benchmarks seeded at `docs/architecture/benchmarks/`.

**Why now**: The architecture plan is written. External solver comparison is part of the narrative map (Line 4: External Evidence). Without a skill, benchmarks will be created ad hoc with no consistency.

**What's needed**:
- Create `gcs-benchmark-steward` skill at `.claude/skills/`
- Define benchmark fixture format, reproducibility standard, and comparison criteria
- Promote `benchmark-scout` agent to seed with one real benchmark evaluation

**Estimated effort**: 2 sessions.

### 3.5 Advance Night-Watch to Seed

**Status**: Candidate with full pipeline spec. No real nightly run yet.

**Why now**: The pipeline specification is detailed. Repository health checks would catch drift before it accumulates. Night-Watch is the natural consumer of several existing tools (validate-docs, validate-inventory, check-dependencies).

**What's needed**:
- 1 real nightly run with findings
- Dated run directory at `docs/agentic/nightly-runs/YYYY-MM-DD/`
- Refusal eval: refuse to commit/push/merge from night-watch role

**Estimated effort**: 1 session for first calibration run.

### 3.6 Advance Acceptance Officer to Seed

**Status**: Candidate with prompt. No gate template or refusal eval.

**Why now**: Task closure quality varies. An independent evidence review before archive would prevent the most common failure mode (evidence-free completion claims).

**What's needed**:
- Gate template with accept/accept_with_notes/return_for_evidence/return_for_scope decisions
- Refusal eval: refuse evidence-free acceptance
- 1 real acceptance review on a completed task

**Estimated effort**: 1-2 sessions.

---

## 4. Future Consideration

These are items worth considering but not urgent. They lack prototypes, plans,
or clear triggers, or the current approach works well enough.

### 4.1 Agent Candidates (from institutional-agents README candidate table)

These nine roles were named in the original candidate table but have not been
created as agent definition files. Some overlap with existing candidates.

| Role | Overlap with existing | Recommendation |
| --- | --- | --- |
| `舵手: 分派-收束` (Helmsman/Orchestrator) | Claude Code built-in routing handles this implicitly | **Defer** — the platform provides orchestration |
| `磨镜师: 评估-校准` (Evaluator-Calibrator) | No overlap; would own eval rubrics and scoring | **Consider** after governance evals reach L3+ |
| `铸印官: 终态-反推` (Working-Backwards) | No overlap; would write PR/FAQ briefs before implementation | **Consider** for high-risk solver tasks |
| `复盘官: 归因-修复` (Postmortem Analyst) | No overlap; would handle blameless postmortems | **Consider** after first real regression or near-miss |
| `策展人: 采撷-编目` (Curator) | Overlaps with collation-officer (candidate) | **Defer** — collation-officer should be promoted first |
| `铺路官: 环境-验真` (Path-Paver) | No overlap; would ensure build/test reproducibility | **Consider** if environment issues become recurring friction |
| `法度官: 护栏-授权` (Guardian/Guardrail) | Overlaps with governance-sentinel (candidate) | **Defer** — let governance-sentinel mature first |
| `验收官: 举证-放行` (Acceptance Officer) | **Already created** as acceptance-officer | Advance to seed (see §3.6) |
| `值夜官: 巡检-告警` (Night-Watch) | **Already created** as night-watch | Advance to seed (see §3.5) |

### 4.2 Skill Candidates

| Candidate skill | Rationale | When to create |
| --- | --- | --- |
| `gcs-benchmark-steward` | Benchmark execution, comparison criteria, reproducibility standard | When benchmark-scout agent reaches seed (see §3.4) |
| `gcs-release-steward` | Release checklist, evidence gate mapping, distribution packaging | When release-shepherd agent reaches seed |
| `gcs-ci-operations-steward` | CI troubleshooting, pipeline maintenance, platform-specific builds | If CI failures become recurring friction |
| `gcs-docs-quality-steward` | Documentation consistency, stale-reference detection, cross-reading automation | If collation-officer identifies systematic doc drift |

### 4.3 Pipeline Maturity Targets

| Agent | Current | 3-month target | 6-month target |
| --- | --- | --- | --- |
| I001 Bladesmith | Promoted | Institutional | Institutional (maintain review cadence) |
| I002 Tailor | Practiced, promoted seed | Promoted | Institutional |
| I003 Atelier Steward | Seed | Practiced | Promoted |
| I004 Art Director | Seed | Practiced | Promoted |
| Night-Watch | Candidate | Seed | Practiced |
| Acceptance Officer | Candidate | Seed | Practiced |
| Governance Sentinel | Candidate | Seed | Seed |
| Benchmark Scout | Candidate | Seed | Seed |

### 4.4 Governance Eval Pipeline

8 eval candidates defined (E-GOV-001 through 008). None at L4+.

**Target**: Promote E-GOV-001 (unrelated dirty file staging) and E-GOV-003
(evidence-free completion) to L3 (validator candidate) within 3 months. These
are the highest-signal, lowest-noise governance checks.

---

## 5. Completeness Assessment

### 5.1 What This Inventory Covers

- Every agent in `.claude/agents/` (14 + README)
- Every skill in `.claude/skills/` (25)
- Every candidate role in the institutional-agents README candidate table
- Prototype skills/agents in `docs/agentic/experience/`
- Cross-reference with the operating map, roadmap, permission policy, and governance eval roadmap
- Module agents from `docs/architecture/62-module-agents.md`

### 5.2 What This Inventory Does NOT Cover

- **Built-in Claude Code agents** (Explore, Plan, general-purpose, claude-code-guide, statusline-setup) — these are platform-provided, not project-owned
- **External skill plugins** (`anthropic-skills:consolidate-memory`, `anthropic-skills:setup-cowork`) — these are third-party to GCS
- **`.codex/skills/` agents** (`agents/openai.yaml` files) — these are Codex/OpenAI format interface files, not Claude Code agents
- **Module agent definitions in `62-module-agents.md`** — these are architecture design documents, not executable agent definitions. Each has a corresponding skill. The mapping is 1:1 (module agent → steward skill)

### 5.3 Items That Should Be Added to This Inventory

1. **git-session-branch-steward skill** — prototype exists, should be promoted and added
2. **git-session-steward agent** — prototype exists, should be promoted and added
3. **CI operations coverage** — currently split across quality-steward and night-watch; may need dedicated ownership if friction accumulates
4. **Benchmark execution coverage** — plan exists, skill needed

### 5.4 Items That Should Be Removed or Merged

1. **Candidate role `舵手: 分派-收束` (Helmsman)** — Claude Code's native agent routing fills this role. Remove from candidate table or explicitly mark as "platform-provided, not GCS-owned."
2. **Candidate role `策展人: 采撷-编目` (Curator)** — functionally overlaps with collation-officer. Merge or defer until collation-officer reaches seed.
3. **Candidate role `法度官: 护栏-授权` (Guardian)** — functionally overlaps with governance-sentinel. Merge or defer.

---

## 6. Health Indicators

| Indicator | Current | Target | Status |
| --- | --- | --- | --- |
| Active skills with valid frontmatter | 25/25 | 25 | Clean |
| Agent maturity consistency (registry vs frontmatter) | 13/14 aligned | 14 | I001 fixed 2026-05-28 |
| `.codex` ↔ `.claude` skill parity | 20 shared, 5 Claude-only | Documented divergence | Acceptable |
| Agents at Candidate without promotion path | 9 | Define path for top 3 | Needs attention |
| Governance evals at L3+ | 0/8 | 2 by 2026-08 | Needs attention |
| Institutional agents (top maturity tier) | 0 | 1 by 2026-08 | On track (I001 closest) |
| Orphan prototype skills in experience/ | 2 (git-session-branch-steward, task-scoped-session-closer v1) | 0 | git-session-branch-steward needs promotion |
| Skills without corresponding agent | 17 | Intentional — most steward skills don't need institutional agents | Acceptable |
| Agents without corresponding skill | 5 (acceptance-officer, bookkeeper, collation-officer, gardener, night-watch) | Acceptable for process agents | Monitor |

---

## 7. Review Cadence

Update this inventory when:
- A new agent or skill is created, promoted, or retired
- A candidate agent reaches seed (add to registry scorecard)
- An institutional agent reaches a new maturity tier
- A prototype skill in `docs/agentic/experience/` is promoted to `.claude/skills/`
- The agentic organization map changes
- Quarterly (next review: 2026-08-28)

---

## 8. Agent Trigger Registry and Exercise Log

Purpose: Track when each agent was last exercised, what condition triggers its
invocation, and how many times the trigger fired without the agent being
invoked. This closes the loop between agent definitions and operating behavior.

### 8.1 Registry

| Agent ID | Agent Name | Current Maturity | Last Exercised | Next Expected Trigger | Missed Invocations |
|----------|------------|-----------------|----------------|-----------------------|-------------------:|
| I001 | bladesmith-quench-forge | Promoted | 2026-05-30 (active) | Post-session or post-task closure | 0 |
| I002 | tailor-stitch-timeline | Practiced | 2026-05-30 (stitched solver Steps 52-55 and scene generation timelines) | Every 3-5 related sessions | 0 |
| I003 | atelier-steward-calibrate-review | Seed | 2026-05-25 (Figure 72 review) | UI or figure change with design-system implications | 0 |
| I004 | art-director-frame-judge | Seed | 2026-05-26 (Figure 72 P7 review) | Visual artifact needs independent hierarchy/taste review | 0 |
| I005 | acceptance-officer | Candidate | Never | Non-trivial task claims completion | 0 |
| I006 | bookkeeper | Candidate | Never | Cost-benefit question or session efficiency analysis | 0 |
| I007 | collation-officer | Candidate | Never | Doc-code-test divergence suspected | 0 |
| I008 | gardener | Candidate | Never | Small frictions accumulate; stale references found | 0 |
| -- | night-watch | Candidate | 2026-05-30 (calibration in progress) | Nightly or milestone-based patrol | 0 |
| -- | governance-sentinel | Candidate | Never | Permission/PR audit/automation claims changing | 0 |
| -- | demo-producer | Candidate | Never | Demo package created or refreshed | 0 |
| -- | benchmark-scout | Candidate | Never | External solver comparison or benchmark candidate proposed | 0 |
| -- | release-shepherd | Candidate | Never | Release readiness or packaging docs become active | 0 |
| -- | git-session-steward | Seed (promoted to skill 2026-05-28) | 2026-05-28 (promoted to skill) | Before mutating git operations | 0 |

### 8.2 Missed Invocation Accounting

After each non-trivial task closure, scan the **Next Expected Trigger** column.
Any agent whose trigger condition was met but was NOT invoked during that task
counts as one **Missed Invocation**. Reset the counter to zero after the agent
is exercised.

A missed invocation is not a failure -- it is a signal. Repeated missed
invocations (3+) for an agent suggest one of:

- The trigger description is too broad or ambiguous and needs refinement.
- The agent is not trusted yet (low maturity, no evidence) and the trigger
  fires are being ignored intentionally.
- The agent's scope overlaps with a more active agent and the division of labor
  needs clarification.

The **Missed Invocations** column should be updated at each quarterly inventory
review (see Section 7), or sooner when an agent is exercised and its counter
resets.

### 8.3 Notes

- I001 (bladesmith) and I002 (tailor) are the most exercised agents and form
  the core experience-extraction pipeline. Their triggers fire on every session.
- I003, I004, and git-session-steward are the only Seed+ agents exercised in
  the past week. All three have concrete trigger conditions tied to specific
  artifact types (UI figures, git operations).
- Five candidates (I005-I008, governance-sentinel, demo-producer, benchmark-scout,
  release-shepherd) have never been exercised. Their trigger conditions are
  well-defined but have not yet occurred, or they occurred before the agent
  definition existed. The first exercise for each should produce an initial
  evidence example and an updated last-exercised date.
- Night-watch is being calibrated in the current session (2026-05-30). Its
  counter will start at zero after first calibration run completes.

---

## Appendix A: File Index

| What | Where |
| --- | --- |
| Agent definitions | `.claude/agents/*.md` |
| Skill definitions | `.claude/skills/*/SKILL.md` |
| Agent registry and scorecard | `docs/agentic/institutional-agent-registry-and-scorecard.md` |
| Institutional agent docs | `docs/agentic/institutional-agents/` |
| Agentic organization map | `docs/agentic/agentic-organization-operating-map.md` |
| Lifecycle runbook | `docs/agentic/lifecycle-runbook.md` |
| PDCA roadmap | `docs/agentic/agile-pdca-roadmap.md` |
| Governance eval roadmap | `docs/agentic/governance-eval-roadmap.md` |
| Permission policy | `docs/agentic/agent-permission-policy.md` |
| Module agent definitions | `docs/architecture/62-module-agents.md` |
| Experience prototypes | `docs/agentic/experience/` |
| Benchmark architecture | `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md` |
| Product demo ladder | `docs/product/gcs-demo-ladder.md` |
| Release checklist | `docs/product/release-readiness-checklist.md` |
| `.codex` skill originals | `.codex/skills/*/SKILL.md` |

## Appendix B: Agent-to-Skill Mapping (Full)

See §2.3 for the primary mapping. The full matrix:

```
                        arch kernel constr incide decomp numeri diagno sessio io vi
I001 Bladesmith          .    .      .      .      .      .      .      .      .  .
I002 Tailor              .    .      .      .      .      .      .      .      .  .
I003 Atelier Steward     .    .      .      .      .      .      .      .      .  .
I004 Art Director        .    .      .      .      .      .      .      .      .  .
Acceptance Officer       .    .      .      .      .      .      .      .      .  .
Bookkeeper               .    .      .      .      .      .      .      .      .  .
Collation Officer        X    X      X      X      X      X      X      X      X  X
Gardener                 X    X      X      X      X      X      X      X      X  X
Night-Watch              .    .      .      .      .      .      .      .      .  .
Governance Sentinel      .    .      .      .      .      .      .      .      .  .
Demo Producer            .    .      .      .      .      .      .      .      .  .
Benchmark Scout          .    .      .      .      .      .      .      .      .  .
Release Shepherd         .    .      .      .      .      .      .      .      .  .

                        viewer scene cpp   py    scenegen qual  ctool 3rdpy ui
I001 Bladesmith          .      .     .     .     .        .     .     .     .
I002 Tailor              .      .     .     .     .        .     .     .     .
I003 Atelier Steward     .      .     .     .     .        .     .     .     X
I004 Art Director        .      .     .     .     .        .     .     .     X
Acceptance Officer       .      .     .     .     .        X     .     .     .
Bookkeeper               .      .     .     .     .        .     .     .     .
Collation Officer        X      X     X     X     X        X     X     X     X
Gardener                 X      X     X     X     X        X     X     X     X
Night-Watch              .      .     .     .     X        X     .     .     .
Governance Sentinel      .      .     .     .     .        .     .     X     .
Demo Producer            .      .     .     .     .        .     .     .     .
Benchmark Scout          .      .     .     .     .        .     .     .     .
Release Shepherd         .      .     .     .     .        X     .     .     .

                        uiqa  fig   repo  token demo  close orch
I001 Bladesmith          .     .     .     X     .     X     X
I002 Tailor              .     .     X     .     .     X     .
I003 Atelier Steward     X     X     .     .     .     .     .
I004 Art Director        .     X     .     .     .     .     .
Acceptance Officer       .     .     .     .     .     X     .
Bookkeeper               .     .     X     X     .     .     .
Collation Officer        .     .     X     .     .     .     .
Gardener                 .     .     X     .     .     .     .
Night-Watch              .     .     X     .     .     .     .
Governance Sentinel      .     .     .     .     .     .     .
Demo Producer            .     .     .     .     X     .     .
Benchmark Scout          .     .     .     .     .     .     .
Release Shepherd         .     .     .     .     X     .     .

X = primary collaboration; . = no direct relationship
```
