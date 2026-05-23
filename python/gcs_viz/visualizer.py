import os
import numpy as np
import matplotlib
if os.environ.get("GCS_GUI") != "1":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import networkx as nx
from gcs_viz.algebra import GCSGraph, GeometryType, ConstraintType, DOF_GEOMETRY, DOF_REMOVED_CONSTRAINT
from gcs_viz.color_scheme import RIGID_SET_COLORS, CONSTRAINT_COLORS, GEOMETRY_NAMES, CONSTRAINT_NAMES, GCS_THEME


def _get_rs_color(graph: GCSGraph, rs_id: int) -> str:
    for i, rs in enumerate(graph.rigid_sets):
        if rs.id == rs_id:
            return RIGID_SET_COLORS[i % len(RIGID_SET_COLORS)]
    return "#888888"


def _get_rs_color_index(graph: GCSGraph, rs_id: int) -> int:
    for i, rs in enumerate(graph.rigid_sets):
        if rs.id == rs_id:
            return i
    return 0


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


def _build_3d_figure(graph: GCSGraph, title: str = "GCS 3D View"):
    fig = plt.figure(figsize=(10, 8))
    _apply_figure_theme(fig)
    ax = fig.add_subplot(111, projection="3d")

    for g in graph.geometries:
        color = _get_rs_color(graph, g.rigid_set_id)
        if g.type == GeometryType.Point:
            ax.scatter([g.v[0]], [g.v[1]], [g.v[2]], color=color, s=80, depthshade=True, zorder=5)
            ax.text(g.v[0], g.v[1], g.v[2] + 0.08, f"G{g.id}", fontsize=8, ha="center", color=color)
        elif g.type == GeometryType.Line:
            p1 = np.array([g.v[0], g.v[1], g.v[2]])
            p2 = np.array([g.v[3], g.v[4], g.v[5]])
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color=color, linewidth=2, zorder=4)
            mid = (p1 + p2) / 2
            ax.text(mid[0], mid[1], mid[2] + 0.08, f"G{g.id}", fontsize=8, ha="center", color=color)
            for pt in [p1, p2]:
                ax.scatter([pt[0]], [pt[1]], [pt[2]], color=color, s=30, depthshade=True, zorder=5)
        elif g.type == GeometryType.Plane:
            pos = np.array([g.v[0], g.v[1], g.v[2]])
            normal = np.array([g.v[3], g.v[4], g.v[5]])
            norm = np.linalg.norm(normal)
            if norm < 1e-12:
                normal = np.array([0, 0, 1])
            else:
                normal = normal / norm
            if abs(normal[2]) < 0.9:
                u = np.cross(normal, [0, 0, 1])
            else:
                u = np.cross(normal, [1, 0, 0])
            u = u / np.linalg.norm(u)
            v = np.cross(normal, u)
            v = v / np.linalg.norm(v)
            size = 1.0
            corners = [pos + size * (-u - v), pos + size * (u - v), pos + size * (u + v), pos + size * (-u + v)]
            poly = Poly3DCollection([corners], alpha=0.25, facecolor=color, edgecolor=color, linewidth=1)
            ax.add_collection3d(poly)
            ax.text(pos[0], pos[1], pos[2] + 0.15, f"G{g.id}", fontsize=8, ha="center", color=color)

    for c in graph.constraints:
        color = CONSTRAINT_COLORS.get(c.type, GCS_THEME["constraint_default"])
        positions = []
        for gid in c.geometry_ids:
            g = graph.find_geometry(gid)
            if g is None:
                continue
            if g.type == GeometryType.Point:
                positions.append(np.array([g.v[0], g.v[1], g.v[2]]))
            elif g.type == GeometryType.Line:
                positions.append(np.array([(g.v[0] + g.v[3]) / 2, (g.v[1] + g.v[4]) / 2, (g.v[2] + g.v[5]) / 2]))
            elif g.type == GeometryType.Plane:
                positions.append(np.array([g.v[0], g.v[1], g.v[2]]))
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                p1, p2 = positions[i], positions[j]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color=color, linewidth=1.5, linestyle="--", alpha=0.7)
                mid = (p1 + p2) / 2
                label = f"C{c.id}({CONSTRAINT_NAMES.get(c.type, '?')})"
                if c.value != 0.0:
                    label += f"={c.value}"
                ax.text(mid[0], mid[1], mid[2] - 0.1, label, fontsize=6, ha="center", color=color, alpha=0.9)

    all_pts = []
    for g in graph.geometries:
        if g.type == GeometryType.Point:
            all_pts.append([g.v[0], g.v[1], g.v[2]])
        elif g.type == GeometryType.Line:
            all_pts.append([g.v[0], g.v[1], g.v[2]])
            all_pts.append([g.v[3], g.v[4], g.v[5]])
        elif g.type == GeometryType.Plane:
            all_pts.append([g.v[0], g.v[1], g.v[2]])

    if all_pts:
        pts = np.array(all_pts)
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

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(title)
    _style_3d_axis(ax)

    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_elements = []
    for i, rs in enumerate(graph.rigid_sets):
        c = RIGID_SET_COLORS[i % len(RIGID_SET_COLORS)]
        legend_elements.append(Patch(facecolor=c, alpha=0.5, label=f"RS {rs.id}"))
    for ct, c in CONSTRAINT_COLORS.items():
        legend_elements.append(Line2D([0], [0], color=c, linestyle="--", label=CONSTRAINT_NAMES.get(ct, "?")))
    _style_legend(ax.legend(handles=legend_elements, loc="upper left", fontsize=7))

    dof = graph.compute_dof()
    info_text = f"RS:{len(graph.rigid_sets)} G:{len(graph.geometries)} C:{len(graph.constraints)} DOF:{dof}"
    fig.text(0.5, 0.01, info_text, ha="center", fontsize=9, color=GCS_THEME["text_secondary"])

    plt.tight_layout()
    return fig


