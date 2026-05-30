# GCS Multi-Agent System — Development Roadmap

**Date:** 2026-05-29
**Status:** Development Plan (post-baseline)
**Baseline:** `docs/research/gcs-multi-agent-system-baseline-2026-05-29.md`
**Principle Source:** `docs/research/orchestrator-design-principles.md` (13 principles)

---

## Executive Summary

The GCS multi-agent system has 28 skills and 14 institutional agents with strong documentation but near-zero programmatic wiring. This roadmap defines 6 phases to go from "documented but disconnected" to "autonomously executable." Each phase has concrete deliverables, success criteria, and a gate before proceeding.

**Target end state**: A single `Skill("orchestrator")` invocation carries a task from intake through execution, verification, closeout, and learning — with human gates only where the lifecycle-runbook requires them.

---

## Phase 1: Wire the Dispatch Layer

**Goal:** Convert all process-steward skills from prose-sequenced to programmatically-dispatched.
**Duration:** 1-2 sessions
**Prerequisite:** None (current baseline)

### 1.1 Convert session-close-orchestrator to Explicit Dispatch

Replace the prose pipeline with actual `Skill()` calls:

**Current (prose):**
```
### Step 2: Task Archive
Use the task-scoped-session-closer conventions...
### Step 3: Experience & Promotion Evaluation
When experience material IS identified, invoke bladesmith-quench-forge...
```

**Target (programmatic):**
```
### Step 2: Task Archive
Skill({skill: "task-scoped-session-closer", args: "archive task <task-id> with evidence at <paths>"})
### Step 3: Experience & Promotion Evaluation
Skill({skill: "bladesmith-quench-forge", args: "evaluate session <session-id> for experience extraction"})
```

**Files to change:**
- `.claude/skills/session-close-orchestrator/SKILL.md` — replace prose pipeline with Skill() calls
- Add `model: opus` to frontmatter (orchestrator must be ≥ workers, Principle 5)

**Success criteria:**
- `session-close-orchestrator` invokes `task-scoped-session-closer` via `Skill()` tool call
- `session-close-orchestrator` invokes `bladesmith-quench-forge` via `Agent()` tool call
- Pipeline steps 0–5 each produce verifiable output (file exists, command succeeded)
- Guardrails remain: "If a step fails, report and continue" — but now with explicit error capture

### 1.2 Audit and Wire Cross-Reference Prose

For the ~10 skills with prose "also use X" references, determine which should become explicit dispatch:

| Skill | References | Should Wire? | Rationale |
|---|---|---|---|
| gcs-cpp-solver-maintainer | gcs-architecture-steward | **Yes** | Architecture steward is the gate for cross-module changes |
| gcs-scene-behavior-steward | gcs-cpp-solver-maintainer, gcs-python-gui-builder | Conditional | Wire only when behavior change spans C++/Python boundary |
| gcs-python-gui-builder | gcs-scene-behavior-steward, gcs-viewer-bridge-steward | Conditional | Wire when GUI change affects scene format or viewer projection |
| gcs-ui-qa-steward | gcs-ui-design-steward | **Yes** | QA must gate on design conventions |
| gcs-scene-generation-engineer | gcs-scene-behavior-steward | Conditional | Wire when generated scene needs compatibility check |

**Rule (Principle 7):** Wire when the downstream skill is a **gate** (must-pass). Leave as prose when the downstream skill is a **reference** (may-consult).

**Success criteria:**
- At least 3 cross-skill prose references converted to explicit dispatch
- Each wired dispatch includes evidence capture (what the downstream skill produced)

### Phase 1 Gate

- [ ] `session-close-orchestrator` uses `Skill()` for all 4 downstream components
- [ ] At least 3 domain skills use explicit dispatch to their gating skills
- [ ] `git diff --stat` shows changes scoped to `.claude/skills/` only
- [ ] Validate: `python tools/agentic_design/agentic_toolkit.py validate-docs`

---

## Phase 2: Connect the Two Orchestrators

**Goal:** Single invocation covers Steps 3–9 (execution through closeout).
**Duration:** 1 session
**Prerequisite:** Phase 1 complete

### 2.1 Wire orchestrator → session-close-orchestrator

The `orchestrator` Phase 5 (Handoff) currently ends with commit and report. Extend it to invoke closeout:

```
Phase 5: Handoff
  Step 5.1: Create/Update Task Card (existing)
  Step 5.2: Commit (existing)
  Step 5.3: Report (existing)
  Step 5.4: Invoke Closeout ← NEW
    Skill({skill: "session-close-orchestrator", args: "close session for task <task-id>"})
```

### 2.2 Add Closeout Decision Logic

Not every orchestrator invocation needs full closeout. Add a decision gate:

```
Step 5.4 Decision:
  - If task is complete AND session is ending → invoke session-close-orchestrator
  - If task is complete BUT session continues → create task card, skip closeout
  - If task is incomplete → flag remaining subtasks, skip closeout
```

### 2.3 Create End-to-End Test Case

A lightweight task that exercises the full pipeline:
1. `Skill("orchestrator", "add a comment to README.md and verify it")`
2. Orchestrator plans → dispatches to cpp-solver-maintainer (or general-purpose)
3. Worker edits file → orchestrator verifies
4. Orchestrator invokes session-close-orchestrator
5. Task card created → token audit → archive → commit → push

**Success criteria:**
- Single `Skill("orchestrator", ...)` invocation produces: changed file + task card + archive + commit
- No manual intermediate steps
- All evidence captured in archive

### Phase 2 Gate

- [ ] `orchestrator` Phase 5 invokes `session-close-orchestrator` via `Skill()` when task is complete
- [ ] End-to-end test case completes without human intervention between invocation and push
- [ ] Archive contains orchestration record (architecture decision, agent count, verification results)

---

## Phase 3: Intake Automation

**Goal:** Task arrival automatically triggers classification, task card creation, and orchestrator invocation.
**Duration:** 1-2 sessions
**Prerequisite:** Phase 2 complete

### 3.1 Create Intake Skill

A lightweight `task-intake` skill that handles Steps 0–2:

```
Skill: task-intake
Trigger: User describes work that is non-trivial
Actions:
  1. Classify: scope, risk, owner, affected paths
  2. Create task card via agentic_toolkit.py
  3. Write .claude/current-task
  4. Determine if human gate required (risk=high → human_gate_required: true)
  5. Invoke orchestrator with task context
     Skill({skill: "orchestrator", args: "<task description from card>"})
```

### 3.2 Wire Human Gate Mechanism

When `human_gate_required: true`:

```
1. Intake creates task card with human_gate_required: true
2. Intake writes the execution plan to the task card
3. Intake STOPS — does NOT invoke orchestrator
4. Output: "Task card created. Human gate required. Review plan at <path>.
   To proceed: Skill({skill: 'orchestrator', args: 'execute task <task-id>'})"
```

This makes the human gate a real enforcement point, not a documentation field.

### 3.3 Auto-Classification Quality

Validate that the intake classification matches what a human would choose:

**Test corpus:** Last 20 completed task cards. For each:
1. Run intake classification
2. Compare to human-assigned scope/risk/owner
3. Target: ≥85% agreement on scope, ≥90% on risk, ≥80% on owner

### Phase 3 Gate

- [ ] `task-intake` skill exists and handles Steps 0–2
- [ ] Human gate (`human_gate_required: true`) actually stops execution
- [ ] Classification accuracy meets thresholds on 20-card corpus
- [ ] Intake → orchestrator handoff is programmatic (Skill() call, not prose)

---

## Phase 4: Error Recovery & Resilience

**Goal:** No skill fails silently. All process stewards have retry, fallback, or escalation.
**Duration:** 1-2 sessions
**Prerequisite:** Phase 2 complete (Phase 3 can run in parallel)

### 4.1 Standardize Error Handling Pattern

Create a reusable error handling template for all process-steward skills:

```yaml
error_handling:
  retry:
    max_retries: 1
    backoff: "report failure, re-invoke with error context"
  fallback:
    strategy: "degrade gracefully — produce partial output with gap flags"
  escalation:
    trigger: "retry also failed OR multiple workers failed"
    action: "write escalation record to task card; flag for human review"
  circuit_breaker:
    trigger: "3 consecutive failures in same skill"
    action: "stop dispatching to this skill; flag in session output summary"
```

### 4.2 Apply to Process Stewards

| Skill | Current State | Phase 4 Target |
|---|---|---|
| `session-close-orchestrator` | "If a step fails, report and continue" | Retry 1× per step; escalate on second failure |
| `task-scoped-session-closer` | No error handling | Retry archive creation; fallback to minimal archive |
| `orchestrator` | Max 1 retry/worker | Add circuit breaker for repeated worker failures |
| `git-session-branch-steward` | No error handling | Retry git operations; escalate on push failure |
| `token-audit-steward` | No error handling | Fallback to manual token count if DB import fails |

### 4.3 Add Tool Approval Handling

When a worker hits a permission prompt:

1. **Detect**: orchestrator monitors worker output for tool denial patterns
2. **Retry**: re-dispatch with explicit permission pre-grant in the prompt ("You are authorized to use Bash, Read, Write")
3. **Escalate**: if retry also blocked, flag for human with exact tool and reason
4. **Circuit break**: if same tool is repeatedly denied, stop dispatching to that worker class

