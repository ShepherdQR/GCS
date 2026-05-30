# Agentic-SE Workflow Operations Plan

Status: active
Date: 2026-05-30
Entry point: `docs/agentic/agentic-organization-operating-map.md`

## Thesis

The GCS agentic-SE operating system is now strong enough to be dangerous. It
has task cards, archives, quality gates, institutional agents, a permission
model, and an operating map. The next risk is not absence — it is **drift**:
the operating system slowly decoupling from the evidence it was built to
produce.

This plan defines how to run, maintain, and evolve the agentic-SE workflow so
that it continues to serve solver evidence, product evidence, governance, and
learning rather than becoming its own self-referential industry.

## Part I: Operating Philosophy

### The Prime Directive

> Every agentic artifact must trace back to solver evidence, product evidence,
> governance, or learning. If it cannot, it should remain a note, not become a
> process rule.

This is not a slogan. It is the test that every new process, skill, agent,
template, eval, and gate must pass. Apply it at every promotion decision, every
retrospective, and every roadmap review.

### The Four Laws of Agentic Operation

1. **Law of Evidence**: No claim of completion without verification evidence
   or explicit skipped-check risk rationale.

2. **Law of Scope**: Every non-trivial task has a named owner, a written
   boundary, and a task card. Files outside the boundary are not staged.

3. **Law of Memory**: A future session must be able to resume the project
   state without reading raw chat logs. Completed-task archives, timelines,
   indexes, and the narrative map are the durable memory surface.

4. **Law of Conservation**: Processes are not added without removing or
   consolidating an existing one. When a new gate, skill, or agent is
   promoted, an old one must be justified as still necessary or retired.

### The Tension To Manage

The agentic operating system exists in permanent tension between:

- **Discipline** (task cards, gates, archives, audits) — prevents chaos.
- **Velocity** (a single session going from request to push) — prevents paralysis.

The right balance is: discipline that pays for itself in reduced rework,
ambiguous handoffs, and lost context. When a process costs more time than the
rework it prevents, it is a candidate for simplification.

## Part II: The Lifecycle — Operation By Phase

### Phase A: Intake (Steps 0-2)

**Goal**: Turn a human request into a scoped, owned, boundary-clear task.

**Critical operations**:

1. Classify scope and risk using the runbook matrix (architecture /
   implementation / test / fixture / ci / docs / tool / review / maintenance
   × low / medium / high).

2. Choose workspace: shared checkout for read-only or single-session work;
   worktree for parallel writing sessions.

3. Create task card for non-trivial work. The task card is not bureaucracy —
   it is the contract that prevents scope creep, protects unrelated files, and
   tells the closer what "done" means.

4. Validate the task card before editing files:
   ```
   python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md
   ```

**Health checks**:
- Is every non-trivial task in the current batch covered by a task card or an
  explicit chat-only exception?
- Are any high-risk tasks missing a human gate or execution plan?
- Are worktree paths recorded for parallel sessions?

**Anti-pattern**: Creating a task card that says "do the thing" without naming
affected files, evidence gates, or excluded boundaries. A vague task card is
worse than no task card — it provides the illusion of discipline.

### Phase B: Context Loading (Step 3)

**Goal**: Load the minimum project state needed for the task without drowning.

**Critical operations**:

1. Read the narrative map (`95-gcs-narrative-map.md`) for strategic context.
2. Read the relevant architecture docs for the module being touched.
3. Read the task card and any predecessor task archives in the same area.
4. Do NOT read all of `docs/`. Do NOT replay raw chat logs. Trust the indexes
   and archives.

**Loading heuristic by scope**:

| Scope | Load |
|-------|------|
| Solver C++ | Target module contract doc, recent step reports, related fixture corpus docs. |
| UI/Viewer | UI architecture docs, viewer bridge contract, design-system conventions. |
| Agentic/governance | Operating map, lifecycle runbook, registry scorecard, eval roadmap. |
| Product/demo | Product brief, demo ladder, release checklist. |
| Fixture/scene | Corpus maturity ladder, scene schema docs, promotion rules. |
| Cross-cutting | Narrative map + operating map as minimum; then module docs for each touched area. |

