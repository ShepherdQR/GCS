"""Composite indices for token economic evaluation.

Implements CI-1 through CI-4 from the unified evaluation system design.
Phase 3 of token-econ-metric-system-v2.
"""

from dataclasses import dataclass
from enum import Enum
from tools.token_audit.metrics_engine import DerivedMetrics, RawTelemetry


class WorkloadCategory(Enum):
    CODE_GEN = "code-gen"
    CODE_REVIEW = "code-review"
    ARCHITECTURE = "architecture"
    RESEARCH = "research"
    DEBUG = "debug"
    DOCS = "docs"
    OPS = "ops"
    PROCESS = "process"


# Per-workload healthy TLR ranges (min, max) for normalization
TLR_RANGES = {
    WorkloadCategory.CODE_GEN:     (0.05, 0.20),
    WorkloadCategory.CODE_REVIEW:  (0.02, 0.08),
    WorkloadCategory.ARCHITECTURE: (0.02, 0.10),
    WorkloadCategory.RESEARCH:     (0.01, 0.05),
    WorkloadCategory.DEBUG:        (0.02, 0.08),
    WorkloadCategory.DOCS:         (0.03, 0.12),
    WorkloadCategory.OPS:          (0.04, 0.15),
    WorkloadCategory.PROCESS:      (0.01, 0.05),
}

# Per-workload SCLOR healthy maximums
SCLOR_MAX = {
    WorkloadCategory.CODE_GEN:     0.12,
    WorkloadCategory.CODE_REVIEW:  0.15,
    WorkloadCategory.ARCHITECTURE: 0.15,
    WorkloadCategory.RESEARCH:     0.20,
    WorkloadCategory.DEBUG:        0.15,
    WorkloadCategory.DOCS:         0.12,
    WorkloadCategory.OPS:          0.10,
    WorkloadCategory.PROCESS:      0.10,
}

# Per-risk-level VCR target ranges (min, max)
VCR_TARGETS = {
    "low":      (0.05, 0.15),
    "medium":   (0.10, 0.25),
    "high":     (0.20, 0.50),
    "critical": (0.30, 0.80),
}

# CWAR break-even thresholds by TTL
CWAR_BREAK_EVEN = {"5min": 1.4, "1hour": 2.2}

# Default Token Health Score weights
DEFAULT_THS_WEIGHTS = {
    "cache": 0.20,
    "overhead": 0.25,
    "leverage": 0.30,
    "waste": 0.25,
}

# Task type weights for ATEI aggregation
ATEI_TYPE_WEIGHTS = {
    "bug-fix": 1.0, "feature": 0.85, "refactor": 0.90,
    "research": 0.70, "docs": 0.95, "ops": 0.90,
    "debug": 0.85, "review": 0.90, "process": 0.90,
    "design": 0.85, "": 0.85,
}

# Task type → workload category mapping
TASK_TYPE_TO_WORKLOAD = {
    "bug-fix": WorkloadCategory.CODE_GEN,
    "feature": WorkloadCategory.CODE_GEN,
    "refactor": WorkloadCategory.CODE_GEN,
    "research": WorkloadCategory.RESEARCH,
    "docs": WorkloadCategory.DOCS,
    "ops": WorkloadCategory.OPS,
    "process": WorkloadCategory.PROCESS,
    "review": WorkloadCategory.CODE_REVIEW,
    "design": WorkloadCategory.ARCHITECTURE,
    "debug": WorkloadCategory.DEBUG,
}


@dataclass
class CompositeIndices:
    """Layer 3: composite evaluation scores."""
    ths: float = 0.0              # CI-1: Token Health Score (0-100)
    cti: float = 0.0              # CI-2: Cache Trust Index (0-1)
    ser: float = 0.0              # CI-3: Session Efficiency Rating (0-1)
    atei: float = 0.0             # CI-4: Aggregate Token Economic Index (0-1)
    workload: str = ""
    cache_health_state: str = ""  # Ideal / Wasteful / Dangerous / Inefficient / Broken


