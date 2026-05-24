# Execution Plan Template

Use this for high-risk, multi-module, or multi-commit work. A plan may be
checked in before implementation or included inside a task card when the scope
is small.

## Task

- Task card:
- Request:
- Risk:
- Human gate:

## Base Context

- Architecture docs read:
- Skills read:
- Source files read:
- Fixtures or tests read:

## Ownership

- Owning module or support boundary:
- Specialist agents:
- Refused boundaries:
- Dependency-direction impact:

## Step Plan

1. Prepare or update task card.
2. Make the smallest contract or documentation change.
3. Add or update deterministic tests, fixtures, or validators.
4. Run focused verification.
5. Run required quality gates.
6. Record evidence and residual risk.
7. Commit and push only scoped changes.

## Parallel Work

Use parallel agents only for independent sidecar tasks such as read-only
review, separate module analysis, or disjoint file edits. Do not delegate a
blocking step that the next local action depends on.

## Verification

```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

## Rollback

Describe how to revert or abandon the step without losing unrelated user work.
