"""Real-time session tracker — monitors active Claude Code sessions."""

import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from tools.token_audit.parser import (
    IncrementalJSONLParser, SessionSnapshot, TokenUsage,
    ToolCall, EditRecord,
)
from tools.token_audit.cost_model import CostModel
from tools.token_audit.alerts import AlertEngine, Alert
from tools.token_audit.db import (
    insert_session, update_session, close_session,
    insert_turn, insert_tool_call, insert_edit, insert_alert,
    upsert_daily_summary,
)


class SessionTracker:
    """Monitors an active Claude Code session via its JSONL transcript."""

    def __init__(
        self,
        project_name: str = "GCS_A",
        db_conn: sqlite3.Connection = None,
        alert_engine: AlertEngine = None,
        cost_model: CostModel = None,
    ):
        self.project_name = project_name
        self.db_conn = db_conn
        self.alert_engine = alert_engine or AlertEngine()
        self.cost_model = cost_model or CostModel()
        self.parser: Optional[IncrementalJSONLParser] = None
        self.snapshot: Optional[SessionSnapshot] = None
        self._running = False
        self._last_activity = time.time()
        self._turn_index = 0
        self._seen_message_ids: set = set()
        self._recent_tools: list[ToolCall] = []  # For agent loop detection
        self._cost_ticks: list[tuple[float, int]] = []  # [(elapsed_seconds, cost_micro)] for burn rate

    def find_active_session(self) -> Optional[str]:
        """Find the currently active JSONL transcript."""
        projects_dir = Path.home() / ".claude" / "projects"

        # Strategy 1: Environment variable
        env_path = os.environ.get("CLAUDE_CODE_SESSION_PATH")
        if env_path and Path(env_path).exists():
            return env_path

        if not projects_dir.exists():
            return None

        # Strategy 2: Most recently modified JSONL
        best_path = None
        best_mtime = 0
        cutoff = time.time() - 120  # Modified within last 2 minutes

        for proj_dir in projects_dir.iterdir():
            if not proj_dir.is_dir():
                continue
            for f in proj_dir.glob("*.jsonl"):
                try:
                    mtime = f.stat().st_mtime
                    if mtime > best_mtime:
                        best_mtime = mtime
                        best_path = str(f)
                except OSError:
                    continue

        if best_path and best_mtime >= cutoff:
            return best_path
        return best_path  # Return even if stale — may be the only session

    def start_tracking(self, jsonl_path: str) -> SessionSnapshot:
        """Start tracking a session from its JSONL path."""
        self.parser = IncrementalJSONLParser(jsonl_path)
        self.snapshot = SessionSnapshot()
        self._running = True
        self._last_activity = time.time()
        self._turn_index = 0
        self._seen_message_ids = set()
        self._recent_tools = []

        # Read all existing records to build initial state
        records = self.parser.read_new_records()
        self._process_records(records)

        # Extract metadata
        if records:
            self.snapshot.session_id = IncrementalJSONLParser.get_session_id(records)
            self.snapshot.project_name = IncrementalJSONLParser.get_project_name(records) or self.project_name
            start, _ = IncrementalJSONLParser.get_timestamps(records)
            self.snapshot.started_at = start

        return self.snapshot

    def tick(self) -> Optional[SessionSnapshot]:
        """Read new records and update state. Call periodically."""
        if not self._running or not self.parser:
            return None

        records = self.parser.read_new_records()
        if records:
            self._last_activity = time.time()
            self._process_records(records)

        return self.snapshot

    def _process_records(self, records: list[dict]) -> None:
        """Process a batch of records into the snapshot."""
        snap = self.snapshot
        if not snap:
            return

        for record in records:
            rtype = record.get("type", "")
            snap.record_count += 1

            if rtype == "assistant":
                self._process_assistant(record)
            elif rtype == "user":
                self._process_user(record)

        # Update ended_at from last record timestamp
        if records:
            last_ts = records[-1].get("timestamp", "")
            if last_ts:
                snap.ended_at = last_ts

    def _process_assistant(self, record: dict) -> None:
        """Process an assistant record."""
        snap = self.snapshot
        parser = self.parser

        # Track model
        model = IncrementalJSONLParser.extract_model(record)
        if model and not snap.model_id:
            snap.model_id = model

        # Track token usage (deduplicate by message.id)
        is_new = IncrementalJSONLParser.is_new_message(record, self._seen_message_ids)
        if is_new:
            usage = IncrementalJSONLParser.extract_usage(record)
            if usage:
                snap.tokens += usage
                # Add cost
                model_id = model or snap.model_id or "claude-sonnet-4-6"
                snap.cost_usd_micro += self.cost_model.calculate(usage, model_id)
                # Record tick for burn rate: (unix_timestamp, cumulative_cost_micro)
                self._cost_ticks.append((time.time(), snap.cost_usd_micro))
                if len(self._cost_ticks) > 20:
                    self._cost_ticks = self._cost_ticks[-20:]
                snap.turn_count += 1
                self._turn_index += 1

        # Track tool calls
        tool_uses = IncrementalJSONLParser.extract_tool_uses(record)
        for tc in tool_uses:
            snap.tool_calls_total += 1
            self._recent_tools.append(tc)
            if IncrementalJSONLParser.is_subagent_spawn(tc):
                snap.subagent_spawns += 1
            if IncrementalJSONLParser.is_skill_invocation(tc):
                skill_name = tc.input_data.get("skill", "") if tc.input_data else ""
                if skill_name and skill_name not in snap.skills_invoked:
                    snap.skills_invoked.append(skill_name)
            if IncrementalJSONLParser.is_edit_tool(tc):
                file_path = tc.input_data.get("file_path", "") if tc.input_data else ""
                snap.files_touched += 1

    def _process_user(self, record: dict) -> None:
        """Process a user record (may contain tool results)."""
        snap = self.snapshot

        # Look for document changes / memory mentions
        content = record.get("message", {}).get("content", "")
        if isinstance(content, str):
            if ".claude/memory" in content or "MEMORY.md" in content:
                if content not in snap.memory_entries:
                    snap.memory_entries.append(content[:200])
            if "docs/" in content and ".md" in content:
                if content not in snap.docs_touched:
                    snap.docs_touched.append(content[:200])

    def is_active(self) -> bool:
        """Check if the session appears to still be active."""
        if not self._running:
            return False
        idle_timeout = 120  # seconds
        return (time.time() - self._last_activity) < idle_timeout

    def stop_tracking(self) -> SessionSnapshot:
        """Stop tracking and finalize the session."""
        self._running = False
        if self.snapshot:
            self.snapshot.ended_at = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        return self.snapshot

    def flush_to_db(self) -> str:
        """Persist the current snapshot to the database."""
        if not self.snapshot or not self.db_conn:
            return ""

        snap = self.snapshot
        session_data = {
            "id": snap.session_id,
            "project_name": snap.project_name,
            "jsonl_path": str(self.parser.path) if self.parser else "",
            "model_id": snap.model_id,
            "started_at": snap.started_at,
            "ended_at": snap.ended_at,
            "total_input_tokens": snap.tokens.input_tokens,
            "total_output_tokens": snap.tokens.output_tokens,
            "total_cache_read_tokens": snap.tokens.cache_read_tokens,
            "total_cache_creation_tokens": snap.tokens.cache_creation_tokens,
            "lines_added": snap.lines_added,
            "lines_removed": snap.lines_removed,
            "files_touched": snap.files_touched,
            "commits_count": snap.commits_count,
            "edit_accept_count": snap.edit_accept_count,
            "edit_reject_count": snap.edit_reject_count,
            "tool_calls_total": snap.tool_calls_total,
            "subagent_spawns": snap.subagent_spawns,
            "skills_invoked": __import__("json").dumps(snap.skills_invoked),
            "memory_entries": __import__("json").dumps(snap.memory_entries),
            "docs_touched": __import__("json").dumps(snap.docs_touched),
        }
        return insert_session(self.db_conn, session_data)

    def flush_alerts(self, alerts: list[Alert]) -> None:
        """Persist alerts to the database."""
        if not self.db_conn:
            return
        for alert in alerts:
            insert_alert(self.db_conn, alert.to_dict())
