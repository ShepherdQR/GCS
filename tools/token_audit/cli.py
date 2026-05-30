"""CLI interface for the GCS Token Audit system."""

import os
import sys
import time
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import click

from tools.token_audit.db import (
    init_db, insert_session, update_session, get_session, list_sessions,
    get_latest_session, session_exists, close_session, db_stats,
    upsert_daily_summary, get_daily_summaries, insert_chapter, get_chapters,
    get_project_summaries, get_daily_bei_series, calibrate_baselines,
    insert_turn, insert_tool_call, insert_edit,
)
from tools.token_audit.parser import (
    IncrementalJSONLParser, SessionSnapshot, TokenUsage, ToolCall,
)
from tools.token_audit.cost_model import CostModel
from tools.token_audit.git_linker import GitLinker
from tools.token_audit.bei_engine import BEIEngine, BEIScores
from tools.token_audit.alerts import AlertEngine, Alert
from tools.token_audit.tracker import SessionTracker
from tools.token_audit.reporter import (
    generate_session_report, generate_trend_report,
    generate_weekly_report, generate_monthly_report,
)


@click.group()
@click.version_option(version="1.0.0")
def main():
    """GCS Token Audit — AI session benefit tracking and analysis."""


# ── watch ────────────────────────────────────────────────────

@main.command()
@click.option("--interval", "-i", default=5, help="Refresh interval in seconds")
@click.option("--format", "-f", "output_fmt", default="text",
              type=click.Choice(["text", "json"]))
@click.option("--no-persist", is_flag=True, help="Do not write to database")
@click.option("--session", "-s", "session_id", default=None, help="Session ID to watch")
def watch(interval, output_fmt, no_persist, session_id):
    """Monitor an active Claude Code session in real time."""
    db_conn = None if no_persist else init_db()
    cost_model = CostModel()
    alert_engine = AlertEngine(db_conn=db_conn, cost_model=cost_model)
    tracker = SessionTracker(db_conn=db_conn, alert_engine=alert_engine, cost_model=cost_model)

    # Find or specify session
    jsonl_path = None
    if session_id:
        # Look up by session ID in DB
        if db_conn:
            sess = get_session(db_conn, session_id)
            if sess and sess.get("jsonl_path"):
                jsonl_path = sess["jsonl_path"]
    if not jsonl_path:
        jsonl_path = tracker.find_active_session()

    if not jsonl_path:
        click.echo("No active Claude Code session found.", err=True)
        click.echo("Start a session or specify --session.", err=True)
        return

    click.echo(f"Watching: {jsonl_path}")
    snap = tracker.start_tracking(jsonl_path)
    click.echo(f"Session: {snap.session_id[:20]}... | Model: {snap.model_id or 'detecting...'}")

    bei_engine = BEIEngine(db_conn=db_conn, cost_model=cost_model)

    try:
        while tracker.is_active():
            time.sleep(interval)
            snap = tracker.tick()

            if snap is None:
                continue

            if output_fmt == "json":
                click.echo(json.dumps(_snap_to_summary(snap)))
            else:
                _render_status_line(snap, bei_engine)

            # Check alerts
            alerts = alert_engine.evaluate(snap, cost_ticks=tracker._cost_ticks)
            if alerts and db_conn:
                tracker.flush_alerts(alerts)
                for a in alerts:
                    icon = "⚠" if a.severity.value == "warning" else "🚨"
                    click.echo(f"\n  {icon} {a.message}")

    except KeyboardInterrupt:
        click.echo("\nStopping...")
    finally:
        snap = tracker.stop_tracking()
        if db_conn and not no_persist:
            tracker.flush_to_db()
            if snap.started_at:
                date_str = snap.started_at[:10]
                upsert_daily_summary(db_conn, date_str)
        click.echo(f"\nSession ended. Tokens: {snap.tokens.total_tokens:,} | Cost: {cost_model.usd_display(snap.cost_usd_micro)}")


def _snap_to_summary(snap: SessionSnapshot) -> dict:
    return {
        "session_id": snap.session_id[:20],
        "turns": snap.turn_count,
        "tokens": snap.tokens.total_tokens,
        "input_tokens": snap.tokens.input_tokens,
        "output_tokens": snap.tokens.output_tokens,
        "cache_hit_rate": round(snap.tokens.cache_hit_rate, 3),
        "cost_usd": round(snap.cost_usd_micro / 1_000_000.0, 4),
        "tool_calls": snap.tool_calls_total,
        "subagents": snap.subagent_spawns,
        "edits": f"{snap.edit_accept_count}A/{snap.edit_reject_count}R",
    }


def _render_status_line(snap: SessionSnapshot, bei_engine: BEIEngine = None):
    """Render a single-line status display."""
    tokens_str = f"In:{_fmt_tokens(snap.tokens.input_tokens)} Out:{_fmt_tokens(snap.tokens.output_tokens)}"
    cache_str = f"Cache:{snap.tokens.cache_hit_rate:.0%}"
    cost_str = f"${snap.cost_usd_micro / 1_000_000:.2f}"
    edits_str = f"Edits:{snap.edit_accept_count}A/{snap.edit_reject_count}R"

    bei_str = ""
    if bei_engine and snap.turn_count >= 3:
        try:
            scores = bei_engine.calculate(snap)
            bei_str = f"BEI:{scores.composite:.2f}"
        except Exception:
            pass

    line = (
        f"\rGCS Session  T:{snap.turn_count}  {tokens_str}  "
        f"{cache_str}  {cost_str}  {edits_str}  {bei_str}"
    )
    # Pad to clear previous line
    term_width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 120
    line = line.ljust(term_width)
    sys.stdout.write(line)
    sys.stdout.flush()


def _fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)


# ── report ───────────────────────────────────────────────────

