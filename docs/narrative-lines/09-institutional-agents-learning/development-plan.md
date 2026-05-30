# 09 — Institutional Agents and Learning

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`
Baseline: `docs/architecture/70-visualization/narrative-line-level-baseline-20260530.md`

## Current Level

**Developing (3.0)** — lowest in Arc 3; agentic-SE operating layer (5.0) and
governance (4.0) bracket it on both sides.

## Root Cause: The Infrastructure-Execution Gap

This line has the full infrastructure layer (registry, scorecard, naming
convention, generation pipeline, operating standard, templates, candidate
table, asset inventory, cross-reference matrix) but thin operational reality.
The steel frame is built; the building has almost no floors.

The gap is not absence of design. It is absence of **exercised evidence
distributed across agents, automated integration, and a closed learning loop.**

## Detailed Gap Diagnosis

### Gap 1 — Evidence Concentration (Critical)

| Agent | Maturity | Examples | Evals |
|-------|----------|----------|-------|
| I001 Bladesmith | Promoted (10/10) | 20+ | 1 refusal eval |
| I002 Tailor | Practiced, promoted seed (8/10) | 6 | 1 refusal eval |
| I003 Atelier Steward | Seed (6/10) | 1 | 1 refusal eval |
| I004 Art Director | Seed (6/10) | 2 | 1 refusal eval |
| I005 Acceptance Officer | Seed (5/10) | 0 | 1 refusal eval |
| 9 other candidates | Candidate | 0 | 0 |

I001 has 20+ examples. The other 4 seed agents combined have 9 examples. The
remaining 9 candidates have zero. This is a single-point-of-failure: if
Bladesmith is the only operational agent, "institutional agents" is a
one-agent show.

**Why this matters**: A narrative line about *institutional* agents requires
evidence that multiple agents exercise independent judgment across different
trigger conditions. One very active agent proves the concept works, not that
the institution works.

### Gap 2 — Candidate Pipeline Blockage (Critical)

9 agents exist in `.claude/agents/` with prompts written but no templates,
refusal evals, or real examples:

| Agent | Has prompt | Has template | Has refusal eval | Has example |
|-------|:----------:|:------------:|:-----------------:|:-----------:|
| gardener | yes | no | no | 0 |
| governance-sentinel | yes | no | no | 0 |
| night-watch | yes | no | no | 0 |
| bookkeeper | yes | no | no | 0 |
| collation-officer | yes | no | no | 0 |
| demo-producer | yes | no | no | 0 |
| benchmark-scout | yes | no | no | 0 |
| release-shepherd | yes | no | no | 0 |
| git-session-steward | yes | no | no | 0 |

The operating standard requires "at least two real sessions of use" before
seed creation, but there is no mechanism to create the *first* use. Candidates
wait passively for a task that matches their trigger — they cannot be
exercised proactively.

**Why this matters**: The candidate-to-seed pipeline is a birth bottleneck.
Without a way to turn candidates into seeds, the agent population cannot grow
beyond the original 5.

### Gap 3 — No Agent at Institutional (Structural)

The maturity pipeline is:

```
Candidate (9) → Seed (2) → Practiced (1) → Promoted (1) → Institutional (0)
                  I003/I004    I002           I001
