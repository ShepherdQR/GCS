#!/usr/bin/env python3
"""Render the GCS Figure 1 architecture SVG from a scene fixture.

The script is intentionally dependency-free. It reads a persisted GCS scene
fixture, computes simple geometric evidence for distance constraints, and
generates editorial SVG assets for the architecture atlas.
"""

from __future__ import annotations

import argparse
import html
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = ROOT / "fixtures" / "scene" / "saved" / "triangle_003_graph.json"
DEFAULT_OUT_DIR = ROOT / "docs" / "architecture" / "70-visualization" / "assets"


COLORS = {
    "ink": "#172033",
    "muted": "#5b677a",
    "rule": "#d7deea",
    "panel": "#ffffff",
    "paper": "#f7f9fc",
    "domain": "#e8f0ff",
    "domain_stroke": "#3157a4",
    "graph": "#efe8ff",
    "graph_stroke": "#7057b8",
    "planner": "#dcfbf4",
    "planner_stroke": "#0f766e",
    "numeric": "#e8f7df",
    "numeric_stroke": "#3a8a36",
    "diagnostic": "#fff3d6",
    "diagnostic_stroke": "#b7791f",
    "failure": "#fee2e2",
    "failure_stroke": "#b91c1c",
    "boundary": "#f3f4f6",
    "boundary_stroke": "#667085",
    "constraint": "#f59e0b",
    "point": "#274c9b",
    "ok": "#20966f",
}


CONSTRAINT_TYPE_NAMES = {
    0: "Coincident",
    1: "Parallel",
    2: "Perpendicular",
    3: "Distance",
    4: "Angle",
}


@dataclass(frozen=True)
class Geometry:
    id: int
    kind: int
    rigid_set_id: int | None
    xyz: tuple[float, float, float]


@dataclass(frozen=True)
class Constraint:
    id: int
    kind: int
    geometry_ids: tuple[int, ...]
    value: float | None


@dataclass(frozen=True)
class Evidence:
    constraint_id: int
    label: str
    actual: float | None
    target: float | None
    residual: float | None


@dataclass(frozen=True)
class Scene:
    geometries: list[Geometry]
    constraints: list[Constraint]
    evidence: list[Evidence]
    rank: int
    residual_dimension: int
    variable_dimension: int


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_scene(path: Path) -> Scene:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    geometries = []
    for raw in data.get("geometries", []):
        values = list(raw.get("v", [])) + [0.0, 0.0, 0.0]
        geometries.append(Geometry(
            id=int(raw["id"]),
            kind=int(raw.get("type", 0)),
            rigid_set_id=raw.get("rigid_set_id"),
            xyz=(float(values[0]), float(values[1]), float(values[2])),
        ))

    constraints = []
    for raw in data.get("constraints", []):
        constraints.append(Constraint(
            id=int(raw["id"]),
            kind=int(raw.get("type", -1)),
            geometry_ids=tuple(int(v) for v in raw.get("geometry_ids", [])),
            value=float(raw["value"]) if "value" in raw else None,
        ))

    by_id = {geometry.id: geometry for geometry in geometries}
    evidence = compute_evidence(constraints, by_id)
    jacobian = distance_jacobian(constraints, by_id, geometries)
    rank = matrix_rank(jacobian)
    return Scene(
        geometries=sorted(geometries, key=lambda item: item.id),
        constraints=sorted(constraints, key=lambda item: item.id),
        evidence=evidence,
        rank=rank,
        residual_dimension=len(jacobian),
        variable_dimension=3 * len(geometries),
    )


def compute_evidence(
    constraints: Iterable[Constraint],
    geometries: dict[int, Geometry],
) -> list[Evidence]:
    rows = []
    for constraint in sorted(constraints, key=lambda item: item.id):
        kind_name = CONSTRAINT_TYPE_NAMES.get(constraint.kind, f"Type {constraint.kind}")
        label = f"C{constraint.id} {kind_name}"
        actual = None
        residual = None
        if constraint.kind == 3 and len(constraint.geometry_ids) >= 2 and constraint.value is not None:
            first = geometries.get(constraint.geometry_ids[0])
            second = geometries.get(constraint.geometry_ids[1])
            if first and second:
                actual = distance(first.xyz, second.xyz)
                residual = actual - constraint.value
        rows.append(Evidence(
            constraint_id=constraint.id,
            label=label,
            actual=actual,
            target=constraint.value,
            residual=residual,
        ))
    return rows


