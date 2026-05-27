"""BEI (Benefit Efficiency Index) — five-dimension scoring engine."""

import sqlite3
from pathlib import Path
from typing import Optional
import yaml

from tools.token_audit.parser import SessionSnapshot, TokenUsage
from tools.token_audit.db import get_project_baseline


class BEIScores:
    """Five-dimension benefit scores."""

    __slots__ = ("output", "quality", "decision", "knowledge", "efficiency", "composite")

    def __init__(self, output: float = 0.0, quality: float = 0.0,
                 decision: float = 0.0, knowledge: float = 0.0,
                 efficiency: float = 0.0):
        self.output = max(0.0, min(1.0, output))
        self.quality = max(0.0, min(1.0, quality))
        self.decision = max(0.0, min(1.0, decision))
        self.knowledge = max(0.0, min(1.0, knowledge))
        self.efficiency = max(0.0, min(1.0, efficiency))
        self.composite = 0.0

    def compute_composite(self, weights: dict) -> float:
        """Compute weighted composite score."""
        w = weights
        self.composite = (
            self.output * w.get("output", 0.30)
            + self.quality * w.get("quality", 0.25)
            + self.decision * w.get("decision", 0.20)
            + self.knowledge * w.get("knowledge", 0.10)
            + self.efficiency * w.get("efficiency", 0.15)
        )
        return self.composite

    @staticmethod
    def rating(composite: float) -> str:
        if composite >= 0.80:
            return "A (高效)"
        elif composite >= 0.60:
            return "B (良好)"
        elif composite >= 0.40:
            return "C (一般)"
        elif composite >= 0.20:
            return "D (低效)"
        return "E (极低效)"


class BEIEngine:
    """Computes BEI scores for a session snapshot."""

    def __init__(self, config_path: str = None, db_conn: sqlite3.Connection = None):
        if config_path is None:
            config_path = str(Path(__file__).parent / "config.yaml")
        self.config = self._load_config(config_path)
        self.db_conn = db_conn
        self.weights = self.config.get("bei", {}).get("weights", {
            "output": 0.30, "quality": 0.25, "decision": 0.20,
            "knowledge": 0.10, "efficiency": 0.15,
        })
        self.baselines = self.config.get("bei", {}).get("baselines", {})

    @staticmethod
    def _load_config(path: str) -> dict:
        if Path(path).exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def calculate(self, snapshot: SessionSnapshot, project: str = "GCS_A") -> BEIScores:
        """Calculate all five BEI dimensions."""
        scores = BEIScores(
            output=self._output_score(snapshot, project),
            quality=self._quality_score(snapshot),
            decision=self._decision_score(snapshot),
            knowledge=self._knowledge_score(snapshot),
            efficiency=self._efficiency_score(snapshot, project),
        )
        scores.compute_composite(self.weights)
        return scores

    def _output_score(self, snapshot: SessionSnapshot, project: str) -> float:
        """Output dimension: LoC per 1M tokens."""
        total_tokens = snapshot.tokens.total_tokens
        if total_tokens == 0:
            return 0.0
        raw = (snapshot.lines_added + snapshot.lines_removed) * 1_000_000.0 / total_tokens

        baseline = self.baselines.get("output_per_1M_tokens", 200)
        if self.db_conn:
            hist = get_project_baseline(self.db_conn, project, "output_per_1M_tokens")
            if hist is not None and hist > 0:
                baseline = hist

        if baseline <= 0:
            return 0.5  # Neutral if no baseline
        return min(raw / baseline, 1.0)

    def _quality_score(self, snapshot: SessionSnapshot) -> float:
        """Quality dimension: 1 - edit rejection rate."""
        total_edits = snapshot.edit_accept_count + snapshot.edit_reject_count
        if total_edits == 0:
            return 0.5  # Neutral — no edit data
        rejection_rate = snapshot.edit_reject_count / total_edits
        return max(0.0, 1.0 - rejection_rate)

    def _decision_score(self, snapshot: SessionSnapshot) -> float:
        """Decision dimension: architecture signals + doc changes."""
        score = 0.0

        # Document changes signal
        if snapshot.docs_touched:
            score += 0.4

        # Memory entries signal
        if snapshot.memory_entries:
            score += min(len(snapshot.memory_entries) * 0.2, 0.3)

        # Skill invocations signal
        if snapshot.skills_invoked:
            score += min(len(snapshot.skills_invoked) * 0.1, 0.3)

        return min(score, 1.0)

    def _knowledge_score(self, snapshot: SessionSnapshot) -> float:
        """Knowledge accumulation dimension."""
        max_memory = self.baselines.get("max_memory_entries", 3)
        max_skill = self.baselines.get("max_skill_invocations", 5)

        memory_sig = min(len(snapshot.memory_entries) / max(max_memory, 1), 1.0)
        skill_sig = min(len(snapshot.skills_invoked) / max(max_skill, 1), 1.0)
        return memory_sig * 0.4 + skill_sig * 0.6

    def _efficiency_score(self, snapshot: SessionSnapshot, project: str) -> float:
        """Efficiency dimension: cache hit rate + cost per commit."""
        cache_rate = snapshot.tokens.cache_hit_rate

        # Cost per commit
        if snapshot.commits_count > 0 and snapshot.cost_usd_micro > 0:
            cost_per_commit = (snapshot.cost_usd_micro / 1_000_000.0) / snapshot.commits_count
        else:
            cost_per_commit = 999.0  # No commits — worst score

        ideal_cost = self.baselines.get("ideal_cost_per_commit_usd", 0.50)
        cost_eff = max(0.0, 1.0 - (cost_per_commit / max(ideal_cost, 0.01)))

        return cache_rate * 0.4 + cost_eff * 0.6