def _build_constraint_graph_figure(graph: GCSGraph, title: str = "Constraint Graph"):
    G = nx.Graph()
    for g in graph.geometries:
        rs_idx = _get_rs_color_index(graph, g.rigid_set_id)
        G.add_node(f"G{g.id}", node_type="geometry", geom_type=int(g.type), rs_index=rs_idx)
    for c in graph.constraints:
        for i in range(len(c.geometry_ids)):
            for j in range(i + 1, len(c.geometry_ids)):
                G.add_edge(
                    f"G{c.geometry_ids[i]}", f"G{c.geometry_ids[j]}",
                    constraint_type=int(c.type), constraint_id=c.id, value=c.value
                )

    fig, ax = plt.subplots(figsize=(10, 8))
    _apply_figure_theme(fig)
    pos = nx.spring_layout(G, seed=42, k=2.0)

    node_colors = []
    node_sizes = []
    for node, data in G.nodes(data=True):
        rs_idx = data.get("rs_index", 0)
        node_colors.append(RIGID_SET_COLORS[rs_idx % len(RIGID_SET_COLORS)])
        geom_type = data.get("geom_type", 0)
        if geom_type == 0:
            node_sizes.append(300)
        elif geom_type == 1:
            node_sizes.append(400)
        else:
            node_sizes.append(500)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes, alpha=0.85)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color="white")

    edge_colors = []
    edge_styles = []
    for u, v, data in G.edges(data=True):
        ct = data.get("constraint_type", 3)
        edge_colors.append(CONSTRAINT_COLORS.get(ct, GCS_THEME["constraint_default"]))
        edge_styles.append("dashed" if ct in (0, 1, 2) else "solid")

    for (u, v, data), color, style in zip(G.edges(data=True), edge_colors, edge_styles):
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], ax=ax, edge_color=color, style=style, width=1.5, alpha=0.7)

    edge_labels = {}
    for u, v, data in G.edges(data=True):
        ct = data.get("constraint_type", 3)
        cid = data.get("constraint_id", "?")
        val = data.get("value", 0)
        label = f"C{cid}({CONSTRAINT_NAMES.get(ct, '?')})"
        if val != 0:
            label += f"={val}"
        edge_labels[(u, v)] = label
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=6, font_color=GCS_THEME["text_muted"])

    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_elements = []
    for i, rs in enumerate(graph.rigid_sets):
        c = RIGID_SET_COLORS[i % len(RIGID_SET_COLORS)]
        legend_elements.append(Patch(facecolor=c, alpha=0.5, label=f"RS {rs.id}"))
    for ct, c in CONSTRAINT_COLORS.items():
        legend_elements.append(Line2D([0], [0], color=c, linestyle="--", label=CONSTRAINT_NAMES.get(ct, "?")))
    _style_legend(ax.legend(handles=legend_elements, loc="upper left", fontsize=7))

    dof = graph.compute_dof()
    ax.set_title(f"{title}  |  RS:{len(graph.rigid_sets)} G:{len(graph.geometries)} C:{len(graph.constraints)} DOF:{dof}")
    ax.axis("off")
    _style_2d_axis(ax)
    plt.tight_layout()
    return fig


