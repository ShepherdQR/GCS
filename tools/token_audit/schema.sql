-- GCS Token Audit System — Database Schema

CREATE TABLE IF NOT EXISTS sessions (
    id              TEXT PRIMARY KEY,
    project_name    TEXT NOT NULL,
    jsonl_path      TEXT,
    model_id        TEXT,
    started_at      TEXT NOT NULL,
    ended_at        TEXT,

    total_input_tokens          INTEGER DEFAULT 0,
    total_output_tokens         INTEGER DEFAULT 0,
    total_cache_read_tokens     INTEGER DEFAULT 0,
    total_cache_creation_tokens INTEGER DEFAULT 0,

    total_cost_usd_micro INTEGER DEFAULT 0,

    lines_added         INTEGER DEFAULT 0,
    lines_removed       INTEGER DEFAULT 0,
    files_touched       INTEGER DEFAULT 0,
    commits_count       INTEGER DEFAULT 0,

    commit_signals      TEXT,
    edit_accept_count   INTEGER DEFAULT 0,
    edit_reject_count   INTEGER DEFAULT 0,

    tool_calls_total    INTEGER DEFAULT 0,
    subagent_spawns     INTEGER DEFAULT 0,

    skills_invoked      TEXT,
    memory_entries      TEXT,
    docs_touched        TEXT,

    bei_output_score    REAL,
    bei_quality_score   REAL,
    bei_decision_score  REAL,
    bei_knowledge_score REAL,
    bei_efficiency_score REAL,
    bei_composite       REAL,

    tags                TEXT,
    notes               TEXT,
    created_at          TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS turns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    turn_index      INTEGER NOT NULL,
    role            TEXT NOT NULL,
    timestamp       TEXT NOT NULL,
    message_id      TEXT,

    input_tokens            INTEGER DEFAULT 0,
    output_tokens           INTEGER DEFAULT 0,
    cache_read_tokens       INTEGER DEFAULT 0,
    cache_creation_tokens   INTEGER DEFAULT 0,

    latency_ms      INTEGER,
    model_id        TEXT,

    UNIQUE(session_id, turn_index)
);

CREATE TABLE IF NOT EXISTS tool_calls (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    turn_index      INTEGER NOT NULL,
    tool_name       TEXT NOT NULL,
    tool_input      TEXT,
    tool_result     TEXT,
    duration_ms     INTEGER,
    success         INTEGER DEFAULT 1,
    timestamp       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS edits (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    turn_index      INTEGER NOT NULL,
    file_path       TEXT NOT NULL,
    lines_added     INTEGER DEFAULT 0,
    lines_removed   INTEGER DEFAULT 0,
    accepted        INTEGER DEFAULT 1,
    timestamp       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_summary (
    date            TEXT PRIMARY KEY,
    sessions_count  INTEGER DEFAULT 0,
    total_input_tokens      INTEGER DEFAULT 0,
    total_output_tokens     INTEGER DEFAULT 0,
    total_cost_usd_micro    INTEGER DEFAULT 0,
    lines_added             INTEGER DEFAULT 0,
    lines_removed           INTEGER DEFAULT 0,
    commits_count           INTEGER DEFAULT 0,
    avg_cache_hit_rate      REAL,
    avg_bei_composite       REAL
);

CREATE TABLE IF NOT EXISTS alert_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT,
    alert_type      TEXT NOT NULL,
    severity        TEXT NOT NULL,
    message         TEXT NOT NULL,
    context         TEXT,
    acknowledged    INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_session ON tool_calls(session_id);
CREATE INDEX IF NOT EXISTS idx_edits_session ON edits(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_name);
CREATE INDEX IF NOT EXISTS idx_turns_message_id ON turns(message_id);
CREATE INDEX IF NOT EXISTS idx_alert_log_session ON alert_log(session_id);

-- Chapter markers within a session
CREATE TABLE IF NOT EXISTS chapters (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL REFERENCES sessions(id),
    chapter_index   INTEGER NOT NULL,
    title           TEXT NOT NULL,
    summary         TEXT,
    start_turn      INTEGER NOT NULL,
    start_timestamp TEXT,
    end_turn        INTEGER,
    end_timestamp   TEXT,
    input_tokens    INTEGER DEFAULT 0,
    output_tokens   INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    tool_calls      INTEGER DEFAULT 0,
    edits           INTEGER DEFAULT 0,

    UNIQUE(session_id, chapter_index)
);

CREATE INDEX IF NOT EXISTS idx_chapters_session ON chapters(session_id);
