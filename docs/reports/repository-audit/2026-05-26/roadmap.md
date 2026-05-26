# Repository Audit Statistics Roadmap

Date: 2026-05-26

Scope: short-term executable audit-statistics items, plus medium and long-term
plans that should wait for more accepted evidence.

## Source Register

| Source | Used for | Confidence |
| --- | --- | --- |
| `docs/architecture/94-repository-audit-statistics-architecture.md` | Repository audit ownership, storage, trend, and gate policy. | High |
| `docs/architecture/95-agentic-session-efficiency-governance.md` | Token/outcome relationship and non-blocking efficiency metrics. | High |
| `docs/reports/repository-audit/README.md` | Current accepted snapshot registry and baseline count. | High |
| `docs/completed-tasks/2026-05-26-repository-audit-snapshot-registry/README.md` | Follow-up items after registry seed. | High |
| `tools/repository_audit/README.md` | Implemented repository-audit commands. | High |
| `tools/session_efficiency/README.md` | Implemented session-efficiency commands. | High |

## Current State

The repository now has one accepted repository-audit baseline:

- snapshot id: `2026-05-26`
- files: `825`
- physical text lines: `149,448`
- findings: `0`

The audit layer can collect snapshots, render reports, compare revisions,
render diffs, render accepted-registry trends, and produce compact archive
delta sections. The session-efficiency layer can render non-blocking reports
from manual or runtime-provided records, with token fields marked exact,
estimated, or unknown.

## Short-Term Plan

Completed in this task:

- `accepted-trend`: render `docs/reports/repository-audit/trend.md` directly
  from accepted snapshot manifests.
- `archive-delta`: render compact completed-task audit-delta sections from
  repository-audit diff JSON.
- `diff --head-index`: compare the staged index to a base revision so archive
  deltas can stay scoped to a task before commit.
- `tools/session_efficiency`: provide `SessionEfficiencyRecord` schema,
  derived metrics, Markdown reporting, and tests for known-token,
  unknown-token, and high-rework cases.
- `docs/reports/session-efficiency/2026-05-26/`: store the first non-blocking
  session-efficiency report for this audit-statistics execution task.

Short-term next steps after this task:

- Add one accepted snapshot after the next meaningful repository-audit or
  governance change.
- Add another accepted snapshot after the next solver/runtime/tool milestone.
- Include generated `repository-audit-delta.md` in every non-trivial
  completed-task archive that touches support tooling, quality gates, or
  governance docs.

## Medium-Term Plan

Medium-term work should start after the registry has at least three accepted
snapshots:

- Generate trend tables by artifact class, lifecycle layer, top-level folder,
  and GCS module from the accepted registry.
- Add a registry-backed `accepted-trend --json` output if dashboard tooling
  needs machine-readable trend data.
- Join repository-audit deltas with session-efficiency records so each task can
  show outcome score, validation yield, and durable artifact density beside
  files/lines/findings deltas.
- Add a non-blocking quality-gate warning when a non-trivial completed-task
  archive lacks an audit-delta section.
- Review recurring cadence: per phase close, weekly, or release-only.

## Long-Term Plan

Long-term work should stay evidence-driven and avoid premature thresholds:

- Add chart rendering only after the trend series has enough meaningful points
  to avoid decorative but weak evidence.
- Calibrate token-efficiency thresholds after at least 10 to 20 comparable
  session-efficiency records.
- Decide whether to promote a `measure-tradeoff` institutional agent after two
  or more real efficiency reports show reusable review value.
- Consider optional external adapters such as `cloc`, `tokei`, or
  GitHub Linguist parity checks only when local audit categories stabilize.
- Promote repository-audit checks into default gates only after accepted
  snapshots show low false-positive risk and documented exemptions are in
  place.

## Decision Rules

- Do not treat raw lines, files, or token count as value by themselves.
- Keep token-efficiency records non-blocking until calibrated.
- Prefer accepted snapshots from committed revisions over dirty worktree
  snapshots.
- Treat missing token telemetry as `unknown`, not as zero.
- Compare efficiency only inside similar task classes.

## Open Questions

- Can token telemetry be captured automatically from the active runtime, or
  should records remain manual/unknown by default?
- Should accepted snapshots be taken after every non-trivial task or only after
  phase/release checkpoints?
- Should audit-delta absence become a warning in task archive validation after
  two more archives use the pattern successfully?
