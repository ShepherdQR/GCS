# GCS Multi-Agent System — Baseline Assessment

**Date:** 2026-05-29
**Status:** Baseline Snapshot (pre-development-plan)
**Scope:** Full-system audit of agent infrastructure, dispatch wiring, autonomy capability, and maturity

---

## 1. Current Inventory

### 1.1 Skills (28 total)

| Category | Count | Skills |
|---|---|---|
| **Domain stewards** (solver-scoped) | 16 | kernel-contract, constraint-semantics, incidence-structure, decomposition-planning, numeric-engine, diagnostics-certification, session-runtime, io-adapter, viewer-bridge, scene-behavior, cpp-solver-maintainer, python-gui-builder, quality-steward, contract-tools, benchmark-steward, scene-generation-engineer |
| **Cross-cutting stewards** | 6 | architecture-steward, ui-design-steward, ui-qa-steward, scientific-figure-producer, product-demo-steward, third-party-governance-steward |
| **Process stewards** | 4 | token-audit-steward, repository-audit-steward, git-session-branch-steward, session-close-orchestrator |
| **New (this session)** | 2 | orchestrator (v1.0.0, Seed), task-scoped-session-closer |

### 1.2 Institutional Agents (14 total)

| Maturity | Count | Agents |
|---|---|---|
| **Institutional** | 0 | — |
| **Promoted** | 1 | Bladesmith: Quench-Forge (I001, 10/10) |
| **Practiced** | 1 | Tailor: Stitch-Timeline (I002, 8/10) |
| **Seed** | 3 | Atelier Steward (I003, 6/10), Art Director (I004, 6/10), Acceptance Officer (I005, 5/10) |
| **Candidate** | 9 | Governance Sentinel, Git Session Steward, Demo Producer, Benchmark Scout, Release Shepherd, Night-Watch, Collation Officer, Bookkeeper, Gardener |

### 1.3 Research Documents (this session)

| Document | Content |
|---|---|
| `docs/research/100-agent-systems-capability-analysis.md` | Google 93-agent demo verified; Claude 100-agent feasibility; 7-paper evidence base |
| `docs/research/orchestrator-design-principles.md` | 13 evidence-based design principles from academic papers + GCS audit |
| `docs/research/3-5-agent-orchestration-patterns.md` | 5 concrete orchestration patterns with architectures, benchmarks, failure modes |
| `docs/research/README.md` | Research index with reading paths and key numbers |

---

## 2. Workflow Coverage: The 9-Step Lifecycle

The GCS lifecycle-runbook defines 9 steps. Here is the coverage map:

| Step | Name | Covered By | Gap |
|---|---|---|---|
| 0 | Choose Workspace | lifecycle-runbook.md (prose only) | No automated worktree creation/selection |
| 1 | Classify | task-scoped-session-closer, session-close-orchestrator Step 0 | Classification only at closeout, not at intake |
| 1.5 | Low-Risk Boundary | lifecycle-runbook.md table | Decision table exists; no automated enforcement |
| 2 | Task Card | Both closers, agentic_toolkit.py | Mature CLI tooling; covered |
| 3 | Plan | orchestrator Phase 1 | Covered IF orchestrator invoked; no auto-invocation |
| 4 | Implement | 22 domain steward skills | Covered per-domain; no skill-to-skill dispatch |
| 5 | Verify | agentic_toolkit.py, orchestrator Phase 3 | Quality gates are strongest part |
| 6 | Review | acceptance-officer (Seed, never exercised) | **Gap.** No active review agent |
| 7 | Commit & Push | Both closers, git-session-branch-steward | Covered operatively |
| 8 | Close & Archive | session-close-orchestrator | Most complete step |
| 9 | Learn | session-close-orchestrator Step 3, bladesmith-quench-forge | Theory only; prose-referenced, not auto-dispatched |

**Two critical seams:**
- **Intake gap (Steps 0–2)**: No component auto-classifies and creates task cards at task arrival.
- **Orchestrator gap (Steps 3–5 vs. 7–9)**: The execution orchestrator and closeout orchestrator are not connected.

---

## 3. Dispatch Wiring: The Central Weakness

### 3.1 How Skills Invoke Each Other

| Dispatch Method | Count | % of 28 |
|---|---|---|
| Explicit `Skill()` / `Agent()` tool calls | **1** (orchestrator, new) | 3.6% |
| Prose "also use `<other-skill>`" references | ~10 | 35.7% |
| No cross-references at all | ~16 | 57.1% |
| Prose `Agent` reference (Explore) | 1 (architecture-steward) | 3.6% |

### 3.2 The Poster Child: session-close-orchestrator

Its description claims: "sequences task-scoped-session-closer, bladesmith-quench-forge, bookkeeper, and gcs-token-audit-steward in order."

Its SKILL.md body contains: **zero `Skill()` calls, zero `Agent()` calls.**

The entire "orchestration" is a numbered list for a human to read and manually execute. This is the dispatch gap in microcosm.

### 3.3 Agent-to-Agent Dispatch

All 14 institutional agent definitions are **role descriptions**, not executable dispatch targets. No agent `.md` file contains `Skill()` or `Agent()` calls to invoke other agents. The Collation Officer says "escalate to gcs-architecture-steward" — but this is prose, not a tool call.

---

## 4. Autonomy Capability Assessment

### 4.1 Autonomous Triggering

| Capability | Status |
|---|---|
| Can a skill detect conditions and self-invoke? | **No** |
| Can a skill invoke another skill without human initiation? | **No** (except orchestrator, which itself requires human invocation) |
| Is there scheduled autonomous work? | Night-watch diagnostics only — explicitly forbidden from commit/push |
| Can the system detect its own completion? | **No.** `acceptance-officer` (Seed) designed for this but never used |

