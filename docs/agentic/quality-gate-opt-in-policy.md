# Agentic Artifact Opt-In Gate Policy

Status: S2-02 and S2-03 implemented.

## Purpose

Agentic SE artifacts should be checkable by the same quality-gate entry point
as code, but they should not become default ceremony for every small edit. This
policy designs opt-in gates for task cards and completed-task reports before
any default enforcement.

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
cards or completed-task archives yet.

Rationale:

- legacy records predate the current frontmatter and closure-score rules;
- S1-04 allows tiny low-risk work to stay chat-only or commit-note-only;
- forcing all archives into the default gate would create noisy migration work
  before S2-04 defines exemptions;
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
- may add optional scoring in S2-05 after scorer thresholds are calibrated;
- validates only explicitly included reports until S2-04 defines legacy
  migration or exemption policy.

Current implementation note:

- `--skip-agentic` skips the default Agentic docs/inventory/skill/dependency
  checks, but explicitly included task cards and completed reports still run.
  The include flags are user-selected gates, not a default Agentic sweep.

## Legacy Policy

Legacy task cards and completed-task archives stay exempt from default
`run-quality-gates` until S2-04.

Allowed legacy states:

- records with older frontmatter conventions;
- records that are useful as narrative archives but not validator-clean;
- low-risk commit-note-only tasks that intentionally have no archive.

Not allowed:

- using "legacy" to exempt a newly created task from validation;
- treating a failed active task-card or archive validation as a pass;
- validating the whole archive tree in a final gate without a migration plan.

## Implementation Order

1. S2-02: implement and test `--include-task-cards`. Done in
   `2026-05-25-agentic-se-roadmap-items-1-2-3-5`.
2. S2-03: implement and test `--include-completed-reports` for new reports
   only. Done in `2026-05-25-agentic-se-roadmap-items-1-2-3-5`.
3. S2-04: define legacy archive migration or exemption policy.
4. S2-05: consider default enforcement only after two clean opt-in task
   cycles.

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

- S2-01 is design-only, so command-line behavior is not implemented yet.
- S2-02 and S2-03 must add unit tests before any workflow relies on these
  flags.

Handoffs:

- `gcs-quality-steward`: implement gate-command construction and tests.
- `gcs-architecture-steward`: keep lifecycle and roadmap policy aligned.
- E001 closure experience: decide later whether closure scoring becomes an
  optional gate.
