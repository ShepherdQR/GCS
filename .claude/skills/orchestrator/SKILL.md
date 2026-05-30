---
name: orchestrator
description: Evidence-based multi-agent task orchestrator. Invoke for complex, multi-step work where the optimal agent architecture is not obvious. This skill analyzes task structure, selects the right architecture (single agent, prompt chain, or parallel workers), dispatches to specialist agents/skills, verifies their outputs, and synthesizes results. NEVER invoke for single-file edits, typos, or trivial lookups — those are single-agent tasks.
model: opus
---

# Orchestrator — Cross-Project Multi-Agent Coordination

## Start Here

This skill turns a complex task into a controlled sequence of specialized agents,
each with scoped context and clear evidence gates. It exists because the academic
consensus is clear: multi-agent systems amplify errors by 4.4×–17.2× when unverified,
but improve performance by up to +80.9% when correctly architecture-matched to
parallel-decomposable tasks.

**This skill is project-agnostic.** Drop it into any project's `.claude/skills/`
directory. Configure the Project Configuration section below for project-specific
paths, then invoke with: `Skill({skill: "orchestrator", args: "<task description>"})`

## Research Foundation

This skill's design is grounded in 7 academic papers and 3 industry sources. See
`docs/research/orchestrator-design-principles.md` in the GCS project for the full
extraction. Key constraints embedded in this skill:

| Constraint | Source |
|---|---|
| 3–5 agent golden ratio; beyond this, coordination cost dominates | Kim et al. (2025), arXiv:2512.08296 |
| Task-structure-first: classify parallel vs. sequential before choosing architecture | Kim et al. (2025); 87% prediction accuracy |
| Centralized verification is mandatory: 4.4× vs. 17.2× error amplification | Kim et al. (2025) |
| Manager must be ≥ worker capability: weak manager + weak worker = worse than alone | Liu (2026), arXiv:2603.26458 |
| 2 diverse agents ≥ 16 homogeneous agents | Yang et al. (2026), arXiv:2602.03794 |
| Context isolation is the primary value of multi-agent, not parallelism | Anthropic Harness; Claude Code docs |

## Project Configuration

Before first use, fill in this section for the current project:

```yaml
project:
  name: "<project-name>"
  root: "<absolute-path-to-project-root>"
  docs_dir: "docs/"             # relative to root; where reports/plans/archive live
  tasks_dir: "docs/tasks/"      # relative to root; where task cards live
  skills_dir: ".claude/skills/" # relative to root; where skills are defined
  agents_dir: ".claude/agents/" # relative to root; where agent definitions live

available_skills:
  # List project skills the orchestrator can dispatch to
  # Format: name: "description of when to use"

available_agents:
  # List project agents the orchestrator can dispatch to
  # Format: name: "description of when to use"

conventions:
  task_card_format: "markdown"  # or "yaml" or "none"
  commit_style: "imperative"    # commit message convention
  archive_enabled: true         # whether to archive completed tasks
  archive_dir: "docs/completed/" # relative to root
```

## Entry Rule

Invoke when ALL of these are true:
- The task is non-trivial (more than a single-file edit, typo fix, or lookup)
- The optimal agent architecture is not immediately obvious (single agent? parallel? chained?)
- The task spans multiple domains, files, or decision points

Skip when:
- The task is a single-file fix, typo, or read-only lookup
- The task fits entirely within one existing skill's scope
- The user has explicitly specified the architecture ("use a single agent")

**If uncertain, invoke.** The cost of misclassification (using multi-agent for sequential work) is higher
than the cost of analysis (a few hundred tokens to think about task structure).

---

## Phase 1: Task Structure Analysis

Before spawning ANY workers, classify the task. This is the single most important decision —
misclassification causes −39% to −70% performance degradation (Kim et al., 2025).

### Step 1.1: Decompose the Task

Write out the task as a list of subtasks. For each subtask, mark its dependency:

```
Task: <one-line summary>

Subtasks:
  1. <description> — depends on: [none | subtask N]
  2. <description> — depends on: [none | subtask N]
  ...
```

### Step 1.2: Classify Dependency Structure

| Structure | Pattern | Recommended Architecture |
|---|---|---|
| **Independent** | All subtasks depend on [none] | Parallel workers (2–5 agents) |
| **Chain** | Each subtask depends on previous one | Single agent or prompt chaining |
| **Tree** | Some parallel branches, some sequential within branches | Mixed: parallel for branches, sequential within |
| **Merge** | Independent work converging to one synthesis step | Parallel workers + single synthesis agent |

### Step 1.3: Decide Agent Count

Apply the golden ratio constraint:

| Subtask Count | Max Parallel Agents | Rationale |
|---|---|---|
| 1–3 | 1 (single agent) | Below parallelism threshold |
| 4–8 | 2–3 | Within golden ratio |
| 9–20 | 3–5 | Upper bound of golden ratio |
| 21+ | 5 max; batch subtasks | Batch subtasks into ≤5 groups |

**Hard constraint: NEVER dispatch more than 5 parallel agents without explicit written justification**
referencing task decomposability evidence (clean interfaces, zero shared state, merge-at-end pattern).

### Step 1.4: Select Model for Each Worker

Apply the diversity principle and manager-quality constraint:

| Worker Role | Recommended Model | When |
|---|---|---|
| Exploration, search, grep-heavy | Haiku (or fastest available) | Read-only, high volume |
| Implementation, writing, editing | Sonnet (or mid-tier) | Standard SWE work |
| Coordination, review, synthesis | Opus (or strongest available) | Orchestrator itself; cross-worker verification |

**Hard constraint: The orchestrator model MUST be ≥ the strongest worker model.**
Never dispatch an Opus worker from a Sonnet orchestrator.

---

## Phase 2: Architecture Execution

### Architecture A: Single Agent (Chain dependency)

When subtasks form a strict chain:

```
Skill({skill: "<most-relevant-skill>", args: "<full task description, all steps in order>"})
```

Document why multi-agent was rejected:
```
## Architecture Decision
- Structure: Chain (each step depends on previous)
- Decision: Single agent — multi-agent would degrade performance by estimated 39–70%
- Reference: Kim et al. (2025), Table 3
```

### Architecture B: Prompt Chaining (Chain with gates)

When subtasks form a chain but each step needs independent verification:

```
Step 1: Skill({skill: "<skill-a>", args: "<step 1 only>"})
Gate 1: Verify step 1 output before proceeding
Step 2: Skill({skill: "<skill-b>", args: "<step 2, with step 1 output as context>"})
Gate 2: Verify step 2 output
...
```

### Architecture C: Parallel Workers (Independent subtasks)

When subtasks are truly independent (clean interfaces, no shared state):

```
Agent({subagent_type: "<type-a>", description: "<3-word desc>", prompt: "<self-contained brief for worker A>"})
Agent({subagent_type: "<type-b>", description: "<3-word desc>", prompt: "<self-contained brief for worker B>"})
Agent({subagent_type: "<type-c>", description: "<3-word desc>", prompt: "<self-contained brief for worker C>"})
```

Dispatch all workers in a SINGLE message with multiple Agent tool calls so they run concurrently.

**Each worker prompt MUST include:**
1. Exact scope boundary (what to do AND what NOT to do)
2. Expected output artifact (file path, format, contents)
3. Evidence requirements (tool outputs, test results, file paths)
4. Token budget (e.g., "complete within 50K tokens")
5. Instruction to report failures honestly, not fabricate success

### Architecture D: Mixed (Tree dependency)

Parallel branches with sequential steps within each branch:

```
# Branch 1 (sequential):
Step 1a: Skill(...) → Gate → Step 1b: Skill(...)

# Branch 2 (sequential, parallel with Branch 1):
Step 2a: Agent(...) → Gate → Step 2b: Agent(...)
```

---

## Phase 3: Evidence Verification

After ALL workers complete (parallel) or each step completes (chain), verify before synthesis.

### Step 3.1: Per-Worker Verification

For each worker output, check:

| Gate | Question | Pass Condition |
|---|---|---|
| **Scope** | Did the worker stay within its assigned boundary? | Output covers assigned subtask; no scope creep |
| **Evidence** | Are tool outputs, test results, and file paths included? | At least one concrete artifact per claim |
| **Honesty** | Did the worker report failures honestly? | Failures are explicit, not hidden or fabricated |
| **Completeness** | Did the worker produce the expected output artifact? | Output artifact exists and matches format spec |

### Step 3.2: Cross-Worker Consistency Check (parallel only)

This is the centralized verification step that reduces error amplification from 17.2× to 4.4×:

1. Read ALL worker outputs
2. Check for contradictions between workers:
   - File conflicts (two workers editing the same file)
   - Semantic conflicts (contradictory claims or approaches)
   - Gap overlaps (two workers covering the same ground)
   - Coverage gaps (subtask not covered by any worker)
3. Record findings

### Step 3.3: Failure Handling

| Failure Type | Response |
|---|---|
| Worker timeout / token exhaustion | Do NOT retry same worker. Assess: is partial output usable? If yes, proceed with flag. If no, reassign to different worker with reduced scope. |
| Worker produced invalid output | Re-dispatch with explicit error feedback. Max 1 retry per worker. |
| Cross-worker contradiction | Orchestrator resolves. If resolution requires domain expertise beyond orchestrator, flag for human judgment. |
| Worker crashed (tool error) | Re-dispatch same task to fresh worker. Crashes are usually transient. |
| Multiple workers failed | Do NOT retry all. Report: which workers failed, why, and what partial results exist. |

**Hard constraint: Maximum 1 retry per worker. Never retry a worker more than once.**
Cascading retries are the mechanism behind coordination collapse.

---

## Phase 4: Synthesis

After all worker outputs pass verification (or failures are documented):

### Step 4.1: Merge Outputs

Combine verified worker outputs into the final deliverable. The orchestrator writes the synthesis
itself — it does NOT delegate synthesis to a worker.

### Step 4.2: Document the Architecture Decision

Include in the output:

```markdown
## Orchestration Record

- **Task structure**: <independent | chain | tree | merge>
- **Architecture**: <single agent | prompt chaining | parallel workers | mixed>
- **Agent count**: <N>
- **Models used**: <orchestrator model> / <worker models>
- **Evidence**: <summary of verification results>
- **Failures**: <which workers failed, how handled>
- **Reference**: Kim et al. (2025), arXiv:2512.08296
```

### Step 4.3: Record for Learning

If the project has an experience directory (`{project_root}/docs/agentic/experience/` or configured
`experience_dir`), append a one-paragraph note recording what architecture was used, whether it
worked, and any surprises. This builds the evidence base for future architecture selection.

---

## Phase 5: Handoff

### Step 5.1: Create or Update Task Card

If the project uses task cards (`conventions.task_card_format` is set):

```markdown
---
task_id: <today>-<slug>
status: complete
architecture: <single | chain | parallel | mixed>
agent_count: <N>
orchestrator_model: <model>
---
```

### Step 5.2: Commit (if project conventions include commit)

```
git add <changed files>
git commit -m "<imperative summary of what was done>"
```

### Step 5.3: Report

Output a one-paragraph summary of:
- What the task was
- What architecture was used and why
- What each worker produced (one line each)
- What verification found (contradictions, failures, gaps)
- What the final deliverable is

---

## Guardrails

### Hard Constraints (MUST follow)

1. **NEVER dispatch more than 5 parallel agents** without explicit decomposability justification
2. **NEVER use multi-agent for sequential/chain tasks** — single agent or prompt chaining only
3. **ALWAYS run cross-worker consistency check** before synthesis in parallel architectures
4. **ALWAYS use orchestrator model ≥ strongest worker model**
5. **Max 1 retry per failed worker** — never retry a worker more than once
6. **Workers produce evidence; orchestrator verifies evidence; only verified outputs enter synthesis**

### Soft Guidelines (SHOULD follow)

7. Prefer heterogeneous models over homogeneous (diversity beats quantity)
8. Prefer 2–3 agents over 4–5 when task decomposability is uncertain
9. Record architecture decisions for future learning
10. If a worker fails, report the failure honestly — do not fabricate a replacement output
11. If verification reveals contradictions, flag them — do not silently pick one side

### Anti-Patterns (NEVER do)

12. Role-based splitting ("let's have a planner, coder, tester, reviewer") — split at context boundaries, not roles
13. LLM routing for fixed control flow — if the sequence is known, hardcode it
14. Parallel dispatch when subtasks share state — if workers must read each other's output, use sequential chaining
15. Delegating synthesis to a worker — the orchestrator owns synthesis

---

## Claude Code Integration

This skill uses only standard Claude Code tools. No platform-specific MCP tools required.

| Tool | Use |
|---|---|
| `Skill` | Dispatch to project skills for sequential/chained work |
| `Agent` | Dispatch to project agents or built-in types (Explore, Plan) for parallel work |
| `TaskCreate` / `TaskUpdate` | Track worker tasks and pipeline steps |
| `Read` | Verify worker outputs, check for cross-worker contradictions |
| `Write` | Create synthesis deliverable, task card, architecture record |
| `Bash` | Run verification commands (tests, linters), git operations |
| `Glob` / `Grep` | Pre-dispatch exploration to understand task scope |

**Tool selection by phase:**
- Phase 1 (Analysis): Read, Glob, Grep — read-only exploration
- Phase 2 (Dispatch): Agent, Skill — worker spawning
- Phase 3 (Verify): Read — cross-read worker outputs
- Phase 4 (Synthesis): Write — orchestrator writes synthesis
- Phase 5 (Handoff): Write, Bash — task card, commit

---

## Quick Reference Card

```
Task received
  │
  ├─ Trivial? → Do it directly (skip orchestrator)
  │
  └─ Non-trivial?
       │
       ├─ Step 1: Decompose & classify dependency structure
       │     │
       │     ├─ Chain → Single agent or prompt chaining (Architecture A/B)
       │     │
       │     ├─ Independent → Parallel workers (Architecture C)
       │     │     ├─ 2–3 agents: default
       │     │     ├─ 4–5 agents: only with clean interfaces
       │     │     └─ 6+: HARD STOP — justify or batch
       │     │
       │     └─ Tree/Mixed → Mixed (Architecture D)
       │
       ├─ Step 2: Dispatch workers with scoped briefs
       │
       ├─ Step 3: Verify each worker (scope, evidence, honesty, completeness)
       │     └─ Cross-worker consistency check (parallel only)
       │
       ├─ Step 4: Synthesize verified outputs
       │     └─ Record architecture decision
       │
       └─ Step 5: Handoff (task card, commit, report)
```

## Version

- **Version**: 1.0.0
- **Date**: 2026-05-29
- **Status**: Seed — based on 13 evidence-based design principles; needs project-specific field testing
- **Design Principles**: See `docs/research/orchestrator-design-principles.md` (GCS project)
- **Academic Foundation**: 7 papers (Kim et al. 2025 through Dente et al. 2026)
- **Portability**: Project-agnostic. Requires only Claude Code standard tools. Configure via Project Configuration section.
