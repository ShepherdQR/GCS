#!/usr/bin/env python3
"""Performance Benchmark Pipeline — measures solver performance across a fixture corpus.

Tracks duration, iterations, and residual norm; stores results in a SQLite
trend database; detects regressions against baselines.

Usage:
    python tools/solver_testing/pipelines/benchmark.py \
        --corpus fixtures/scene/ \
        --db tools/solver_testing/benchmarks/trend.db \
        --warmup 3 --runs 5
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sqlite3
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class BenchmarkPoint:
    """A single benchmark result for one scene."""

    scene_id: str
    duration_median_ms: float
    duration_std_ms: float
    iterations: int
    status: str
    residual_norm: float


@dataclass
class BenchmarkReport:
    """Full benchmark run output."""

    points: list[BenchmarkPoint] = field(default_factory=list)
    regressions: list[dict[str, Any]] = field(default_factory=list)
    solver_version: str = ""
    timestamp: str = ""
    corpus_path: str = ""
    total_scenes: int = 0
    solved: int = 0
    failed: int = 0

    def summary(self) -> dict[str, Any]:
        return {
            "solver_version": self.solver_version,
            "timestamp": self.timestamp,
            "corpus_path": self.corpus_path,
            "total_scenes": self.total_scenes,
            "solved": self.solved,
            "failed": self.failed,
            "regression_count": len(self.regressions),
            "points": len(self.points),
        }


# ---------------------------------------------------------------------------
# Solver output parsing
# ---------------------------------------------------------------------------

_ITER_RE = re.compile(
    r"(?:iteration[s]?\s*(?:count)?[:\s]*)(\d+)",
    re.IGNORECASE,
)
_RESIDUAL_RE = re.compile(
    r"(?:(?:final|last)\s*residual[:\s]*)([\d.eE+\-]+)",
    re.IGNORECASE,
)
_STATUS_RE = re.compile(
    r"^Status:\s*(.+)$",
    re.MULTILINE | re.IGNORECASE,
)
_ACCEPTED_RE = re.compile(
    r"^Accepted:\s*(true|false)$",
    re.MULTILINE | re.IGNORECASE,
)
_LOCAL_REPORTS_RE = re.compile(
    r"^Local numeric reports:\s*(\d+)$",
    re.MULTILINE | re.IGNORECASE,
)


def _parse_iterations(stdout: str) -> int:
    """Extract iteration count from solver stdout.

    Tries several strategies:
    1.  Explicit 'iteration count' or 'iterations: N' pattern.
    2.  Sum of per-section iteration counts found in numeric report lines.
    3.  'Local numeric reports' count as a rough proxy.
    """
    # Direct iteration count
    m = _ITER_RE.search(stdout)
    if m:
        return int(m.group(1))

    # Check for per-line iteration entries (e.g. "  iteration 3: residual ...")
    per_line = re.findall(r"iteration\s*(\d+)", stdout, re.IGNORECASE)
    if per_line:
        return max(int(v) for v in per_line)

    # Fall back to Local numeric reports count
    m = _LOCAL_REPORTS_RE.search(stdout)
    if m:
        return int(m.group(1))

    return 0


def _parse_residual(stdout: str) -> float:
    """Extract final residual norm from solver stdout."""
    m = _RESIDUAL_RE.search(stdout)
    if m:
        try:
            return float(m.group(1))
        except (ValueError, TypeError):
            pass

    # Try to find scientific notation numbers near 'residual' in free text
    residual_lines = [line for line in stdout.splitlines() if "residual" in line.lower()]
    for line in reversed(residual_lines):  # prefer later mentions
        numbers = re.findall(r"([\d]+(?:\.[\d]+)?(?:[eE][+\-]?\d+)?)", line)
        for n in reversed(numbers):
            try:
                val = float(n)
                if val > 0:
                    return val
            except (ValueError, TypeError):
                continue

    return 0.0


def _parse_status(stdout: str) -> str:
    """Extract solver status from stdout."""
    m = _STATUS_RE.search(stdout)
    if m:
        return m.group(1).strip().lower()
    m = _ACCEPTED_RE.search(stdout)
    if m:
        accepted = m.group(1).lower() == "true"
        return "solved" if accepted else "failed"
    # Fallback text inspection
    lower = stdout.lower()
    if "accepted: true" in lower or "solved" in lower:
        return "solved"
    if "accepted: false" in lower or "obstruction" in lower:
        return "failed"
    return "unknown"


# ---------------------------------------------------------------------------
# Solver version detection
# ---------------------------------------------------------------------------


def _detect_solver_version(solver_command: list[str]) -> str:
    """Attempt to detect solver version from the binary."""
    try:
        result = subprocess.run(
            [*solver_command, "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        combined = stdout + stderr
        # Look for version strings
        ver = re.search(r"version[:\s]*([\d.]+)", combined, re.IGNORECASE)
        if ver:
            return ver.group(1)
        # Try git describe if solver is a local build
        exe_path = solver_command[0]
        exe_dir = os.path.dirname(os.path.abspath(exe_path))
        try:
            git_result = subprocess.run(
                ["git", "describe", "--always", "--dirty"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=exe_dir,
            )
            if git_result.returncode == 0:
                return f"git-{git_result.stdout.strip()}"
        except (OSError, subprocess.TimeoutExpired):
            pass
    except (OSError, subprocess.TimeoutExpired, ValueError):
        pass
    return "unknown"


# ---------------------------------------------------------------------------
# BenchmarkPipeline
# ---------------------------------------------------------------------------


class BenchmarkPipeline:
    """Measures solver performance (duration, iterations) across a fixture corpus."""

    def __init__(self, solver_command: list[str] | None = None):
        self._solver_command = solver_command
        self._version: str | None = None

    @property
    def solver_command(self) -> list[str]:
        if self._solver_command is None:
            self._solver_command = self._resolve_solver()
            if self._solver_command is None:
                raise RuntimeError(
                    "GCS solver not found. Set GCS_EXE or build the project."
                )
        return self._solver_command

    @solver_command.setter
    def solver_command(self, value: list[str]):
        self._solver_command = value
        self._version = None

    def _resolve_solver(self) -> list[str] | None:
        """Find the GCS solver executable."""
        # Import existing resolver from runner module
        try:
            from tools.solver_testing.runner import find_solver

            return find_solver()
        except ImportError:
            pass

        # Fallback resolution
        candidates: list[str] = []
        env_exe = os.environ.get("GCS_EXE")
        if env_exe:
            candidates.append(env_exe)
        default = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..", "out", "build", "clang-ninja",
                "GCS.exe" if os.name == "nt" else "GCS",
            )
        )
        candidates.append(default)
        for candidate in candidates:
            if os.path.exists(candidate):
                return [candidate]
        return None

    def _solver_version(self) -> str:
        if self._version is None:
            self._version = _detect_solver_version(self.solver_command)
        return self._version

    # ------------------------------------------------------------------
    # timed_solve
    # ------------------------------------------------------------------

    def timed_solve(
        self,
        scene_path: str,
        scene_id: str,
        solver_command: list[str] | None = None,
        warmup: int = 3,
        runs: int = 5,
    ) -> BenchmarkPoint:
        """Run solver *runs* times, discard *warmup* results, compute stats.

        Args:
            scene_path: Absolute or relative path to the scene file.
            scene_id: Human-readable scene identifier.
            solver_command: Override the default solver command.
            warmup: Number of initial runs to discard (OS cache warm-up).
            runs: Number of measured runs after warmup.

        Returns:
            BenchmarkPoint with median duration, std, iterations, status,
            and residual norm.
        """
        cmd = solver_command if solver_command is not None else self.solver_command
        total_runs = warmup + runs
        durations: list[float] = []
        all_stdouts: list[str] = []
        final_status = "unknown"
        last_exit_code = 0

        for i in range(total_runs):
            started = time.monotonic()
            try:
                completed = subprocess.run(
                    [*cmd, scene_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
            except subprocess.TimeoutExpired:
                duration_ms = (time.monotonic() - started) * 1000.0
                durations.append(duration_ms)
                all_stdouts.append("")
                final_status = "timeout"
                last_exit_code = -1
                continue
            except OSError as exc:
                duration_ms = (time.monotonic() - started) * 1000.0
                durations.append(duration_ms)
                all_stdouts.append(str(exc))
                final_status = "crash"
                last_exit_code = -2
                continue

            duration_ms = (time.monotonic() - started) * 1000.0
            durations.append(duration_ms)
            all_stdouts.append(completed.stdout)
            last_exit_code = completed.returncode

        # Discard warmup
        measured = durations[warmup:] if len(durations) > warmup else durations
        measured_stdouts = all_stdouts[warmup:] if len(all_stdouts) > warmup else all_stdouts

        # Compute statistics
        if not measured:
            return BenchmarkPoint(
                scene_id=scene_id,
                duration_median_ms=0.0,
                duration_std_ms=0.0,
                iterations=0,
                status="no_measurements",
                residual_norm=0.0,
            )

        median = statistics.median(measured)
        try:
            std = statistics.stdev(measured) if len(measured) > 1 else 0.0
        except statistics.StatisticsError:
            std = 0.0

        # Parse from the last measured run's output (most representative)
        last_stdout = measured_stdouts[-1] if measured_stdouts else ""
        iterations = _parse_iterations(last_stdout)
        residual_norm = _parse_residual(last_stdout)

        # Status from last measured run; fall back to exit-code inference
        parsed_status = _parse_status(last_stdout)
        if parsed_status == "unknown":
            parsed_status = "solved" if last_exit_code == 0 else "failed"
        final_status = parsed_status

        return BenchmarkPoint(
            scene_id=scene_id,
            duration_median_ms=median,
            duration_std_ms=std,
            iterations=iterations,
            status=final_status,
            residual_norm=residual_norm,
        )

    # ------------------------------------------------------------------
    # benchmark_corpus
    # ------------------------------------------------------------------

    def benchmark_corpus(
        self,
        corpus_path: str,
        solver_command: list[str] | None = None,
        warmup: int = 3,
        runs: int = 5,
    ) -> list[BenchmarkPoint]:
        """Scan *corpus_path* for .txt and .json scene files, benchmark each.

        Args:
            corpus_path: Directory to scan recursively for scene files.
            solver_command: Override the default solver command.
            warmup: Warmup runs to discard per scene.
            runs: Measured runs per scene.

        Returns:
            List of BenchmarkPoint (one per discovered scene file).
        """
        patterns = [
            os.path.join(corpus_path, "**", "*.txt"),
            os.path.join(corpus_path, "**", "*.json"),
        ]
        scene_files: set[str] = set()
        for pat in patterns:
            for path in glob.glob(pat, recursive=True):
                if os.path.basename(path) == "baseline.json":
                    continue
                scene_files.add(os.path.abspath(path))

        if not scene_files:
            print(f"[benchmark_corpus] No .txt or .json files found in {corpus_path}")
            return []

        sorted_files = sorted(scene_files)
        print(f"[benchmark_corpus] Found {len(sorted_files)} scene(s) in {corpus_path}")

        results: list[BenchmarkPoint] = []
        for n, abs_path in enumerate(sorted_files, start=1):
            # Derive a stable, relative scene id
            scene_id = os.path.relpath(abs_path, corpus_path).replace("\\", "/")
            print(
                f"  [{n}/{len(sorted_files)}] {scene_id}  "
                f"(warmup={warmup}, runs={runs})"
            )
            point = self.timed_solve(
                abs_path,
                scene_id,
                solver_command=solver_command,
                warmup=warmup,
                runs=runs,
            )
            results.append(point)
            print(
                f"       -> median={point.duration_median_ms:.1f}ms "
                f"std={point.duration_std_ms:.1f} "
                f"iter={point.iterations} "
                f"status={point.status} "
                f"residual={point.residual_norm:.4g}"
            )

        return results

    # ------------------------------------------------------------------
    # run — full pipeline
    # ------------------------------------------------------------------

    def run(
        self,
        corpus_path: str,
        db_path: str,
        solver_command: list[str] | None = None,
        warmup: int = 3,
        runs: int = 5,
        threshold: float = 1.2,
    ) -> BenchmarkReport:
        """Full pipeline: benchmark corpus, store in TrendDB, detect regressions.

        Args:
            corpus_path: Path to the fixture corpus directory.
            db_path: Path to the SQLite trend database.
            solver_command: Solver executable command.
            warmup: Warmup runs per scene.
            runs: Measured runs per scene.
            threshold: Regression threshold multiplier on baseline.

        Returns:
            BenchmarkReport with all points, regressions, and summary stats.
        """
        cmd = solver_command if solver_command is not None else self.solver_command
        db = TrendDB(db_path)

        print("=" * 60)
        print("PERFORMANCE BENCHMARK PIPELINE")
        print("=" * 60)
        print(f"Solver:  {' '.join(cmd)}")
        print(f"Version: {self._solver_version()}")
        print(f"Corpus:  {corpus_path}")
        print(f"DB:      {db_path}")
        print(f"Config:  warmup={warmup}, runs={runs}, threshold={threshold}")
        print()

        points = self.benchmark_corpus(corpus_path, solver_command=cmd, warmup=warmup, runs=runs)

        # Persist to TrendDB
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        solver_version = self._solver_version()
        for pt in points:
            db.insert_benchmark(pt, timestamp=timestamp, solver_version=solver_version)

        # Detect regressions
        regressions = db.detect_regressions(points, threshold=threshold)

        # Build report
        report = BenchmarkReport(
            points=points,
            regressions=regressions,
            solver_version=solver_version,
            timestamp=timestamp,
            corpus_path=corpus_path,
            total_scenes=len(points),
            solved=sum(1 for p in points if p.status in ("solved", "accepted_with_warnings")),
            failed=sum(1 for p in points if p.status not in ("solved", "accepted_with_warnings")),
        )

        # Print summary
        print()
        print("=" * 60)
        print("BENCHMARK REPORT")
        print("=" * 60)
        for key, val in report.summary().items():
            print(f"  {key}: {val}")

        if regressions:
            print()
            print(f"REGRESSIONS DETECTED ({len(regressions)}):")
            for r in regressions:
                print(
                    f"  {r['scene_id']}: "
                    f"baseline={r['baseline_median_ms']:.1f}ms -> "
                    f"current={r['current_median_ms']:.1f}ms "
                    f"(x{r['ratio']:.2f})"
                )
        else:
            print()
            print("No regressions detected.")

        return report


# ---------------------------------------------------------------------------
# TrendDB — SQLite-backed trend database
# ---------------------------------------------------------------------------


class TrendDB:
    """SQLite-backed storage and query for benchmark trend data."""

    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(db_path)
        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self) -> None:
        d = os.path.dirname(self.db_path)
        if d:
            os.makedirs(d, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    # ------------------------------------------------------------------
    # init_db
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        """Create the benchmarks table if it does not exist."""
        ddl = """
        CREATE TABLE IF NOT EXISTS benchmarks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            scene_id        TEXT    NOT NULL,
            timestamp       TEXT    NOT NULL,
            solver_version  TEXT    NOT NULL DEFAULT 'unknown',
            duration_median_ms REAL NOT NULL,
            duration_std_ms REAL    NOT NULL DEFAULT 0.0,
            iterations      INTEGER NOT NULL DEFAULT 0,
            status          TEXT    NOT NULL DEFAULT 'unknown',
            residual_norm   REAL    NOT NULL DEFAULT 0.0
        );
        """
        with self._connect() as conn:
            conn.execute(ddl)
            # Index for fast per-scene trend queries
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_bench_scene_time "
                "ON benchmarks (scene_id, timestamp DESC);"
            )
            conn.commit()

    # ------------------------------------------------------------------
    # insert_benchmark
    # ------------------------------------------------------------------

    def insert_benchmark(
        self,
        point: BenchmarkPoint,
        timestamp: str | None = None,
        solver_version: str = "unknown",
    ) -> int:
        """Insert a single benchmark point. Returns the new row id."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        sql = """
        INSERT INTO benchmarks
            (scene_id, timestamp, solver_version,
             duration_median_ms, duration_std_ms,
             iterations, status, residual_norm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self._connect() as conn:
            cur = conn.execute(
                sql,
                (
                    point.scene_id,
                    timestamp,
                    solver_version,
                    point.duration_median_ms,
                    point.duration_std_ms,
                    point.iterations,
                    point.status,
                    point.residual_norm,
                ),
            )
            conn.commit()
            return cur.lastrowid or 0

    # ------------------------------------------------------------------
    # query_trend
    # ------------------------------------------------------------------

    def query_trend(self, scene_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return recent benchmark history for one scene, newest first."""
        sql = """
        SELECT id, scene_id, timestamp, solver_version,
               duration_median_ms, duration_std_ms,
               iterations, status, residual_norm
        FROM benchmarks
        WHERE scene_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """
        with self._connect() as conn:
            rows = conn.execute(sql, (scene_id, limit)).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # detect_regressions
    # ------------------------------------------------------------------

    def detect_regressions(
        self,
        current_points: list[BenchmarkPoint],
        baseline_median: float | None = None,
        threshold: float = 1.2,
    ) -> list[dict[str, Any]]:
        """Detect regressions by comparing current results to database baselines.

        For each scene in *current_points*, looks up the most recent baseline
        run in the DB (excluding any run in the same second).  A regression is
        flagged when `current >= baseline * threshold`.

        If *baseline_median* is provided (float), it is used as an absolute
        baseline for every scene instead of querying the DB.

        Args:
            current_points: Current benchmark results.
            baseline_median: Optional absolute baseline for all scenes.
            threshold: Multiplier — e.g. 1.2 means 20% slower triggers.

        Returns:
            List of regression dicts with scene_id, ratio, baseline, current, etc.
        """
        regressions: list[dict[str, Any]] = []
        seen: set[str] = set()

        for pt in current_points:
            if pt.scene_id in seen:
                continue
            seen.add(pt.scene_id)

            if pt.status not in ("solved", "accepted_with_warnings"):
                # Only compare scenes that solve successfully now
                continue

            if baseline_median is not None:
                bl = baseline_median
                bl_source = "provided"
            else:
                trend = self.query_trend(pt.scene_id, limit=10)
                # Find the most recent *other* run (different timestamp to
                # avoid comparing against ourselves when called right after
                # insert).  We simply take the first run whose scene matches.
                solved_trend = [
                    t
                    for t in trend
                    if t.get("status") in ("solved", "accepted_with_warnings")
                ]
                if len(solved_trend) < 2:
                    # Need at least one *other* baseline point besides the
                    # one we just inserted.
                    continue
                # The most recent entry is the one we just inserted (same
                # batch), so use the second as baseline.
                bl = solved_trend[1]["duration_median_ms"]
                bl_source = "db"

            if bl <= 0:
                continue

            ratio = pt.duration_median_ms / bl
            if ratio >= threshold:
                regressions.append({
                    "scene_id": pt.scene_id,
                    "baseline_median_ms": bl,
                    "current_median_ms": pt.duration_median_ms,
                    "ratio": round(ratio, 4),
                    "baseline_source": bl_source,
                    "status": pt.status,
                })

        return regressions

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def list_scenes(self) -> list[str]:
        """Return all distinct scene IDs in the database."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT scene_id FROM benchmarks ORDER BY scene_id"
            ).fetchall()
        return [r[0] for r in rows]

    def latest_for_scene(self, scene_id: str) -> dict[str, Any] | None:
        """Return the most recent benchmark for a scene."""
        trend = self.query_trend(scene_id, limit=1)
        return trend[0] if trend else None

    def count(self) -> int:
        """Total number of benchmark rows."""
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM benchmarks").fetchone()
        return row[0] if row else 0

    def close(self) -> None:
        """No-op for API symmetry — connections are short-lived."""
        pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: tuple) -> dict[str, Any]:
    cols = [
        "id",
        "scene_id",
        "timestamp",
        "solver_version",
        "duration_median_ms",
        "duration_std_ms",
        "iterations",
        "status",
        "residual_norm",
    ]
    return dict(zip(cols, row))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _resolve_implicit_corpus(default: str) -> str:
    """Resolve default corpus path relative to the repo root."""
    if os.path.isdir(default):
        return default
    # Try repo-root relative
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    candidate = os.path.join(repo, default)
    if os.path.isdir(candidate):
        return candidate
    return default


