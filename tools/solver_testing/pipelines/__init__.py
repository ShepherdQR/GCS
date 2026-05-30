"""Pipeline classes for solver testing workflows."""

from .benchmark import BenchmarkPipeline, BenchmarkPoint, BenchmarkReport, TrendDB
from .contract_compliance import ContractCompliancePipeline, ComplianceReport, Violation
from .cross_solver_compare import CrossSolverComparePipeline, ComparisonPoint, ComparisonReport, ExternalSolverSpec
from .defect_discovery import DefectDiscoveryPipeline, PipelineResult
from .diagnostics_cert import CertReport, CertResult, DiagnosticsCertPipeline
from .regression import Regression, RegressionPipeline
from .repo_audit import AuditReport, FileClassification, RepoAuditPipeline, RepoSnapshot
from .roundtrip import FixtureRoundTripResult, RoundTripPipeline, RoundTripReport, RoundTripResult, SolveCompareResult
from .scene_gen import CoverageSpec, Gap, SceneGenPipeline, SceneGenReport
from .stability import StabilityAnalysis, StabilityPipeline, StabilityPoint, StabilityResult

__all__ = [
    # benchmark
    "BenchmarkPipeline", "BenchmarkPoint", "BenchmarkReport", "TrendDB",
    # contract_compliance
    "ComplianceReport", "ContractCompliancePipeline", "Violation",
    # cross_solver_compare
    "ComparisonPoint", "ComparisonReport", "CrossSolverComparePipeline", "ExternalSolverSpec",
    # defect_discovery
    "DefectDiscoveryPipeline", "PipelineResult",
    # diagnostics_cert
    "CertReport", "CertResult", "DiagnosticsCertPipeline",
    # regression
    "Regression", "RegressionPipeline",
    # repo_audit
    "AuditReport", "FileClassification", "RepoAuditPipeline", "RepoSnapshot",
    # roundtrip
    "RoundTripPipeline", "RoundTripReport", "RoundTripResult",
    # scene_gen
    "CoverageSpec", "Gap", "SceneGenPipeline", "SceneGenReport",
    # stability
    "StabilityAnalysis", "StabilityPipeline", "StabilityPoint", "StabilityResult",
]
