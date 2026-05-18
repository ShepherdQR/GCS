import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from model.graph import (
    GeometryType,
    ConstraintType,
    Manager,
    type_name_geometry,
    type_name_constraint,
)

RIGID_SET_COLORS = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990",
    "#dcbeff", "#9A6324", "#fffac8", "#800000", "#aaffc3",
]

CONSTRAINT_COLORS = {
    ConstraintType.Coincident: "#ff0000",
    ConstraintType.Parallel: "#00ff00",
    ConstraintType.Perpendicular: "#0000ff",
    ConstraintType.Distance: "#ffaa00",
    ConstraintType.Angle: "#ff00ff",
}


def _get_rigid_set_color(manager: Manager, rs_id: int) -> str:
    for i, rs in enumerate(manager.rigid_sets):
        if rs.id == rs_id:
            return RIGID_SET_COLORS[i % len(RIGID_SET_COLORS)]
    return "#888888"


def _draw_point(ax, g, color, label_prefix=""):
    x, y, z = g.v[0], g.v[1], g.v[2]
    ax.scatter([x], [y], [z], color=color, s=80, depthshade=True, zorder=5)
    ax.text(x, y, z + 0.08, f"{label_prefix}{g.id}", fontsize=8, ha="center", color=color)


def _draw_line(ax, g, color, label_prefix=""):
    p1 = np.array([g.v[0], g.v[1], g.v[2]])
    p2 = np.array([g.v[3], g.v[4], g.v[5]])
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
            color=color, linewidth=2, zorder=4)
    mid = (p1 + p2) / 2
    ax.text(mid[0], mid[1], mid[2] + 0.08, f"{label_prefix}{g.id}",
            fontsize=8, ha="center", color=color)
    for pt in [p1, p2]:
        ax.scatter([pt[0]], [pt[1]], [pt[2]], color=color, s=30, depthshade=True, zorder=5)


def _draw_plane(ax, g, color, label_prefix=""):
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
    corners = [
        pos + size * (-u - v),
        pos + size * (u - v),
        pos + size * (u + v),
        pos + size * (-u + v),
    ]

    verts = [corners]
    poly = Poly3DCollection(verts, alpha=0.25, facecolor=color, edgecolor=color, linewidth=1)
    ax.add_collection3d(poly)
    ax.text(pos[0], pos[1], pos[2] + 0.15, f"{label_prefix}{g.id}",
            fontsize=8, ha="center", color=color)


def _draw_constraint(ax, manager: Manager, c):
    color = CONSTRAINT_COLORS.get(c.type, "#ffffff")
    positions = []
    for gid in c.geometry_ids:
        g = manager.find_geometry(gid)
        if g is None:
            continue
        if g.type == GeometryType.Point:
            positions.append(np.array([g.v[0], g.v[1], g.v[2]]))
        elif g.type == GeometryType.Line:
            mid = np.array([(g.v[0] + g.v[3]) / 2, (g.v[1] + g.v[4]) / 2, (g.v[2] + g.v[5]) / 2])
            positions.append(mid)
        elif g.type == GeometryType.Plane:
            positions.append(np.array([g.v[0], g.v[1], g.v[2]]))

    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            p1, p2 = positions[i], positions[j]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                    color=color, linewidth=1.5, linestyle="--", alpha=0.7)
            mid = (p1 + p2) / 2
            label = f"C{c.id}({type_name_constraint(c.type)})"
            if c.value != 0.0:
                label += f"={c.value}"
            ax.text(mid[0], mid[1], mid[2] - 0.1, label,
                    fontsize=6, ha="center", color=color, alpha=0.9)


def view_graph(manager: Manager, title: str = "GCS Graph Viewer", block: bool = True):
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")

    for g in manager.geometries:
        color = _get_rigid_set_color(manager, g.rigid_set_id)
        if g.type == GeometryType.Point:
            _draw_point(ax, g, color)
        elif g.type == GeometryType.Line:
            _draw_line(ax, g, color)
        elif g.type == GeometryType.Plane:
            _draw_plane(ax, g, color)

    for c in manager.constraints:
        _draw_constraint(ax, manager, c)

    all_pts = []
    for g in manager.geometries:
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

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(title)

    legend_elements = []
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    for i, rs in enumerate(manager.rigid_sets):
        c = RIGID_SET_COLORS[i % len(RIGID_SET_COLORS)]
        legend_elements.append(Patch(facecolor=c, alpha=0.5, label=f"RS {rs.id}"))
    for ct, c in CONSTRAINT_COLORS.items():
        legend_elements.append(Line2D([0], [0], color=c, linestyle="--",
                                       label=type_name_constraint(ct)))

    ax.legend(handles=legend_elements, loc="upper left", fontsize=7)

    info_text = (
        f"RigidSets: {len(manager.rigid_sets)}  "
        f"Geometries: {len(manager.geometries)}  "
        f"Constraints: {len(manager.constraints)}"
    )
    fig.text(0.5, 0.01, info_text, ha="center", fontsize=9, color="gray")

    plt.tight_layout()
    plt.show(block=block)
