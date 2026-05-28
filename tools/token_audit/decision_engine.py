"""Decision rule engine for token economic evaluation.

Implements D1-D7 from the unified evaluation system design.
Phase 4 of token-econ-metric-system-v2.
"""

from dataclasses import dataclass, field
from enum import Enum
from tools.token_audit.metrics_engine import DerivedMetrics, RawTelemetry
from tools.token_audit.composite_indices import (
    CompositeIndices, VCR_TARGETS, CWAR_BREAK_EVEN,
)


class RuleSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DecisionAlert:
    rule_id: str
    severity: RuleSeverity
    message: str
    session_id: str = ""
    fix_suggestion: str = ""


class DecisionEngine:
    """Evaluates D1-D7 decision rules against session metrics."""

    def evaluate(self, m: DerivedMetrics, ci: CompositeIndices,
                 raw: RawTelemetry, historical: dict = None) -> list[DecisionAlert]:
        """Evaluate all decision rules. Returns triggered alerts."""
        alerts = []
        sid = getattr(raw, 'session_id', '')

        alerts.extend(self._d1_cache_deception(m, ci, raw, sid))
        alerts.extend(self._d2_context_bloat(m, raw, sid))
        alerts.extend(self._d3_verification_gap(m, raw, sid))
        alerts.extend(self._d4_cold_load_dominance(m, raw, sid))
        alerts.extend(self._d5_write_premium_loss(m, raw, sid))
        alerts.extend(self._d6_atei_decline(historical, sid))
        alerts.extend(self._d7_task_cost_anomaly(raw, historical, sid))

        return alerts

    # ── D1: Cache Deception ──────────────────────────────────────

    @staticmethod
    def _d1_cache_deception(m, ci, raw, sid) -> list[DecisionAlert]:
        """High raw hit rate but low cache trust."""
        if m.hr_raw > 0.90 and ci.cti < 0.50:
            return [DecisionAlert(
                rule_id="D1",
                severity=RuleSeverity.CRITICAL,
                message=f"Cache deception: HR_raw={m.hr_raw:.1%} but CTI={ci.cti:.2f}. "
                        f"Cache may be losing money or serving stale data.",
                session_id=sid,
                fix_suggestion="Check TTL mismatch, dynamic content in cache blocks, "
                               "or stale file references.",
            )]
        return []

    # ── D2: Context Bloat ────────────────────────────────────────

    @staticmethod
    def _d2_context_bloat(m, raw, sid) -> list[DecisionAlert]:
        """Context grew 10x+ but output per input token is very low."""
        if m.cgr > 10 and m.tlr < 0.02:
            return [DecisionAlert(
                rule_id="D2",
                severity=RuleSeverity.WARNING,
                message=f"Context bloat: CGR={m.cgr:.1f}x, TLR={m.tlr:.4f}. "
                        f"Context grew but output per input token is very low.",
                session_id=sid,
                fix_suggestion="Consider context compaction or starting a fresh session.",
            )]
        return []

    # ── D3: Verification Gap ─────────────────────────────────────

    @staticmethod
    def _d3_verification_gap(m, raw, sid) -> list[DecisionAlert]:
        """Verification tokens below half of risk-appropriate target."""
        risk = raw.task_risk_level or "medium"
        vcr_min, _ = VCR_TARGETS.get(risk, (0.10, 0.25))
        if m.vcr < vcr_min * 0.5 and m.vcr >= 0:
            severity = RuleSeverity.CRITICAL if risk in ("high", "critical") else RuleSeverity.WARNING
            return [DecisionAlert(
                rule_id="D3",
                severity=severity,
                message=f"Verification gap: VCR={m.vcr:.3f} below {vcr_min * 0.5:.3f} "
                        f"(50% of target for {risk}-risk tasks).",
                session_id=sid,
                fix_suggestion=f"Risk level is {risk}; increase verification "
                               f"(tests, linting, review) to at least VCR={vcr_min:.2f}.",
            )]
        return []

    # ── D4: Cold-Load Dominance ──────────────────────────────────

    @staticmethod
    def _d4_cold_load_dominance(m, raw, sid) -> list[DecisionAlert]:
        """Overhead dominates input in very short sessions."""
        if m.sclor > 0.25 and raw.turn_count < 5:
            return [DecisionAlert(
                rule_id="D4",
                severity=RuleSeverity.INFO,
                message=f"Cold-load dominance: {m.sclor:.0%} of input is fixed overhead "
                        f"in a {raw.turn_count}-turn session.",
                session_id=sid,
                fix_suggestion="Consider whether this task needed a full agentic session, "
                               "or could be done in a simpler mode.",
            )]
        return []

    # ── D5: Write-Premium Loss ───────────────────────────────────

    @staticmethod
    def _d5_write_premium_loss(m, raw, sid) -> list[DecisionAlert]:
        """CWAR below break-even for the TTL setting."""
        if m.cwar == float('inf') or m.cwar == 0.0:
            return []
        ttl = raw.cache_ttl_setting or "5min"
        break_even = CWAR_BREAK_EVEN.get(ttl, 1.4)
        if m.cwar < break_even:
            severity = RuleSeverity.CRITICAL if m.cwar < 1.0 else RuleSeverity.WARNING
            return [DecisionAlert(
                rule_id="D5",
                severity=severity,
                message=f"Write-premium loss: CWAR={m.cwar:.1f} below {ttl} "
                        f"break-even ({break_even}).",
                session_id=sid,
                fix_suggestion=f"Consider switching to {'1hour' if ttl == '5min' else '5min'} "
                               f"TTL, or batching sessions to increase cache reuse.",
            )]
        return []

    # ── D6: ATEI Decline ─────────────────────────────────────────

    @staticmethod
    def _d6_atei_decline(historical, sid) -> list[DecisionAlert]:
        """7-day ATEI dropped >15% below 14-day baseline."""
        if not historical:
            return []
        atei_7d = historical.get("atei_7d", 0)
        atei_14d = historical.get("atei_14d", 0)
        if atei_14d > 0 and atei_7d < atei_14d * 0.85:
            drop_pct = (1 - atei_7d / atei_14d) * 100
            return [DecisionAlert(
                rule_id="D6",
                severity=RuleSeverity.WARNING,
                message=f"ATEI decline: 7d ATEI={atei_7d:.2f} dropped {drop_pct:.0f}% "
                        f"below 14d baseline ({atei_14d:.2f}).",
                session_id=sid,
                fix_suggestion="Review recent changes to skill/agent definitions, "
                               "tool configurations, or workload patterns.",
            )]
        return []

    # ── D7: Task Cost Anomaly ────────────────────────────────────

    @staticmethod
    def _d7_task_cost_anomaly(raw, historical, sid) -> list[DecisionAlert]:
        """Task type cost 50%+ above historical average."""
        if not historical:
            return []
        task_type = raw.task_type
        if not task_type:
            return []
        current_cpct = historical.get("cpct_current", 0)
        historical_cpct = historical.get(f"cpct_{task_type}", 0)
        if historical_cpct > 0 and current_cpct > historical_cpct * 1.5:
            ratio = current_cpct / historical_cpct
            return [DecisionAlert(
                rule_id="D7",
                severity=RuleSeverity.WARNING,
                message=f"Task cost anomaly: {task_type} CPCT=${current_cpct:.2f} "
                        f"is {ratio:.1f}x historical (${historical_cpct:.2f}).",
                session_id=sid,
                fix_suggestion="Review recent sessions of this type for common "
                               "inefficiency patterns.",
            )]
        return []
