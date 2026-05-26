from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SCHEMA_VERSION = "gcs-agentic-session-efficiency-0.1"
TOOL_VERSION = "0.1"


@dataclass(frozen=True)
class TokenTelemetry:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    source: str = "unknown"
    confidence: str = "unknown"


@dataclass(frozen=True)
class ExecutionTelemetry:
    wall_minutes: float | None = None
    tool_calls: int = 0
    shell_commands: int = 0
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0


@dataclass(frozen=True)
class DurableOutputs:
    code_files: int = 0
    test_files: int = 0
    architecture_docs: int = 0
    research_reports: int = 0
    task_cards: int = 0
    completed_archives: int = 0
    generated_reports: int = 0
    commits: int = 0


@dataclass(frozen=True)
class Validation:
    checks_run: int = 0
    checks_passed: int = 0
    checks_failed: int = 0
    checks_skipped: int = 0
    closure_score: int | None = None
    closure_score_max: int = 40


@dataclass(frozen=True)
class OutcomeAssessment:
    scope_completion: float = 0.0
    risk_reduction: float = 0.0
    reuse_score: float = 0.0
    review_burden: float = 0.0
    rework_penalty: float = 0.0
    outcome_score: float = 0.0
    value_per_1k_tokens: float | None = None
    net_efficiency: float | None = None


@dataclass(frozen=True)
class SessionEfficiencyRecord:
    schema_version: str = SCHEMA_VERSION
    tool_version: str = TOOL_VERSION
    session_id: str = ""
    task_id: str = ""
    task_class: str = "implementation"
    started_at: str | None = None
    ended_at: str | None = None
    token_telemetry: TokenTelemetry = field(default_factory=TokenTelemetry)
    execution_telemetry: ExecutionTelemetry = field(default_factory=ExecutionTelemetry)
    durable_outputs: DurableOutputs = field(default_factory=DurableOutputs)
    validation: Validation = field(default_factory=Validation)
    outcome_assessment: OutcomeAssessment = field(default_factory=OutcomeAssessment)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionEfficiencyRecord":
        return cls(
            schema_version=str(data.get("schema_version") or SCHEMA_VERSION),
            tool_version=str(data.get("tool_version") or TOOL_VERSION),
            session_id=str(data.get("session_id") or ""),
            task_id=str(data.get("task_id") or ""),
            task_class=str(data.get("task_class") or "implementation"),
            started_at=data.get("started_at"),
            ended_at=data.get("ended_at"),
            token_telemetry=TokenTelemetry(**dict(data.get("token_telemetry") or {})),
            execution_telemetry=ExecutionTelemetry(**dict(data.get("execution_telemetry") or {})),
            durable_outputs=DurableOutputs(**dict(data.get("durable_outputs") or {})),
            validation=Validation(**dict(data.get("validation") or {})),
            outcome_assessment=OutcomeAssessment(**dict(data.get("outcome_assessment") or {})),
            notes=str(data.get("notes") or ""),
        )
