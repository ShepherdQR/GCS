"""Bridge taste seed: minimal constraint graph on A4 paper using GCS palette.

Translates the GCS "Quiet Technical Atelier" color tokens into a second
calibration image. Where the first taste seed ("A Single Curve") answers
"what does our taste look like on a blank page?", this one answers "what
does our taste look like with solver evidence on the page?"

Scene: 3 rigid sets (nodes) + 2 constraints (edges) — the smallest graph
that still carries constraint semantics.
"""

import matplotlib.pyplot as plt
import numpy as np

# A4 in inches at 300 DPI
W, H = 210 / 25.4, 297 / 25.4

# ── GCS palette tokens (from python/gcs_viz/color_scheme.py) ──
PAPER = "#F7F4EC"
TEXT_PRIMARY = "#181715"
TEXT_MUTED = "#8B867A"
RS_A = "#587C7A"       # rigidSet.palette.01 — teal
RS_B = "#B88746"       # rigidSet.palette.02 — ochre
RS_C = "#C66E4E"       # rigidSet.palette.05 — rust
DISTANCE_COLOR = "#B88746"     # constraint.type.distance.color
COINCIDENT_COLOR = "#B8574E"   # constraint.type.coincident.color
RULE_SOFT = "#ECE7DD"          # rule.soft — subtle grid/guide lines

fig, ax = plt.subplots(figsize=(W, H), dpi=300)
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

fig.patch.set_facecolor(PAPER)
ax.set_facecolor(PAPER)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
ax.axis('off')

# ── Node positions (asymmetric triangle) ──
nodes = {
    "A": np.array([0.20, 0.62]),
    "B": np.array([0.55, 0.78]),
    "C": np.array([0.38, 0.30]),
}

node_colors = {"A": RS_A, "B": RS_B, "C": RS_C}
node_labels = {"A": "RS 1", "B": "RS 2", "C": "RS 3"}

# ── Constraint edges ──
# A–B: distance constraint (solid)
# B–C: coincident constraint (dotted)
# A–C: distance constraint (solid)
edges = [
    ("A", "B", DISTANCE_COLOR, "solid", 1.8),
    ("B", "C", COINCIDENT_COLOR, "dotted", 1.6),
    ("A", "C", DISTANCE_COLOR, "solid", 1.8),
]

# ── Draw edges ──
for a, b, color, style, lw in edges:
    pa, pb = nodes[a], nodes[b]
    ax.plot([pa[0], pb[0]], [pa[1], pb[1]],
            color=color, linestyle=style, linewidth=lw,
            alpha=0.75, solid_capstyle='round', zorder=2)

# ── Draw nodes ──
node_radius = 0.028
for name, pos in nodes.items():
    circle = plt.Circle(pos, node_radius, facecolor=node_colors[name],
                        edgecolor='none', alpha=0.88, zorder=3)
    ax.add_patch(circle)

# ── Node labels ──
for name, pos in nodes.items():
    label = node_labels[name]
    # Offset label above the node
    offset = np.array([0, node_radius + 0.022])
    ax.text(pos[0] + offset[0], pos[1] + offset[1], label,
            fontsize=7, color=TEXT_MUTED, ha='center', va='bottom',
            fontfamily='sans-serif', alpha=0.80)

# ── Subtle constraint-type legend (bottom-right margin) ──
lx, ly = 0.62, 0.16
ax.plot([lx, lx + 0.06], [ly, ly], color=DISTANCE_COLOR, linestyle='solid',
        linewidth=1.6, alpha=0.75, solid_capstyle='round')
ax.text(lx + 0.08, ly, "distance", fontsize=5.5, color=TEXT_MUTED,
        va='center', fontfamily='sans-serif', alpha=0.75)

ax.plot([lx, lx + 0.06], [ly - 0.04, ly - 0.04], color=COINCIDENT_COLOR,
        linestyle='dotted', linewidth=1.6, alpha=0.75, solid_capstyle='round')
ax.text(lx + 0.08, ly - 0.04, "coincident", fontsize=5.5, color=TEXT_MUTED,
        va='center', fontfamily='sans-serif', alpha=0.75)

# ── Minimal title (bottom-left, very subdued) ──
ax.text(0.12, 0.08, "Rigid Sets 3 · Constraints 2 · DOF 1",
        fontsize=6, color=TEXT_MUTED, fontfamily='sans-serif', alpha=0.55)

out = "docs/research/20260527/aesthetic-taste/bridge_constraint_graph.png"
fig.savefig(out, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print(f"Saved: {out}")