def distance_jacobian(
    constraints: Iterable[Constraint],
    geometries: dict[int, Geometry],
    ordered_geometries: list[Geometry],
) -> list[list[float]]:
    offsets = {geometry.id: index * 3 for index, geometry in enumerate(ordered_geometries)}
    rows: list[list[float]] = []
    for constraint in sorted(constraints, key=lambda item: item.id):
        if constraint.kind != 3 or len(constraint.geometry_ids) < 2:
            continue
        left = geometries.get(constraint.geometry_ids[0])
        right = geometries.get(constraint.geometry_ids[1])
        if left is None or right is None:
            continue
        delta = tuple(left.xyz[i] - right.xyz[i] for i in range(3))
        length = math.sqrt(sum(value * value for value in delta))
        if length <= 1.0e-12:
            continue
        row = [0.0] * (3 * len(ordered_geometries))
        left_offset = offsets[left.id]
        right_offset = offsets[right.id]
        for i in range(3):
            derivative = delta[i] / length
            row[left_offset + i] = derivative
            row[right_offset + i] = -derivative
        rows.append(row)
    return rows


def matrix_rank(matrix: list[list[float]], tolerance: float = 1.0e-9) -> int:
    if not matrix:
        return 0
    rows = [row[:] for row in matrix]
    row_count = len(rows)
    column_count = len(rows[0])
    rank = 0
    for column in range(column_count):
        pivot = None
        best_value = tolerance
        for row in range(rank, row_count):
            value = abs(rows[row][column])
            if value > best_value:
                pivot = row
                best_value = value
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][column]
        rows[rank] = [value / pivot_value for value in rows[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = rows[row][column]
            if abs(factor) <= tolerance:
                continue
            rows[row] = [
                rows[row][index] - factor * rows[rank][index]
                for index in range(column_count)
            ]
        rank += 1
        if rank == row_count:
            break
    return rank


def distance(left: tuple[float, float, float], right: tuple[float, float, float]) -> float:
    return math.sqrt(sum((left[index] - right[index]) ** 2 for index in range(3)))


def point_layout(scene: Scene, width: float, height: float, pad: float) -> dict[int, tuple[float, float]]:
    xs = [geometry.xyz[0] for geometry in scene.geometries] or [0.0]
    ys = [geometry.xyz[1] for geometry in scene.geometries] or [0.0]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1.0e-9)
    span_y = max(max_y - min_y, 1.0e-9)
    usable_w = width - 2 * pad
    usable_h = height - 2 * pad
    scale = min(usable_w / span_x, usable_h / span_y)
    used_w = span_x * scale
    used_h = span_y * scale
    offset_x = (width - used_w) / 2
    offset_y = (height - used_h) / 2
    layout = {}
    for geometry in scene.geometries:
        x = offset_x + (geometry.xyz[0] - min_x) * scale
        y = height - (offset_y + (geometry.xyz[1] - min_y) * scale)
        layout[geometry.id] = (x, y)
    return layout


def svg_rect(x: float, y: float, w: float, h: float, fill: str, stroke: str, rx: float = 8.0) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.1"/>'
    )


def svg_text(
    text: str,
    x: float,
    y: float,
    size: int = 13,
    weight: int = 400,
    fill: str | None = None,
    anchor: str = "start",
) -> str:
    color = fill or COLORS["ink"]
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Inter, Segoe UI, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">'
        f'{escape(text)}</text>'
    )


def svg_line(x1: float, y1: float, x2: float, y2: float, stroke: str, width: float = 1.6, dash: str = "") -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{stroke}" stroke-width="{width:.1f}" stroke-linecap="round"{dash_attr}/>'
    )


