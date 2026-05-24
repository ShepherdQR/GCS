#!/usr/bin/env python3
"""Render the scene-backed integrated showcase figure and report."""

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
DEFAULT_OUT_SVG = (
    ROOT / "docs" / "architecture" / "70-visualization" / "assets"
    / "figure72-gcs-integrated-showcase-scene.svg"
)
DEFAULT_OUT_REPORT = (
    ROOT / "docs" / "architecture" / "70-visualization"
    / "showcase-scene-report.md"
)

GEOMETRY_NAMES = {0: "Point", 1: "Line", 2: "Plane"}
CONSTRAINT_NAMES = {0: "Coincident", 1: "Parallel", 2: "Perpendicular", 3: "Distance", 4: "Angle"}
COLORS = {
    "paper": "#f7f4ec",
    "panel": "#fffefa",
    "rule": "#d8d1c4",
    "muted": "#5f5b53",
    "ink": "#181715",
    "point": "#334c78",
    "line": "#477861",
    "plane": "#765d87",
    "constraint": "#b97834",
    "fixed": "#c8643f",
    "positive": "#4b8a64",
    "negative": "#a94c43",
    "chip": "#efede6",
    "component_a": "#e7edf8",
    "component_b": "#e3f0e4",
}
FONT = "Anthropic Sans, Inter, Segoe UI, Arial, sans-serif"
SERIF = "Anthropic Serif, Georgia, Cambria, Times New Roman, serif"


@dataclass(frozen=True)
class Entity:
    id: int
    type: int
    rigid_set_id: int
    values: tuple[float, ...]


@dataclass(frozen=True)
class Constraint:
    id: int
    type: int
    geometry_ids: tuple[int, ...]
    value: float


@dataclass(frozen=True)
class ShowcaseModel:
    scene_path: Path
    metadata_path: Path
    negative_metadata_path: Path
    scene: dict[str, Any]
    metadata: dict[str, Any]
    negative_metadata: dict[str, Any]
    entities: tuple[Entity, ...]
    constraints: tuple[Constraint, ...]
    fixed_geometry_ids: tuple[int, ...]
    components: tuple[tuple[int, ...], ...]


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def build_components(entity_ids: list[int], constraints: tuple[Constraint, ...]) -> tuple[tuple[int, ...], ...]:
    parent = {entity_id: entity_id for entity_id in entity_ids}

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(a: int, b: int) -> None:
        root_a = find(a)
        root_b = find(b)
        if root_a != root_b:
            parent[root_b] = root_a

    for constraint in constraints:
        ids = list(constraint.geometry_ids)
        for current in ids[1:]:
            union(ids[0], current)

    groups: dict[int, list[int]] = {}
    for entity_id in entity_ids:
        groups.setdefault(find(entity_id), []).append(entity_id)
    return tuple(tuple(sorted(group)) for group in sorted(groups.values(), key=lambda ids: ids[0]))


def load_showcase_model(
    scene_path: Path = DEFAULT_SCENE,
    metadata_path: Path = DEFAULT_METADATA,
    negative_metadata_path: Path = DEFAULT_NEGATIVE_METADATA,
) -> ShowcaseModel:
    scene = read_json(scene_path)
    metadata = read_json(metadata_path)
    negative_metadata = read_json(negative_metadata_path)
    entities = tuple(
        Entity(
            id=int(item["id"]),
            type=int(item["type"]),
            rigid_set_id=int(item["rigid_set_id"]),
            values=tuple(float(value) for value in item.get("v", [])),
        )
        for item in sorted(scene.get("geometries", []), key=lambda item: int(item["id"]))
    )
    constraints = tuple(
        Constraint(
            id=int(item["id"]),
            type=int(item["type"]),
            geometry_ids=tuple(int(value) for value in item.get("geometry_ids", [])),
            value=float(item.get("value", 0.0)),
        )
        for item in sorted(scene.get("constraints", []), key=lambda item: int(item["id"]))
    )
    behavior = scene.get("behavior", {})
    fixed_geometry_ids = tuple(int(value) for value in behavior.get("fixed_geometry_ids", []))
    components = build_components([entity.id for entity in entities], constraints)
    return ShowcaseModel(
        scene_path=scene_path,
        metadata_path=metadata_path,
        negative_metadata_path=negative_metadata_path,
        scene=scene,
        metadata=metadata,
        negative_metadata=negative_metadata,
        entities=entities,
        constraints=constraints,
        fixed_geometry_ids=fixed_geometry_ids,
        components=components,
    )


def display_position(entity: Entity) -> tuple[float, float]:
    x = entity.values[0] if len(entity.values) > 0 else 0.0
    y = entity.values[1] if len(entity.values) > 1 else 0.0
    if entity.type == 1:
        return x + 0.18, y - 0.22
    if entity.type == 2:
        return x + 0.32, y + 0.22
    if entity.id == 3:
        return x - 0.22, y - 0.18
    return x, y