@main.command()
@click.option("--session", "-s", "session_id", default=None,
              help="Session ID (default: latest)")
@click.option("--from", "-f", "from_date", default=None, help="Start date (YYYY-MM-DD)")
@click.option("--to", "-t", "to_date", default=None, help="End date (YYYY-MM-DD)")
@click.option("--format", "-fmt", "output_fmt", default="markdown",
              type=click.Choice(["markdown", "json"]))
@click.option("--output", "-o", "output_path", default=None, help="Output file path")
@click.option("--pricing", "-p", "pricing_model", default="",
              help="Pricing model: deepseek (default), anthropic, or specific model name")
@click.option("--baseline/--no-baseline", default=True,
              help="Show efficiency analysis vs calibrated baselines (default: on)")
@click.option("--compare/--no-compare", default=False,
              help="Show multi-model cost comparison (DeepSeek + Sonnet + Opus)")
@click.option("--batch/--no-batch", default=False,
              help="Use Anthropic Batch API pricing (50% off input/output)")
@click.option("--cache-ttl", default="5min", type=click.Choice(["5min", "1hour"]),
              help="Cache TTL for cache write pricing (default: 5min)")
@click.option("--this-week", is_flag=True, help="Generate weekly report")
@click.option("--this-month", is_flag=True, help="Generate monthly report")
def report(session_id, from_date, to_date, output_fmt, output_path, pricing_model, baseline, compare, batch, cache_ttl, this_week, this_month):
    """Generate session or time-range reports.

    Cost is computed at report time from raw token counts.
    Default pricing: deepseek-v4-pro (configurable in config.yaml).
    Includes one-sentence efficiency analysis vs calibrated baselines.
    """
    db_conn = init_db()
    cost_model = CostModel()
    bei_engine = BEIEngine(db_conn=db_conn, cost_model=cost_model)
    git_linker = GitLinker()

    if not pricing_model:
        pricing_model = cost_model.default_model

    # Compute baselines for efficiency analysis
    baselines = {}
    if baseline:
        try:
            baselines = calibrate_baselines(db_conn, window_days=30)
            if baselines:
                bei_engine.load_baselines(baselines)
        except Exception:
            pass  # Best-effort — report still works without baselines

    content = ""

    if this_week:
        content = generate_weekly_report(db_conn, pricing_model=pricing_model)
    elif this_month:
        content = generate_monthly_report(db_conn, pricing_model=pricing_model)
    elif from_date and to_date:
        days = (datetime.strptime(to_date, "%Y-%m-%d") - datetime.strptime(from_date, "%Y-%m-%d")).days
        content = generate_trend_report(db_conn, days=max(days, 1), pricing_model=pricing_model)
    elif session_id:
        content = _report_single_session(db_conn, session_id, bei_engine, git_linker, cost_model, pricing_model, baselines, compare, batch, cache_ttl, output_fmt)
    else:
        # Latest session
        sess = get_latest_session(db_conn)
        if not sess:
            click.echo("No sessions in database. Run 'db import' first or specify --session.")
            return
        content = _report_single_session(db_conn, sess["id"], bei_engine, git_linker, cost_model, pricing_model, baselines, compare, batch, cache_ttl, output_fmt)

    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
        click.echo(f"Report saved to {output_path}")
    else:
        click.echo(content)


def _report_single_session(db_conn, session_id, bei_engine, git_linker, cost_model, pricing_model, baselines, compare, batch, cache_ttl, fmt):
    """Generate a single-session report. Cost is computed at report time."""
    sess = get_session(db_conn, session_id)
    if not sess:
        return f"Session {session_id} not found."

    # Reconstruct snapshot from DB — raw token counts only, no pre-computed cost
    snap = SessionSnapshot(
        session_id=sess["id"],
        project_name=sess["project_name"],
        started_at=sess["started_at"],
    )
    snap.ended_at = sess.get("ended_at", "")
    snap.model_id = sess.get("model_id", "")
    snap.tokens = TokenUsage(
        input_tokens=sess.get("total_input_tokens", 0),
        output_tokens=sess.get("total_output_tokens", 0),
        cache_read_tokens=sess.get("total_cache_read_tokens", 0),
        cache_creation_tokens=sess.get("total_cache_creation_tokens", 0),
    )
    snap.lines_added = sess.get("lines_added", 0)
    snap.lines_removed = sess.get("lines_removed", 0)
    snap.files_touched = sess.get("files_touched", 0)
    snap.commits_count = sess.get("commits_count", 0)
    try:
        snap.commit_signals = json.loads(sess.get("commit_signals", "{}"))
    except (json.JSONDecodeError, TypeError):
        snap.commit_signals = {}
    snap.edit_accept_count = sess.get("edit_accept_count", 0)
    snap.edit_reject_count = sess.get("edit_reject_count", 0)
    snap.tool_calls_total = sess.get("tool_calls_total", 0)
    snap.subagent_spawns = sess.get("subagent_spawns", 0)
    snap.chapters = get_chapters(db_conn, session_id)
    try:
        snap.skills_invoked = json.loads(sess.get("skills_invoked", "[]"))
        snap.memory_entries = json.loads(sess.get("memory_entries", "[]"))
        snap.docs_touched = json.loads(sess.get("docs_touched", "[]"))
    except (json.JSONDecodeError, TypeError):
        pass

    # Enrich with git data if available
    if snap.started_at:
        try:
            s_dt = datetime.fromisoformat(snap.started_at.replace("Z", "+00:00"))
            e_dt = datetime.fromisoformat(
                (snap.ended_at or snap.started_at).replace("Z", "+00:00")
            )
            diff = git_linker.get_session_diff(s_dt, e_dt)
            if diff["lines_added"] > 0 or diff["lines_removed"] > 0:
                snap.lines_added = max(snap.lines_added, diff["lines_added"])
                snap.lines_removed = max(snap.lines_removed, diff["lines_removed"])
                snap.files_touched = max(snap.files_touched, diff["files_changed"])

            commits = git_linker.get_commits_in_window(s_dt, e_dt)
            if commits:
                snap.commits_count = max(snap.commits_count, len(commits))
        except (ValueError, TypeError):
            pass

    # Calculate BEI
    bei = bei_engine.calculate(snap, snap.project_name)

    return generate_session_report(snap, bei, cost_model, pricing_model, baselines, compare, batch, cache_ttl, fmt=fmt)


