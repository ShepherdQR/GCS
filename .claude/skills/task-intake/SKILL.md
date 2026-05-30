---
name: task-intake
description: Task intake and classification for GCS. Invoke when a non-trivial task arrives — classifies scope/risk/owner, creates task card with agentic_toolkit.py, enforces human gate for high-risk tasks, and dispatches to orchestrator for low/medium-risk execution. NEVER invoke for typos, status checks, or single-line fixes.
model: sonnet
priority: 95
exclusive: false
---

# Task Intake — GCS Task Lifecycle Steps 0-2

## Start Here

This skill is the front door for every non-trivial GCS task. It classifies incoming work,
creates a durable task card, enforces the human gate for high-risk changes, and hands
off low/medium-risk tasks to the orchestrator for execution.

**This skill covers three lifecycle steps:**

| Step | What | Output |
|------|------|--------|
| 0 | Classify | scope, risk, owner, rationale |
| 1 | Create task card | `docs/agentic/tasks/<date-slug>.md` + `.claude/current-task` |
| 2 | Human gate or dispatch | STOP (high) or `Skill("orchestrator")` (low/medium) |

It does NOT execute the task itself. That is the orchestrator's job.

## Entry Rule

Invoke when ANY of these are true:
- A non-trivial task arrives (multi-file change, new feature, architecture shift,
  fixture work, quality gate change, pipeline definition, documentation restructure)
- The user describes work needing classification ("what scope is this?", "how risky?")
- The user asks to "start a task", "create a task card", "intake this", or similar
- A task spans multiple domains and needs an owning steward assigned
- The user's request is ambiguous and classification is the first meaningful step

Skip when:
- The work is trivial: typo fix, status check, single-line change, read-only lookup
- The task card already exists and only needs execution (go directly to orchestrator)
- A steward skill is already clearly in scope and classification would add no value
- The user has explicitly specified scope, risk, and owner

**If uncertain, invoke.** An extra classification pass costs at most a few hundred tokens.
Missing classification on a misrouted task can cost the whole session.

Before proceeding, read:
- `docs/agentic/lifecycle-runbook.md` — task lifecycle phases and risk boundaries
- `docs/agentic/agentic-organization-operating-map.md` — operating map for steward skills
- `CLAUDE.md` — skill table for owner assignment

---

## Step 1: Classify

### Step 1.1: Determine Scope

Classify the work into exactly one scope category. Match against the work's primary
effect, not incidental touches.

| Scope | Definition | Examples |
|-------|-----------|----------|
| `implementation` | C++ solver code, algorithm changes, module logic | Editing `src/gcs/`, solver behavior, numeric routines |
| `docs` | Documentation creation or restructuring | Architecture docs, agentic SE docs, research notes |
| `tool` | Tooling, scripts, agentic toolkit, pipelines | `tools/`, `scripts/`, agentic design tooling |
| `architecture` | Cross-module architecture design or refactor | Contract definitions, module boundaries, dependency decisions |
| `fixture` | Test fixture creation, curation, or repair | `fixtures/scene/`, test data, corpus management |
| `ci` | CI configuration, build matrix, presets | `CMakePresets.json`, CI scripts, build toolchain |
| `review` | Review-only work (code review, design review, audit) | Repository audits, contract reviews, quality reviews |
| `maintenance` | Cleanup, refactoring without behavior change, repo hygiene | Renames, dead code removal, formatting |

**Ambiguity rule**: If the work touches two scopes equally, choose the one with higher
risk. If still uncertain, use the scope that produces the primary deliverable.

### Step 1.2: Determine Risk

Risk is about blast radius — what breaks if this goes wrong.