### Phase 4 Gate

- [ ] All 5 process stewards have error handling matching the template
- [ ] Circuit breaker prevents cascading retries (Principle 13)
- [ ] Tool approval blocking has detection + retry + escalation path
- [ ] Error handling tested with at least 1 intentional failure per skill

---

## Phase 5: Agent Maturity Pipeline

**Goal:** Move 3+ agents from Candidate → Seed → Practiced → Promoted.
**Duration:** Ongoing (3-5 sessions with evidence accumulation)
**Prerequisite:** Phase 2 complete (agents need real usage to accumulate evidence)

### 5.1 Candidate Exercise Rotation

Schedule each candidate agent for a real-task exercise:

| Session | Candidate Agent | Exercise Task |
|---|---|---|
| 1 | Acceptance Officer | Review a completed task archive; produce pass/fail verdict with evidence |
| 2 | Bookkeeper | Analyze a session's token cost vs. delivered value; produce BEI report |
| 3 | Collation Officer | Cross-read 3 related docs; flag contradictions and stale references |
| 4 | Gardener | Scan for accumulated small issues; batch-fix 3-5 minor items |
| 5 | Night-Watch | Run full diagnostic patrol; produce health report (no commit/push) |

### 5.2 Evidence Collection Automation

For each exercise:
1. Record: which agent, which task, what outputs, what the human reviewer decided
2. Store evidence at `docs/agentic/institutional-agents/<agent-slug>/examples/`
3. After 3 successful exercises, flag for promotion review

### 5.3 Promotion Automation

When an agent accumulates sufficient evidence:

```
Skill({skill: "bladesmith-quench-forge", args: "evaluate promotion readiness for <agent-slug>"})
```

The Bladesmith (already Promoted, 10/10) reviews:
1. Contract clarity — is the agent's README unambiguous?
2. Example evidence — do the 3+ examples show consistent value?
3. Refusal behavior — does the agent decline out-of-scope work?
4. Boundary discipline — does the agent stay in its lane?

If all 4 pass → promote to next maturity level and update registry.

### 5.4 Target Progression

| Agent | Current | Phase 5 Target | Rationale |
|---|---|---|---|
| Acceptance Officer | Seed (5/10) | Practiced (7+/10) | Critical path for autonomous verification |
| Bookkeeper | Candidate | Seed (5+/10) | Token economics is active domain |
| Collation Officer | Candidate | Seed (5+/10) | Cross-reading fills a real gap |
| Night-Watch | Candidate | Seed (5+/10) | Only scheduled automation; needs trust |
| Gardener | Candidate | Seed (5+/10) | Low-risk entry point for autonomy |

### Phase 5 Gate

- [ ] At least 3 agents promoted one maturity level with evidence
- [ ] Acceptance Officer promoted to Practiced (blocks Phase 6)
- [ ] All promotions recorded in institutional-agent-registry-and-scorecard.md
- [ ] Each promoted agent has ≥3 example exercises in its `examples/` directory

---

## Phase 6: Autonomous Operation

**Goal:** The system can run end-to-end without human intervention between intake and push, with human gates only at lifecycle-runbook-mandated checkpoints.
**Duration:** 2-3 sessions
**Prerequisite:** Phases 1-5 complete

### 6.1 Condition-Based Self-Invocation

Enable the system to detect conditions and self-invoke:

| Condition | Action |
|---|---|
| Session starts, no `.claude/current-task` | Invoke `task-intake` to classify and card |
| Task card exists with `status: draft` | Invoke `orchestrator` to execute |
| Task complete, session ending | Invoke `session-close-orchestrator` |
| 3+ sessions since last Night-Watch patrol | Invoke `night-watch` diagnostics |

**Implementation:** Extend CLAUDE.md with auto-invocation rules that check these conditions at session start.

### 6.2 Human Gates as Active Enforcement

Convert the documented-but-unenforced human gates into real checkpoints:

```
High-risk task workflow:
  1. task-intake: creates card, sets human_gate_required: true, STOPS
  2. HUMAN: reviews plan, approves → updates task card status to "approved"
  3. orchestrator: checks human_gate_required AND status=approved before executing
  4. If human_gate_required=true AND status≠approved → REFUSE to execute
```

### 6.3 Night-Watch Autonomy

Remove the "do not commit or push" restriction. Night-watch can:
- Run diagnostics
- If clean: auto-commit health report, auto-push
- If issues found: create task cards for each issue, report, do NOT push (escalate to human)

This requires Night-Watch to reach at least Seed maturity (Phase 5).

### 6.4 Headless Orchestrator Mode

The orchestrator can run without a human in the loop when:
- Task is classified as `risk: low` or `risk: medium`
- `human_gate_required: false`
- Acceptance Officer (now Practiced) verifies completion
- All quality gates pass

