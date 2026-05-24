#!/usr/bin/env python3
"""Run structural QA for GCS architecture visualization figures."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC_ROOT = ROOT / "tools" / "architecture_visualization" / "specs"


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object")
    return data


def root_path(path_value: object) -> Path:
    path = Path(str(path_value))
    return path if path.is_absolute() else ROOT / path


def parse_report_steps(report_path: Path) -> set[int]:
    steps: set[int] = set()
    for line in report_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0].isdigit():
            steps.add(int(cells[0]))
    return steps


def source_report_paths(spec: dict[str, object]) -> list[Path]:
    raw_reports = spec.get("source_reports")
    if isinstance(raw_reports, list) and raw_reports:
        return [root_path(item) for item in raw_reports]
    return [root_path(spec["source_report"])]


def parse_source_steps(spec: dict[str, object]) -> set[int]:
    steps: set[int] = set()
    for report_path in source_report_paths(spec):
        steps.update(parse_report_steps(report_path))
    return steps


def expected_steps(spec: dict[str, object]) -> set[int]:
    raw_range = spec.get("expected_step_range", [1, 40])
    if isinstance(raw_range, list) and len(raw_range) == 2:
        start, end = int(raw_range[0]), int(raw_range[1])
        return set(range(start, end + 1))
    return set(range(1, 41))


def arc_steps(spec: dict[str, object]) -> set[int]:
    covered: set[int] = set()
    arcs = spec.get("arcs", [])
    if not isinstance(arcs, list):
        return covered
    for arc in arcs:
        if not isinstance(arc, dict):
            continue
        raw_range = arc.get("range", [])
        if not isinstance(raw_range, list) or len(raw_range) != 2:
            continue
        start, end = int(raw_range[0]), int(raw_range[1])
        covered.update(range(start, end + 1))
    return covered


def html_checks(html_path: Path, spec: dict[str, object]) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    html = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    quality = spec.get("quality", {})
    if not isinstance(quality, dict):
        quality = {}

    require_no_absolute = bool(quality.get("require_no_absolute_positioning", True))
    absolute_found = bool(re.search(r"position\s*:\s*absolute", html, re.IGNORECASE))
    checks.append({
        "name": "no_absolute_positioning",
        "passed": (not absolute_found) if require_no_absolute else True,
        "detail": "Dense execution-map HTML should rely on grid/flex text flow, not absolute positioning.",
    })

    require_wrap = bool(quality.get("require_overflow_wrap", True))
    wrap_found = "overflow-wrap" in html
    checks.append({
        "name": "overflow_wrap_rule",
        "passed": wrap_found if require_wrap else True,
        "detail": "CSS should include overflow-wrap for long report-derived labels.",
    })

    min_font = int(quality.get("min_font_px", 10))
    font_sizes = [int(value) for value in re.findall(r"font-size:\s*(\d+)px", html)]
    too_small = [value for value in font_sizes if value < min_font]
    checks.append({
        "name": "minimum_font_size",
        "passed": not too_small,
        "detail": f"Minimum font size is {min_font}px; observed too-small sizes: {too_small}.",
    })
    return checks


def run_qa(spec_path: Path) -> dict[str, object]:
    spec = load_json(spec_path)
    exports = spec.get("exports", {})
    if not isinstance(exports, dict):
        exports = {}
    html_path = root_path(exports.get("html", ""))
    report_steps = parse_source_steps(spec)
    covered_steps = arc_steps(spec)
    expected = expected_steps(spec)

    checks: list[dict[str, object]] = [
        {
            "name": "report_has_expected_steps",
            "passed": expected.issubset(report_steps),
            "detail": f"Missing report steps: {sorted(expected - report_steps)}",
        },
        {
            "name": "spec_covers_expected_steps",
            "passed": expected == covered_steps,
            "detail": f"Missing spec steps: {sorted(expected - covered_steps)}; extra: {sorted(covered_steps - expected)}",
        },
        {
            "name": "html_export_exists",
            "passed": html_path.exists(),
            "detail": str(html_path),
        },
    ]
    if html_path.exists():
        checks.extend(html_checks(html_path, spec))

    passed = all(bool(check["passed"]) for check in checks)
    return {
        "figure": spec.get("id", spec_path.stem),
        "spec": str(spec_path.relative_to(ROOT)),
        "passed": passed,
        "checks": checks,
        "browser_qa_required_before_final": bool(
            isinstance(spec.get("quality", {}), dict)
            and spec["quality"].get("browser_screenshot_required_before_final", False)
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run structural QA for a GCS figure.")
    parser.add_argument("--figure", default="figure71", help="Figure id, resolved to specs/<figure>.yaml.")
    parser.add_argument("--spec", type=Path, help="Explicit spec path.")
    parser.add_argument("--out", type=Path, help="Optional QA JSON output path. Defaults to spec exports.qa.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec_path = args.spec if args.spec else SPEC_ROOT / f"{args.figure}.yaml"
    if not spec_path.is_absolute():
        spec_path = ROOT / spec_path
    result = run_qa(spec_path)
    spec = load_json(spec_path)
    out_path = args.out
    if out_path is None:
        exports = spec.get("exports", {})
        if isinstance(exports, dict) and "qa" in exports:
            out_path = root_path(exports["qa"])
    elif not out_path.is_absolute():
        out_path = ROOT / out_path
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
