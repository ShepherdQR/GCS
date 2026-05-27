"""Capture a full-window GCS viewer screenshot at standard resolution.

Launches the GCSPlatformGUI, loads a scene, configures window geometry,
and captures the full window (canvas + panels + status bar + toolbar).

Usage:
  python tools/ui_qa/capture_full_window.py
  python tools/ui_qa/capture_full_window.py --scene fixtures/scene/saved/triangle_003.json
  python tools/ui_qa/capture_full_window.py --width 1600 --height 900
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_DIR = REPO_ROOT / "python"
sys.path.insert(0, str(PYTHON_DIR))

DEFAULT_SCENE = "fixtures/scene/saved/triangle_003.json"
DEFAULT_OUTPUT = (
    REPO_ROOT / "docs" / "architecture" / "70-visualization" / "assets"
    / "ve003-full-window-viewer-20260528.png"
)
DEFAULT_WIDTH = 1600
DEFAULT_HEIGHT = 900


def capture_full_window(
    scene_path: str,
    output_path: Path,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> None:
    import platform
    import time

    from gcs_viz import algebra
    from gcs_viz.platform_gui import GCSPlatformGUI

    print(f"Loading scene: {scene_path}")
    graph = algebra.read_graph_file(str(REPO_ROOT / scene_path))

    print("Creating GUI...")
    app = GCSPlatformGUI()
    app.root.title(f"GCS — Aesthetic Capture — {Path(scene_path).name}")

    # Set window geometry
    x = 40
    y = 40
    app.root.geometry(f"{width}x{height}+{x}+{y}")
    app.root.update_idletasks()

    # Load the scene
    app.graph = graph
    app._cancel_history_replay()
    app._clear_constraint_states()
    app._selection_focus = None
    app._set_current_model(str(REPO_ROOT / scene_path))
    app._refresh_tables()
    app.view_var.set("3d")
    app._set_solve_summary("idle", "Aesthetic review capture — no solve run")
    app._set_replay_state("Replay ready", "Step 0 / 0", "No active replay", 0.0)
    app._draw_graph_on_canvas(app.graph, "3d")

    # Let Tkinter settle
    for _ in range(8):
        app.root.update_idletasks()
        app.root.update()
        time.sleep(0.15)

    # Full window capture using Tkinter + PIL
    try:
        from PIL import ImageGrab
        x0 = app.root.winfo_rootx()
        y0 = app.root.winfo_rooty()
        x1 = x0 + app.root.winfo_width()
        y1 = y0 + app.root.winfo_height()
        print(f"Capturing window region: ({x0}, {y0}) → ({x1}, {y1})")
        img = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG")
        print(f"Saved: {output_path}")
        print(f"  Size: {img.size[0]}×{img.size[1]}px")
    except ImportError:
        # Fallback: canvas-only capture
        print("ImageGrab not available, falling back to canvas capture")
        app.fig.savefig(str(output_path), dpi=120,
                        facecolor=app.fig.get_facecolor())
        print(f"Saved (canvas only): {output_path}")

    app.root.destroy()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture full-window GCS viewer screenshot"
    )
    parser.add_argument(
        "--scene", default=DEFAULT_SCENE,
        help=f"Scene file path relative to repo root (default: {DEFAULT_SCENE})"
    )
    parser.add_argument(
        "--output", default=str(DEFAULT_OUTPUT),
        help=f"Output PNG path (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    args = parser.parse_args()

    capture_full_window(
        scene_path=args.scene,
        output_path=Path(args.output),
        width=args.width,
        height=args.height,
    )


if __name__ == "__main__":
    main()
