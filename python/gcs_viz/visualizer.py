import os
from typing import Mapping, Optional

import numpy as np
import matplotlib
if os.environ.get("GCS_GUI") != "1":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import networkx as nx

from gcs_viz.algebra import GCSGraph, GeometryType
from gcs_viz.color_scheme import (
    RIGID_SET_COLORS,
    CONSTRAINT_COLORS,
    GEOMETRY_MARKERS,
    GEOMETRY_NODE_SIZES,
    CONSTRAINT_LINE_STYLES,
    CONSTRAINT_GRAPH_LINE_STYLES,
    GEOMETRY_NAMES,
    CONSTRAINT_NAMES,
    GCS_THEME,
    STATE_COLORS,
)


def _hex_rgb(color: str) -> tuple[float, float, float]:
    value = str(color or "").strip().lstrip("#")
    if len(value) != 6:
        return (0.0, 0.0, 0.0)
    try:
        return tuple(int(value[index:index + 2], 16) / 255.0 for index in (0, 2, 4))
    except ValueError:
        return (0.0, 0.0, 0.0)


def _linear_channel(channel: float) -> float:
    if channel <= 0.03928:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def _relative_luminance(color: str) -> float:
    red, green, blue = _hex_rgb(color)
    return (
        0.2126 * _linear_channel(red)
        + 0.7152 * _linear_channel(green)
        + 0.0722 * _linear_channel(blue)
    )


def _contrast_ratio(foreground: str, background: str) -> float:
    fg = _relative_luminance(foreground)
    bg = _relative_luminance(background)
    lighter = max(fg, bg)
    darker = min(fg, bg)
    return (lighter + 0.05) / (darker + 0.05)


def _label_color_for_fill(fill_color: str) -> str:
    light = GCS_THEME["text_node_light"]
    dark = GCS_THEME["text_node_dark"]
    if _contrast_ratio(light, fill_color) >= _contrast_ratio(dark, fill_color):
        return light
    return dark


def _get_rs_color(graph: GCSGraph, rs_id: int) -> str:
    for i, rs in enumerate(graph.rigid_sets):
        if rs.id == rs_id:
            return RIGID_SET_COLORS[i % len(RIGID_SET_COLORS)]
    return GCS_THEME["text_muted"]


def _get_rs_color_index(graph: GCSGraph, rs_id: int) -> int:
    for i, rs in enumerate(graph.rigid_sets):
        if rs.id == rs_id:
            return i
    return 0


def _focus_ids(focus: Optional[Mapping], key: str) -> set[int]:
    if not focus:
        return set()
    result = set()
    for value in focus.get(key, []) or []:
        try:
            result.add(int(value))
        except (TypeError, ValueError):
            continue
    return result


def _constraint_states(focus: Optional[Mapping]) -> dict[int, str]:
    if not focus:
        return {}
    states = {}
    for key, value in (focus.get("constraint_states") or {}).items():
        try:
            constraint_id = int(key)
        except (TypeError, ValueError):
            continue
        normalized = str(value or "unknown").strip().lower()
        if normalized not in ("satisfied", "violated", "unknown"):
            normalized = "unknown"
        states[constraint_id] = normalized
    return states


def _constraint_state(constraint, focus: Optional[Mapping]) -> Optional[str]:
    return _constraint_states(focus).get(constraint.id)


def _has_constraint_states(focus: Optional[Mapping]) -> bool:
    return bool(_constraint_states(focus))


def _is_focused_geometry(geometry, focus: Optional[Mapping]) -> bool:
    return (
        geometry.id in _focus_ids(focus, "geometry_ids")
        or geometry.rigid_set_id in _focus_ids(focus, "rigid_set_ids")
    )


def _is_focused_constraint(constraint, focus: Optional[Mapping]) -> bool:
    return constraint.id in _focus_ids(focus, "constraint_ids")


def _has_focus(focus: Optional[Mapping]) -> bool:
    return bool(
        _focus_ids(focus, "constraint_ids")
        or _focus_ids(focus, "geometry_ids")
        or _focus_ids(focus, "rigid_set_ids")
    )


