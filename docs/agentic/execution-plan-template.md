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

## PBCA Step Loop

Use this loop for each step in a multi-step plan:

| PBCA stage | Required action | Required artifact |
| --- | --- | --- |
| Plan | Confirm the current step, governing docs, scope, risks, and commit boundary. | One-sentence step intent and files likely to change. |
| Build | Make the smallest coherent change for this step only. | Diff scoped to the current step. |
| Check | Run focused checks and inspect whether future steps need adjustment. | Command outputs, skipped-check reasons, and residual risks. |
| Act | Summarize the completed step, update later steps if needed, commit, then start the next step. | Step summary, plan update, commit hash. |

Step completion note:

```text
PBCA step:
- Plan:
- Build:
- Check:
- Act:
- Changed files:
- Evidence:
- Follow-up adjustment:
- Commit:
```

Do not start the next step until the Act stage has updated the plan and created
the scoped commit, unless the user explicitly pauses commits.

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
