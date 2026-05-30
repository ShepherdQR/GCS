#!/usr/bin/env python3
"""Contract Compliance Pipeline — verifies module boundaries and interface contracts.

Checks:
  1. Module import boundaries — Python imports and C++ #include directives
     must not cross forbidden module boundaries.
  2. Stable ID reassignment — frozen @dataclass fields named "id" must not be
     reassigned after construction.
  3. Tolerance consistency — hardcoded tolerance values (1e-6, 1e-9, 1e-12)
     must be consistent across modules.

Usage:
  python tools/solver_testing/pipelines/contract_compliance.py --root . --checks all
  python tools/solver_testing/pipelines/contract_compliance.py --root . --checks imports,stable_ids
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class Violation:
    """A single contract-compliance violation."""

    check: str  # "imports" | "stable_ids" | "tolerance"
    severity: str  # "error" | "warning"
    file_path: str
    line: int
    message: str
    evidence: str = ""


@dataclass
class ComplianceReport:
    """Aggregate result from all compliance checks."""

    violations: List[Violation] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)

    def summary(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("CONTRACT COMPLIANCE REPORT")
        lines.append("=" * 60)
        for key, value in sorted(self.stats.items()):
            lines.append(f"  {key}: {value}")
        lines.append(f"  total_violations: {len(self.violations)}")
        if not self.violations:
            lines.append("  result: PASS")
        else:
            lines.append("  result: FAIL" if self.has_errors else "  result: WARN")
            lines.append("-" * 60)
            by_check: Dict[str, List[Violation]] = defaultdict(list)
            for v in self.violations:
                by_check[v.check].append(v)
            for check, items in sorted(by_check.items()):
                lines.append(f"\n  [{check}] ({len(items)} violations)")
                for v in items:
                    rel = os.path.relpath(v.file_path, os.getcwd()) if v.file_path else "?"
                    lines.append(f"    {v.severity:7s}  {rel}:{v.line}  {v.message}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Regex for Python import statements.
# Group 1: module in "from X import ..."
# Group 2: module(s) in "import X" or "import X, Y"
_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+(\S+?)\s+import\s+\S+|import\s+(.+))",
    re.MULTILINE,
)

# Regex for C++ #include directives.
_INCLUDE_RE = re.compile(r'^\s*#\s*include\s+[<"]([^>"]+)[>"]', re.MULTILINE)

# Tolerance patterns to scan for.
_TOLERANCE_RE = re.compile(r"\b(\d+(?:\.\d*)?[eE][+-]?\d+)\b")

# Frozen-dataclass decorator pattern.
_FROZEN_DATACLASS_RE = re.compile(
    r"@dataclass\s*\(\s*.*?\bfrozen\s*=\s*True\s*.*?\)",
    re.DOTALL,
)

# Field assignment after construction:  <expr>.id = <value>
_DOT_ID_ASSIGN_RE = re.compile(r"(\w+)\.id\s*=")


def _collect_python_files(root: str) -> List[str]:
    """Collect all .py files under *root*, ignoring __pycache__ and .git."""
    py_files: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", ".agents", "node_modules")]
        for fn in filenames:
            if fn.endswith(".py"):
                py_files.append(os.path.join(dirpath, fn))
    return py_files


def _collect_cpp_files(root: str) -> List[str]:
    """Collect all .cpp and .h files under *root*."""
    cpp_files: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "build", "out", "__pycache__")]
        for fn in filenames:
            if fn.endswith((".cpp", ".h", ".hpp", ".cxx", ".hxx")):
                cpp_files.append(os.path.join(dirpath, fn))
    return cpp_files


def _file_to_module(file_path: str, root: str) -> Optional[str]:
    """Map a filesystem path to the GCS module name used in the allowed graph.

    Returns None for files that don't belong to a tracked module.
    """
    rel = os.path.relpath(file_path, root).replace("\\", "/")

    # Python modules under tools/
    if rel.startswith("tools/scene_generation/gcs_scene_generation"):
        sub = rel[len("tools/scene_generation/gcs_scene_generation/"):]
        return _module_name("gcs_scene_generation", sub)

    if rel.startswith("tools/solver_testing"):
        sub = rel[len("tools/solver_testing/"):]
        return _module_name("solver_testing", sub)

    # gcs_viz under python/
    if rel.startswith("python/gcs_viz"):
        sub = rel[len("python/gcs_viz/"):]
        return _module_name("gcs_viz", sub)

    # Top-level tools/ scripts
    if rel.startswith("tools/") and rel.endswith(".py"):
        sub = rel[len("tools/"):]
        return _module_name("tools", sub)

    # C++ modules under src/gcs/
    if rel.startswith("src/gcs/"):
        parts = rel[len("src/gcs/"):].split("/")
        if parts:
            top = parts[0]  # e.g. kernel, io_adapters, ...
            return f"gcs_{top}"

    return None


def _module_name(top: str, sub: str) -> str:
    """Build a dotted module name from top-level package and sub-path."""
    sub = sub.removesuffix(".py").removesuffix("__init__").strip("/").strip(".")
    if sub and sub != ".":
        sub = sub.replace("/", ".")
        return f"{top}.{sub}"
    return top


def _top_level_module(module_name: str) -> str:
    """Extract the top-level package from a dotted module name."""
    return module_name.split(".")[0]


def _collapse_parenthesized(source: str) -> str:
    """Replace newlines inside parenthesized blocks with spaces so that
    multi-line import statements can be matched by single-line regex."""
    result: List[str] = []
    depth = 0
    for ch in source:
        if ch == "(":
            depth += 1
            result.append(ch)
        elif ch == ")":
            if depth > 0:
                depth -= 1
            result.append(ch)
        elif ch in ("\r", "\n"):
            if depth > 0:
                result.append(" ")  # collapse newline inside parens
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result)


def _extract_python_imports(file_path: str) -> List[str]:
    """Extract imported module names from a .py file using regex.

    Returns a list of top-level module names imported by this file.
    Handles single-line imports, multi-import ``import X, Y``, and
    parenthesized multi-line ``from X import (Y, Z)``.
    """
    try:
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            source = fh.read()
    except OSError:
        return []

    # Collapse parenthesized blocks so multi-line imports become single-line.
    collapsed = _collapse_parenthesized(source)

    imported: List[str] = []
    for m in _IMPORT_RE.finditer(collapsed):
        mod = m.group(1)  # "from X import ..." — group 1 is X
        if mod is None:
            mod = m.group(2)  # "import X, Y" — group 2 is the tail
        if mod:
            # For bare ``import X, Y``, split on commas
            parts = [p.strip().split(".")[0] for p in mod.split(",") if p.strip()]
            for p in parts:
                if p.startswith("."):
                    continue  # relative import — skip
                imported.append(p)
    return imported


def _extract_cpp_includes(file_path: str) -> List[str]:
    """Extract included module names from .cpp/.h #include directives.

    Returns a list of logical module names derived from the include path.
    """
    try:
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            source = fh.read()
    except OSError:
        return []

    imported: List[str] = []
    for m in _INCLUDE_RE.finditer(source):
        inc = m.group(1)
        # Map src/gcs include paths to module names
        if inc.startswith("gcs/"):
            part = inc[len("gcs/"):].split("/")[0]
            imported.append(f"gcs_{part}")
    return imported


def _find_dataclass_frozen_id_classes(file_path: str) -> List[str]:
    """Return names of @dataclass(frozen=True) classes that have an 'id' field."""
    try:
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            source = fh.read()
    except OSError:
        return []

    names: List[str] = []
    # Find frozen dataclass definitions
    for match in _FROZEN_DATACLASS_RE.finditer(source):
        # Find the class definition that follows this decorator
        after = source[match.end():]
        class_match = re.search(r"class\s+(\w+)", after)
        if class_match:
            class_name = class_match.group(1)
            # Check if this class has an 'id' field (simple heuristic: look
            # for 'id' type annotation in the class body)
            class_start = match.end() + class_match.end()
            # Find class body — look for next top-level class/def or EOF
            next_class = re.search(r"^\s*(?:class\s+|def\s+|@)", after[class_match.end():], re.MULTILINE)
            if next_class:
                body_end = class_start + next_class.start()
            else:
                body_end = len(source)
            class_body = source[class_start:body_end]
            if re.search(r"\bid\s*:\s*\w+", class_body):
                names.append(class_name)
    return names


def _find_id_reassignments(file_path: str, frozen_class_names: Set[str]) -> List[Tuple[int, str]]:
    """Find lines that reassign .id on objects that may be frozen dataclass instances."""
    try:
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return []

    violations: List[Tuple[int, str]] = []
    for i, line in enumerate(lines, start=1):
        for m in _DOT_ID_ASSIGN_RE.finditer(line):
            obj_name = m.group(1)
            # Skip 'self' — self.id = ... in __init__ is allowed
            if obj_name == "self":
                continue
            violations.append((i, line.strip()))
    return violations


def _extract_tolerances(file_path: str) -> List[float]:
    """Extract hardcoded floating-point tolerance values from a source file.

    Scans for numbers like 1e-6, 1.0e-9, 1E-12, etc.
    Returns only values that look like tolerances (small positive values).
    """
    try:
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            source = fh.read()
    except OSError:
        return []

    values: List[float] = []
    for m in _TOLERANCE_RE.finditer(source):
        try:
            val = float(m.group(1))
        except ValueError:
            continue
        # Only collect small values that look like tolerances
        if val > 0 and val < 1.0:
            values.append(val)
    return values


# ---------------------------------------------------------------------------
# ContractCompliancePipeline
# ---------------------------------------------------------------------------


class ContractCompliancePipeline:
    """Verifies module boundaries and interface contracts across the GCS codebase."""

    # ------------------------------------------------------------------
    # 1. Module import boundary check
    # ------------------------------------------------------------------

    @staticmethod
    def check_module_imports(
        root_path: str,
        allowed_graph: Optional[Dict[str, Set[str]]] = None,
    ) -> List[Violation]:
        """Scan .py and .cpp/.h files, compare actual imports against *allowed_graph*.

        *allowed_graph* is a dict mapping top-level module name -> set of allowed
        top-level import names.  If None, ``build_allowed_graph()`` is used.
        """
        if allowed_graph is None:
            allowed_graph = ContractCompliancePipeline.build_allowed_graph()

        violations: List[Violation] = []

        # Python files
        for py_file in _collect_python_files(root_path):
            module = _file_to_module(py_file, root_path)
            if module is None:
                continue
            top = _top_level_module(module)
            allowed = allowed_graph.get(top, set())
            imports = _extract_python_imports(py_file)
            for imp in imports:
                if imp == top:
                    continue  # self-import is always ok
                if imp.startswith("_"):
                    continue  # private / stdlib-ish
                if imp not in allowed:
                    violations.append(Violation(
                        check="imports",
                        severity="error",
                        file_path=py_file,
                        line=0,
                        message=f"Module '{top}' imports '{imp}' which is not in allowed set: {sorted(allowed)}",
                        evidence=f"import {imp}",
                    ))

        # C++ files
        for cpp_file in _collect_cpp_files(root_path):
            module = _file_to_module(cpp_file, root_path)
            if module is None:
                continue
            top = _top_level_module(module)
            allowed = allowed_graph.get(top, set())
            includes = _extract_cpp_includes(cpp_file)
            for inc in includes:
                if inc == top:
                    continue
                if inc not in allowed:
                    violations.append(Violation(
                        check="imports",
                        severity="error",
                        file_path=cpp_file,
                        line=0,
                        message=f"C++ module '{top}' includes '{inc}' which is not in allowed set: {sorted(allowed)}",
                        evidence=f"#include ... {inc}",
                    ))

        return violations

    # ------------------------------------------------------------------
    # 2. Allowed dependency graph
    # ------------------------------------------------------------------

    @staticmethod
    def build_allowed_graph() -> Dict[str, Set[str]]:
        """Return the hardcoded GCS allowed dependency graph.

        Top-level module -> set of allowed top-level import targets.
        """
        return {
            # gcs_scene_generation may import from its own submodules only
            "gcs_scene_generation": {"gcs_scene_generation"},

            # solver_testing may import from its own submodules + gcs_scene_generation
            "solver_testing": {"solver_testing", "gcs_scene_generation"},

            # gcs_viz may import from gcs_viz only
            "gcs_viz": {"gcs_viz"},

            # tools may import from gcs_scene_generation, solver_testing
            "tools": {"gcs_scene_generation", "solver_testing"},

            # C++ modules — each may import its own sub-area
            "gcs_kernel": {"gcs_kernel"},
            "gcs_io_adapters": {"gcs_kernel", "gcs_io_adapters"},
            "gcs_incidence_graph": {"gcs_kernel", "gcs_incidence_graph"},
            "gcs_constraint_catalog": {"gcs_kernel", "gcs_constraint_catalog"},
            "gcs_numeric_engine": {"gcs_kernel", "gcs_numeric_engine"},
            "gcs_diagnostics": {"gcs_kernel", "gcs_numeric_engine", "gcs_diagnostics"},
            "gcs_decomposition_planner": {
                "gcs_kernel",
                "gcs_incidence_graph",
                "gcs_decomposition_planner",
            },
            "gcs_session_runtime": {
                "gcs_kernel",
                "gcs_io_adapters",
                "gcs_diagnostics",
                "gcs_session_runtime",
            },
            "gcs_viewer_bridge": {"gcs_kernel", "gcs_viewer_bridge"},
            "gcs_tools": {"gcs_kernel", "gcs_tools"},
        }

    # ------------------------------------------------------------------
    # 3. Stable ID check
    # ------------------------------------------------------------------

    @staticmethod
    def check_stable_ids(paths: Optional[List[str]] = None) -> List[Violation]:
        """Scan .py files for 'id' field reassignment on frozen @dataclass instances.

        If *paths* is None, scans the repo root (current working directory).
        """
        root = os.getcwd()
        py_files = _collect_python_files(root)

        # Step A: collect all frozen-dataclass names that have an 'id' field
        frozen_id_classes: Set[str] = set()
        for py_file in py_files:
            frozen_id_classes.update(_find_dataclass_frozen_id_classes(py_file))

        if not frozen_id_classes:
            return []

        # Step B: scan for .id = reassignments
        violations: List[Violation] = []
        for py_file in py_files:
            reassignments = _find_id_reassignments(py_file, frozen_id_classes)
            for line_no, line_text in reassignments:
                violations.append(Violation(
                    check="stable_ids",
                    severity="warning",
                    file_path=py_file,
                    line=line_no,
                    message=f"Potential reassignment of 'id' on what may be a frozen dataclass instance. "
                            f"Frozen classes with id field: {sorted(frozen_id_classes)}",
                    evidence=line_text,
                ))

        return violations

    # ------------------------------------------------------------------
    # 4. Tolerance consistency check
    # ------------------------------------------------------------------

    # Recognized tolerance values and their semantic labels.
    TOLERANCE_LABELS: Dict[float, str] = {
        1e-6:  "FINE (1e-6)",
        1e-7:  "FINE (1e-7)",
        1e-8:  "MEDIUM (1e-8)",
        1e-9:  "MEDIUM (1e-9)",
        1e-10: "COARSE (1e-10)",
        1e-11: "COARSE (1e-11)",
        1e-12: "COARSE (1e-12)",
    }

    # Canonical tolerance value the project should converge on.
    CANONICAL_TOLERANCE: float = 1e-9

    @classmethod
    def check_tolerance_consistency(cls, paths: Optional[List[str]] = None) -> List[Violation]:
        """Scan .py and C++ files for hardcoded tolerance values.

        Flags files that use a tolerance different from the canonical default.
        """
        root = os.getcwd()
        py_files = _collect_python_files(root)
        cpp_files = _collect_cpp_files(root)

        all_files = py_files + cpp_files
        violations: List[Violation] = []
        module_tolerances: Dict[str, Set[float]] = defaultdict(set)

        for file_path in all_files:
            tolerances = _extract_tolerances(file_path)
            module = _file_to_module(file_path, root)
            if module is None:
                continue
            top = _top_level_module(module)
            for t in tolerances:
                module_tolerances[top].add(t)

        # Check each module's tolerances against canonical
        for top_mod, tols in sorted(module_tolerances.items()):
            non_canonical = [t for t in tols if t != cls.CANONICAL_TOLERANCE]
            if non_canonical:
                # Find representative files
                for file_path in all_files:
                    fmod = _file_to_module(file_path, root)
                    if fmod and _top_level_module(fmod) == top_mod:
                        f_tols = _extract_tolerances(file_path)
                        bad = [t for t in f_tols if t != cls.CANONICAL_TOLERANCE]
                        for t in bad:
                            label = cls.TOLERANCE_LABELS.get(t, f"{t:.0e}")
                            violations.append(Violation(
                                check="tolerance",
                                severity="warning",
                                file_path=file_path,
                                line=0,
                                message=f"Module '{top_mod}' uses tolerance {t} ({label}); "
                                        f"canonical is {cls.CANONICAL_TOLERANCE}",
                                evidence=f"tolerance = {t}",
                            ))
                        break  # one representative per module

        return violations

    # ------------------------------------------------------------------
    # 5. run — orchestrate all checks
    # ------------------------------------------------------------------

    @classmethod
    def run(cls, root_path: str, checks: Optional[Set[str]] = None) -> ComplianceReport:
        """Run all (or selected) compliance checks and return a ``ComplianceReport``.

        *checks* can be a set of check names: ``{"imports", "stable_ids", "tolerance"}``.
        When None or empty, all checks are executed.
        """
        if checks is None:
            checks = {"imports", "stable_ids", "tolerance"}

        report = ComplianceReport()
        stats: Dict[str, int] = {
            "python_files_scanned": 0,
            "cpp_files_scanned": 0,
            "import_violations": 0,
            "stable_id_violations": 0,
            "tolerance_violations": 0,
        }

        allowed_graph = cls.build_allowed_graph()

        # ---- imports ----
        if "imports" in checks:
            py_files = _collect_python_files(root_path)
            cpp_files = _collect_cpp_files(root_path)
            stats["python_files_scanned"] = len(py_files)
            stats["cpp_files_scanned"] = len(cpp_files)
            import_violations = cls.check_module_imports(root_path, allowed_graph)
            stats["import_violations"] = len(import_violations)
            report.violations.extend(import_violations)

        # ---- stable_ids ----
        if "stable_ids" in checks:
            if stats["python_files_scanned"] == 0:
                stats["python_files_scanned"] = len(_collect_python_files(root_path))
            sid_violations = cls.check_stable_ids()
            stats["stable_id_violations"] = len(sid_violations)
            report.violations.extend(sid_violations)

        # ---- tolerance ----
        if "tolerance" in checks:
            if stats["python_files_scanned"] == 0:
                stats["python_files_scanned"] = len(_collect_python_files(root_path))
            if stats["cpp_files_scanned"] == 0:
                stats["cpp_files_scanned"] = len(_collect_cpp_files(root_path))
            tol_violations = cls.check_tolerance_consistency()
            stats["tolerance_violations"] = len(tol_violations)
            report.violations.extend(tol_violations)

        report.stats = stats
        return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Contract Compliance Pipeline — verify module boundaries and interface contracts.",
    )
    parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Repository root directory (default: cwd)",
    )
    parser.add_argument(
        "--checks",
        default="all",
        help="Comma-separated check names: imports,stable_ids,tolerance, or 'all' (default: all)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable text",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)

    if args.checks == "all":
        checks = {"imports", "stable_ids", "tolerance"}
    else:
        checks = {c.strip() for c in args.checks.split(",") if c.strip()}

    valid = {"imports", "stable_ids", "tolerance"}
    unknown = checks - valid
    if unknown:
        print(f"ERROR: Unknown check(s): {unknown}. Valid: {sorted(valid)}", file=sys.stderr)
        sys.exit(2)

    report = ContractCompliancePipeline.run(root, checks)

    if getattr(args, "json", False):
        import json

        output = {
            "stats": report.stats,
            "violations": [
                {
                    "check": v.check,
                    "severity": v.severity,
                    "file_path": v.file_path,
                    "line": v.line,
                    "message": v.message,
                    "evidence": v.evidence,
                }
                for v in report.violations
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(report.summary())

    if report.has_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
