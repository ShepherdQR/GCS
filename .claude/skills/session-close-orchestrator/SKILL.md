---
name: session-close-orchestrator
description: Unified session-closing orchestrator for GCS. Invoke at the end of every non-trivial session to run the full close pipeline: archive session history, extract reusable experience, evaluate skill/agent promotion candidates, generate token benefit report, and push. This is the single entry point — it sequences task-scoped-session-closer, bladesmith-quench-forge, bookkeeper, and gcs-token-audit-steward in order.
---

# Session Close Orchestrator

## Start Here

Use this skill at the end of every non-trivial GCS session. It runs the full
close pipeline so no step is forgotten and all outputs land in the right place.

**One invocation covers all five requirements:**

1. Session history → persistent archive md
2. Experience extraction → experience doc
3. Skill/agent promotion evaluation → candidate decision
4. Token benefit report → data-driven efficiency analysis
5. Git commit + push → durable handoff

## Entry Rule

Invoke when:
- A session is ending and the work was non-trivial (more than a typo or status
  check)
- The user says "close session", "wrap up", "finish up", "总结", "关闭",
  "归档", or "push"
- A PDCA cycle is complete and the next session needs a clean handoff

Skip only when:
- The session was a trivial chat, status check, or single-line fix
- The lifecycle runbook explicitly allows chat-only closure

## Pipeline

Run these steps in order. Do not skip steps unless the user explicitly says so.
If a step fails, report the failure and continue to the next step.

---

### Step 0: Task Card Gate

**What**: Verify that a task card exists for the current session's work before
proceeding with closeout. If no task card exists, auto-create one.

**Check**:

1. Read `.claude/current-task` if it exists. If it points to a valid file, go
   to step 2.
2. If `.claude/current-task` is missing or the file it points to does not exist,
   auto-create a task card:

   a. Classify the work from the session conversation:
      - `scope`: `implementation` | `docs` | `tool` | `architecture` | `fixture` | `ci` | `review` | `maintenance`
      - `risk`: `low` (docs/config only) | `medium` (tooling/quality gates) | `high` (solver/runtime/IO/viewer)
      - `owner`: the best-fit steward skill from CLAUDE.md's skill table

   b. Create the file at `docs/agentic/tasks/<today>-<slug>.md`:

      ```markdown
      ---
      task_id: <today>-<slug>
      status: complete
      request: "<one-sentence summary of what was done>"
      scope: <scope>
      risk: <risk>
      owning_agent: <owner>
      specialist_agents:
        - none
      affected_contracts:
        - none
      affected_paths:
        - <paths from git diff --stat>
      required_evidence:
        - validate-docs
      human_gate_required: false
      human_gate_reason: ""
      ---

      # <today>-<slug>

      ## Scope

      <one paragraph>

      ## Evidence Bundle

      <key commands run and their results>

      ## Residual Risks

      <remaining uncertainty>
      ```

   c. Write `.claude/current-task`:
      ```
      task_card: docs/agentic/tasks/<today>-<slug>.md
      created: <today>
      ```

3. If the task card exists with `status: draft`, update it to `status: complete`
   and fill the evidence bundle if it was still a planning skeleton.

**Output**: A confirmed task card at `docs/agentic/tasks/<date>-<slug>.md` and
an up-to-date `.claude/current-task`.

**Rationale**: The task card is the "plan before act" contract. Auto-creating
one on closeout prevents the "implement first, archive directly" drift pattern
while keeping the pipeline fast — the card is filled from what actually
happened.

---

### Step 1: Token Audit — Import & Report

**What**: Import the current session's JSONL transcript into the audit database,
then generate the token benefit report with baseline comparison.

```bash
# Import current session data
python -m tools.token_audit db import --project GCS-A --force

# Generate benefit report with baseline comparison (default: on)
python -m tools.token_audit report --format markdown
```

**The report automatically includes**:
- One-sentence efficiency analysis comparing this session to calibrated
  P50/P75 baselines (e.g. "产出效率位于历史前25%，缓存命中率高于历史中位数")
- Baseline comparison column in the Efficiency Metrics table
- Token usage, cost, cache efficiency, BEI scores
- Chapter breakdown (if CCD chapter markers were used)

**Output**: Token usage, cost, cache efficiency, BEI scores, baseline comparison.

Save the report to `docs/reports/token-audit/session-<date>.md`.

---

### Step 2: Task Archive

**What**: Create the completed-task archive.

- Classify the task: scope, risk, affected paths, non-goals.
- Create `docs/completed-tasks/<date-slug>/README.md`.
- Link task card, changed files, evidence, decisions, risks, follow-up.

