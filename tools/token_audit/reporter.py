"""Report generator — produces Markdown/JSON session reports."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from tools.token_audit.parser import SessionSnapshot
from tools.token_audit.bei_engine import BEIScores, BEIEngine
from tools.token_audit.cost_model import CostModel
from tools.token_audit.db import get_session, list_sessions, get_daily_summaries, db_stats


def generate_session_report(
    snapshot: SessionSnapshot,
    bei_scores: Optional[BEIScores] = None,
    cost_model: Optional[CostModel] = None,
    fmt: str = "markdown",
) -> str:
    """Generate a single-session report."""
    if fmt == "json":
        return _session_report_json(snapshot, bei_scores, cost_model)
    return _session_report_markdown(snapshot, bei_scores, cost_model)


def _session_report_markdown(
    snap: SessionSnapshot,
    bei: Optional[BEIScores],
    cm: Optional[CostModel],
) -> str:
    """Generate a Markdown session report."""
    if cm is None:
        cm = CostModel()

    cost_usd = snap.cost_usd_micro / 1_000_000.0
    cache_rate = snap.tokens.cache_hit_rate
    total_tokens = snap.tokens.total_tokens
    total_edits = snap.edit_accept_count + snap.edit_reject_count
    rejection_rate = (
        snap.edit_reject_count / total_edits if total_edits > 0 else 0.0
    )
    commits = snap.commits_count
    cost_per_commit = cost_usd / commits if commits > 0 else float("inf")
    output_per_1M = (
        (snap.lines_added + snap.lines_removed) * 1_000_000.0 / total_tokens
        if total_tokens > 0 else 0.0
    )

    duration = ""
    if snap.started_at and snap.ended_at:
        try:
            s = datetime.fromisoformat(snap.started_at.replace("Z", "+00:00"))
            e = datetime.fromisoformat(snap.ended_at.replace("Z", "+00:00"))
            delta = e - s
            hours = int(delta.total_seconds() // 3600)
            mins = int((delta.total_seconds() % 3600) // 60)
            duration = f"{hours}h{mins}m"
        except (ValueError, TypeError):
            pass

    lines = []
    lines.append("# Session Audit Report\n")
    lines.append(f"**Session**: `{snap.session_id[:20]}...`")
    if duration:
        lines.append(f" | **Duration**: {duration}")
    lines.append(f" | **Date**: {snap.started_at[:19] if snap.started_at else 'unknown'}")
    lines.append(f"\n**Model**: {snap.model_id or 'unknown'}")
    lines.append(f" | **Project**: {snap.project_name}")
    if bei:
        lines.append(f" | **BEI**: {BEIScores.rating(bei.composite)} ({bei.composite:.2f})\n")
    else:
        lines.append("\n")

    # Token & Cost Summary
    lines.append("---\n\n## Token & Cost Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Tokens | {total_tokens:,}")
    lines.append(f"| Input Tokens | {snap.tokens.input_tokens:,}")
    lines.append(f"| Output Tokens | {snap.tokens.output_tokens:,}")
    lines.append(f"| Cache Read Tokens | {snap.tokens.cache_read_tokens:,}")
    lines.append(f"| Cache Creation Tokens | {snap.tokens.cache_creation_tokens:,}")
    lines.append(f"| Cache Hit Rate | {cache_rate:.1%}")
    lines.append(f"| Estimated Cost | {cm.usd_display(snap.cost_usd_micro)}")

    # Output Summary
    lines.append("\n## Output Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Lines Added | {snap.lines_added:,}")
    lines.append(f"| Lines Removed | {snap.lines_removed:,}")
    lines.append(f"| Files Touched | {snap.files_touched}")
    lines.append(f"| Commits | {commits}")
    lines.append(f"| Edits Accepted / Rejected | {snap.edit_accept_count} / {snap.edit_reject_count}")
    lines.append(f"| Tool Calls | {snap.tool_calls_total}")
    lines.append(f"| Subagents Spawned | {snap.subagent_spawns}")

    # Efficiency Metrics
    lines.append("\n## Efficiency Metrics\n")
    lines.append("| Metric | Value | Status |")
    lines.append("|--------|-------|--------|")
    op_status = "Good" if output_per_1M > 200 else "Low"
    lines.append(f"| Output-per-1M-Tokens | {output_per_1M:.0f} LoC | {op_status}")
    cpc_status = "Good" if cost_per_commit <= 0.50 else "High"
    lines.append(f"| Cost-per-Commit | {cm.usd_display_f(cost_per_commit) if cost_per_commit != float('inf') else 'N/A'} | {cpc_status}")
    rej_status = "Good" if rejection_rate <= 0.20 else "High"
    lines.append(f"| Edit Rejection Rate | {rejection_rate:.1%} | {rej_status}")
    cache_status = "Good" if cache_rate >= 0.30 else "Low"
    lines.append(f"| Cache Hit Rate | {cache_rate:.1%} | {cache_status}")

    # BEI Breakdown
    if bei:
        lines.append("\n## BEI Breakdown\n")
        lines.append("| Dimension | Score | Contribution |")
        lines.append("|-----------|-------|-------------|")
        w = {"output": 0.30, "quality": 0.25, "decision": 0.20, "knowledge": 0.10, "efficiency": 0.15}
        lines.append(f"| Output | {bei.output:.2f} | {bei.output * w['output']:.3f}")
        lines.append(f"| Quality | {bei.quality:.2f} | {bei.quality * w['quality']:.3f}")
        lines.append(f"| Decision | {bei.decision:.2f} | {bei.decision * w['decision']:.3f}")
        lines.append(f"| Knowledge | {bei.knowledge:.2f} | {bei.knowledge * w['knowledge']:.3f}")
        lines.append(f"| Efficiency | {bei.efficiency:.2f} | {bei.efficiency * w['efficiency']:.3f}")
        lines.append(f"| **Composite** | **{bei.composite:.2f}** | —")

    # Skills & Memory
    if snap.skills_invoked:
        lines.append("\n## Skills Invoked\n")
        for s in snap.skills_invoked:
            lines.append(f"- {s}")
    if snap.memory_entries:
        lines.append("\n## Memory Activity\n")
        for m in snap.memory_entries[:5]:
            lines.append(f"- ...{m[-100:]}")

    lines.append(f"\n---\n*Generated by GCS Token Audit v1.0.0 at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    return "\n".join(lines)


def _session_report_json(
    snap: SessionSnapshot,
    bei: Optional[BEIScores],
    cm: Optional[CostModel],
) -> str:
    """Generate a JSON session report."""
    if cm is None:
        cm = CostModel()

    data = {
        "session_id": snap.session_id,
        "project": snap.project_name,
        "model": snap.model_id,
        "started_at": snap.started_at,
        "ended_at": snap.ended_at,
        "tokens": {
            "input": snap.tokens.input_tokens,
            "output": snap.tokens.output_tokens,
            "cache_read": snap.tokens.cache_read_tokens,
            "cache_creation": snap.tokens.cache_creation_tokens,
            "total": snap.tokens.total_tokens,
        },
        "cost_usd": round(snap.cost_usd_micro / 1_000_000.0, 4),
        "output": {
            "lines_added": snap.lines_added,
            "lines_removed": snap.lines_removed,
            "files_touched": snap.files_touched,
            "commits": snap.commits_count,
            "edits_accepted": snap.edit_accept_count,
            "edits_rejected": snap.edit_reject_count,
            "tool_calls": snap.tool_calls_total,
            "subagents": snap.subagent_spawns,
        },
        "skills_invoked": snap.skills_invoked,
        "memory_entries": len(snap.memory_entries),
        "bei": None,
    }
    if bei:
        data["bei"] = {
            "output": round(bei.output, 3),
            "quality": round(bei.quality, 3),
            "decision": round(bei.decision, 3),
            "knowledge": round(bei.knowledge, 3),
            "efficiency": round(bei.efficiency, 3),
            "composite": round(bei.composite, 3),
            "rating": BEIScores.rating(bei.composite),
        }
    return json.dumps(data, indent=2, ensure_ascii=False)


def generate_trend_report(
    db_conn: sqlite3.Connection,
    days: int = 7,
    fmt: str = "markdown",
) -> str:
    """Generate a trend report from daily summaries."""
    summaries = get_daily_summaries(db_conn, days)
    if fmt == "json":
        return json.dumps(summaries, indent=2, ensure_ascii=False)
    return _trend_report_markdown(summaries, days)


def _trend_report_markdown(summaries: list[dict], days: int) -> str:
    """Generate a Markdown trend report."""
    lines = []
    lines.append(f"# Token Efficiency Trend ({days}d)\n")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("---\n")
    lines.append("| Date | Sessions | Tokens | Cost | LoC | Commits | Cache Hit | BEI |")
    lines.append("|------|----------|--------|------|-----|---------|-----------|-----|")

    for s in sorted(summaries, key=lambda x: x["date"]):
        cost = s.get("total_cost_usd_micro", 0) / 1_000_000.0
        bei = s.get("avg_bei_composite", 0) or 0
        cache = s.get("avg_cache_hit_rate", 0) or 0
        lines.append(
            f"| {s['date']} | {s['sessions_count']} | "
            f"{s['total_input_tokens'] + s['total_output_tokens']:,} | "
            f"${cost:.2f} | "
            f"{s['lines_added'] + s['lines_removed']:,} | "
            f"{s['commits_count']} | "
            f"{cache:.1%} | "
            f"{bei:.2f}"
        )

    # Summary row
    total_cost = sum(s.get("total_cost_usd_micro", 0) for s in summaries) / 1_000_000.0
    total_sessions = sum(s["sessions_count"] for s in summaries)
    lines.append(f"\n**Total**: {total_sessions} sessions, ${total_cost:.2f} cost")

    # ASCII trend of BEI
    if summaries and len(summaries) >= 3:
        lines.append("\n## BEI Trend\n```")
        bei_vals = [s.get("avg_bei_composite", 0) or 0 for s in sorted(summaries, key=lambda x: x["date"])]
        max_val = max(bei_vals) if bei_vals else 1.0
        for i, v in enumerate(bei_vals):
            bar_len = int(v / max(max_val, 0.01) * 30)
            bar = "█" * bar_len
            lines.append(f"  {v:.2f} {bar}")
        lines.append("```")

    lines.append(f"\n---\n*Generated by GCS Token Audit*")
    return "\n".join(lines)


def generate_weekly_report(db_conn: sqlite3.Connection) -> str:
    """Generate a weekly report."""
    return generate_trend_report(db_conn, days=7)


def generate_monthly_report(db_conn: sqlite3.Connection) -> str:
    """Generate a monthly report."""
    return generate_trend_report(db_conn, days=30)
