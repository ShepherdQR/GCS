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
DEFAULT_THEME = Path(__file__).with_name("figure1.theme.json")
DEFAULT_LAYOUT = Path(__file__).with_name("figure1.layout.json")


def load_theme_colors(path: Path = DEFAULT_THEME) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    colors = data.get("colors", {}) if isinstance(data, dict) else {}
    if not isinstance(colors, dict):
        raise ValueError(f"{path} must define a colors object")
    return {str(key): str(value) for key, value in colors.items()}


COLORS = load_theme_colors()


SANS = "Anthropic Sans, Inter, Segoe UI, Arial, sans-serif"
SERIF = "Anthropic Serif, Georgia, Cambria, Times New Roman, serif"
THEME: dict[str, object] = {}
LAYOUT: dict[str, object] = {}


CONSTRAINT_TYPE_NAMES = {
    0: "Coincident",
    1: "Parallel",
    2: "Perpendicular",
    3: "Distance",
    4: "Angle",
}


def deep_merge(base: dict[str, object], override: dict[str, object]) -> dict[str, object]:
    merged = dict(base)
    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = deep_merge(current, value)
        else:
            merged[key] = value
    return merged


def load_json_if_exists(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def config_value(source: dict[str, object], dotted_path: str, default: object) -> object:
    current: object = source
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return default
    return current


def layout_value(dotted_path: str, default: object) -> object:
    return config_value(LAYOUT, dotted_path, default)


def lf(dotted_path: str, default: float) -> float:
    return float(layout_value(dotted_path, default))


def li(dotted_path: str, default: int) -> int:
    return int(round(lf(dotted_path, float(default))))


def theme_value(dotted_path: str, default: object) -> object:
    return config_value(THEME, dotted_path, default)


def load_design_controls(theme_path: Path, layout_path: Path) -> None:
    global COLORS, SANS, SERIF, THEME, LAYOUT

    fallback_theme: dict[str, object] = {
        "colors": COLORS,
        "fonts": {
            "sans": SANS,
            "serif": SERIF,
        },
        "radii": {
            "panel": 8,
            "plot": 8,
            "card": 6,
            "pill": 12,
            "small": 4,
        },
        "strokes": {
            "default": 1.1,
            "grid": 1.0,
            "arrow": 1.4,
            "constraint": 2.4,
        },
    }
    THEME = deep_merge(fallback_theme, load_json_if_exists(theme_path))
    raw_colors = theme_value("colors", COLORS)
    if not isinstance(raw_colors, dict):
        raise ValueError("theme colors must be a JSON object")
    COLORS = {str(key): str(value) for key, value in raw_colors.items()}
    SANS = str(theme_value("fonts.sans", SANS))
    SERIF = str(theme_value("fonts.serif", SERIF))
    LAYOUT = load_json_if_exists(layout_path)


def svg_attrs(element_id: str | None = None, layout_key: str | None = None) -> str:
    attrs = []
    if element_id:
        attrs.append(f'id="{escape(element_id)}"')
    if layout_key:
        attrs.append(f'data-layout-key="{escape(layout_key)}"')
    return (" " + " ".join(attrs)) if attrs else ""


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
    free_variable_dimension: int
    frozen_variable_dimension: int


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
    variable_dimension = 3 * len(geometries)
    return Scene(
        geometries=sorted(geometries, key=lambda item: item.id),
        constraints=sorted(constraints, key=lambda item: item.id),
        evidence=evidence,
        rank=rank,
        residual_dimension=len(jacobian),
        variable_dimension=variable_dimension,
        free_variable_dimension=variable_dimension,
        frozen_variable_dimension=0,
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


def svg_rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    stroke: str,
    rx: float = 8.0,
    element_id: str | None = None,
    layout_key: str | None = None,
) -> str:
    stroke_width = float(theme_value("strokes.default", 1.1))
    return (
        f'<rect{svg_attrs(element_id, layout_key)} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:.1f}"/>'
    )


def svg_text(
    text: str,
    x: float,
    y: float,
    size: int = 13,
    weight: int = 400,
    fill: str | None = None,
    anchor: str = "start",
    family: str | None = None,
) -> str:
    color = fill or COLORS["ink"]
    font_family = family or SANS
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font_family}" '
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
    frame = "panels.frame"
    panel_rx = float(theme_value("radii.panel", 8))
    return [
        svg_rect(0, 0, width, height, COLORS["panel"], COLORS["rule"], rx=panel_rx, element_id=f"panel-{label}-frame"),
        svg_text(label, lf(f"{frame}.label_x", 18), lf(f"{frame}.label_y", 29), size=li(f"{frame}.label_size", 22), weight=700, fill=COLORS["accent"], family=SERIF),
        svg_text(title, lf(f"{frame}.title_x", 48), lf(f"{frame}.title_y", 27), size=li(f"{frame}.title_size", 15), weight=650),
    ]


