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

### Step 1: Token Audit — Import & Report

**What**: Import the current session's JSONL transcript into the audit database,
then generate the token benefit report.

```bash
# Import current session data
python -m tools.token_audit db import --project GCS-A

# Generate benefit report
python -m tools.token_audit report --format markdown
```

**Output**: Token usage, cost, cache efficiency, BEI scores.

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

| Metric | Value |
|--------|-------|
| Session Duration | <duration> |
| Model | <model_id> |
| Total Tokens | <total> (in: <input> / out: <output>) |
| Cache Hit Rate | <rate> |
| Estimated Cost | $<cost> |
| Lines Changed | +<added>/-<removed> |
| Commits | <count> |
| BEI Composite | <score> (<rating>) |
| Cost per Commit | $<cpc> |

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

1. `docs/completed-tasks/<date-slug>/README.md` — task archive with embedded
   token benefit summary
2. `docs/reports/token-audit/session-<date>.md` — full token benefit report
   (if not already generated in Step 1)
3. If experience extracted: `docs/agentic/experience/<slug>/README.md`
4. Commit on `master` containing all of the above

## Guardrails

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
