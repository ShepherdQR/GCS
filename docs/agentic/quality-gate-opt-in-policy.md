# Agentic Artifact Opt-In Gate Policy

Status: S2-05 default-enforcement decision complete.

## Purpose

Agentic SE artifacts should be checkable by the same quality-gate entry point
as code, but they should not become default ceremony for every small edit. This
policy defines opt-in gates for task cards and completed-task reports and
records the S2-05 decision to avoid broad default enforcement for now.

## Implemented Flags

These flags are implemented in `python tools\agentic_design\agentic_toolkit.py
run-quality-gates`:

| Flag | Gate ID | Validator command | Scope |
| --- | --- | --- | --- |
| `--include-task-cards <pathspec>` | `agentic.task-cards` | `validate-task-card-includes` | Explicit task-card files, directories, or globs. |
| `--include-completed-reports <pathspec>` | `agentic.completed-task-reports` | `validate-completed-report-includes` | Explicit completed-task `README.md` files, directories, or globs. |

Pathspec rules:

- pathspecs are repository-relative;
- the flags may be repeated;
- a pathspec may be a file, directory, or glob;
- task-card directories expand to `*.md`;
- completed-task directories expand to `*/README.md` or `README.md`;
- an unmatched explicit pathspec fails the gate instead of silently passing;
- generated scratch stores remain out of scope unless explicitly promoted into
  tracked docs.

## Default Behavior

The default `run-quality-gates` command must not validate all historical task
cards or completed-task archives.

Rationale:

- legacy records predate the current frontmatter and closure-score rules;
- S1-04 allows tiny low-risk work to stay chat-only or commit-note-only;
- forcing all archives into the default gate would create noisy migration work
  that S2-04 explicitly rejects;
- high-risk tasks can still opt in by naming their own active artifacts.

## Intended Usage

For a non-trivial Agentic SE task:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --include-task-cards docs\agentic\tasks\2026-05-25-s2-01-opt-in-gate-policy.md --include-completed-reports docs\completed-tasks\2026-05-25-s2-01-opt-in-gate-policy
```

For a high-risk implementation task with normal build and CTest gates:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates --include-task-cards docs\agentic\tasks\<task>.md --include-completed-reports docs\completed-tasks\<task>
```

Direct validators remain valid for focused checks:

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\<task>\README.md
python tools\agentic_design\agentic_toolkit.py validate-task-card-includes docs\agentic\tasks\<task>.md
python tools\agentic_design\agentic_toolkit.py validate-completed-report-includes docs\completed-tasks\<task>
```

## Gate Semantics

Task-card gate:

- runs `validate-task-card` on all expanded task-card paths;
- fails on missing required frontmatter;
- fails when high-risk task cards omit a human gate;
- fails on planned evidence left as final evidence if future validator support
  adds that check;
- does not require a completed-task archive by itself.

Completed-report gate:

- runs `validate-completed-task-report` on expanded completed-task reports;
- does not score by default;
- closure scoring remains advisory and opt-in after S2-05;
- validates only explicitly included reports under the S2-04 legacy migration
  or exemption policy.

Current implementation note:

- `--skip-agentic` skips the default Agentic docs/inventory/skill/dependency
  checks, but explicitly included task cards and completed reports still run.
  The include flags are user-selected gates, not a default Agentic sweep.

## Legacy Policy

Legacy task cards and completed-task archives follow
`docs/agentic/legacy-artifact-policy.md`.

Allowed non-default states:

- `legacy-exempt`: useful historical records that predate the current
  validator shape;
- `migratable-legacy`: old records that must be migrated before a new task uses
  them as active evidence;
- `low-risk-no-archive`: chat-only or commit-note-only tasks allowed by the
  lifecycle runbook;
- `parallel-session-pending`: artifacts owned by another active branch,
  worktree, or conversation.

Not allowed:

- using "legacy" to exempt a newly created task from validation;
- treating a failed active task-card or archive validation as a pass;
- validating the whole archive tree in a final gate without a migration plan.

## Implementation Order

1. S2-02: implement and test `--include-task-cards`. Done in
   `2026-05-25-agentic-se-roadmap-items-1-2-3-5`.
2. S2-03: implement and test `--include-completed-reports` for new reports
   only. Done in `2026-05-25-agentic-se-roadmap-items-1-2-3-5`.
3. S2-04: define legacy archive migration or exemption policy. Done in
   `docs/agentic/legacy-artifact-policy.md`.
4. S2-05: consider default enforcement only after two clean opt-in task
   cycles. Done in `docs/agentic/default-agentic-gate-decision.md`; default
   behavior remains broad-scan-free.

## Quality Report

Contract under test:

- Agentic artifact quality-gate opt-in behavior.

Fixtures needed:

- valid task card;
- task card missing required frontmatter;
- high-risk task card missing human gate;
- valid completed-task report;
- completed-task report missing required sections;
- unmatched include pathspec.

Assertions:

- included artifacts create named gate commands;
- unmatched pathspecs fail;
- skipped build/CTest/CLI flags remain composable with Agentic artifact gates;
- legacy archive trees are not selected by default.

Missing-test risk:

- A future current-task default gate still needs an explicit current artifact
  declaration mechanism.
- Completed-report validation and closure scoring remain opt-in closeout
  checks rather than default pre-build gates.

Handoffs:

- `gcs-quality-steward`: keep future current-task default validation scoped to
  explicitly declared active artifacts.
- `gcs-architecture-steward`: keep lifecycle and roadmap policy aligned as
  implementation tasks land.
- E001 closure experience: keep closure scoring advisory unless a future PDCA
  cycle proves it belongs in a stronger gate.
