"""Alert engine for session monitoring."""

import json
import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional
import yaml

from tools.token_audit.parser import SessionSnapshot, ToolCall


class AlertType(Enum):
    COST_SPIKE = "cost_spike"
    EFFICIENCY_DROP = "efficiency_drop"
    CACHE_DROP = "cache_drop"
    REJECTION_SPIKE = "rejection_spike"
    AGENT_LOOP = "agent_loop"
    # v2 token economic evaluation alert types
    CACHE_DECEPTION = "cache_deception"
    CONTEXT_BLOAT = "context_bloat"
    VERIFICATION_GAP = "verification_gap"
    COLD_LOAD_DOMINANCE = "cold_load_dominance"
    WRITE_PREMIUM_LOSS = "write_premium_loss"
    ATEI_DECLINE = "atei_decline"
    TASK_COST_ANOMALY = "task_cost_anomaly"


class AlertSeverity(Enum):
    WARNING = "warning"
    CRITICAL = "critical"


class Alert:
    __slots__ = ("alert_type", "severity", "message", "session_id", "context")

    def __init__(self, alert_type: AlertType, severity: AlertSeverity,
                 message: str, session_id: str = "", context: dict = None):
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.session_id = session_id
        self.context = context or {}

    def to_dict(self) -> dict:
        return {
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "session_id": self.session_id,
            "context": json.dumps(self.context) if self.context else None,
        }