High-risk tasks still require human gate per lifecycle-runbook.

### 6.5 Full Autonomy Test Suite

A battery of end-to-end tests:

| Test | Description | Expected Behavior |
|---|---|---|
| Low-risk typo fix | "Fix typo in README.md" | Intake → orchestrator → close → push. No human gate. |
| Medium-risk tool change | "Add --verbose flag to agentic_toolkit.py validate-docs" | Intake → orchestrator (with verification) → close → push. No human gate. |
| High-risk solver change | "Change Jacobian assembly in numeric engine" | Intake → STOP at human gate. Requires human approval before orchestrator executes. |
| Multi-skill coordination | "Add new scene format and update Python GUI to support it" | Intake → orchestrator (parallel: scene-behavior + python-gui) → cross-worker verification → close → push. |
| Night-watch clean run | Scheduled patrol with no issues | Auto-commit health report, auto-push. |
| Night-watch issue found | Scheduled patrol finds stale reference | Create task card, report, STOP. Human reviews task card. |

### Phase 6 Gate

- [ ] All 6 autonomy tests pass
- [ ] Human gate is enforced for high-risk tasks (not just documented)
- [ ] Night-watch can auto-commit/push clean health reports
- [ ] Headless orchestrator completes low/medium-risk tasks without human intervention
- [ ] Acceptance Officer gates all closures (Practiced maturity)

---

## Dependency Graph

```
Phase 1 (Dispatch Wiring)
  │
  ├──→ Phase 2 (Connect Orchestrators)
  │      │
  │      ├──→ Phase 3 (Intake Automation)
  │      │      │
  │      │      └──→ Phase 6 (Autonomous Operation)
  │      │
  │      ├──→ Phase 4 (Error Recovery)  ← can run parallel with Phase 3
  │      │      │
  │      │      └──→ Phase 6 (Autonomous Operation)
  │      │
  │      └──→ Phase 5 (Agent Maturity)  ← can run parallel with Phase 3+4
  │             │
  │             └──→ Phase 6 (Autonomous Operation)
  │
  └── All phases converge on Phase 6
```

**Parallelism opportunities:**
- Phase 3 + Phase 4 can run in parallel (different files, different concerns)
- Phase 5 can start as soon as Phase 2 delivers (agents need real usage on wired pipelines)

---

## Resource Estimates

| Phase | Sessions | Tokens (est.) | Risk |
|---|---|---|---|
| 1: Dispatch Wiring | 1-2 | 200K-400K | Low — editing existing skill files |
| 2: Connect Orchestrators | 1 | 150K-300K | Low — extending orchestrator Phase 5 |
| 3: Intake Automation | 1-2 | 200K-500K | Medium — new skill, classification accuracy |
| 4: Error Recovery | 1-2 | 200K-400K | Low — applying template to existing skills |
| 5: Agent Maturity | 3-5 | 500K-1M | Medium — requires real-task evidence accumulation |
| 6: Autonomous Operation | 2-3 | 300K-600K | High — changes fundamental operating model |
| **Total** | **9-15 sessions** | **1.5M-3.2M tokens** | |

---

## Success Metrics

| Metric | Baseline (2026-05-29) | Phase 6 Target |
|---|---|---|
| Skills with explicit dispatch | 1/28 (3.6%) | ≥6/28 (all process stewards + key gates) |
| Orchestrator connection | None | Single invocation covers Steps 3–9 |
| Autonomous triggering | None | Condition-based at session start |
| Error recovery coverage | 1/28 skills | All 5 process stewards |
| Agent maturity (Institutional) | 0/14 | ≥3/14 promoted (Acceptance Officer must be Practiced+) |
| Acceptance Officer usage | 0 real tasks | Gates all closures |
| Human gate mechanism | Documentation field | Active enforcement for high-risk |
| End-to-end autonomy | 0% | Low/medium-risk tasks complete without human intervention |
| Night-watch autonomy | Read-only (no commit/push) | Auto-commit clean reports |

---

## References

- `docs/research/gcs-multi-agent-system-baseline-2026-05-29.md` — Current state baseline
- `docs/research/orchestrator-design-principles.md` — 13 design principles governing all phases
- `docs/research/3-5-agent-orchestration-patterns.md` — Pattern reference for architecture decisions
- `docs/agentic/lifecycle-runbook.md` — 9-step lifecycle and human gate policy
- `docs/agentic/institutional-agent-registry-and-scorecard.md` — Agent maturity tracking
- `.claude/skills/orchestrator/SKILL.md` — Execution orchestrator (v1.0.0)
- `.claude/skills/session-close-orchestrator/SKILL.md` — Closeout orchestrator