| Risk | Definition | Typical Scope Match |
|------|-----------|---------------------|
| `low` | Docs-only or config-only changes. No solver/runtime/IO/viewer impact. | `docs`, `ci` config, README updates |
| `medium` | Tooling changes, quality gates, fixtures, pipelines. Indirect impact on solver quality. | `tool`, `fixture`, `review`, `maintenance` with test impact |
| `high` | Solver runtime, IO serialization, viewer behavior, kernel contracts, session runtime, or anything that changes solver output semantics. | `implementation`, `architecture` that touches solver contracts |

**Default rule**: When uncertain between two risk levels, choose the higher one.
A false-positive human gate is a minor delay. A false-negative is a regression.

**High-risk triggers** (any one of these sets risk to `high`):
- Changes to `src/gcs/` C++ solver code
- Changes to `apps/gcs_cli/` CLI behavior
- Changes to IO adapters (JSON/text serialization format)
- Changes to viewer bridge or Python visualization behavior
- Changes to kernel contracts (ModelSnapshot, ContextSnapshot, StateDelta)
- Changes to numeric engine (NumericTask, Jacobian assembly, solving)
- Changes to session runtime (RuntimeCommand, transactions, history)

### Step 1.3: Determine Owner

Map the work to the best-fit steward skill from CLAUDE.md's skill table.
This is the skill that would own the primary deliverable.

**Quick-reference mapping:**

| Work touches... | Owning Skill |
|-----------------|-------------|
| Architecture docs, cross-module refactors | `gcs-architecture-steward` |
| C++ solver code, CMake, CLI | `gcs-cpp-solver-maintainer` |
| Python GUI, tkinter, matplotlib | `gcs-python-gui-builder` |
| Scene formats, JSON, history, IO | `gcs-scene-behavior-steward` |
| Quality gates, contract tests, CTest | `gcs-quality-steward` |
| Visual tokens, UI aesthetics | `gcs-ui-design-steward` |
| Task closure, archives, session lifecycle | `task-scoped-session-closer` |
| Constraint definitions, DOF, Jacobians | `gcs-constraint-semantics-steward` |
| Incidence graphs, connectivity | `gcs-incidence-structure-steward` |
| Decomposition planning, subproblems | `gcs-decomposition-planning-steward` |
| Numeric engine, local solves, scaling | `gcs-numeric-engine-steward` |
| Diagnostics, DOF reports, obstruction | `gcs-diagnostics-certification-steward` |
| Session runtime, transactions, history | `gcs-session-runtime-steward` |
| IO adapters, schemas, serialization | `gcs-io-adapter-steward` |
| Viewer bridge, diagnostic overlays | `gcs-viewer-bridge-steward` |
| Kernel contracts, snapshots, IDs | `gcs-kernel-contract-steward` |
| Contract tools, fixture builders | `gcs-contract-tools-steward` |
| Scene generation, synthetic graphs | `gcs-scene-generation-engineer` |
| Third-party deps, licensing | `gcs-third-party-governance-steward` |
| Scientific figures, diagrams | `gcs-scientific-figure-producer` |
| Token audit, cost tracking | `gcs-token-audit-steward` |
| Repository audit, trend analysis | `gcs-repository-audit-steward` |
| UI QA, theme validation | `gcs-ui-qa-steward` |
| Product demos, smoke tests | `gcs-product-demo-steward` |
| Benchmark execution, solver comparison | `gcs-benchmark-steward` |
| Git branches, worktrees, push safety | `git-session-branch-steward` |

**Ambiguity rule**: If two skills could own it, prefer the one that owns the primary
changed path. If still ambiguous, record both as `owning_agent` and `specialist_agents`
and let the orchestrator decide.

### Step 1.4: Record Classification Rationale

Write a one-sentence rationale before proceeding to card creation:
```
Classification rationale: scope=<X> because <reason>; risk=<Y> because <blast radius>;
owner=<Z> because <primary path/domain match>.
```

Include this in the task card under `## Classification Rationale`.

---

## Step 2: Create Task Card

### Step 2.1: Derive Slug

From the request, derive a short kebab-case slug (under 64 chars):