class AlertEngine:
    """Evaluates alert rules against session state."""

    def __init__(self, config_path: str = None, db_conn: sqlite3.Connection = None,
                 cost_model=None):
        if config_path is None:
            config_path = str(Path(__file__).parent / "config.yaml")
        cfg = self._load_config(config_path)
        self.alert_config = cfg.get("alerts", {})
        self.db_conn = db_conn
        self.cost_model = cost_model

        # Cooldown tracking: (alert_type_value, session_id) -> last_fire_time
        self._cooldowns: dict[tuple, datetime] = {}

    @staticmethod
    def _load_config(path: str) -> dict:
        if Path(path).exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _in_cooldown(self, alert_type: AlertType, session_id: str) -> bool:
        """Check if alert is in cooldown period."""
        key = (alert_type.value, session_id)
        now = datetime.utcnow()
        if key in self._cooldowns:
            elapsed = (now - self._cooldowns[key]).total_seconds()
            cooldown_sec = self.alert_config.get("cooldown", {}).get("per_30min", 1800)
            if elapsed < cooldown_sec:
                return True
        self._cooldowns[key] = now
        return False

    def evaluate(self, snapshot: SessionSnapshot, history: list = None,
                 cost_ticks: list = None) -> list[Alert]:
        """Evaluate all alert rules against current snapshot. Returns triggered alerts."""
        alerts = []
        sid = snapshot.session_id

        # Cost spike
        alerts.extend(self._check_cost_spike(snapshot, sid))

        # Burn rate prediction
        if cost_ticks and len(cost_ticks) >= 5:
            alerts.extend(self._check_burn_rate(snapshot, cost_ticks, sid))

        # Efficiency drop (only after enough data)
        if snapshot.turn_count >= 5:
            alerts.extend(self._check_efficiency_drop(snapshot, sid))
            alerts.extend(self._check_cache_drop(snapshot, sid))

        # Rejection spike
        total_edits = snapshot.edit_accept_count + snapshot.edit_reject_count
        if total_edits >= 5:
            alerts.extend(self._check_rejection_spike(snapshot, sid))

        return alerts

    def _check_cost_spike(self, snapshot: SessionSnapshot, sid: str) -> list[Alert]:
        """Check if session cost exceeds thresholds."""
        alerts = []
        max_cost = self.alert_config.get("max_cost_per_session_usd", 2.00)

        cost_micro = snapshot.cost_usd_micro
        if cost_micro == 0 and snapshot.tokens.total_tokens > 0 and self.cost_model:
            cost_micro = self.cost_model.calculate(snapshot.tokens, self.cost_model.default_model)

        cost_usd = cost_micro / 1_000_000.0

        if cost_usd > max_cost * 2:
            if not self._in_cooldown(AlertType.COST_SPIKE, sid):
                alerts.append(Alert(
                    AlertType.COST_SPIKE, AlertSeverity.CRITICAL,
                    f"Session cost ${cost_usd:.2f} exceeds 2x budget (${max_cost:.2f})",
                    sid, {"cost_usd": cost_usd, "threshold": max_cost * 2},
                ))
        elif cost_usd > max_cost:
            if not self._in_cooldown(AlertType.COST_SPIKE, sid):
                alerts.append(Alert(
                    AlertType.COST_SPIKE, AlertSeverity.WARNING,
                    f"Session cost ${cost_usd:.2f} exceeds budget (${max_cost:.2f})",
                    sid, {"cost_usd": cost_usd, "threshold": max_cost},
                ))
        return alerts

    def _check_burn_rate(self, snapshot: SessionSnapshot, ticks: list, sid: str) -> list[Alert]:
        """Predict budget exceedance from cost/time slope (linear regression).

        ticks: list of (unix_timestamp, cumulative_cost_micro) from tracker.
        """
        if len(ticks) < 5:
            return []

        # Linear regression on last N ticks
        n = len(ticks)
        t0 = ticks[0][0]
        sum_t = 0.0
        sum_c = 0.0
        sum_tt = 0.0
        sum_tc = 0.0
        for ts, cost_micro in ticks:
            t = (ts - t0) / 60.0  # minutes since first tick
            c = cost_micro / 1_000_000.0  # USD
            sum_t += t
            sum_c += c
            sum_tt += t * t
            sum_tc += t * c

        denom = n * sum_tt - sum_t * sum_t
        if abs(denom) < 1e-9:
            return []
        slope = (n * sum_tc - sum_t * sum_c) / denom  # USD/minute

        if slope <= 0:
            return []  # Cost not increasing

        current_cost = ticks[-1][1] / 1_000_000.0
        budget = self.alert_config.get("budgets", {}).get("per_session_usd", 2.00)
        remaining = budget - current_cost
        if remaining <= 0:
            return [Alert(
                AlertType.COST_SPIKE, AlertSeverity.CRITICAL,
                f"Session cost ${current_cost:.2f} has exceeded budget ${budget:.2f}",
                sid, {"cost_usd": current_cost, "budget": budget},
            )]

        minutes_to_budget = remaining / slope
        warn_min = self.alert_config.get("burn_rate", {}).get("warning_minutes", 30)
        crit_min = self.alert_config.get("burn_rate", {}).get("critical_minutes", 10)

        alerts = []
        if minutes_to_budget < crit_min:
            alerts.append(Alert(
                AlertType.COST_SPIKE, AlertSeverity.CRITICAL,
                f"Burn rate ${slope*60:.2f}/hr — budget exceeded in {minutes_to_budget:.0f}m",
                sid, {"burn_rate_hourly": slope * 60, "minutes_to_budget": minutes_to_budget},
            ))
        elif minutes_to_budget < warn_min:
            alerts.append(Alert(
                AlertType.COST_SPIKE, AlertSeverity.WARNING,
                f"Burn rate ${slope*60:.2f}/hr — on track to exceed budget in {minutes_to_budget:.0f}m",
                sid, {"burn_rate_hourly": slope * 60, "minutes_to_budget": minutes_to_budget},
            ))
        return alerts

    def _check_efficiency_drop(self, snapshot: SessionSnapshot, sid: str) -> list[Alert]:
        """Check for significant output-per-token drop."""
        alerts = []
        total_tokens = snapshot.tokens.total_tokens
        if total_tokens == 0:
            return alerts

        current = (snapshot.lines_added + snapshot.lines_removed) / total_tokens

        # Need historical baseline from DB
        if not self.db_conn:
            return alerts

        # Get 7-day average from daily_summary
        row = self.db_conn.execute(
            """SELECT AVG(CAST(lines_added + lines_removed AS REAL)
               / NULLIF(total_input_tokens + total_output_tokens, 0))
               FROM daily_summary
               WHERE date >= date('now', '-7 days')"""
        ).fetchone()
        if not row or not row[0] or row[0] == 0:
            return alerts

        baseline = row[0]
        threshold = self.alert_config.get("efficiency_drop_threshold", 0.5)
        if current < baseline * threshold:
            if not self._in_cooldown(AlertType.EFFICIENCY_DROP, sid):
                drop_pct = (1 - current / baseline) * 100
                alerts.append(Alert(
                    AlertType.EFFICIENCY_DROP, AlertSeverity.CRITICAL,
                    f"Output-per-token dropped {drop_pct:.0f}% vs 7-day average",
                    sid, {"current": current, "baseline": baseline},
                ))
        elif current < baseline * 0.7:
            if not self._in_cooldown(AlertType.EFFICIENCY_DROP, sid):
                drop_pct = (1 - current / baseline) * 100
                alerts.append(Alert(
                    AlertType.EFFICIENCY_DROP, AlertSeverity.WARNING,
                    f"Output-per-token declining ({drop_pct:.0f}% below average)",
                    sid, {"current": current, "baseline": baseline},
                ))
        return alerts

    def _check_cache_drop(self, snapshot: SessionSnapshot, sid: str) -> list[Alert]:
        """Check for cache hit rate decline."""
        alerts = []
        current = snapshot.tokens.cache_hit_rate
        if current == 0.0 and snapshot.tokens.input_tokens < 1000:
            return alerts  # Too early

        if not self.db_conn:
            return alerts

        row = self.db_conn.execute(
            "SELECT AVG(avg_cache_hit_rate) FROM daily_summary WHERE date >= date('now', '-7 days')"
        ).fetchone()
        if not row or not row[0] or row[0] == 0:
            return alerts

        baseline = row[0]
        threshold = self.alert_config.get("cache_drop_threshold", 0.7)
        if current < baseline * threshold:
            if not self._in_cooldown(AlertType.CACHE_DROP, sid):
                drop_pct = (1 - current / max(baseline, 0.01)) * 100
                alerts.append(Alert(
                    AlertType.CACHE_DROP, AlertSeverity.WARNING,
                    f"Cache hit rate dropped to {current:.0%} (7d avg: {baseline:.0%})",
                    sid, {"current": current, "baseline": baseline},
                ))
        return alerts

    def _check_rejection_spike(self, snapshot: SessionSnapshot, sid: str) -> list[Alert]:
        """Check for high edit rejection rate."""
        alerts = []
        total = snapshot.edit_accept_count + snapshot.edit_reject_count
        if total == 0:
            return alerts

        rate = snapshot.edit_reject_count / total
        threshold = self.alert_config.get("rejection_rate_threshold", 0.40)
        if rate > threshold:
            if not self._in_cooldown(AlertType.REJECTION_SPIKE, sid):
                alerts.append(Alert(
                    AlertType.REJECTION_SPIKE, AlertSeverity.WARNING,
                    f"Edit rejection rate {rate:.0%} exceeds threshold ({threshold:.0%})",
                    sid, {"rate": rate, "threshold": threshold},
                ))
        return alerts

    def check_agent_loop(self, recent_tools: list[ToolCall], sid: str) -> list[Alert]:
        """Detect agent loops: same tool + similar input repeated."""
        alerts = []
        if len(recent_tools) < self.alert_config.get("agent_loop_min_repetition", 3):
            return alerts

        # Group by tool name
        by_name: dict[str, list[ToolCall]] = {}
        for tc in recent_tools:
            by_name.setdefault(tc.name, []).append(tc)

        window = self.alert_config.get("agent_loop_window_minutes", 10)
        for name, calls in by_name.items():
            if len(calls) < 3:
                continue
            # Check if last 3 calls are within the window and have similar input
            recent = calls[-3:]
            if len(recent) < 3:
                continue
            try:
                t0 = datetime.fromisoformat(recent[0].timestamp.replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(recent[2].timestamp.replace("Z", "+00:00"))
                if (t2 - t0).total_seconds() / 60 > window:
                    continue
            except (ValueError, TypeError):
                continue

            # Compare input similarity (simple JSON string comparison)
            inputs = [json.dumps(c.input_data, sort_keys=True) for c in recent]
            if len(set(inputs)) == 1:
                if not self._in_cooldown(AlertType.AGENT_LOOP, sid):
                    alerts.append(Alert(
                        AlertType.AGENT_LOOP, AlertSeverity.CRITICAL,
                        f"Agent loop detected: {name} called 3+ times with identical input",
                        sid, {"tool": name, "count": len(calls)},
                    ))
        return alerts