# ── trend ────────────────────────────────────────────────────

@main.command()
@click.option("--days", "-d", default=7, help="Number of days to analyze")
@click.option("--metric", "-m", default="bei_composite",
              type=click.Choice(["bei_composite", "cost_per_commit", "cache_hit_rate"]))
@click.option("--pricing", "-p", "pricing_model", default="",
              help="Pricing model: deepseek (default), anthropic, or specific model name")
@click.option("--format", "-f", "output_fmt", default="markdown",
              type=click.Choice(["markdown", "json"]))
def trend(days, metric, pricing_model, output_fmt):
    """Show historical efficiency trends."""
    db_conn = init_db()
    content = generate_trend_report(db_conn, days=days, pricing_model=pricing_model, fmt=output_fmt)
    click.echo(content)


# ── config ───────────────────────────────────────────────────

@main.group()
def config():
    """Manage audit configuration."""
    pass


@config.command("show")
def config_show():
    """Show current configuration."""
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        content = config_path.read_text(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
        click.echo(content)
    else:
        click.echo("No config.yaml found.")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a configuration value (e.g. 'bei.weights.output 0.35')."""
    import yaml
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        click.echo("config.yaml not found.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # Parse dotted key path
    parts = key.split(".")
    target = cfg
    for part in parts[:-1]:
        if part not in target:
            target[part] = {}
        target = target[part]

    # Try to coerce value type
    try:
        if "." in value:
            coerced = float(value)
        else:
            coerced = int(value)
    except ValueError:
        coerced = value

    target[parts[-1]] = coerced

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, default_flow_style=False, allow_unicode=True)

    click.echo(f"Set {key} = {coerced}")


# ── db ───────────────────────────────────────────────────────

@main.group()
def db():
    """Database maintenance commands."""
    pass


@db.command("import")
@click.option("--all", "-a", "import_all", is_flag=True, help="Import all historical sessions")
@click.option("--since", "-s", default=None, help="Import sessions since date (YYYY-MM-DD)")
@click.option("--project", "-p", default=None,
              help="Filter by project name (comma-separated for multiple, e.g. 'GCS-A,s009')")
@click.option("--all-projects", is_flag=True, help="Import from all discovered projects")
@click.option("--force", is_flag=True, help="Re-import sessions already in the database")
def db_import(import_all, since, project, all_projects, force):
    """Import session data from JSONL transcripts into the database."""
    db_conn = init_db()
    projects_dir = Path.home() / ".claude" / "projects"

    if not projects_dir.exists():
        click.echo("No Claude Code projects directory found.", err=True)
        return

    # Resolve project filters
    project_filter = None
    if not all_projects and project:
        project_filter = set(p.strip() for p in project.split(",") if p.strip())

    imported = 0
    skipped = 0
    updated = 0

    for proj_dir in projects_dir.iterdir():
        if not proj_dir.is_dir():
            continue
        proj_name = proj_dir.name.replace("C--Codes-AI-", "").replace("C--Users-QR-Documents-", "")

        if project_filter and not any(p in proj_name for p in project_filter):
            continue

        for jsonl_file in proj_dir.glob("*.jsonl"):
            # Check if already imported
            parser = IncrementalJSONLParser(str(jsonl_file))
            records = parser.read_new_records()
            if not records:
                continue

            sid = IncrementalJSONLParser.get_session_id(records)
            if not sid:
                continue

            if session_exists(db_conn, sid):
                if force:
                    # Delete old data before re-import
                    db_conn.execute("DELETE FROM edits WHERE session_id = ?", (sid,))
                    db_conn.execute("DELETE FROM tool_calls WHERE session_id = ?", (sid,))
                    db_conn.execute("DELETE FROM turns WHERE session_id = ?", (sid,))
                    db_conn.execute("DELETE FROM chapters WHERE session_id = ?", (sid,))
                    db_conn.execute("DELETE FROM alert_log WHERE session_id = ?", (sid,))
                    db_conn.execute("DELETE FROM sessions WHERE id = ?", (sid,))
                    db_conn.commit()
                    updated += 1
                else:
                    skipped += 1
                    continue

            if since:
                start_ts, _ = IncrementalJSONLParser.get_timestamps(records)
                if start_ts and start_ts[:10] < since:
                    continue

            # Parse and import
            try:
                _import_session(db_conn, str(jsonl_file), records, proj_name)
                imported += 1
                click.echo(f"  Imported: {sid[:20]}... ({jsonl_file.name})")
            except Exception as e:
                click.echo(f"  Error importing {jsonl_file.name}: {e}", err=True)

    click.echo(f"\nDone: {imported} imported, {updated} updated, {skipped} skipped")
    db_conn.close()


def _import_session(db_conn, jsonl_path, records, project_name):
    """Import a single session from parsed records with git and BEI enrichment.

    Populates sessions, turns, tool_calls, edits, and chapters tables.
    """
    cost_model = CostModel()
    git_linker = GitLinker()
    bei_engine = BEIEngine(db_conn=db_conn, cost_model=cost_model)
    try:
        baselines = calibrate_baselines(db_conn, window_days=30)
        if baselines:
            bei_engine.load_baselines(baselines)
    except Exception:
        pass

    sid = IncrementalJSONLParser.get_session_id(records)
    start_ts, end_ts = IncrementalJSONLParser.get_timestamps(records)
    model_id = ""
    tokens = TokenUsage()
    seen_ids = set()
    turn_count = 0
    tool_count = 0
    subagent_count = 0
    skills = []
    memory_entries = []
    docs_touched = []
    chapters_list = []
    edit_accept_count = 0
    edit_reject_count = 0
    tool_use_queue: dict[str, dict] = {}  # tool_use_id → pending tool info

    # Collect detail rows before inserting (FK constraint requires session row first)
    pending_turns: list[dict] = []
    pending_tool_calls: list[dict] = []
    pending_edits: list[dict] = []

    for record in records:
        rtype = record.get("type", "")
        rts = record.get("timestamp", "")

        if rtype == "assistant":
            m = IncrementalJSONLParser.extract_model(record)
            if m and not model_id:
                model_id = m

            is_new = IncrementalJSONLParser.is_new_message(record, seen_ids)
            if is_new:
                usage = IncrementalJSONLParser.extract_usage(record)
                if usage:
                    tokens += usage
                    turn_count += 1

                    # Queue turn record for later insert
                    msg = record.get("message", {})
                    pending_turns.append({
                        "session_id": sid,
                        "turn_index": turn_count,
                        "role": "assistant",
                        "timestamp": rts,
                        "message_id": msg.get("id", ""),
                        "input_tokens": usage.input_tokens,
                        "output_tokens": usage.output_tokens,
                        "cache_read_tokens": usage.cache_read_tokens,
                        "cache_creation_tokens": usage.cache_creation_tokens,
                        "model_id": m or model_id,
                    })

            # Queue tool uses for later matching with results
            for tc in IncrementalJSONLParser.extract_tool_uses(record):
                tool_count += 1
                if IncrementalJSONLParser.is_subagent_spawn(tc):
                    subagent_count += 1
                if IncrementalJSONLParser.is_skill_invocation(tc):
                    skill_name = tc.input_data.get("skill", "") if tc.input_data else ""
                    if skill_name and skill_name not in skills:
                        skills.append(skill_name)
                if IncrementalJSONLParser.is_chapter_marker(tc):
                    chapter_info = IncrementalJSONLParser.extract_chapter_info(tc)
                    chapter_info["start_turn"] = turn_count
                    chapter_info["start_timestamp"] = rts
                    chapters_list.append(chapter_info)

                tool_use_queue[tc.tool_use_id] = {
                    "name": tc.name,
                    "input": tc.input_data,
                    "timestamp": rts,
                    "turn_index": turn_count,
                }

        elif rtype == "user":
            # Extract memory/docs hints from user message content
            content = record.get("message", {}).get("content", "")
            if isinstance(content, str):
                if ".claude/memory" in content or "MEMORY.md" in content:
                    memory_entries.append(content[:200])
                if "docs/" in content and ".md" in content:
                    docs_touched.append(content[:200])

            # Match tool results with queued tool uses
            for result in IncrementalJSONLParser.extract_tool_results(record):
                tuid = result["tool_use_id"]
                pending = tool_use_queue.pop(tuid, None)
                if pending is None:
                    continue

                is_error = result.get("is_error", False)
                result_str = _truncate_result(result.get("content", ""))

                # Queue tool_call record for later insert
                pending_tool_calls.append({
                    "session_id": sid,
                    "turn_index": pending["turn_index"],
                    "tool_name": pending["name"],
                    "tool_input": json.dumps(pending["input"]) if pending["input"] else "",
                    "tool_result": result_str,
                    "success": 0 if is_error else 1,
                    "timestamp": pending["timestamp"],
                })

                # Insert edit record for edit-type tools
                if IncrementalJSONLParser.is_edit_tool(
                    ToolCall(name=pending["name"], tool_use_id=tuid, input_data=pending["input"])
                ):
                    lines_added, lines_removed = IncrementalJSONLParser.count_edit_lines(
                        pending["name"], pending["input"]
                    )
                    accepted = 0 if is_error else 1
                    if accepted:
                        edit_accept_count += 1
                    else:
                        edit_reject_count += 1

                    file_path = pending["input"].get("file_path", "")
                    if not file_path:
                        file_path = pending["input"].get("notebook_path", "")

                    pending_edits.append({
                        "session_id": sid,
                        "turn_index": pending["turn_index"],
                        "file_path": file_path,
                        "lines_added": lines_added,
                        "lines_removed": lines_removed,
                        "accepted": accepted,
                        "timestamp": pending["timestamp"],
                    })

    # Flush unmatched tool uses (no result received yet — session may be partial)
    for tuid, pending in tool_use_queue.items():
        pending_tool_calls.append({
            "session_id": sid,
            "turn_index": pending["turn_index"],
            "tool_name": pending["name"],
            "tool_input": json.dumps(pending["input"]) if pending["input"] else "",
            "tool_result": "",
            "success": 1,
            "timestamp": pending["timestamp"],
        })
        if IncrementalJSONLParser.is_edit_tool(
            ToolCall(name=pending["name"], tool_use_id=tuid, input_data=pending["input"])
        ):
            lines_added, lines_removed = IncrementalJSONLParser.count_edit_lines(
                pending["name"], pending["input"]
            )
            file_path = pending["input"].get("file_path", "")
            if not file_path:
                file_path = pending["input"].get("notebook_path", "")
            pending_edits.append({
                "session_id": sid,
                "turn_index": pending["turn_index"],
                "file_path": file_path,
                "lines_added": lines_added,
                "lines_removed": lines_removed,
                "accepted": 1,
                "timestamp": pending["timestamp"],
            })
            edit_accept_count += 1

    # Compute cost for BEI scoring and storage
    cost_for_bei = cost_model.calculate(tokens, model_id or "claude-sonnet-4-6")
    total_cost_usd_micro = int(cost_for_bei * 1_000_000)

    # Enrich with git data from session time window
    lines_added = 0
    lines_removed = 0
    files_touched = 0
    commits_count = 0
    commit_signals = {}
    if start_ts and end_ts:
        try:
            s_dt = datetime.fromisoformat(start_ts.replace("Z", "+00:00"))
            e_dt = datetime.fromisoformat(end_ts.replace("Z", "+00:00"))
            session_output = git_linker.get_session_output(s_dt, e_dt)
            lines_added = session_output["lines_added"]
            lines_removed = session_output["lines_removed"]
            files_touched = session_output["files_changed"]
            commits_count = session_output["commits_count"]
            commit_signals = session_output.get("decision_signals", {})
        except (ValueError, TypeError):
            pass

    session_data = {
        "id": sid,
        "project_name": project_name,
        "jsonl_path": jsonl_path,
        "model_id": model_id,
        "started_at": start_ts,
        "ended_at": end_ts,
        "total_input_tokens": tokens.input_tokens,
        "total_output_tokens": tokens.output_tokens,
        "total_cache_read_tokens": tokens.cache_read_tokens,
        "total_cache_creation_tokens": tokens.cache_creation_tokens,
        "total_cost_usd_micro": total_cost_usd_micro,
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "files_touched": files_touched,
        "commits_count": commits_count,
        "commit_signals": json.dumps(commit_signals),
        "tool_calls_total": tool_count,
        "subagent_spawns": subagent_count,
        "skills_invoked": json.dumps(skills),
        "memory_entries": json.dumps(memory_entries),
        "docs_touched": json.dumps(docs_touched),
        "edit_accept_count": edit_accept_count,
        "edit_reject_count": edit_reject_count,
    }
    insert_session(db_conn, session_data)

    # Bulk insert detail rows (FK requires session row to exist first)
    for t in pending_turns:
        insert_turn(db_conn, t)
    for tc in pending_tool_calls:
        insert_tool_call(db_conn, tc)
    for e in pending_edits:
        insert_edit(db_conn, e)

    # Insert chapter markers
    for i, ch in enumerate(chapters_list):
        insert_chapter(db_conn, {
            "session_id": sid,
            "chapter_index": i,
            "title": ch["title"],
            "summary": ch.get("summary", ""),
            "start_turn": ch["start_turn"],
            "start_timestamp": ch.get("start_timestamp", ""),
        })

    # Calculate and store BEI scores
    try:
        snap = SessionSnapshot(
            session_id=sid,
            project_name=project_name,
            started_at=start_ts or "",
        )
        snap.ended_at = end_ts or ""
        snap.model_id = model_id
        snap.tokens = tokens
        snap.cost_usd_micro = cost_for_bei
        snap.lines_added = lines_added
        snap.lines_removed = lines_removed
        snap.files_touched = files_touched
        snap.commits_count = commits_count
        snap.commit_signals = commit_signals
        snap.tool_calls_total = tool_count
        snap.subagent_spawns = subagent_count
        snap.skills_invoked = skills
        snap.memory_entries = memory_entries
        snap.docs_touched = docs_touched
        snap.edit_accept_count = edit_accept_count
        snap.edit_reject_count = edit_reject_count

        bei = bei_engine.calculate(snap, project_name)
        update_session(db_conn, sid,
                       bei_output_score=bei.output,
                       bei_quality_score=bei.quality,
                       bei_decision_score=bei.decision,
                       bei_knowledge_score=bei.knowledge,
                       bei_efficiency_score=bei.efficiency,
                       bei_composite=bei.composite)
    except Exception:
        pass

    # Update daily summary
    if start_ts:
        upsert_daily_summary(db_conn, start_ts[:10])

    return sid


def _truncate_result(content, max_chars: int = 500) -> str:
    """Truncate tool result content for storage."""
    if isinstance(content, str):
        return content[:max_chars]
    if isinstance(content, list):
        text = "".join(
            (c.get("text", "") if isinstance(c, dict) else str(c))
            for c in content
        )
        return text[:max_chars]
    return str(content)[:max_chars]


@db.command("stats")
def db_stats_cmd():
    """Show database statistics."""
    db_conn = init_db()
    stats = db_stats(db_conn)
    cm = CostModel()
    from tools.token_audit.parser import TokenUsage
    total_usage = TokenUsage(
        input_tokens=stats["total_input_tokens"],
        output_tokens=stats["total_output_tokens"],
        cache_read_tokens=stats.get("total_cache_read_tokens", 0),
        cache_creation_tokens=stats.get("total_cache_creation_tokens", 0),
    )
    cost_usd = cm.calculate_usd(total_usage, cm.default_model)
    click.echo("Database Statistics:")
    click.echo(f"  Sessions:    {stats['total_sessions']}")
    click.echo(f"  Turns:       {stats['total_turns']}")
    click.echo(f"  Tool Calls:  {stats['total_tool_calls']}")
    click.echo(f"  Edits:       {stats['total_edits']}")
    click.echo(f"  Alerts:      {stats['total_alerts']}")
    click.echo(f"  Date Range:  {stats['earliest_session'] or 'N/A'} → {stats['latest_session'] or 'N/A'}")
    click.echo(f"  Total Tokens: {stats['total_tokens']:,} (in: {stats['total_input_tokens']:,} / out: {stats['total_output_tokens']:,})")
    click.echo(f"  Cache Read:   {stats.get('total_cache_read_tokens', 0):,}")
    click.echo(f"  Cache Create: {stats.get('total_cache_creation_tokens', 0):,}")
    click.echo(f"  Total Cost ({cm.default_model}): ${cost_usd:.2f}")
    db_conn.close()


@db.command("vacuum")
def db_vacuum():
    """Compact and optimize the database."""
    db_conn = init_db()
    db_conn.execute("VACUUM")
    click.echo("Database vacuumed.")
    db_conn.close()


# ── dashboard ─────────────────────────────────────────────────

@main.command("dashboard")
@click.option("--days", "-d", default=30, help="Days to aggregate")
@click.option("--format", "-f", "output_fmt", default="terminal",
              type=click.Choice(["terminal", "html", "markdown"]))
@click.option("--output", "-o", "output_path", default=None, help="Output file path")
def dashboard_cmd(days, output_fmt, output_path):
    """Cross-project dashboard comparing all projects."""
    db_conn = init_db()
    cm = CostModel()
    from tools.token_audit.reporter import generate_dashboard
    content = generate_dashboard(db_conn, cm, days=days, fmt=output_fmt)
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
        click.echo(f"Dashboard saved to {output_path}")
    else:
        click.echo(content)
    db_conn.close()


# ── routing ─────────────────────────────────────────────────

@main.command("routing")
@click.option("--days", "-d", default=90, help="Days of history to analyze")
@click.option("--format", "-f", "output_fmt", default="markdown",
              type=click.Choice(["markdown", "json"]))
@click.option("--output", "-o", "output_path", default=None, help="Output file path")
def routing_cmd(days, output_fmt, output_path):
    """Analyze model routing: find sessions where a cheaper model could be used."""
    db_conn = init_db()
    cm = CostModel()
    from tools.token_audit.db import get_routing_candidates
    from tools.token_audit.reporter import generate_routing_report

    candidates = get_routing_candidates(db_conn, cm, days=days)
    content = generate_routing_report(candidates, days=days, fmt=output_fmt)

    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
        click.echo(f"Routing report saved to {output_path}")
    else:
        click.echo(content)
    db_conn.close()


# ── baseline ──────────────────────────────────────────────────

@main.group()
def baseline():
    """BEI baseline calibration commands."""
    pass


@baseline.command("calibrate")
@click.option("--project", "-p", default=None, help="Project name (default: all projects)")
@click.option("--days", "-d", default=30, help="Window in days")
def baseline_calibrate(project, days):
    """Calibrate BEI baselines from historical data (P25/P50/P75)."""
    db_conn = init_db()
    metrics = calibrate_baselines(db_conn, project=project, window_days=days)
    if metrics:
        click.echo(f"Calibrated baselines ({days}d window):")
        for metric, stats in sorted(metrics.items()):
            conf = stats.get("confidence", "normal")
            conf_str = " [LOW CONFIDENCE]" if conf == "low" else ""
            click.echo(f"  {metric}:{conf_str}")
            click.echo(f"    P25={stats['p25']:.2f}  P50={stats['p50']:.2f}  P75={stats['p75']:.2f}  n={stats['sample_size']}")
    else:
        click.echo("Insufficient data for calibration (need >=3 sessions per metric).")
    db_conn.close()


# ── snap ──────────────────────────────────────────────────────

@main.command()
@click.option("--session", "-s", "session_id", default=None, help="Session ID (default: latest)")
@click.option("--format", "-f", "output_fmt", default="text",
              type=click.Choice(["text", "json"]))
@click.option("--pricing", "-p", "pricing_model", default="",
              help="Pricing model for cost display")
@click.option("--trend/--no-trend", default=False,
              help="Compare vs 7-day average (BEI, cost, tokens, cache)")
def snap(session_id, output_fmt, pricing_model, trend):
    """Quick one-shot session summary — no JSONL scanning, DB-only.

    Much faster than 'report' for a quick check. Shows tokens, cost,
    BEI, cache rate, and edits in a compact format.
    """
    db_conn = init_db()
    cost_model = CostModel()
    if not pricing_model:
        pricing_model = cost_model.default_model

    if session_id:
        sess = get_session(db_conn, session_id)
    else:
        sess = get_latest_session(db_conn)

    if not sess:
        click.echo("No sessions in database. Run 'db import' first.")
        db_conn.close()
        return

    model_for_cost = cost_model.resolve_model(pricing_model, sess.get("model_id", ""))
    usage = TokenUsage(
        input_tokens=sess.get("total_input_tokens", 0),
        output_tokens=sess.get("total_output_tokens", 0),
        cache_read_tokens=sess.get("total_cache_read_tokens", 0),
        cache_creation_tokens=sess.get("total_cache_creation_tokens", 0),
    )
    cost_usd = cost_model.calculate_usd(usage, model_for_cost)
    total_tokens = usage.input_tokens + usage.output_tokens
    cache_rate = usage.cache_hit_rate
    bei = sess.get("bei_composite", 0) or 0
    commits = sess.get("commits_count", 0) or 0
    cpc = cost_usd / commits if commits > 0 else float("inf")
    loc = (sess.get("lines_added", 0) or 0) + (sess.get("lines_removed", 0) or 0)

    # Compute 7-day averages for trend comparison
    trend_data = {}
    if trend:
        trend_data = _compute_7day_averages(db_conn, cost_model, model_for_cost)

    if output_fmt == "json":
        data = {
            "session_id": sess["id"][:20],
            "project": sess.get("project_name", ""),
            "started_at": sess.get("started_at", ""),
            "model": sess.get("model_id", ""),
            "tokens": {"input": usage.input_tokens, "output": usage.output_tokens,
                       "cache_read": usage.cache_read_tokens, "cache_creation": usage.cache_creation_tokens,
                       "total": total_tokens},
            "cost_usd": round(cost_usd, 4),
            "pricing_model": model_for_cost,
            "cache_hit_rate": round(cache_rate, 3),
            "bei": round(bei, 3),
            "bei_rating": BEIScores.rating(bei),
            "commits": commits,
            "cost_per_commit": round(cpc, 4) if cpc != float("inf") else None,
            "lines_changed": loc,
        }
        if trend_data:
            data["trend"] = trend_data
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"Session: {sess['id'][:20]}...  {sess.get('started_at', '?')[:19]}")
        click.echo(f"Project: {sess.get('project_name', '?')}  Model: {sess.get('model_id', '?')}")
        click.echo(f"Tokens:  in={usage.input_tokens:,}  out={usage.output_tokens:,}  "
                   f"cache_read={usage.cache_read_tokens:,}  total={total_tokens:,}")
        click.echo(f"Cost:    ${cost_usd:.2f} ({model_for_cost})  "
                   f"Cache: {cache_rate:.1%}  BEI: {bei:.2f} {BEIScores.rating(bei)}")
        click.echo(f"Output:  {loc} lines  {commits} commits  "
                   f"CPC=${cpc:.2f}" if cpc != float("inf") else f"Output:  {loc} lines  {commits} commits")

        if trend_data:
            click.echo(f"\n── vs 7-day average (n={trend_data.get('sample_size', 0)}) ──")
            for label, key, fmt_fn, invert in [
                ("BEI", "avg_bei", lambda v: f"{v:.2f}", False),
                ("Cost", "avg_cost", lambda v: f"${v:.2f}", True),
                ("Tokens", "avg_tokens", lambda v: f"{v:,.0f}", True),
                ("Cache", "avg_cache", lambda v: f"{v:.1%}", False),
            ]:
                avg = trend_data.get(key)
                if avg is None:
                    continue
                if key == "avg_bei":
                    cur = bei
                elif key == "avg_cost":
                    cur = cost_usd
                elif key == "avg_tokens":
                    cur = float(total_tokens)
                elif key == "avg_cache":
                    cur = cache_rate
                else:
                    continue

                if avg > 0:
                    delta = (cur - avg) / avg * 100
                    arrow = _trend_arrow(delta, invert)
                    click.echo(f"  {label}: {fmt_fn(cur)} vs {fmt_fn(avg)}  {arrow} {abs(delta):.0f}%")

    db_conn.close()


def _compute_7day_averages(db_conn, cost_model, pricing_model) -> dict:
    """Compute 7-day averages for key metrics from the sessions table."""
    from tools.token_audit.parser import TokenUsage

    rows = db_conn.execute(
        """SELECT
            COALESCE(AVG(bei_composite), 0) as avg_bei,
            COALESCE(AVG(total_input_tokens + total_output_tokens), 0) as avg_tokens,
            COALESCE(AVG(
                CAST(total_cache_read_tokens AS REAL)
                / NULLIF(total_cache_read_tokens + total_input_tokens, 0)
            ), 0) as avg_cache,
            COALESCE(SUM(total_input_tokens), 0) as sum_input,
            COALESCE(SUM(total_output_tokens), 0) as sum_output,
            COALESCE(SUM(total_cache_read_tokens), 0) as sum_cache_read,
            COALESCE(SUM(total_cache_creation_tokens), 0) as sum_cache_create,
            COUNT(*) as n
        FROM sessions
        WHERE date(started_at) >= date('now', '-7 days')
          AND date(started_at) < date('now')"""
    ).fetchone()

    if not rows or rows["n"] == 0:
        return {}

    usage = TokenUsage(
        input_tokens=rows["sum_input"],
        output_tokens=rows["sum_output"],
        cache_read_tokens=rows["sum_cache_read"],
        cache_creation_tokens=rows["sum_cache_create"],
    )
    avg_cost = cost_model.calculate_usd(usage, pricing_model) / rows["n"]

    return {
        "avg_bei": round(rows["avg_bei"], 3),
        "avg_tokens": round(rows["avg_tokens"], 0),
        "avg_cache": round(rows["avg_cache"], 3),
        "avg_cost": round(avg_cost, 4),
        "sample_size": rows["n"],
    }


def _trend_arrow(delta_pct: float, invert: bool) -> str:
    """Return trend arrow indicator. invert=True means lower is better (cost, tokens)."""
    is_up = delta_pct > 0
    if invert:
        is_up = not is_up
    if abs(delta_pct) < 3:
        return "→"
    return "↑" if is_up else "↓"


# ── diagnose (v2) ──────────────────────────────────────────────

@main.command()
@click.option("--session", "-s", "session_id", required=True, help="Session ID to diagnose")
@click.option("--format", "-f", "output_fmt", default="text",
              type=click.Choice(["text", "json"]))
def diagnose(session_id, output_fmt):
    """Generate a full v2 token economic diagnostic for a session."""
    db_conn = init_db()
    sess = get_session(db_conn, session_id)
    if not sess:
        click.echo(f"Session {session_id} not found.")
        return

    from tools.token_audit.metrics_engine import (
        RawTelemetry, MetricsEngine, CACHEABLE_PREFIX_ESTIMATE,
    )
    from tools.token_audit.composite_indices import CompositeIndexEngine
    from tools.token_audit.decision_engine import DecisionEngine
    from tools.token_audit.reporter import generate_session_diagnostic_card

    # Build RawTelemetry from DB session
    raw = RawTelemetry(
        input_tokens=sess.get("total_input_tokens", 0),
        output_tokens=sess.get("total_output_tokens", 0),
        cache_read_tokens=sess.get("total_cache_read_tokens", 0),
        cache_creation_tokens=sess.get("total_cache_creation_tokens", 0),
        turn_count=sess.get("turn_count", 0),
        tool_call_count=sess.get("tool_calls_total", 0),
        task_outcome=sess.get("task_outcome", "") or "",
        task_type=sess.get("task_type", "") or "",
        task_risk_level=sess.get("task_risk_level", "medium") or "medium",
        model_id=sess.get("model_id", "") or "",
        cache_ttl_setting=sess.get("cache_ttl_setting", "5min") or "5min",
        estimated_overhead_tokens=sess.get("estimated_overhead_tokens", 0) or CACHEABLE_PREFIX_ESTIMATE,
        staleness_events=sess.get("staleness_events", 0),
        verification_tokens_estimate=sess.get("verification_tokens_estimate", 0),
        tool_definition_tokens_estimate=sess.get("tool_definition_tokens_estimate", 0),
        lines_added=sess.get("lines_added", 0),
        lines_removed=sess.get("lines_removed", 0),
        commits_count=sess.get("commits_count", 0),
        session_id=session_id,
    )

    engine = MetricsEngine()
    m = engine.compute(raw)

    cie = CompositeIndexEngine()
    ci = cie.compute_all(m, raw)

    de = DecisionEngine()
    historical = _load_historical_atei(db_conn)
    alerts = de.evaluate(m, ci, raw, historical)

    if output_fmt == "json":
        import json as _json
        result = {
            "session_id": session_id,
            "derived_metrics": {
                "hr_raw": m.hr_raw, "hr_effective": m.hr_effective, "cwar": m.cwar,
                "sclor": m.sclor, "clae": m.clae, "tlr": m.tlr, "twr": m.twr,
                "usr": m.usr, "stes": m.stes, "vcr": m.vcr, "cgr": m.cgr, "tdor": m.tdor,
            },
            "composite_indices": {
                "ths": ci.ths, "cti": ci.cti, "ser": ci.ser,
                "workload": ci.workload, "cache_health_state": ci.cache_health_state,
            },
            "alerts": [{"rule": a.rule_id, "severity": a.severity.value, "message": a.message}
                       for a in alerts],
        }
        click.echo(_json.dumps(result, indent=2, ensure_ascii=False))
    else:
        card = generate_session_diagnostic_card(raw, m, ci, alerts)
        click.echo(card)


# ── cache-health (v2) ──────────────────────────────────────────

@main.command()
@click.option("--days", "-d", default=30, help="Number of days to analyze")
@click.option("--format", "-f", "output_fmt", default="text",
              type=click.Choice(["text", "json"]))
def cache_health(days, output_fmt):
    """Generate a cache health deep-dive report across recent sessions."""
    db_conn = init_db()
    from tools.token_audit.metrics_engine import (
        RawTelemetry, MetricsEngine, CACHEABLE_PREFIX_ESTIMATE,
    )
    from tools.token_audit.composite_indices import CompositeIndexEngine
    from tools.token_audit.cost_model import CostModel

    cm = CostModel()
    engine = MetricsEngine()
    cie = CompositeIndexEngine()

    sessions = list_sessions(db_conn, limit=200)
    results = []
    for sess in sessions:
        raw = RawTelemetry(
            input_tokens=sess.get("total_input_tokens", 0),
            output_tokens=sess.get("total_output_tokens", 0),
            cache_read_tokens=sess.get("total_cache_read_tokens", 0),
            cache_creation_tokens=sess.get("total_cache_creation_tokens", 0),
            turn_count=sess.get("turn_count", 0),
            task_type=sess.get("task_type", "") or "",
            task_risk_level=sess.get("task_risk_level", "medium") or "medium",
            model_id=sess.get("model_id", "") or "",
            cache_ttl_setting=sess.get("cache_ttl_setting", "5min") or "5min",
            estimated_overhead_tokens=sess.get("estimated_overhead_tokens", 0) or CACHEABLE_PREFIX_ESTIMATE,
            staleness_events=sess.get("staleness_events", 0),
            verification_tokens_estimate=sess.get("verification_tokens_estimate", 0),
            session_id=sess.get("id", ""),
        )
        m = engine.compute(raw)
        ci = cie.compute_all(m, raw)
        results.append({
            "session_id": sess.get("id", ""),
            "date": (sess.get("started_at", "") or "")[:10],
            "model": raw.model_id,
            "hr_raw": m.hr_raw,
            "hr_effective": m.hr_effective,
            "cwar": m.cwar,
            "usr": m.usr,
            "cti": ci.cti,
            "state": ci.cache_health_state,
        })

    if output_fmt == "json":
        import json as _json
        click.echo(_json.dumps(results, indent=2, ensure_ascii=False))
        return

    # Text report
    states = {}
    for r in results:
        states.setdefault(r["state"], 0)
        states[r["state"]] += 1

    avg_cti = sum(r["cti"] for r in results) / max(len(results), 1)
    avg_cwar = sum(r["cwar"] for r in results if r["cwar"] != float('inf')) / max(len(results), 1)
    total_usr = sum(r["usr"] for r in results)

    click.echo(f"Cache Health Report ({days}d)")
    click.echo(f"  Sessions analyzed: {len(results)}")
    click.echo(f"  Avg CTI: {avg_cti:.2f}  |  Avg CWAR: {avg_cwar:.1f}  |  Total USR events: {total_usr:.0f}")
    click.echo(f"  State distribution:")
    for state in ["Ideal", "Wasteful", "Dangerous", "Inefficient", "Broken"]:
        count = states.get(state, 0)
        if count > 0:
            bar = "#" * max(count, 1)
            click.echo(f"    {state:<14} {count:>3}  {bar}")


def _load_historical_atei(db_conn) -> dict:
    """Load ATEI historical baselines from daily_summary."""
    try:
        summaries_7d = get_daily_summaries(db_conn, 7)
        summaries_14d = get_daily_summaries(db_conn, 14)
        atei_7d = sum(s.get("atei", 0) or 0 for s in summaries_7d) / max(len(summaries_7d), 1)
        atei_14d = sum(s.get("atei", 0) or 0 for s in summaries_14d) / max(len(summaries_14d), 1)
        return {"atei_7d": atei_7d, "atei_14d": atei_14d}
    except Exception:
        return {}


if __name__ == "__main__":
    main()