- Use the primary action noun + key object
- Remove articles, prepositions, filler words
- Examples: `add-connectivity-fallback`, `refactor-kernel-snapshot-api`, `audit-token-june-2026`

### Step 2.2: Build and Run Command

Construct the agentic_toolkit.py command with all classification results:

```bash
python tools/agentic_design/agentic_toolkit.py new-task-card \
  --slug "<slug>" \
  --scope "<scope>" \
  --risk "<risk>" \
  --owner "<owner>" \
  --request "<one-sentence summary of the user's request>" \
  --write
```

Additional flags based on classification:
- `--specialist "<skill>"` — if the task needs a second specialist (comma-separated for multiple)
- `--human-gate` — if risk is `high` (applied in Step 3)
- `--human-gate-reason "<reason>"` — if human gate is set (applied in Step 3)
- `--evidence "<requirement>"` — if specific evidence requirements are known upfront
- `--narrative-line "<line>"` — if the task is tied to a narrative line

### Step 2.2b: Set Token Budget (Phase 7.5)

Set `token_budget.max_total` in the task card based on risk classification:

| Risk | Budget | Rationale |
|---|---|---|
| `low` | 200,000 | Single file, docs, config — minimal exploration needed |
| `medium` | 500,000 | Multi-file, tooling, quality gates — moderate exploration |
| `high` | 1,000,000 | Solver, runtime, IO, viewer — substantial exploration expected |

The orchestrator enforces this budget (see Step 1.6 of orchestrator SKILL.md). If a task legitimately needs more, the task card can be manually edited to increase the budget before re-dispatching.

### Step 2.3: Validate the Card

After creation, run validation:

```bash
python tools/agentic_design/agentic_toolkit.py validate-task-card docs/agentic/tasks/<today>-<slug>.md
```

If validation fails, fix the issues and re-validate. Do not proceed with an invalid card.

### Step 2.4: Write Current Task Pointer

Create or update `.claude/current-task`:

```
task_card: docs/agentic/tasks/<today>-<slug>.md
created: <today>
scope: <scope>
risk: <risk>
owner: <owner>
```

This file is the session's single source of truth for "what are we working on right now."

### Step 2.5: Fill the Task Card Body

After the tool creates the skeleton, fill in the body sections. The card must contain:

```markdown
---
task_id: <today>-<slug>
status: draft
request: "<one-sentence summary>"
scope: <scope>
risk: <risk>
owning_agent: <owner>
specialist_agents:
  - <specialist>          # or "none"
affected_contracts:
  - <contract>            # or "none" — kernel, IO, graph, numeric, etc.
affected_paths:
  - <path>                # best-guess paths this work will touch
required_evidence:
  - validate-task-card
  - validate-docs         # default for all non-trivial tasks
human_gate_required: <true|false>
human_gate_reason: "<reason if true, empty if false>"
token_budget:
  max_total: <200000|500000|1000000>   # low=200K, medium=500K, high=1M
  budget_consumed: 0
---

# <today>-<slug>

## Classification Rationale

scope=<X> because <reason>; risk=<Y> because <blast radius>; owner=<Z> because <primary domain match>.

## Scope

<one paragraph describing what IS and is NOT in scope>

## Non-Goals

- <explicitly out-of-scope item 1>
- <explicitly out-of-scope item 2>

## Context To Read

- <relevant architecture doc 1>
- <relevant architecture doc 2>
- Owning skill: `<owner>` (CLAUDE.md skill table)

## Acceptance Gates

- The owning boundary is clear.
- Required evidence is produced or a reason is recorded.
- Residual risks are named.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<today>-<slug>.md
```

## Evidence Bundle