### 4.2 Error Recovery

| Capability | Status |
|---|---|
| Retry on failure | Only orchestrator (max 1 retry/worker) |
| Fallback path | None in any skill |
| Escalation to human | None in any skill |
| Circuit breaker | None |
| Degradation mode (continue with reduced scope) | None |
| Timeout handling | Only orchestrator |

### 4.3 Human Gates

The `human_gate_required` field exists in the task card schema. Of ~60 task cards:
- **3 cards** have `human_gate_required: true` (all high-risk runtime/replay work, May 24)
- **57+ cards** have `human_gate_required: false` (including many `risk: high`)

The gate is satisfied by "user explicitly requested executing this step in this session" — meaning the user starting a Claude session IS the gate. There is no mid-workflow pause-and-approve mechanism.

### 4.4 Tool Approval Blocking

No skill addresses tool approval prompts blocking autonomous execution. If a worker hits a permission prompt, orchestration stalls with no recovery path.

---

## 5. Maturity Pipeline

### 5.1 Current State

```
Candidate (9) ──→ Seed (3) ──→ Practiced (1) ──→ Promoted (1) ──→ Institutional (0)
                                    ↑                                   ↑
                               major bottleneck                    target state
```

### 5.2 Bottleneck Analysis

The promotion pipeline from Candidate → Seed is stalled. Nine candidate agents have been defined but none promoted in the observable period. The promotion rule is: "enough real examples to show that future sessions will behave better with the role than without it."

**Root cause**: Candidates are rarely invoked on real tasks, so they never accumulate evidence. This is a chicken-and-egg problem — agents need usage to be promoted, but they are not promoted enough to be trusted for usage.

### 5.3 Scorecard Distribution

| Score | Agents |
|---|---|
| 10/10 | Bladesmith (only agent with complete evidence across all 7 dimensions) |
| 8/10 | Tailor |
| 6/10 | Atelier Steward, Art Director |
| 5/10 | Acceptance Officer |
| Unscored | All 9 candidates |

---

## 6. The Two Orchestrator Problem

The system now has two orchestrators that don't know about each other:

| | orchestrator (new) | session-close-orchestrator (existing) |
|---|---|---|
| **Scope** | Task execution (Steps 3-5) | Session closeout (Steps 7-9) |
| **Dispatch** | Explicit `Skill()`/`Agent()` calls | Prose numbered list |
| **Status** | v1.0.0 Seed (1 day old) | GA (in production use) |
| **Invocation** | Manual: `Skill({skill: "orchestrator"})` | Manual: `Skill({skill: "session-close-orchestrator"})` |
| **Connection** | Does not invoke closeout orchestrator | Does not invoke execution orchestrator |

**The result**: A human must run two separate Skill invocations to complete one task end-to-end. The execution phase and the closeout phase are islands.

---

## 7. Summary: What "Complete Flow / Independent Operation" Requires

For true end-to-end autonomous operation, the following must exist and be wired together:

```
                    ┌──────────────────┐
                    │  Intake Agent     │  ← DOES NOT EXIST
                    │  (auto-classify,  │
                    │   create task card)│
                    └────────┬─────────┘
                             │ Skill() dispatch
                    ┌────────▼─────────┐
                    │  Orchestrator     │  ← EXISTS (v1.0.0 Seed)
                    │  (plan, dispatch, │
                    │   verify, synthesize)│
                    └────────┬─────────┘
                             │ Skill() dispatch
                    ┌────────▼─────────┐
                    │  Domain Skills    │  ← EXIST (22 skills)
                    │  (implement)      │     No dispatch wiring
                    └────────┬─────────┘
                             │ Agent() dispatch
                    ┌────────▼─────────┐
                    │  Acceptance       │  ← EXISTS (Seed, never used)
                    │  Officer          │
                    │  (verify complete)│
                    └────────┬─────────┘
                             │ Skill() dispatch
                    ┌────────▼─────────┐
                    │  Session Close    │  ← EXISTS (GA)
                    │  Orchestrator     │     No programmatic dispatch
                    │  (archive, learn, │
                    │   commit, push)   │
                    └──────────────────┘
```

**Current state**: Components exist in isolation. No wiring connects them. Every arrow above is currently a human reading prose and manually invoking the next step.

---

## 8. Key Metrics Baseline

| Metric | Current Value | Target |
|---|---|---|
| Skills with explicit dispatch | 1/28 (3.6%) | 100% of process stewards |
| Orchestrator connection | None | Single invocation covers Steps 3–9 |
| Autonomous triggering | None | Night-watch + condition-based self-invocation |
| Error recovery coverage | 1/28 skills | All process stewards + orchestrator |
| Agent maturity (Institutional) | 0/14 | 3 by end of Phase 4 |
| Acceptance Officer usage | 0 real tasks | Gating all high-risk closures |
| Human gate mechanism | Documentation field | Active mid-workflow pause-and-approve |
| Tool approval handling | Not addressed | Circuit breaker + escalation path |

---

## References

- `docs/agentic/lifecycle-runbook.md` — 9-step lifecycle definition
- `docs/agentic/institutional-agent-registry-and-scorecard.md` — Agent maturity tracking
- `docs/agentic/institutional-agents/README.md` — Institutional agent directory
- `docs/research/orchestrator-design-principles.md` — 13 design principles
- `docs/research/3-5-agent-orchestration-patterns.md` — 5 concrete orchestration patterns
- `.claude/skills/orchestrator/SKILL.md` — New execution orchestrator (v1.0.0)
- `.claude/skills/session-close-orchestrator/SKILL.md` — Existing closeout orchestrator
- Agent audit performed 2026-05-29 (this session)
