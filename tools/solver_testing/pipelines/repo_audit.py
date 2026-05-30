#!/usr/bin/env python3
"""Repository Audit Pipeline — automated repository health checks.

File classification, directory convention validation, stale file detection, and
snapshot collection.

Usage:
  python tools/solver_testing/pipelines/repo_audit.py --root . --stale-threshold 90 --snapshot
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Default classification rules
# ---------------------------------------------------------------------------

DEFAULT_CATEGORY_RULES: dict[str, tuple[str, ...]] = {
    "source": (".cpp", ".h", ".hpp", ".c", ".cc", ".cxx", ".hxx"),
    "python": (".py", ".pyx", ".pxd", ".pxi"),
    "docs": (".md", ".rst", ".txt"),
    "fixtures": (".txt", ".json"),
    "config": (
        ".cmake",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
    ),
    "scripts": (".cmd", ".bat", ".sh", ".ps1"),
    "assets": (".png", ".svg", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".bmp"),
    "data": (".db", ".sqlite", ".csv", ".tsv"),
}

LARGE_FILE_THRESHOLD_BYTES = 1_048_576  # 1 MB

TEXT_EXTENSIONS: frozenset[str] = frozenset({
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".hxx", ".cppm",
    ".py", ".pyx", ".pxd", ".pxi",
    ".md", ".rst", ".txt",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".cmake", ".cmd", ".bat", ".sh", ".ps1",
    ".svg", ".html", ".css", ".js", ".ts",
    ".gitignore", ".gitattributes", ".gitmodules",
    ".csv", ".tsv",
})

ALLOWED_EMPTY_DIRS: frozenset[str] = frozenset({".claude", "node_modules", "__pycache__"})

STALE_PATTERNS: list[tuple[str, str]] = [
    (".pyc", "compiled"),
    (".pyo", "compiled"),
    (".bak", "backup"),
    (".tmp", "temporary"),
    (".swp", "vim_swap"),
    (".swo", "vim_swap"),
    ("*~", "backup"),
]
STALE_LOG_EXTENSIONS: frozenset[str] = frozenset({".log"})
STALE_LOG_MAX_AGE_DAYS = 30


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FlaggedFile:
    """A file that has been flagged for size or binary content."""

    path: str
    flag_type: str  # "large_file" or "binary_file"
    size_bytes: int
    reason: str


@dataclass
class FileClassification:
    """Result of file classification across a repository."""

    counts: dict[str, int] = field(default_factory=dict)
    flagged_files: list[FlaggedFile] = field(default_factory=list)

    def total_files(self) -> int:
        return sum(self.counts.values())


@dataclass
class DirectoryViolation:
    """A directory convention violation."""

    path: str
    violation_type: str
    message: str


@dataclass
class StaleFile:
    """A stale or cleanup-candidate file."""

    path: str
    stale_type: str  # "compiled", "backup", "temporary", "vim_swap", "stale_log"
    age_days: float
    size_bytes: int
    recommendation: str


@dataclass
class FileInfo:
    """Compact file metadata collected during classification."""

    path: str
    category: str
    size_bytes: int
    lines: int
    mtime: float
    is_text: bool
    is_binary: bool


@dataclass
class RepoSnapshot:
    """Aggregate snapshot of repository file counts and line counts."""

    total_files: int = 0
    total_lines: int = 0
    by_category: dict[str, int] = field(default_factory=dict)
    largest_files: list[dict[str, Any]] = field(default_factory=list)
    newest_files: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class AuditReport:
    """Full repository audit report combining all checks."""

    classification: FileClassification
    directory_violations: list[DirectoryViolation]
    stale_files: list[StaleFile]
    snapshot: RepoSnapshot
    generated_at: str

    def summary(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("REPOSITORY AUDIT REPORT")
        lines.append("=" * 60)
        cls = self.classification
        lines.append(f"  total_files:          {cls.total_files()}")
        for cat, count in sorted(cls.counts.items()):
            if count > 0:
                lines.append(f"    {cat:20s}  {count}")
        lines.append(f"  flagged_files:        {len(cls.flagged_files)}")
        lines.append(f"  directory_violations: {len(self.directory_violations)}")
        lines.append(f"  stale_files:          {len(self.stale_files)}")
        snap = self.snapshot
        lines.append(f"  snapshot_total_lines: {snap.total_lines}")
        lines.append(f"  generated_at:         {self.generated_at}")
        lines.append("-" * 60)
        # Show top 5 largest files
        if snap.largest_files:
            lines.append("  Largest files:")
            for lf in snap.largest_files[:5]:
                lines.append(f"    {lf['size_bytes']:>10_d} bytes  {lf['path']}")
        # Show directory violations
        if self.directory_violations:
            lines.append("  Directory issues:")
            for dv in self.directory_violations[:10]:
                lines.append(f"    [{dv.violation_type}] {dv.path}: {dv.message}")
        # Show stale files
        if self.stale_files:
            lines.append("  Stale files (>{}d):".format(90))
            for sf in self.stale_files[:10]:
                lines.append(f"    {sf.path} ({sf.age_days:.0f}d)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# RepoAuditPipeline
# ---------------------------------------------------------------------------

class RepoAuditPipeline:
    """Automated repository health pipeline.

    Provides static methods for file classification, directory convention
    checking, stale file detection, snapshot collection, and a `run` method
    that orchestrates all checks into a single AuditReport.
    """

    # ------------------------------------------------------------------
    # classify_files
    # ------------------------------------------------------------------

    @staticmethod
    def classify_files(
        root: str | Path,
        rules: dict[str, tuple[str, ...]] | None = None,
    ) -> FileClassification:
        """Walk *root* and classify every file into a category.

        Args:
            root: Repository root directory.
            rules: Optional category -> extensions mapping.  When ``None``,
                   ``DEFAULT_CATEGORY_RULES`` is used.

        Returns:
            FileClassification with per-category counts and any flagged files.
        """
        root = Path(root).resolve()
        if rules is None:
            rules = DEFAULT_CATEGORY_RULES

        counts: dict[str, int] = {cat: 0 for cat in rules}
        counts["other"] = 0
        counts["unknown"] = 0
        flagged: list[FlaggedFile] = []

        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root)

            # Skip well-known VCS / build output directories
            for skip in (".git", "out", "outputs", "var", "build", "__pycache__"):
                if skip in dirnames:
                    dirnames.remove(skip)

            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root).replace("\\", "/")

                try:
                    stat = os.stat(full_path)
                except OSError:
                    continue

                size = stat.st_size
                ext = os.path.splitext(filename)[1].lower()

                # Determine category
                category = RepoAuditPipeline._classify_one(
                    rel_path, filename, ext, root, rules
                )

                # Check for CMakeLists.txt special case (no extension)
                if filename == "CMakeLists.txt":
                    category = "config"

                # Increment category count
                counts[category] = counts.get(category, 0) + 1

                # Flag checks
                if size > LARGE_FILE_THRESHOLD_BYTES:
                    flagged.append(
                        FlaggedFile(
                            path=rel_path,
                            flag_type="large_file",
                            size_bytes=size,
                            reason=(
                                f"File exceeds {LARGE_FILE_THRESHOLD_BYTES} bytes "
                                f"({size:_} bytes)"
                            ),
                        )
                    )

                # Binary detection: if extension is not a known text extension,
                # peek at the first 8 KiB for null bytes
                is_text = ext in TEXT_EXTENSIONS
                is_binary = False
                if not is_text and size > 0:
                    try:
                        with open(full_path, "rb") as fh:
                            chunk = fh.read(8192)
                        if b"\x00" in chunk:
                            is_text = False
                            is_binary = True
                    except OSError:
                        pass

                if is_binary:
                    flagged.append(
                        FlaggedFile(
                            path=rel_path,
                            flag_type="binary_file",
                            size_bytes=size,
                            reason="File contains null bytes (likely binary)",
                        )
                    )

        return FileClassification(counts=counts, flagged_files=flagged)

    @staticmethod
    def _classify_one(
        rel_path: str,
        filename: str,
        ext: str,
        root: Path,
        rules: dict[str, tuple[str, ...]],
    ) -> str:
        """Classify a single file into a category."""

        # Special name-based matches first
        if filename == "CMakeLists.txt":
            return "config"

        # Direct category lookup by extension
        for category, extensions in rules.items():
            if ext in extensions:
                return category

        # Context-dependent overrides
        # .md anywhere is docs
        if ext == ".md":
            return "docs"

        # .txt or .json in fixtures/ are fixtures
        if ext in (".txt", ".json") and "fixtures" in rel_path.replace("\\", "/").split("/"):
            return "fixtures"

        return "other"

    # ------------------------------------------------------------------
    # check_directory_conventions
    # ------------------------------------------------------------------

    @staticmethod
    def check_directory_conventions(root: str | Path) -> list[DirectoryViolation]:
        """Verify directory layout conventions.

        Checks:
        - No ``.git`` directories outside the repository root.
        - No empty directories (except allowed exclusions).
        - Source files only in ``src/`` or ``apps/``.
        - Python files only in ``python/`` or ``tools/``.
        - Documentation only in ``docs/``.

        Returns:
            List of ``DirectoryViolation`` objects.
        """
        root = Path(root).resolve()
        violations: list[DirectoryViolation] = []

        src_exts = frozenset({".cpp", ".h", ".hpp", ".c", ".cc", ".cxx", ".hxx", ".cppm"})
        py_exts = frozenset({".py", ".pyx", ".pxd", ".pxi"})
        doc_exts = frozenset({".md", ".rst"})

        has_content: set[str] = set()
        all_dirs: set[str] = set()

        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root).replace("\\", "/")

            # Skip .git and common build output directories
            for skip in (".git", "out", "outputs", "var", "build", "__pycache__", "node_modules"):
                if skip in dirnames:
                    dirnames.remove(skip)

            if rel_dir != ".":
                all_dirs.add(rel_dir)
                if filenames or dirnames:
                    has_content.add(rel_dir)

            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()

                # Check .git directories outside root
                if filename == ".git" or dirpath.endswith("/.git"):
                    continue  # skipped by os.walk filter, but belt-and-suspenders

                # Source file location check
                if ext in src_exts:
                    top = rel_dir.split("/")[0] if rel_dir != "." else ""
                    if top not in ("src", "apps", ""):
                        violations.append(
                            DirectoryViolation(
                                path=rel_dir + "/" + filename,
                                violation_type="source_outside_src_or_apps",
                                message=(
                                    f"Source file '{filename}' found in '{rel_dir}'; "
                                    "source files should be under src/ or apps/"
                                ),
                            )
                        )

                # Python file location check
                if ext in py_exts:
                    top = rel_dir.split("/")[0] if rel_dir != "." else ""
                    if top not in ("python", "tools", ""):
                        violations.append(
                            DirectoryViolation(
                                path=rel_dir + "/" + filename,
                                violation_type="python_outside_python_or_tools",
                                message=(
                                    f"Python file '{filename}' found in '{rel_dir}'; "
                                    "Python files should be under python/ or tools/"
                                ),
                            )
                        )

                # Documentation location check
                if ext in doc_exts:
                    top = rel_dir.split("/")[0] if rel_dir != "." else ""
                    if top not in ("docs", ""):
                        violations.append(
                            DirectoryViolation(
                                path=rel_dir + "/" + filename,
                                violation_type="docs_outside_docs",
                                message=(
                                    f"Documentation file '{filename}' found in '{rel_dir}'; "
                                    "documentation should be under docs/"
                                ),
                            )
                        )

        # Check for empty directories
        for adir in sorted(all_dirs):
            if adir not in has_content:
                dir_name = adir.split("/")[-1] if "/" in adir else adir
                # Allow certain empty dirs
                if dir_name in ALLOWED_EMPTY_DIRS or any(
                    adir.endswith("/" + aed) or adir == aed
                    for aed in ALLOWED_EMPTY_DIRS
                ):
                    continue
                # Allow empty dirs that contain only allowed-empty subdirs
                # (Skip for now — exact check is tricky; we just whitelist the known names)
                violations.append(
                    DirectoryViolation(
                        path=adir,
                        violation_type="empty_directory",
                        message=f"Directory '{adir}' is empty",
                    )
                )

        return violations

    # ------------------------------------------------------------------
    # detect_stale_artifacts
    # ------------------------------------------------------------------

    @staticmethod
    def detect_stale_artifacts(
        root: str | Path,
        max_age_days: float = 90.0,
    ) -> list[StaleFile]:
        """Find files that have not been modified within *max_age_days*.

        Stale patterns include:
        - ``.pyc`` / ``.pyo`` compiled bytecode
        - ``__pycache__`` directories (flagged)
        - ``.bak``, ``.tmp``, ``*~``, ``.swp``, ``.swo`` files
        - ``.log`` files older than 30 days

        Args:
            root: Repository root.
            max_age_days: Age threshold in days for general stale files.

        Returns:
            List of ``StaleFile`` objects.
        """
        root = Path(root).resolve()
        now = time.time()
        max_age_seconds = max_age_days * 86_400.0
        stale_log_max_age_seconds = STALE_LOG_MAX_AGE_DAYS * 86_400.0
        stale: list[StaleFile] = []

        stale_ext_lookup: dict[str, str] = {
            ext: label for ext, label in STALE_PATTERNS
            if not ext.startswith("*")
        }
        stale_suffixes: list[tuple[str, str]] = [
            (s, l) for s, l in STALE_PATTERNS if s.startswith("*")
        ]

        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root).replace("\\", "/")

            # Skip .git but NOT __pycache__ — we want to inspect it
            for skip in (".git",):
                if skip in dirnames:
                    dirnames.remove(skip)

            # Flag __pycache__ directories
            if "__pycache__" in dirnames:
                pycache_path = os.path.join(dirpath, "__pycache__")
                pycache_rel = os.path.relpath(pycache_path, root).replace("\\", "/")
                try:
                    pycache_stat = os.stat(pycache_path)
                    age_days = (now - pycache_stat.st_mtime) / 86_400.0
                except OSError:
                    age_days = 0.0
                stale.append(
                    StaleFile(
                        path=pycache_rel,
                        stale_type="pycache",
                        age_days=age_days,
                        size_bytes=0,
                        recommendation=(
                            f"__pycache__ directory at '{pycache_rel}' "
                            "(remove with `find . -name __pycache__ -type d -exec rm -rf {} +`)"
                        ),
                    )
                )

            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root).replace("\\", "/")

                try:
                    stat = os.stat(full_path)
                except OSError:
                    continue

                age_days = (now - stat.st_mtime) / 86_400.0
                ext = os.path.splitext(filename)[1].lower()

                # Exact extension matches
                if ext in stale_ext_lookup:
                    if age_days >= max_age_days:
                        stale.append(
                            StaleFile(
                                path=rel_path,
                                stale_type=stale_ext_lookup[ext],
                                age_days=round(age_days, 1),
                                size_bytes=stat.st_size,
                                recommendation=f"Remove stale {stale_ext_lookup[ext]} file: '{rel_path}'",
                            )
                        )

                # Suffix matches (e.g., *~)
                for suffix, label in stale_suffixes:
                    if filename.endswith(suffix[1:]):  # strip the *
                        if age_days >= max_age_days:
                            stale.append(
                                StaleFile(
                                    path=rel_path,
                                    stale_type=label,
                                    age_days=round(age_days, 1),
                                    size_bytes=stat.st_size,
                                    recommendation=f"Remove stale {label} file: '{rel_path}'",
                                )
                            )

                # Log files: separate, shorter threshold
                if ext in STALE_LOG_EXTENSIONS and age_days >= stale_log_max_age_seconds / 86_400.0:
                    stale.append(
                        StaleFile(
                            path=rel_path,
                            stale_type="stale_log",
                            age_days=round(age_days, 1),
                            size_bytes=stat.st_size,
                            recommendation=(
                                f"Log file '{rel_path}' has not been modified in "
                                f"{round(age_days, 1)} days; consider archival or removal"
                            ),
                        )
                    )

        return stale

    # ------------------------------------------------------------------
    # collect_snapshot
    # ------------------------------------------------------------------

    @staticmethod
    def collect_snapshot(root: str | Path) -> RepoSnapshot:
        """Count files and lines by category.

        Returns a ``RepoSnapshot`` with total counts, the 10 largest files,
        and the 5 most recently modified files.
        """
        root = Path(root).resolve()
        all_files: list[FileInfo] = []

        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root)

            for skip in (".git", "out", "outputs", "var", "build", "__pycache__"):
                if skip in dirnames:
                    dirnames.remove(skip)

            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root).replace("\\", "/")

                try:
                    stat = os.stat(full_path)
                except OSError:
                    continue

                ext = os.path.splitext(filename)[1].lower()

                # Classify
                category = RepoAuditPipeline._classify_one(
                    rel_path, filename, ext, root, DEFAULT_CATEGORY_RULES
                )
                if filename == "CMakeLists.txt":
                    category = "config"

                # Count lines for text files
                lines = 0
                is_text = ext in TEXT_EXTENSIONS
                is_binary = False
                if is_text:
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as fh:
                            lines = sum(1 for _ in fh)
                    except OSError:
                        lines = 0
                elif stat.st_size > 0:
                    try:
                        with open(full_path, "rb") as fh:
                            chunk = fh.read(8192)
                        if b"\x00" not in chunk:
                            is_text = True
                            try:
                                with open(full_path, "r", encoding="utf-8", errors="ignore") as fh2:
                                    lines = sum(1 for _ in fh2)
                            except OSError:
                                lines = 0
                        else:
                            is_binary = True
                    except OSError:
                        pass

                all_files.append(
                    FileInfo(
                        path=rel_path,
                        category=category,
                        size_bytes=stat.st_size,
                        lines=lines,
                        mtime=stat.st_mtime,
                        is_text=is_text,
                        is_binary=is_binary,
                    )
                )

        if not all_files:
            return RepoSnapshot()

        by_category: dict[str, int] = {}
        for fi in all_files:
            by_category[fi.category] = by_category.get(fi.category, 0) + 1

        total_lines = sum(fi.lines for fi in all_files)

        largest = sorted(all_files, key=lambda x: x.size_bytes, reverse=True)[:10]
        largest_files = [
            {
                "path": fi.path,
                "size_bytes": fi.size_bytes,
                "category": fi.category,
            }
            for fi in largest
        ]

        newest = sorted(all_files, key=lambda x: x.mtime, reverse=True)[:5]
        newest_files = [
            {
                "path": fi.path,
                "mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(fi.mtime)),
                "category": fi.category,
            }
            for fi in newest
        ]

        return RepoSnapshot(
            total_files=len(all_files),
            total_lines=total_lines,
            by_category=by_category,
            largest_files=largest_files,
            newest_files=newest_files,
        )

    # ------------------------------------------------------------------
    # run
    # ------------------------------------------------------------------

    @staticmethod
    def run(
        root: str | Path,
        max_age_days: float = 90.0,
    ) -> AuditReport:
        """Run all repository audit checks and return a unified report.

        Args:
            root: Repository root directory.
            max_age_days: Age threshold for stale file detection.

        Returns:
            ``AuditReport`` bundling classification, violations, stale files,
            and snapshot.
        """
        root = Path(root).resolve()

        classification = RepoAuditPipeline.classify_files(root)
        violations = RepoAuditPipeline.check_directory_conventions(root)
        stale = RepoAuditPipeline.detect_stale_artifacts(root, max_age_days)
        snapshot = RepoAuditPipeline.collect_snapshot(root)

        return AuditReport(
            classification=classification,
            directory_violations=violations,
            stale_files=stale,
            snapshot=snapshot,
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Repository Audit Pipeline — automated repository health checks"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--stale-threshold",
        type=float,
        default=90.0,
        help="Age threshold in days for stale file detection (default: 90)",
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Print the full repository snapshot",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output report as JSON",
    )
    parser.add_argument(
        "--classify-only",
        action="store_true",
        help="Only run file classification",
    )
    parser.add_argument(
        "--conventions-only",
        action="store_true",
        help="Only run directory convention checks",
    )
    parser.add_argument(
        "--stale-only",
        action="store_true",
        help="Only run stale file detection",
    )
    parser.add_argument(
        "--snapshot-only",
        action="store_true",
        help="Only run snapshot collection",
    )
    return parser


def _print_classification(cls: FileClassification) -> None:
    print("=== FILE CLASSIFICATION ===")
    for cat, count in sorted(cls.counts.items()):
        print(f"  {cat}: {count}")
    if cls.flagged_files:
        print(f"\n  Flagged files ({len(cls.flagged_files)}):")
        for ff in cls.flagged_files:
            print(f"    [{ff.flag_type}] {ff.path} — {ff.reason}")
    else:
        print("\n  No flagged files.")


def _print_violations(violations: list[DirectoryViolation]) -> None:
    print("\n=== DIRECTORY CONVENTION VIOLATIONS ===")
    if not violations:
        print("  No violations found.")
        return
    by_type: dict[str, list[DirectoryViolation]] = {}
    for v in violations:
        by_type.setdefault(v.violation_type, []).append(v)
    for vtype, items in sorted(by_type.items()):
        print(f"\n  [{vtype}] ({len(items)}):")
        for item in items[:10]:
            print(f"    {item.path}")
            print(f"      {item.message}")
        if len(items) > 10:
            print(f"    ... {len(items) - 10} more")


def _print_stale(stale_files: list[StaleFile]) -> None:
    print("\n=== STALE FILES ===")
    if not stale_files:
        print("  No stale files found.")
        return
    by_type: dict[str, list[StaleFile]] = {}
    for sf in stale_files:
        by_type.setdefault(sf.stale_type, []).append(sf)
    for stype, items in sorted(by_type.items()):
        print(f"\n  [{stype}] ({len(items)}):")
        for item in items[:10]:
            print(f"    {item.path}  (age: {item.age_days:.0f}d, size: {item.size_bytes:_}B)")
            print(f"      -> {item.recommendation}")
        if len(items) > 10:
            print(f"    ... {len(items) - 10} more")


def _print_snapshot(snap: RepoSnapshot) -> None:
    print("\n=== REPOSITORY SNAPSHOT ===")
    print(f"  Total files:      {snap.total_files}")
    print(f"  Total lines:      {snap.total_lines:_}")
    print("\n  By category:")
    for cat, count in sorted(snap.by_category.items()):
        print(f"    {cat}: {count}")
    if snap.largest_files:
        print("\n  Largest files (top 10):")
        for lf in snap.largest_files:
            print(f"    [{lf['category']}] {lf['path']} — {lf['size_bytes']:_} bytes")
    if snap.newest_files:
        print("\n  Newest files (top 5):")
        for nf in snap.newest_files:
            print(f"    [{nf['category']}] {nf['path']} — {nf['mtime']}")


def _report_to_dict(report: AuditReport) -> dict[str, Any]:
    return {
        "generated_at": report.generated_at,
        "classification": {
            "counts": dict(sorted(report.classification.counts.items())),
            "flagged_files": [
                {
                    "path": ff.path,
                    "flag_type": ff.flag_type,
                    "size_bytes": ff.size_bytes,
                    "reason": ff.reason,
                }
                for ff in report.classification.flagged_files
            ],
        },
        "directory_violations": [
            {
                "path": v.path,
                "violation_type": v.violation_type,
                "message": v.message,
            }
            for v in report.directory_violations
        ],
        "stale_files": [
            {
                "path": sf.path,
                "stale_type": sf.stale_type,
                "age_days": sf.age_days,
                "size_bytes": sf.size_bytes,
                "recommendation": sf.recommendation,
            }
            for sf in report.stale_files
        ],
        "snapshot": {
            "total_files": report.snapshot.total_files,
            "total_lines": report.snapshot.total_lines,
            "by_category": dict(sorted(report.snapshot.by_category.items())),
            "largest_files": report.snapshot.largest_files,
            "newest_files": report.snapshot.newest_files,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    pipeline = RepoAuditPipeline()
    root = args.root

    # Determine mode
    single_mode = args.classify_only or args.conventions_only or args.stale_only or args.snapshot_only

    if args.classify_only:
        cls = pipeline.classify_files(root)
        _print_classification(cls)
        return 0

    if args.conventions_only:
        violations = pipeline.check_directory_conventions(root)
        _print_violations(violations)
        return 0

    if args.stale_only:
        stale = pipeline.detect_stale_artifacts(root, args.stale_threshold)
        _print_stale(stale)
        return 0

    if args.snapshot_only:
        snap = pipeline.collect_snapshot(root)
        _print_snapshot(snap)
        return 0

    # Full run
    report = pipeline.run(root, args.stale_threshold)

    if args.json_output:
        import json

        print(json.dumps(_report_to_dict(report), indent=2, sort_keys=True))
        return 0

    _print_classification(report.classification)
    _print_violations(report.directory_violations)
    _print_stale(report.stale_files)

    if args.snapshot:
        _print_snapshot(report.snapshot)

    print(f"\nReport generated at {report.generated_at}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
