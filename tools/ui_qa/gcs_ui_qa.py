from __future__ import annotations

import ast
import importlib.util
import json
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_DIR = REPO_ROOT / "python"

REQUIRED_DOCS = [
    "docs/architecture/72-ui-aesthetic-roadmap.md",
    "docs/architecture/72-ui-aesthetic-phase-3-inspector-layout.md",
    "docs/architecture/72-ui-aesthetic-phase-4-replay-solve-polish.md",
    "docs/architecture/72-ui-aesthetic-phase-5-design-qa-accessibility.md",
]

REQUIRED_THEME_KEYS = [
    "bg_window",
    "bg_panel",
    "bg_panel_alt",
    "bg_canvas",
    "bg_table",
    "text_primary",
    "text_secondary",
    "text_muted",
    "text_on_accent",
    "accent",
    "success",
    "warning",
    "error",
    "border",
    "grid",
]

ACTIVE_GUI_BUILDERS = {"_build_inspector_panel", "_build_right_panel"}
ASCII_LABEL_RE = re.compile(r"^[\x20-\x7E]+$")
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


@dataclass
class QaResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def require(self, condition: bool, message: str):
        if not condition:
            self.errors.append(message)

    def warn(self, condition: bool, message: str):
        if not condition:
            self.warnings.append(message)


def _load_color_scheme(repo_root: Path):
    module_path = repo_root / "python" / "gcs_viz" / "color_scheme.py"
    spec = importlib.util.spec_from_file_location("gcs_ui_qa_color_scheme", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _rgb(hex_color: str) -> tuple[float, float, float]:
    value = hex_color.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _linear(channel: float) -> float:
    if channel <= 0.03928:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def contrast_ratio(foreground: str, background: str) -> float:
    fg = _rgb(foreground)
    bg = _rgb(background)
    fg_lum = 0.2126 * _linear(fg[0]) + 0.7152 * _linear(fg[1]) + 0.0722 * _linear(fg[2])
    bg_lum = 0.2126 * _linear(bg[0]) + 0.7152 * _linear(bg[1]) + 0.0722 * _linear(bg[2])
    lighter = max(fg_lum, bg_lum)
    darker = min(fg_lum, bg_lum)
    return (lighter + 0.05) / (darker + 0.05)


def check_docs(repo_root: Path, result: QaResult):
    for relative in REQUIRED_DOCS:
        path = repo_root / relative
        result.require(path.exists(), f"Missing UI aesthetic design doc: {relative}")


def check_theme(repo_root: Path, result: QaResult):
    color_scheme = _load_color_scheme(repo_root)
    theme = color_scheme.GCS_THEME
    for key in REQUIRED_THEME_KEYS:
        result.require(key in theme, f"Missing GCS_THEME token: {key}")
        if key in theme:
            result.require(bool(HEX_RE.match(theme[key])), f"GCS_THEME token {key} is not a #RRGGBB color")

    if result.errors:
        return

    backgrounds = ["bg_window", "bg_panel", "bg_panel_alt", "bg_canvas", "bg_table"]
    for text_key in ("text_primary", "text_secondary"):
        for bg_key in backgrounds:
            ratio = contrast_ratio(theme[text_key], theme[bg_key])
            result.require(
                ratio >= 4.5,
                f"{text_key} on {bg_key} contrast is {ratio:.2f}, expected >= 4.5",
            )

    state_text = getattr(color_scheme, "STATE_TEXT_COLORS", {})
    result.require(bool(state_text), "color_scheme.py must expose STATE_TEXT_COLORS for small status text")
    for state_key in ("solved", "info", "warning", "error", "pending", "replay_current"):
        if state_key not in state_text:
            result.errors.append(f"Missing STATE_TEXT_COLORS token: {state_key}")
            continue
        for bg_key in ("bg_window", "bg_panel", "bg_panel_alt"):
            ratio = contrast_ratio(state_text[state_key], theme[bg_key])
            result.require(
                ratio >= 4.5,
                f"STATE_TEXT_COLORS[{state_key!r}] on {bg_key} contrast is {ratio:.2f}, expected >= 4.5",
            )

    node_light = theme.get("text_node_light")
    node_dark = theme.get("text_node_dark")
    result.require(bool(node_light and node_dark), "GCS_THEME must expose text_node_light and text_node_dark")
    for index, fill in enumerate(getattr(color_scheme, "RIGID_SET_COLORS", []), start=1):
        light_ratio = contrast_ratio(node_light, fill)
        dark_ratio = contrast_ratio(node_dark, fill)
        result.require(
            max(light_ratio, dark_ratio) >= 4.5,
            f"rigidSet.palette.{index:02d} has no readable dynamic graph-node label color",
        )

    for semantic_key in ("success", "warning", "error", "info", "accent"):
        if semantic_key not in theme:
            continue
        ratio = contrast_ratio(theme[semantic_key], theme["bg_panel_alt"])
        result.warn(
            ratio >= 4.5,
            f"{semantic_key} on bg_panel_alt contrast is {ratio:.2f}; use as graphic/status accent, not small body text",
        )


def _parent_methods(tree: ast.AST) -> dict[ast.AST, str]:
    parents: dict[ast.AST, str] = {}

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef):
            self.stack.append(node.name)
            for child in node.body:
                parents[child] = node.name
                self.visit(child)
            self.stack.pop()

        def generic_visit(self, node: ast.AST):
            if self.stack:
                parents[node] = self.stack[-1]
            super().generic_visit(node)

    Visitor().visit(tree)
    return parents