def _build_three_view_figure(graph: GCSGraph, title: str = "GCS Three-View"):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    _apply_figure_theme(fig)
    views = [
        (axes[0, 0], "XY (Front)", 0, 1),
        (axes[0, 1], "XZ (Top)", 0, 2),
        (axes[1, 0], "YZ (Side)", 1, 2),
    ]
    axes[1, 1].axis("off")

    for ax, view_name, dim1, dim2 in views:
        for g in graph.geometries:
            color = _get_rs_color(graph, g.rigid_set_id)
            if g.type == GeometryType.Point:
                ax.scatter(g.v[dim1], g.v[dim2], color=color, s=60, zorder=5)
                ax.annotate(f"G{g.id}", (g.v[dim1], g.v[dim2]), fontsize=7, color=color)
            elif g.type == GeometryType.Line:
                ax.plot([g.v[dim1], g.v[dim1 + 3]], [g.v[dim2], g.v[dim2 + 3]], color=color, linewidth=2)
            elif g.type == GeometryType.Plane:
                ax.scatter(g.v[dim1], g.v[dim2], color=color, s=100, marker="s", alpha=0.5)

        for c in graph.constraints:
            color = CONSTRAINT_COLORS.get(c.type, GCS_THEME["constraint_default"])
            positions = []
            for gid in c.geometry_ids:
                g = graph.find_geometry(gid)
                if g is None:
                    continue
                if g.type == GeometryType.Point:
                    positions.append((g.v[dim1], g.v[dim2]))
                elif g.type == GeometryType.Line:
                    positions.append(((g.v[dim1] + g.v[dim1 + 3]) / 2, (g.v[dim2] + g.v[dim2 + 3]) / 2))
                elif g.type == GeometryType.Plane:
                    positions.append((g.v[dim1], g.v[dim2]))
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    ax.plot([positions[i][0], positions[j][0]], [positions[i][1], positions[j][1]],
                            color=color, linewidth=1, linestyle="--", alpha=0.5)

        ax.set_xlabel(["X", "Y", "Z"][dim1])
        ax.set_ylabel(["X", "Y", "Z"][dim2])
        ax.set_title(view_name)
        ax.set_aspect("equal")
        _style_2d_axis(ax, grid=True)

    dof = graph.compute_dof()
    info = f"RS:{len(graph.rigid_sets)} G:{len(graph.geometries)} C:{len(graph.constraints)} DOF:{dof}"
    axes[1, 1].set_facecolor(GCS_THEME["bg_canvas"])
    axes[1, 1].text(0.5, 0.5, info, ha="center", va="center", fontsize=14,
                    transform=axes[1, 1].transAxes, color=GCS_THEME["text_secondary"])
    axes[1, 1].set_title("Summary")
    axes[1, 1].title.set_color(GCS_THEME["text_primary"])

    fig.suptitle(title)
    fig._suptitle.set_color(GCS_THEME["text_primary"])
    plt.tight_layout()
    return fig


