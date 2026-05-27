"""Generate an A4 white paper with a single elegant curve."""
import matplotlib.pyplot as plt
import numpy as np

DPI = 300
# A4 in inches: 210×297 mm
W, H = 210 / 25.4, 297 / 25.4  # 8.2677 × 11.6929 in

fig, ax = plt.subplots(figsize=(W, H), dpi=DPI)
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

# White paper
fig.patch.set_facecolor('#FAFAF9')
ax.set_facecolor('#FAFAF9')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
ax.axis('off')

# Elegant cubic Bézier — a single flowing stroke
t = np.linspace(0, 1, 1200)
P0 = [0.10, 0.82]
P1 = [0.30, 0.10]
P2 = [0.68, 0.08]
P3 = [0.90, 0.78]

mt  = 1 - t
bez = np.column_stack([
    mt**3 * P0[0] + 3*mt**2*t * P1[0] + 3*mt*t**2 * P2[0] + t**3 * P3[0],
    mt**3 * P0[1] + 3*mt**2*t * P1[1] + 3*mt*t**2 * P2[1] + t**3 * P3[1],
])

# Tapered width: thicker in the middle
widths = 1.6 + 0.8 * np.sin(t * np.pi)

from matplotlib.collections import LineCollection
points = np.array([bez[:-1, :], bez[1:, :]]).transpose(1, 0, 2)
lc = LineCollection(points, linewidths=widths, colors='#1A1A1A',
                    capstyle='round', joinstyle='round', alpha=0.90)
ax.add_collection(lc)

# Minimal endpoint dots
for pt in (P0, P3):
    ax.scatter(*pt, s=6, c='#1A1A1A', alpha=0.65, zorder=5)

fig.savefig('elegant_curve_a4.png', dpi=DPI, facecolor=fig.get_facecolor(),
            edgecolor='none')
plt.close()
print(f"Saved. Figure: {W*DPI:.0f}×{H*DPI:.0f}px")