def geometry_panel(scene: Scene, width: int = 430, height: int = 300) -> str:
    parts = panel_frame("a", "Geometry fixture", width, height)
    panel = "panels.geometry"
    plot_x = lf(f"{panel}.plot.x", 24)
    plot_y = lf(f"{panel}.plot.y", 58)
    plot_w = lf(f"{panel}.plot.width", 244)
    plot_h = lf(f"{panel}.plot.height", height - 110)
    plot_rx = float(theme_value("radii.plot", 8))
    parts.append(svg_rect(
        plot_x,
        plot_y,
        plot_w,
        plot_h,
        COLORS["plot"],
        COLORS["rule_soft"],
        rx=plot_rx,
        element_id="panel-a-geometry-plot",
        layout_key="panels.geometry.plot",
    ))
    layout = point_layout(scene, plot_w, plot_h, lf(f"{panel}.plot.pad", 34))
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

    for geometry in scene.geometries:
        x, y = layout[geometry.id]
        sx, sy = plot_x + x, plot_y + y
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="8.0" fill="{COLORS["point"]}" stroke="{COLORS["white"]}" stroke-width="2"/>')
        label_y = sy - 16 if sy > plot_y + 30 else sy + 25
        parts.append(svg_rect(sx - 17, label_y - 14, 34, 18, COLORS["panel"], COLORS["rule"], rx=8))
        parts.append(svg_text(f"G{geometry.id}", sx, label_y, size=10, weight=650, anchor="middle"))

    legend_x = lf(f"{panel}.evidence_title.x", 286)
    parts.append(svg_text("constraint evidence", legend_x, lf(f"{panel}.evidence_title.y", 62), size=11, weight=650, fill=COLORS["muted"]))
    for index, constraint in enumerate(scene.constraints):
        card_x = lf(f"{panel}.evidence_card.x", legend_x)
        card_y = lf(f"{panel}.evidence_card.y", 76) + index * lf(f"{panel}.evidence_card.gap", 58)
        card_w = lf(f"{panel}.evidence_card.width", 128)
        card_h = lf(f"{panel}.evidence_card.height", 50)
        evidence = evidence_by_constraint.get(constraint.id)
        residual = 0.0 if not evidence or evidence.residual is None else evidence.residual
        target = "-" if not evidence or evidence.target is None else f"{evidence.target:.3g}"
        actual = "-" if not evidence or evidence.actual is None else f"{evidence.actual:.3g}"
        endpoints = "-".join(f"G{geometry_id}" for geometry_id in constraint.geometry_ids)
        parts.append(svg_rect(
            card_x,
            card_y,
            card_w,
            card_h,
            COLORS["surface"],
            COLORS["rule_soft"],
            rx=float(theme_value("radii.card", 6)),
            element_id=f"panel-a-evidence-card-{index}",
            layout_key="panels.geometry.evidence_card" if index == 0 else None,
        ))
        parts.append(svg_text(f"C{constraint.id}", card_x + 10, card_y + 17, size=11, weight=650))
        parts.append(svg_text(endpoints, card_x + 44, card_y + 17, size=9, fill=COLORS["muted"]))
        parts.append(svg_text(f"target {target}  actual {actual}", card_x + 10, card_y + 32, size=8, fill=COLORS["muted"]))
        parts.append(svg_text(f"residual {residual:+.1e}", card_x + 10, card_y + 45, size=8, fill=COLORS["muted"]))

    parts.append(svg_text(
        f"{len(scene.geometries)} geometries, {len(scene.constraints)} constraints, stable IDs",
        lf(f"{panel}.footer.x", 24),
        height - lf(f"{panel}.footer.bottom", 18),
        size=12,
        fill=COLORS["muted"],
    ))
    return "\n".join(parts)


