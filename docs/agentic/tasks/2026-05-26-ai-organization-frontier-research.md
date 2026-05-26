---
task_id: 2026-05-26-ai-organization-frontier-research
status: complete
request: "Research McKinsey AI reports, OpenAI and Claude agentic-SE practices, frontier developer AI workflows, AI organization paradigms, and audit GCS narrative-line completeness; persist Markdown reports."
scope: docs
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - task-scoped-session-closer
affected_contracts:
  - none
affected_paths:
  - docs/research/20260526/ai-organization-frontier/
  - docs/agentic/tasks/2026-05-26-ai-organization-frontier-research.md
  - docs/completed-tasks/2026-05-26-ai-organization-frontier-research/
  - docs/completed-tasks/README.md
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - validate-docs
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-26-ai-organization-frontier-research

## Scope

In scope:

- Research McKinsey's recent AI, gen AI, agentic AI, software PDLC, workforce,
  and organization-design reports.
- Research OpenAI and Claude/Anthropic frontier practices in agentic software
  engineering, agent design, SDLC change, and governance.
- Research highly visible developer AI practices, including the OpenClaw/Peter
  Steinberger pattern, Simon Willison's security framing, Addy Osmani's 70
  percent problem, Thorsten Ball's cheap-code thesis, Hamel Husain's eval
  practice, and Karpathy-style Software 3.0 framing.
- Synthesize the core AI organization paradigm and project-promotion narrative
  lines.
- Audit current GCS narrative-line completeness and propose development plans.

Out of scope:

- Exhaustively crawl every McKinsey localized page, podcast derivative,
  newsletter, or industry short note.
- Change solver/runtime/IO/viewer behavior.
- Commit or push changes.

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.
- Do not introduce new quality-gate requirements from this research alone.

## Context To Read

- `docs/architecture/README.md`
- `docs/architecture/10-system/current-to-target-map.md`
- `docs/agentic/README.md`
- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/task-to-archive-checklist.md`
- `docs/research/20260524/agentic-se-dimensions-metrics-research-report.md`
- `docs/research/20260524/agentic-se-gcs-progress-and-development-plan.md`
- Owning skill: `gcs-architecture-steward`
- Supporting skill: `source-aware-research-report`
- Closure skill: `task-scoped-session-closer`

## Acceptance Gates

- The owning boundary is clear.
- Reports are persisted under a dated research folder.
- External source registers contain source URLs and dates where available.
- The GCS narrative audit is grounded in current repo docs rather than external
  strategy prose alone.
- Required evidence is produced or a reason is recorded.
- Residual risks and follow-up narrative lines are named.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-ai-organization-frontier-research.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-ai-organization-frontier-research\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

Commands and outcomes:

- `python tools\agentic_design\agentic_toolkit.py new-task-card ... --write`:
  initially failed under normal permissions, then succeeded with scoped
  escalation.
- Web research: completed against McKinsey, OpenAI, Anthropic/Claude, and
  developer-practice sources. Source URLs were embedded in the reports.
- Local context review: read relevant GCS architecture, agentic lifecycle, and
  prior agentic-SE research artifacts.
- Final validation results are recorded in the completed-task archive.
- `python tools\agentic_design\agentic_toolkit.py validate-task-card
  docs\agentic\tasks\2026-05-26-ai-organization-frontier-research.md`:
  passed.
- `python tools\agentic_design\agentic_toolkit.py
  validate-completed-task-report
  docs\completed-tasks\2026-05-26-ai-organization-frontier-research\README.md`:
  passed.
- `python tools\agentic_design\agentic_toolkit.py validate-docs`: passed with
  module design coverage OK.
- `python tools\agentic_design\agentic_toolkit.py score-closure-report
  docs\completed-tasks\2026-05-26-ai-organization-frontier-research\README.md
  --min-score 30`: scored 38/40.

Changed files:

- `docs/research/20260526/ai-organization-frontier/README.md`
- `docs/research/20260526/ai-organization-frontier/01-mckinsey-ai-report-review.md`
- `docs/research/20260526/ai-organization-frontier/02-openai-claude-agentic-se-frontier.md`
- `docs/research/20260526/ai-organization-frontier/03-developer-ai-practice-paradigms.md`
- `docs/research/20260526/ai-organization-frontier/04-ai-organization-core-paradigm.md`
- `docs/research/20260526/ai-organization-frontier/05-gcs-narrative-line-audit-and-development-plan.md`
- `docs/completed-tasks/2026-05-26-ai-organization-frontier-research/README.md`
- `docs/completed-tasks/README.md`

## Residual Risks

- McKinsey coverage is a flagship-source review, not an exhaustive inventory of
  every McKinsey AI item published in the period.
- Some developer-practice sources are fast-moving public coverage rather than
  formal primary engineering docs; the reports label those as medium
  confidence.
- Recommended next documents, such as a narrative map, product/user brief, and
  metrics dashboard, were not created in this task.