def build_3d_on_figure(graph: GCSGraph, fig, title="GCS 3D View"):
    fig.clear()
    _apply_figure_theme(fig)
    ax = fig.add_subplot(111, projection="3d")

    for g in graph.geometries:
        color = _get_rs_color(graph, g.rigid_set_id)
        if g.type == GeometryType.Point:
            ax.scatter([g.v[0]], [g.v[1]], [g.v[2]], color=color, s=80, depthshade=True, zorder=5)
            ax.text(g.v[0], g.v[1], g.v[2] + 0.08, f"G{g.id}", fontsize=8, ha="center", color=color)
        elif g.type == GeometryType.Line:
            p1 = np.array([g.v[0], g.v[1], g.v[2]])
            p2 = np.array([g.v[3], g.v[4], g.v[5]])
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color=color, linewidth=2, zorder=4)
            mid = (p1 + p2) / 2
            ax.text(mid[0], mid[1], mid[2] + 0.08, f"G{g.id}", fontsize=8, ha="center", color=color)
            for pt in [p1, p2]:
                ax.scatter([pt[0]], [pt[1]], [pt[2]], color=color, s=30, depthshade=True, zorder=5)
        elif g.type == GeometryType.Plane:
            pos = np.array([g.v[0], g.v[1], g.v[2]])
            normal = np.array([g.v[3], g.v[4], g.v[5]])
            norm = np.linalg.norm(normal)
            if norm < 1e-12:
                normal = np.array([0, 0, 1])
            else:
                normal = normal / norm
            if abs(normal[2]) < 0.9:
                u = np.cross(normal, [0, 0, 1])
            else:
                u = np.cross(normal, [1, 0, 0])
            u = u / np.linalg.norm(u)
            v = np.cross(normal, u)
            v = v / np.linalg.norm(v)
            size = 1.0
            corners = [pos + size * (-u - v), pos + size * (u - v), pos + size * (u + v), pos + size * (-u + v)]
            poly = Poly3DCollection([corners], alpha=0.25, facecolor=color, edgecolor=color, linewidth=1)
            ax.add_collection3d(poly)
            ax.text(pos[0], pos[1], pos[2] + 0.15, f"G{g.id}", fontsize=8, ha="center", color=color)

    for c in graph.constraints:
        color = CONSTRAINT_COLORS.get(c.type, GCS_THEME["constraint_default"])
        positions = []
        for gid in c.geometry_ids:
            g = graph.find_geometry(gid)
            if g is None:
                continue
            if g.type == GeometryType.Point:
                positions.append(np.array([g.v[0], g.v[1], g.v[2]]))
            elif g.type == GeometryType.Line:
                positions.append(np.array([(g.v[0] + g.v[3]) / 2, (g.v[1] + g.v[4]) / 2, (g.v[2] + g.v[5]) / 2]))
            elif g.type == GeometryType.Plane:
                positions.append(np.array([g.v[0], g.v[1], g.v[2]]))
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                p1, p2 = positions[i], positions[j]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color=color, linewidth=1.5, linestyle="--", alpha=0.7)
                mid = (p1 + p2) / 2
                label = f"C{c.id}({CONSTRAINT_NAMES.get(c.type, '?')})"
                if c.value != 0.0:
                    label += f"={c.value}"
                ax.text(mid[0], mid[1], mid[2] - 0.1, label, fontsize=6, ha="center", color=color, alpha=0.9)

    all_pts = []
    for g in graph.geometries:
        if g.type == GeometryType.Point:
            all_pts.append([g.v[0], g.v[1], g.v[2]])
        elif g.type == GeometryType.Line:
            all_pts.append([g.v[0], g.v[1], g.v[2]])
            all_pts.append([g.v[3], g.v[4], g.v[5]])
        elif g.type == GeometryType.Plane:
            all_pts.append([g.v[0], g.v[1], g.v[2]])

    if all_pts:
        pts = np.array(all_pts)
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

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(title)
    _style_3d_axis(ax)

    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_elements = []
    for i, rs in enumerate(graph.rigid_sets):
        c = RIGID_SET_COLORS[i % len(RIGID_SET_COLORS)]
        legend_elements.append(Patch(facecolor=c, alpha=0.5, label=f"RS {rs.id}"))
    for ct, c in CONSTRAINT_COLORS.items():
        legend_elements.append(Line2D([0], [0], color=c, linestyle="--", label=CONSTRAINT_NAMES.get(ct, "?")))
    _style_legend(ax.legend(handles=legend_elements, loc="upper left", fontsize=7))

    dof = graph.compute_dof()
    info_text = f"RS:{len(graph.rigid_sets)} G:{len(graph.geometries)} C:{len(graph.constraints)} DOF:{dof}"
    fig.text(0.5, 0.01, info_text, ha="center", fontsize=9, color=GCS_THEME["text_secondary"])

    return ax


