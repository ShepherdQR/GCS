#!/usr/bin/env python3
"""Render a deterministic D5 Solver Evidence Workbench evidence screenshot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_D2 = ROOT / "docs" / "product" / "demos" / "d2-diagnostic-classification" / "artifacts" / "d2-diagnostic-summary.json"
DEFAULT_D3 = ROOT / "docs" / "product" / "demos" / "d3-replay-evidence" / "artifacts" / "g1-replay-evidence.report.json"
DEFAULT_OUTPUT = ROOT / "docs" / "product" / "demos" / "d5-solver-evidence-workbench" / "artifacts" / "d5-workbench-evidence.png"
DEFAULT_MANIFEST = ROOT / "docs" / "product" / "demos" / "d5-solver-evidence-workbench" / "artifacts" / "screenshot-baselines.json"


def repo_display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{repo_display(path)} must contain a JSON object")
    return payload


def font(name: str, size: int) -> ImageFont.ImageFont:
    for candidate in [
        rf"C:\Windows\Fonts\{name}.ttf",
        rf"C:\Windows\Fonts\{name}.TTF",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, fill: str, fnt: ImageFont.ImageFont) -> None:
    draw.text(xy, value, fill=fill, font=fnt)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, fill: str = "#fffefa") -> None:
    draw.rounded_rectangle(box, radius=8, fill=fill, outline="#d8d1c4", width=1)
    draw.text((box[0] + 18, box[1] + 16), title, fill="#181715", font=font("segoeuib", 18))


def render(output: Path, d2: dict[str, Any], d3: dict[str, Any]) -> None:
    width, height = 1600, 980
    img = Image.new("RGB", (width, height), "#f7f4ec")
    draw = ImageDraw.Draw(img)

    f_title = font("georgia", 34)
    f_h = font("segoeuib", 18)
    f = font("segoeui", 15)
    f_mono = font("consola", 14)
    ink = "#181715"
    muted = "#5f5b53"
    good = "#4d6f73"
    warn = "#9a7a4f"
    fail = "#b86850"
    rail = "#ebe5da"

    def short_status(value: Any) -> str:
        mapping = {
            "AcceptedWithWarnings": "Accepted + warn",
            "NumericallySingular": "Singular",
        }
        return mapping.get(str(value), str(value))

    draw.rounded_rectangle((44, 38, 1556, 936), radius=8, fill="#fffefa", outline="#d8d1c4", width=1)
    text(draw, (76, 82), "D5 Solver Evidence Workbench", ink, f_title)
    text(draw, (78, 124), "Static evidence-board screenshot package. Governing convention: GCS Evidence-First Interface Grammar.", muted, f)
    text(draw, (78, 150), "This is not a live GUI claim; it shows the target workbench evidence hierarchy from D2 and D3 artifacts.", muted, f)

    panel(draw, (76, 196, 530, 560), "Model Canvas")
    draw.rectangle((108, 255, 498, 510), fill="#f2eee5", outline="#d8d1c4")
    pts = [(180, 430), (300, 280), (430, 430)]
    draw.line([pts[0], pts[1], pts[2], pts[0]], fill="#4d6f73", width=5)
    for idx, (x, y) in enumerate(pts, start=1):
        draw.ellipse((x - 11, y - 11, x + 11, y + 11), fill="#fffefa", outline="#181715", width=2)
        text(draw, (x + 14, y - 10), f"p{idx}", ink, f_mono)
    text(draw, (124, 520), "Scene: fixtures/scene/basic/g1.txt", muted, f)

    panel(draw, (560, 196, 1036, 560), "Solver Evidence Rail")
    rail_items = [
        ("Status", short_status(d3.get("status")), warn),
        ("Accepted", str(d3.get("accepted")).lower(), good if d3.get("accepted") else fail),
        ("Committed", str(d3.get("committed")).lower(), good if d3.get("committed") else fail),
        ("Rolled back", str(d3.get("rolled_back")).lower(), good if not d3.get("rolled_back") else fail),
        ("Report codes", str(len(d3.get("report_codes", []))), good),
    ]
    y = 252
    for label, value, color in rail_items:
        draw.rounded_rectangle((594, y, 1000, y + 42), radius=6, fill="#f7f4ec", outline=rail)
        text(draw, (614, y + 11), label, muted, f)
        draw.rounded_rectangle((812, y + 8, 982, y + 34), radius=5, fill=color)
        text(draw, (824, y + 12), value, "#fffefa", f_mono)
        y += 54
    text(draw, (594, 516), "D3 replay artifact: schema, stages, report codes, commit boundary", muted, f)

    panel(draw, (1066, 196, 1524, 560), "D2 Diagnostic Classes")
    cases = d2.get("cases", [])
    y = 252
    for case in cases[:5]:
        color = good if case.get("passed") else fail
        draw.rounded_rectangle((1096, y, 1494, y + 38), radius=6, fill="#f7f4ec", outline=rail)
        draw.ellipse((1112, y + 11, 1128, y + 27), fill=color)
        text(draw, (1140, y + 9), str(case.get("case_id", "")), ink, f)
        text(draw, (1356, y + 9), short_status(case.get("status") or "parse"), muted, f_mono)
        y += 48
    text(draw, (1096, 516), f"D2 JSON summary: {d2.get('passed_count')}/{d2.get('case_count')} cases passed", muted, f)

    panel(draw, (76, 594, 756, 884), "Replay Timeline")
    stages = [stage for stage in d3.get("stages", []) if isinstance(stage, dict)]
    start_x, start_y = 120, 690
    for idx, stage in enumerate(stages[:10]):
        x = start_x + idx * 58
        draw.line((x, start_y, x + 52, start_y), fill="#cfc6b8", width=2)
        fill = good if stage.get("stage_status") == "Ok" else warn
        draw.ellipse((x - 10, start_y - 10, x + 10, start_y + 10), fill=fill, outline="#181715")
        text(draw, (x - 10, start_y + 22), str(stage.get("order", idx)), muted, f_mono)
    text(draw, (120, 760), "Stages preserve command validation, planning, numeric solve, diagnostics, gluing, and commit.", muted, f)
    text(draw, (120, 792), "Durable mutation is visible at commit stage, not hidden in the visual layer.", muted, f)

    panel(draw, (786, 594, 1524, 884), "Research Boundary")
    bullets = [
        "Evidence-first: status, rank/residual, obstruction, replay, and commit are visible.",
        "Viewer truth boundary: UI observes artifacts; solver/runtime remain durable truth.",
        "Current limitation: this PNG is a deterministic evidence board, not the live Tkinter workbench.",
        "Next gate: produce a live workbench screenshot after visual QA and structured projection hardening.",
    ]
    y = 660
    for item in bullets:
        draw.ellipse((818, y + 6, 828, y + 16), fill="#806c98")
        text(draw, (844, y), item, muted, f)
        y += 44

    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output)


def write_manifest(output: Path, manifest: Path) -> dict[str, Any]:
    data = output.read_bytes()
    payload = {
        "schema_version": "gcs.screenshot_baselines.v1",
        "baselines": [
            {
                "id": "d5-solver-evidence-workbench-static",
                "path": repo_display(output),
                "width": 1600,
                "height": 980,
                "min_bytes": 50000,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        ],
    }
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--d2-summary", type=Path, default=DEFAULT_D2)
    parser.add_argument("--d3-replay", type=Path, default=DEFAULT_D3)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    d2_path = args.d2_summary if args.d2_summary.is_absolute() else ROOT / args.d2_summary
    d3_path = args.d3_replay if args.d3_replay.is_absolute() else ROOT / args.d3_replay
    output = args.output if args.output.is_absolute() else ROOT / args.output
    manifest = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest

    d2 = load_json(d2_path)
    d3 = load_json(d3_path)
    render(output, d2, d3)
    baseline = write_manifest(output, manifest)
    print(
        "[OK] D5 workbench package rendered -> "
        f"{repo_display(output)} ({baseline['baselines'][0]['bytes']} bytes)"
    )
    print(f"[OK] screenshot manifest -> {repo_display(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
