"""Lightweight Full/Lite cache-hit experiment runner.

This module intentionally uses only the Python standard library. It is meant to
keep the cache-hit diagnosis experiment runnable even when the richer
``python -m tools.token_audit`` CLI is unavailable because optional dependencies
such as PyYAML or Click are missing.
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "tools" / "token_audit" / "audit.db"
DEFAULT_RUNS = (
    ROOT
    / "docs"
    / "research"
    / "20260530"
    / "cache-hit-diagnosis-experiment"
    / "experiment-runs.csv"
)
DEFAULT_REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "token-audit"
    / "cache-hit-diagnosis-20260530"
    / "pilot-summary.md"
)
DEFAULT_JSON_REPORT = DEFAULT_REPORT.with_suffix(".json")

CACHEABLE_PREFIX_ESTIMATE = 39_000
CSV_FIELDS = [
    "run_id",
    "date",
    "task_pair",
    "mode",
    "task_type",
    "risk",
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "estimated_cache_write_tokens",
    "legacy_cache_hit_rate",
    "estimated_raw_cache_hit_rate",
    "token_leverage_ratio",
    "estimated_cold_load_overhead_ratio",
    "bei_composite",
    "audit_score_0_5",
    "validation_passed",
    "rework_turns",
    "defect_or_reopen_count",
    "skills_invoked",
    "files_touched",
    "notes",
]


@dataclass(frozen=True)
class SessionMetrics:
    session_id: str
    started_at: str
    project_name: str
    model_id: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_creation_tokens: int
    estimated_cache_write_tokens: int
    legacy_cache_hit_rate: float
    estimated_raw_cache_hit_rate: float
    token_leverage_ratio: float
    estimated_cold_load_overhead_ratio: float
    bei_composite: float | None
    task_type: str
    task_risk_level: str
    skills_invoked: str
    files_touched: int


def safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def db_connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def session_metrics(conn: sqlite3.Connection, session_id: str) -> SessionMetrics:
    row = conn.execute(
        """
        SELECT id, project_name, model_id, started_at,
               total_input_tokens, total_output_tokens,
               total_cache_read_tokens, total_cache_creation_tokens,
               bei_composite, task_type, task_risk_level,
               skills_invoked, files_touched
        FROM sessions
        WHERE id = ?
        """,
        (session_id,),
    ).fetchone()
    if row is None:
        raise SystemExit(f"session not found: {session_id}")

    input_tokens = int(row["total_input_tokens"] or 0)
    output_tokens = int(row["total_output_tokens"] or 0)
    cache_read_tokens = int(row["total_cache_read_tokens"] or 0)
    cache_creation_tokens = int(row["total_cache_creation_tokens"] or 0)
    estimated_write = (
        cache_creation_tokens if cache_creation_tokens > 0 else CACHEABLE_PREFIX_ESTIMATE
    )
    legacy_hit = safe_div(cache_read_tokens, cache_read_tokens + input_tokens)
    estimated_raw_hit = safe_div(cache_read_tokens, cache_read_tokens + estimated_write)
    tlr = safe_div(output_tokens, input_tokens)
    sclor = safe_div(CACHEABLE_PREFIX_ESTIMATE, input_tokens)

    return SessionMetrics(
        session_id=str(row["id"]),
        started_at=str(row["started_at"] or ""),
        project_name=str(row["project_name"] or ""),
        model_id=str(row["model_id"] or ""),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read_tokens,
        cache_creation_tokens=cache_creation_tokens,
        estimated_cache_write_tokens=estimated_write,
        legacy_cache_hit_rate=legacy_hit,
        estimated_raw_cache_hit_rate=estimated_raw_hit,
        token_leverage_ratio=tlr,
        estimated_cold_load_overhead_ratio=sclor,
        bei_composite=row["bei_composite"],
        task_type=str(row["task_type"] or ""),
        task_risk_level=str(row["task_risk_level"] or ""),
        skills_invoked=str(row["skills_invoked"] or "[]"),
        files_touched=int(row["files_touched"] or 0),
    )


def inspect_db(args: argparse.Namespace) -> int:
    with db_connect(args.db) as conn:
        counts = {}
        for table in ["sessions", "turns", "tool_calls", "edits", "daily_summary"]:
            counts[table] = int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        agg = conn.execute(
            """
            SELECT SUM(total_input_tokens), SUM(total_output_tokens),
                   SUM(total_cache_read_tokens), SUM(total_cache_creation_tokens),
                   AVG(bei_composite)
            FROM sessions
            """
        ).fetchone()

    input_tokens = int(agg[0] or 0)
    output_tokens = int(agg[1] or 0)
    cache_read_tokens = int(agg[2] or 0)
    cache_creation_tokens = int(agg[3] or 0)
    sessions = counts["sessions"]
    estimated_writes = CACHEABLE_PREFIX_ESTIMATE * sessions
    payload = {
        "db": str(args.db),
        "counts": counts,
        "aggregate": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_tokens": cache_read_tokens,
            "cache_creation_tokens": cache_creation_tokens,
            "avg_bei_composite": agg[4],
        },
        "metrics": {
            "legacy_cache_hit_rate": safe_div(
                cache_read_tokens, cache_read_tokens + input_tokens
            ),
            "estimated_raw_cache_hit_rate": safe_div(
                cache_read_tokens, cache_read_tokens + estimated_writes
            ),
            "token_leverage_ratio": safe_div(output_tokens, input_tokens),
            "estimated_cold_load_overhead_ratio": safe_div(
                estimated_writes, input_tokens
            ),
        },
        "caveats": [
            "DeepSeek cache_creation_tokens are often zero; estimated raw cache metrics use 39000 tokens/session.",
            "Stored USD cost is intentionally excluded from this experiment runner.",
        ],
    }
    write_payload(payload, args.format)
    return 0


def list_sessions(args: argparse.Namespace) -> int:
    with db_connect(args.db) as conn:
        rows = conn.execute(
            """
            SELECT id, started_at, project_name, model_id,
                   total_input_tokens, total_output_tokens,
                   total_cache_read_tokens, bei_composite, task_type
            FROM sessions
            ORDER BY started_at DESC
            LIMIT ?
            """,
            (args.limit,),
        ).fetchall()
    payload = []
    for row in rows:
        metrics = {
            "session_id": row["id"],
            "started_at": row["started_at"],
            "project_name": row["project_name"],
            "model_id": row["model_id"],
            "input_tokens": row["total_input_tokens"],
            "output_tokens": row["total_output_tokens"],
            "cache_read_tokens": row["total_cache_read_tokens"],
            "bei_composite": row["bei_composite"],
            "task_type": row["task_type"] or "",
        }
        metrics["token_leverage_ratio"] = safe_div(
            row["total_output_tokens"] or 0, row["total_input_tokens"] or 0
        )
        payload.append(metrics)
    write_payload({"sessions": payload}, args.format)
    return 0


def record_run(args: argparse.Namespace) -> int:
    mode = normalize_mode(args.mode)
    validation_passed = normalize_bool(args.validation_passed)
    with db_connect(args.db) as conn:
        metrics = session_metrics(conn, args.session_id)

    row = {
        "run_id": args.run_id,
        "date": args.date or date.today().isoformat(),
        "task_pair": args.task_pair,
        "mode": mode,
        "task_type": args.task_type or metrics.task_type,
        "risk": args.risk or metrics.task_risk_level or "medium",
        "input_tokens": metrics.input_tokens,
        "output_tokens": metrics.output_tokens,
        "cache_read_tokens": metrics.cache_read_tokens,
        "estimated_cache_write_tokens": metrics.estimated_cache_write_tokens,
        "legacy_cache_hit_rate": fmt_float(metrics.legacy_cache_hit_rate),
        "estimated_raw_cache_hit_rate": fmt_float(metrics.estimated_raw_cache_hit_rate),
        "token_leverage_ratio": fmt_float(metrics.token_leverage_ratio),
        "estimated_cold_load_overhead_ratio": fmt_float(
            metrics.estimated_cold_load_overhead_ratio
        ),
        "bei_composite": fmt_optional_float(metrics.bei_composite),
        "audit_score_0_5": fmt_float(args.audit_score),
        "validation_passed": "true" if validation_passed else "false",
        "rework_turns": args.rework_turns,
        "defect_or_reopen_count": args.defect_or_reopen_count,
        "skills_invoked": args.skills_invoked or metrics.skills_invoked,
        "files_touched": args.files_touched
        if args.files_touched is not None
        else metrics.files_touched,
        "notes": args.notes or f"session_id={metrics.session_id}",
    }
    append_csv(args.runs, row)
    write_payload({"recorded": row}, args.format)
    return 0


def summarize(args: argparse.Namespace) -> int:
    rows = read_run_rows(args.runs)
    pairs = summarize_pairs(rows)
    aggregate = summarize_aggregate(pairs)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runs_file": str(args.runs),
        "runs_count": len(rows),
        "complete_pairs_count": len(pairs),
        "pairs": pairs,
        "aggregate": aggregate,
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render_markdown(payload), encoding="utf-8")
    if not args.output and not args.json_output:
        write_payload(payload, args.format)
    return 0


def append_csv(path: Path, row: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def read_run_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if is_real_run(row)]


def is_real_run(row: dict[str, str]) -> bool:
    if not row.get("run_id") or row.get("run_id") == "example":
        return False
    return bool(row.get("task_pair") and row.get("mode"))


def summarize_pairs(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, list[dict[str, str]]]] = {}
    for row in rows:
        pair = row.get("task_pair", "")
        mode = normalize_mode(row.get("mode", ""))
        grouped.setdefault(pair, {}).setdefault(mode, []).append(row)

    summaries = []
    for pair, by_mode in sorted(grouped.items()):
        full_rows = by_mode.get("Full", [])
        lite_rows = by_mode.get("Lite", [])
        if not full_rows or not lite_rows:
            summaries.append(
                {
                    "task_pair": pair,
                    "status": "incomplete",
                    "full_runs": len(full_rows),
                    "lite_runs": len(lite_rows),
                    "classification": "needs paired data",
                }
            )
            continue
        full = average_rows(full_rows)
        lite = average_rows(lite_rows)
        classification = classify_pair(full, lite)
        summaries.append(
            {
                "task_pair": pair,
                "status": "complete",
                "full_runs": len(full_rows),
                "lite_runs": len(lite_rows),
                "full": full,
                "lite": lite,
                "delta": pair_delta(full, lite),
                "classification": classification,
            }
        )
    return summaries


def average_rows(rows: list[dict[str, str]]) -> dict[str, float]:
    return {
        "input_tokens": avg(rows, "input_tokens"),
        "output_tokens": avg(rows, "output_tokens"),
        "token_leverage_ratio": avg(rows, "token_leverage_ratio"),
        "legacy_cache_hit_rate": avg(rows, "legacy_cache_hit_rate"),
        "estimated_raw_cache_hit_rate": avg(rows, "estimated_raw_cache_hit_rate"),
        "estimated_cold_load_overhead_ratio": avg(
            rows, "estimated_cold_load_overhead_ratio"
        ),
        "bei_composite": avg(rows, "bei_composite"),
        "audit_score_0_5": avg(rows, "audit_score_0_5"),
        "validation_passed_rate": avg_bool(rows, "validation_passed"),
        "rework_turns": avg(rows, "rework_turns"),
        "defect_or_reopen_count": avg(rows, "defect_or_reopen_count"),
    }


def pair_delta(full: dict[str, float], lite: dict[str, float]) -> dict[str, float]:
    return {
        "lite_input_savings_pct": safe_div(
            full["input_tokens"] - lite["input_tokens"], full["input_tokens"]
        ),
        "lite_audit_delta_pct": safe_div(
            lite["audit_score_0_5"] - full["audit_score_0_5"],
            full["audit_score_0_5"],
        ),
        "lite_bei_delta_pct": safe_div(
            lite["bei_composite"] - full["bei_composite"], full["bei_composite"]
        ),
        "lite_rework_delta": lite["rework_turns"] - full["rework_turns"],
        "lite_defect_delta": lite["defect_or_reopen_count"]
        - full["defect_or_reopen_count"],
        "lite_validation_delta": lite["validation_passed_rate"]
        - full["validation_passed_rate"],
    }


def classify_pair(full: dict[str, float], lite: dict[str, float]) -> str:
    delta = pair_delta(full, lite)
    if (
        delta["lite_input_savings_pct"] >= 0.25
        and delta["lite_audit_delta_pct"] >= -0.10
        and delta["lite_bei_delta_pct"] >= -0.10
        and delta["lite_rework_delta"] <= 0
        and delta["lite_defect_delta"] <= 0
    ):
        return "redundant-overhead"
    full_audit_advantage = safe_div(
        full["audit_score_0_5"] - lite["audit_score_0_5"], lite["audit_score_0_5"]
    )
    if (
        full_audit_advantage >= 0.15
        or delta["lite_rework_delta"] > 0
        or delta["lite_defect_delta"] > 0
        or delta["lite_validation_delta"] < 0
    ):
        return "healthy-institutionalization"
    return "mixed-or-inconclusive"


def summarize_aggregate(pairs: list[dict[str, object]]) -> dict[str, object]:
    complete = [pair for pair in pairs if pair.get("status") == "complete"]
    counts = {
        "redundant-overhead": 0,
        "healthy-institutionalization": 0,
        "mixed-or-inconclusive": 0,
        "needs paired data": 0,
    }
    for pair in pairs:
        counts[str(pair.get("classification", "mixed-or-inconclusive"))] = (
            counts.get(str(pair.get("classification")), 0) + 1
        )
    if not complete:
        return {
            "classification_counts": counts,
            "overall_classification": "needs paired data",
            "recommendation": "Record at least one Full and one Lite run for a task_pair.",
        }
    if counts["redundant-overhead"] > counts["healthy-institutionalization"]:
        overall = "redundant-overhead"
    elif counts["healthy-institutionalization"] > counts["redundant-overhead"]:
        overall = "healthy-institutionalization"
    else:
        overall = "mixed-or-inconclusive"
    return {
        "classification_counts": counts,
        "overall_classification": overall,
        "recommendation": "Do not promote policy until 6 to 8 paired runs are complete."
        if len(complete) < 6
        else "Review task-class split and promote only the classes that meet thresholds.",
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Cache-Hit Full/Lite Pilot Summary\n",
        f"Generated: `{payload['generated_at_utc']}`\n",
        f"Runs file: `{payload['runs_file']}`\n",
        "\n## Aggregate\n",
    ]
    aggregate = payload["aggregate"]
    lines.append(
        f"- Complete pairs: {payload['complete_pairs_count']} / {len(payload['pairs'])}\n"
    )
    lines.append(f"- Overall classification: `{aggregate['overall_classification']}`\n")
    lines.append(f"- Recommendation: {aggregate['recommendation']}\n")
    lines.append("\n## Pair Results\n")
    lines.append(
        "| Pair | Status | Classification | Lite input savings | Audit delta | BEI delta | Rework delta | Defect delta |\n"
    )
    lines.append("|---|---|---|---:|---:|---:|---:|---:|\n")
    for pair in payload["pairs"]:
        if pair.get("status") != "complete":
            lines.append(
                f"| {pair['task_pair']} | incomplete | {pair['classification']} |  |  |  |  |  |\n"
            )
            continue
        delta = pair["delta"]
        lines.append(
            f"| {pair['task_pair']} | complete | {pair['classification']} | "
            f"{pct(delta['lite_input_savings_pct'])} | "
            f"{pct(delta['lite_audit_delta_pct'])} | "
            f"{pct(delta['lite_bei_delta_pct'])} | "
            f"{delta['lite_rework_delta']:.2f} | "
            f"{delta['lite_defect_delta']:.2f} |\n"
        )
    if not payload["pairs"]:
        lines.append("| none | incomplete | needs paired data |  |  |  |  |  |\n")
    return "".join(lines)


def avg(rows: list[dict[str, str]], field: str) -> float:
    values = [to_float(row.get(field, "")) for row in rows if row.get(field, "") != ""]
    return sum(values) / len(values) if values else 0.0


def avg_bool(rows: list[dict[str, str]], field: str) -> float:
    values = [1.0 if normalize_bool(row.get(field, "")) else 0.0 for row in rows]
    return sum(values) / len(values) if values else 0.0


def to_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def normalize_mode(value: str) -> str:
    mode = value.strip().lower()
    if mode == "full":
        return "Full"
    if mode == "lite":
        return "Lite"
    raise SystemExit("mode must be Full or Lite")


def normalize_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "pass", "passed"}:
        return True
    if text in {"0", "false", "no", "n", "fail", "failed", ""}:
        return False
    raise SystemExit(f"cannot parse boolean: {value!r}")


def fmt_float(value: float) -> str:
    return f"{value:.6f}"


def fmt_optional_float(value: float | None) -> str:
    return "" if value is None else fmt_float(float(value))


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_payload(payload: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run and summarize the GCS cache-hit Full/Lite experiment."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_cmd = sub.add_parser("inspect-db", help="Inspect token-audit DB state")
    inspect_cmd.add_argument("--format", choices=["text", "json"], default="text")
    inspect_cmd.set_defaults(func=inspect_db)

    list_cmd = sub.add_parser("list-sessions", help="List recent sessions")
    list_cmd.add_argument("--limit", type=int, default=10)
    list_cmd.add_argument("--format", choices=["text", "json"], default="text")
    list_cmd.set_defaults(func=list_sessions)

    record_cmd = sub.add_parser("record", help="Append one experiment run row")
    record_cmd.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    record_cmd.add_argument("--session-id", required=True)
    record_cmd.add_argument("--run-id", required=True)
    record_cmd.add_argument("--task-pair", required=True)
    record_cmd.add_argument("--mode", required=True)
    record_cmd.add_argument("--date")
    record_cmd.add_argument("--task-type", default="")
    record_cmd.add_argument("--risk", default="")
    record_cmd.add_argument("--audit-score", type=float, required=True)
    record_cmd.add_argument("--validation-passed", required=True)
    record_cmd.add_argument("--rework-turns", type=int, default=0)
    record_cmd.add_argument("--defect-or-reopen-count", type=int, default=0)
    record_cmd.add_argument("--skills-invoked", default="")
    record_cmd.add_argument("--files-touched", type=int)
    record_cmd.add_argument("--notes", default="")
    record_cmd.add_argument("--format", choices=["text", "json"], default="text")
    record_cmd.set_defaults(func=record_run)

    summary_cmd = sub.add_parser("summarize", help="Summarize experiment runs")
    summary_cmd.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    summary_cmd.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    summary_cmd.add_argument("--json-output", type=Path, default=DEFAULT_JSON_REPORT)
    summary_cmd.add_argument("--format", choices=["text", "json"], default="text")
    summary_cmd.set_defaults(func=summarize)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
