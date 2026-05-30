---
name: session-close-orchestrator
description: Unified session-closing orchestrator for GCS. Invoke at the end of every non-trivial session to run the full close pipeline: archive session history, extract reusable experience, evaluate skill/agent promotion candidates, generate token benefit report, and push. This is the single entry point — it sequences task-scoped-session-closer, bladesmith-quench-forge, bookkeeper, and gcs-token-audit-steward in order.
model: opus
priority: 90
exclusive: false
---

# Session Close Orchestrator

## Start Here

Use this skill at the end of every non-trivial GCS session. It runs the full
close pipeline so no step is forgotten and all outputs land in the right place.

**One invocation covers all six requirements:**

1. Session history → persistent archive md
2. Experience extraction → experience doc
3. Skill/agent promotion evaluation → candidate decision
4. Token benefit report → data-driven efficiency analysis
5. Output existence verification → mechanical gate before commit
6. Git commit + push → durable handoff

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
Each step uses explicit tool dispatch — no prose-only handoffs.

**Error handling per step:**
- If a step fails: capture the error, write it to the step output, continue to next step
- If a dispatched skill/agent fails: record failure reason, retry once with reduced scope; escalate on second failure
- All step outputs are written to disk before proceeding to the next step

---

### Step 0: Task Card Gate

**What**: Verify that a task card exists for the current session's work before
proceeding with closeout. If no task card exists, auto-create one.

**Dispatch**: Direct operations (Read, Write, Bash) — no sub-skill needed.

**Check**:

1. `Read` `.claude/current-task` if it exists. If it points to a valid file, go
   to Step 1.
2. If `.claude/current-task` is missing or the file it points to does not exist,
   auto-create a task card:

   a. Classify the work from the session conversation:
      - `scope`: `implementation` | `docs` | `tool` | `architecture` | `fixture` | `ci` | `review` | `maintenance`
      - `risk`: `low` (docs/config only) | `medium` (tooling/quality gates) | `high` (solver/runtime/IO/viewer)
      - `owner`: the best-fit steward skill from CLAUDE.md's skill table

   b. `Write` the file at `docs/agentic/tasks/<today>-<slug>.md`:

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
      token_budget:
        max_total: 500000
        budget_consumed: 0
      ---

      # <today>-<slug>

      ## Scope

      <one paragraph>

      ## Evidence Bundle

      <key commands run and their results>

      ## Residual Risks

      <remaining uncertainty>
      ```

   c. `Write` `.claude/current-task`:
      ```
      task_card: docs/agentic/tasks/<today>-<slug>.md
      created: <today>
      ```

3. If the task card exists with `status: draft`, update it to `status: complete`
   and fill the evidence bundle if it was still a planning skeleton.

**Error capture**: If classification fails, use defaults (`scope: maintenance`, `risk: low`, `owner: general-purpose`) and flag in task card.

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

**Dispatch**: Direct `Bash` operations.

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

**Error capture**: If `db import` fails, retry once with `--force` flag. If retry also fails, skip to `report` (may use cached data). If `report` fails, create a minimal manual report with token counts from the session transcript.

**Output**: Token usage, cost, cache efficiency, BEI scores, baseline comparison.

Save the report to `docs/reports/token-audit/session-<date>.md`.

**v2 Diagnostic** (if session has a session_id in the database):

```bash
# Generate v2 token economic diagnostic
python -m tools.token_audit diagnose --session <session-id>
```

Include the diagnostic card output in the completed-task archive README
under a `## Token Economic Diagnostic` section.

---

### Step 1.5: Session Output Summary

**What**: Create a top-level session output summary document that captures the
closing summary shown to the user as a persistent, scannable artifact.

**Dispatch**: Direct `Write` operation.

**Output**: `docs/reports/session-output-summary-<date>.md`

**Contents**:
- One-sentence summary of the session.
- Deliverables table: each with type, affected files, and status.
- Verification gates table: what was tested and the result.
- Remaining roadmap (if the work was part of a larger plan).
- Narrative line impact: which lines moved and why.
- Token benefit summary (inline from Step 1 report).
- Final commit reference.

**Template**:

```markdown
# Session Output Summary — <date>

Session: <title>
Date: <date>
Status: closed

## One-Sentence Summary
<one sentence>

## Deliverables
| # | Deliverable | Type | Files | Status |

## Verification Gates
| Gate | Result |

## Remaining Roadmap
...

## Narrative Line Impact
| Narrative line | Before | After | Change |

## Token Benefit
| Metric | Value |

## Commit
`<hash> <message>`
```

**Error capture**: If summary creation fails, record the failure and continue — the archive README (Step 2) serves as the fallback summary.

---

### Step 2: Task Archive

