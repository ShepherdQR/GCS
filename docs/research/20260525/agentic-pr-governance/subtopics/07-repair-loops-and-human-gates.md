# Repair Loops And Human Gates

Date: 2026-05-25

## Question

When should an agent repair defects automatically, and when should it stop at
recommendations?

## Pattern

The safe repair loop is:

```text
detect -> reproduce/validate -> classify -> propose minimal repair
  -> apply in isolated workspace only when allowed
  -> revalidate -> summarize -> human review
```

OpenAI Codex Security reproduces and validates before surfacing, proposes a
minimal patch, and leaves code changes to human review and PR flow. Codex
repair-loop examples use structured review, repair, validation, and remaining
delta. This is the right template for GCS.

## Human Gate Levels

| Gate | Required when | Action |
| --- | --- | --- |
| `none` | Docs typo, local report formatting, clearly scoped low-risk artifact | Automation may patch in worktree |
| `review_before_commit` | Medium-risk docs/process/tooling | Automation may create diff but not commit/push |
| `task_card_before_edit` | Solver, runtime, IO, fixture promotion, quality-gate default behavior | Create task card candidate first |
| `human_approval_before_command` | Network install, dependency change, destructive operation, push, branch delete | Stop and ask |
| `forbidden` | Merge, self-approve, force-push, publish secrets, rewrite history | Never perform |

## Minimal Repair Rules

An automated repair proposal should:

- address one finding or one coherent finding cluster;
- include before/after evidence;
- avoid opportunistic refactors;
- preserve module ownership;
- add or update tests only when the affected contract justifies it;
- state why a broader fix is deferred.

## Revalidation

Every repair candidate needs a matching validation:

| Finding type | Revalidation |
| --- | --- |
| Docs link/index | `validate-docs` or explicit path check |
| Task/archive closure | `validate-task-card`, `validate-completed-task-report`, score if applicable |
| Quality gate | focused unit test plus selected gate |
| Scene explorer | scene generation tool validation and no fixture promotion |
| Solver contract | focused CTest plus build when feasible |
| Security/permission | no automated patch unless explicitly authorized |

## Stop Conditions

Stop and summarize when:

- the same command fails twice for the same reason;
- evidence points to high-risk semantic change;
- validation requires network/dependency installation;
- the diff grows beyond the original finding;
- a repair would require fixture promotion;
- a human-gate category is reached.

## GCS Decision

Nightly diagnostics may propose repairs and may create local patches only for
low-risk categories. It must not turn a high-risk finding into code changes
without a task card and human approval.