**Health checks**:
- Did the session read at least the narrative map before mutating?
- Are architecture docs consulted for module-level work?

**Anti-pattern**: Reading everything "just in case." Context overload produces
false confidence — the agent thinks it understands more than it does.

### Phase C: Implementation (Step 4)

**Goal**: Edit, implement, or research inside the chosen boundary.

**Critical operations**:

1. Follow the owning skill's conventions (steward skills encode module-specific
   patterns, naming, and contract expectations).
2. Preserve unrelated dirty files. Never `git add -A` or `git add .`.
3. Keep solver runtime code free of agentic infrastructure (no imports of
   agentic tools in `src/gcs/`).
4. For parallel work: use independent agents only for sidecar tasks that do not
   share mutable state.

**Health checks**:
- Does `git status` show only scoped changes?
- Are any generated artifacts attributed to their source session?

**Anti-pattern**: Fixing "one small thing" outside the task card boundary
because it's convenient. Those small things accumulate into unscoped debt.

### Phase D: Verification (Step 5)

**Goal**: Prove the changed surface with the smallest meaningful checks.

**Critical operations**:

1. Run focused checks first — the ones that directly test the changed surface.
2. Run the quality gate that fits the scope:
   - Docs-only: `validate-docs`, `validate-inventory`, `validate-skills`,
     `check-dependencies`.
   - Implementation: the above plus focused tests, contract tests, CTest.
   - Fixture: the above plus scene validation, round-trip checks.
   - UI: the above plus visual QA, screenshot baselines, contrast checks.
3. Record skipped checks with reason and residual risk.

**The verification ladder** (cheapest → most expensive):

| Level | Check | When |
|-------|-------|------|
| V0 | Self-review of diff | Every task. |
| V1 | Agentic validators (docs, inventory, skills, deps) | Every non-trivial task. |
| V2 | Focused tests (unit, contract, fixture-specific) | Implementation, fixture, CI tasks. |
| V3 | Broad tests (CTest full suite) | Solver-semantic changes, before release. |
| V4 | Visual QA (screenshots, contrast, overflow) | UI/Viewer changes. |
| V5 | Replay evidence check | Runtime/history changes. |
| V6 | External baseline comparison | Benchmark claims. |

**Health checks**:
- Does the verification level match the scope?
- Are skipped checks recorded with rationale?
- Is the residual risk acceptable?

**Anti-pattern**: Running expensive broad tests to "prove" a docs-only change,
or running only validators for a solver-semantic change. Match the gate to the
risk.

### Phase E: Review and Archive (Steps 6-8)

**Goal**: Turn finished work into durable project memory.

**Critical operations**:

1. Review for scope control, dependency direction, public contract evidence,
   missing negative cases, skipped checks.
2. Create completed-task archive with evidence bundle.
3. Score the closure report (minimum 30 for non-trivial work):
   ```
   python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\<task>\README.md --min-score 30
   ```
4. Stage only scoped files. Commit with concise message. Push.
5. Update indexes, metrics dashboard, and narrative map if the task changes
   project-level state.

**The archive must answer five questions**:
1. What was the task? (link to task card)
2. What was done? (summary of changes)
3. What evidence proves it? (commands run, outputs, pass/fail)
4. What was skipped and why? (residual risk)
5. What should the next session know? (follow-up, experience notes)

**Health checks**:
- Does the archive score ≥ 30?
- Does the commit contain only scoped files?
- Are unrelated dirty files preserved and noted?

**Anti-pattern**: An archive that says "done" without commands, pass/fail
summaries, or skipped-check risk. This is evidence-free completion (E-GOV-003).

### Phase F: Learning (Step 9)

**Goal**: Convert repeated pressure into templates, evals, and institutional
memory without over-promoting one-off experiences.

**Critical operations**:

1. After each non-trivial task, ask: "Did anything surprise us?"
2. Create an experience record when:
   - The same omission appears twice.
   - A high-severity issue escapes review.
   - CI fails for a preventable workflow reason.
   - A skill, template, fixture, or tool would have prevented the failure.