**What**: Create the completed-task archive with full evidence bundle.

**Dispatch**: Explicit `Skill()` call to task-scoped-session-closer.

```
Skill({
  skill: "task-scoped-session-closer",
  args: "archive task from card docs/agentic/tasks/<today>-<slug>.md
         Session scope: <scope>, risk: <risk>
         Changed files: <paths from git diff --stat>
         Evidence: token report at docs/reports/token-audit/session-<date>.md,
                   session summary at docs/reports/session-output-summary-<date>.md
         Output: docs/completed-tasks/<date-slug>/README.md"
})
```

**What the dispatched skill produces:**
- `docs/completed-tasks/<date-slug>/README.md` — task archive with evidence, decisions, risks, follow-up
- Classification: scope, risk, affected paths, non-goals
- Links to task card, changed files, evidence artifacts

**The dispatched skill enforces:**
- Do not archive raw chat logs.
- Record skipped checks as risk, not as passes.
- Stage only scoped files for commit.

**Verification**: After the skill completes, `Read` the archive README to verify it exists and has all required sections (Scope, Evidence Bundle, Decisions, Residual Risks, Follow-up).

**Error capture**: If task-scoped-session-closer dispatch fails, retry once. If retry also fails, create a minimal archive README with the session output summary embedded and a note: "Minimal archive — task-scoped-session-closer dispatch failed: <reason>".

---

### Step 3: Experience & Promotion Evaluation

**What**: Determine whether the session produced reusable material, and forge
it into durable artifacts when found.

**Dispatch**: Two-stage — direct evaluation table + conditional Agent dispatch.

**Stage 3a: Evaluate (direct operation)**

Answer each of these explicitly and write to the archive:

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

**Stage 3b: Forge experience (conditional Agent dispatch)**

When experience material IS identified (yes or candidate):

```
Agent({
  subagent_type: "bladesmith-quench-forge",
  description: "Forge session experience",
  prompt: "Forge experience from session <session-id>.
           Task card: docs/agentic/tasks/<today>-<slug>.md
           Archive: docs/completed-tasks/<date-slug>/README.md
           Experience type: <experience/skill/agent>
           Candidate name: <name>
           Target: docs/agentic/experience/<slug>/
           Evidence: <specific evidence from this session>
           Forge a durable artifact with README, prompt, template, and eval scaffold."
})
```

**Stage 3c: Token economics review (conditional Agent dispatch)**

When the session had significant token cost (>200K tokens) or the BEI score is notable:

```
Agent({
  subagent_type: "bookkeeper",
  description: "Review session cost efficiency",
  prompt: "Review token economics for session <session-id>.
           Token report: docs/reports/token-audit/session-<date>.md
           BEI score: <score>
           Cost: $<cost>
           Compare against project baselines (P50/P75).
           Produce a one-paragraph efficiency verdict for the archive."
})
```

**Error capture**: If bladesmith-quench-forge fails, record the candidate in the archive with a note: "Forge dispatch failed: <reason>. Candidate preserved for next session." If bookkeeper fails, embed the raw token report without commentary.

---

### Step 4: Token Benefit Report

**What**: Include the token benefit summary as a section in the archive README.

**Dispatch**: Direct `Read` (from Step 1 output) + `Edit` (embed in archive).

Embed the key table from Step 1's report into the archive README:

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

**Error capture**: If the trend report fails, skip it — it is informational, not blocking.

---

### Step 4.5: Output Existence Check

**What**: Before committing, verify every required output from Steps 0-4 actually
exists on disk. This is a mechanical gate — do not skip.

**Dispatch**: Direct `Bash` existence checks.

**Checklist** (each item must return `true`):

| # | Required file | Step | Blocking? |
|---|--------------|------|:---------:|
| 1 | `.claude/current-task` | 0 | yes |
| 2 | `docs/agentic/tasks/<date-slug>.md` | 0 | yes |
| 3 | `docs/reports/token-audit/session-<date>.md` | 1 | yes |
| 4 | `docs/reports/session-output-summary-<date>.md` | 1.5 | yes |
| 5 | `docs/completed-tasks/<date-slug>/README.md` | 2 | yes |
| 6 | `docs/agentic/experience/<slug>/README.md` | 3 | if candidate identified |

**Content checks** (Read the archive README and verify):

| # | Content requirement | Blocking? |
|---|--------------------|:---------:|
| C1 | Archive README has `## Narrative Line Impact` section | yes |
| C2 | Archive README has `## Evidence` section with at least one command/result | yes |
| C3 | Experience/Skill/Agent evaluation table is present (Step 3 stage 3a) | yes |
| C4 | All three rows answered (experience, skill, agent — even if "no") | yes |
| C5 | If experience "yes" or "candidate", `docs/agentic/experience/<slug>/` exists | yes |

