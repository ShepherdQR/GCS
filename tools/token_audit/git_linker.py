"""Git data linker — correlates session time windows with git activity."""

import subprocess
from datetime import datetime
from typing import Optional


class GitLinker:
    """Link AI session activity to git changes."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

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

    def get_commits_in_window(
        self, start: datetime, end: datetime
    ) -> list[dict]:
        """Get commits between two timestamps."""
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
        """Get diff statistics between two timestamps using reflog."""
        start_str = start.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end.strftime("%Y-%m-%dT%H:%M:%S")

        # Try to find commits in the window
        commits = self.get_commits_in_window(start, end)
        if not commits:
            return {"lines_added": 0, "lines_removed": 0, "files_changed": 0}

        # Get diff between first and last commit's parents
        first = commits[-1]["hash"]
        last = commits[0]["hash"]

        # diff between parent of first and last
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
        """Get diff stats for changes made during the session time window."""
        # Use reflog to find HEAD position at start time
        start_str = start.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end.strftime("%Y-%m-%dT%H:%M:%S")

        # Try HEAD@{...} based on time
        # First, find the closest reflog entry before start
        reflog = self._run([
            "reflog",
            "--format=%H|%gd|%ai",
            "-n", "50",
        ])
        if not reflog:
            return self.get_diff_stats(start, end)

        before_ref = "HEAD"
        after_ref = "HEAD"
        for line in reflog.split("\n"):
            parts = line.split("|")
            if len(parts) < 3:
                continue
            ref_date = parts[2].strip()
            try:
                ref_dt = datetime.strptime(ref_date[:19], "%Y-%m-%d %H:%M:%S")
                if ref_dt <= start and before_ref == "HEAD":
                    before_ref = parts[0].strip()
                if ref_dt <= end and after_ref == "HEAD":
                    after_ref = parts[0].strip()
            except ValueError:
                continue

        if before_ref == after_ref:
            return {"lines_added": 0, "lines_removed": 0, "files_changed": 0}

        stat_output = self._run([
            "diff", "--stat", f"{before_ref}..{after_ref}",
        ])
        return self._parse_diff_stat(stat_output)

    @staticmethod
    def _parse_diff_stat(stat_output: str) -> dict:
        """Parse `git diff --stat` output."""
        if not stat_output:
            return {"lines_added": 0, "lines_removed": 0, "files_changed": 0}

        lines = stat_output.strip().split("\n")
        # Last line is summary: "X files changed, Y insertions(+), Z deletions(-)"
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
        """Extract architecture/design decision signals from commit messages."""
        keywords = {
            "architecture", "architectural", "design", "refactor", "extract",
            "introduce", "module", "boundary", "contract", "interface",
            "separate", "pattern", "abstract", "decouple", "restructure",
            "reorganize", "rename", "migrate", "consolidate", "split",
            "pipeline", "layer", "adapter", "bridge", "facade",
        }

        signal_count = 0
        for c in commits:
            msg_lower = c["message"].lower()
            for kw in keywords:
                if kw in msg_lower:
                    signal_count += 1
                    break

        return {
            "total_commits": len(commits),
            "architecture_signals": signal_count,
            "signal_ratio": signal_count / max(len(commits), 1),
        }
