"""Defect record storage and query.

Defects are stored as JSON files under tools/solver_testing/.defects/
Each defect captures: original scene + values, mutation applied,
original solver result, mutated solver result, and classification.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field

from .mutator import Mutation
from .runner import SolveResult


@dataclass
class DefectRecord:
    defect_id: str
    scene_id: str
    original_values: dict[str, float]  # {constraint_id: value}
    mutated_values: dict[str, float]   # {constraint_id: value}
    mutation_strategies: list[str]
    original_result: dict | None  # serialized SolveResult
    mutated_result: dict | None   # serialized SolveResult
    error_type: str = ""
    severity: str = "unknown"  # "crash", "wrong_result", "diagnostic_only"
    enumeration_id: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DefectRecord":
        return cls(**{k: data.get(k) for k in cls.__dataclass_fields__})


class DefectStore:
    """JSON-file-based defect record storage."""

    def __init__(self, store_dir: str | None = None):
        if store_dir is None:
            store_dir = os.path.join(os.path.dirname(__file__), ".defects")
        self.store_dir = os.path.abspath(store_dir)
        os.makedirs(self.store_dir, exist_ok=True)

    def _path(self, defect_id: str) -> str:
        return os.path.join(self.store_dir, f"{defect_id}.json")

    def save(self, record: DefectRecord) -> str:
        path = self._path(record.defect_id)
        data = record.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True, default=str)
            f.write("\n")
        return path

    def load(self, defect_id: str) -> DefectRecord:
        path = self._path(defect_id)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Defect '{defect_id}' not found")
        with open(path, "r", encoding="utf-8") as f:
            return DefectRecord.from_dict(json.load(f))

    def list_all(self) -> list[dict]:
        results = []
        for fname in sorted(os.listdir(self.store_dir)):
            if fname.endswith(".json"):
                with open(os.path.join(self.store_dir, fname), "r", encoding="utf-8") as f:
                    results.append(json.load(f))
        return results

    def query(self, severity: str | None = None, error_type: str | None = None) -> list[DefectRecord]:
        records = []
        for entry in self.list_all():
            rec = DefectRecord.from_dict(entry)
            if severity and rec.severity != severity:
                continue
            if error_type and rec.error_type != error_type:
                continue
            records.append(rec)
        return records

    def summary(self) -> dict:
        all_records = self.list_all()
        by_severity = {}
        by_error = {}
        for r in all_records:
            sev = r.get("severity", "unknown")
            err = r.get("error_type", "unknown")
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_error[err] = by_error.get(err, 0) + 1
        return {
            "total_defects": len(all_records),
            "by_severity": by_severity,
            "by_error_type": by_error,
        }


def make_defect_id(enumeration_id: str, scene_id: str, mutation_index: int) -> str:
    ts = int(time.time() * 1000) % 1000000
    return f"DEF-{enumeration_id}-{scene_id}-m{mutation_index:03d}-{ts:06d}"


def classify_defect(original: SolveResult, mutated: SolveResult) -> tuple[str, str]:
    """Classify defect severity and error type from result pair."""
    if mutated.status == "crash":
        return "crash", "solver_crash"
    if mutated.status == "timeout":
        return "crash", "solver_timeout"

    if original.status == "solved" and mutated.status == "failed":
        if "negative" in mutated.stderr.lower() or "distance" in mutated.stderr.lower():
            return "wrong_result", "negative_distance"
        if "angle" in mutated.stderr.lower():
            return "wrong_result", "invalid_angle_range"
        if "degenerate" in mutated.stderr.lower():
            return "wrong_result", "degenerate_geometry"
        return "wrong_result", "solver_failed"

    if original.status == "solved" and mutated.status == "solved":
        orig_has_diag = original.diagnostics_present
        mut_has_diag = mutated.diagnostics_present
        if orig_has_diag and not mut_has_diag:
            return "diagnostic_only", "diagnostics_lost"
        if not orig_has_diag and mut_has_diag:
            return "diagnostic_only", "diagnostics_appeared"

    return "unknown", "unknown"