3. Promote experience into process only after at least two occurrences or one
   severe near miss.
4. Review the institutional agent scorecard after each promotion candidate.

**Health checks**:
- Are there experience records for repeated friction?
- Has any one-off experience been promoted without a second example?

**Anti-pattern**: Creating a new rule, skill, or agent after a single
surprising event. One swallow does not make a summer.

## Part III: Governance Operations

### Permission Model

The permission threat matrix (`docs/agentic/permission-threat-matrix.md`)
classifies every action on five axes:

1. **Data access**: Is private repository data exposed?
2. **Content trust**: Is untrusted input consumed?
3. **Outbound channel**: Does data leave the local machine?
4. **Mutation scope**: What files/branches are written?
5. **Network surface**: What remote services are contacted?

Before any action that triggers three or more axes, explicitly note the
permission posture in the task card or archive.

### Eval Pipeline Operations

The eight governance evals (E-GOV-001 through E-GOV-008) live at different
maturity levels. The operations task is to move them rightward on the ladder
without skipping levels:

```text
L0 Note → L1 Prompt eval → L2 Template check → L3 Validator candidate →
L4 Opt-in gate → L5 Default gate
```

**Current priority**:
1. E-GOV-001: Move from L2 (exercised template evidence) to L3 (validator
   candidate). **Most actionable.**
2. E-GOV-003: Already partially enforced by score-closure-report. Monitor.
3. E-GOV-002: Gather one more PR-audit artifact before L3.
4. E-GOV-005: Keep at L2 until external publication workflow is active.
5. E-GOV-004, E-GOV-006, E-GOV-007, E-GOV-008: Maintain at current level;
   reassess after E-GOV-001 L3 is operational.

### Default Gate Policy

No new default gate is added without:
- At least two successful opt-in uses, or one severe near miss.
- Documented false-positive behavior.
- A bypass process.

The current default gates are:
- Task card for non-trivial work.
- Completed-task archive for non-trivial work.
- `validate-docs` for architecture/agentic docs changes.
- Scoped staging (no unrelated files in commits).

These are minimal and intentional. Resist the gravitational pull toward more
default gates.

## Part IV: Institutional Agent Management

### Promotion Cadence

The five institutional agents are at different maturity levels. The operations
task is to move each toward its next level **only when evidence supports it**.

| Agent | Current | Next target | Required evidence |
|-------|---------|-------------|-------------------|
| I001 Bladesmith | Promoted | Institutional | Ownership rotation, periodic review evidence, at least one rejected lesson. |
| I002 Tailor | Practiced | Promoted | Divergent timeline examples (solver thread, agentic thread, product thread). |
| I003 Atelier Steward | Seed | Practiced | Two more UI/figure convention-fit reviews. |
| I004 Art Director | Seed | Practiced | Two more visual reviews with rendered-artifact evidence. |
| I005 Acceptance Officer | Seed | Practiced | Two real acceptance reviews on completed tasks. |

### Agent Health Monitoring

Each institutional agent should be reviewed every 10-15 sessions or when its
trigger domain changes significantly:

1. Is the agent still being invoked for its intended trigger?
2. Are its outputs being used by downstream sessions?
3. Has it accumulated false positives or overclaiming behavior?
4. Does it need a new refusal eval based on recent experience?

### Candidate Backlog Triage

The ten candidate agents in the registry backlog should be promoted to seed
only when:
- A real task triggers the candidate's domain.
- The candidate adds value beyond what a skill or template already provides.
- A prompt, template, and refusal eval are written.

**Next candidate likely to promote**: Git Session Steward (pre-mutation
checklist already exists; needs one real push-safety intervention).

## Part V: Cross-Session Memory Architecture

### The Memory Surface

Cross-session memory is distributed across five artifact types:

| Artifact | Lifetime | What it preserves | Read by |
|----------|----------|-------------------|---------|
| Task cards | Until archive | Scope, owner, boundary, evidence plan. | Current session. |
| Completed-task archives | Permanent | What was done, evidence, skipped checks, follow-up. | Future sessions in the same domain. |
| Narrative map | Continuous | Strategic state of all 14 lines. | Every session. |
| Timelines (Tailor) | Continuous | Cross-session event ordering. | Planning and retrospective sessions. |
| Experience records | Permanent | Repeated friction, lessons, near misses. | Skill/agent promotion, process design. |