```

No agent has reached Institutional — the tier defined as "standing project
capability with ownership, operating standard, evals, and review cadence."
I001 is closest, but the review cadence and ownership aspects are
undocumented.

**Why this matters**: The top tier being empty means the entire concept of
"institutional" is aspirational. The line cannot claim to have institutional
agents when none exist at that level.

### Gap 4 — No Automated Integration (Structural)

No institutional agent is wired into:

- Pre-commit or pre-push hooks
- CI/CD pipeline stages
- Quality gate execution (the validator tools exist but agents don't run them)
- Lifecycle runbook as a **required** step (they are "recommended rhythms")
- The `agentic_toolkit.py` as automated checks

Agents are invoked ad-hoc by a human or by Claude during a session. They are
not systemically triggered.

**Why this matters**: Without automated integration, institutional agents are
conversational patterns, not institutional mechanisms. A "night watch" that
never runs at night is a name, not an agent.

### Gap 5 — Learning Loop is Open (Structural)

The current learning flow:

```
Session → bladesmith forging note → experience/ directory → (end)
```

Missing links:

- Forging notes are not systematically reviewed to produce skill patches
- No agent checks whether a recorded lesson changed subsequent behavior
- No mechanism exists to retire a lesson that proved wrong or situational
- Eval failures don't feed back into agent prompt or template updates
- The scorecard is reviewed manually, not on a trigger

**Why this matters**: "Learning" in the narrative line name implies a closed
loop. An open loop means the project accumulates notes but doesn't adapt.

### Gap 6 — Evals Are Prompt-Level, Not Executable (Structural)

All governance evals (E-GOV-001 through 008) are markdown files describing
scenarios. None are executable tests. E-GOV-001 has exercised evidence from
real sessions but no validator candidate has been built.

The eval pipeline:

```
L1 (eval candidate) → L2 (prompt-level eval) → L3 (validator candidate) → L4 (default gate)
```

All existing evals are at L2. None have reached L3.

**Why this matters**: Evals that can't be run can't catch regressions.
"Evidence" that can't be verified is documentation, not evidence.

### Gap 7 — Agent Exercise Is Ad-Hoc (Process)

There is no process for deciding "which agent should handle this task." The
operating standard says to answer four questions before invoking an agent,
but there is no gate that checks whether the right agent *was* invoked.

Specifically:

- The `task-scoped-session-closer` skill sequences bladesmith post-task, but
  this is the only hard-wired agent invocation
- Tailor is invoked "every 3-5 related sessions" — completely ad-hoc
- Acceptance Officer has never been exercised on a real task
- Night-Watch has a full pipeline spec but has never run

**Why this matters**: Without deliberate exercise, agents with narrow trigger
conditions (acceptance-officer, night-watch, bookkeeper) will never accumulate
examples organically. They must be deliberately exercised.

### Gap 8 — Scorecard Has No Teeth (Process)

The scorecard gives I005 a 5/10 and says "collect two real acceptance reviews
before promotion." But there is no mechanism that prevents I005 from being
invoked as if it were promoted, or that forces the two reviews to happen.

The scorecard is diagnostic, not prescriptive. It describes what should happen
but doesn't make it happen.

**Why this matters**: A scorecard that only reports state doesn't drive state
changes. The promotion rules exist but are not enforced by any tool or gate.

## Comparison With Peer Lines in Arc 3

| Line | Level | Key difference from 09 |
|------|-------|----------------------|
| 06 Agentic-SE operating layer | Very strong (5.0) | Has executable artifacts: task cards, runbooks, toolkit validators, archives. These are *used* in every session. |
| 07 Quality gates | Strong (4.0) | Has executable validators in `agentic_toolkit.py` and CI matrix. Gates *run*, not just documented. |
| 10 Git/worktree/PR governance | Strong (4.0) | Has exercised eval evidence and a concrete validator candidate backlog item. |

The pattern is clear: lines become Strong when they have **executable
artifacts that run without human judgment call each time.** Line 09 stays
Developing because its artifacts (registry, scorecard, templates) are
reference documents, not executable mechanisms.

## What "Strong (4.0)" Would Look Like

For this line to reach Strong, the following would need to be true:

1. At least 3 agents at Promoted or higher, with distributed evidence
2. At least 1 agent at Institutional with documented ownership and review cadence
3. At least 2 governance evals at L3 (validator candidate) with passing tests
4. At least 1 agent integrated into an automated trigger (CI, hook, or
   lifecycle runbook required step)
5. A closed learning loop: at least one instance where a forging note led to a
   skill/template/runbook change, and the change was verified
6. The candidate pipeline is unblocked: at least 3 candidates advanced to seed
   with real exercise evidence

## Development Plan

### Principle

**Turn reference documents into executable mechanisms.** Every phase below
creates something that runs, checks, or enforces — not something that
describes.

### Phase 1 — Unblock the Candidate Pipeline (next 2-3 sessions)

The highest-leverage action is to create a deliberate exercise mechanism so
candidates don't wait passively for matching tasks.

#### 1.1 — Advance acceptance-officer to Practiced

Acceptance Officer is the most immediately exercisable agent: every non-trivial
task completion is a trigger. It already has a prompt, gate template, and
refusal eval. It needs 2 real exercises.

**Concrete actions**:
- On the next 2 non-trivial task closures, invoke acceptance-officer as an
  independent evidence gate **before** running task-scoped-session-closer
- Record each exercise at `005-acceptance-officer/examples/`
- Each exercise must produce a gate decision (accept / accept_with_notes /
  return_for_evidence / return_for_scope)

**Acceptance**: 2 real acceptance reviews with gate decisions and evidence links.

#### 1.2 — Create seed packages for 3 high-signal candidates

Three candidates have clear triggers that are likely to fire soon:

| Candidate | Trigger expected | Priority rationale |
|-----------|-----------------|-------------------|
| bookkeeper | Token audit v2 complete; cost questions active | Already has real data to analyze |
| collation-officer | Architecture docs vs implementation may have diverged after Steps 52-55 | Solver changes create drift opportunity |
| gardener | Stale references from narrative map refresh; `.codex/` clutter | Small items accumulate every session |

**Concrete actions**:
- For each, create `templates/` (output template) and `evals/` (one refusal eval)
- Do NOT create `examples/` until a real exercise happens
- Write a one-paragraph "exercise trigger" that a future session can use to
  know when to invoke this agent

**Acceptance**: 3 candidate agents now have templates + refusal evals in their
institutional-agents directories (or `.claude/agents/` prompt files).

#### 1.3 — Run one night-watch calibration run

Night-Watch has the most detailed pipeline spec of any candidate. It needs one
real run to move from candidate to seed.

**Concrete actions**:
- Execute a manual night-watch run covering: stale task check, doc-validation
  pass, dependency inventory check, git worktree hygiene
- Create dated run directory at `docs/agentic/nightly-runs/2026-05-30/`
- Record findings, false positives, and a calibration note
- Create refusal eval: refuse to commit/push/merge from night-watch role

**Acceptance**: One dated night-watch run directory with findings artifact.

### Phase 2 — Build Executable Evals (next 3-5 sessions)

#### 2.1 — Build E-GOV-001 validator candidate

This is the highest-leverage governance action and is already in the
weakness plan (P1.1). It bridges lines 09 and 10.

**Concrete actions**:
- Create `tools/governance/check_staged_scope.py`
- Compares `git diff --cached --name-only` against task-card affected paths
- Returns PASS / FAIL / SKIP with documented false-positive cases
- Add a test that verifies detection of unrelated dirty-file staging
- Wire into `agentic_toolkit.py` as `validate-staged-scope`

**Acceptance**: Python validator exists, passes its own test, documented
false-positive notes. This is an L3 eval.

#### 2.2 — Build E-GOV-003 validator candidate (evidence-free completion)

**Concrete actions**:
- Create `tools/governance/check_completion_evidence.py`
- Checks that a completed-task report has: task card link, git diff summary,
  evidence artifact links, and a gate decision
- Returns PASS (all evidence categories present), FAIL (missing required
  category), or SKIP (not a completed-task directory)
- Add test with a deliberately evidence-free report

**Acceptance**: Python validator exists with test.

#### 2.3 — Make acceptance-officer refusal eval executable

Acceptance Officer's refusal eval (`refuse-evidence-free-acceptance.md`)
currently describes a scenario. Make it runnable.

**Concrete actions**:
- Create a test fixture: a completed-task report with missing evidence
- Script the check: does the acceptance report identify the missing evidence?
- Add to `tools/governance/` alongside the other validators

**Acceptance**: Runnable test that verifies the acceptance-officer refuses
evidence-free completion.

### Phase 3 — Close the Learning Loop (next 4-6 sessions)

#### 3.1 — Forging-note-to-action pipeline

**Concrete actions**:
- Review the last 10 bladesmith forging notes (2026-05-24 through 2026-05-30)
- Classify each as: `action_taken`, `deferred_with_trigger`, `one_off`,
  `superseded`, or `still_open`
- For any `still_open` note older than 2 weeks, create a gardener task or
  explicit deferral with trigger condition
- Update at least one skill, template, or runbook based on a forging note
- Record the change and verify it in a subsequent session

**Acceptance**: At least one closed loop: forging note → action → verification.
All forging notes older than 2 weeks classified.

#### 3.2 — Agent exercise log and trigger registry

**Concrete actions**:
- Add a section to the agent/skill asset inventory: "Last exercised" date
  for each agent
- Create a simple trigger registry: for each agent, list the conditions that
  should cause its invocation
- After each non-trivial task closure, check the trigger registry and note
  which agents should have been invoked but weren't

**Acceptance**: Trigger registry exists. At least one post-task check
identifies a missed agent invocation.

#### 3.3 — Promote I002 Tailor to Promoted

Tailor has 6 examples, a full package, and a score of 8/10. It's the
closest agent to promotion after I001.

**Concrete actions**:
- Run a formal promotion review using the scorecard
- Document the decision at `002-tailor-stitch-timeline/promotion-YYYYMMDD.md`
- Update registry and scorecard

**Acceptance**: I002 at Promoted with promotion record.

### Phase 4 — First Institutional Agent (next 6-10 sessions)

#### 4.1 — Advance I001 Bladesmith to Institutional

Bladesmith is Promoted (10/10) with 20+ examples. The gap to Institutional
is: ownership, operating standard, evals, and review cadence.

**Concrete actions**:
- Document ownership: who decides when Bladesmith's prompt or template changes
- Define review cadence: e.g., review forging notes monthly for stale rules
- Create a second refusal eval (currently has 1; Institutional needs 2+)
- Ensure Bladesmith is referenced from lifecycle runbook as a standard
  post-task step (it already effectively is via session-close-orchestrator)
- Formalize: write the institutional promotion record

**Acceptance**: I001 at Institutional with documented ownership, review
cadence, and at least 2 refusal evals.

#### 4.2 — Wire one agent into an automated trigger

**Concrete actions**:
- Choose the agent with the most automatable trigger (night-watch via cron,
  or acceptance-officer via task-closure hook)
- Implement the trigger: cron job, pre-commit hook, or lifecycle runbook
  required step
- Run it automatically at least once and verify the output

**Acceptance**: One agent runs without a human deciding to invoke it.

### Phase 5 — Distributed Evidence (ongoing, next 8-12 weeks)

The long-term health of this line depends on evidence distribution — not one
very active agent and many inactive ones.

#### 5.1 — Quarterly agent exercise review

**Concrete actions**:
- Each quarter, review the trigger registry and exercise log
- Any agent not exercised in the quarter gets either: a deliberate exercise
  session, a deferral with trigger condition, or a demotion/candidate-merge
  decision

#### 5.2 — Candidate backlog grooming

**Concrete actions**:
- Review the candidate table quarterly
- Merge overlapping candidates (as was done for Curator and Helmsman)
- Promote candidates that have accumulated trigger pressure
- Remove candidates whose triggers never materialized

## Dependency Graph

```
Phase 1 (unblock pipeline)
  ├── 1.1 acceptance-officer → practiced     ← independent, start immediately
  ├── 1.2 seed packages for 3 candidates      ← independent, start immediately
  └── 1.3 night-watch calibration run          ← independent, start immediately

