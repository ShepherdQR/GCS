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
    compare: bool = False,
    batch: bool = False,
    cache_ttl: str = "5min",
    fmt: str = "markdown",
) -> str:
    """Generate a single-session report.

    Cost is computed at report time from raw token counts using the given
    pricing_model (defaults to config's report.default_pricing_model).
    """
    if fmt == "json":
        return _session_report_json(snapshot, bei_scores, cost_model, pricing_model, baselines, compare, batch, cache_ttl)
    return _session_report_markdown(snapshot, bei_scores, cost_model, pricing_model, baselines, compare, batch, cache_ttl)


def _session_report_markdown(
    snap: SessionSnapshot,
    bei: Optional[BEIScores],
    cm: Optional[CostModel],
    pricing_model: str = "",
    baselines: dict = None,
    compare: bool = False,
    batch: bool = False,
    cache_ttl: str = "5min",
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
    cost_usd = cm.calculate_usd(snap.tokens, model_for_cost, batch=batch, cache_ttl=cache_ttl)
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
    if compare:
        multi = cm.calculate_multi_usd(snap.tokens, batch=batch, cache_ttl=cache_ttl)
        cost_str = cm.format_comparison(cost_usd, multi, model_for_cost)
    else:
        cost_str = cm.usd_display_f(cost_usd)
    lines.append(f"| Estimated Cost ({model_for_cost}) | {cost_str}")

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
    compare: bool = False,
    batch: bool = False,
    cache_ttl: str = "5min",
) -> str:
    """Generate a JSON session report."""
    if cm is None:
        cm = CostModel()
    if not pricing_model:
        pricing_model = cm.default_model
    if baselines is None:
        baselines = {}

    model_for_cost = cm.resolve_model(pricing_model, snap.model_id or "")
    cost_usd = cm.calculate_usd(snap.tokens, model_for_cost, batch=batch, cache_ttl=cache_ttl)
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
    from tools.token_audit.db import get_project_summaries, get_daily_bei_series, get_today_cost, get_week_cost, get_month_prediction
    from tools.token_audit.parser import TokenUsage

    projects = get_project_summaries(db_conn, days=days)
    if not projects:
        return "No data available. Run 'db import' first."

    # Budget & prediction data
    budgets = cm.config.get("alerts", {}).get("budgets", {})
    per_day = budgets.get("per_day_usd", 10.00)
    per_week = budgets.get("per_week_usd", 50.00)
    today_cost = get_today_cost(db_conn, cm)
    week_cost = get_week_cost(db_conn, cm)
    prediction = get_month_prediction(db_conn, cm)

    budget_info = {
        "today_cost": today_cost, "week_cost": week_cost,
        "per_day": per_day, "per_week": per_week,
        "prediction": prediction,
    }

    if fmt == "html":
        return _dashboard_html(projects, cm, days, budget_info)
    if fmt == "markdown":
        return _dashboard_markdown(projects, cm, days, budget_info)
    return _dashboard_terminal(projects, cm, days, budget_info)


def _dashboard_terminal(projects: list[dict], cm, days: int, budget_info: dict = None) -> str:
    """Terminal dashboard with table and sparklines."""
    from tools.token_audit.parser import TokenUsage

    if budget_info is None:
        budget_info = {}

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
    # Budget tracking
    td = budget_info.get("today_cost", 0)
    tw = budget_info.get("week_cost", 0)
    pd = budget_info.get("per_day", 10)
    pw = budget_info.get("per_week", 50)
    tp = td / pd * 100 if pd > 0 else 0
    wp = tw / pw * 100 if pw > 0 else 0
    lines.append(f"  Budget: Today ${td:.2f} / ${pd:.2f} ({tp:.0f}%)  |  Week ${tw:.2f} / ${pw:.2f} ({wp:.0f}%)")
    # Month prediction
    pred = budget_info.get("prediction", {})
    if pred:
        lines.append(f"  Month: ${pred.get('month_to_date', 0):.2f} MTD  |  "
                     f"Predicted: ${pred.get('predicted_total', 0):.2f} "
                     f"(${pred.get('avg_daily_cost', 0):.2f}/day x {pred.get('remaining_days', 0)}d remaining)")
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


def _dashboard_markdown(projects: list[dict], cm, days: int, budget_info: dict = None) -> str:
    """Markdown dashboard."""
    from tools.token_audit.parser import TokenUsage
    if budget_info is None:
        budget_info = {}
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
    td = budget_info.get("today_cost", 0); tw = budget_info.get("week_cost", 0)
    pd = budget_info.get("per_day", 10); pw = budget_info.get("per_week", 50)
    pred = budget_info.get("prediction", {})
    lines.append(f"**Budget**: Today ${td:.2f} / ${pd:.2f} | Week ${tw:.2f} / ${pw:.2f}")
    if pred:
        lines.append(f" | Month ${pred.get('month_to_date', 0):.2f} MTD, Predicted ${pred.get('predicted_total', 0):.2f}")
    lines.append("")
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