### Memory Integrity Rules

1. The narrative map is the single source of truth for strategic state. Update
   it after any task that changes a narrative line's level or next move.

2. Completed-task archives must be self-contained. A future reader should not
   need the raw chat log to understand what happened.

3. Timeline entries must cite specific archives, commits, or artifacts. No
   invented causality.

4. Experience records must name the specific trigger (which task, which
   failure) and the proposed remedy. Vague "we should be more careful" records
   are not actionable.

### The Index Obligation

Every new completed-task archive must be discoverable. The minimum is:
- Entry in the narrative map's next-task queue if it changes project direction.
- Entry in the metrics dashboard if it was a non-trivial lifecycle task.
- Entry in the Tailor timeline if it connects to other sessions.
- Entry in the completed-tasks index (if one exists) or the relevant module
  doc's "related tasks" section.

## Part VI: Quality Gate Operations

### Gate Selection Algorithm

```
if scope is docs-only:
    run validate-docs, validate-inventory, validate-skills, check-dependencies
    skip build, CTest, UI checks (record with rationale)
elif scope is implementation:
    run V1 validators + focused unit/contract tests + CTest
    skip UI checks unless viewer code changed
elif scope is fixture:
    run V1 validators + scene validation + round-trip checks
elif scope is UI/viewer:
    run V1 validators + visual QA + screenshot baselines + contrast checks
elif scope is CI/release:
    run V1 validators + full CTest + package smoke
```

### Metrics Dashboard Operations

Update `docs/agentic/metrics-dashboard.md` after:
- Every non-trivial task closure.
- Any high-risk task.
- Any task where a check was skipped for a meaningful reason.
- Any governance eval level change.

The trend history table must include at least one row with contract-test and
CTest results within the next five non-trivial implementation tasks.

### The Trend Mandate

The metrics dashboard currently has three data points, all docs-only. This is a
**visibility gap**. The next five non-trivial tasks must include at least two
that exercise code-level gates (V2 or above), and the trend table must record
them. Without code-level trend data, the quality story is incomplete.

## Part VII: Session Orchestration

### Single-Session Flow

```
session start
  → load narrative map + relevant context
  → classify request
  → create task card (if non-trivial)
  → implement inside boundary
  → verify with appropriate gate
  → review
  → archive
  → commit (scoped)
  → push
  → update indexes, metrics, narrative map
  → learn (if applicable)
session end
```

### Multi-Session Flow

When a task spans sessions:
1. The first session creates the task card and marks it as in-progress with a
   session-note.
2. Each subsequent session reads the task card and previous session-note before
   resuming.
3. The final session closes the task card, creates the archive, and updates
   all indexes.
4. The Tailor stitches the multi-session timeline.

### Parallel Session Safety

When multiple sessions edit different parts of the project:
1. Each session uses its own worktree.
2. Task cards declare affected paths explicitly.
3. Before commit, check that no other session's task card claims the same
   paths.
4. Merge order is recorded if branches depend on each other.

### Session Close Orchestration

The `session-close-orchestrator` skill sequences:
1. `task-scoped-session-closer` — archive, evidence, closure score.
2. `bladesmith-quench-forge` — extract reusable lessons.
3. `bookkeeper` — cost-benefit analysis.
4. `gcs-token-audit-steward` — token benefit report.

This is the standard close pipeline for non-trivial sessions. Do not skip it
for implementation, architecture, or governance sessions.

## Part VIII: Anti-Drift Mechanisms

### Drift Detection Signals

The operating system is drifting when:
1. Task cards are created but not read by the implementation phase.
2. Archives are written but never consulted by future sessions.
3. Quality gates always pass because they test the wrong surface.
4. Institutional agents are invoked but their outputs are ignored.
5. New processes are added without removing old ones.
6. The narrative map goes stale (no update for >10 non-trivial tasks).

### Drift Correction