def svg_arrow(x1: float, y1: float, x2: float, y2: float, stroke: str, width: float = 1.4, dash: str = "") -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{stroke}" stroke-width="{width:.1f}" stroke-linecap="round" '
        f'marker-end="url(#arrow)"{dash_attr}/>'
    )


def panel_frame(label: str, title: str, width: int, height: int) -> list[str]:
    return [
        svg_rect(0, 0, width, height, COLORS["panel"], COLORS["rule"], rx=10),
        svg_text(label, 18, 29, size=22, weight=700),
        svg_text(title, 48, 27, size=15, weight=650),
    ]


def geometry_panel(scene: Scene, width: int = 360, height: int = 260) -> str:
    parts = panel_frame("a", "Geometry fixture", width, height)
    plot_x, plot_y, plot_w, plot_h = 22, 52, width - 44, height - 78
    parts.append(svg_rect(plot_x, plot_y, plot_w, plot_h, "#fbfcff", "#e5eaf3", rx=8))
    layout = point_layout(scene, plot_w, plot_h, 32)
    evidence_by_constraint = {item.constraint_id: item for item in scene.evidence}

    for constraint in scene.constraints:
        if len(constraint.geometry_ids) < 2:
            continue
        first = layout.get(constraint.geometry_ids[0])
        second = layout.get(constraint.geometry_ids[1])
        if not first or not second:
            continue
        x1, y1 = plot_x + first[0], plot_y + first[1]
        x2, y2 = plot_x + second[0], plot_y + second[1]
        parts.append(svg_line(x1, y1, x2, y2, COLORS["constraint"], width=2.4))
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        evidence = evidence_by_constraint.get(constraint.id)
        residual = 0.0 if not evidence or evidence.residual is None else evidence.residual
        label = f"C{constraint.id} r={residual:+.2g}"
        parts.append(svg_text(label, mid_x, mid_y - 6, size=11, fill=COLORS["muted"], anchor="middle"))

    for geometry in scene.geometries:
        x, y = layout[geometry.id]
        sx, sy = plot_x + x, plot_y + y
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="7.0" fill="{COLORS["point"]}" stroke="#ffffff" stroke-width="2"/>')
        parts.append(svg_text(f"G{geometry.id}", sx, sy - 13, size=12, weight=650, anchor="middle"))
        parts.append(svg_text(f"RS{geometry.rigid_set_id}", sx, sy + 22, size=10, fill=COLORS["muted"], anchor="middle"))

    parts.append(svg_text(f"{len(scene.geometries)} geometries, {len(scene.constraints)} constraints", 24, height - 18, size=12, fill=COLORS["muted"]))
    return "\n".join(parts)


def incidence_panel(scene: Scene, width: int = 360, height: int = 260) -> str:
    parts = panel_frame("b", "Incidence hypergraph", width, height)
    left_x, right_x = 84, width - 92
    top_y = 72
    spacing = 46
    geometry_y = {geometry.id: top_y + index * spacing for index, geometry in enumerate(scene.geometries)}
    constraint_y = {constraint.id: top_y + index * spacing for index, constraint in enumerate(scene.constraints)}

    parts.append(svg_text("geometry IDs", left_x, 58, size=11, fill=COLORS["muted"], anchor="middle"))
    parts.append(svg_text("constraint IDs", right_x, 58, size=11, fill=COLORS["muted"], anchor="middle"))

    for constraint in scene.constraints:
        cy = constraint_y[constraint.id]
        for geometry_id in constraint.geometry_ids:
            gy = geometry_y.get(geometry_id)
            if gy is None:
                continue
            parts.append(svg_line(left_x + 34, gy, right_x - 34, cy, COLORS["graph_stroke"], width=1.25, dash="4 4"))

    for geometry in scene.geometries:
        y = geometry_y[geometry.id]
        parts.append(svg_rect(left_x - 35, y - 16, 70, 32, COLORS["domain"], COLORS["domain_stroke"], rx=16))
        parts.append(svg_text(f"G{geometry.id}", left_x, y + 5, size=13, weight=650, anchor="middle"))

    for constraint in scene.constraints:
        y = constraint_y[constraint.id]
        parts.append(svg_rect(right_x - 37, y - 16, 74, 32, COLORS["diagnostic"], COLORS["diagnostic_stroke"], rx=16))
        parts.append(svg_text(f"C{constraint.id}", right_x, y + 5, size=13, weight=650, anchor="middle"))

    parts.append(svg_text("hyperedges preserve stable IDs before solving", width / 2, height - 18, size=12, fill=COLORS["muted"], anchor="middle"))
    return "\n".join(parts)


