#!/usr/bin/env python3
"""Render the P6 integrated showcase as a tokenized HTML figure."""

from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENE = ROOT / "fixtures" / "scene" / "showcase" / "integrated_feature_showcase.gcs.json"
DEFAULT_METADATA = ROOT / "fixtures" / "scene" / "showcase" / "integrated_feature_showcase.metadata.json"
DEFAULT_NEGATIVE_METADATA = (
    ROOT / "fixtures" / "scene" / "showcase" / "integrated_feature_showcase_missing_fixed.metadata.json"
)
DEFAULT_THEME = ROOT / "tools" / "architecture_visualization" / "figure1.theme.json"
DEFAULT_OUT_HTML = (
    ROOT
    / "docs"
    / "architecture"
    / "70-visualization"
    / "assets"
    / "figure72-gcs-integrated-showcase-scene.html"
)

GEOMETRY_NAMES = {0: "Point", 1: "Line", 2: "Plane"}
CONSTRAINT_NAMES = {0: "Coincident", 1: "Parallel", 2: "Perpendicular", 3: "Distance", 4: "Angle"}
PANEL_BOXES = {
    "scene_contract": (0, 0, 4, 1),
    "constraint_graph": (4, 0, 4, 1),
    "boundary_plan": (8, 0, 4, 1),
    "numeric_evidence": (0, 1, 4, 1),
    "gluing_and_diagnostics": (4, 1, 4, 1),
    "negative_variant": (8, 1, 4, 1),
    "gate_chain": (0, 2, 12, 1),
}


@dataclass(frozen=True)
class ShowcaseContext:
    scene: dict[str, Any]
    metadata: dict[str, Any]
    negative_metadata: dict[str, Any]
    colors: dict[str, str]
    fonts: dict[str, str]


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def load_theme(path: Path = DEFAULT_THEME) -> tuple[dict[str, str], dict[str, str]]:
    data = read_json(path)
    colors = data.get("colors", {})
    fonts = data.get("fonts", {})
    if not isinstance(colors, dict) or not isinstance(fonts, dict):
        raise ValueError(f"{path} must define colors and fonts objects")
    return {str(key): str(value) for key, value in colors.items()}, {
        str(key): str(value) for key, value in fonts.items()
    }


def load_context(
    scene_path: Path = DEFAULT_SCENE,
    metadata_path: Path = DEFAULT_METADATA,
    negative_metadata_path: Path = DEFAULT_NEGATIVE_METADATA,
    theme_path: Path = DEFAULT_THEME,
) -> ShowcaseContext:
    colors, fonts = load_theme(theme_path)
    return ShowcaseContext(
        scene=read_json(scene_path),
        metadata=read_json(metadata_path),
        negative_metadata=read_json(negative_metadata_path),
        colors=colors,
        fonts=fonts,
    )


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text_attrs(label: str, budget: int) -> str:
    return f'data-gcs-text-label="{esc(label)}" data-gcs-text-budget="{budget}"'


def contrast_attrs(label: str,
                   foreground: str,
                   background: str,
                   threshold: float = 4.5) -> str:
    return (
        f'data-gcs-contrast-label="{esc(label)}" '
        f'data-gcs-contrast-fg="{esc(foreground)}" '
        f'data-gcs-contrast-bg="{esc(background)}" '
        f'data-gcs-contrast-min="{threshold:.1f}"'
    )


def box_attrs(panel_id: str) -> str:
    box = PANEL_BOXES[panel_id]
    raw_box = ",".join(str(value) for value in box)
    return (
        f'data-gcs-box-label="figure72-{panel_id}" '
        f'data-gcs-box-group="figure72-grid" '
        f'data-gcs-box="{raw_box}"'
    )


def css_vars(colors: dict[str, str], fonts: dict[str, str]) -> str:
    lines = [
        f"--gcs-{key.replace('_', '-')}: {value};"
        for key, value in sorted(colors.items())
    ]
    lines.extend([
        f"--gcs-font-{key}: {value};"
        for key, value in sorted(fonts.items())
    ])
    return "\n      ".join(lines)


