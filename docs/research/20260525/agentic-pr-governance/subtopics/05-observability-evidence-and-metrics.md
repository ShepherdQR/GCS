# Observability, Evidence, And Metrics

Date: 2026-05-25

## Question

What should a project observe when agents perform software-governance work?

## Pattern

Observability has two levels:

- operational telemetry: who ran what, when, where, with which cost and status;
- engineering evidence: what changed, which commands ran, which findings
  remain, and why the result is safe or unsafe.

## Vendor Patterns

OpenAI Codex enterprise governance exposes analytics and compliance logs for
adoption, usage, code review impact, priority-level findings, comments, and
activity logs. GitHub enterprise agent monitoring exposes recent agentic
sessions and audit logs. Jules exposes activity feed, errors, final summary,
runtime, files changed, and branch/commit metadata.

GCS cannot assume those SaaS dashboards are always available, so it should
write local evidence artifacts with a similar shape.

## GCS Local Evidence Model

### Run Record

Each automation run should record:

- run ID;
- date/time and timezone;
- branch/worktree;
- commit SHA before run;
- model/reasoning if available;
- prompt version or policy file version;
- status;
- changed files;
- commands and interpreted outcomes;
- skipped checks;
- findings and severity;
- next actions.

### Finding Record

Each finding should record:

- finding ID;
- category;
- severity;
- affected paths;
- affected contracts;
- reproduction command or evidence source;
- confidence;
- recommended action;
- whether repair is safe for automation;
- link to task card or PR when promoted.

### Metrics

Track trends, not vanity counts:

| Metric | Why it matters |
| --- | --- |
| nightly run completion rate | detects broken automation |
| findings by category and severity | shows where governance debt accumulates |
| repeated findings | identifies issues that should become tests/tools |
| repair proposal acceptance rate | measures usefulness |
| skipped-check frequency | detects environmental drift |
| PR audit P0/P1 rate | shows whether PRs arrive review-ready |
| false-positive review feedback | tunes audit strictness |
| time from finding to task/PR closure | measures governance throughput |

## Evidence Anti-Patterns

- logs without interpretation;
- "all good" without command evidence;
- planned evidence left in final task cards;
- failure hidden as "best effort";
- AI review comments not tied to files/contracts;
- PR summaries that omit skipped checks.

## GCS Decision

Use local Markdown plus JSON artifacts first. This keeps the workflow portable,
reviewable, and compatible with the existing task-card/archive system. Add
dashboarding only after the schema stabilizes through several runs.
