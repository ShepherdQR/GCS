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


def generate_efficiency_analysis(
    output_per_1M: float, cache_hit_rate: float,
    baselines: dict = None
) -> str:
    """Generate a one-sentence efficiency analysis comparing to calibrated baselines.

    Args:
        output_per_1M: LoC per 1M tokens for this session
        cache_hit_rate: cache hit rate (0.0-1.0)
        baselines: dict with metric -> {p25, p50, p75, sample_size} from calibrate_baselines()

    Returns a Chinese one-sentence analysis suitable for reports and skill output.
    """
    if not baselines:
        baselines = {}

    parts = []

    # Output efficiency
    output_bl = baselines.get("output_per_1M_tokens")
    if output_bl:
        p50 = output_bl["p50"]
        p75 = output_bl["p75"]
        if output_per_1M >= p75:
            parts.append(f"产出效率位于历史前25%（{output_per_1M:.0f} LoC/1M tokens, P75={p75:.0f}）")
        elif output_per_1M >= p50:
            parts.append(f"产出效率高于历史中位数（{output_per_1M:.0f} LoC/1M tokens, P50={p50:.0f}）")
        else:
            parts.append(f"产出效率低于历史中位数（{output_per_1M:.0f} LoC/1M tokens, P50={p50:.0f}）")
    else:
        parts.append(f"产出效率 {output_per_1M:.0f} LoC/1M tokens")

    # Cache efficiency
    cache_bl = baselines.get("cache_hit_rate")
    if cache_bl:
        p50 = cache_bl["p50"]
        p75 = cache_bl["p75"]
        cache_pct = cache_hit_rate * 100
        if cache_hit_rate >= p75:
            parts.append(f"缓存命中率位于历史前25%（{cache_pct:.0f}%, P75={p75*100:.0f}%）")
        elif cache_hit_rate >= p50:
            parts.append(f"缓存命中率高于历史中位数（{cache_pct:.0f}%, P50={p50*100:.0f}%）")
        else:
            parts.append(f"缓存命中率低于历史中位数（{cache_pct:.0f}%, P50={p50*100:.0f}%）")
    else:
        parts.append(f"缓存命中率 {cache_hit_rate:.1%}")

    # Compose
    if not parts:
        return "暂无基准数据可供比较。"

    prefix = "本会话"
    if output_bl and cache_bl:
        if output_per_1M >= output_bl["p75"] and cache_hit_rate >= cache_bl["p75"]:
            prefix += "表现优异："
        elif output_per_1M >= output_bl["p50"] and cache_hit_rate >= cache_bl["p50"]:
            prefix += "表现良好："
        elif output_per_1M < output_bl["p50"] and cache_hit_rate < cache_bl["p50"]:
            prefix += "有改进空间："
        else:
            prefix += "表现一般："

    return prefix + "，".join(parts) + "。"


def generate_session_report(
    snapshot: SessionSnapshot,
    bei_scores: Optional[BEIScores] = None,
    cost_model: Optional[CostModel] = None,
    pricing_model: str = "",
    baselines: dict = None,
    fmt: str = "markdown",
) -> str:
    """Generate a single-session report.

    Cost is computed at report time from raw token counts using the given
    pricing_model (defaults to config's report.default_pricing_model).
    """
    if fmt == "json":
        return _session_report_json(snapshot, bei_scores, cost_model, pricing_model, baselines)
    return _session_report_markdown(snapshot, bei_scores, cost_model, pricing_model, baselines)