def svg_text(text: str, x: float, y: float, size: int, weight: int = 400,
             fill: str = COLORS["ink"], anchor: str = "start", family: str = FONT) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(text)}</text>'
    )


def chip(label: str, value: object, x: float, y: float, width: float) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="32" rx="6" '
        f'fill="{COLORS["chip"]}" stroke="{COLORS["rule"]}" stroke-width="1"/>'
        + svg_text(label, x + 10, y + 13, 9, 700, COLORS["muted"])
        + svg_text(str(value), x + width - 10, y + 23, 13, 700, COLORS["ink"], "end")
    )


def render_svg(model: ShowcaseModel) -> str:
    width, height = 1200, 760
    panel_x, panel_y, panel_w, panel_h = 54, 132, 770, 500
    evidence_x, evidence_y, evidence_w, evidence_h = 850, 132, 296, 500
    positions = {entity.id: display_position(entity) for entity in model.entities}
    min_x = min(x for x, _ in positions.values())
    max_x = max(x for x, _ in positions.values())
    min_y = min(y for _, y in positions.values())
    max_y = max(y for _, y in positions.values())
    scale_x = (panel_w - 180) / max(1.0, max_x - min_x)
    scale_y = (panel_h - 190) / max(1.0, max_y - min_y)
    scale = min(scale_x, scale_y)

    def project(entity_id: int) -> tuple[float, float]:
        x, y = positions[entity_id]
        sx = panel_x + 92 + (x - min_x) * scale
        sy = panel_y + panel_h - 100 - (y - min_y) * scale
        return sx, sy

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">',
        '<title id="title">GCS Integrated Showcase Scene</title>',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{COLORS["paper"]}"/>',
        svg_text("Figure 72 | GCS Integrated Showcase Scene", 54, 58, 30, 650, family=SERIF),
        svg_text("Scene-backed public demo from fixtures/scene/showcase, with behavior intent and negative validation evidence.", 54, 88, 13, 400, COLORS["muted"]),
        svg_text(f"Source: {rel(model.scene_path)}", width - 54, 88, 12, 400, COLORS["muted"], "end"),
        f'<rect x="{panel_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="8" '
        f'fill="{COLORS["panel"]}" stroke="{COLORS["rule"]}" stroke-width="1.1"/>',
        f'<rect x="{evidence_x}" y="{evidence_y}" width="{evidence_w}" height="{evidence_h}" rx="8" '
        f'fill="{COLORS["panel"]}" stroke="{COLORS["rule"]}" stroke-width="1.1"/>',
        svg_text("Public scene graph", panel_x + 24, panel_y + 36, 18, 700),
        svg_text("Evidence contract", evidence_x + 24, evidence_y + 36, 18, 700),
    ]

    for index, component in enumerate(model.components):
        xs = [project(entity_id)[0] for entity_id in component]
        ys = [project(entity_id)[1] for entity_id in component]
        fill = COLORS["component_a"] if index == 0 else COLORS["component_b"]
        parts.append(
            f'<rect x="{min(xs) - 54:.1f}" y="{min(ys) - 54:.1f}" '
            f'width="{max(xs) - min(xs) + 108:.1f}" height="{max(ys) - min(ys) + 108:.1f}" '
            f'rx="10" fill="{fill}" stroke="{COLORS["rule"]}" stroke-dasharray="6 5" opacity="0.55"/>'
        )
        parts.append(svg_text(f"local component {index + 1}", min(xs) - 42, min(ys) - 32, 11, 700, COLORS["muted"]))

    for constraint in model.constraints:
        if len(constraint.geometry_ids) < 2:
            continue
        a, b = constraint.geometry_ids[0], constraint.geometry_ids[1]
        x1, y1 = project(a)
        x2, y2 = project(b)
        parts.append(
            f'<line id="constraint-{constraint.id}" x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" stroke="{COLORS["constraint"]}" stroke-width="2.4"/>'
        )
        parts.append(svg_text(
            f"C{constraint.id} {CONSTRAINT_NAMES.get(constraint.type, 'Constraint')}",
            (x1 + x2) / 2,
            (y1 + y2) / 2 - 10,
            10,
            700,
            COLORS["constraint"],
            "middle",
        ))

    for entity in model.entities:
        x, y = project(entity.id)
        is_fixed = entity.id in model.fixed_geometry_ids
        color = COLORS["point"] if entity.type == 0 else COLORS["line"] if entity.type == 1 else COLORS["plane"]
        if entity.type == 0:
            parts.append(f'<circle id="entity-{entity.id}" cx="{x:.1f}" cy="{y:.1f}" r="16" fill="{color}"/>')
        elif entity.type == 1:
            parts.append(
                f'<rect id="entity-{entity.id}" x="{x - 22:.1f}" y="{y - 13:.1f}" '
                f'width="44" height="26" rx="5" fill="{color}"/>'
            )
        else:
            parts.append(
                f'<polygon id="entity-{entity.id}" points="{x:.1f},{y - 20:.1f} '
                f'{x + 22:.1f},{y:.1f} {x:.1f},{y + 20:.1f} {x - 22:.1f},{y:.1f}" '
                f'fill="{color}"/>'
            )
        if is_fixed:
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="24" fill="none" '
                f'stroke="{COLORS["fixed"]}" stroke-width="3"/>'
            )
            parts.append(svg_text("fixed", x, y - 34, 10, 700, COLORS["fixed"], "middle"))
        parts.append(svg_text(
            f"G{entity.id} {GEOMETRY_NAMES.get(entity.type, 'Geometry')}",
            x,
            y + 38,
            11,
            700,
            COLORS["ink"],
            "middle",
        ))

    expected = model.metadata.get("expected_public_evidence", {})
    parts.extend([
        chip("schema", model.scene.get("format_version", "?"), evidence_x + 24, evidence_y + 66, 248),
        chip("geometries", expected.get("geometries", len(model.entities)), evidence_x + 24, evidence_y + 108, 118),
        chip("constraints", expected.get("constraints", len(model.constraints)), evidence_x + 154, evidence_y + 108, 118),
        chip("fixed ids", ",".join(str(value) for value in model.fixed_geometry_ids), evidence_x + 24, evidence_y + 150, 248),
        chip("subproblems", expected.get("planner_subproblems", "?"), evidence_x + 24, evidence_y + 192, 118),
        chip("numeric reports", expected.get("numeric_reports", "?"), evidence_x + 154, evidence_y + 192, 118),
        chip("solve status", expected.get("solve_status", "?"), evidence_x + 24, evidence_y + 234, 248),
    ])

    negative = model.negative_metadata.get("expected_public_evidence", {})
    parts.append(
        f'<rect x="{evidence_x + 24:.1f}" y="{evidence_y + 296:.1f}" width="248" height="112" rx="7" '
        f'fill="#f3ddd7" stroke="{COLORS["negative"]}" stroke-width="1.1"/>'
    )
    parts.append(svg_text("negative behavior boundary", evidence_x + 40, evidence_y + 322, 12, 700, COLORS["negative"]))
    parts.append(svg_text(str(negative.get("report_code", "missing report")), evidence_x + 40, evidence_y + 350, 11, 700))
    parts.append(svg_text(
        f"missing fixed ids: {negative.get('missing_fixed_geometry_ids', [])}",
        evidence_x + 40,
        evidence_y + 374,
        11,
        400,
        COLORS["muted"],
    ))

    parts.append(svg_text("Regenerate: python tools/architecture_visualization/render_showcase_scene.py", 54, height - 46, 11, 400, COLORS["muted"]))
    parts.append("</svg>\n")
    return "\n".join(parts)


