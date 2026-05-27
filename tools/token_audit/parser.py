"""JSONL transcript parser for Claude Code sessions."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class TokenUsage:
    """Token usage for a single LLM response."""
    __slots__ = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_creation_tokens")

    def __init__(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_read_tokens: int = 0,
        cache_creation_tokens: int = 0,
    ):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cache_read_tokens = cache_read_tokens
        self.cache_creation_tokens = cache_creation_tokens

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cache_hit_rate(self) -> float:
        denom = self.cache_read_tokens + self.input_tokens
        return self.cache_read_tokens / denom if denom > 0 else 0.0

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_read_tokens=self.cache_read_tokens + other.cache_read_tokens,
            cache_creation_tokens=self.cache_creation_tokens + other.cache_creation_tokens,
        )

    def __iadd__(self, other: "TokenUsage") -> "TokenUsage":
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.cache_read_tokens += other.cache_read_tokens
        self.cache_creation_tokens += other.cache_creation_tokens
        return self


class ToolCall:
    """A single tool invocation."""
    __slots__ = ("name", "tool_use_id", "input_data", "result", "timestamp")

    def __init__(self, name: str, tool_use_id: str = "", input_data: dict = None,
                 result: str = "", timestamp: str = ""):
        self.name = name
        self.tool_use_id = tool_use_id
        self.input_data = input_data or {}
        self.result = result
        self.timestamp = timestamp


class EditRecord:
    """A file edit operation."""
    __slots__ = ("file_path", "lines_added", "lines_removed", "accepted", "timestamp")

    def __init__(self, file_path: str = "", lines_added: int = 0,
                 lines_removed: int = 0, accepted: bool = True, timestamp: str = ""):
        self.file_path = file_path
        self.lines_added = lines_added
        self.lines_removed = lines_removed
        self.accepted = accepted
        self.timestamp = timestamp


class SessionSnapshot:
    """Accumulated session state."""

    def __init__(self, session_id: str = "", project_name: str = "",
                 started_at: str = ""):
        self.session_id = session_id
        self.project_name = project_name
        self.started_at = started_at
        self.ended_at: str = ""
        self.model_id: str = ""
        self.tokens = TokenUsage()
        self.cost_usd_micro: int = 0
        self.lines_added: int = 0
        self.lines_removed: int = 0
        self.files_touched: int = 0
        self.commits_count: int = 0
        self.commit_signals: dict = {}  # {total_commits, conventional_commits, semantic_signals, architecture_signals}
        self.edit_accept_count: int = 0
        self.edit_reject_count: int = 0
        self.tool_calls_total: int = 0
        self.subagent_spawns: int = 0
        self.skills_invoked: list = []
        self.memory_entries: list = []
        self.docs_touched: list = []
        self.turn_count: int = 0
        self.record_count: int = 0


class IncrementalJSONLParser:
    """Incremental reader for a JSONL transcript file."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.offset: int = 0
        self.session_id: Optional[str] = None
        self.project_name: str = "unknown"
        self._seen_message_ids: set = set()
        self._tool_use_queue: dict = {}  # tool_use_id -> ToolCall (pending result)

    def reset(self) -> None:
        """Reset parser state for a new session."""
        self.offset = 0
        self.session_id = None
        self._seen_message_ids.clear()
        self._tool_use_queue.clear()

    def read_new_records(self) -> list[dict]:
        """Read records added since last call. Returns list of parsed JSON dicts."""
        if not self.path.exists():
            return []

        try:
            size = self.path.stat().st_size
        except OSError:
            return []

        if size < self.offset:
            self.offset = 0
            self._seen_message_ids.clear()

        records = []
        with open(self.path, "r", encoding="utf-8") as f:
            f.seek(self.offset)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            self.offset = f.tell()

        return records

    # ── Static extraction helpers ──────────────────────────────

    @staticmethod
    def extract_usage(record: dict) -> Optional[TokenUsage]:
        """Extract token usage from an assistant record. Deduplicates by message.id."""
        if record.get("type") != "assistant":
            return None
        msg = record.get("message", {})
        usage = msg.get("usage", {})
        if not usage:
            return None
        return TokenUsage(
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            cache_read_tokens=usage.get("cache_read_input_tokens", 0),
            cache_creation_tokens=usage.get("cache_creation_input_tokens", 0),
        )

    @staticmethod
    def is_new_message(record: dict, seen_ids: set) -> bool:
        """Check if this record is the first occurrence of a message.id."""
        msg = record.get("message", {})
        msg_id = msg.get("id", "")
        if not msg_id:
            return True  # No message ID — treat as new to be safe
        if msg_id in seen_ids:
            return False
        seen_ids.add(msg_id)
        return True

    @staticmethod
    def extract_model(record: dict) -> str:
        """Extract model ID from a record."""
        return record.get("message", {}).get("model", "")

    @staticmethod
    def extract_tool_uses(record: dict) -> list[ToolCall]:
        """Extract tool_use blocks from a record."""
        tools = []
        content = record.get("message", {}).get("content", [])
        if not isinstance(content, list):
            return tools
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                tc = ToolCall(
                    name=block.get("name", "unknown"),
                    tool_use_id=block.get("id", ""),
                    input_data=block.get("input", {}),
                    timestamp=record.get("timestamp", ""),
                )
                tools.append(tc)
        return tools

    @staticmethod
    def extract_tool_results(record: dict) -> list[dict]:
        """Extract tool_result blocks from a user record."""
        results = []
        content = record.get("message", {}).get("content", [])
        if not isinstance(content, list):
            return results
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                results.append({
                    "tool_use_id": block.get("tool_use_id", ""),
                    "content": block.get("content", ""),
                })
        return results

    @staticmethod
    def get_timestamps(records: list[dict]) -> tuple[str, str]:
        """Get start and end timestamps from a list of records."""
        timestamps = [
            r["timestamp"] for r in records
            if r.get("timestamp") and r.get("type") in ("user", "assistant")
        ]
        if not timestamps:
            return "", ""
        return timestamps[0], timestamps[-1]

    @staticmethod
    def get_session_id(records: list[dict]) -> str:
        """Extract session ID from records."""
        for r in records:
            sid = r.get("sessionId", "")
            if sid:
                return sid
        return ""

    @staticmethod
    def get_project_name(records: list[dict]) -> str:
        """Infer project name from cwd."""
        for r in records:
            cwd = r.get("cwd", "")
            if cwd:
                return Path(cwd).name
        return "unknown"

    @staticmethod
    def get_git_branch(records: list[dict]) -> str:
        """Extract git branch from records."""
        for r in records:
            branch = r.get("gitBranch", "")
            if branch:
                return branch
        return ""

    @staticmethod
    def is_subagent_spawn(tool_call: ToolCall) -> bool:
        """Check if a tool call spawns a subagent."""
        return tool_call.name in ("Agent", "Task")

    @staticmethod
    def is_skill_invocation(tool_call: ToolCall) -> bool:
        """Check if a tool call invokes a skill."""
        return tool_call.name == "Skill"

    @staticmethod
    def is_edit_tool(tool_call: ToolCall) -> bool:
        """Check if a tool call is a file edit operation."""
        return tool_call.name in ("Edit", "Write", "NotebookEdit")

    @staticmethod
    def is_chapter_marker(tool_call: ToolCall) -> bool:
        """Check if a tool call is a CCD session chapter marker."""
        return tool_call.name == "mcp__ccd_session__mark_chapter"

    @staticmethod
    def extract_chapter_info(tool_call: ToolCall) -> dict:
        """Extract chapter title and summary from a mark_chapter tool call."""
        return {
            "title": tool_call.input_data.get("title", "Untitled"),
            "summary": tool_call.input_data.get("summary", ""),
        }