def _session_report_markdown(
    snap: SessionSnapshot,
    bei: Optional[BEIScores],
    cm: Optional[CostModel],
    pricing_model: str = "",
    baselines: dict = None,
) -> str:
    """Generate a Markdown session report."""
    if cm is None:
        cm = CostModel()
    if not pricing_model:
        pricing_model = cm.default_model
    if baselines is None:
        baselines = {}

    # Compute cost at report time from raw token counts
    model_for_cost = cm.resolve_model(pricing_model, snap.model_id or "")
    cost_usd = cm.calculate_usd(snap.tokens, model_for_cost)
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

    # Efficiency analysis (one-liner vs calibrated baselines)
    analysis = generate_efficiency_analysis(output_per_1M, cache_rate, baselines)
    lines.append(f"> {analysis}\n")

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
    lines.append(f"| Estimated Cost ({model_for_cost}) | {cm.usd_display_f(cost_usd)}")

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
    lines.append("| Metric | Value | Status | vs Baseline (P50) |")
    lines.append("|--------|-------|--------|-------------------|")

    # Output-per-1M with baseline
    op_bl = baselines.get("output_per_1M_tokens", {})
    op_p50 = op_bl.get("p50", 200)
    op_status = "Top 25%" if output_per_1M >= op_bl.get("p75", 999999) else ("Above median" if output_per_1M >= op_p50 else "Below median")
    lines.append(f"| Output-per-1M-Tokens | {output_per_1M:.0f} LoC | {op_status} | P50={op_p50:.0f} |")

    # Cost-per-commit with baseline
    cpc_bl = baselines.get("cost_per_commit", {})
    cpc_p50 = cpc_bl.get("p50", 0.50)
    cpc_status = "Good" if cost_per_commit <= cpc_p50 else "High"
    cpc_display = cm.usd_display_f(cost_per_commit) if cost_per_commit != float('inf') else 'N/A'
    lines.append(f"| Cost-per-Commit | {cpc_display} | {cpc_status} | P50=${cpc_p50:.2f} |")

    # Edit rejection
    rej_status = "Good" if rejection_rate <= 0.20 else "High"
    lines.append(f"| Edit Rejection Rate | {rejection_rate:.1%} | {rej_status} | — |")

    # Cache hit rate with baseline
    cache_bl = baselines.get("cache_hit_rate", {})
    cache_p50 = cache_bl.get("p50", 0.30)
    cache_status = "Top 25%" if cache_rate >= cache_bl.get("p75", 0.99) else ("Above median" if cache_rate >= cache_p50 else "Below median")
    lines.append(f"| Cache Hit Rate | {cache_rate:.1%} | {cache_status} | P50={cache_p50:.1%} |")

    # Commit Quality
    commit_signals = getattr(snap, 'commit_signals', None) or {}
    if commit_signals.get("total_commits", 0) > 0:
        lines.append("\n## Commit Quality\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Commits | {commit_signals.get('total_commits', 0)}")
        lines.append(f"| Conventional Commits | {commit_signals.get('conventional_commits', 0)}")
        lines.append(f"| Semantic Signals | {commit_signals.get('semantic_signals', 0)}")
        lines.append(f"| Architecture Signals | {commit_signals.get('architecture_signals', 0)}")

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

    # Chapters
    chapters = getattr(snap, 'chapters', None) or []
    if chapters:
        lines.append("\n## Chapter Breakdown\n")
        lines.append("| # | Title | Start Turn |")
        lines.append("|---|-------|-----------|")
        for ch in chapters:
            lines.append(f"| {ch.get('chapter_index', '?')} | {ch.get('title', '?')} | T+{ch.get('start_turn', 0)} |")
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
    pricing_model: str = "",
    baselines: dict = None,
) -> str:
    """Generate a JSON session report."""
    if cm is None:
        cm = CostModel()
    if not pricing_model:
        pricing_model = cm.default_model
    if baselines is None:
        baselines = {}

    model_for_cost = cm.resolve_model(pricing_model, snap.model_id or "")
    cost_usd = cm.calculate_usd(snap.tokens, model_for_cost)
    output_per_1M = (
        (snap.lines_added + snap.lines_removed) * 1_000_000.0 / snap.tokens.total_tokens
        if snap.tokens.total_tokens > 0 else 0.0
    )
    analysis = generate_efficiency_analysis(output_per_1M, snap.tokens.cache_hit_rate, baselines)

    data = {
        "session_id": snap.session_id,
        "project": snap.project_name,
        "model": snap.model_id,
        "started_at": snap.started_at,
        "ended_at": snap.ended_at,
        "analysis": analysis,
        "baselines": {k: {"p50": v["p50"], "p75": v["p75"]} for k, v in baselines.items()},
        "tokens": {
            "input": snap.tokens.input_tokens,
            "output": snap.tokens.output_tokens,
            "cache_read": snap.tokens.cache_read_tokens,
            "cache_creation": snap.tokens.cache_creation_tokens,
            "total": snap.tokens.total_tokens,
        },
        "cost_usd": round(cost_usd, 4),
        "cost_pricing_model": model_for_cost,
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
    pricing_model: str = "",
    fmt: str = "markdown",
) -> str:
    """Generate a trend report from daily summaries.

    Cost is computed at report time from raw token counts.
    """
    summaries = get_daily_summaries(db_conn, days)
    if fmt == "json":
        return json.dumps(summaries, indent=2, ensure_ascii=False)
    return _trend_report_markdown(summaries, days, pricing_model)