def build_report(model: ShowcaseModel) -> str:
    expected = model.metadata.get("expected_public_evidence", {})
    negative = model.negative_metadata.get("expected_public_evidence", {})
    return f"""# Integrated Showcase Scene Report

Source scene: `{rel(model.scene_path)}`

Metadata: `{rel(model.metadata_path)}`

Generated figure: `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.svg`

## Public Evidence

| Evidence | Value |
| --- | --- |
| Schema | `{model.scene.get("format_version", "?")}` |
| Rigid sets | `{expected.get("rigid_sets", len(model.scene.get("rigid_sets", [])))}` |
| Geometries | `{expected.get("geometries", len(model.entities))}` |
| Constraints | `{expected.get("constraints", len(model.constraints))}` |
| Fixed geometry IDs | `{list(model.fixed_geometry_ids)}` |
| Planner subproblems | `{expected.get("planner_subproblems", "?")}` |
| Numeric reports | `{expected.get("numeric_reports", "?")}` |
| Solve status | `{expected.get("solve_status", "?")}` |

## Negative Variant

| Evidence | Value |
| --- | --- |
| Metadata | `{rel(model.negative_metadata_path)}` |
| Expected report code | `{negative.get("report_code", "?")}` |
| Missing fixed geometry IDs | `{negative.get("missing_fixed_geometry_ids", [])}` |

## Regeneration

```bat
python tools\\architecture_visualization\\render_showcase_scene.py
```
"""


def write_outputs(model: ShowcaseModel, out_svg: Path, out_report: Path) -> None:
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_svg.write_text(render_svg(model), encoding="utf-8", newline="\n")
    out_report.write_text(build_report(model), encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", type=Path, default=DEFAULT_SCENE)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--negative-metadata", type=Path, default=DEFAULT_NEGATIVE_METADATA)
    parser.add_argument("--out-svg", type=Path, default=DEFAULT_OUT_SVG)
    parser.add_argument("--out-report", type=Path, default=DEFAULT_OUT_REPORT)
    args = parser.parse_args(argv)

    model = load_showcase_model(args.scene, args.metadata, args.negative_metadata)
    write_outputs(model, args.out_svg, args.out_report)
    print(f"wrote {rel(args.out_svg)}")
    print(f"wrote {rel(args.out_report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
