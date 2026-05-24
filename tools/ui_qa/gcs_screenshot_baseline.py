from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = (
    REPO_ROOT
    / "docs"
    / "architecture"
    / "70-visualization"
    / "assets"
    / "screenshot-baselines.json"
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class PngInfo:
    width: int
    height: int
    byte_count: int
    sha256: str


@dataclass
class ScreenshotBaselineResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    baselines_checked: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


def repo_relative(path: Path, repo_root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def resolve_repo_path(raw_path: str, repo_root: Path = REPO_ROOT) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return repo_root / path


def inspect_png(path: Path) -> PngInfo:
    data = path.read_bytes()
    if len(data) < 33:
        raise ValueError("PNG is too small to contain an IHDR chunk")
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("file does not start with a PNG signature")
    if data[12:16] != b"IHDR":
        raise ValueError("PNG first chunk is not IHDR")
    width, height = struct.unpack(">II", data[16:24])
    if width <= 0 or height <= 0:
        raise ValueError("PNG width and height must be positive")
    return PngInfo(
        width=width,
        height=height,
        byte_count=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require_string(entry: dict[str, Any], key: str) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing string field {key!r}")
    return value


def check_number(entry: dict[str, Any],
                 key: str,
                 actual: int,
                 baseline_id: str,
                 result: ScreenshotBaselineResult) -> None:
    if key not in entry:
        return
    expected = entry[key]
    if not isinstance(expected, int):
        result.errors.append(f"{baseline_id}: {key} must be an integer")
    elif actual != expected:
        result.errors.append(f"{baseline_id}: {key} is {actual}, expected {expected}")


def check_baseline(entry: dict[str, Any],
                   repo_root: Path,
                   result: ScreenshotBaselineResult) -> None:
    try:
        baseline_id = require_string(entry, "id")
        artifact_path = resolve_repo_path(require_string(entry, "path"), repo_root)
    except ValueError as exc:
        result.errors.append(str(exc))
        return

    if artifact_path.suffix.lower() != ".png":
        result.errors.append(f"{baseline_id}: screenshot baseline must point to a PNG")
        return
    if not artifact_path.is_file():
        result.errors.append(f"{baseline_id}: missing PNG artifact {repo_relative(artifact_path, repo_root)}")
        return

    try:
        info = inspect_png(artifact_path)
    except ValueError as exc:
        result.errors.append(f"{baseline_id}: {repo_relative(artifact_path, repo_root)}: {exc}")
        return

    result.baselines_checked += 1
    check_number(entry, "width", info.width, baseline_id, result)
    check_number(entry, "height", info.height, baseline_id, result)
    check_number(entry, "bytes", info.byte_count, baseline_id, result)

    min_bytes = entry.get("min_bytes")
    if min_bytes is not None:
        if not isinstance(min_bytes, int):
            result.errors.append(f"{baseline_id}: min_bytes must be an integer")
        elif info.byte_count < min_bytes:
            result.errors.append(f"{baseline_id}: byte count {info.byte_count} is below min_bytes {min_bytes}")

    expected_sha = entry.get("sha256")
    if not isinstance(expected_sha, str) or len(expected_sha.strip()) != 64:
        result.errors.append(f"{baseline_id}: sha256 must be a 64-character hex string")
    elif info.sha256.lower() != expected_sha.lower():
        result.errors.append(f"{baseline_id}: sha256 changed from {expected_sha.lower()} to {info.sha256.lower()}")


def run_checks(manifest_path: Path = DEFAULT_MANIFEST_PATH,
               repo_root: Path = REPO_ROOT) -> ScreenshotBaselineResult:
    result = ScreenshotBaselineResult()
    if not manifest_path.is_file():
        result.errors.append(f"Missing screenshot baseline manifest: {repo_relative(manifest_path, repo_root)}")
        return result

    try:
        manifest = load_manifest(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        result.errors.append(f"Could not read screenshot baseline manifest: {exc}")
        return result

    if manifest.get("schema_version") != "gcs.screenshot_baselines.v1":
        result.errors.append("Screenshot baseline manifest schema_version must be gcs.screenshot_baselines.v1")

    baselines = manifest.get("baselines")
    if not isinstance(baselines, list) or not baselines:
        result.errors.append("Screenshot baseline manifest must contain at least one baseline")
        return result

    seen_ids: set[str] = set()
    for entry in baselines:
        if not isinstance(entry, dict):
            result.errors.append("Screenshot baseline entry must be an object")
            continue
        baseline_id = entry.get("id")
        if isinstance(baseline_id, str):
            if baseline_id in seen_ids:
                result.errors.append(f"{baseline_id}: duplicate baseline id")
            seen_ids.add(baseline_id)
        check_baseline(entry, repo_root, result)

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check GCS screenshot baseline artifacts")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="Screenshot baseline manifest to validate",
    )
    args = parser.parse_args(argv)

    result = run_checks(args.manifest)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.ok:
        print(f"GCS screenshot baseline checks passed ({result.baselines_checked} baselines)")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