def metric(label: str, value: object, token: str, colors: dict[str, str]) -> str:
    token_fill = colors[token]
    token_stroke = colors[f"{token}_stroke"] if f"{token}_stroke" in colors else colors["rule"]
    return f"""
      <div class="metric" style="--metric-fill:{esc(token_fill)};--metric-stroke:{esc(token_stroke)};">
        <span {text_attrs(f"metric-{label}-label", 28)} {contrast_attrs(f"metric-{label}-label", colors["muted"], token_fill)}>{esc(label)}</span>
        <strong {text_attrs(f"metric-{label}-value", 30)} {contrast_attrs(f"metric-{label}-value", colors["ink"], token_fill)}>{esc(value)}</strong>
      </div>
    """


def evidence_chip(label: str, token: str, colors: dict[str, str]) -> str:
    fill_key = token.split(".")[1] if token.startswith("evidence.") else "boundary"
    fill = colors.get(fill_key, colors["boundary"])
    stroke = colors.get(f"{fill_key}_stroke", colors["boundary_stroke"])
    return (
        f'<span class="chip" style="--chip-fill:{esc(fill)};--chip-stroke:{esc(stroke)};" '
        f'{text_attrs(f"chip-{label}", 40)} {contrast_attrs(f"chip-{label}", stroke, fill, 3.0)}>'
        f'{esc(label)}</span>'
    )


def panel(panel_id: str,
          title: str,
          token: str,
          claim: str,
          body: str,
          colors: dict[str, str]) -> str:
    token_key = token.split(".")[1]
    fill = colors[token_key]
    stroke = colors[f"{token_key}_stroke"]
    return f"""
    <section class="panel panel-{esc(panel_id)}" style="--panel-token-fill:{esc(fill)};--panel-token-stroke:{esc(stroke)};" {box_attrs(panel_id)}>
      <div class="panel-topline">
        <div>
          <p class="eyebrow" {text_attrs(f"{panel_id}-eyebrow", 34)} {contrast_attrs(f"{panel_id}-eyebrow", colors["muted"], colors["panel"])}>{esc(token)}</p>
          <h2 {text_attrs(f"{panel_id}-title", 44)} {contrast_attrs(f"{panel_id}-title", colors["ink"], colors["panel"])}>{esc(title)}</h2>
        </div>
        {evidence_chip(title, token, colors)}
      </div>
      <p class="panel-claim" {text_attrs(f"{panel_id}-claim", 150)} {contrast_attrs(f"{panel_id}-claim", colors["muted"], colors["panel"])}>{esc(claim)}</p>
      {body}
    </section>
    """


def scene_counts(context: ShowcaseContext) -> dict[str, int]:
    return {
        "Rigid sets": len(context.scene.get("rigid_sets", [])),
        "Geometries": len(context.scene.get("geometries", [])),
        "Constraints": len(context.scene.get("constraints", [])),
        "Fixed IDs": len(context.scene.get("behavior", {}).get("fixed_geometry_ids", [])),
    }


def components(context: ShowcaseContext) -> list[list[int]]:
    parent = {int(item["id"]): int(item["id"]) for item in context.scene.get("geometries", [])}

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        root_left = find(left)
        root_right = find(right)
        if root_left != root_right:
            parent[root_right] = root_left

    for constraint in context.scene.get("constraints", []):
        ids = [int(value) for value in constraint.get("geometry_ids", [])]
        for current in ids[1:]:
            union(ids[0], current)

    grouped: dict[int, list[int]] = {}
    for entity_id in sorted(parent):
        grouped.setdefault(find(entity_id), []).append(entity_id)
    return [sorted(group) for group in grouped.values()]


def render_scene_glyph(context: ShowcaseContext) -> str:
    colors = context.colors
    entities = context.scene.get("geometries", [])
    constraints = context.scene.get("constraints", [])
    positions = {
        int(item["id"]): (
            40 + (float(item.get("v", [0, 0])[0]) * 70),
            54 + (float(item.get("v", [0, 0])[1]) * 62),
        )
        for item in entities
    }
    lines = []
    for constraint in constraints:
        ids = [int(value) for value in constraint.get("geometry_ids", [])]
        if len(ids) < 2:
            continue
        x1, y1 = positions[ids[0]]
        x2, y2 = positions[ids[1]]
        lines.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{esc(colors["constraint"])}" stroke-width="2.2" stroke-linecap="round"/>'
        )
    nodes = []
    fixed_ids = set(context.scene.get("behavior", {}).get("fixed_geometry_ids", []))
    for entity in entities:
        entity_id = int(entity["id"])
        x, y = positions[entity_id]
        fill = colors["accent"] if entity_id in fixed_ids else colors["domain"]
        stroke = colors["domain_stroke"]
        nodes.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{esc(fill)}" '
            f'stroke="{esc(stroke)}" stroke-width="1.4"/>'
        )
    return f"""
      <svg class="scene-glyph" viewBox="0 0 240 210" role="img" aria-label="integrated showcase scene graph">
        <rect x="1" y="1" width="238" height="208" rx="8" fill="{esc(colors["plot"])}" stroke="{esc(colors["rule"])}"/>
        {''.join(lines)}
        {''.join(nodes)}
      </svg>
    """


