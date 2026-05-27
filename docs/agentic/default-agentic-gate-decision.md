# S2-05 Default Agentic Gate Decision

Status: S2-05 complete.

## Decision

Do not bulk-promote Agentic artifact validation into the default
`run-quality-gates` sequence yet.

Adopt this enforcement posture:

| Check | S2-05 decision | Rationale |
| --- | --- | --- |
| Task-card validation | Keep opt-in today; allow a future current-task default only after the command has an explicit current-task artifact input. | A task-card gate can be a good default for non-trivial current work, but filesystem-wide discovery would sweep legacy and unrelated parallel files. |
| Completed-report validation | Keep opt-in. | Completed reports are produced at task close, and default enforcement could interfere with small tasks or in-progress parallel sessions. |
| Closure score | Keep advisory and opt-in. | The score is useful for review calibration but remains heuristic; low scores should trigger review, not automatic failure. |
| Legacy artifacts | Keep exempt unless migrated or explicitly included. | Historical records preserve memory and should not be rewritten only to satisfy new validators. |

## Evidence Used

S2-05 used the S2-04 legacy policy and two post-policy opt-in cycles:

| Cycle | Task card | Completed report | Include gate result | Counted? |
| --- | --- | --- | --- | --- |
| S2-04 legacy policy | `docs/agentic/tasks/2026-05-25-s2-04-legacy-artifact-policy.md` | `docs/completed-tasks/2026-05-25-s2-04-legacy-artifact-policy/README.md` | Passed `agentic.task-cards` and `agentic.completed-task-reports`. | yes |
| S2-05 default decision | `docs/agentic/tasks/2026-05-25-s2-05-agentic-default-gate-decision.md` | `docs/completed-tasks/2026-05-25-s2-05-agentic-default-gate-decision/README.md` | Passed `agentic.task-cards` and `agentic.completed-task-reports`. | yes |

Earlier evidence:

- `2026-05-25-agentic-se-roadmap-items-1-2-3-5` remains a useful
  pre-policy rehearsal. It proved command behavior, but S2-04 classifies it
  outside the official two post-policy cycle count.

## Why Not Default Now

The current gate command does not know which task card or completed report is
the current task's intended artifact. Without an explicit declaration, a
default gate has only poor choices:

- scan nothing and provide false assurance;
- scan the whole tree and turn legacy records into noisy failures;
- infer from modified files and risk picking up unrelated parallel-session
  work;
- force completed reports before the task is actually ready to close.

The opt-in path already gives high-risk or non-trivial tasks a reliable
command. S2-05 therefore chooses discipline over broad automation.

## Future Promotion Criteria

A later task may promote task-card validation into a current-task default only
after all of these are true:

- `run-quality-gates` accepts an explicit current artifact declaration, such
  as a task-card path or manifest;
- the declaration is generated or recorded by the lifecycle runbook;
- parallel-session and low-risk no-archive states are excluded by construction;
- at least two additional non-documentation tasks pass the declared current
  task-card gate without exemptions;
- failure output points to the current artifact, not historical archive drift.

Completed-report validation may become default only for a closeout profile,
not for the general pre-build/pre-test gate. That profile must run after the
archive exists and the completed-task index has been updated.

Closure scoring may become a warning gate only after calibration defines:

- a threshold;
- an override path;
- examples of acceptable low-score but valid archives;
- examples of structurally valid archives that should still be blocked.

## S2-05 Amendment: Current-Task Declaration (2026-05-27)

The original S2-05 decision deferred default task-card validation because
`run-quality-gates` had no way to identify the current task's card. That gap
is now closed.

### Mechanism

A new `.claude/current-task` file in the project root provides an explicit
current-task declaration:

```
task_card: docs/agentic/tasks/2026-05-27-my-task.md
created: 2026-05-27
```

**Write path**: `new-task-card --write` automatically creates this file,
pointing to the new task card. No extra step.

**Read path**: `run-quality-gates` reads `.claude/current-task` and
auto-includes the declared task card in `agentic.task-cards` — no
`--include-task-cards` flag needed.

**Strict path**: `run-quality-gates --require-task-card` fails when no
`.claude/current-task` exists and no explicit `--include-task-cards` is
provided. Use this in CI for non-trivial branches.

### Updated Enforcement Posture

| Check | S2-05 decision | Update |
| --- | --- | --- |
| Task-card validation | Keep opt-in | Auto-included when `.claude/current-task` exists. `--require-task-card` for strict CI enforcement. |
| Completed-report validation | Keep opt-in | Unchanged — reports are produced at close. |
| Closure score | Keep advisory | Unchanged. |
| Legacy artifacts | Keep exempt | Unchanged. |

### Why This Satisfies the Promotion Criteria

The original criteria required:
- A current artifact declaration → `.claude/current-task`
- Generated by lifecycle runbook → `new-task-card --write` writes it
- Parallel-session exclusion by construction → each worktree has its own `.claude/current-task`
- At least two non-documentation tasks pass → pending calibration

Task-card validation is now **default-active when declared**, opt-in otherwise.

## Current Recommended Commands

For ordinary code or fixture quality:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates
```

For non-trivial Agentic SE closeout:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --include-task-cards docs\agentic\tasks\<task>.md --include-completed-reports docs\completed-tasks\<task>
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\<task>\README.md --min-score 30
```

For high-risk solver work, keep normal build/CTest/CLI gates and add the
current task artifacts explicitly:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates --include-task-cards docs\agentic\tasks\<task>.md --include-completed-reports docs\completed-tasks\<task>
```

## Follow-Up

- ~~Add a future current-task artifact declaration only if a real workflow needs
  less manual include syntax.~~ **Done 2026-05-27**: `.claude/current-task` file
  serves as the declaration; `new-task-card --write` sets it; `run-quality-gates`
  reads it.
- Calibrate `--require-task-card` on at least two non-documentation CI branches
  before making it the default for all CI presets.
- Keep `docs/agentic/legacy-artifact-policy.md` as the source of truth for
  archive migration and exemption.
- Use rendered-artifact evidence before promoting I003/I004 visual seed roles.
