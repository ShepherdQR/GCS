# Agentic Trace Schema

Agentic traces make important work replayable without storing private chat
history as the source of truth.

## Minimal Trace

```yaml
trace_id: 2026-05-24-example-task-run-1
task_id: 2026-05-24-example-task
agent: gcs-architecture-steward
started_at: 2026-05-24T00:00:00Z
finished_at: 2026-05-24T00:10:00Z
status: accepted
inputs:
  - docs/architecture/README.md
  - .codex/skills/gcs-architecture-steward/SKILL.md
tool_calls:
  - command: python tools/agentic_design/agentic_toolkit.py validate-docs
    exit_code: 0
outputs:
  changed_files:
    - docs/agentic/README.md
  evidence:
    - validate-docs passed
residual_risks:
  - none recorded
```

## Status Values

- `accepted`: all required evidence passed.
- `accepted_with_risk`: work is usable but has named residual risk.
- `rejected`: guardrail, test, or review failure blocked the work.
- `abandoned`: task was intentionally stopped.

## Trace Rules

- Keep traces concise and path-based.
- Do not paste long logs.
- Preserve enough command and file evidence for review.
- Promote repeated failures into experience records.