<filled during execution by orchestrator or closer>
```

---

## Step 3: Human Gate

### Decision Point

This step applies only when `risk = high`.

If `risk = low` or `risk = medium`, skip to Step 4.

If `risk = high`:

1. Set `human_gate_required: true` in the task card frontmatter.
2. Set `human_gate_reason` to a specific explanation of what needs human review:
   - What solver/runtime/IO/viewer behavior is at risk
   - What contracts or semantics could change
   - What the blast radius is (which modules, formats, or behaviors)
3. Re-run the toolkit with the human gate flags:
   ```bash
   python tools/agentic_design/agentic_toolkit.py new-task-card \
     --slug "<slug>" --scope "<scope>" --risk "high" --owner "<owner>" \
     --request "<request>" --human-gate --human-gate-reason "<reason>" \
     --write --force
   ```
4. Output the following message verbatim:

```
⚠️ HUMAN GATE REQUIRED

Task card created at: docs/agentic/tasks/<today>-<slug>.md
Risk: high
Reason: <human_gate_reason>

Review the plan before proceeding. When ready, execute:

    Skill({skill: "orchestrator", args: "execute task <task-id>: <request>. Task card: docs/agentic/tasks/<today>-<slug>.md."})
```

5. **STOP. Do NOT invoke orchestrator.** The human gate must be manually cleared before
   execution can proceed. The `.claude/current-task` pointer is set, but no further
   automated steps are taken.

6. If the user explicitly clears the gate ("proceed", "approved", "go ahead"),
   transition to Step 4.

### Gate Clearance

When the user clears the gate:
- Update the task card: `human_gate_required: false`, `human_gate_reason: "cleared by user on <date>"`
- Re-run toolkit with `--force` to update the card
- Proceed to Step 4

---

## Step 4: Dispatch (Low/Medium Risk Only)

This step applies only when `risk != high` (or when a high-risk gate has been
explicitly cleared).

### Step 4.1: Confirm Readiness

Verify before dispatching:
- Task card exists and passes `validate-task-card`
- `.claude/current-task` points to the correct card
- `risk` is `low` or `medium` (or high gate was cleared)

### Step 4.2: Dispatch to Orchestrator

Invoke the orchestrator skill with the full task context:

```
Skill({
  skill: "orchestrator",
  args: "execute task <task-id>: <request>. Task card: docs/agentic/tasks/<today>-<slug>.md. Scope: <scope>. Risk: <risk>. Owner: <owner>."
})
```

The orchestrator receives:
- The task ID and request for decomposition
- The task card path for reading full context
- Scope, risk, and owner for architecture decisions

### Step 4.3: Output Dispatch Confirmation

```
Task classified and dispatched.

Task ID:   <task-id>
Task card: docs/agentic/tasks/<today>-<slug>.md
Scope:     <scope>
Risk:      <risk>
Owner:     <owner>
Status:    → orchestrator
```

---

## Guardrails

### Hard Constraints (MUST follow)

1. **NEVER invoke orchestrator for high-risk tasks** without explicit human gate clearance.
2. **NEVER skip classification** — "unknown" is better than "default". Every task gets
   scope, risk, and owner.
3. **ALWAYS create a task card** before mutating files for non-trivial work.
4. **ALWAYS validate the task card** with `agentic_toolkit.py validate-task-card` before
   marking intake complete.
5. **ALWAYS write `.claude/current-task`** — this is the session's grounding mechanism.
6. **NEVER fabricate a slug** — derive it from the actual request content.
7. **NEVER set risk to `low` for anything touching `src/gcs/`, `apps/`, IO, or viewer.**

### Soft Guidelines (SHOULD follow)

8. Prefer conservative (higher) risk classification when uncertain.
9. Record classification rationale — future agents and reviewers need it.
10. If two owners are equally valid, record both (owning + specialist).
11. If the request is ambiguous, ask one clarifying question before classifying.
    Do not guess at the user's intent when the cost of misclassification is high.

### Anti-Patterns (NEVER do)

12. "Default" classification — `scope: implementation, risk: medium, owner: gcs-cpp-solver-maintainer`
    applied blindly to everything. Each field needs a reason.
13. Skipping the task card because "it's small" — if it's truly small enough to
    skip, the entry rule would have caught it. If uncertain, create the card.
14. Dispatching to orchestrator without writing `.claude/current-task`.
15. Classifying tool work as `risk: low` when it touches quality gates or CI.

---

## Task Card Template Reference

For quick copy-paste when the toolkit is unavailable or a manual card is needed:

```markdown
---
task_id: <today>-<slug>
status: draft
request: "<one-sentence summary>"
scope: <implementation|docs|tool|architecture|fixture|ci|review|maintenance>
risk: <low|medium|high>
owning_agent: <best-fit steward skill>
specialist_agents:
  - none