def _constraint_color(constraint, focus: Optional[Mapping]) -> str:
    state = _constraint_state(constraint, focus)
    if state == "violated":
        return STATE_COLORS["violated"]
    if state == "satisfied":
        return STATE_COLORS["solved"]
    if state == "unknown":
        return STATE_COLORS["pending"]
    if _is_focused_constraint(constraint, focus):
        return STATE_COLORS["focus"]
    return CONSTRAINT_COLORS.get(int(constraint.type), GCS_THEME["constraint_default"])


def _constraint_line_style(constraint_type) -> object:
    return CONSTRAINT_LINE_STYLES.get(int(constraint_type), "dashed")


def _constraint_graph_line_style(constraint_type) -> str:
    return CONSTRAINT_GRAPH_LINE_STYLES.get(int(constraint_type), "dashed")


def _constraint_line_width(constraint, focus: Optional[Mapping]) -> float:
    if _is_focused_constraint(constraint, focus):
        return 2.7
    state = _constraint_state(constraint, focus)
    if state == "violated":
        return 2.35
    if state == "satisfied":
        return 1.15
    return 1.35


def _constraint_alpha(constraint, focus: Optional[Mapping]) -> float:
    if _is_focused_constraint(constraint, focus):
        return 0.95
    state = _constraint_state(constraint, focus)
    if state == "violated":
        return 0.92
    if state == "satisfied":
        return 0.42
    if state == "unknown":
        return 0.50
    return 0.56


def _geometry_label_color(color: str, focused: bool) -> str:
    return STATE_COLORS["focus_active"] if focused else color


def _constraint_label(constraint, focused: bool, state: Optional[str] = None) -> str:
    if focused:
        label = f"C{constraint.id} {CONSTRAINT_NAMES.get(int(constraint.type), '?')}"
        if constraint.value != 0:
            label += f"={constraint.value:g}"
        if state:
            label += f" {state.upper()}"
        return label
    if state == "violated":
        return f"C{constraint.id} VIOL"
    if state == "unknown":
        return f"C{constraint.id} UNK"
    return f"C{constraint.id}"


def _apply_figure_theme(fig):
    fig.patch.set_facecolor(GCS_THEME["bg_canvas"])


def _style_2d_axis(ax, grid: bool = False):
    ax.set_facecolor(GCS_THEME["bg_canvas"])
    ax.title.set_color(GCS_THEME["text_primary"])
    ax.xaxis.label.set_color(GCS_THEME["text_secondary"])
    ax.yaxis.label.set_color(GCS_THEME["text_secondary"])
    ax.tick_params(colors=GCS_THEME["axis"], labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GCS_THEME["border"])
    if grid:
        ax.grid(True, color=GCS_THEME["grid"], alpha=0.45, linewidth=0.8)


def _style_3d_axis(ax):
    ax.set_facecolor(GCS_THEME["bg_canvas"])
    ax.title.set_color(GCS_THEME["text_primary"])
    ax.xaxis.label.set_color(GCS_THEME["text_secondary"])
    ax.yaxis.label.set_color(GCS_THEME["text_secondary"])
    ax.zaxis.label.set_color(GCS_THEME["text_secondary"])
    ax.tick_params(colors=GCS_THEME["axis"], labelsize=8)
    pane = to_rgba(GCS_THEME["bg_canvas"], 0.96)
    grid = to_rgba(GCS_THEME["grid"], 0.55)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color(pane)
        axis._axinfo["grid"]["color"] = grid
        axis._axinfo["grid"]["linewidth"] = 0.8


def _style_legend(legend):
    if legend is None:
        return
    frame = legend.get_frame()
    frame.set_facecolor(GCS_THEME["bg_canvas"])
    frame.set_edgecolor(GCS_THEME["border"])
    frame.set_alpha(0.92)
    for text in legend.get_texts():
        text.set_color(GCS_THEME["text_secondary"])


def _geometry_anchor_3d(geometry) -> np.ndarray:
    if geometry.type == GeometryType.Line:
        return np.array(
            [
                (geometry.v[0] + geometry.v[3]) / 2,
                (geometry.v[1] + geometry.v[4]) / 2,
                (geometry.v[2] + geometry.v[5]) / 2,
            ]
        )
    return np.array([geometry.v[0], geometry.v[1], geometry.v[2]])