class CompositeIndexEngine:
    """Computes composite indices from derived metrics."""

    def __init__(self, ths_weights: dict = None):
        self.ths_weights = ths_weights or DEFAULT_THS_WEIGHTS.copy()

    # ── workload classification ─────────────────────────────────

    @staticmethod
    def classify_workload(task_type: str, tool_call_pattern: dict = None) -> WorkloadCategory:
        """Classify session into workload category."""
        if task_type in TASK_TYPE_TO_WORKLOAD:
            return TASK_TYPE_TO_WORKLOAD[task_type]

        if tool_call_pattern:
            read_ratio = tool_call_pattern.get("read_ratio", 0)
            edit_ratio = tool_call_pattern.get("edit_ratio", 0)
            if read_ratio > 0.6 and edit_ratio < 0.1:
                return WorkloadCategory.RESEARCH
            if edit_ratio > 0.3:
                return WorkloadCategory.CODE_GEN

        return WorkloadCategory.CODE_GEN

    @staticmethod
    def classify_workload_str(task_type: str) -> str:
        """Return workload category string for a task type."""
        wc = CompositeIndexEngine.classify_workload(task_type)
        return wc.value

    # ── CI-1: Token Health Score ─────────────────────────────────

    def compute_ths(self, m: DerivedMetrics, workload: WorkloadCategory) -> float:
        """CI-1: Token Health Score (0-100)."""
        w = self.ths_weights

        tlr_min, tlr_max = TLR_RANGES.get(workload, (0.02, 0.10))
        tlr_norm = min(max((m.tlr - tlr_min) / max(tlr_max - tlr_min, 0.001), 0), 1)

        sclor_max = SCLOR_MAX.get(workload, 0.15)
        sclor_score = max(0, 1 - m.sclor / max(sclor_max, 0.001))

        cwar_capped = min(m.cwar, 10.0) if m.cwar != float('inf') else 10.0
        cwar_score = min(cwar_capped / 3.0, 1.0)

        score = 100 * (
            w["cache"] * cwar_score
            + w["overhead"] * sclor_score
            + w["leverage"] * tlr_norm
            + w["waste"] * (1 - m.twr)
        )
        return min(max(score, 0), 100)

    @staticmethod
    def ths_rating(ths: float) -> str:
        if ths >= 80: return "Healthy"
        elif ths >= 60: return "Adequate"
        elif ths >= 40: return "Concerning"
        elif ths >= 20: return "Poor"
        return "Critical"

    # ── CI-2: Cache Trust Index ──────────────────────────────────

    @staticmethod
    def compute_cti(m: DerivedMetrics, raw: RawTelemetry) -> float:
        """CI-2: Cache Trust Index (0-1).

        Three-dimensional: Efficiency × Freshness × Economics.
        Directly addresses "cache hit rate too high is not necessarily good."
        """
        ttl = raw.cache_ttl_setting or "5min"
        break_even = CWAR_BREAK_EVEN.get(ttl, 1.4)

        efficiency = m.hr_effective
        freshness = 1.0 - min(m.usr, 1.0)

        if m.cwar == float('inf'):
            economics = 1.0
        else:
            economics = min(m.cwar / break_even, 1.0)

        cti = efficiency * freshness * economics
        return min(max(cti, 0.0), 1.0)

    @staticmethod
    def cti_rating(cti: float) -> str:
        if cti >= 0.80: return "Trustworthy"
        elif cti >= 0.60: return "Cautious"
        elif cti >= 0.40: return "Suspicious"
        elif cti >= 0.20: return "Untrustworthy"
        return "Broken"

    # ── CI-3: Session Efficiency Rating ───────────────────────────

    @staticmethod
    def compute_ser(m: DerivedMetrics, raw: RawTelemetry,
                    historical_stes_median: float = None) -> float:
        """CI-3: Session Efficiency Rating (0-1)."""
        if historical_stes_median and historical_stes_median > 0:
            stes_norm = min(m.stes / historical_stes_median, 2.0) / 2.0
        else:
            stes_norm = 0.5

        risk = raw.task_risk_level or "medium"
        vcr_min, _ = VCR_TARGETS.get(risk, (0.10, 0.25))
        if m.vcr >= vcr_min:
            vcr_adequacy = 1.0
        elif m.vcr > 0:
            vcr_adequacy = m.vcr / vcr_min
        else:
            vcr_adequacy = 0.5

        staleness_penalty = 1.0 - 0.5 * min(m.usr, 1.0)
        ser = stes_norm * vcr_adequacy * staleness_penalty
        return min(max(ser, 0.0), 1.0)

    @staticmethod
    def ser_rating(ser: float) -> str:
        if ser >= 0.80: return "Excellent"
        elif ser >= 0.60: return "Good"
        elif ser >= 0.40: return "Fair"
        elif ser >= 0.20: return "Poor"
        return "Failing"

    # ── CI-4: Aggregate Token Economic Index ──────────────────────

    @staticmethod
    def compute_atei(sessions: list[dict]) -> float:
        """CI-4: Aggregate Token Economic Index (0-1).

        Each session dict needs: 'ser' (float), 'task_type' (str).
        """
        if not sessions:
            return 0.0

        weighted_sum = 0.0
        weight_sum = 0.0
        for s in sessions:
            ser = s.get("ser", 0.0)
            task_type = s.get("task_type", "")
            w = ATEI_TYPE_WEIGHTS.get(task_type, 0.85)
            weighted_sum += ser * w
            weight_sum += w

        return weighted_sum / weight_sum if weight_sum > 0 else 0.0

    # ── Cache health diagnosis ───────────────────────────────────

    @staticmethod
    def cache_health_diagnosis(m: DerivedMetrics, cti: float = None) -> str:
        """Determine cache health state from three dimensions.

        Efficiency (HR_eff) × Freshness (1-USR) × Economics (CWAR).
        """
        efficiency_ok = m.hr_effective >= 0.40
        freshness_ok = m.usr <= 0.05
        cwar_ok = m.cwar >= 1.4 if m.cwar != float('inf') else True

        if efficiency_ok and freshness_ok and cwar_ok:
            return "Ideal"
        elif efficiency_ok and freshness_ok and not cwar_ok:
            return "Wasteful"
        elif efficiency_ok and not freshness_ok:
            return "Dangerous"
        elif not efficiency_ok and freshness_ok and cwar_ok:
            return "Inefficient"
        else:
            return "Broken"

    # ── Full computation ─────────────────────────────────────────

    def compute_all(self, m: DerivedMetrics, raw: RawTelemetry,
                    historical_stes_median: float = None) -> CompositeIndices:
        """Compute all composite indices for a session."""
        workload = self.classify_workload(raw.task_type)
        cti = self.compute_cti(m, raw)

        return CompositeIndices(
            ths=self.compute_ths(m, workload),
            cti=cti,
            ser=self.compute_ser(m, raw, historical_stes_median),
            workload=workload.value,
            cache_health_state=self.cache_health_diagnosis(m, cti),
        )