affected_contracts:
  - none
affected_paths:
  - <best-guess path>
required_evidence:
  - validate-task-card
  - validate-docs
human_gate_required: false
human_gate_reason: ""
token_budget:
  max_total: <200000|500000|1000000>   # low=200K, medium=500K, high=1M
  budget_consumed: 0
---

# <today>-<slug>

## Classification Rationale

<one sentence>

## Scope

<one paragraph>

## Non-Goals

- <item>

## Context To Read

- <doc>
- Owning skill: `<owner>`

## Acceptance Gates

- The owning boundary is clear.
- Required evidence is produced or a reason is recorded.
- Residual risks are named.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<today>-<slug>.md
```

## Evidence Bundle

<filled during execution>
```

---

## Claude Code Integration

### Read operations
- `Read` — check `CLAUDE.md` for skill table, read existing task cards, read
  lifecycle runbook and operating map for classification guidance
- `Glob` — find existing task cards for the same domain to avoid duplicates
- `Grep` — search for related task cards or affected paths

### Write operations
- `Write` — create new task card at `docs/agentic/tasks/<date>-<slug>.md`,
  create/update `.claude/current-task`
- `Edit` — update task card frontmatter (human gate clearance, status changes)

### Bash operations
- `python tools/agentic_design/agentic_toolkit.py new-task-card ...` — create card
- `python tools/agentic_design/agentic_toolkit.py validate-task-card ...` — validate card

### Skill dispatch
- `Skill({skill: "orchestrator", args: "..."})` — Step 4 dispatch for low/medium-risk tasks

### Task tracking
- `TaskCreate` / `TaskUpdate` — track the intake workflow itself if it spans
  multiple turns

### Memory
- Check `C:\Users\QR\.claude\projects\C--Codes-AI-GCS-A\memory\` for relevant
  patterns (previous classification decisions, owner assignments for similar tasks)

---

## Quick Reference Card

```
Task arrives
  │
  ├─ Trivial? → Skip intake (do it directly)
  │
  └─ Non-trivial?
       │
       ├─ Step 1: Classify
       │     ├─ scope: implementation|docs|tool|architecture|fixture|ci|review|maintenance
       │     ├─ risk: low|medium|high
       │     └─ owner: best-fit steward skill
       │
       ├─ Step 2: Create task card
       │     ├─ toolkit new-task-card --write
       │     ├─ validate-task-card
       │     └─ Write .claude/current-task
       │
       └─ Decision: risk?
             │
             ├─ HIGH
             │     ├─ Set human_gate_required: true
             │     ├─ Output ⚠️ HUMAN GATE REQUIRED
             │     └─ STOP (do NOT invoke orchestrator)
             │
             └─ LOW or MEDIUM
                   ├─ Confirm readiness
                   └─ Skill("orchestrator", ...)
```

---

## Version

- **Version**: 1.0.0
- **Date**: 2026-05-30
- **Status**: Seed — initial classification + card creation + gate + dispatch pipeline
- **Lifecycle Steps Covered**: 0 (classify), 1 (create task card), 2 (human gate / dispatch)
- **Dependencies**: `orchestrator` skill, `agentic_toolkit.py`
- **Next**: Field testing with real task intake; refine scope/risk heuristics from
  classification accuracy data