When drift is detected:
1. Name the specific process that is drifting.
2. Identify whether it needs simplification, removal, or reinforcement.
3. If reinforcement: add a concrete trigger (e.g., "archive must score ≥ 30
   before commit").
4. If simplification: merge it with a related process or reduce its scope.
5. If removal: archive it as a retired process with a note on why it was
   removed.

### The Simplification Mandate

Every six months or every 50 non-trivial tasks (whichever comes first), conduct
a **process audit**:
1. List every active process, gate, skill, and institutional agent.
2. For each: what is the last task it improved? What evidence exists?
3. Mark as "active" (used in last 10 tasks), "dormant" (no recent use), or
   "overlapping" (duplicates another process).
4. Retire dormant processes. Merge overlapping ones. Justify active ones.
5. Update the operating map.

## Part IX: Evolution Roadmap

### Immediate (next 1-2 weeks)

1. **E-GOV-001 validator candidate**: Build and test. This is the first
   executable governance check and will set the pattern for all future
   validators.

2. **Metrics dashboard diversity**: Add at least one row with code-level gate
   results (CTest, contract tests) to break the docs-only pattern.

3. **Agent I005 first exercise**: Run the Acceptance Officer on one real
   completed task to gather seed-level evidence.

### Short-term (next 2-6 weeks)

4. **Governance validator pattern**: After E-GOV-001 L3 is stable, document the
   pattern (input, check logic, output format, false-positive handling) so that
   E-GOV-002 through E-GOV-008 can follow the same template.

5. **Tailor timeline divergence**: Produce separate solver-thread, agentic-thread,
   and product-thread timelines to move I002 toward "promoted."

6. **Skill usage audit**: Review which steward skills are being auto-invoked and
   which are dormant. Simplify or retire unused skills.

### Medium-term (next 2-6 months)

7. **Process audit**: First formal simplification audit per Part VIII.

8. **Candidate promotion wave**: Based on accumulated evidence, promote the
   strongest 2-3 candidates from the backlog (Git Session Steward, Bookkeeper,
   Collation Officer are likely first).

9. **Agentic-SE metrics v2**: Move beyond task-count metrics to flow metrics
   (time from request to push, rework rate, context-recovery time for a cold
   session).

### Long-term (6-12 months)

10. **Institutional knowledge base**: A queryable index of all completed-task
    archives, experience records, and architectural decisions — accessible to
    a cold session in under 60 seconds.

11. **Governance automation maturity**: At least three validators at L4 (opt-in
    gate), one at L5 (default gate), with documented false-positive rates.

12. **Operating system simplification**: The operating map should be shorter
    after 12 months than it is today, because the processes that survived have
    proven their value and the rest were retired.

## Part X: Operating Standards Summary

### Every Session

- Read narrative map before mutating.
- Classify scope and risk.
- Create task card for non-trivial work.
- Preserve unrelated dirty files.
- Run appropriate verification.
- Record skipped checks with rationale.

### Every Non-Trivial Task Closure

- Completed-task archive with evidence bundle.
- Closure score ≥ 30.
- Scoped commit (no unrelated files).
- Metrics dashboard update.
- Experience check (any surprises?).

### Every Narrative or Governance Change

- Narrative map refresh.
- Metrics dashboard refresh (if metrics changed).
- Figure 95 baseline refresh (if levels changed).

### Every 10-15 Sessions

- Institutional agent health review.
- Candidate backlog triage.
- Drift detection check.

### Every 6 Months or 50 Tasks

- Formal process audit (simplification mandate).
- Operating map review and update.
- Retire dormant processes.

## Anti-Patterns (repeated from operating map, reinforced here)

1. A process doc that cannot name the protected boundary it improves.
2. A completed archive that says "done" without validation or skipped-check risk.
3. A role marked institutional only because it has a clever name.
4. A demo that displays architecture but does not let a user inspect evidence.
5. An automated audit that implies approval, merge permission, or human review.
6. **New**: A quality gate that always passes because it tests the wrong surface.
7. **New**: A task card that is created but never read during implementation.
8. **New**: An experience record that names a problem without a specific trigger
   event and a proposed remedy.
