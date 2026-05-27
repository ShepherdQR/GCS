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
    return conn


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


# ── Daily Summary ─────────────────────────────────────────────

def upsert_daily_summary(conn: sqlite3.Connection, date_str: str = None) -> None:
    """Recalculate and upsert daily summary for the given date (default: today)."""
    if date_str is None:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    row = conn.execute(
        """
        SELECT
            COUNT(*) as sessions_count,
            COALESCE(SUM(total_input_tokens), 0) as total_input_tokens,
            COALESCE(SUM(total_output_tokens), 0) as total_output_tokens,
            COALESCE(SUM(total_cost_usd_micro), 0) as total_cost_usd_micro,
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
            row["total_cost_usd_micro"],
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
        rows = conn.execute(
            """
            SELECT CAST(total_cost_usd_micro AS REAL) / 1000000.0 / NULLIF(commits_count, 0) as val
            FROM sessions
            WHERE project_name = ? AND commits_count > 0
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
    else:
        return None

    if not rows:
        return None

    values = [r[0] for r in rows if r[0] is not None]
    if not values:
        return None

    # P75
    values.sort()
    idx = int(len(values) * 0.75)
    return values[min(idx, len(values) - 1)]


def db_stats(conn: sqlite3.Connection) -> dict:
    """Return database statistics."""
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
        "total_tokens": conn.execute(
            "SELECT COALESCE(SUM(total_input_tokens + total_output_tokens), 0) FROM sessions"
        ).fetchone()[0],
        "total_cost_usd": conn.execute(
            "SELECT COALESCE(SUM(total_cost_usd_micro), 0) / 1000000.0 FROM sessions"
        ).fetchone()[0],
    }