def incidence_panel(scene: Scene, width: int = 430, height: int = 300) -> str:
    parts = panel_frame("b", "Incidence matrix and site base", width, height)
    panel = "panels.incidence"
    matrix_x = lf(f"{panel}.matrix.x", 128)
    matrix_y = lf(f"{panel}.matrix.y", 100)
    cell = lf(f"{panel}.matrix.cell", 48)

    parts.append(svg_text("constraint columns", matrix_x + cell, 54, size=11, fill=COLORS["muted"], anchor="middle"))
    parts.append(svg_text("geometry rows", 58, 78, size=11, fill=COLORS["muted"], anchor="middle"))

    for index, constraint in enumerate(scene.constraints):
        x = matrix_x + index * cell
        parts.append(svg_rect(x - 18, matrix_y - 38, 36, 24, COLORS["diagnostic"], COLORS["diagnostic_stroke"], rx=12))
        parts.append(svg_text(f"C{constraint.id}", x, matrix_y - 22, size=11, weight=650, anchor="middle"))

    for row, geometry in enumerate(scene.geometries):
        y = matrix_y + row * cell
        parts.append(svg_rect(34, y - 16, 48, 28, COLORS["domain"], COLORS["domain_stroke"], rx=14))
        parts.append(svg_text(f"G{geometry.id}", 58, y + 3, size=11, weight=650, anchor="middle"))
        parts.append(svg_line(matrix_x - 28, y, matrix_x + cell * (len(scene.constraints) - 1) + 28, y, COLORS["rule_soft"], width=1.0))

    for index, constraint in enumerate(scene.constraints):
        x = matrix_x + index * cell
        parts.append(svg_line(x, matrix_y - 8, x, matrix_y + cell * (len(scene.geometries) - 1) + 22, COLORS["rule_soft"], width=1.0))
        for geometry_id in constraint.geometry_ids:
            row = next((i for i, geometry in enumerate(scene.geometries) if geometry.id == geometry_id), None)
            if row is None:
                continue
            y = matrix_y + row * cell
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7.0" fill="{COLORS["graph_stroke"]}" stroke="{COLORS["white"]}" stroke-width="2"/>')

    site_x = lf(f"{panel}.site.x", 288)
    site_y = lf(f"{panel}.site.y", 82)
    site_w = lf(f"{panel}.site.width", 100)
    site_h = lf(f"{panel}.site.height", 118)
    parts.append(svg_text("finite site C", site_x + 50, site_y - 14, size=11, weight=650, fill=COLORS["muted"], anchor="middle"))
    parts.append(svg_rect(site_x, site_y, site_w, site_h, COLORS["surface"], COLORS["rule_soft"], rx=8, element_id="panel-b-finite-site", layout_key="panels.incidence.site"))
    parts.append(svg_rect(site_x + 28, site_y + 10, 44, 24, COLORS["domain"], COLORS["domain_stroke"], rx=12))
    parts.append(svg_text("X", site_x + 50, site_y + 27, size=11, weight=650, anchor="middle"))
    parts.append(svg_rect(site_x + 10, site_y + 58, 38, 24, COLORS["planner"], COLORS["planner_stroke"], rx=12))
    parts.append(svg_text("Ua", site_x + 29, site_y + 75, size=10, weight=650, anchor="middle"))
    parts.append(svg_rect(site_x + 52, site_y + 58, 38, 24, COLORS["cool_domain"], COLORS["domain_stroke"], rx=12))
    parts.append(svg_text("Ub", site_x + 71, site_y + 75, size=10, weight=650, anchor="middle"))
    parts.append(svg_rect(site_x + 31, site_y + 88, 38, 22, COLORS["graph"], COLORS["graph_stroke"], rx=11))
    parts.append(svg_text("Uab", site_x + 50, site_y + 103, size=9, weight=650, anchor="middle"))
    parts.append(svg_arrow(site_x + 38, site_y + 58, site_x + 45, site_y + 36, COLORS["muted"], width=1.0))
    parts.append(svg_arrow(site_x + 62, site_y + 58, site_x + 55, site_y + 36, COLORS["muted"], width=1.0))
    parts.append(svg_arrow(site_x + 43, site_y + 88, site_x + 32, site_y + 82, COLORS["muted"], width=1.0))
    parts.append(svg_arrow(site_x + 57, site_y + 88, site_x + 68, site_y + 82, COLORS["muted"], width=1.0))

    parts.append(svg_text("incidence builds the base category for covers", width / 2, height - lf(f"{panel}.footer_bottom", 18), size=12, fill=COLORS["muted"], anchor="middle"))
    return "\n".join(parts)


