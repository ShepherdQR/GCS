"""Git data linker — correlates session time windows with git activity."""

import subprocess
from datetime import datetime, timezone, timedelta
from typing import Optional


class GitLinker:
    """Link AI session activity to git changes."""

    def __init__(self, repo_path: str = ".", window_padding_minutes: int = 2):
        self.repo_path = repo_path
        self.window_padding = timedelta(minutes=window_padding_minutes)

    def _run(self, args: list[str]) -> str:
        """Run a git command and return stdout."""
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path] + args,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""

    @staticmethod
    def _normalize_dt(dt: datetime) -> datetime:
        """Convert a datetime to a naive UTC datetime for git comparison.

        Git log dates are in local time without timezone markers.
        We convert aware datetimes to UTC then strip tzinfo so comparisons
        against git output (parsed as naive local) are consistent.
        """
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt

    def get_commits_in_window(
        self, start: datetime, end: datetime
    ) -> list[dict]:
        """Get commits between two timestamps with configurable padding."""
        start = self._normalize_dt(start) - self.window_padding
        end = self._normalize_dt(end) + self.window_padding

        start_str = start.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end.strftime("%Y-%m-%dT%H:%M:%S")

        output = self._run([
            "log",
            f"--after={start_str}",
            f"--before={end_str}",
            "--format=%H|%s|%ai|%an",
            "--no-merges",
        ])
        if not output:
            return []

        commits = []
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 3)
            if len(parts) >= 4:
                commits.append({
                    "hash": parts[0],
                    "message": parts[1],
                    "date": parts[2],
                    "author": parts[3],
                })
        return commits

    def get_diff_stats(
        self, start: datetime, end: datetime
    ) -> dict:
        """Get diff statistics between two timestamps using commit range."""
        commits = self.get_commits_in_window(start, end)
        if not commits:
            return {"lines_added": 0, "lines_removed": 0, "files_changed": 0}

        first = commits[-1]["hash"]
        last = commits[0]["hash"]

        stat_output = self._run([
            "diff", "--stat",
            f"{first}~1..{last}",
        ])
        if not stat_output:
            return {"lines_added": 0, "lines_removed": 0, "files_changed": 0}

        return self._parse_diff_stat(stat_output)

    def get_diff_between(
        self, start_ref: str, end_ref: str
    ) -> dict:
        """Get diff stats between two git refs."""
        stat_output = self._run([
            "diff", "--stat", f"{start_ref}..{end_ref}",
        ])
        return self._parse_diff_stat(stat_output)

    def get_session_diff(
        self, start: datetime, end: datetime
    ) -> dict:
        """Get diff stats for changes made during the session time window.

        Uses a multi-strategy approach:
        1. Try reflog-based HEAD position matching with padded window
        2. Fall back to commit-based diff if reflog yields no match
        3. Fall back to wider reflog search if narrow window fails
        """
        start = self._normalize_dt(start)
        end = self._normalize_dt(end)
        padded_start = start - self.window_padding
        padded_end = end + self.window_padding

        # Strategy 1: reflog-based matching
        reflog = self._run([
            "reflog",
            "--format=%H|%gd|%ai",
            "-n", "100",
        ])
        if reflog:
            result = self._match_reflog(reflog, padded_start, padded_end)
            if result and (result["lines_added"] > 0 or result["files_changed"] > 0):
                return result

        # Strategy 2: commit-based diff with padded window
        result = self.get_diff_stats(padded_start, padded_end)
        if result["lines_added"] > 0 or result["files_changed"] > 0:
            return result

        # Strategy 3: wider window (10 min padding) as last resort
        wide_start = start - timedelta(minutes=10)
        wide_end = end + timedelta(minutes=10)
        return self.get_diff_stats(wide_start, wide_end)

    def _match_reflog(
        self, reflog: str, start: datetime, end: datetime
    ) -> Optional[dict]:
        """Find HEAD positions bracketing the session window from reflog."""
        entries = []
        for line in reflog.split("\n"):
            parts = line.split("|")
            if len(parts) < 3:
                continue
            try:
                ref_dt = datetime.strptime(parts[2].strip()[:19], "%Y-%m-%d %H:%M:%S")
                entries.append((parts[0].strip(), ref_dt))
            except ValueError:
                continue

        if not entries:
            return None

        before_ref = None
        after_ref = None
        for commit_hash, ref_dt in entries:
            if ref_dt <= start and before_ref is None:
                before_ref = commit_hash
            if ref_dt >= end:
                after_ref = commit_hash

        if not before_ref or not after_ref:
            # Use earliest and latest matching entries we can find
            before_ref = entries[-1][0]  # oldest in reflog
            after_ref = entries[0][0]    # newest in reflog

        if before_ref == after_ref:
            return None

        stat_output = self._run([
            "diff", "--stat", f"{before_ref}..{after_ref}",
        ])
        return self._parse_diff_stat(stat_output)

    def get_session_output(self, start: datetime, end: datetime) -> dict:
        """Get complete session output: commits, diff stats, and decision signals."""
        commits = self.get_commits_in_window(start, end)
        diff = self.get_session_diff(start, end)
        decisions = self.extract_decision_signals(commits)

        return {
            "commits": commits,
            "commits_count": len(commits),
            "lines_added": diff["lines_added"],
            "lines_removed": diff["lines_removed"],
            "files_changed": diff["files_changed"],
            "decision_signals": decisions,
        }

    @staticmethod
    def _parse_diff_stat(stat_output: str) -> dict:
        """Parse `git diff --stat` output."""
        if not stat_output:
            return {"lines_added": 0, "lines_removed": 0, "files_changed": 0}

        lines = stat_output.strip().split("\n")
        summary = lines[-1] if lines else ""
        files_changed = 0
        lines_added = 0
        lines_removed = 0

        parts = summary.split(",")
        for p in parts:
            p = p.strip()
            if "file" in p and "changed" in p:
                try:
                    files_changed = int(p.split()[0])
                except (ValueError, IndexError):
                    pass
            elif "insertion" in p:
                try:
                    lines_added = int(p.split()[0])
                except (ValueError, IndexError):
                    pass
            elif "deletion" in p:
                try:
                    lines_removed = int(p.split()[0])
                except (ValueError, IndexError):
                    pass

        return {
            "lines_added": lines_added,
            "lines_removed": lines_removed,
            "files_changed": files_changed,
        }

    def extract_decision_signals(self, commits: list[dict]) -> dict:
        """Extract architecture/design decision signals from commit messages.

        Returns:
            total_commits, conventional_commits, semantic_signals,
            architecture_signals, signal_ratio
        """
        arch_keywords = {
            "architecture", "architectural", "design", "refactor", "extract",
            "introduce", "module", "boundary", "contract", "interface",
            "separate", "pattern", "abstract", "decouple", "restructure",
            "reorganize", "rename", "migrate", "consolidate", "split",
            "pipeline", "layer", "adapter", "bridge", "facade",
        }
        semantic_keywords = {
            "fix", "bug", "patch", "hotfix",
            "feat", "feature", "add", "implement",
            "refactor", "cleanup", "simplify",
            "perf", "performance", "optimize", "speed",
            "test", "testing", "verify",
            "docs", "document", "readme",
            "chore", "build", "ci", "cd", "release",
            "style", "format", "lint",
        }

        signal_count = 0
        semantic_count = 0
        conventional_count = 0

        for c in commits:
            msg_lower = c["message"].lower()

            # Conventional commit detection: type(scope): desc or type: desc
            msg_stripped = c["message"].strip()
            if ":" in msg_stripped:
                prefix = msg_stripped.split(":", 1)[0].strip()
                if " " not in prefix or ("(" in prefix and ")" in prefix):
                    conventional_count += 1

            # Architecture keywords
            for kw in arch_keywords:
                if kw in msg_lower:
                    signal_count += 1
                    break

            # Semantic keywords
            for kw in semantic_keywords:
                if kw in msg_lower:
                    semantic_count += 1
                    break

        return {
            "total_commits": len(commits),
            "conventional_commits": conventional_count,
            "semantic_signals": semantic_count,
            "architecture_signals": signal_count,
            "signal_ratio": signal_count / max(len(commits), 1),
        }
