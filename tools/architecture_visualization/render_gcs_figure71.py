#!/usr/bin/env python3
"""Render Figure 71: the GCS Step 1-40 evidence-boundary map."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "docs" / "architecture" / "71-step-1-40-execution-report.md"
DEFAULT_THEME = Path(__file__).with_name("figure1.theme.json")
DEFAULT_LAYOUT = Path(__file__).with_name("figure71.layout.json")
DEFAULT_OUT_DIR = ROOT / "docs" / "architecture" / "70-visualization" / "assets"
DEFAULT_OUT_NAME = "figure71-gcs-step-1-40-evidence-map.svg"


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


@dataclass(frozen=True)
class Step:
    number: int
    status: str
    focus: str
    core: str
    evidence: str


@dataclass(frozen=True)
class Arc:
    key: str
    title: str
    label: str
    token: str
    claim: str
    steps: tuple[Step, ...]


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def deep_merge(base: dict[str, object], override: dict[str, object]) -> dict[str, object]:
    result = dict(base)
    for key, value in override.items():
        current = result.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            result[key] = deep_merge(current, value)
        else:
            result[key] = value
    return result


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def nested(source: dict[str, object], dotted: str, default: object) -> object:
    current: object = source
    for part in dotted.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    return current


def lf(path: str, default: float) -> float:
    return float(nested(LAYOUT, path, default))


def li(path: str, default: int) -> int:
    return int(round(lf(path, float(default))))


def load_controls(theme_path: Path, layout_path: Path) -> None:
    global COLORS, SANS, SERIF, THEME, LAYOUT
    THEME = deep_merge({
        "colors": COLORS,
        "fonts": {"sans": SANS, "serif": SERIF},
        "strokes": {"default": 1.1}
    }, read_json(theme_path))
    colors = nested(THEME, "colors", COLORS)
    if not isinstance(colors, dict):
        raise ValueError("theme colors must be an object")
    COLORS = {str(key): str(value) for key, value in colors.items()}
    SANS = str(nested(THEME, "fonts.sans", SANS))
    SERIF = str(nested(THEME, "fonts.serif", SERIF))
    LAYOUT = read_json(layout_path)


def attrs(element_id: str | None = None, layout_key: str | None = None) -> str:
    values = []
    if element_id:
        values.append(f'id="{escape(element_id)}"')
    if layout_key:
        values.append(f'data-layout-key="{escape(layout_key)}"')
    return (" " + " ".join(values)) if values else ""


def rect(x: float, y: float, w: float, h: float, fill: str, stroke: str, rx: float = 8.0, dash: str = "", element_id: str | None = None, layout_key: str | None = None) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect{attrs(element_id, layout_key)} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.1"{dash_attr}/>'


def text(value: str, x: float, y: float, size: int = 12, weight: int = 400, fill: str | None = None, anchor: str = "start", family: str | None = None) -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family or SANS}" font-size="{size}" font-weight="{weight}" fill="{fill or COLORS["ink"]}" text-anchor="{anchor}">{escape(value)}</text>'


def wrapped(value: str, x: float, y: float, chars: int, size: int = 10, fill: str | None = None, max_lines: int = 2, line_height: float = 12.0) -> str:
    words = re.split(r"\s+", value.strip())
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,;:") + "..."
    tspans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        tspans.append(f'<tspan x="{x:.1f}" dy="{dy:.1f}">{escape(line)}</tspan>')
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{SANS}" font-size="{size}" fill="{fill or COLORS["ink"]}">{"".join(tspans)}</text>'


def line(x1: float, y1: float, x2: float, y2: float, stroke: str, width: float = 1.3, dash: str = "", arrow: bool = False) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    marker_attr = ' marker-end="url(#arrow)"' if arrow else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width:.1f}" stroke-linecap="round"{dash_attr}{marker_attr}/>'


def path(d: str, stroke: str, width: float = 1.3, dash: str = "", arrow: bool = False, fill: str = "none") -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    marker_attr = ' marker-end="url(#arrow)"' if arrow else ""
    return f'<path d="{escape(d)}" fill="{fill}" stroke="{stroke}" stroke-width="{width:.1f}" stroke-linecap="round" stroke-linejoin="round"{dash_attr}{marker_attr}/>'


def done(cx: float, cy: float, color: str) -> str:
    return "\n".join([
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8.5" fill="{COLORS["panel"]}" stroke="{color}" stroke-width="1.3"/>',
        path(f"M {cx - 4:.1f} {cy:.1f} L {cx - 1:.1f} {cy + 3.5:.1f} L {cx + 5:.1f} {cy - 5:.1f}", color, 1.6)
    ])


def parse_steps(report: Path) -> list[Step]:
    steps = []
    for raw in report.read_text(encoding="utf-8").splitlines():
        if not raw.startswith("| "):
            continue
        cells = [cell.strip() for cell in raw.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0].isdigit():
            continue
        steps.append(Step(int(cells[0]), cells[1], cells[2], cells[3], cells[4]))
    return steps


def arcs_for(steps: list[Step]) -> list[Arc]:
    by_number = {step.number: step for step in steps}

    def span(start: int, end: int) -> tuple[Step, ...]:
        return tuple(by_number[number] for number in range(start, end + 1) if number in by_number)

    return [
        Arc("foundation", "Foundation Runway", "Steps 1-13", "domain", "Contract-tested kernel-to-viewer boundaries", span(1, 13)),
        Arc("algorithm", "Algorithm Lift", "Steps 14-18", "numeric", "Real local solve, JSON IO, diagnostics, corpus, gates", span(14, 18)),
        Arc("scene_generation", "Scene-Generation Loop", "Steps 19-27", "planner", "Generated candidates pass public solver gates", span(19, 27)),
        Arc("rank_spine", "Rank Evidence Spine", "Steps 28-35", "diagnostic", "Free/frozen rank evidence reaches runtime, viewer, promotion", span(28, 35)),
        Arc("next_batch", "Evidence Closure Horizon", "Steps 36-40", "boundary", "Robustness, corpus, viewer evidence, quality, atlas sync", span(36, 40)),
    ]


def panel_header(letter: str, arc: Arc, w: float, h: float) -> list[str]:
    stroke = COLORS.get(f"{arc.token}_stroke", COLORS["boundary_stroke"])
    return [
        rect(0, 0, w, h, COLORS["panel"], COLORS["rule"], 8),
        text(letter, 22, 34, 23, 700, COLORS["accent"], family=SERIF),
        text(arc.title, 58, 29, 15, 650),
        rect(w - 112, 17, 84, 24, COLORS[arc.token], stroke, 12),
        text(arc.label, w - 70, 33, 10, 650, stroke, "middle"),
        wrapped(arc.claim, 58, 52, 54, 10, COLORS["muted"], 2, 13)
    ]


def foundation_panel(arc: Arc, w: float, h: float) -> str:
    parts = panel_header("a", arc, w, h)
    names = ["kernel", "catalog", "incidence", "planner", "numeric", "rank", "diagnostics", "gluing", "runtime", "IO", "viewer", "tools", "quality"]
    tokens = ["domain", "numeric", "graph", "planner", "numeric", "numeric", "diagnostic", "planner", "diagnostic", "boundary", "boundary", "graph", "diagnostic"]
    x0, y0, gap = 28.0, 108.0, 8.0
    chip_w = (w - 56 - gap * 3) / 4
    for index, step in enumerate(arc.steps):
        row, col = divmod(index, 4)
        x = x0 + col * (chip_w + gap)
        y = y0 + row * 52
        token = tokens[index]
        stroke = COLORS.get(f"{token}_stroke", COLORS["boundary_stroke"])
        parts.append(rect(x, y, chip_w, 39, COLORS[token], stroke, 7))
        parts.append(text(str(step.number), x + 13, y + 24, 12, 700, stroke))
        parts.append(text(names[index], x + 33, y + 24, 10, 650))
        parts.append(done(x + chip_w - 14, y + 15, stroke))
    parts.append(line(34, h - 36, w - 36, h - 36, COLORS["domain_stroke"], 1.5, arrow=True))
    parts.append(text("source-of-truth contracts reach public viewer and quality boundaries", 34, h - 48, 10, fill=COLORS["muted"]))
    return "\n".join(parts)


def algorithm_panel(arc: Arc, w: float, h: float) -> str:
    parts = panel_header("b", arc, w, h)
    positions = [(34, 112), (232, 112), (133, 182), (34, 252), (232, 252)]
    for index, step in enumerate(arc.steps):
        x, y = positions[index]
        token = "numeric" if step.number == 14 else "boundary" if step.number == 15 else "diagnostic"
        if step.number == 18:
            token = "planner"
        stroke = COLORS.get(f"{token}_stroke", COLORS["boundary_stroke"])
        parts.append(rect(x, y, 152, 46, COLORS[token], stroke, 7))
        parts.append(text(f"Step {step.number}", x + 12, y + 17, 10, 700, stroke))
        parts.append(wrapped(step.focus, x + 12, y + 32, 24, 9, max_lines=2, line_height=11))
        parts.append(done(x + 136, y + 16, stroke))
    for start, end in zip(positions, positions[1:]):
        sx, sy = start[0] + 76, start[1] + 46
        ex, ey = end[0] + 76, end[1]
        parts.append(path(f"M {sx:.1f} {sy:.1f} C {sx:.1f} {sy + 25:.1f}, {ex:.1f} {ey - 25:.1f}, {ex:.1f} {ey:.1f}", COLORS["muted"], 1.2, arrow=True))
    parts.append(text("This batch turns scaffolding into executable evidence.", 34, h - 28, 11, fill=COLORS["muted"]))
    return "\n".join(parts)


def scene_generation_panel(arc: Arc, w: float, h: float) -> str:
    parts = panel_header("c", arc, w, h)
    cx, cy, radius = w / 2, 158.0, 76.0
    parts.append(path(f"M {cx - radius:.1f} {cy:.1f} A {radius:.1f} {radius:.1f} 0 1 1 {cx + radius:.1f} {cy:.1f} A {radius:.1f} {radius:.1f} 0 1 1 {cx - radius:.1f} {cy:.1f}", COLORS["planner_stroke"], 1.3, "5 5"))
    parts.append(rect(cx - 70, cy - 25, 140, 50, COLORS["surface"], COLORS["planner_stroke"], 8))
    parts.append(text("fixture corpus", cx, cy - 4, 13, 700, anchor="middle"))
    parts.append(text("public gates", cx, cy + 15, 10, fill=COLORS["muted"], anchor="middle"))
    labels = [
        ("explorer", 19, -88, -62, "graph"),
        ("package", 20, 48, -78, "planner"),
        ("topology", 21, 98, -2, "graph"),
        ("validation", 22, 45, 76, "diagnostic"),
        ("params", 23, -86, 74, "numeric"),
        ("repair", 24, -126, 0, "failure"),
        ("orchestrate", 25, -50, -100, "planner"),
        ("store", 26, 112, 58, "boundary"),
        ("gates", 27, -122, 50, "diagnostic")
    ]
    for label, number, dx, dy, token in labels:
        x, y = cx + dx, cy + dy
        stroke = COLORS.get(f"{token}_stroke", COLORS["boundary_stroke"])
        parts.append(rect(x - 48, y - 15, 96, 30, COLORS[token], stroke, 15))
        parts.append(text(f"{number} {label}", x, y + 4, 9, 650, anchor="middle"))
        parts.append(done(x + 38, y - 8, stroke))
    parts.append(text("Generated scenes become trustworthy only after public adapter evidence.", 34, h - 26, 10, fill=COLORS["muted"]))
    return "\n".join(parts)


def rank_spine_panel(arc: Arc, w: float, h: float) -> str:
    parts = panel_header("d", arc, w, h)
    spine_x, top, bottom = 168.0, 92.0, h - 58
    parts.append(line(spine_x, top, spine_x, bottom, COLORS["diagnostic_stroke"], 2.2, arrow=True))
    parts.append(text("rank evidence", spine_x - 72, top - 14, 12, 700, COLORS["diagnostic_stroke"]))
    labels = [
        (28, "free/frozen columns", "numeric"),
        (29, "atlas sync", "boundary"),
        (30, "diagnostics rank", "diagnostic"),
        (31, "runtime/viewer projection", "boundary"),
        (32, "promotion rank gate", "planner"),
        (33, "SolveDAG dependencies", "graph"),
        (34, "post-local diagnostics", "diagnostic"),
        (35, "conflict/redundancy subjects", "failure")
    ]
    for index, (number, label, token) in enumerate(labels):
        y = top + index * ((bottom - top) / (len(labels) - 1))
        x2 = 302 if index % 2 == 0 else 512
        stroke = COLORS.get(f"{token}_stroke", COLORS["boundary_stroke"])
        parts.append(f'<circle cx="{spine_x:.1f}" cy="{y:.1f}" r="7.0" fill="{COLORS[token]}" stroke="{stroke}" stroke-width="1.2"/>')
        parts.append(line(spine_x + 10, y, x2 - 10, y, COLORS["rule"], 1.2, "3 4"))
        parts.append(rect(x2 - 8, y - 18, 86, 36, COLORS[token], stroke, 7))
        parts.append(text(str(number), x2 + 9, y + 4, 12, 700, stroke))
        parts.append(wrapped(label, x2 + 31, y - 4, 24, 8, max_lines=2, line_height=9))
    parts.append(rect(28, h - 38, w - 56, 26, COLORS["surface"], COLORS["rule_soft"], 6))
    parts.append(text("Evidence moves outward without UI or gates reading numeric internals.", 42, h - 20, 11, fill=COLORS["muted"]))
    return "\n".join(parts)


def next_batch_panel(arc: Arc, w: float, h: float) -> str:
    parts = panel_header("e", arc, w, h)
    horizon_y = 210.0
    parts.append(rect(34, horizon_y, w - 68, 42, COLORS["plot"], COLORS["rule_soft"], 21))
    parts.append(path(f"M 48 {horizon_y + 28:.1f} C 122 {horizon_y - 18:.1f}, 210 {horizon_y + 60:.1f}, {w - 48:.1f} {horizon_y + 12:.1f}", COLORS["accent"], 2.0, arrow=True))
    for index, step in enumerate(arc.steps):
        x = 58 + index * ((w - 116) / max(len(arc.steps) - 1, 1))
        y = horizon_y - 72 + (index % 2) * 28
        done_step = step.status.lower() == "done"
        fill = COLORS["boundary"] if done_step else COLORS["surface"]
        dash = "" if done_step else "5 4"
        parts.append(rect(x - 34, y - 16, 68, 32, fill, COLORS["boundary_stroke"], 8, dash=dash))
        parts.append(text(str(step.number), x - 21, y + 5, 12, 700, COLORS["boundary_stroke"]))
        parts.append(wrapped(step.focus, x + 2, y - 4, 14, 7, max_lines=2, line_height=8))
        parts.append(line(x, y + 17, x, horizon_y, COLORS["boundary_stroke"], 1.0, "3 4"))
        if done_step:
            parts.append(done(x + 24, y - 7, COLORS["boundary_stroke"]))
    if all(step.status.lower() == "done" for step in arc.steps):
        footer = "Quality gates and atlas now launch the showcase graph."
    else:
        footer = "Pending is not failure: it is the next evidence frontier."
    parts.append(text(footer, 34, h - 26, 11, fill=COLORS["muted"]))
    return "\n".join(parts)


def showcase_panel(w: float, h: float) -> str:
    arc = Arc("showcase", "Showcase Candidate", "after Step 40", "planner", "Integrated feature constraint graph", tuple())
    parts = panel_header("f", arc, w, h)
    plot_x, plot_y, plot_w, plot_h = 34.0, 88.0, 218.0, 178.0
    parts.append(rect(plot_x, plot_y, plot_w, plot_h, COLORS["plot"], COLORS["rule_soft"], 8))
    points = {
        "G1": (plot_x + 46, plot_y + 116),
        "G2": (plot_x + 108, plot_y + 54),
        "G3": (plot_x + 184, plot_y + 118),
        "G4": (plot_x + 112, plot_y + 142)
    }
    parts.append(rect(plot_x + 30, plot_y + 32, 108, 118, COLORS["planner"], COLORS["planner_stroke"], 16, "4 5"))
    parts.append(rect(plot_x + 88, plot_y + 42, 112, 118, COLORS["cool_domain"], COLORS["domain_stroke"], 16, "4 5"))
    for left, right in [("G1", "G2"), ("G2", "G3"), ("G3", "G4"), ("G4", "G1"), ("G1", "G3")]:
        x1, y1 = points[left]
        x2, y2 = points[right]
        diag = left == "G1" and right == "G3"
        parts.append(line(x1, y1, x2, y2, COLORS["failure_stroke"] if diag else COLORS["constraint"], 2.0, "5 4" if diag else ""))
    for name, (x, y) in points.items():
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{COLORS["point"]}" stroke="{COLORS["white"]}" stroke-width="2"/>')
        parts.append(text(name, x, y - 13, 9, 650, anchor="middle"))
    cards = [("free rank", "8 / 10", "numeric"), ("frozen cols", "2", "boundary"), ("gluing", "ok", "planner"), ("obstruction", "variant", "failure")]
    for index, (label, value, token) in enumerate(cards):
        y = 102 + index * 48
        stroke = COLORS.get(f"{token}_stroke", COLORS["boundary_stroke"])
        parts.append(rect(274, y, 100, 34, COLORS[token], stroke, 7))
        parts.append(text(label, 284, y + 13, 8, fill=COLORS["muted"]))
        parts.append(text(value, 284, y + 28, 11, 700))
    parts.append(text("A demo image should combine geometry, cover, rank, gluing, and variants.", 34, h - 26, 10, fill=COLORS["muted"]))
    return "\n".join(parts)


def summary(arcs: list[Arc]) -> str:
    x, y = lf("summary.x", 52), lf("summary.y", 120)
    w, h = lf("summary.width", 1496), lf("summary.height", 58)
    done_count = sum(1 for arc in arcs for step in arc.steps if step.status.lower() == "done")
    total = sum(len(arc.steps) for arc in arcs)
    claim = "canonical contracts -> executable solver evidence -> public promotion gates -> viewer-visible diagnostics -> post-Step-40 showcase"
    return "\n".join([
        rect(x, y, w, h, COLORS["surface"], COLORS["rule"], 8),
        text("Procedure claim", x + 18, y + 24, 11, 700, COLORS["accent"]),
        text(claim, x + 18, y + 45, 16, 650),
        text(f"{done_count} done / {total - done_count} pending", x + w - 28, y + 36, 14, 700, COLORS["diagnostic_stroke"], "end")
    ])


def wrap_svg(content: str, width: int, height: int, title_value: str) -> str:
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">',
        f'<title id="title">{escape(title_value)}</title>',
        "<defs>",
        '<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth">',
        f'<path d="M0,0 L8,4 L0,8 Z" fill="{COLORS["muted"]}"/>',
        "</marker>",
        "</defs>",
        content,
        "</svg>",
        ""
    ])


def render(report: Path, steps: list[Step]) -> str:
    width, height = li("canvas.width", 1600), li("canvas.height", 1000)
    arcs = arcs_for(steps)
    by_key = {arc.key: arc for arc in arcs}
    parts = [
        f'<rect id="figure71-background" x="0" y="0" width="{width}" height="{height}" fill="{COLORS["paper"]}"/>',
        text("Figure 71 | GCS Evidence-Boundary Flight Map", lf("title.x", 52), lf("title.y", 58), li("title.size", 30), 650, family=SERIF),
        text("A vivid procedure map for Step 1-40: from contracts to public evidence and the showcase frontier.", lf("subtitle.x", 52), lf("subtitle.y", 88), li("subtitle.size", 13), fill=COLORS["muted"]),
        text(f"Source: {report.relative_to(ROOT).as_posix()}", width - lf("meta.right", 52), lf("meta.y", 88), li("meta.size", 12), fill=COLORS["muted"], anchor="end"),
        summary(arcs)
    ]
    renderers = {
        "foundation": foundation_panel,
        "algorithm": algorithm_panel,
        "scene_generation": scene_generation_panel,
        "rank_spine": rank_spine_panel,
        "next_batch": next_batch_panel
    }
    for key, renderer in renderers.items():
        x, y = lf(f"panels.{key}.x", 0), lf(f"panels.{key}.y", 0)
        w, h = lf(f"panels.{key}.width", 400), lf(f"panels.{key}.height", 260)
        parts.append(f'<g id="figure71-panel-{key}" data-layout-key="panels.{key}" transform="translate({x:.1f} {y:.1f})">{renderer(by_key[key], w, h)}</g>')
    x, y = lf("panels.showcase.x", 0), lf("panels.showcase.y", 0)
    w, h = lf("panels.showcase.width", 400), lf("panels.showcase.height", 300)
    parts.append(f'<g id="figure71-panel-showcase" data-layout-key="panels.showcase" transform="translate({x:.1f} {y:.1f})">{showcase_panel(w, h)}</g>')
    parts.append(text("Taste rule applied: evidence is the ornament; the diagram groups work by credibility boundaries, not by checklist rows.", lf("footer.x", 52), lf("footer.y", 936), li("footer.size", 13), fill=COLORS["muted"]))
    return wrap_svg("\n".join(parts), width, height, "GCS Evidence-Boundary Flight Map")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Figure 71 Step 1-40 evidence map.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Step 1-40 report Markdown path.")
    parser.add_argument("--theme", type=Path, default=DEFAULT_THEME, help="Theme JSON path.")
    parser.add_argument("--layout", type=Path, default=DEFAULT_LAYOUT, help="Figure 71 layout JSON path.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Output asset directory.")
    parser.add_argument("--out-name", default=DEFAULT_OUT_NAME, help="Output SVG file name.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = args.report if args.report.is_absolute() else ROOT / args.report
    theme = args.theme if args.theme.is_absolute() else ROOT / args.theme
    layout = args.layout if args.layout.is_absolute() else ROOT / args.layout
    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    load_controls(theme, layout)
    steps = parse_steps(report)
    if len(steps) < 40:
        raise ValueError(f"expected at least 40 steps in {report}, found {len(steps)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / args.out_name
    out_path.write_text(render(report, steps), encoding="utf-8", newline="\n")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