Use the `task-scoped-session-closer` conventions:
- Do not archive raw chat logs.
- Record skipped checks as risk, not as passes.
- Stage only scoped files for commit.

---

### Step 3: Experience & Promotion Evaluation

**What**: Determine whether the session produced reusable material.

Answer each of these explicitly in the archive:

| Material | Decision | Reason / Evidence |
|----------|----------|-------------------|
| Experience | yes / candidate / no | What pattern was learned? |
| Skill | active / candidate / no | Ready for promotion? Threshold met? |
| Agent | active / candidate / no | Institutional role justified? |

When a candidate is identified:
- Name the candidate.
- Record the target path or agent name.
- Note the evidence threshold for revisiting.
- Link to the specific session evidence that supports promotion.

If the answer is "no" for all three, write one sentence explaining why.

When experience material IS identified (yes or candidate), invoke
`bladesmith-quench-forge` to forge it into a durable artifact under
`docs/agentic/experience/`.

---

### Step 4: Token Benefit Report

**What**: Include the token benefit summary as a section in the archive README.

Embed the key table from Step 1's report:

```markdown
## Token Benefit Summary

> <one-sentence efficiency analysis from report>

| Metric | Value |
|--------|-------|
| Session Duration | <duration> |
| Model | <model_id> |
| Total Tokens | <total> (in: <input> / out: <output>) |
| Cache Read Tokens | <cache_read> |
| Cache Hit Rate | <rate> |
| Estimated Cost | $<cost> |
| Lines Changed | +<added>/-<removed> |
| Commits | <count> |
| BEI Composite | <score> (<rating>) |
| Cost per Commit | $<cpc> |

### Baseline Comparison

| Metric | Session | P50 | P75 | Status |
|--------|---------|-----|-----|--------|
| LoC/1M tokens | <value> | <p50> | <p75> | Top 25% / Above median / Below median |
| Cache Hit Rate | <value> | <p50> | <p75> | Top 25% / Above median / Below median |

### Key Findings

- <finding 1>
- <finding 2>
- <finding 3>
```

Also run the full trend report to update the project-level view:

```bash
python -m tools.token_audit trend --days 7
```

---

### Step 5: Commit & Push

**What**: Stage only scoped files, commit with a concise message, push.

Before commit:
```bash
git status
git diff --stat
```

Commit message format: `<action>: <what changed>` (imperative, lowercase).

Then:
```bash
git push
```

---

## Required Output

At close, the following must exist on disk and be pushed:

1. `.claude/current-task` — pointing to the current task card (Step 0)
2. `docs/agentic/tasks/<date-slug>.md` — task card with `status: complete`
   and filled evidence (Step 0)
3. `docs/completed-tasks/<date-slug>/README.md` — task archive with embedded
   token benefit summary (Step 2)
4. `docs/reports/token-audit/session-<date>.md` — full token benefit report
   (Step 1)
5. If experience extracted: `docs/agentic/experience/<slug>/README.md` (Step 3)
6. Commit on `master` containing all of the above (Step 5)

## Guardrails

- Do not skip Step 0 (task card gate) — the task card is the plan-before-act
  contract and every non-trivial session needs one.
- Do not skip Step 1 (token import) — it is the data foundation.
- Do not archive raw chat logs.
- Do not fabricate BEI scores; mark "N/A" when git data is unavailable.
- Do not promote a skill or agent from a single session without an explicit
  provisional label and evidence threshold.
- Do not skip the push step if the user has authorized direct push.
- Do not skip the experience/skill/agent evaluation table — "no" still needs a
  one-sentence reason.

## Claude Code Integration

When invoked:
- Use `Read` to check `.claude/current-task` and any existing task card.
- Use `Write` to create or update the task card and `.claude/current-task`.
- Use `Bash` to run `python -m tools.token_audit` commands for token data.
- Use `Bash` to run `git status`, `git diff`, `git log` for commit prep.
- Use `Write` to create the archive README, token report, and experience docs.
- Use `Read` to inspect session JSONL transcripts for metadata.
- Use `mcp__ccd_session__mark_chapter` to mark pipeline phase transitions.
- Use `TaskCreate` / `TaskUpdate` to track pipeline steps if the session is
  complex enough.
- For the experience/skill/agent evaluation, check Claude memory at
  `C:\Users\QR\.claude\projects\C--Codes-AI-GCS-A\memory\` for relevant
  patterns before deciding.
- At commit: stage only scoped files, use a concise imperative message, push
  when authorized.