def _geometry_anchor_2d(geometry, dim1: int, dim2: int) -> tuple[float, float]:
    if geometry.type == GeometryType.Line:
        return (
            (geometry.v[dim1] + geometry.v[dim1 + 3]) / 2,
            (geometry.v[dim2] + geometry.v[dim2 + 3]) / 2,
        )
    return geometry.v[dim1], geometry.v[dim2]


def _draw_geometry_3d(ax, geometry, color: str, focused: bool):
    label_color = _geometry_label_color(color, focused)
    text_alpha = 0.95 if focused else 0.74

    if geometry.type == GeometryType.Point:
        point = np.array([geometry.v[0], geometry.v[1], geometry.v[2]])
        if focused:
            ax.scatter(
                [point[0]], [point[1]], [point[2]],
                color=STATE_COLORS["selected"], s=190, alpha=0.18,
                edgecolors="none", depthshade=False, zorder=7,
            )
        ax.scatter(
            [point[0]], [point[1]], [point[2]],
            color=color, s=98 if focused else 72, depthshade=True,
            edgecolors=GCS_THEME["bg_canvas"], linewidths=1.5 if focused else 0.9,
            zorder=8 if focused else 5,
        )
        ax.text(
            point[0], point[1], point[2] + 0.08, f"G{geometry.id}",
            fontsize=8, ha="center", color=label_color, alpha=text_alpha,
        )
        return

    if geometry.type == GeometryType.Line:
        p1 = np.array([geometry.v[0], geometry.v[1], geometry.v[2]])
        p2 = np.array([geometry.v[3], geometry.v[4], geometry.v[5]])
        if focused:
            ax.plot(
                [p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                color=STATE_COLORS["selected"], linewidth=5.5, alpha=0.24, zorder=6,
            )
        ax.plot(
            [p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
            color=color, linewidth=2.7 if focused else 2.0, zorder=7 if focused else 4,
        )
        mid = (p1 + p2) / 2
        ax.text(
            mid[0], mid[1], mid[2] + 0.08, f"G{geometry.id}",
            fontsize=8, ha="center", color=label_color, alpha=text_alpha,
        )
        for point in (p1, p2):
            ax.scatter(
                [point[0]], [point[1]], [point[2]],
                color=color, s=42 if focused else 26, depthshade=True,
                edgecolors=GCS_THEME["bg_canvas"], linewidths=1.1,
                zorder=8 if focused else 5,
            )
        return

    if geometry.type == GeometryType.Plane:
        pos = np.array([geometry.v[0], geometry.v[1], geometry.v[2]])
        normal = np.array([geometry.v[3], geometry.v[4], geometry.v[5]])
        norm = np.linalg.norm(normal)
        normal = np.array([0, 0, 1]) if norm < 1e-12 else normal / norm
        if abs(normal[2]) < 0.9:
            u = np.cross(normal, [0, 0, 1])
        else:
            u = np.cross(normal, [1, 0, 0])
        u = u / np.linalg.norm(u)
        v = np.cross(normal, u)
        v = v / np.linalg.norm(v)
        size = 1.0
        corners = [
            pos + size * (-u - v),
            pos + size * (u - v),
            pos + size * (u + v),
            pos + size * (-u + v),
        ]
        poly = Poly3DCollection(
            [corners],
            facecolor=to_rgba(color, 0.30 if focused else 0.22),
            edgecolor=STATE_COLORS["selected"] if focused else color,
            linewidth=2.0 if focused else 1.0,
        )
        ax.add_collection3d(poly)
        ax.text(
            pos[0], pos[1], pos[2] + 0.15, f"G{geometry.id}",
            fontsize=8, ha="center", color=label_color, alpha=text_alpha,
        )


def _draw_constraints_3d(graph: GCSGraph, ax, focus: Optional[Mapping]):
    show_default_labels = len(graph.constraints) <= 8
    for constraint in graph.constraints:
        positions = []
        for gid in constraint.geometry_ids:
            geometry = graph.find_geometry(gid)
            if geometry is not None:
                positions.append(_geometry_anchor_3d(geometry))

        focused = _is_focused_constraint(constraint, focus)
        state = _constraint_state(constraint, focus)
        color = _constraint_color(constraint, focus)
        linewidth = _constraint_line_width(constraint, focus)
        alpha = _constraint_alpha(constraint, focus)
        linestyle = _constraint_line_style(constraint.type)

        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                p1, p2 = positions[i], positions[j]
                ax.plot(
                    [p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                    color=color, linewidth=linewidth, linestyle=linestyle,
                    alpha=alpha, zorder=9 if focused else 3,
                )
                if focused or show_default_labels:
                    mid = (p1 + p2) / 2
                    ax.text(
                        mid[0], mid[1], mid[2] - 0.1,
                        _constraint_label(constraint, focused, state),
                        fontsize=7 if focused else 6,
                        ha="center", color=color, alpha=0.94 if focused else 0.68,
                    )


def _draw_geometry_2d(ax, geometry, color: str, dim1: int, dim2: int, focused: bool):
    label_color = _geometry_label_color(color, focused)
    text_alpha = 0.95 if focused else 0.72

    if geometry.type == GeometryType.Point:
        x, y = geometry.v[dim1], geometry.v[dim2]
        if focused:
            ax.scatter(x, y, color=STATE_COLORS["selected"], s=170, alpha=0.18, linewidths=0, zorder=7)
        ax.scatter(
            x, y, color=color, s=76 if focused else 54,
            edgecolors=GCS_THEME["bg_canvas"], linewidths=1.3 if focused else 0.8,
            zorder=8 if focused else 5,
        )
        ax.annotate(
            f"G{geometry.id}", (x, y), xytext=(4, 4), textcoords="offset points",
            fontsize=7, color=label_color, alpha=text_alpha,
        )
        return

    if geometry.type == GeometryType.Line:
        xs = [geometry.v[dim1], geometry.v[dim1 + 3]]
        ys = [geometry.v[dim2], geometry.v[dim2 + 3]]
        if focused:
            ax.plot(xs, ys, color=STATE_COLORS["selected"], linewidth=5.0, alpha=0.20, zorder=6)
        ax.plot(xs, ys, color=color, linewidth=2.5 if focused else 1.8, zorder=7 if focused else 4)
        ax.scatter(
            xs, ys, color=color, s=32 if focused else 20,
            edgecolors=GCS_THEME["bg_canvas"], linewidths=0.9,
            zorder=8 if focused else 5,
        )
        mid = ((xs[0] + xs[1]) / 2, (ys[0] + ys[1]) / 2)
        ax.annotate(
            f"G{geometry.id}", mid, xytext=(4, 4), textcoords="offset points",
            fontsize=7, color=label_color, alpha=text_alpha,
        )
        return

    if geometry.type == GeometryType.Plane:
        x, y = geometry.v[dim1], geometry.v[dim2]
        if focused:
            ax.scatter(x, y, color=STATE_COLORS["selected"], s=210, marker="s", alpha=0.18, linewidths=0, zorder=7)
        ax.scatter(
            x, y, color=color, s=112 if focused else 88, marker="s",
            alpha=0.62 if focused else 0.48,
            edgecolors=STATE_COLORS["selected"] if focused else color,
            linewidths=1.7 if focused else 0.9,
            zorder=8 if focused else 5,
        )
        ax.annotate(
            f"G{geometry.id}", (x, y), xytext=(4, 4), textcoords="offset points",
            fontsize=7, color=label_color, alpha=text_alpha,
        )


def _draw_constraints_2d(graph: GCSGraph, ax, dim1: int, dim2: int, focus: Optional[Mapping]):
    show_default_labels = len(graph.constraints) <= 6
    for constraint in graph.constraints:
        positions = []
        for gid in constraint.geometry_ids:
            geometry = graph.find_geometry(gid)
            if geometry is not None:
                positions.append(_geometry_anchor_2d(geometry, dim1, dim2))

        focused = _is_focused_constraint(constraint, focus)
        state = _constraint_state(constraint, focus)
        color = _constraint_color(constraint, focus)
        linewidth = _constraint_line_width(constraint, focus)
        alpha = _constraint_alpha(constraint, focus)
        linestyle = _constraint_line_style(constraint.type)

        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                p1, p2 = positions[i], positions[j]
                ax.plot(
                    [p1[0], p2[0]], [p1[1], p2[1]],
                    color=color, linewidth=linewidth, linestyle=linestyle,
                    alpha=alpha, zorder=9 if focused else 3,
                )
                if focused or show_default_labels:
                    mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
                    ax.annotate(
                        _constraint_label(constraint, focused, state),
                        mid, xytext=(4, -8), textcoords="offset points",
                        fontsize=6, color=color, alpha=0.92 if focused else 0.64,
                    )


def _collect_scene_points(graph: GCSGraph) -> list[list[float]]:
    points = []
    for geometry in graph.geometries:
        if geometry.type == GeometryType.Point:
            points.append([geometry.v[0], geometry.v[1], geometry.v[2]])
        elif geometry.type == GeometryType.Line:
            points.append([geometry.v[0], geometry.v[1], geometry.v[2]])
            points.append([geometry.v[3], geometry.v[4], geometry.v[5]])
        elif geometry.type == GeometryType.Plane:
            points.append([geometry.v[0], geometry.v[1], geometry.v[2]])
    return points


def _set_3d_bounds(ax, graph: GCSGraph):
    points = _collect_scene_points(graph)
    if points:
        pts = np.array(points)
        center = pts.mean(axis=0)
        max_range = max(pts.max(axis=0) - pts.min(axis=0)) / 2
        if max_range < 0.5:
            max_range = 2.0
        margin = max_range * 1.3
        ax.set_xlim(center[0] - margin, center[0] + margin)
        ax.set_ylim(center[1] - margin, center[1] + margin)
        ax.set_zlim(center[2] - margin, center[2] + margin)
    else:
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_zlim(-2, 2)


def _legend_elements(graph: GCSGraph, focus: Optional[Mapping] = None):
    elements = []
    for i, rigid_set in enumerate(graph.rigid_sets):
        color = RIGID_SET_COLORS[i % len(RIGID_SET_COLORS)]
        elements.append(Patch(facecolor=color, alpha=0.5, label=f"RS {rigid_set.id}"))

    used_constraint_types = sorted({int(constraint.type) for constraint in graph.constraints})
    for constraint_type in used_constraint_types:
        color = CONSTRAINT_COLORS.get(constraint_type, GCS_THEME["constraint_default"])
        elements.append(
            Line2D(
                [0], [0],
                color=color,
                linestyle=_constraint_line_style(constraint_type),
                linewidth=1.8,
                label=CONSTRAINT_NAMES.get(constraint_type, "?"),
            )
        )

    if _has_focus(focus):
        elements.append(
            Line2D(
                [0], [0],
                color=STATE_COLORS["focus"],
                linewidth=2.7,
                label="Focus",
            )
        )
    if _has_constraint_states(focus):
        state_labels = {
            "violated": ("Violated", STATE_COLORS["violated"], 2.3, 0.92),
            "satisfied": ("Satisfied", STATE_COLORS["solved"], 1.4, 0.52),
            "unknown": ("Unknown", STATE_COLORS["pending"], 1.4, 0.62),
        }
        present_states = set(_constraint_states(focus).values())
        for state in ("violated", "satisfied", "unknown"):
            if state not in present_states:
                continue
            label, color, linewidth, alpha = state_labels[state]
            elements.append(
                Line2D(
                    [0], [0],
                    color=color,
                    linewidth=linewidth,
                    alpha=alpha,
                    label=label,
                )
            )
    return elements


def _build_3d_figure(graph: GCSGraph, title: str = "GCS 3D View", focus: Optional[Mapping] = None):
    fig = plt.figure(figsize=(10, 8))
    build_3d_on_figure(graph, fig, title=title, focus=focus)
    plt.tight_layout()
    return fig


def _build_constraint_graph_figure(
    graph: GCSGraph,
    title: str = "Constraint Graph",
    focus: Optional[Mapping] = None,
):
    fig = plt.figure(figsize=(10, 8))
    build_graph_on_figure(graph, fig, title=title, focus=focus)
    plt.tight_layout()
    return fig


def _build_three_view_figure(graph: GCSGraph, title: str = "GCS Three-View", focus: Optional[Mapping] = None):
    fig = plt.figure(figsize=(12, 10))
    build_three_view_on_figure(graph, fig, title=title, focus=focus)
    plt.tight_layout()
    return fig


def build_3d_on_figure(
    graph: GCSGraph,
    fig,
    title: str = "GCS 3D View",
    focus: Optional[Mapping] = None,
):
    fig.clear()
    _apply_figure_theme(fig)
    ax = fig.add_subplot(111, projection="3d")

    for geometry in graph.geometries:
        color = _get_rs_color(graph, geometry.rigid_set_id)
        _draw_geometry_3d(ax, geometry, color, _is_focused_geometry(geometry, focus))

    _draw_constraints_3d(graph, ax, focus)
    _set_3d_bounds(ax, graph)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(title)
    _style_3d_axis(ax)
    _style_legend(ax.legend(handles=_legend_elements(graph, focus), loc="upper left", fontsize=7))

    dof = graph.compute_dof()
    info_text = f"RS:{len(graph.rigid_sets)} G:{len(graph.geometries)} C:{len(graph.constraints)} DOF:{dof}"
    fig.text(0.5, 0.01, info_text, ha="center", fontsize=9, color=GCS_THEME["text_secondary"])

    return ax


def build_graph_on_figure(
    graph: GCSGraph,
    fig,
    title: str = "Constraint Graph",
    focus: Optional[Mapping] = None,
):
    fig.clear()
    _apply_figure_theme(fig)
    ax = fig.add_subplot(111)

    network = nx.Graph()
    for geometry in graph.geometries:
        rs_idx = _get_rs_color_index(graph, geometry.rigid_set_id)
        network.add_node(
            f"G{geometry.id}",
            node_type="geometry",
            geom_id=geometry.id,
            geom_type=int(geometry.type),
            rs_id=geometry.rigid_set_id,
            rs_index=rs_idx,
        )

    for constraint in graph.constraints:
        for i in range(len(constraint.geometry_ids)):
            for j in range(i + 1, len(constraint.geometry_ids)):
                network.add_edge(
                    f"G{constraint.geometry_ids[i]}",
                    f"G{constraint.geometry_ids[j]}",
                    constraint_type=int(constraint.type),
                    constraint_id=constraint.id,
                    value=constraint.value,
                )

    pos = nx.spring_layout(network, seed=42, k=2.0) if network.nodes else {}
    geometry_focus_ids = _focus_ids(focus, "geometry_ids")
    rigid_set_focus_ids = _focus_ids(focus, "rigid_set_ids")

    for geom_type, marker in GEOMETRY_MARKERS.items():
        nodes = [node for node, data in network.nodes(data=True) if data.get("geom_type") == geom_type]
        if not nodes:
            continue

        halo_nodes = [
            node for node in nodes
            if network.nodes[node].get("geom_id") in geometry_focus_ids
            or network.nodes[node].get("rs_id") in rigid_set_focus_ids
        ]
        if halo_nodes:
            nx.draw_networkx_nodes(
                network,
                pos,
                nodelist=halo_nodes,
                ax=ax,
                node_shape=marker,
                node_color=STATE_COLORS["selected"],
                node_size=[GEOMETRY_NODE_SIZES[geom_type] + 430 for _ in halo_nodes],
                alpha=0.20,
                linewidths=0,
            )

        node_colors = [
            RIGID_SET_COLORS[network.nodes[node].get("rs_index", 0) % len(RIGID_SET_COLORS)]
            for node in nodes
        ]
        node_sizes = [
            GEOMETRY_NODE_SIZES[geom_type]
            + (120 if node in halo_nodes else 0)
            for node in nodes
        ]
        node_edges = [
            STATE_COLORS["selected"] if node in halo_nodes else GCS_THEME["bg_canvas"]
            for node in nodes
        ]
        nx.draw_networkx_nodes(
            network,
            pos,
            nodelist=nodes,
            ax=ax,
            node_shape=marker,
            node_color=node_colors,
            node_size=node_sizes,
            edgecolors=node_edges,
            linewidths=1.5,
            alpha=0.92,
        )

    for node, data in network.nodes(data=True):
        fill_color = RIGID_SET_COLORS[data.get("rs_index", 0) % len(RIGID_SET_COLORS)]
        nx.draw_networkx_labels(
            network,
            pos,
            labels={node: node},
            ax=ax,
            font_size=8,
            font_color=_label_color_for_fill(fill_color),
        )

    constraint_focus_ids = _focus_ids(focus, "constraint_ids")
    for u, v, data in network.edges(data=True):
        constraint_id = data.get("constraint_id")
        focused = constraint_id in constraint_focus_ids
        constraint_type = data.get("constraint_type", 3)
        constraint = graph.find_constraint(int(constraint_id)) if constraint_id is not None else None
        if constraint is not None:
            color = _constraint_color(constraint, focus)
            width = _constraint_line_width(constraint, focus)
            alpha = _constraint_alpha(constraint, focus)
        else:
            color = STATE_COLORS["focus"] if focused else CONSTRAINT_COLORS.get(
                constraint_type, GCS_THEME["constraint_default"]
            )
            width = 2.8 if focused else 1.35
            alpha = 0.95 if focused else 0.58
        nx.draw_networkx_edges(
            network,
            pos,
            edgelist=[(u, v)],
            ax=ax,
            edge_color=color,
            style=_constraint_graph_line_style(constraint_type),
            width=width,
            alpha=alpha,
        )

    edge_labels = {}
    for u, v, data in network.edges(data=True):
        constraint_id = data.get("constraint_id", "?")
        constraint_type = data.get("constraint_type", 3)
        focused = constraint_id in constraint_focus_ids
        try:
            constraint = graph.find_constraint(int(constraint_id))
        except (TypeError, ValueError):
            constraint = None
        if constraint is not None:
            label = _constraint_label(constraint, focused, _constraint_state(constraint, focus))
        else:
            label = f"C{constraint_id}"
            if focused:
                label += f" {CONSTRAINT_NAMES.get(constraint_type, '?')}"
        edge_labels[(u, v)] = label
    nx.draw_networkx_edge_labels(
        network,
        pos,
        edge_labels=edge_labels,
        ax=ax,
        font_size=6,
        font_color=GCS_THEME["text_muted"],
    )

    _style_legend(ax.legend(handles=_legend_elements(graph, focus), loc="upper left", fontsize=7))

    dof = graph.compute_dof()
    ax.set_title(f"{title}  |  RS:{len(graph.rigid_sets)} G:{len(graph.geometries)} C:{len(graph.constraints)} DOF:{dof}")
    ax.axis("off")
    _style_2d_axis(ax)

    return ax


def build_three_view_on_figure(
    graph: GCSGraph,
    fig,
    title: str = "GCS Three-View",
    focus: Optional[Mapping] = None,
):
    fig.clear()
    _apply_figure_theme(fig)
    axes = fig.subplots(2, 2)
    views = [
        (axes[0, 0], "XY (Front)", 0, 1),
        (axes[0, 1], "XZ (Top)", 0, 2),
        (axes[1, 0], "YZ (Side)", 1, 2),
    ]
    axes[1, 1].axis("off")

    for ax, view_name, dim1, dim2 in views:
        for geometry in graph.geometries:
            color = _get_rs_color(graph, geometry.rigid_set_id)
            _draw_geometry_2d(ax, geometry, color, dim1, dim2, _is_focused_geometry(geometry, focus))

        _draw_constraints_2d(graph, ax, dim1, dim2, focus)

        ax.set_xlabel(["X", "Y", "Z"][dim1])
        ax.set_ylabel(["X", "Y", "Z"][dim2])
        ax.set_title(view_name)
        ax.set_aspect("equal")
        _style_2d_axis(ax, grid=True)

    dof = graph.compute_dof()
    info = f"RS:{len(graph.rigid_sets)} G:{len(graph.geometries)} C:{len(graph.constraints)} DOF:{dof}"
    axes[1, 1].set_facecolor(GCS_THEME["bg_canvas"])
    axes[1, 1].text(
        0.5,
        0.92 if _has_constraint_states(focus) else 0.5,
        info,
        ha="center",
        va="top" if _has_constraint_states(focus) else "center",
        fontsize=10 if _has_constraint_states(focus) else 14,
        transform=axes[1, 1].transAxes,
        color=GCS_THEME["text_secondary"],
    )
    if _has_constraint_states(focus):
        _style_legend(
            axes[1, 1].legend(
                handles=_legend_elements(graph, focus),
                loc="lower center",
                bbox_to_anchor=(0.5, 0.00),
                fontsize=6,
            )
        )
    axes[1, 1].set_title("Summary")
    axes[1, 1].title.set_color(GCS_THEME["text_primary"])

    fig.suptitle(title)
    fig._suptitle.set_color(GCS_THEME["text_primary"])

    return axes
