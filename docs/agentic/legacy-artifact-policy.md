# Legacy Agentic Artifact Policy

Status: S2-04 complete.

## Purpose

S2-02 and S2-03 made task-card and completed-task report validation executable
through explicit include gates. S2-04 defines how older Agentic artifacts are
handled so that default quality gates do not become a noisy historical cleanup
project.

The policy separates two questions:

- Is a current task artifact good enough to block or warn on?
- Is an older artifact still useful as project memory, even if it predates the
  current validator shape?

## Artifact States

Use these states when referring to task cards, completed-task reports, and
low-risk lifecycle records.

| State | Meaning | Gate policy | Migration rule |
| --- | --- | --- | --- |
| `validator-clean` | Current artifact created or materially edited after S2-02/S2-03 and accepted by the current validator. | May be included in `--include-task-cards` or `--include-completed-reports`. | No migration needed. |
| `migrated` | Older artifact intentionally updated to current structure because a new task depends on it. | May be included after the migration commit. | Record why migration was needed. |
| `legacy-exempt` | Older narrative artifact that remains useful but predates current frontmatter, section, or archive-index rules. | Not selected by default and not used as a current-cycle pass. | Do not migrate only to make the whole tree green. |
| `migratable-legacy` | Older artifact that is close to current structure and will be cited as evidence for a new gate, promotion, roadmap decision, or E001 calibration. | Must be migrated before it is used as new gate evidence. | Migrate in the task that depends on it. |
| `low-risk-no-archive` | Work that the lifecycle runbook Step 1.5 allows to remain chat-only or commit-note-only. | No missing-archive failure. | Do not backfill unless future work depends on it. |
| `parallel-session-pending` | Artifact owned by another active branch, worktree, or conversation. | Excluded from the current task's gate evidence. | Review only after the owning session lands or hands off. |

## Current Artifact Rule

An artifact is current when any of these are true:

- it is created after S2-02/S2-03;
- it is materially edited after S2-04;
- it is used to justify a new roadmap `done` state, default-gate decision,
  E001 promotion, institutional-agent promotion, or quality-gate change;
- it is included by explicit `--include-task-cards` or
  `--include-completed-reports` pathspecs.

Current artifacts must validate. A current artifact cannot claim
`legacy-exempt` to avoid a failed gate.

## Migration Triggers

Migrate a legacy artifact only when a new task needs it as active evidence:

- the artifact is cited as one of the two S2-05 opt-in cycles;
- the artifact is used as E001 scorer or promotion evidence;
- the artifact is used to promote an institutional agent beyond seed status;
- the artifact is used to justify default quality-gate behavior;
- a new completed-task archive links to it as a dependency, not merely as
  background reading.

When migrating, keep the migration scoped:

- preserve the original task meaning;
- add missing frontmatter or required sections only as needed;
- record the migration reason in the new task archive;
- avoid rewriting historical decisions to sound cleaner than they were.

## Non-Migration Boundaries

Do not migrate artifacts for these reasons alone:

- the historical tree does not pass current validators;
- a low-risk chat-only task has no archive;
- a narrative archive is useful for memory but not part of current evidence;
- a parallel session has unlanded files;
- a default gate would be easier to implement by sweeping all files.

Bulk migration requires a separate migration task card, impact review, and
exemption table. It is out of scope for ordinary feature work.

## Opt-In Cycle Counting

An opt-in artifact-gate cycle counts toward S2-05 only when all conditions hold:

- the cycle happens after S2-04 policy is recorded;
- the task is non-trivial under `docs/agentic/lifecycle-runbook.md`;
- a task card and completed-task archive both exist;
- final verification explicitly runs `--include-task-cards` and
  `--include-completed-reports` on the current artifacts;
- both include gates pass without relying on `legacy-exempt`;
- the archive records commands, results, skipped checks, commit/push status,
  and residual risk.

The earlier `2026-05-25-agentic-se-roadmap-items-1-2-3-5` cycle remains valid
evidence that the gates work, but it is classified as `pre-policy-rehearsal`
rather than one of the official post-S2-04 cycles.

## S2-05 Input

For S2-05, use two post-policy cycles:

1. `2026-05-25-s2-04-legacy-artifact-policy`
2. `2026-05-25-s2-05-agentic-default-gate-decision`

These cycles are intentionally narrow. They prove that current-task artifacts
can be validated reliably by explicit path, not that every historical archive
is validator-clean.

## Quality-Gate Implications

- Default `run-quality-gates` must not scan all task cards or completed-task
  reports.
- A future current-task default gate needs an explicit current artifact
  declaration, not filesystem discovery across historical archives.
- Completed-task report validation should remain opt-in until the archive is
  created and indexed.
- Closure score remains advisory unless a later task defines a calibrated
  failure threshold and override path.

## Review Checklist

Before using an older artifact as active evidence, answer:

- Is the artifact `validator-clean`, `migrated`, or `migratable-legacy`?
- What new decision depends on it?
- Is migration scoped to the dependency, or is this only historical cleanup?
- Would a failure reveal a current task problem or only old-format drift?
- Is another branch or conversation still editing the artifact?

If the answer points to old-format drift or parallel ownership, do not include
the artifact in the current gate.