def build_graph_on_figure(graph: GCSGraph, fig, title="Constraint Graph"):
    fig.clear()
    _apply_figure_theme(fig)
    ax = fig.add_subplot(111)

    G = nx.Graph()
    for g in graph.geometries:
        rs_idx = _get_rs_color_index(graph, g.rigid_set_id)
        G.add_node(f"G{g.id}", node_type="geometry", geom_type=int(g.type), rs_index=rs_idx)
    for c in graph.constraints:
        for i in range(len(c.geometry_ids)):
            for j in range(i + 1, len(c.geometry_ids)):
                G.add_edge(
                    f"G{c.geometry_ids[i]}", f"G{c.geometry_ids[j]}",
                    constraint_type=int(c.type), constraint_id=c.id, value=c.value
                )

    pos = nx.spring_layout(G, seed=42, k=2.0)

    node_colors = []
    node_sizes = []
    for node, data in G.nodes(data=True):
        rs_idx = data.get("rs_index", 0)
        node_colors.append(RIGID_SET_COLORS[rs_idx % len(RIGID_SET_COLORS)])
        geom_type = data.get("geom_type", 0)
        if geom_type == 0:
            node_sizes.append(300)
        elif geom_type == 1:
            node_sizes.append(400)
        else:
            node_sizes.append(500)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes, alpha=0.85)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color="white")

    edge_colors = []
    edge_styles = []
    for u, v, data in G.edges(data=True):
        ct = data.get("constraint_type", 3)
        edge_colors.append(CONSTRAINT_COLORS.get(ct, GCS_THEME["constraint_default"]))
        edge_styles.append("dashed" if ct in (0, 1, 2) else "solid")

    for (u, v, data), color, style in zip(G.edges(data=True), edge_colors, edge_styles):
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], ax=ax, edge_color=color, style=style, width=1.5, alpha=0.7)

    edge_labels = {}
    for u, v, data in G.edges(data=True):
        ct = data.get("constraint_type", 3)
        cid = data.get("constraint_id", "?")
        val = data.get("value", 0)
        label = f"C{cid}({CONSTRAINT_NAMES.get(ct, '?')})"
        if val != 0:
            label += f"={val}"
        edge_labels[(u, v)] = label
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=6, font_color=GCS_THEME["text_muted"])

    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_elements = []
    for i, rs in enumerate(graph.rigid_sets):
        c = RIGID_SET_COLORS[i % len(RIGID_SET_COLORS)]
        legend_elements.append(Patch(facecolor=c, alpha=0.5, label=f"RS {rs.id}"))
    for ct, c in CONSTRAINT_COLORS.items():
        legend_elements.append(Line2D([0], [0], color=c, linestyle="--", label=CONSTRAINT_NAMES.get(ct, "?")))
    _style_legend(ax.legend(handles=legend_elements, loc="upper left", fontsize=7))

    dof = graph.compute_dof()
    ax.set_title(f"{title}  |  RS:{len(graph.rigid_sets)} G:{len(graph.geometries)} C:{len(graph.constraints)} DOF:{dof}")
    ax.axis("off")
    _style_2d_axis(ax)

    return ax


def build_three_view_on_figure(graph: GCSGraph, fig, title="GCS Three-View"):
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
        for g in graph.geometries:
            color = _get_rs_color(graph, g.rigid_set_id)
            if g.type == GeometryType.Point:
                ax.scatter(g.v[dim1], g.v[dim2], color=color, s=60, zorder=5)
                ax.annotate(f"G{g.id}", (g.v[dim1], g.v[dim2]), fontsize=7, color=color)
            elif g.type == GeometryType.Line:
                ax.plot([g.v[dim1], g.v[dim1 + 3]], [g.v[dim2], g.v[dim2 + 3]], color=color, linewidth=2)
            elif g.type == GeometryType.Plane:
                ax.scatter(g.v[dim1], g.v[dim2], color=color, s=100, marker="s", alpha=0.5)

        for c in graph.constraints:
            color = CONSTRAINT_COLORS.get(c.type, GCS_THEME["constraint_default"])
            positions = []
            for gid in c.geometry_ids:
                g = graph.find_geometry(gid)
                if g is None:
                    continue
                if g.type == GeometryType.Point:
                    positions.append((g.v[dim1], g.v[dim2]))
                elif g.type == GeometryType.Line:
                    positions.append(((g.v[dim1] + g.v[dim1 + 3]) / 2, (g.v[dim2] + g.v[dim2 + 3]) / 2))
                elif g.type == GeometryType.Plane:
                    positions.append((g.v[dim1], g.v[dim2]))
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    ax.plot([positions[i][0], positions[j][0]], [positions[i][1], positions[j][1]],
                            color=color, linewidth=1, linestyle="--", alpha=0.5)

        ax.set_xlabel(["X", "Y", "Z"][dim1])
        ax.set_ylabel(["X", "Y", "Z"][dim2])
        ax.set_title(view_name)
        ax.set_aspect("equal")
        _style_2d_axis(ax, grid=True)

    dof = graph.compute_dof()
    info = f"RS:{len(graph.rigid_sets)} G:{len(graph.geometries)} C:{len(graph.constraints)} DOF:{dof}"
    axes[1, 1].set_facecolor(GCS_THEME["bg_canvas"])
    axes[1, 1].text(0.5, 0.5, info, ha="center", va="center", fontsize=14,
                    transform=axes[1, 1].transAxes, color=GCS_THEME["text_secondary"])
    axes[1, 1].set_title("Summary")
    axes[1, 1].title.set_color(GCS_THEME["text_primary"])

    fig.suptitle(title)
    fig._suptitle.set_color(GCS_THEME["text_primary"])

    return axes