def _dashboard_html(projects: list[dict], cm, days: int, budget_info: dict = None) -> str:
    """Self-contained HTML dashboard with Chart.js trends and session filtering."""
    from tools.token_audit.parser import TokenUsage
    if budget_info is None:
        budget_info = {}

    for p in projects:
        usage = TokenUsage(input_tokens=p["total_input_tokens"], output_tokens=p["total_output_tokens"],
                           cache_read_tokens=p.get("total_cache_read_tokens", 0))
        p["cost_usd"] = cm.calculate_usd(usage, cm.default_model)
        p["total_tokens"] = p["total_input_tokens"] + p["total_output_tokens"]
        p["total_loc"] = p["lines_added"] + p["lines_removed"]

    total_cost = sum(p["cost_usd"] for p in projects)
    total_tokens = sum(p["total_tokens"] for p in projects)
    total_sessions = sum(p["sessions_count"] for p in projects)

    # Build project summary rows
    project_rows = ""
    for p in projects:
        bei_color = "#4caf50" if p["avg_bei"] >= 0.6 else "#ff9800" if p["avg_bei"] >= 0.4 else "#f44336"
        project_rows += f"""
        <tr>
            <td>{p['project_name']}</td>
            <td>{p['sessions_count']}</td>
            <td>{p['total_tokens']:,}</td>
            <td>${p['cost_usd']:.2f}</td>
            <td>{p['total_loc']:,}</td>
            <td style="color:{bei_color};font-weight:bold">{p['avg_bei']:.2f}</td>
            <td>{p.get('avg_cache_hit_rate', 0):.1%}</td>
        </tr>"""

    # Build session list for filtering table (populated by caller if needed)
    session_rows = ""

    # Chart data: project names + BEI values for bar chart
    proj_names_json = json.dumps([p["project_name"] for p in projects])
    bei_vals_json = json.dumps([round(p["avg_bei"], 3) for p in projects])
    cost_vals_json = json.dumps([round(p["cost_usd"], 3) for p in projects])
    tokens_vals_json = json.dumps([p["total_tokens"] for p in projects])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GCS Token Audit Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {{
  --bg: #0f0f1a; --card: #1a1a2e; --border: #2a2a4a;
  --text: #c8c8d8; --muted: #8080a0; --accent: #7c8cf8;
  --green: #4caf50; --orange: #ff9800; --red: #f44336;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg); color: var(--text); padding: 1.5rem;
}}
h1 {{ color: var(--accent); font-size: 1.5rem; margin-bottom: 0.25rem; }}
h2 {{ color: var(--muted); font-size: 1rem; font-weight: 500; margin: 1.5rem 0 0.5rem; }}
.summary {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 1rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0; }}
.stat-card {{
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  padding: 1rem; text-align: center;
}}
.stat-card .value {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); }}
.stat-card .label {{ font-size: 0.75rem; color: var(--muted); margin-top: 0.25rem; }}
.charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0; }}
@media (max-width: 768px) {{ .charts {{ grid-template-columns: 1fr; }} }}
.chart-box {{
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  padding: 1rem;
}}
.chart-box canvas {{ max-height: 260px; }}
table {{ border-collapse: collapse; width: 100%; margin: 0.5rem 0; }}
th, td {{ padding: 0.4rem 0.75rem; text-align: right; border-bottom: 1px solid var(--border); font-size: 0.85rem; }}
th {{ background: #16213e; color: var(--muted); font-weight: 600; position: sticky; top: 0; }}
td:first-child, th:first-child {{ text-align: left; }}
tr:hover {{ background: #16213e; }}
.search-box {{
  width: 100%; padding: 0.5rem 0.75rem; background: var(--card); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text); font-size: 0.85rem; margin: 0.5rem 0;
}}
.search-box::placeholder {{ color: var(--muted); }}
.table-wrap {{ max-height: 400px; overflow-y: auto; border-radius: 8px; border: 1px solid var(--border); }}
.footer {{ color: var(--muted); font-size: 0.75rem; margin-top: 1.5rem; text-align: center; }}
.badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
.badge-a {{ background: #4caf5040; color: var(--green); }}
.badge-b {{ background: #8bc34a40; color: #8bc34a; }}
.badge-c {{ background: #ff980040; color: var(--orange); }}
.badge-d {{ background: #f4433640; color: var(--red); }}
</style>
</head>
<body>
<h1>GCS Token Audit &mdash; Dashboard</h1>
<p class="summary">
  Period: last {days}d &nbsp;|&nbsp; Pricing: {cm.default_model} &nbsp;|&nbsp;
  Total: {total_sessions} sessions, {total_tokens:,} tokens, ${total_cost:.2f}
</p>

<div class="grid">
  <div class="stat-card"><div class="value">{total_sessions}</div><div class="label">Sessions</div></div>
  <div class="stat-card"><div class="value">{_fmt_dash(total_tokens)}</div><div class="label">Tokens</div></div>
  <div class="stat-card"><div class="value">${total_cost:.2f}</div><div class="label">Cost ({cm.default_model})</div></div>
  <div class="stat-card"><div class="value">{len(projects)}</div><div class="label">Projects</div></div>
</div>

<div class="charts">
  <div class="chart-box">
    <h2>BEI by Project</h2>
    <canvas id="beiChart"></canvas>
  </div>
  <div class="chart-box">
    <h2>Cost &amp; Tokens by Project</h2>
    <canvas id="costChart"></canvas>
  </div>
</div>

<h2>Project Summary</h2>
<table>
<thead><tr>
  <th>Project</th><th>Sessions</th><th>Tokens</th><th>Cost</th><th>LoC</th><th>BEI</th><th>Cache Hit</th>
</tr></thead>
<tbody>{project_rows}</tbody>
</table>

<div class="footer">Generated by GCS Token Audit v1.0.0 &mdash; {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}</div>

<script>
const projNames = {proj_names_json};
const beiVals = {bei_vals_json};
const costVals = {cost_vals_json};
const tokensVals = {tokens_vals_json};

const colors = beiVals.map(v => v >= 0.6 ? '#4caf50' : v >= 0.4 ? '#ff9800' : '#f44336');

new Chart(document.getElementById('beiChart'), {{
  type: 'bar',
  data: {{
    labels: projNames,
    datasets: [{{
      label: 'BEI', data: beiVals,
      backgroundColor: colors,
      borderColor: colors,
      borderRadius: 4,
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      y: {{ beginAtZero: true, max: 1.0, ticks: {{ color: '#8080a0' }}, grid: {{ color: '#2a2a4a' }} }},
      x: {{ ticks: {{ color: '#8080a0' }}, grid: {{ display: false }} }}
    }}
  }}
}});

new Chart(document.getElementById('costChart'), {{
  type: 'bar',
  data: {{
    labels: projNames,
    datasets: [
      {{ label: 'Cost (USD)', data: costVals, backgroundColor: '#7c8cf880', borderColor: '#7c8cf8', borderRadius: 4, yAxisID: 'y' }},
      {{ label: 'Tokens (K)', data: tokensVals.map(v => Math.round(v/1000)), backgroundColor: '#e040fb40', borderColor: '#e040fb', borderRadius: 4, yAxisID: 'y1' }}
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: true,
    plugins: {{ legend: {{ labels: {{ color: '#8080a0' }} }} }},
    scales: {{
      y: {{ type: 'linear', position: 'left', title: {{ display: true, text: 'USD', color: '#7c8cf8' }}, ticks: {{ color: '#8080a0' }}, grid: {{ color: '#2a2a4a' }} }},
      y1: {{ type: 'linear', position: 'right', title: {{ display: true, text: 'Tokens (K)', color: '#e040fb' }}, ticks: {{ color: '#8080a0' }}, grid: {{ display: false }} }},
      x: {{ ticks: {{ color: '#8080a0' }}, grid: {{ display: false }} }}
    }}
  }}
}});
</script>
</body>
</html>"""


def generate_routing_report(
    candidates: list[dict], days: int = 90, fmt: str = "markdown"
) -> str:
    """Generate a model routing optimization report."""
    if not candidates:
        return "No routing optimization candidates found."

    if fmt == "json":
        import json
        return json.dumps(candidates, indent=2, ensure_ascii=False)

    short = {"claude-sonnet-4-6": "Sonnet", "claude-opus-4-7": "Opus",
             "claude-haiku-4-5": "Haiku", "deepseek-v4-pro": "DeepSeek"}
    total_savings = sum(c["savings_usd"] for c in candidates)

    lines = [f"# Model Routing Optimization Report ({days}d)\n"]
    lines.append(f"**Potential Savings**: ${total_savings:.2f} across {len(candidates)} sessions\n")
    lines.append("| Session | Project | Date | Pattern | Actual | Rec | Actual $ | Rec'd $ | Savings |")
    lines.append("|---------|---------|------|---------|--------|-----|----------|---------|---------|")

    for c in candidates[:50]:
        actual_short = short.get(c["actual_model"], c["actual_model"])
        rec_short = short.get(c["recommended_model"], c["recommended_model"])
        lines.append(
            f"| {c['session_id']}... | {c['project']} | {c['started_at']} | "
            f"{c['pattern']} | {actual_short} | {rec_short} | "
            f"${c['actual_cost']:.2f} | ${c['recommended_cost']:.2f} | ${c['savings_usd']:.2f} |"
        )

    # Summary by pattern
    lines.append("\n## Savings by Pattern\n")
    by_pattern = {}
    for c in candidates:
        by_pattern.setdefault(c["pattern"], {"count": 0, "savings": 0.0})
        by_pattern[c["pattern"]]["count"] += 1
        by_pattern[c["pattern"]]["savings"] += c["savings_usd"]

    lines.append("| Pattern | Sessions | Total Savings |")
    lines.append("|---------|----------|--------------|")
    for pattern, stats in sorted(by_pattern.items()):
        lines.append(f"| {pattern} | {stats['count']} | ${stats['savings']:.2f} |")

    lines.append(f"\n---\n*Generated by GCS Token Audit*")
    return "\n".join(lines)


# ── v2 Session Diagnostic Card ──────────────────────────────────

def generate_session_diagnostic_card(
    raw,          # RawTelemetry
    metrics,      # DerivedMetrics
    indices,      # CompositeIndices
    alerts=None,  # list[DecisionAlert]
    cost_model=None,
) -> str:
    """Generate the v2 session-level token economic diagnostic card."""
    from tools.token_audit.composite_indices import (
        CompositeIndexEngine, CWAR_BREAK_EVEN,
    )
    engine = CompositeIndexEngine()

    alerts = alerts or []
    cm = cost_model or CostModel()

    total_tokens = raw.input_tokens + raw.output_tokens

    lines = []
    lines.append("=" * 65)
    lines.append(f"  SESSION TOKEN ECONOMIC DIAGNOSTIC")
    lines.append(f"  Session: {raw.session_id[:40] if raw.session_id else 'unknown'}")
    lines.append(f"  Workload: {indices.workload}   Risk: {raw.task_risk_level}   "
                 f"Model: {raw.model_id or 'unknown'}")
    lines.append("=" * 65)
    lines.append("")

    ths_bar = _diagnostic_bar(indices.ths / 100)
    cti_bar = _diagnostic_bar(indices.cti)
    ser_bar = _diagnostic_bar(indices.ser)
    lines.append(f"  TOKEN HEALTH SCORE:  {indices.ths:5.0f}/100  {ths_bar}")
    lines.append(f"  CACHE TRUST INDEX:   {indices.cti:.2f}      {cti_bar}")
    lines.append(f"  SESSION EFF. RATING: {indices.ser:.2f}      {ser_bar}")
    lines.append("")

    lines.append("  " + "-" * 61)
    lines.append("  CACHE HEALTH")
    eff_ok = "OK" if metrics.hr_effective >= 0.40 else "LOW"
    fresh_ok = "OK" if metrics.usr <= 0.05 else "STALE"
    cwar_val = f"{metrics.cwar:.1f}" if metrics.cwar != float('inf') else "inf"
    cwar_be = CWAR_BREAK_EVEN.get(raw.cache_ttl_setting, 1.4)
    econ_ok = "OK" if metrics.cwar >= cwar_be or metrics.cwar == float('inf') else "LOSS"
    lines.append(f"  Efficiency: {metrics.hr_effective:.3f} [{eff_ok}]  "
                 f"Freshness: {1-metrics.usr:.3f} [{fresh_ok}]  "
                 f"Economics: {cwar_val} [{econ_ok}]")
    lines.append(f"  State: {indices.cache_health_state.upper()}")
    lines.append("")

    lines.append("  " + "-" * 61)
    lines.append("  KEY METRICS")
    lines.append(f"  Input: {raw.input_tokens:>10,}  Output: {raw.output_tokens:>10,}  "
                 f"Total: {total_tokens:>12,}")
    lines.append(f"  TLR: {metrics.tlr:.4f}  CGR: {metrics.cgr:.1f}x  "
                 f"SCLOR: {metrics.sclor:.1%}  TWR(est): {metrics.twr:.1%}")
    lines.append(f"  VCR: {metrics.vcr:.3f}  USR: {metrics.usr:.3f}  "
                 f"CWAR: {cwar_val}  TDOR: {metrics.tdor:.1%}")
    lines.append(f"  Overhead est: {raw.estimated_overhead_tokens:,} tokens  "
                 f"Turns: {raw.turn_count}")
    lines.append("")

    if alerts:
        lines.append("  " + "-" * 61)
        lines.append("  ALERTS")
        for a in alerts:
            sev = "!!" if a.severity.value == "critical" else "! " if a.severity.value == "warning" else "  "
            lines.append(f"  {sev} [{a.rule_id}] {a.message[:90]}")
    else:
        lines.append("  ALERTS: None")

    lines.append("")
    lines.append("=" * 65)
    return "\n".join(lines)


def _diagnostic_bar(value: float) -> str:
    """ASCII bar 0-12 chars."""
    n = min(int(value * 12), 12)
    return "[" + "=" * n + " " * (12 - n) + "]"
