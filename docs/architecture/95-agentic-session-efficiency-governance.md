# Agentic Session Efficiency Governance

Status: proposed architecture.

Date: 2026-05-26

Related audit layer:
`docs/architecture/94-repository-audit-statistics-architecture.md`.

## Purpose

GCS needs a quantitative way to discuss the relationship between agentic
session cost and durable engineering output. The goal is not to minimize token
usage in isolation. The goal is to detect waste, compare similar task classes,
and improve the repository's agentic workflow without sacrificing correctness,
evidence, or maintainability.

This governance layer answers:

- how many tokens, tool calls, and minutes a session consumed;
- what durable artifacts, tests, reports, decisions, and commits it produced;
- whether verification and closure quality justified the cost;
- whether rework, failed gates, or unresolved risks reduced the useful value;
- which task types have healthy or unhealthy value-per-token patterns.

## Source Basis

Local sources:

| Source | Used for |
| --- | --- |
| `docs/research/20260524/agentic-se-dimensions-metrics-research-report.md` | Lifecycle metrics, closure score, evidence traceability, and anti-metrics. |
| `docs/agentic/institutional-agents/README.md` | Candidate `measure-tradeoff` governance role for time, token, complexity, and value accounting. |
| `tools/agentic_design/agentic_toolkit.py` | Existing closure-score implementation and completed-task validation gates. |
| `docs/architecture/94-repository-audit-statistics-architecture.md` | Repository-shape audit and project overview metrics. |
| `docs/research/20260514-GLM-ACG/01-IBM-ACG-deep-dive.md` | Effectiveness, efficiency, cost, and joint quality-cost optimization framing. |

Inference:

- Token efficiency is meaningful only when paired with outcome quality,
  validation evidence, task type, and rework cost.
- Session-level telemetry should start as a diagnostic report. It should not be
  a blocking quality gate until the project has a calibrated baseline.

## Boundary

This layer belongs to agentic support tooling and project governance. It may
read task cards, completed-task archives, repository-audit reports, validation
results, commit metadata, and externally supplied token telemetry.

It must not:

- change solver behavior;
- call external APIs by default;
- infer exact token counts when the runtime does not expose them;
- reward raw line count, file count, or PR count without evidence quality;
- compare research, implementation, debugging, and closure sessions as if they
  were the same kind of work.

## Task Classes

Efficiency comparisons are valid only inside comparable task classes:

| Class | Primary output | Typical evidence |
| --- | --- | --- |
| `research_design` | durable report, architecture note, decision map | source register, recommendations, open questions |
| `implementation` | code, tests, fixtures, docs | focused tests, quality gates, commit |
| `debug_repair` | removed failure, reduced rework, regression coverage | failing-before/passing-after evidence |
| `governance_closure` | task card, archive, audit, roadmap update | validators, closure score, traceability |
| `exploration` | bounded findings, candidate plan, risk map | explicit stopping condition and follow-up |

## Session Efficiency Record

The durable schema should be JSON-compatible and may later be projected into
Markdown dashboards:

```json
{
  "schema_version": "gcs-agentic-session-efficiency-0.1",
  "session_id": "<runtime-or-manual-id>",
  "task_id": "2026-05-26-example",
  "task_class": "implementation",
  "started_at": "2026-05-26T00:00:00+08:00",
  "ended_at": "2026-05-26T00:30:00+08:00",
  "token_telemetry": {
    "input_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0,
    "source": "runtime|api|manual|unknown",
    "confidence": "exact|estimated|unknown"
  },
  "execution_telemetry": {
    "wall_minutes": 0,
    "tool_calls": 0,
    "shell_commands": 0,
    "files_changed": 0,
    "lines_added": 0,
    "lines_deleted": 0
  },
  "durable_outputs": {
    "code_files": 0,
    "test_files": 0,
    "architecture_docs": 0,
    "research_reports": 0,
    "task_cards": 0,
    "completed_archives": 0,
    "generated_reports": 0,
    "commits": 0
  },
  "validation": {
    "checks_run": 0,
    "checks_passed": 0,
    "checks_failed": 0,
    "checks_skipped": 0,
    "closure_score": 0,
    "closure_score_max": 40
  },
  "outcome_assessment": {
    "scope_completion": 0.0,
    "risk_reduction": 0.0,
    "reuse_score": 0.0,
    "review_burden": 0.0,
    "rework_penalty": 0.0,
    "outcome_score": 0.0,
    "value_per_1k_tokens": 0.0,
    "net_efficiency": 0.0
  }
}
```

Token fields can be absent or marked `unknown` when runtime telemetry is not
available. Unknown token counts should exclude the record from token-efficiency
aggregates rather than forcing a misleading estimate.

## Outcome Score

Use a bounded score from 0 to 1:

```text
closure_score_norm = closure_score / closure_score_max

OutcomeScore =
  0.25 * closure_score_norm +
  0.20 * validation_score +
  0.20 * durable_artifact_score +
  0.15 * scope_completion +
  0.10 * risk_reduction +
  0.10 * reuse_score
```

Subscore guidance:

| Subscore | Meaning |
| --- | --- |
| `validation_score` | Pass quality of focused tests, docs validators, PR audits, and skipped-check justification. |
| `durable_artifact_score` | Whether the session left inspectable repo artifacts instead of only chat claims. |
| `scope_completion` | Whether the accepted task scope was actually completed. |
| `risk_reduction` | Whether the session removed known warnings, failures, ambiguity, or governance gaps. |
| `reuse_score` | Whether the output helps future sessions through tools, schemas, docs, skills, fixtures, or reports. |

Do not compute these from line count alone. For design and governance work, a
short architecture note can be higher value than many generated lines.

## Efficiency Metrics

Primary metrics:

```text
TokenCostK = total_tokens / 1000
ValuePer1KTokens = OutcomeScore / TokenCostK
NetEfficiency = OutcomeScore * (1 - rework_penalty) / TokenCostK
```

Secondary metrics:

| Metric | Formula | Use |
| --- | --- | --- |
| `ArtifactDensity` | durable_artifact_count / TokenCostK | Detect chat-heavy sessions with little persistent output. |
| `ValidationYield` | checks_passed / TokenCostK | Compare verification efficiency inside similar task classes. |
| `ClosureYield` | closure_score / TokenCostK | Detect expensive sessions that still leave poor handoff state. |
| `ReworkAdjustedYield` | OutcomeScore * (1 - rework_penalty) / TokenCostK | Penalize failed checks, reversions, and unresolved severe risks. |
| `DeltaOutcomePerTurn` | delta_outcome_score / delta_tokens | Evaluate individual interaction efficiency when turn-level telemetry exists. |

## Rework Penalty

Rework penalty is also bounded from 0 to 1:

```text
rework_penalty =
  min(
    1.0,
    0.10 * failed_checks +
    0.10 * unjustified_skipped_checks +
    0.20 * reverted_or_discarded_changes +
    0.20 * unresolved_high_severity_risks +
    0.10 * stale_or_broken_artifact_links
  )
```

The penalty should be evidence-based. A failed command that is diagnosed and
fixed in the same session is weaker evidence of waste than a failed gate left
unresolved.

## Interaction-Level Evaluation

When per-turn telemetry is available, record deltas:

```text
DeltaValuePer1KTokens = DeltaOutcomeScore / (DeltaTokens / 1000)
```

Each interaction should be tagged:

- `clarify_intent`
- `research_context`
- `plan`
- `implement`
- `debug`
- `verify`
- `closeout`
- `handoff`

This lets the project distinguish useful context-gathering turns from waste.
For example, a research turn can have no code output but still raise the final
outcome score by preventing the wrong implementation path.

## Storage Policy

Use three levels:

```text
var/session-efficiency/
  latest.session-efficiency.json

docs/reports/session-efficiency/YYYY-MM-DD/
  README.md
  session-efficiency.json

docs/completed-tasks/<task>/
  README.md
```

Rules:

- `var/` is local scratch and should not normally be committed.
- `docs/reports/session-efficiency/` is for calibrated or milestone summaries.
- Completed-task archives may include a compact session-efficiency table, but
  should not duplicate large telemetry payloads.
- Records with unknown token counts can still contribute to outcome and
  validation dashboards, but not to value-per-token aggregates.

## Rollout Phases

### Phase 0: Manual Diagnostic Notes

- Add the architecture note and keep token efficiency non-blocking.
- Use completed-task archives to record whether token telemetry was available.
- Compare only obvious outliers.

### Phase 1: Schema And Reporter

- Add a `SessionEfficiencyRecord` schema and a small reporter.
- Allow manual token fields with `confidence: estimated` or `unknown`.
- Project session summaries into Markdown tables.

### Phase 2: Repository-Audit Join

- Join files changed, artifact classes, generated reports, and task archives
  from repository-audit snapshots.
- Add task-class buckets and avoid cross-bucket comparisons.

### Phase 3: Calibration

- Collect at least 10 to 20 sessions before setting thresholds.
- Review outliers manually.
- Tune subscore weights only when examples show systematic distortion.

### Phase 4: Optional Governance Gate

- Add a non-blocking warning for missing telemetry on non-trivial tasks.
- Keep token efficiency out of blocking gates unless humans explicitly promote
  a narrow, calibrated policy.

## Acceptance Criteria For First Implementation

A first implementation task is complete when:

- a JSON schema or dataclass exists for `SessionEfficiencyRecord`;
- a report command can render session-efficiency Markdown from one or more
  records;
- completed-task archives have an optional, documented telemetry section;
- token counts can be exact, estimated, or unknown;
- no score is computed when denominator token counts are unknown;
- tests cover known-token, unknown-token, and high-rework examples.

## Anti-Metrics

Do not optimize:

- fewer tokens without checking correctness or handoff quality;
- more files, lines, commits, or reports without validation;
- more agent roles or skills without evidence of reuse;
- higher value-per-token by skipping research, tests, or closure;
- a single global leaderboard across different task classes.

## Open Decisions

- Whether token telemetry can be captured automatically from the active runtime
  or must remain manually entered.
- Whether session-efficiency records should live in `tools/agentic_design` or a
  separate `tools/session_efficiency` package.
- Whether a future `measure-tradeoff` institutional agent should be promoted
  after two or more real session-efficiency reports.