def evidence_panel(scene: Scene, width: int = 520, height: int = 300) -> str:
    parts = panel_frame("c", "Residual and rank evidence", width, height)
    panel = "panels.evidence"
    chart_x = lf(f"{panel}.chart.x", 30)
    chart_y = lf(f"{panel}.chart.y", 76)
    chart_w = lf(f"{panel}.chart.width", 220)
    row_gap = lf(f"{panel}.chart.row_gap", 34)
    bar_h = lf(f"{panel}.chart.bar_height", 18)
    max_residual = max([abs(item.residual or 0.0) for item in scene.evidence] + [1.0e-9])
    residual_scale = max(max_residual, 1.0e-6)

    parts.append(svg_text("per-constraint |residual|", chart_x, chart_y - 12, size=11, fill=COLORS["muted"]))
    for index, item in enumerate(scene.evidence):
        y = chart_y + index * row_gap
        value = abs(item.residual or 0.0)
        bar_w = chart_w * min(value / residual_scale, 1.0)
        bar_w = max(bar_w, 3.0 if value <= 1.0e-9 else bar_w)
        fill = COLORS["ok"] if value <= 1.0e-6 else COLORS["failure_stroke"]
        parts.append(svg_text(f"C{item.constraint_id}", chart_x, y + 14, size=12, weight=650))
        parts.append(svg_rect(chart_x + 34, y, chart_w, bar_h, COLORS["bar_track"], COLORS["rule_soft"], rx=float(theme_value("radii.small", 4)), element_id=f"panel-c-residual-track-{index}"))
        parts.append(svg_rect(chart_x + 34, y, bar_w, bar_h, fill, fill, rx=float(theme_value("radii.small", 4))))
        parts.append(svg_text(f"{value:.2e}", chart_x + chart_w + 50, y + 14, size=11, fill=COLORS["muted"]))

    rank_x = lf(f"{panel}.rank_card.x", 342)
    rank_y = lf(f"{panel}.rank_card.y", 76)
    rank_w = lf(f"{panel}.rank_card.width", 154)
    rank_h = lf(f"{panel}.rank_card.height", 176)
    nullity = max(scene.free_variable_dimension - scene.rank, 0)
    parts.append(svg_rect(rank_x, rank_y, rank_w, rank_h, COLORS["numeric"], COLORS["numeric_stroke"], rx=8, element_id="panel-c-rank-card", layout_key="panels.evidence.rank_card"))
    parts.append(svg_text("Free-column rank", rank_x + 16, rank_y + 25, size=11, fill=COLORS["muted"]))
    parts.append(svg_text(f"{scene.rank}", rank_x + 16, rank_y + 61, size=34, weight=700, fill=COLORS["numeric_stroke"]))
    parts.append(svg_text(f"/ {scene.residual_dimension} eqs", rank_x + 63, rank_y + 56, size=11, fill=COLORS["muted"]))
    parts.append(svg_line(rank_x + 16, rank_y + 76, rank_x + rank_w - 16, rank_y + 76, COLORS["numeric_stroke"], width=1.0))
    parts.append(svg_text(f"full vars {scene.variable_dimension}", rank_x + 16, rank_y + 98, size=10, fill=COLORS["muted"]))
    parts.append(svg_text(f"free cols {scene.free_variable_dimension}", rank_x + 16, rank_y + 119, size=10, fill=COLORS["muted"]))
    parts.append(svg_text(f"frozen cols {scene.frozen_variable_dimension}", rank_x + 16, rank_y + 140, size=10, fill=COLORS["muted"]))
    parts.append(svg_text(f"nullity {nullity}", rank_x + 16, rank_y + 161, size=10, fill=COLORS["muted"]))
    parts.append(svg_text("numeric evidence is a report, not a commit", lf(f"{panel}.footer.x", 30), height - lf(f"{panel}.footer.bottom", 18), size=12, fill=COLORS["muted"]))
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
    panel = "panels.pipeline"
    x0 = lf(f"{panel}.stage_grid.x", 24)
    y0 = lf(f"{panel}.stage_grid.y", 70)
    box_w = lf(f"{panel}.stage_grid.box_width", 72)
    box_h = lf(f"{panel}.stage_grid.box_height", 34)
    gap = lf(f"{panel}.stage_grid.gap", 10)
    columns = li(f"{panel}.stage_grid.columns", 6)
    row_gap = lf(f"{panel}.stage_grid.row_gap", 58)
    for index, (name, token) in enumerate(stages):
        row = index // columns
        col = index % columns
        x = x0 + col * (box_w + gap)
        y = y0 + row * row_gap
        fill = COLORS[token]
        stroke = COLORS.get(f"{token}_stroke", COLORS["boundary_stroke"])
        parts.append(svg_rect(x, y, box_w, box_h, fill, stroke, rx=7))
        parts.append(svg_text(name, x + box_w / 2, y + 22, size=11, weight=650, anchor="middle"))
        if col < columns - 1:
            parts.append(svg_arrow(x + box_w + 2, y + 17, x + box_w + gap - 2, y + 17, COLORS["muted"], width=1.1))
        elif row == 0:
            parts.append(svg_arrow(x + box_w / 2, y + box_h + 4, x + box_w / 2, y + 54, COLORS["muted"], width=1.1))
    parts.append(svg_text("Each stage contributes typed evidence or a typed rejection.", lf(f"{panel}.footer.x", 24), height - lf(f"{panel}.footer.bottom", 18), size=12, fill=COLORS["muted"]))
    return "\n".join(parts)


