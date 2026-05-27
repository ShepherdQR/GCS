"""CLI interface for the GCS Token Audit system."""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

import click

from tools.token_audit.db import (
    init_db, insert_session, update_session, get_session, list_sessions,
    get_latest_session, session_exists, close_session, db_stats,
    upsert_daily_summary, get_daily_summaries,
)
from tools.token_audit.parser import (
    IncrementalJSONLParser, SessionSnapshot, TokenUsage,
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
    alert_engine = AlertEngine(db_conn=db_conn)
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

    bei_engine = BEIEngine(db_conn=db_conn)

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
            alerts = alert_engine.evaluate(snap)
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
@click.option("--this-week", is_flag=True, help="Generate weekly report")
@click.option("--this-month", is_flag=True, help="Generate monthly report")
def report(session_id, from_date, to_date, output_fmt, output_path, this_week, this_month):
    """Generate session or time-range reports."""
    db_conn = init_db()
    cost_model = CostModel()
    bei_engine = BEIEngine(db_conn=db_conn)
    git_linker = GitLinker()

    content = ""

    if this_week:
        content = generate_weekly_report(db_conn)
    elif this_month:
        content = generate_monthly_report(db_conn)
    elif from_date and to_date:
        days = (datetime.strptime(to_date, "%Y-%m-%d") - datetime.strptime(from_date, "%Y-%m-%d")).days
        content = generate_trend_report(db_conn, days=max(days, 1))
    elif session_id:
        content = _report_single_session(db_conn, session_id, bei_engine, git_linker, cost_model, output_fmt)
    else:
        # Latest session
        sess = get_latest_session(db_conn)
        if not sess:
            click.echo("No sessions in database. Run 'db import' first or specify --session.")
            return
        content = _report_single_session(db_conn, sess["id"], bei_engine, git_linker, cost_model, output_fmt)

    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
        click.echo(f"Report saved to {output_path}")
    else:
        click.echo(content)


def _report_single_session(db_conn, session_id, bei_engine, git_linker, cost_model, fmt):
    """Generate a single-session report."""
    sess = get_session(db_conn, session_id)
    if not sess:
        return f"Session {session_id} not found."

    # Reconstruct snapshot from DB
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
    snap.cost_usd_micro = sess.get("total_cost_usd_micro", 0)
    snap.lines_added = sess.get("lines_added", 0)
    snap.lines_removed = sess.get("lines_removed", 0)
    snap.files_touched = sess.get("files_touched", 0)
    snap.commits_count = sess.get("commits_count", 0)
    snap.edit_accept_count = sess.get("edit_accept_count", 0)
    snap.edit_reject_count = sess.get("edit_reject_count", 0)
    snap.tool_calls_total = sess.get("tool_calls_total", 0)
    snap.subagent_spawns = sess.get("subagent_spawns", 0)
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

    return generate_session_report(snap, bei, cost_model, fmt)


# ── trend ────────────────────────────────────────────────────

@main.command()
@click.option("--days", "-d", default=7, help="Number of days to analyze")
@click.option("--metric", "-m", default="bei_composite",
              type=click.Choice(["bei_composite", "cost_per_commit", "cache_hit_rate"]))
@click.option("--format", "-f", "output_fmt", default="markdown",
              type=click.Choice(["markdown", "json"]))
def trend(days, metric, output_fmt):
    """Show historical efficiency trends."""
    db_conn = init_db()
    content = generate_trend_report(db_conn, days=days, fmt=output_fmt)
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
        click.echo(config_path.read_text(encoding="utf-8"))
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
@click.option("--project", "-p", default=None, help="Filter by project name")
def db_import(import_all, since, project):
    """Import session data from JSONL transcripts into the database."""
    db_conn = init_db()
    projects_dir = Path.home() / ".claude" / "projects"

    if not projects_dir.exists():
        click.echo("No Claude Code projects directory found.", err=True)
        return

    imported = 0
    skipped = 0

    for proj_dir in projects_dir.iterdir():
        if not proj_dir.is_dir():
            continue
        proj_name = proj_dir.name.replace("C--Codes-AI-", "").replace("C--Users-QR-Documents-", "")

        if project and project not in proj_name:
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

    click.echo(f"\nDone: {imported} imported, {skipped} skipped")
    db_conn.close()


def _import_session(db_conn, jsonl_path, records, project_name):
    """Import a single session from parsed records."""
    cost_model = CostModel()
    parser = IncrementalJSONLParser(jsonl_path)

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

    for record in records:
        if record.get("type") == "assistant":
            m = IncrementalJSONLParser.extract_model(record)
            if m and not model_id:
                model_id = m

            is_new = IncrementalJSONLParser.is_new_message(record, seen_ids)
            if is_new:
                usage = IncrementalJSONLParser.extract_usage(record)
                if usage:
                    tokens += usage
                    turn_count += 1

            for tc in IncrementalJSONLParser.extract_tool_uses(record):
                tool_count += 1
                if IncrementalJSONLParser.is_subagent_spawn(tc):
                    subagent_count += 1
                if IncrementalJSONLParser.is_skill_invocation(tc):
                    skill_name = tc.input_data.get("skill", "") if tc.input_data else ""
                    if skill_name and skill_name not in skills:
                        skills.append(skill_name)

        elif record.get("type") == "user":
            content = record.get("message", {}).get("content", "")
            if isinstance(content, str):
                if ".claude/memory" in content or "MEMORY.md" in content:
                    memory_entries.append(content[:200])
                if "docs/" in content and ".md" in content:
                    docs_touched.append(content[:200])

    cost = cost_model.calculate(tokens, model_id or "claude-sonnet-4-6")

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
        "total_cost_usd_micro": cost,
        "tool_calls_total": tool_count,
        "subagent_spawns": subagent_count,
        "skills_invoked": json.dumps(skills),
        "memory_entries": json.dumps(memory_entries),
        "docs_touched": json.dumps(docs_touched),
    }
    insert_session(db_conn, session_data)

    # Update daily summary
    if start_ts:
        upsert_daily_summary(db_conn, start_ts[:10])

    return sid


@db.command("stats")
def db_stats_cmd():
    """Show database statistics."""
    db_conn = init_db()
    stats = db_stats(db_conn)
    click.echo("Database Statistics:")
    click.echo(f"  Sessions:    {stats['total_sessions']}")
    click.echo(f"  Turns:       {stats['total_turns']}")
    click.echo(f"  Tool Calls:  {stats['total_tool_calls']}")
    click.echo(f"  Edits:       {stats['total_edits']}")
    click.echo(f"  Alerts:      {stats['total_alerts']}")
    click.echo(f"  Date Range:  {stats['earliest_session'] or 'N/A'} → {stats['latest_session'] or 'N/A'}")
    click.echo(f"  Total Tokens: {stats['total_tokens']:,} (in: {stats['total_input_tokens']:,} / out: {stats['total_output_tokens']:,})")
    click.echo(f"  Total Cost:   ${stats['total_cost_usd']:.2f}")
    db_conn.close()


@db.command("vacuum")
def db_vacuum():
    """Compact and optimize the database."""
    db_conn = init_db()
    db_conn.execute("VACUUM")
    click.echo("Database vacuumed.")
    db_conn.close()


if __name__ == "__main__":
    main()