def _trend_report_markdown(summaries: list[dict], days: int, pricing_model: str = "") -> str:
    """Generate a Markdown trend report."""
    cm = CostModel()
    if not pricing_model:
        pricing_model = cm.default_model
    model_for_cost = cm.resolve_model(pricing_model)

    lines = []
    lines.append(f"# Token Efficiency Trend ({days}d)\n")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Pricing model: **{model_for_cost}**\n")
    lines.append("---\n")
    lines.append("| Date | Sessions | Tokens | Cost | LoC | Commits | Cache Hit | BEI |")
    lines.append("|------|----------|--------|------|-----|---------|-----------|-----|")

    for s in sorted(summaries, key=lambda x: x["date"]):
        # Compute cost from raw tokens
        from tools.token_audit.parser import TokenUsage
        usage = TokenUsage(
            input_tokens=s.get("total_input_tokens", 0),
            output_tokens=s.get("total_output_tokens", 0),
        )
        cost = cm.calculate_usd(usage, model_for_cost)
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

    # Summary row — compute total cost from raw tokens
    total_input = sum(s.get("total_input_tokens", 0) for s in summaries)
    total_output = sum(s.get("total_output_tokens", 0) for s in summaries)
    total_usage = TokenUsage(input_tokens=total_input, output_tokens=total_output)
    total_cost = cm.calculate_usd(total_usage, model_for_cost)
    total_sessions = sum(s["sessions_count"] for s in summaries)
    total_tokens = total_input + total_output
    lines.append(
        f"\n**Total**: {total_sessions} sessions, "
        f"{total_tokens:,} tokens, "
        f"${total_cost:.2f} cost ({model_for_cost})"
    )

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


def generate_weekly_report(db_conn: sqlite3.Connection, pricing_model: str = "") -> str:
    """Generate a weekly report."""
    return generate_trend_report(db_conn, days=7, pricing_model=pricing_model)


def generate_monthly_report(db_conn: sqlite3.Connection, pricing_model: str = "") -> str:
    """Generate a monthly report."""
    return generate_trend_report(db_conn, days=30, pricing_model=pricing_model)


def generate_dashboard(
    db_conn: sqlite3.Connection, cm, days: int = 30, fmt: str = "terminal"
) -> str:
    """Generate a cross-project dashboard.

    Args:
        db_conn: database connection
        cm: CostModel instance
        days: aggregation window
        fmt: terminal, html, or markdown
    """
    from tools.token_audit.db import get_project_summaries, get_daily_bei_series
    from tools.token_audit.parser import TokenUsage

    projects = get_project_summaries(db_conn, days=days)
    if not projects:
        return "No data available. Run 'db import' first."

    if fmt == "html":
        return _dashboard_html(projects, cm, days)
    if fmt == "markdown":
        return _dashboard_markdown(projects, cm, days)
    return _dashboard_terminal(projects, cm, days)