def _resolve_implicit_db(default: str) -> str:
    """Resolve default db path relative to solver_testing directory."""
    if os.path.isabs(default):
        return default
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base, "benchmarks", os.path.basename(default))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Performance Benchmark Pipeline — measure solver speed and detect regressions.",
    )
    parser.add_argument(
        "--corpus",
        default="fixtures/scene/",
        help="Path to fixture corpus directory (default: fixtures/scene/)",
    )
    parser.add_argument(
        "--db",
        default="tools/solver_testing/benchmarks/trend.db",
        help="Path to SQLite trend database (default: tools/solver_testing/benchmarks/trend.db)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=3,
        help="Number of warmup runs to discard per scene (default: 3)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of measured runs per scene (default: 5)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=1.2,
        help="Regression threshold multiplier (default: 1.2)",
    )
    parser.add_argument(
        "--solver",
        type=str,
        default=None,
        help="Path to GCS solver executable (default: auto-detect)",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        metavar="SCENE_ID",
        help="Query trend history for a scene and exit (no benchmarking)",
    )
    parser.add_argument(
        "--list-scenes",
        action="store_true",
        help="List all scenes in the trend DB and exit",
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Query-only modes
    # ------------------------------------------------------------------
    db_path = _resolve_implicit_db(args.db)
    if args.query or args.list_scenes:
        db = TrendDB(db_path)
        if args.list_scenes:
            scenes = db.list_scenes()
            if scenes:
                print(f"Scenes in trend DB ({len(scenes)}):")
                for s in scenes:
                    latest = db.latest_for_scene(s)
                    if latest:
                        print(
                            f"  {s}  "
                            f"median={latest['duration_median_ms']:.1f}ms  "
                            f"status={latest['status']}  "
                            f"ts={latest['timestamp']}"
                        )
                        continue
                    print(f"  {s}")
            else:
                print("No benchmark data in DB.")
        if args.query:
            print(f"Trend history for: {args.query}")
            rows = db.query_trend(args.query, limit=20)
            if not rows:
                print("  (no data)")
            for r in rows:
                print(
                    f"  {r['timestamp']}  "
                    f"median={r['duration_median_ms']:.1f}ms  "
                    f"std={r['duration_std_ms']:.1f}  "
                    f"iter={r['iterations']}  "
                    f"status={r['status']}"
                )
        return

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------
    corpus_path = _resolve_implicit_corpus(args.corpus)
    solver_command = [args.solver] if args.solver else None

    pipeline = BenchmarkPipeline(solver_command=solver_command)
    pipeline.run(
        corpus_path=corpus_path,
        db_path=db_path,
        solver_command=solver_command,
        warmup=args.warmup,
        runs=args.runs,
        threshold=args.threshold,
    )


if __name__ == "__main__":
    main()
