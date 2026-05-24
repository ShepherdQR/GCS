# Task Card Template

Copy this template to `docs/agentic/tasks/<date>-<slug>.md` for non-trivial
work. Keep the frontmatter machine-checkable; keep the body concise and useful
for humans.

```yaml
---
task_id: 2026-05-24-example-task
status: draft
request: "Describe the human intent in one sentence."
scope: implementation
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - gcs-quality-steward
affected_contracts:
  - ContractNameOrNone
affected_paths:
  - docs/agentic/
required_evidence:
  - validate-docs
  - validate-inventory
  - check-dependencies
human_gate_required: false
human_gate_reason: ""
---
```

## Scope

Describe what is in scope and what is intentionally out of scope.

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.

## Context To Read

- `docs/architecture/README.md`
- Owning module skill or runbook.

## Acceptance Gates

- The owning boundary is clear.
- Required evidence is produced or a reason is recorded.
- Residual risks are named.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md
```

## Evidence Bundle

Record commands run, important outputs, changed files, and skipped checks.

## Residual Risks

List remaining uncertainty, review focus, or follow-up work.