def evidence_panel(scene: Scene, width: int = 460, height: int = 260) -> str:
    parts = panel_frame("c", "Residual and rank evidence", width, height)
    chart_x, chart_y = 28, 68
    chart_w, chart_h = 190, 132
    max_residual = max([abs(item.residual or 0.0) for item in scene.evidence] + [1.0e-9])
    residual_scale = max(max_residual, 1.0e-6)

    parts.append(svg_text("per-constraint |residual|", chart_x, chart_y - 12, size=11, fill=COLORS["muted"]))
    for index, item in enumerate(scene.evidence):
        y = chart_y + index * 34
        value = abs(item.residual or 0.0)
        bar_w = chart_w * min(value / residual_scale, 1.0)
        bar_w = max(bar_w, 3.0 if value <= 1.0e-9 else bar_w)
        fill = COLORS["ok"] if value <= 1.0e-6 else COLORS["failure_stroke"]
        parts.append(svg_text(f"C{item.constraint_id}", chart_x, y + 14, size=12, weight=650))
        parts.append(svg_rect(chart_x + 34, y, chart_w, 18, "#eef2f7", "#e1e7ef", rx=4))
        parts.append(svg_rect(chart_x + 34, y, bar_w, 18, fill, fill, rx=4))
        parts.append(svg_text(f"{value:.2e}", chart_x + chart_w + 46, y + 14, size=11, fill=COLORS["muted"]))

    rank_x = 305
    nullity = max(scene.variable_dimension - scene.rank, 0)
    parts.append(svg_rect(rank_x, 68, 128, 132, COLORS["numeric"], COLORS["numeric_stroke"], rx=8))
    parts.append(svg_text("J rank", rank_x + 18, 94, size=12, fill=COLORS["muted"]))
    parts.append(svg_text(f"{scene.rank}", rank_x + 18, 126, size=34, weight=700, fill=COLORS["numeric_stroke"]))
    parts.append(svg_text(f"/ {scene.residual_dimension} equations", rank_x + 68, 122, size=12, fill=COLORS["muted"]))
    parts.append(svg_line(rank_x + 18, 140, rank_x + 110, 140, "#c8e4be", width=1.0))
    parts.append(svg_text(f"vars {scene.variable_dimension}", rank_x + 18, 164, size=12, fill=COLORS["muted"]))
    parts.append(svg_text(f"nullity {nullity}", rank_x + 18, 185, size=12, fill=COLORS["muted"]))
    parts.append(svg_text("numeric evidence is a report, not a commit", 28, height - 18, size=12, fill=COLORS["muted"]))
    return "\n".join(parts)


def pipeline_panel(width: int = 520, height: int = 195) -> str:
    stages = [
        ("Intake", "domain"),
        ("Normalize", "domain"),
        ("Validate", "domain"),
        ("Index", "graph"),
        ("Decompose", "planner"),
        ("Diagnose", "diagnostic"),
        ("Plan", "planner"),
        ("Solve", "numeric"),
        ("Assemble", "planner"),
        ("Verify", "diagnostic"),
        ("Commit", "diagnostic"),
        ("Report", "boundary"),
    ]
    parts = panel_frame("d", "Runtime contract pipeline", width, height)
    x0, y0 = 24, 70
    box_w, box_h, gap = 72, 34, 10
    for index, (name, token) in enumerate(stages):
        row = index // 6
        col = index % 6
        x = x0 + col * (box_w + gap)
        y = y0 + row * 58
        fill = COLORS[token]
        stroke = COLORS.get(f"{token}_stroke", COLORS["boundary_stroke"])
        parts.append(svg_rect(x, y, box_w, box_h, fill, stroke, rx=7))
        parts.append(svg_text(name, x + box_w / 2, y + 22, size=11, weight=650, anchor="middle"))
        if col < 5:
            parts.append(svg_arrow(x + box_w + 2, y + 17, x + box_w + gap - 2, y + 17, COLORS["muted"], width=1.1))
        elif row == 0:
            parts.append(svg_arrow(x + box_w / 2, y + box_h + 4, x + box_w / 2, y + 54, COLORS["muted"], width=1.1))
    parts.append(svg_text("Each stage contributes typed evidence or a typed rejection.", 24, height - 18, size=12, fill=COLORS["muted"]))
    return "\n".join(parts)