def topos_semantics_panel(width: int = 780, height: int = 360) -> str:
    parts = panel_frame("e", "Topos semantics: finite site, sections, gluing", width, height)
    panel = "panels.topos"
    default_columns = [
        {"x": 28, "y": 66, "width": 176, "height": 200},
        {"x": 228, "y": 66, "width": 220, "height": 200},
        {"x": 472, "y": 66, "width": 280, "height": 200},
    ]
    column_layouts = layout_value(f"{panel}.columns", default_columns)
    if not isinstance(column_layouts, list):
        column_layouts = default_columns
    column_labels = [
        ("1 Finite site C", "contexts and overlaps", "domain"),
        ("2 Presheaf F", "restriction maps", "planner"),
        ("3 Sheaf condition", "gluing or obstruction", "diagnostic"),
    ]
    for index, (title, subtitle, token) in enumerate(column_labels):
        raw = column_layouts[index] if index < len(column_layouts) and isinstance(column_layouts[index], dict) else default_columns[index]
        x = float(raw.get("x", default_columns[index]["x"]))
        y = float(raw.get("y", default_columns[index]["y"]))
        w = float(raw.get("width", default_columns[index]["width"]))
        h = float(raw.get("height", default_columns[index]["height"]))
        parts.append(svg_rect(x, y, w, h, COLORS["surface"], COLORS["rule"], rx=8, element_id=f"panel-e-column-{index}", layout_key=f"panels.topos.columns.{index}"))
        parts.append(svg_text(title, x + 14, y + 24, size=12, weight=650))
        parts.append(svg_text(subtitle, x + 14, y + 43, size=10, fill=COLORS["muted"]))

    # Finite site: overlaps map into local contexts, which cover the whole model.
    x0, y0 = 44, 130
    parts.append(svg_rect(x0 + 52, y0 - 44, 48, 26, COLORS["domain"], COLORS["domain_stroke"], rx=13))
    parts.append(svg_text("X", x0 + 76, y0 - 27, size=11, weight=650, anchor="middle"))
    parts.append(svg_rect(x0 + 12, y0 + 8, 52, 26, COLORS["planner"], COLORS["planner_stroke"], rx=13))
    parts.append(svg_text("Ua", x0 + 38, y0 + 25, size=11, weight=650, anchor="middle"))
    parts.append(svg_rect(x0 + 88, y0 + 8, 52, 26, COLORS["cool_domain"], COLORS["domain_stroke"], rx=13))
    parts.append(svg_text("Ub", x0 + 114, y0 + 25, size=11, weight=650, anchor="middle"))
    parts.append(svg_rect(x0 + 50, y0 + 68, 52, 24, COLORS["graph"], COLORS["graph_stroke"], rx=12))
    parts.append(svg_text("Uab", x0 + 76, y0 + 84, size=10, weight=650, anchor="middle"))
    parts.append(svg_arrow(x0 + 47, y0 + 8, x0 + 68, y0 - 18, COLORS["muted"], width=1.0))
    parts.append(svg_arrow(x0 + 106, y0 + 8, x0 + 84, y0 - 18, COLORS["muted"], width=1.0))
    parts.append(svg_arrow(x0 + 66, y0 + 68, x0 + 47, y0 + 34, COLORS["muted"], width=1.0))
    parts.append(svg_arrow(x0 + 86, y0 + 68, x0 + 106, y0 + 34, COLORS["muted"], width=1.0))

    # Presheaf: local sections restrict to the overlap.
    px, py = 250, 120
    parts.append(svg_rect(px, py - 34, 74, 30, COLORS["numeric"], COLORS["numeric_stroke"], rx=7))
    parts.append(svg_text("F(Ua)", px + 37, py - 14, size=11, weight=650, anchor="middle"))
    parts.append(svg_rect(px + 118, py - 34, 74, 30, COLORS["cool_domain"], COLORS["domain_stroke"], rx=7))
    parts.append(svg_text("F(Ub)", px + 155, py - 14, size=11, weight=650, anchor="middle"))
    parts.append(svg_rect(px + 58, py + 70, 78, 30, COLORS["graph"], COLORS["graph_stroke"], rx=7))
    parts.append(svg_text("F(Uab)", px + 97, py + 90, size=11, weight=650, anchor="middle"))
    parts.append(svg_arrow(px + 37, py - 4, px + 84, py + 70, COLORS["planner_stroke"], width=1.2))
    parts.append(svg_arrow(px + 155, py - 4, px + 110, py + 70, COLORS["planner_stroke"], width=1.2))
    parts.append(svg_text("rho_a", px + 44, py + 36, size=10, fill=COLORS["muted"], anchor="middle"))
    parts.append(svg_text("rho_b", px + 150, py + 36, size=10, fill=COLORS["muted"], anchor="middle"))

    # Sheaf condition: compatible restrictions glue into a global proposal.
    gx = lf(f"{panel}.gluing_report.x", 494)
    gluing_y = lf(f"{panel}.gluing_report.y", 178)
    gy = gluing_y - 54
    gluing_w = lf(f"{panel}.gluing_report.width", 246)
    gluing_h = lf(f"{panel}.gluing_report.height", 38)
    parts.append(svg_text("Gamma(X,F) = compatible families", gx, gy + 6, size=12, weight=650))
    parts.append(svg_text("Eq(F(Ua) x F(Ub) => F(Uab))", gx, gy + 31, size=11, fill=COLORS["muted"]))
    parts.append(svg_rect(gx, gluing_y, gluing_w, gluing_h, COLORS["diagnostic"], COLORS["diagnostic_stroke"], rx=7, element_id="panel-e-gluing-report", layout_key="panels.topos.gluing_report"))
    parts.append(svg_text("GluingReport: rho_a(sa) == rho_b(sb)", gx + gluing_w / 2, gy + 79, size=10, weight=650, anchor="middle"))
    parts.append(svg_rect(gx, gy + 108, 108, 34, COLORS["planner"], COLORS["planner_stroke"], rx=7))
    parts.append(svg_text("global section", gx + 54, gy + 130, size=11, weight=650, anchor="middle"))
    parts.append(svg_rect(gx + 122, gy + 108, 108, 34, COLORS["failure"], COLORS["failure_stroke"], rx=7))
    parts.append(svg_text("obstruction", gx + 176, gy + 130, size=11, weight=650, anchor="middle"))

    map_x = lf(f"{panel}.dictionary.x", 28)
    map_y = lf(f"{panel}.dictionary.y", 276)
    pill_w = lf(f"{panel}.dictionary.pill_width", 174)
    pill_h = lf(f"{panel}.dictionary.pill_height", 30)
    col_gap = lf(f"{panel}.dictionary.column_gap", 184)
    row_gap = lf(f"{panel}.dictionary.row_gap", 34)
    columns_count = li(f"{panel}.dictionary.columns", 4)
    parts.append(svg_text("GCS contract dictionary", map_x, map_y - 12, size=12, weight=650, fill=COLORS["muted"]))
    mappings = [
        ("site object", "ContextSnapshot"),
        ("cover", "CoverPlan"),
        ("section", "LocalSection"),
        ("restriction", "BoundaryProjection"),
        ("gluing", "GluingReport"),
        ("obstruction", "ObstructionReport"),
        ("quotient/groupoid", "GaugePolicy"),
    ]
    for index, (left, right) in enumerate(mappings):
        row = index // columns_count
        col = index % columns_count
        x = map_x + col * col_gap
        y = map_y + row * row_gap
        parts.append(svg_rect(x, y, pill_w, pill_h, COLORS["surface"], COLORS["rule_soft"], rx=6, element_id=f"panel-e-dictionary-pill-{index}", layout_key="panels.topos.dictionary" if index == 0 else None))
        parts.append(svg_text(left, x + 8, y + 11, size=8, fill=COLORS["muted"]))
        parts.append(svg_text(right, x + 8, y + 25, size=8, weight=650))

    parts.append(svg_text(
        "The advanced theory is visible as data contracts, not as runtime abstraction leakage.",
        lf(f"{panel}.footer.x", 28),
        height - lf(f"{panel}.footer.bottom", 8),
        size=12,
        fill=COLORS["muted"],
    ))
    return "\n".join(parts)


