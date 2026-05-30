"""Solver testing tools — mutation, batch execution, defect storage, analysis."""

from .analyzer import RepairResult, analyze_and_repair_defects, analyze_defect, apply_repair, verify_repair
from .defect_store import DefectRecord, DefectStore, SolveResult, classify_defect, make_defect_id
from .mutator import MUTATION_STRATEGIES, Mutation, mutate_constraint_values
from .runner import batch_solve, find_solver

__all__ = [
    "DefectRecord",
    "DefectStore",
    "MUTATION_STRATEGIES",
    "Mutation",
    "RepairResult",
    "SolveResult",
    "analyze_and_repair_defects",
    "analyze_defect",
    "apply_repair",
    "batch_solve",
    "classify_defect",
    "find_solver",
    "make_defect_id",
    "mutate_constraint_values",
    "verify_repair",
]
