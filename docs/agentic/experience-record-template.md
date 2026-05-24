# Experience Record Template

Use this when a failure, review finding, or repeated agent mistake might teach
the project something durable.

```yaml
---
experience_id: 2026-05-24-source-short-slug
source: human-review
status: draft
root_cause: weak_skill
affected_modules:
  - quality
promotion_target: skill
---
```

## Symptom

What happened?

## Evidence

- Task card:
- Commit or branch:
- Failed command or review finding:

## Root Cause

Classify as one of:

- `ambiguous_task`
- `weak_skill`
- `missing_fixture`
- `missing_eval`
- `contract_gap`
- `flaky_tool`
- `permission_gap`
- `dependency_gap`

## Lesson

State the reusable lesson in one or two sentences.

## Proposed Promotion

- T0 experience note
- T1 checklist or template update
- T2 skill update
- T3 fixture or contract test
- T4 architecture rule
- T5 tool or CI gate

## Validation

- Before:
- After:
- New gate or eval:
