"""SQLite database layer for the token audit system."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_db(path: str = None) -> sqlite3.Connection:
    """Initialize the audit database, creating tables if they don't exist."""
    if path is None:
        path = str(Path(__file__).parent / "audit.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    _migrate(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Apply schema migrations for existing databases."""
    existing = {r[1] for r in conn.execute("PRAGMA table_info(sessions)").fetchall()}
    if "commit_signals" not in existing:
        conn.execute("ALTER TABLE sessions ADD COLUMN commit_signals TEXT")
    if "total_cache_read_tokens" not in existing:
        conn.execute("ALTER TABLE sessions ADD COLUMN total_cache_read_tokens INTEGER DEFAULT 0")
        conn.execute("ALTER TABLE sessions ADD COLUMN total_cache_creation_tokens INTEGER DEFAULT 0")

    # v2 migrations — token economic evaluation system
    _migrate_v2_sessions(conn, existing)

    daily_existing = {r[1] for r in conn.execute("PRAGMA table_info(daily_summary)").fetchall()}
    _migrate_v2_daily_summary(conn, daily_existing)


def _migrate_v2_sessions(conn: sqlite3.Connection, existing: set) -> None:
    """Phase 1 v2 columns for sessions table."""
    v2_columns = [
        ("cache_ttl_setting", "TEXT DEFAULT '5min'"),
        ("workload_category", "TEXT DEFAULT ''"),
        ("task_type", "TEXT DEFAULT ''"),
        ("task_risk_level", "TEXT DEFAULT 'medium'"),
        ("task_outcome", "TEXT DEFAULT ''"),
        ("estimated_overhead_tokens", "INTEGER DEFAULT 0"),
        ("staleness_events", "INTEGER DEFAULT 0"),
        ("verification_tokens_estimate", "INTEGER DEFAULT 0"),
        ("tool_definition_tokens_estimate", "INTEGER DEFAULT 0"),
    ]
    for col_name, col_def in v2_columns:
        if col_name not in existing:
            conn.execute(f"ALTER TABLE sessions ADD COLUMN {col_name} {col_def}")


def _migrate_v2_daily_summary(conn: sqlite3.Connection, existing: set) -> None:
    """Phase 1 v2 columns for daily_summary table."""
    v2_columns = [
        ("avg_hr_effective", "REAL DEFAULT 0"),
        ("avg_cwar", "REAL DEFAULT 0"),
        ("total_staleness_events", "INTEGER DEFAULT 0"),
        ("avg_sclor", "REAL DEFAULT 0"),
        ("avg_tlr", "REAL DEFAULT 0"),
        ("atei", "REAL DEFAULT 0"),
    ]
    for col_name, col_def in v2_columns:
        if col_name not in existing:
            conn.execute(f"ALTER TABLE daily_summary ADD COLUMN {col_name} {col_def}")


# ── Session CRUD ──────────────────────────────────────────────

def insert_session(conn: sqlite3.Connection, session_data: dict) -> str:
    """Insert a new session record. Returns session_id."""
    cols = ", ".join(session_data.keys())
    placeholders = ", ".join("?" for _ in session_data)
    conn.execute(
        f"INSERT OR REPLACE INTO sessions ({cols}) VALUES ({placeholders})",
        list(session_data.values()),
    )
    conn.commit()
    return session_data["id"]


def update_session(conn: sqlite3.Connection, session_id: str, **kwargs) -> None:
    """Update session fields."""
    if not kwargs:
        return
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    conn.execute(
        f"UPDATE sessions SET {sets} WHERE id = ?",
        list(kwargs.values()) + [session_id],
    )
    conn.commit()


def get_session(conn: sqlite3.Connection, session_id: str) -> Optional[dict]:
    """Get a session by ID."""
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    return dict(row) if row else None


# ── Detail table inserts ─────────────────────────────────────

def insert_turn(conn: sqlite3.Connection, turn_data: dict) -> int:
    """Insert a turn record. Returns row id."""
    cur = conn.execute(
        """INSERT OR REPLACE INTO turns
           (session_id, turn_index, role, timestamp, message_id,
            input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens, model_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (turn_data["session_id"], turn_data["turn_index"], turn_data["role"],
         turn_data["timestamp"], turn_data.get("message_id", ""),
         turn_data.get("input_tokens", 0), turn_data.get("output_tokens", 0),
         turn_data.get("cache_read_tokens", 0), turn_data.get("cache_creation_tokens", 0),
         turn_data.get("model_id", "")),
    )
    return cur.lastrowid


def insert_tool_call(conn: sqlite3.Connection, tc_data: dict) -> int:
    """Insert a tool_call record. Returns row id."""
    cur = conn.execute(
        """INSERT INTO tool_calls
           (session_id, turn_index, tool_name, tool_input, tool_result,
            duration_ms, success, timestamp)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (tc_data["session_id"], tc_data["turn_index"], tc_data["tool_name"],
         tc_data.get("tool_input", ""), tc_data.get("tool_result", ""),
         tc_data.get("duration_ms", 0), tc_data.get("success", 1),
         tc_data["timestamp"]),
    )
    return cur.lastrowid


def insert_edit(conn: sqlite3.Connection, edit_data: dict) -> int:
    """Insert an edit record. Returns row id."""
    cur = conn.execute(
        """INSERT INTO edits
           (session_id, turn_index, file_path, lines_added, lines_removed, accepted, timestamp)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (edit_data["session_id"], edit_data["turn_index"], edit_data["file_path"],
         edit_data.get("lines_added", 0), edit_data.get("lines_removed", 0),
         edit_data.get("accepted", 1), edit_data["timestamp"]),
    )
    return cur.lastrowid


def list_sessions(
    conn: sqlite3.Connection,
    project: str = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """List sessions, optionally filtered by project."""
    if project:
        rows = conn.execute(
            "SELECT * FROM sessions WHERE project_name = ? ORDER BY started_at DESC LIMIT ? OFFSET ?",
            (project, limit, offset),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY started_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [dict(r) for r in rows]


def get_latest_session(conn: sqlite3.Connection, project: str = None) -> Optional[dict]:
    """Get the most recent session."""
    if project:
        row = conn.execute(
            "SELECT * FROM sessions WHERE project_name = ? ORDER BY started_at DESC LIMIT 1",
            (project,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM sessions ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def session_exists(conn: sqlite3.Connection, session_id: str) -> bool:
    """Check if a session is already in the database."""
    row = conn.execute(
        "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    return row is not None


def get_active_sessions(conn: sqlite3.Connection) -> list[dict]:
    """Get sessions that are still in progress (no ended_at)."""
    rows = conn.execute(
        "SELECT * FROM sessions WHERE ended_at IS NULL ORDER BY started_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def close_session(conn: sqlite3.Connection, session_id: str, ended_at: str = None) -> None:
    """Mark a session as ended."""
    if ended_at is None:
        ended_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.execute(
        "UPDATE sessions SET ended_at = ? WHERE id = ?",
        (ended_at, session_id),
    )
    conn.commit()


# ── Turn CRUD ─────────────────────────────────────────────────

def insert_turn(conn: sqlite3.Connection, turn_data: dict) -> int:
    """Insert a turn record. Returns row id."""
    cols = ", ".join(turn_data.keys())
    placeholders = ", ".join("?" for _ in turn_data)
    cur = conn.execute(
        f"INSERT INTO turns ({cols}) VALUES ({placeholders})",
        list(turn_data.values()),
    )
    conn.commit()
    return cur.lastrowid


# ── Tool Call CRUD ────────────────────────────────────────────

def insert_tool_call(conn: sqlite3.Connection, tc_data: dict) -> int:
    """Insert a tool call record."""
    cols = ", ".join(tc_data.keys())
    placeholders = ", ".join("?" for _ in tc_data)
    cur = conn.execute(
        f"INSERT INTO tool_calls ({cols}) VALUES ({placeholders})",
        list(tc_data.values()),
    )
    conn.commit()
    return cur.lastrowid


# ── Edit CRUD ─────────────────────────────────────────────────

def insert_edit(conn: sqlite3.Connection, edit_data: dict) -> int:
    """Insert an edit record."""
    cols = ", ".join(edit_data.keys())
    placeholders = ", ".join("?" for _ in edit_data)
    cur = conn.execute(
        f"INSERT INTO edits ({cols}) VALUES ({placeholders})",
        list(edit_data.values()),
    )
    conn.commit()
    return cur.lastrowid


# ── Alert CRUD ────────────────────────────────────────────────

def insert_alert(conn: sqlite3.Connection, alert_data: dict) -> int:
    """Insert an alert record."""
    cols = ", ".join(alert_data.keys())
    placeholders = ", ".join("?" for _ in alert_data)
    cur = conn.execute(
        f"INSERT INTO alert_log ({cols}) VALUES ({placeholders})",
        list(alert_data.values()),
    )
    conn.commit()
    return cur.lastrowid


def get_recent_alerts(
    conn: sqlite3.Connection, session_id: str = None, limit: int = 20
) -> list[dict]:
    """Get recent alerts, optionally filtered by session."""
    if session_id:
        rows = conn.execute(
            "SELECT * FROM alert_log WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM alert_log ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Chapter CRUD ───────────────────────────────────────────────

def insert_chapter(conn: sqlite3.Connection, chapter_data: dict) -> int:
    """Insert a chapter record. Returns row id."""
    cols = ", ".join(chapter_data.keys())
    placeholders = ", ".join("?" for _ in chapter_data)
    cur = conn.execute(
        f"INSERT OR REPLACE INTO chapters ({cols}) VALUES ({placeholders})",
        list(chapter_data.values()),
    )
    conn.commit()
    return cur.lastrowid


def get_chapters(conn: sqlite3.Connection, session_id: str) -> list[dict]:
    """Get all chapters for a session, ordered by chapter_index."""
    rows = conn.execute(
        "SELECT * FROM chapters WHERE session_id = ? ORDER BY chapter_index",
        (session_id,),
    ).fetchall()
    return [dict(r) for r in rows]


# ── Dashboard Aggregation ────────────────────────────────────

def get_project_summaries(
    conn: sqlite3.Connection, days: int = 30
) -> list[dict]:
    """Aggregate per-project metrics for the cross-project dashboard."""
    rows = conn.execute(
        """
        SELECT
            project_name,
            COUNT(*) as sessions_count,
            COALESCE(SUM(total_input_tokens), 0) as total_input_tokens,
            COALESCE(SUM(total_output_tokens), 0) as total_output_tokens,
            COALESCE(SUM(total_cache_read_tokens), 0) as total_cache_read_tokens,
            COALESCE(SUM(lines_added), 0) as lines_added,
            COALESCE(SUM(lines_removed), 0) as lines_removed,
            COALESCE(SUM(commits_count), 0) as commits_count,
            COALESCE(SUM(tool_calls_total), 0) as tool_calls,
            COALESCE(AVG(bei_composite), 0) as avg_bei,
            COALESCE(AVG(
                CAST(total_cache_read_tokens AS REAL)
                / NULLIF(total_cache_read_tokens + total_input_tokens, 0)
            ), 0) as avg_cache_hit_rate
        FROM sessions
        WHERE date(started_at) >= date('now', ?)
        GROUP BY project_name
        ORDER BY sessions_count DESC
        """,
        (f"-{days} days",),
    ).fetchall()
    return [dict(r) for r in rows]


def get_daily_bei_series(
    conn: sqlite3.Connection, project: str, days: int = 7
) -> list[float]:
    """Get daily BEI averages for a project (for sparkline)."""
    rows = conn.execute(
        """
        SELECT COALESCE(AVG(bei_composite), 0) as bei
        FROM sessions
        WHERE project_name = ? AND date(started_at) >= date('now', ?)
        GROUP BY date(started_at)
        ORDER BY date(started_at)
        """,
        (project, f"-{days} days"),
    ).fetchall()
    return [r["bei"] for r in rows]


# ── Budget Tracking ─────────────────────────────────────────

def get_today_cost(conn: sqlite3.Connection, cm) -> float:
    """Get total cost for today's sessions in USD."""
    from tools.token_audit.parser import TokenUsage
    row = conn.execute(
        """SELECT COALESCE(SUM(total_input_tokens), 0) as inp,
                  COALESCE(SUM(total_output_tokens), 0) as outp,
                  COALESCE(SUM(total_cache_read_tokens), 0) as cr,
                  COALESCE(SUM(total_cache_creation_tokens), 0) as cc
           FROM sessions WHERE date(started_at) = date('now')"""
    ).fetchone()
    usage = TokenUsage(input_tokens=row["inp"], output_tokens=row["outp"],
                       cache_read_tokens=row["cr"], cache_creation_tokens=row["cc"])
    return cm.calculate_usd(usage, cm.default_model)


def get_week_cost(conn: sqlite3.Connection, cm) -> float:
    """Get total cost for the current calendar week (Mon-Sun) in USD."""
    from tools.token_audit.parser import TokenUsage
    row = conn.execute(
        """SELECT COALESCE(SUM(total_input_tokens), 0) as inp,
                  COALESCE(SUM(total_output_tokens), 0) as outp,
                  COALESCE(SUM(total_cache_read_tokens), 0) as cr,
                  COALESCE(SUM(total_cache_creation_tokens), 0) as cc
           FROM sessions
           WHERE date(started_at) >= date('now', 'weekday 0', '-6 days')
             AND date(started_at) <= date('now')"""
    ).fetchone()
    usage = TokenUsage(input_tokens=row["inp"], output_tokens=row["outp"],
                       cache_read_tokens=row["cr"], cache_creation_tokens=row["cc"])
    return cm.calculate_usd(usage, cm.default_model)


def get_month_prediction(conn: sqlite3.Connection, cm) -> dict:
    """Predict end-of-month cost based on daily average.

    Returns {avg_daily_cost, month_to_date, remaining_days, predicted_total, predicted_remaining}.
    All values in USD.
    """
    import calendar
    from datetime import datetime
    from tools.token_audit.parser import TokenUsage

    today = datetime.utcnow()
    day_of_month = today.day
    total_days = calendar.monthrange(today.year, today.month)[1]
    remaining = total_days - day_of_month

    row = conn.execute(
        """SELECT COALESCE(SUM(total_input_tokens), 0) as inp,
                  COALESCE(SUM(total_output_tokens), 0) as outp,
                  COALESCE(SUM(total_cache_read_tokens), 0) as cr,
                  COALESCE(SUM(total_cache_creation_tokens), 0) as cc
           FROM sessions
           WHERE strftime('%Y-%m', started_at) = strftime('%Y-%m', 'now')"""
    ).fetchone()
    usage = TokenUsage(input_tokens=row["inp"], output_tokens=row["outp"],
                       cache_read_tokens=row["cr"], cache_creation_tokens=row["cc"])
    mtd_cost = cm.calculate_usd(usage, cm.default_model)
    avg_daily = mtd_cost / max(day_of_month, 1)
    predicted_remaining = avg_daily * remaining
    predicted_total = mtd_cost + predicted_remaining

    return {
        "avg_daily_cost": round(avg_daily, 4),
        "month_to_date": round(mtd_cost, 2),
        "remaining_days": remaining,
        "predicted_remaining": round(predicted_remaining, 2),
        "predicted_total": round(predicted_total, 2),
    }


# ── Routing Optimization ─────────────────────────────────────

def get_routing_candidates(
    conn: sqlite3.Connection, cm, days: int = 90
) -> list[dict]:
    """Find sessions where a cheaper model could have been used.

    Classifies sessions by pattern (edit ratio as proxy) and output complexity.
    Returns candidates sorted by potential savings (highest first).
    """
    from tools.token_audit.parser import TokenUsage

    rows = conn.execute(
        """SELECT id, project_name, model_id, started_at,
                  total_input_tokens, total_output_tokens,
                  total_cache_read_tokens, total_cache_creation_tokens,
                  tool_calls_total, edit_accept_count, edit_reject_count
           FROM sessions
           WHERE date(started_at) >= date('now', ?)
             AND total_input_tokens > 0
             AND (model_id LIKE '%sonnet%' OR model_id LIKE '%opus%')
           ORDER BY started_at DESC""",
        (f"-{days} days",),
    ).fetchall()

    candidates = []
    for row in rows:
        row = dict(row)
        usage = TokenUsage(
            input_tokens=row["total_input_tokens"],
            output_tokens=row["total_output_tokens"],
            cache_read_tokens=row["total_cache_read_tokens"],
            cache_creation_tokens=row["total_cache_creation_tokens"],
        )
        total_edits = row["edit_accept_count"] + row["edit_reject_count"]
        tool_total = max(row["tool_calls_total"], 1)
        edit_ratio = total_edits / tool_total

        if edit_ratio > 0.3:
            pattern = "editing-heavy"
        elif edit_ratio < 0.1 and row["tool_calls_total"] > 5:
            pattern = "reading-heavy"
        else:
            pattern = "mixed"

        actual_model = row["model_id"] or "claude-sonnet-4-6"
        recommended = _recommend_model(pattern, actual_model)
        if recommended == actual_model:
            continue

        actual_cost = cm.calculate_usd(usage, actual_model)
        recommended_cost = cm.calculate_usd(usage, recommended)
        savings = actual_cost - recommended_cost
        if savings <= 0:
            continue

        candidates.append({
            "session_id": row["id"][:20],
            "project": row["project_name"],
            "started_at": row["started_at"][:19] if row["started_at"] else "",
            "actual_model": actual_model,
            "recommended_model": recommended,
            "actual_cost": round(actual_cost, 4),
            "recommended_cost": round(recommended_cost, 4),
            "savings_usd": round(savings, 4),
            "pattern": pattern,
        })

    return sorted(candidates, key=lambda c: c["savings_usd"], reverse=True)


def _recommend_model(pattern: str, actual_model: str) -> str:
    """Recommend a cheaper model based on session pattern."""
    if "haiku" in actual_model.lower():
        return actual_model
    if pattern == "reading-heavy":
        return "claude-haiku-4-5"
    if pattern == "mixed":
        return "claude-haiku-4-5"
    return actual_model  # editing-heavy: keep current


# ── Baseline Calibration ─────────────────────────────────────

def calibrate_baselines(
    conn: sqlite3.Connection, project: str = None, window_days: int = 30
) -> dict:
    """Compute P25/P50/P75 baselines from historical sessions."""
    from tools.token_audit.cost_model import CostModel
    cm = CostModel()

    project_filter = "AND project_name = ?" if project else ""
    params = (project,) if project else ()

    metrics = {}

    # output_per_1M_tokens
    rows = conn.execute(
        f"""
        SELECT (CAST(lines_added + lines_removed AS REAL) * 1000000.0)
               / NULLIF(total_input_tokens + total_output_tokens, 0) as val
        FROM sessions
        WHERE total_input_tokens > 0
          AND date(started_at) >= date('now', ?)
          {project_filter}
        ORDER BY val
        """,
        (f"-{window_days} days",) + params,
    ).fetchall()
    vals = [r[0] for r in rows if r[0] is not None]
    if len(vals) >= 5:
        metrics["output_per_1M_tokens"] = {
            "p25": vals[int(len(vals) * 0.25)], "p50": vals[int(len(vals) * 0.50)],
            "p75": vals[int(len(vals) * 0.75)], "sample_size": len(vals),
        }

    # cost_per_commit (computed with default pricing)
    dp = cm.pricing["other"]["deepseek-v4-pro"]
    rows = conn.execute(
        f"""
        SELECT (total_input_tokens * ? + total_output_tokens * ?
                + total_cache_read_tokens * ? + total_cache_creation_tokens * ?
               ) / 1000000.0 / NULLIF(commits_count, 0) as val
        FROM sessions
        WHERE commits_count > 0 AND total_input_tokens > 0
          AND date(started_at) >= date('now', ?)
          {project_filter}
        ORDER BY val
        """,
        (dp["input"], dp["output"], dp["cache_read"], dp["cache_write"],
         f"-{window_days} days") + params,
    ).fetchall()
    vals = [r[0] for r in rows if r[0] is not None]
    if len(vals) >= 3:
        metrics["cost_per_commit"] = {
            "p25": vals[int(len(vals) * 0.25)], "p50": vals[int(len(vals) * 0.50)],
            "p75": vals[int(len(vals) * 0.75)], "sample_size": len(vals),
            "confidence": "low" if len(vals) < 5 else "normal",
        }

    # cache_hit_rate
    rows = conn.execute(
        f"""
        SELECT CAST(total_cache_read_tokens AS REAL)
               / NULLIF(total_cache_read_tokens + total_input_tokens, 0) as val
        FROM sessions
        WHERE total_input_tokens > 0
          AND date(started_at) >= date('now', ?)
          {project_filter}
        ORDER BY val
        """,
        (f"-{window_days} days",) + params,
    ).fetchall()
    vals = [r[0] for r in rows if r[0] is not None]
    if len(vals) >= 5:
        metrics["cache_hit_rate"] = {
            "p25": vals[int(len(vals) * 0.25)], "p50": vals[int(len(vals) * 0.50)],
            "p75": vals[int(len(vals) * 0.75)], "sample_size": len(vals),
        }

    # memory_entries_p90 — P90 of memory entries per session
    rows = conn.execute(
        f"""
        SELECT CAST(json_array_length(memory_entries) AS REAL) as val
        FROM sessions
        WHERE memory_entries IS NOT NULL AND memory_entries != '[]'
          AND date(started_at) >= date('now', ?)
          {project_filter}
        ORDER BY val
        """,
        (f"-{window_days} days",) + params,
    ).fetchall()
    vals = [r[0] for r in rows if r[0] is not None and r[0] > 0]
    if len(vals) >= 5:
        p90_idx = min(int(len(vals) * 0.90), len(vals) - 1)
        metrics["memory_entries_p90"] = {
            "p25": vals[int(len(vals) * 0.25)], "p50": vals[int(len(vals) * 0.50)],
            "p75": vals[int(len(vals) * 0.75)], "p90": vals[p90_idx],
            "sample_size": len(vals),
        }

    # skill_invocations_p90 — P90 of skill invocations per session
    rows = conn.execute(
        f"""
        SELECT CAST(json_array_length(skills_invoked) AS REAL) as val
        FROM sessions
        WHERE skills_invoked IS NOT NULL AND skills_invoked != '[]'
          AND date(started_at) >= date('now', ?)
          {project_filter}
        ORDER BY val
        """,
        (f"-{window_days} days",) + params,
    ).fetchall()
    vals = [r[0] for r in rows if r[0] is not None and r[0] > 0]
    if len(vals) >= 5:
        p90_idx = min(int(len(vals) * 0.90), len(vals) - 1)
        metrics["skill_invocations_p90"] = {
            "p25": vals[int(len(vals) * 0.25)], "p50": vals[int(len(vals) * 0.50)],
            "p75": vals[int(len(vals) * 0.75)], "p90": vals[p90_idx],
            "sample_size": len(vals),
        }

    return metrics


# ── Daily Summary ─────────────────────────────────────────────

def upsert_daily_summary(conn: sqlite3.Connection, date_str: str = None) -> None:
    """Recalculate and upsert daily summary for the given date (default: today).

    Cost is computed from raw tokens using the default pricing model.
    """
    if date_str is None:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    row = conn.execute(
        """
        SELECT
            COUNT(*) as sessions_count,
            COALESCE(SUM(total_input_tokens), 0) as total_input_tokens,
            COALESCE(SUM(total_output_tokens), 0) as total_output_tokens,
            COALESCE(SUM(total_cache_read_tokens), 0) as total_cache_read_tokens,
            COALESCE(SUM(total_cache_creation_tokens), 0) as total_cache_creation_tokens,
            COALESCE(SUM(lines_added), 0) as lines_added,
            COALESCE(SUM(lines_removed), 0) as lines_removed,
            COALESCE(SUM(commits_count), 0) as commits_count,
            CASE WHEN COUNT(*) > 0
                THEN CAST(COALESCE(SUM(total_cache_read_tokens), 0) AS REAL)
                     / NULLIF(COALESCE(SUM(total_input_tokens), 0) + COALESCE(SUM(total_cache_read_tokens), 0), 0)
                ELSE 0
            END as avg_cache_hit_rate,
            COALESCE(AVG(bei_composite), 0) as avg_bei_composite
        FROM sessions
        WHERE date(started_at) = ?
        """,
        (date_str,),
    ).fetchone()

    # Compute cost from raw tokens using default pricing model
    from tools.token_audit.cost_model import CostModel
    from tools.token_audit.parser import TokenUsage
    cm = CostModel()
    usage = TokenUsage(
        input_tokens=row["total_input_tokens"],
        output_tokens=row["total_output_tokens"],
        cache_read_tokens=row["total_cache_read_tokens"],
        cache_creation_tokens=row["total_cache_creation_tokens"],
    )
    cost_micro = cm.calculate(usage, cm.default_model)

    conn.execute(
        """
        INSERT INTO daily_summary
            (date, sessions_count, total_input_tokens, total_output_tokens,
             total_cost_usd_micro, lines_added, lines_removed, commits_count,
             avg_cache_hit_rate, avg_bei_composite)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            sessions_count = excluded.sessions_count,
            total_input_tokens = excluded.total_input_tokens,
            total_output_tokens = excluded.total_output_tokens,
            total_cost_usd_micro = excluded.total_cost_usd_micro,
            lines_added = excluded.lines_added,
            lines_removed = excluded.lines_removed,
            commits_count = excluded.commits_count,
            avg_cache_hit_rate = excluded.avg_cache_hit_rate,
            avg_bei_composite = excluded.avg_bei_composite
        """,
        (
            date_str,
            row["sessions_count"],
            row["total_input_tokens"],
            row["total_output_tokens"],
            cost_micro,
            row["lines_added"],
            row["lines_removed"],
            row["commits_count"],
            row["avg_cache_hit_rate"],
            row["avg_bei_composite"],
        ),
    )
    conn.commit()


def get_daily_summaries(
    conn: sqlite3.Connection, days: int = 30
) -> list[dict]:
    """Get daily summaries for the last N days."""
    rows = conn.execute(
        "SELECT * FROM daily_summary ORDER BY date DESC LIMIT ?",
        (days,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_project_baseline(
    conn: sqlite3.Connection, project: str, metric: str
) -> Optional[float]:
    """Get a project's historical P75 for a given metric."""
    valid_metrics = {
        "output_per_1M_tokens",
        "cost_per_commit",
        "cache_hit_rate",
        "edit_rejection_rate",
        "memory_entries_p90",
        "skill_invocations_p90",
    }
    if metric not in valid_metrics:
        return None

    if metric == "output_per_1M_tokens":
        rows = conn.execute(
            """
            SELECT (CAST(lines_added + lines_removed AS REAL) * 1000000.0)
                   / NULLIF(total_input_tokens + total_output_tokens, 0) as val
            FROM sessions
            WHERE project_name = ? AND total_input_tokens > 0
            ORDER BY val
            """,
            (project,),
        ).fetchall()
    elif metric == "cost_per_commit":
        # Compute cost from raw tokens using default pricing, then per-commit.
        # Default deepseek-v4-pro rates (USD/1M tokens) — matches config.yaml.
        rows = conn.execute(
            """
            SELECT (total_input_tokens * 0.435
                    + total_output_tokens * 0.87
                    + total_cache_read_tokens * 0.0035
                    + total_cache_creation_tokens * 0.435
                   ) / 1000000.0 / NULLIF(commits_count, 0) as val
            FROM sessions
            WHERE project_name = ? AND commits_count > 0
               AND total_input_tokens > 0
            ORDER BY val
            """,
            (project,),
        ).fetchall()
    elif metric == "cache_hit_rate":
        rows = conn.execute(
            """
            SELECT CAST(total_cache_read_tokens AS REAL)
                   / NULLIF(total_cache_read_tokens + total_input_tokens, 0) as val
            FROM sessions
            WHERE project_name = ? AND total_input_tokens > 0
            ORDER BY val
            """,
            (project,),
        ).fetchall()
    elif metric == "edit_rejection_rate":
        rows = conn.execute(
            """
            SELECT CAST(edit_reject_count AS REAL)
                   / NULLIF(edit_accept_count + edit_reject_count, 0) as val
            FROM sessions
            WHERE project_name = ? AND (edit_accept_count + edit_reject_count) > 0
            ORDER BY val
            """,
            (project,),
        ).fetchall()
    elif metric == "memory_entries_p90":
        rows = conn.execute(
            """
            SELECT CAST(json_array_length(memory_entries) AS REAL) as val
            FROM sessions
            WHERE project_name = ? AND memory_entries IS NOT NULL
            ORDER BY val
            """,
            (project,),
        ).fetchall()
    elif metric == "skill_invocations_p90":
        rows = conn.execute(
            """
            SELECT CAST(json_array_length(skills_invoked) AS REAL) as val
            FROM sessions
            WHERE project_name = ? AND skills_invoked IS NOT NULL
            ORDER BY val
            """,
            (project,),
        ).fetchall()
    else:
        return None

    if not rows:
        return None

    values = [r[0] for r in rows if r[0] is not None]
    if not values:
        return None

    # P75 for most metrics, P90 for thresholds (memory/skills)
    values.sort()
    if "p90" in metric:
        idx = int(len(values) * 0.90)
    else:
        idx = int(len(values) * 0.75)
    return values[min(idx, len(values) - 1)]


def db_stats(conn: sqlite3.Connection) -> dict:
    """Return database statistics. Cost is NOT computed here — caller should use CostModel."""
    return {
        "total_sessions": conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
        "total_turns": conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0],
        "total_tool_calls": conn.execute("SELECT COUNT(*) FROM tool_calls").fetchone()[0],
        "total_edits": conn.execute("SELECT COUNT(*) FROM edits").fetchone()[0],
        "total_alerts": conn.execute("SELECT COUNT(*) FROM alert_log").fetchone()[0],
        "earliest_session": conn.execute(
            "SELECT MIN(started_at) FROM sessions"
        ).fetchone()[0],
        "latest_session": conn.execute(
            "SELECT MAX(started_at) FROM sessions"
        ).fetchone()[0],
        "total_input_tokens": conn.execute(
            "SELECT COALESCE(SUM(total_input_tokens), 0) FROM sessions"
        ).fetchone()[0],
        "total_output_tokens": conn.execute(
            "SELECT COALESCE(SUM(total_output_tokens), 0) FROM sessions"
        ).fetchone()[0],
        "total_cache_read_tokens": conn.execute(
            "SELECT COALESCE(SUM(total_cache_read_tokens), 0) FROM sessions"
        ).fetchone()[0],
        "total_cache_creation_tokens": conn.execute(
            "SELECT COALESCE(SUM(total_cache_creation_tokens), 0) FROM sessions"
        ).fetchone()[0],
        "total_tokens": conn.execute(
            "SELECT COALESCE(SUM(total_input_tokens + total_output_tokens), 0) FROM sessions"
        ).fetchone()[0],
    }