def _dashboard_terminal(projects: list[dict], cm, days: int) -> str:
    """Terminal dashboard with table and sparklines."""
    from tools.token_audit.parser import TokenUsage

    # Compute per-project cost
    for p in projects:
        usage = TokenUsage(
            input_tokens=p["total_input_tokens"],
            output_tokens=p["total_output_tokens"],
            cache_read_tokens=p.get("total_cache_read_tokens", 0),
        )
        p["cost_usd"] = cm.calculate_usd(usage, cm.default_model)
        p["total_tokens"] = p["total_input_tokens"] + p["total_output_tokens"]
        p["total_loc"] = p["lines_added"] + p["lines_removed"]
        p["cache_rate"] = p.get("avg_cache_hit_rate", 0) or 0

    # Totals
    total_cost = sum(p["cost_usd"] for p in projects)
    total_tokens = sum(p["total_tokens"] for p in projects)
    total_sessions = sum(p["sessions_count"] for p in projects)
    total_loc = sum(p["total_loc"] for p in projects)
    avg_bei = sum(p["avg_bei"] for p in projects) / max(len(projects), 1)

    # BEI rating symbols (ASCII-safe)
    def bei_bar(val):
        if val >= 0.80: return "[A]"
        if val >= 0.60: return "[B]"
        if val >= 0.40: return "[C]"
        if val >= 0.20: return "[D]"
        return "[E]"

    lines = []
    lines.append("=" * 78)
    lines.append(f"  GCS Token Audit - Cross-Project Dashboard    {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("=" * 78)
    lines.append(f"  Period: last {days}d    Cost: ${total_cost:.2f}    Tokens: {total_tokens:,}    Sessions: {total_sessions}")
    lines.append("-" * 78)
    header = f"  {'Project':<12} {'Sess':>4} {'Tokens':>10} {'Cost':>8} {'LoC':>8} {'BEI':>6} {'Cache':>6}"
    lines.append(header)
    lines.append("  " + "-" * 74)

    for p in projects:
        bei_val = p["avg_bei"]
        name = p["project_name"][:12]
        tokens_str = f"{p['total_tokens']/1000:.0f}K" if p["total_tokens"] < 1e6 else f"{p['total_tokens']/1e6:.1f}M"
        loc_str = f"{p['total_loc']/1000:.1f}K" if p["total_loc"] >= 1000 else str(p["total_loc"])
        line = (
            f"  {name:<12} {p['sessions_count']:>4} {tokens_str:>10} "
            f"${p['cost_usd']:>7.2f} {loc_str:>8} "
            f"{bei_bar(bei_val)} {bei_val:.2f} {p['cache_rate']:>5.0%}"
        )
        lines.append(line)

    lines.append("  " + "-" * 74)
    lines.append(f"  {'TOTALS':<12} {total_sessions:>4} {_fmt_dash(total_tokens):>10} ${total_cost:>7.2f} {_fmt_dash(total_loc):>8} {bei_bar(avg_bei)} {avg_bei:.2f}")
    lines.append("=" * 78)
    lines.append(f"  Pricing: {cm.default_model} | Generated by GCS Token Audit")
    return "\n".join(lines)


def _fmt_dash(n: int) -> str:
    if n >= 1_000_000: return f"{n/1e6:.1f}M"
    if n >= 1_000: return f"{n/1e3:.0f}K"
    return str(n)


def _dashboard_markdown(projects: list[dict], cm, days: int) -> str:
    """Markdown dashboard."""
    from tools.token_audit.parser import TokenUsage
    for p in projects:
        usage = TokenUsage(input_tokens=p["total_input_tokens"], output_tokens=p["total_output_tokens"],
                           cache_read_tokens=p.get("total_cache_read_tokens", 0))
        p["cost_usd"] = cm.calculate_usd(usage, cm.default_model)
        p["total_tokens"] = p["total_input_tokens"] + p["total_output_tokens"]
        p["total_loc"] = p["lines_added"] + p["lines_removed"]

    total_cost = sum(p["cost_usd"] for p in projects)
    total_tokens = sum(p["total_tokens"] for p in projects)

    lines = [f"# Cross-Project Dashboard ({days}d)\n"]
    lines.append(f"**Pricing**: {cm.default_model} | **Total**: ${total_cost:.2f}, {total_tokens:,} tokens\n")
    lines.append("| Project | Sessions | Tokens | Cost | LoC | BEI | Cache |")
    lines.append("|---------|----------|--------|------|-----|-----|-------|")
    for p in projects:
        lines.append(
            f"| {p['project_name']} | {p['sessions_count']} | "
            f"{p['total_tokens']:,} | ${p['cost_usd']:.2f} | "
            f"{p['total_loc']:,} | {p['avg_bei']:.2f} | {p.get('avg_cache_hit_rate', 0):.1%} |"
        )
    lines.append(f"\n*Generated by GCS Token Audit*")
    return "\n".join(lines)


def _dashboard_html(projects: list[dict], cm, days: int) -> str:
    """Self-contained HTML dashboard."""
    from tools.token_audit.parser import TokenUsage
    for p in projects:
        usage = TokenUsage(input_tokens=p["total_input_tokens"], output_tokens=p["total_output_tokens"],
                           cache_read_tokens=p.get("total_cache_read_tokens", 0))
        p["cost_usd"] = cm.calculate_usd(usage, cm.default_model)
        p["total_tokens"] = p["total_input_tokens"] + p["total_output_tokens"]
        p["total_loc"] = p["lines_added"] + p["lines_removed"]

    total_cost = sum(p["cost_usd"] for p in projects)
    total_tokens = sum(p["total_tokens"] for p in projects)
    total_sessions = sum(p["sessions_count"] for p in projects)

    rows = ""
    for p in projects:
        bei_color = "#4caf50" if p["avg_bei"] >= 0.6 else "#ff9800" if p["avg_bei"] >= 0.4 else "#f44336"
        rows += f"""
        <tr>
            <td>{p['project_name']}</td>
            <td>{p['sessions_count']}</td>
            <td>{p['total_tokens']:,}</td>
            <td>${p['cost_usd']:.2f}</td>
            <td>{p['total_loc']:,}</td>
            <td style="color:{bei_color};font-weight:bold">{p['avg_bei']:.2f}</td>
            <td>{p.get('avg_cache_hit_rate', 0):.1%}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GCS Token Audit Dashboard</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #1a1a2e; color: #e0e0e0; padding: 2rem; }}
h1 {{ color: #7c8cf8; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th, td {{ padding: 0.5rem 1rem; text-align: right; border-bottom: 1px solid #333; }}
th {{ background: #16213e; color: #a0a0c0; font-weight: 600; }}
td:first-child, th:first-child {{ text-align: left; }}
tr:hover {{ background: #16213e; }}
.summary {{ color: #a0a0c0; margin: 1rem 0; }}
</style>
</head>
<body>
<h1>GCS Token Audit — Cross-Project Dashboard</h1>
<p class="summary">Period: last {days}d | Pricing: {cm.default_model} |
   Total sessions: {total_sessions} | Total tokens: {total_tokens:,} | Total cost: ${total_cost:.2f}</p>
<table>
<thead><tr>
    <th>Project</th><th>Sessions</th><th>Tokens</th><th>Cost</th><th>LoC</th><th>BEI</th><th>Cache Hit</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
<p class="summary">Generated by GCS Token Audit v1.0.0</p>
</body>
</html>"""