def local_to_global_panel(width: int = 640, height: int = 330) -> str:
    parts = panel_frame("e", "Local-to-global solve semantics", width, height)
    y = 74
    nodes = [
        (28, y, 116, 48, "ModelSnapshot", "stable IDs", "domain"),
        (176, y, 116, 48, "CoverPlan", "contexts", "planner"),
        (324, y, 116, 48, "NumericTask[]", "local problems", "numeric"),
        (472, y, 132, 48, "LocalSection[]", "proposals", "numeric"),
    ]
    for x, y0, w, h, title, subtitle, token in nodes:
        parts.append(svg_rect(x, y0, w, h, COLORS[token], COLORS.get(f"{token}_stroke", COLORS["boundary_stroke"]), rx=8))
        parts.append(svg_text(title, x + w / 2, y0 + 20, size=12, weight=650, anchor="middle"))
        parts.append(svg_text(subtitle, x + w / 2, y0 + 38, size=10, fill=COLORS["muted"], anchor="middle"))
    for x in (144, 292, 440):
        parts.append(svg_arrow(x + 4, 98, x + 28, 98, COLORS["muted"]))

    cover_y = 168
    parts.append(svg_text("context cover", 48, cover_y - 18, size=12, fill=COLORS["muted"]))
    parts.append(svg_rect(36, cover_y, 126, 78, "#fafdff", COLORS["planner_stroke"], rx=8))
    parts.append(f'<ellipse cx="84" cy="{cover_y + 38}" rx="38" ry="24" fill="{COLORS["planner"]}" stroke="{COLORS["planner_stroke"]}" stroke-width="1.2"/>')
    parts.append(f'<ellipse cx="114" cy="{cover_y + 38}" rx="38" ry="24" fill="#e6f7ff" stroke="{COLORS["domain_stroke"]}" stroke-width="1.2" fill-opacity="0.75"/>')
    parts.append(svg_text("overlap", 98, cover_y + 43, size=10, fill=COLORS["muted"], anchor="middle"))

    parts.append(svg_text("boundary projections", 210, cover_y - 18, size=12, fill=COLORS["muted"]))
    parts.append(svg_rect(200, cover_y, 140, 78, "#fbfcff", COLORS["rule"], rx=8))
    parts.append(svg_arrow(226, cover_y + 24, 310, cover_y + 24, COLORS["planner_stroke"], dash="5 4"))
    parts.append(svg_arrow(226, cover_y + 54, 310, cover_y + 54, COLORS["planner_stroke"], dash="5 4"))
    parts.append(svg_text("restrict local state", 270, cover_y + 43, size=10, fill=COLORS["muted"], anchor="middle"))

    parts.append(svg_text("gluing and transaction", 392, cover_y - 18, size=12, fill=COLORS["muted"]))
    parts.append(svg_rect(382, cover_y, 220, 78, COLORS["diagnostic"], COLORS["diagnostic_stroke"], rx=8))
    parts.append(svg_text("GluingReport: compatible overlaps", 492, cover_y + 30, size=12, weight=650, anchor="middle"))
    parts.append(svg_text("CommandResult: accept or reject", 492, cover_y + 55, size=12, fill=COLORS["muted"], anchor="middle"))

    parts.append(svg_arrow(162, cover_y + 39, 196, cover_y + 39, COLORS["muted"]))
    parts.append(svg_arrow(340, cover_y + 39, 378, cover_y + 39, COLORS["muted"]))
    parts.append(svg_text("A local numeric section is never a durable commit by itself.", 30, height - 24, size=12, fill=COLORS["muted"]))
    return "\n".join(parts)