def render_html(context: ShowcaseContext) -> str:
    colors = context.colors
    fonts = context.fonts
    expected = context.metadata["expected_public_evidence"]
    solver = context.metadata["expected_solver_evidence"]
    negative = context.negative_metadata["expected_public_evidence"]
    rank_reports = solver["local_numeric_reports"]
    component_text = "; ".join(f"({', '.join(str(value) for value in group)})" for group in components(context))
    gate_list = context.metadata["quality_gates"]
    required_panels = context.metadata["showcase_brief"]["required_panels"]

    scene_body = f"""
      <div class="scene-contract-layout">
        {render_scene_glyph(context)}
        <div class="metric-grid">
          {''.join(metric(label, value, "domain", colors) for label, value in scene_counts(context).items())}
        </div>
      </div>
    """

    graph_body = f"""
      <div class="evidence-list">
        <p {text_attrs("constraint-components", 90)} {contrast_attrs("constraint-components", colors["ink"], colors["panel"])}>Components: {esc(component_text)}</p>
        <p {text_attrs("constraint-types", 130)} {contrast_attrs("constraint-types", colors["muted"], colors["panel"])}>Constraints: {esc(", ".join(CONSTRAINT_NAMES.get(int(item["type"]), "Unknown") for item in context.scene.get("constraints", [])))}</p>
        <p {text_attrs("constraint-geometry-types", 130)} {contrast_attrs("constraint-geometry-types", colors["muted"], colors["panel"])}>Geometry mix: {esc(", ".join(GEOMETRY_NAMES.get(int(item["type"]), "Unknown") for item in context.scene.get("geometries", [])))}</p>
      </div>
    """

    boundary_body = f"""
      <div class="metric-grid">
        {metric("fixed boundary", expected["fixed_geometry_ids"], "planner", colors)}
        {metric("planner subproblems", expected["planner_subproblems"], "planner", colors)}
        {metric("cover contexts", solver["cover_contexts"], "planner", colors)}
      </div>
    """

    numeric_items = "".join(
        f"""
        <li>
          <strong {text_attrs(f"rank-{index}-label", 24)} {contrast_attrs(f"rank-{index}-label", colors["ink"], colors["panel"])}>local {index}</strong>
          <span {text_attrs(f"rank-{index}-detail", 96)} {contrast_attrs(f"rank-{index}-detail", colors["muted"], colors["panel"])}>rank {report["rank"]}, free {report["free_variables"]}, frozen {report["frozen_variables"]}, residual max {report["max_residual"]}</span>
        </li>
        """
        for index, report in enumerate(rank_reports)
    )
    numeric_body = f'<ul class="rank-list">{numeric_items}</ul>'

    gluing_body = f"""
      <div class="evidence-list">
        <p {text_attrs("gluing-code", 42)} {contrast_attrs("gluing-code", colors["ink"], colors["panel"])}>{esc(solver["gluing"]["report_code"])}</p>
        <p {text_attrs("gluing-message", 120)} {contrast_attrs("gluing-message", colors["muted"], colors["panel"])}>{esc(solver["gluing"]["message"])}</p>
        <p {text_attrs("diagnostic-count", 80)} {contrast_attrs("diagnostic-count", colors["muted"], colors["panel"])}>post-local diagnostics warnings: {esc(solver["diagnostics"]["post_local_diagnostics_warnings"])}</p>
      </div>
    """

    negative_body = f"""
      <div class="evidence-list negative-list">
        <p {text_attrs("negative-code", 70)} {contrast_attrs("negative-code", colors["ink"], colors["panel"])}>{esc(negative["report_code"])}</p>
        <p {text_attrs("negative-missing", 60)} {contrast_attrs("negative-missing", colors["muted"], colors["panel"])}>missing fixed geometry IDs: {esc(negative["missing_fixed_geometry_ids"])}</p>
      </div>
    """

    gate_items = "".join(
        f'<li {text_attrs(f"gate-{index}", 94)} {contrast_attrs(f"gate-{index}", colors["muted"], colors["panel"])}>{esc(gate)}</li>'
        for index, gate in enumerate(gate_list)
    )
    panel_items = "".join(
        f'<span class="panel-tag" {text_attrs(f"required-panel-{index}", 32)} {contrast_attrs(f"required-panel-{index}", colors["boundary_stroke"], colors["boundary"], 3.0)}>{esc(item)}</span>'
        for index, item in enumerate(required_panels)
    )
    gate_body = f"""
      <div class="gate-layout">
        <ul>{gate_items}</ul>
        <div class="panel-tags">{panel_items}</div>
      </div>
    """

    panels = [
        panel(
            "scene_contract",
            "Scene Contract",
            "evidence.domain",
            "Public JSON carries durable solve intent and inspectable geometry.",
            scene_body,
            colors,
        ),
        panel(
            "constraint_graph",
            "Constraint Graph",
            "evidence.graph",
            "Two local components make the showcase a real decomposition scene.",
            graph_body,
            colors,
        ),
        panel(
            "boundary_plan",
            "Boundary Plan",
            "evidence.planner",
            "Fixed geometry propagates into cover and local numeric tasks.",
            boundary_body,
            colors,
        ),
        panel(
            "numeric_evidence",
            "Numeric Evidence",
            "evidence.numeric",
            "Rank and residual reports stay visible at the local-solve boundary.",
            numeric_body,
            colors,
        ),
        panel(
            "gluing_and_diagnostics",
            "Gluing Diagnostics",
            "evidence.diagnostic",
            "Local sections become a committed accepted state through diagnostics.",
            gluing_body,
            colors,
        ),
        panel(
            "negative_variant",
            "Negative Variant",
            "evidence.failure",
            "Invalid solve intent fails with a stable typed report code.",
            negative_body,
            colors,
        ),
        panel(
            "gate_chain",
            "Gate Chain",
            "evidence.boundary",
            "The showcase is public evidence because fixture, viewer, replay, and CLI gates name it.",
            gate_body,
            colors,
        ),
    ]

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Figure 72 - GCS Integrated Showcase Evidence</title>
  <style>
    :root {{
      {css_vars(colors, fonts)}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--gcs-paper);
      color: var(--gcs-ink);
      font-family: var(--gcs-font-sans);
      overflow-wrap: anywhere;
    }}
    main {{
      max-width: 1480px;
      margin: 0 auto;
      padding: 38px;
    }}
    .figure-shell {{
      background: var(--gcs-paper);
      border: 1px solid var(--gcs-rule);
      border-radius: 8px;
      padding: 34px;
    }}
    header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 24px;
      align-items: end;
      border-bottom: 1px solid var(--gcs-rule);
      padding-bottom: 22px;
      margin-bottom: 24px;
    }}
    h1 {{
      font-family: var(--gcs-font-serif);
      font-size: 34px;
      line-height: 1.08;
      margin: 0 0 10px;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 0;
      max-width: 900px;
      color: var(--gcs-muted);
      font-size: 15px;
      line-height: 1.5;
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      min-height: 34px;
      padding: 7px 12px;
      border: 1px solid var(--gcs-planner-stroke);
      border-radius: 999px;
      background: var(--gcs-planner);
      color: var(--gcs-planner-stroke);
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .panel-grid {{
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      gap: 16px;
    }}
    .panel {{
      grid-column: span 4;
      min-height: 280px;
      background: var(--gcs-panel);
      border: 1px solid var(--gcs-rule);
      border-top: 5px solid var(--panel-token-stroke);
      border-radius: 8px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .panel-gate_chain {{
      grid-column: 1 / -1;
      min-height: 210px;
    }}
    .panel-topline {{
      display: flex;
      gap: 14px;
      justify-content: space-between;
      align-items: flex-start;
    }}
    .eyebrow {{
      margin: 0 0 5px;
      font-size: 11px;
      font-weight: 700;
      color: var(--gcs-muted);
    }}
    h2 {{
      margin: 0;
      font-size: 20px;
      line-height: 1.15;
      letter-spacing: 0;
    }}
    .panel-claim {{
      margin: 0;
      color: var(--gcs-muted);
      font-size: 13px;
      line-height: 1.42;
    }}
    .chip,
    .panel-tag {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 6px 10px;
      border: 1px solid var(--chip-stroke);
      border-radius: 999px;
      background: var(--chip-fill);
      color: var(--chip-stroke);
      font-size: 11px;
      font-weight: 700;
    }}
    .scene-contract-layout {{
      display: grid;
      grid-template-columns: minmax(160px, 0.85fr) minmax(0, 1fr);
      gap: 14px;
      align-items: stretch;
    }}
    .scene-glyph {{
      width: 100%;
      min-height: 180px;
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .metric {{
      min-height: 70px;
      border: 1px solid var(--metric-stroke);
      border-radius: 7px;
      background: var(--metric-fill);
      padding: 10px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .metric span {{
      font-size: 10px;
      color: var(--gcs-muted);
      font-weight: 700;
    }}
    .metric strong {{
      font-size: 18px;
      line-height: 1.1;
    }}
    .evidence-list,
    .rank-list,
    .gate-layout ul {{
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 10px;
    }}
    .evidence-list p,
    .rank-list li,
    .gate-layout li {{
      margin: 0;
      padding: 10px 11px;
      border: 1px solid var(--gcs-rule-soft);
      border-radius: 7px;
      background: var(--gcs-surface);
      font-size: 13px;
      line-height: 1.38;
    }}
    .rank-list li {{
      display: grid;
      gap: 4px;
    }}
    .rank-list span {{
      color: var(--gcs-muted);
    }}
    .negative-list p:first-child {{
      border-color: var(--gcs-failure-stroke);
      background: var(--gcs-failure);
    }}
    .gate-layout {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(260px, 0.65fr);
      gap: 18px;
      align-items: start;
    }}
    .panel-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    @media (max-width: 980px) {{
      main {{ padding: 16px; }}
      .figure-shell {{ padding: 20px; }}
      header,
      .scene-contract-layout,
      .gate-layout {{
        grid-template-columns: 1fr;
      }}
      .panel {{ grid-column: 1 / -1; }}
    }}
  </style>
</head>
<body>
  <main>
    <article class="figure-shell">
      <header>
        <div>
          <h1 {text_attrs("figure72-title", 70)} {contrast_attrs("figure72-title", colors["ink"], colors["paper"])}>GCS Integrated Showcase Evidence</h1>
          <p class="subtitle" {text_attrs("figure72-subtitle", 190)} {contrast_attrs("figure72-subtitle", colors["muted"], colors["paper"])}>One public constraint scene carries solve intent through decomposition, numeric evidence, gluing diagnostics, viewer projection, CLI smoke, and typed rejection evidence.</p>
        </div>
        <span class="status-pill" {text_attrs("figure72-status", 44)} {contrast_attrs("figure72-status", colors["planner_stroke"], colors["planner"], 3.0)}>{esc(expected["solve_status"])}</span>
      </header>
      <div class="panel-grid">
        {''.join(panels)}
      </div>
    </article>
  </main>
</body>
</html>
"""


def write_html(path: Path, html_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the tokenized Figure 72 showcase HTML")
    parser.add_argument("--out-html", type=Path, default=DEFAULT_OUT_HTML)
    parser.add_argument("--check", action="store_true", help="Fail if the generated HTML differs from the target")
    args = parser.parse_args(argv)

    out_html = args.out_html if args.out_html.is_absolute() else ROOT / args.out_html
    html_text = render_html(load_context())
    if args.check:
        if not out_html.is_file():
            print(f"ERROR: missing generated HTML {out_html}")
            return 1
        current = out_html.read_text(encoding="utf-8-sig")
        if current != html_text:
            print(f"ERROR: generated HTML is stale: {out_html}")
            return 1
        print(f"Figure 72 showcase HTML is up to date: {out_html}")
        return 0

    write_html(out_html, html_text)
    print(f"wrote {out_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
