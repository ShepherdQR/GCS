from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import SCHEMA_VERSION, TOOL_VERSION, SessionEfficiencyRecord


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _fmt_float(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{_as_float(value):.3f}"


def _fmt_int(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{_as_int(value):,}"


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def read_record(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _known_token_cost_k(record: SessionEfficiencyRecord) -> float | None:
    telemetry = record.token_telemetry
    if telemetry.confidence == "unknown":
        return None
    total = telemetry.total_tokens
    if total is None:
        total = (telemetry.input_tokens or 0) + (telemetry.output_tokens or 0)
    if total <= 0:
        return None
    return total / 1000.0


def _durable_artifact_count(record: SessionEfficiencyRecord) -> int:
    outputs = record.durable_outputs
    return (
        outputs.code_files
        + outputs.test_files
        + outputs.architecture_docs
        + outputs.research_reports
        + outputs.task_cards
        + outputs.completed_archives
        + outputs.generated_reports
        + outputs.commits
    )


def _validation_score(record: SessionEfficiencyRecord) -> float:
    validation = record.validation
    effective = max(0, validation.checks_run - validation.checks_skipped)
    if effective <= 0:
        return 0.0
    return _clamp01(validation.checks_passed / effective)


def _closure_score_norm(record: SessionEfficiencyRecord) -> float:
    validation = record.validation
    if validation.closure_score is None or validation.closure_score_max <= 0:
        return 0.0
    return _clamp01(validation.closure_score / validation.closure_score_max)


def _rework_penalty(record: SessionEfficiencyRecord) -> float:
    validation = record.validation
    explicit = _as_float(record.outcome_assessment.rework_penalty)
    evidence_penalty = min(1.0, 0.10 * validation.checks_failed)
    return _clamp01(max(explicit, evidence_penalty))


def enrich_record(data: dict[str, Any]) -> dict[str, Any]:
    record = SessionEfficiencyRecord.from_dict(data)
    outcome = record.outcome_assessment
    validation_score = _validation_score(record)
    durable_artifact_score = _clamp01(_durable_artifact_count(record) / 5.0)
    closure_score_norm = _closure_score_norm(record)
    rework_penalty = _rework_penalty(record)

    outcome_score = _clamp01(
        0.25 * closure_score_norm
        + 0.20 * validation_score
        + 0.20 * durable_artifact_score
        + 0.15 * _clamp01(outcome.scope_completion)
        + 0.10 * _clamp01(outcome.risk_reduction)
        + 0.10 * _clamp01(outcome.reuse_score)
    )

    token_cost_k = _known_token_cost_k(record)
    if token_cost_k is None:
        value_per_1k_tokens = None
        net_efficiency = None
        artifact_density = None
        validation_yield = None
    else:
        value_per_1k_tokens = outcome_score / token_cost_k
        net_efficiency = outcome_score * (1.0 - rework_penalty) / token_cost_k
        artifact_density = _durable_artifact_count(record) / token_cost_k
        validation_yield = record.validation.checks_passed / token_cost_k

    result = asdict(record)
    result["schema_version"] = SCHEMA_VERSION
    result["tool_version"] = TOOL_VERSION
    result["derived_metrics"] = {
        "durable_artifact_count": _durable_artifact_count(record),
        "validation_score": validation_score,
        "durable_artifact_score": durable_artifact_score,
        "closure_score_norm": closure_score_norm,
        "rework_penalty": rework_penalty,
        "outcome_score": outcome_score,
        "token_cost_k": token_cost_k,
        "value_per_1k_tokens": value_per_1k_tokens,
        "net_efficiency": net_efficiency,
        "artifact_density": artifact_density,
        "validation_yield": validation_yield,
    }
    return result


def render_markdown_report(records: list[dict[str, Any]], *, command: str | None = None) -> str:
    enriched = [enrich_record(record) for record in records]
    known_token_records = [
        record for record in enriched if record["derived_metrics"]["token_cost_k"] is not None
    ]
    avg_outcome = (
        sum(record["derived_metrics"]["outcome_score"] for record in enriched) / len(enriched)
        if enriched
        else 0.0
    )

    lines: list[str] = [
        "# GCS Session Efficiency Report",
        "",
        f"Schema: `{SCHEMA_VERSION}`",
        f"Tool: `{TOOL_VERSION}`",
        f"Records: `{len(enriched)}`",
        f"Token-known records: `{len(known_token_records)}`",
        f"Average outcome score: `{_fmt_float(avg_outcome)}`",
        "",
        "## Session Records",
        "",
    ]
    lines.extend(
        _table(
            [
                "Task",
                "Class",
                "Tokens",
                "Confidence",
                "Artifacts",
                "Checks",
                "Closure",
                "Outcome",
                "Value/1k",
                "Net",
            ],
            [
                [
                    record.get("task_id") or record.get("session_id") or "<unknown>",
                    record.get("task_class", ""),
                    _fmt_int(record.get("token_telemetry", {}).get("total_tokens")),
                    record.get("token_telemetry", {}).get("confidence", "unknown"),
                    _fmt_int(record["derived_metrics"]["durable_artifact_count"]),
                    (
                        f"{_fmt_int(record.get('validation', {}).get('checks_passed'))}/"
                        f"{_fmt_int(record.get('validation', {}).get('checks_run'))}"
                    ),
                    (
                        f"{_fmt_int(record.get('validation', {}).get('closure_score'))}/"
                        f"{_fmt_int(record.get('validation', {}).get('closure_score_max'))}"
                    ),
                    _fmt_float(record["derived_metrics"]["outcome_score"]),
                    _fmt_float(record["derived_metrics"]["value_per_1k_tokens"]),
                    _fmt_float(record["derived_metrics"]["net_efficiency"]),
                ]
                for record in enriched
            ],
        )
    )

    lines.extend(["", "## Interpretation Rules", ""])
    lines.extend(
        [
            "- Records with unknown token telemetry participate in outcome reporting but not value-per-token aggregates.",
            "- Scores compare best within similar task classes; they are not a global leaderboard.",
            "- Repository-audit deltas and closure evidence should be reviewed alongside any token metric.",
        ]
    )

    lines.extend(["", "## Reproduction", ""])
    if command:
        lines.extend(["```bat", command, "```"])
    else:
        lines.append("Generated from supplied session-efficiency records.")

    return "\n".join(lines).rstrip() + "\n"


def write_markdown_report(records: list[dict[str, Any]], output: Path, *, command: str | None = None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown_report(records, command=command), encoding="utf-8", newline="\n")


def write_enriched_record(record: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(enrich_record(record), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