```bash
# Existence check (run for each file)
ls -la <file-path>

# Content check (grep for required sections)
grep -c "## Narrative Line Impact" docs/completed-tasks/<date-slug>/README.md
grep -c "## Evidence" docs/completed-tasks/<date-slug>/README.md
grep -c "| Experience |" docs/completed-tasks/<date-slug>/README.md
```

**Decision**:

- ALL blocking checks pass → proceed to Step 5
- Any blocking check fails → **STOP**. Report which check failed and what is
  missing. Do NOT proceed to commit. Fix the missing output, then re-check.

**Error capture**: Record the check results (pass/fail for each item) in the
pipeline output. If blocked, write the block reason to the archive README
under `## Pipeline Block Log`.

### Step 5: Commit & Push

**What**: Stage only scoped files, commit with a concise message, push.

**Dispatch**: Direct `Bash` operations with pre-commit safety check.

**Step 5a: Pre-commit safety check**

Before staging, invoke git-session-branch-steward for branch safety:

```
Agent({
  subagent_type: "git-session-branch-steward",
  description: "Pre-commit branch safety check",
  prompt: "Verify branch safety before committing session close artifacts.
           Check: branch is master, no unrelated dirty files, push payload is scoped.
           Changed files: <list from git status>
           If safe: respond 'CLEAR'. If issues: respond 'BLOCKED: <reason>'."
})
```

If the steward responds BLOCKED, stop and report the reason. Do NOT proceed to commit.

**Step 5b: Stage and commit**

```bash
git status
git diff --stat
```

Stage only the files created/modified in this pipeline:
- `docs/agentic/tasks/<today>-<slug>.md`
- `docs/reports/session-output-summary-<date>.md`
- `docs/completed-tasks/<date-slug>/README.md`
- `docs/reports/token-audit/session-<date>.md`
- `docs/agentic/experience/<slug>/` (if created)
- `.claude/current-task`

```bash
git add <scoped file list>
git commit -m "<action>: <what changed>"
```

Commit message format: `<action>: <what changed>` (imperative, lowercase).

**Step 5c: Push**

```bash
git push
```

**Error capture**: If pre-commit check blocks, record block reason in archive. If commit fails, check for merge conflicts. If push fails, report: "Push failed — commits saved locally. Retry with `git push`."

---

## Required Output

At close, the following must exist on disk and be pushed:

1. `.claude/current-task` — pointing to the current task card (Step 0)
2. `docs/agentic/tasks/<date-slug>.md` — task card with `status: complete`
   and filled evidence (Step 0)
3. `docs/reports/session-output-summary-<date>.md` — top-level session overview
   with deliverables, verification gates, narrative impact, and token summary
   (Step 1.5)
4. `docs/completed-tasks/<date-slug>/README.md` — task archive with embedded
   token benefit summary (Step 2, dispatched to task-scoped-session-closer)
5. `docs/reports/token-audit/session-<date>.md` — full token benefit report
   (Step 1)
6. If experience extracted: `docs/agentic/experience/<slug>/README.md` (Step 3,
   dispatched to bladesmith-quench-forge)
7. Commit on `master` containing all of the above (Step 5, with git-session-branch-steward pre-check)

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
- Do not proceed to commit if git-session-branch-steward returns BLOCKED.
- Do not skip Step 4.5 (output existence check) — if any blocking file is
  missing, stop and fix before commit.
- Retry a failed skill dispatch once with reduced scope. If retry also fails, record failure and continue.

## Claude Code Integration

### Direct operations (this skill performs itself)
- `Read` — check `.claude/current-task`, existing task cards, session transcripts
- `Write` — create/update task card, session output summary, `.claude/current-task`
- `Edit` — embed token benefit report into archive README
- `Bash` — run `python -m tools.token_audit`, `git status/diff/add/commit/push`

### Explicit skill dispatch (this skill invokes other skills)
- `Skill({skill: "task-scoped-session-closer", ...})` — Step 2 (task archive)
- `Agent({subagent_type: "bladesmith-quench-forge", ...})` — Step 3b (experience forging)
- `Agent({subagent_type: "bookkeeper", ...})` — Step 3c (token economics review)
- `Agent({subagent_type: "git-session-branch-steward", ...})` — Step 5a (pre-commit safety)

### Tracking
- `TaskCreate` / `TaskUpdate` — track pipeline steps and dispatched sub-tasks
- `mcp__ccd_session__mark_chapter` — mark pipeline phase transitions (CCD only)

### Memory
- Check Claude memory at `C:\Users\QR\.claude\projects\C--Codes-AI-GCS-A\memory\` for relevant patterns before experience/skill/agent evaluation