def _is_ttk_button_call(call: ast.Call) -> bool:
    func = call.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "Button"
        and isinstance(func.value, ast.Name)
        and func.value.id == "ttk"
    )


def check_gui_static(repo_root: Path, result: QaResult):
    path = repo_root / "python" / "gcs_viz" / "platform_gui.py"
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(path))
    methods = _parent_methods(tree)

    for token in (
        "summary_model_var",
        "summary_counts_var",
        "replay_state_var",
        "replay_progress_var",
        "solve_summary_var",
        "_build_inspector_panel",
    ):
        result.require(token in source, f"platform_gui.py missing UI contract token: {token}")

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _is_ttk_button_call(node):
            continue
        if methods.get(node) not in ACTIVE_GUI_BUILDERS:
            continue
        for keyword in node.keywords:
            if keyword.arg == "text" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                label = keyword.value.value
                result.require(
                    bool(ASCII_LABEL_RE.match(label)),
                    f"Active command label should be ASCII text, got {label!r}",
                )


def check_ui_fixture(repo_root: Path, result: QaResult):
    fixture_path = repo_root / "fixtures" / "scene" / "ui_qa" / "mixed_geometry_constraints.json"
    result.require(fixture_path.exists(), "Missing UI QA fixture: fixtures/scene/ui_qa/mixed_geometry_constraints.json")
    if not fixture_path.exists():
        return

    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    geometries = {int(item["id"]): item for item in data.get("geometries", [])}
    geometry_types = {int(item["type"]) for item in geometries.values()}
    constraint_types = {int(item["type"]) for item in data.get("constraints", [])}
    result.require({0, 1, 2}.issubset(geometry_types), "UI QA fixture must cover point, line, and plane geometries")
    result.require(set(range(5)).issubset(constraint_types), "UI QA fixture must cover all five constraint types")

    for constraint in data.get("constraints", []):
        geometry_ids = [int(gid) for gid in constraint.get("geometry_ids", [])]
        result.require(len(geometry_ids) >= 2, f"Constraint {constraint.get('id')} must reference at least two geometries")
        rs_ids = {
            int(geometries[gid]["rigid_set_id"])
            for gid in geometry_ids
            if gid in geometries
        }
        result.require(
            len(rs_ids) >= 2,
            f"Constraint {constraint.get('id')} must span multiple rigid sets",
        )


def check_optional_headless_render(repo_root: Path, result: QaResult):
    try:
        sys.path.insert(0, str(repo_root / "python"))
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from gcs_viz.algebra import read_graph_file
        from gcs_viz.viewer_bridge import render_graph_view
    except ModuleNotFoundError as exc:
        result.notes.append(f"Headless render skipped: missing {exc.name}")
        return

    fixture = repo_root / "fixtures" / "scene" / "ui_qa" / "mixed_geometry_constraints.json"
    graph = read_graph_file(str(fixture))
    focus = {"mode": "qa", "geometry_ids": [0], "constraint_ids": [0], "rigid_set_ids": [0]}
    with tempfile.TemporaryDirectory() as tmp:
        for view in ("3d", "graph", "3view"):
            fig = plt.figure(figsize=(4, 3), dpi=80)
            render_graph_view(graph, fig, view=view, title=f"QA {view}", focus=focus)
            output = Path(tmp) / f"{view}.png"
            fig.savefig(output)
            result.require(output.stat().st_size > 1024, f"Headless render for {view} looks empty")
            plt.close(fig)


def run_checks(repo_root: Path = REPO_ROOT) -> QaResult:
    result = QaResult()
    check_docs(repo_root, result)
    check_theme(repo_root, result)
    check_gui_static(repo_root, result)
    check_ui_fixture(repo_root, result)
    check_optional_headless_render(repo_root, result)
    return result


def main() -> int:
    result = run_checks()
    for note in result.notes:
        print(f"NOTE: {note}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.ok:
        print("UI QA checks passed")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