Phase 2 (executable evals)
  ├── 2.1 E-GOV-001 validator                  ← independent, start immediately
  ├── 2.2 E-GOV-003 validator                  ← independent, can parallel 2.1
  └── 2.3 acceptance-officer eval executable   ← depends on 1.1

Phase 3 (closed learning loop)
  ├── 3.1 forging-note review                  ← independent, start immediately
  ├── 3.2 trigger registry                     ← independent, start immediately
  └── 3.3 I002 Tailor promotion                ← independent, can run any time

Phase 4 (first institutional)
  ├── 4.1 I001 → Institutional                 ← benefits from 3.1
  └── 4.2 automated trigger                    ← depends on 1.3 or 2.1

Phase 5 (distributed evidence)
  ├── 5.1 quarterly review                     ← ongoing
  └── 5.2 candidate grooming                   ← ongoing
```

## What Does NOT Need to Happen

These are deliberate non-goals to prevent process sprawl:

1. **Do not create more candidate roles.** The candidate table has 10 entries;
   9 are unimplemented. Adding more names before existing ones have evidence
   makes the ratio worse.

2. **Do not add more scorecard dimensions.** The 7-dimension system is
   adequate. Adding dimensions before the existing ones drive real decisions
   is measurement without action.

3. **Do not require every agent to reach Promoted.** Some agents serve narrow
   triggers (release-shepherd fires only near releases). Seed or Practiced is
   the right ceiling for narrow-trigger agents.

4. **Do not automate agent invocation before manual exercise proves value.**
   An automated night-watch that produces noise is worse than no night-watch.
   Manual calibration runs must precede automation.

5. **Do not create a "meta-agent" to manage agents.** The scorecard and asset
   inventory already serve this function. A meta-agent adds a layer without
   adding execution.

## Scorecard: What Moves the Level

| Condition | From | To | When |
|-----------|------|----|------|
| 3+ agents at Promoted with distributed evidence | Developing (3.0) | Strong but split (3.5) | Phase 3 complete |
| 1+ agent at Institutional, 2+ L3 evals, 1+ automated trigger | Strong but split (3.5) | Strong (4.0) | Phase 4 complete |
| All 5 seed+ agents exercised in current quarter, learning loop closed | Strong (4.0) | Very strong (5.0) | Phase 5 sustained |

## Dependencies

- **Agentic-SE operating layer (06)**: The operating layer determines when
  agents are invoked. Phase 4.2 requires a hook point in the lifecycle runbook.
- **Quality gates (07)**: Agent eval evidence is a quality gate category.
  Phase 2 creates validators that bridge lines 07 and 09.
- **Git/worktree/PR governance (10)**: E-GOV-001 bridges lines 09 and 10.
  Phase 2.1 is shared work.

## Related

- Arc 3: Agentic Organization
- `docs/agentic/institutional-agent-registry-and-scorecard.md`
- `docs/agentic/institutional-agents/`
- `docs/agentic/evals/`
- `docs/agentic/agent-skill-asset-inventory.md`
- `docs/agentic/agent-skill-development-plan.md`
- `docs/agentic/narrative-weakness-development-plan-20260530.md`
- `docs/agentic/agentic-se-workflow-operations-plan-20260530.md`
