"""BEI (Benefit Efficiency Index) — five-dimension scoring engine."""

import sqlite3
from pathlib import Path
from typing import Optional
import yaml

from tools.token_audit.parser import SessionSnapshot, TokenUsage


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
    """Computes BEI scores for a session snapshot.

    Baselines are loaded from config.yaml as fallback, and can be
    overridden with percentile data from calibrate_baselines().
    """

    def __init__(self, config_path: str = None, db_conn: sqlite3.Connection = None,
                 cost_model=None):
        if config_path is None:
            config_path = str(Path(__file__).parent / "config.yaml")
        self.config = self._load_config(config_path)
        self.db_conn = db_conn
        self.cost_model = cost_model
        self.weights = self.config.get("bei", {}).get("weights", {
            "output": 0.30, "quality": 0.25, "decision": 0.20,
            "knowledge": 0.10, "efficiency": 0.15,
        })
        # Config hardcoded baselines — used only when no DB calibration available
        self._config_baselines = dict(self.config.get("bei", {}).get("baselines", {}))
        # DB-calibrated baselines (set via load_baselines)
        self.baselines: dict = {}

    @staticmethod
    def _load_config(path: str) -> dict:
        if Path(path).exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def load_baselines(self, calibrated: dict) -> None:
        """Load P25/P50/P75 baselines from calibrate_baselines().

        These percentile baselines replace the hardcoded config values
        for scoring normalization.
        """
        self.baselines = calibrated

    def calculate(self, snapshot: SessionSnapshot, project: str = "GCS_A") -> BEIScores:
        """Calculate all five BEI dimensions using available baselines."""
        scores = BEIScores(
            output=self._output_score(snapshot),
            quality=self._quality_score(snapshot),
            decision=self._decision_score(snapshot),
            knowledge=self._knowledge_score(snapshot),
            efficiency=self._efficiency_score(snapshot),
        )
        scores.compute_composite(self.weights)
        return scores

    # ── percentile-based normalization ──────────────────────────

    @staticmethod
    def _percentile_score(value: float, bl: dict, higher_is_better: bool = True) -> float:
        """Normalize a value to [0, 1] using P25/P50/P75 baselines.

        higher_is_better=True:  larger values → higher score (e.g. output, cache)
        higher_is_better=False: smaller values → higher score (e.g. cost, rejection)
        """
        p25 = bl.get("p25", 0)
        p50 = bl.get("p50", 0)
        p75 = bl.get("p75", 0)

        if p50 <= 0:
            return 0.5  # No usable baseline

        if higher_is_better:
            if value >= p75:
                return 0.85 + 0.15 * min((value - p75) / max(p75 - p50, 0.01), 1.0)
            elif value >= p50:
                return 0.50 + 0.35 * (value - p50) / max(p75 - p50, 0.01)
            elif value >= p25:
                return 0.15 + 0.35 * (value - p25) / max(p50 - p25, 0.01)
            else:
                return 0.15 * max(value / max(p25, 0.01), 0.0)
        else:
            if value <= p25:
                return 0.85 + 0.15 * min((p25 - value) / max(p50 - p25, 0.01), 1.0)
            elif value <= p50:
                return 0.50 + 0.35 * (p50 - value) / max(p50 - p25, 0.01)
            elif value <= p75:
                return 0.15 + 0.35 * (p75 - value) / max(p75 - p50, 0.01)
            else:
                return 0.15 * max(p75 / max(value, 0.01), 0.0)

    # ── dimension scoring ───────────────────────────────────────

    def _output_score(self, snapshot: SessionSnapshot) -> float:
        """Output dimension: LoC per 1M tokens, normalized vs P50/P75."""
        total_tokens = snapshot.tokens.total_tokens
        if total_tokens == 0:
            return 0.0
        raw = (snapshot.lines_added + snapshot.lines_removed) * 1_000_000.0 / total_tokens

        bl = self.baselines.get("output_per_1M_tokens")
        if bl and bl.get("p50", 0) > 0:
            return self._percentile_score(raw, bl, higher_is_better=True)

        # Fallback: config hardcoded baseline
        baseline = self._config_baselines.get("output_per_1M_tokens", 200)
        if baseline <= 0:
            return 0.5
        return min(raw / baseline, 1.0)

    def _quality_score(self, snapshot: SessionSnapshot) -> float:
        """Quality dimension: edit acceptance + commit message signals."""
        total_edits = snapshot.edit_accept_count + snapshot.edit_reject_count
        if total_edits == 0:
            edit_score = 0.5
        else:
            rejection_rate = snapshot.edit_reject_count / total_edits
            edit_score = max(0.0, 1.0 - rejection_rate)

        commit_score = self._commit_quality_score(snapshot)
        return edit_score * 0.5 + commit_score * 0.5

    def _commit_quality_score(self, snapshot: SessionSnapshot) -> float:
        """Score commit message quality from git data attached to snapshot."""
        commit_signals = getattr(snapshot, 'commit_signals', None)
        if not commit_signals:
            return 0.5

        total = commit_signals.get("total_commits", 0)
        if total == 0:
            return 0.3

        conventional_count = commit_signals.get("conventional_commits", 0)
        conv_rate = conventional_count / total

        semantic_count = commit_signals.get("semantic_signals", 0)
        sem_rate = min(semantic_count / total, 1.0)

        arch_count = commit_signals.get("architecture_signals", 0)
        arch_rate = min(arch_count / max(total, 1), 1.0)

        score = 0.3 + conv_rate * 0.3 + sem_rate * 0.2 + arch_rate * 0.2
        return min(score, 1.0)

    def _decision_score(self, snapshot: SessionSnapshot) -> float:
        """Decision dimension: architecture signals + doc changes."""
        score = 0.0
        if snapshot.docs_touched:
            score += 0.4
        if snapshot.memory_entries:
            score += min(len(snapshot.memory_entries) * 0.2, 0.3)
        if snapshot.skills_invoked:
            score += min(len(snapshot.skills_invoked) * 0.1, 0.3)
        return min(score, 1.0)

    def _knowledge_score(self, snapshot: SessionSnapshot) -> float:
        """Knowledge accumulation dimension — with DB-baseline-aware thresholds."""
        # Prefer DB-calibrated P90 baselines, fall back to config hardcoded values
        mem_bl = self.baselines.get("memory_entries_p90")
        skill_bl = self.baselines.get("skill_invocations_p90")

        if mem_bl and mem_bl.get("p90", 0) > 0:
            max_memory = mem_bl["p90"]
        else:
            max_memory = self._config_baselines.get("max_memory_entries", 3)

        if skill_bl and skill_bl.get("p90", 0) > 0:
            max_skill = skill_bl["p90"]
        else:
            max_skill = self._config_baselines.get("max_skill_invocations", 5)

        memory_sig = min(len(snapshot.memory_entries) / max(max_memory, 1), 1.0)
        skill_sig = min(len(snapshot.skills_invoked) / max(max_skill, 1), 1.0)
        return memory_sig * 0.4 + skill_sig * 0.6

    def _efficiency_score(self, snapshot: SessionSnapshot) -> float:
        """Efficiency dimension: cache hit rate + cost per commit.

        Uses percentile baselines when available, falls back to config values.
        """
        cache_rate = snapshot.tokens.cache_hit_rate

        # Cost per commit
        cost_micro = snapshot.cost_usd_micro
        if cost_micro == 0 and snapshot.tokens.total_tokens > 0 and self.cost_model:
            cost_micro = self.cost_model.calculate(snapshot.tokens, self.cost_model.default_model)

        if snapshot.commits_count > 0 and cost_micro > 0:
            cost_per_commit = (cost_micro / 1_000_000.0) / snapshot.commits_count
        else:
            cost_per_commit = 999.0

        # Cache hit rate score
        cache_bl = self.baselines.get("cache_hit_rate")
        if cache_bl and cache_bl.get("p50", 0) > 0:
            cache_eff = self._percentile_score(cache_rate, cache_bl, higher_is_better=True)
        else:
            ideal_cache = self._config_baselines.get("ideal_cache_hit_rate", 0.85)
            cache_eff = min(cache_rate / max(ideal_cache, 0.01), 1.0)

        # Cost per commit score
        cpc_bl = self.baselines.get("cost_per_commit")
        if cpc_bl and cpc_bl.get("p50", 0) > 0:
            cost_eff = self._percentile_score(cost_per_commit, cpc_bl, higher_is_better=False)
        else:
            ideal_cost = self._config_baselines.get("ideal_cost_per_commit_usd", 0.50)
            cost_eff = max(0.0, 1.0 - (cost_per_commit / max(ideal_cost, 0.01)))

        return cache_eff * 0.4 + cost_eff * 0.6