def legend_panel(width: int = 520, height: int = 126) -> str:
    parts = panel_frame("f", "Visual grammar", width, height)
    items = [
        ("domain", "stable model truth"),
        ("graph", "incidence structure"),
        ("planner", "cover / gluing"),
        ("numeric", "residual / rank"),
        ("diagnostic", "reports / decision"),
        ("boundary", "IO / viewer boundary"),
    ]
    for index, (token, label) in enumerate(items):
        row = index // 3
        col = index % 3
        x = 28 + col * 165
        y = 58 + row * 34
        parts.append(svg_rect(x, y - 16, 26, 18, COLORS[token], COLORS.get(f"{token}_stroke", COLORS["boundary_stroke"]), rx=4))
        parts.append(svg_text(label, x + 36, y - 2, size=11, fill=COLORS["muted"]))
    return "\n".join(parts)


def wrap_svg(content: str, width: int, height: int, title: str) -> str:
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">',
        f'<title id="title">{escape(title)}</title>',
        "<defs>",
        '<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth">',
        f'<path d="M0,0 L8,4 L0,8 Z" fill="{COLORS["muted"]}"/>',
        "</marker>",
        "</defs>",
        content,
        "</svg>",
        "",
    ])


def final_figure(scene: Scene, fixture_label: str) -> str:
    width, height = 1280, 900
    parts = [
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{COLORS["paper"]}"/>',
        svg_text("Figure 1 | GCS Local-To-Global Constraint Solving", 40, 52, size=26, weight=720),
        svg_text("Structural source: Mermaid architecture atlas. Data panels generated from a scene fixture.", 40, 78, size=13, fill=COLORS["muted"]),
        svg_text(f"Fixture: {fixture_label}", width - 40, 78, size=12, fill=COLORS["muted"], anchor="end"),
        f'<g transform="translate(40 110)">{geometry_panel(scene, 360, 260)}</g>',
        f'<g transform="translate(410 110)">{incidence_panel(scene, 360, 260)}</g>',
        f'<g transform="translate(780 110)">{evidence_panel(scene, 460, 260)}</g>',
        f'<g transform="translate(40 420)">{pipeline_panel(520, 195)}</g>',
        f'<g transform="translate(600 420)">{local_to_global_panel(640, 330)}</g>',
        f'<g transform="translate(40 650)">{legend_panel(520, 126)}</g>',
        svg_text(
            "Design claim: GCS accepts only globally verified proposals whose local sections glue over declared overlaps.",
            40,
            842,
            size=15,
            weight=650,
        ),
        svg_text(
            "Geometry, incidence, residuals, rank, gluing, and transaction status are all first-class reports.",
            40,
            867,
            size=13,
            fill=COLORS["muted"],
        ),
    ]
    return wrap_svg("\n".join(parts), width, height, "GCS Local-To-Global Constraint Solving")


def write_svg(path: Path, content: str, width: int, height: int, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(wrap_svg(content, width, height, title), encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render GCS Figure 1 architecture SVG assets.")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE, help="Scene fixture JSON path.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Output asset directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixture = args.fixture if args.fixture.is_absolute() else ROOT / args.fixture
    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    scene = load_scene(fixture)

    outputs = {
        "figure1-panel-a-geometry.svg": wrap_svg(
            geometry_panel(scene, 360, 260),
            360,
            260,
            "GCS geometry fixture panel",
        ),
        "figure1-panel-b-incidence.svg": wrap_svg(
            incidence_panel(scene, 360, 260),
            360,
            260,
            "GCS incidence hypergraph panel",
        ),
        "figure1-panel-c-residual-rank.svg": wrap_svg(
            evidence_panel(scene, 460, 260),
            460,
            260,
            "GCS residual and rank evidence panel",
        ),
        "figure1-gcs-local-to-global.svg": final_figure(scene, fixture.relative_to(ROOT).as_posix()),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        (out_dir / name).write_text(content, encoding="utf-8", newline="\n")
        print(out_dir / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