def legend_panel(width: int = 520, height: int = 126) -> str:
    parts = panel_frame("f", "Visual grammar", width, height)
    panel = "panels.legend"
    grid_x = lf(f"{panel}.grid.x", 28)
    grid_y = lf(f"{panel}.grid.y", 58)
    col_gap = lf(f"{panel}.grid.column_gap", 165)
    row_gap = lf(f"{panel}.grid.row_gap", 34)
    columns = li(f"{panel}.grid.columns", 3)
    items = [
        ("domain", "stable model truth"),
        ("graph", "incidence structure"),
        ("planner", "cover / gluing"),
        ("numeric", "residual / rank"),
        ("diagnostic", "reports / decision"),
        ("boundary", "IO / viewer boundary"),
    ]
    for index, (token, label) in enumerate(items):
        row = index // columns
        col = index % columns
        x = grid_x + col * col_gap
        y = grid_y + row * row_gap
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
    width = li("canvas.width", 1600)
    height = li("canvas.height", 980)
    panel_a_w = li("panels.geometry.width", 430)
    panel_a_h = li("panels.geometry.height", 300)
    panel_b_w = li("panels.incidence.width", 430)
    panel_b_h = li("panels.incidence.height", 300)
    panel_c_w = li("panels.evidence.width", 520)
    panel_c_h = li("panels.evidence.height", 300)
    panel_d_w = li("panels.pipeline.width", 600)
    panel_d_h = li("panels.pipeline.height", 220)
    panel_e_w = li("panels.topos.width", 780)
    panel_e_h = li("panels.topos.height", 360)
    panel_f_w = li("panels.legend.width", 600)
    panel_f_h = li("panels.legend.height", 126)
    parts = [
        f'<rect{svg_attrs("figure1-background")} x="0" y="0" width="{width}" height="{height}" fill="{COLORS["paper"]}"/>',
        svg_text(
            "Figure 1 | GCS Local-To-Global Constraint Solving",
            lf("final.title.x", 48),
            lf("final.title.y", 54),
            size=li("final.title.size", 29),
            weight=li("final.title.weight", 650),
            family=SERIF,
        ),
        svg_text(
            "Structural source: Mermaid atlas. Mathematical source: finite-site / sheaf gluing semantics.",
            lf("final.subtitle.x", 48),
            lf("final.subtitle.y", 84),
            size=li("final.subtitle.size", 13),
            fill=COLORS["muted"],
        ),
        svg_text(
            f"Fixture: {fixture_label}",
            width - lf("final.fixture_label.right", 48),
            lf("final.fixture_label.y", 82),
            size=li("final.fixture_label.size", 12),
            fill=COLORS["muted"],
            anchor="end",
        ),
        f'<g{svg_attrs("figure1-panel-a", "final.panels.geometry")} transform="translate({lf("final.panels.geometry.x", 48):.1f} {lf("final.panels.geometry.y", 118):.1f})">{geometry_panel(scene, panel_a_w, panel_a_h)}</g>',
        f'<g{svg_attrs("figure1-panel-b", "final.panels.incidence")} transform="translate({lf("final.panels.incidence.x", 522):.1f} {lf("final.panels.incidence.y", 118):.1f})">{incidence_panel(scene, panel_b_w, panel_b_h)}</g>',
        f'<g{svg_attrs("figure1-panel-c", "final.panels.evidence")} transform="translate({lf("final.panels.evidence.x", 996):.1f} {lf("final.panels.evidence.y", 118):.1f})">{evidence_panel(scene, panel_c_w, panel_c_h)}</g>',
        f'<g{svg_attrs("figure1-panel-d", "final.panels.pipeline")} transform="translate({lf("final.panels.pipeline.x", 48):.1f} {lf("final.panels.pipeline.y", 462):.1f})">{pipeline_panel(panel_d_w, panel_d_h)}</g>',
        f'<g{svg_attrs("figure1-panel-e", "final.panels.topos")} transform="translate({lf("final.panels.topos.x", 672):.1f} {lf("final.panels.topos.y", 462):.1f})">{topos_semantics_panel(panel_e_w, panel_e_h)}</g>',
        f'<g{svg_attrs("figure1-panel-f", "final.panels.legend")} transform="translate({lf("final.panels.legend.x", 48):.1f} {lf("final.panels.legend.y", 724):.1f})">{legend_panel(panel_f_w, panel_f_h)}</g>',
        svg_text(
            "Design claim: a command is accepted only when local sections agree on declared overlaps modulo gauge.",
            lf("final.claim.x", 48),
            lf("final.claim.y", 906),
            size=li("final.claim.size", 15),
            weight=li("final.claim.weight", 650),
        ),
        svg_text(
            "Residuals, free/frozen rank evidence, boundary projections, gluing, obstruction, and transaction status are first-class reports.",
            lf("final.note.x", 48),
            lf("final.note.y", 932),
            size=li("final.note.size", 13),
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
    parser.add_argument("--theme", type=Path, default=DEFAULT_THEME, help="Figure theme JSON path.")
    parser.add_argument("--layout", type=Path, default=DEFAULT_LAYOUT, help="Figure layout JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixture = args.fixture if args.fixture.is_absolute() else ROOT / args.fixture
    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    theme = args.theme if args.theme.is_absolute() else ROOT / args.theme
    layout = args.layout if args.layout.is_absolute() else ROOT / args.layout
    load_design_controls(theme, layout)
    scene = load_scene(fixture)
    panel_a_w = li("panels.geometry.width", 430)
    panel_a_h = li("panels.geometry.height", 300)
    panel_b_w = li("panels.incidence.width", 430)
    panel_b_h = li("panels.incidence.height", 300)
    panel_c_w = li("panels.evidence.width", 520)
    panel_c_h = li("panels.evidence.height", 300)

    outputs = {
        "figure1-panel-a-geometry.svg": wrap_svg(
            geometry_panel(scene, panel_a_w, panel_a_h),
            panel_a_w,
            panel_a_h,
            "GCS geometry fixture panel",
        ),
        "figure1-panel-b-incidence.svg": wrap_svg(
            incidence_panel(scene, panel_b_w, panel_b_h),
            panel_b_w,
            panel_b_h,
            "GCS incidence hypergraph panel",
        ),
        "figure1-panel-c-residual-rank.svg": wrap_svg(
            evidence_panel(scene, panel_c_w, panel_c_h),
            panel_c_w,
            panel_c_h,
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
