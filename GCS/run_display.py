import sys
import os
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.graph import type_name_geometry, type_name_constraint
from display.parser import read_graph, dump_graph, print_summary
from display.viewer import view_graph
from display.server import start_server


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_display.py <graph_file> [--viewer|--server|--summary]")
        print("       python run_display.py <scene_subdir> --scene")
        print("  --viewer   : Open matplotlib 3D viewer (default)")
        print("  --server   : Start web server for Three.js viewer")
        print("  --summary  : Print graph summary only")
        print("  --scene    : Treat <scene_subdir> as scene/<subdir>, display each txt in a separate figure")
        print()
        print("Example: python run_display.py g1.txt --viewer")
        print("         python run_display.py bcc --scene")
        sys.exit(1)

    path = sys.argv[1]
    mode = "--viewer"
    if len(sys.argv) > 2:
        mode = sys.argv[2]

    if mode == "--scene":
        scene_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scene", path)
        if not os.path.isdir(scene_dir):
            print(f"Error: Scene directory not found: {scene_dir}")
            sys.exit(1)

        txt_files = sorted(glob.glob(os.path.join(scene_dir, "*_graph.txt")))
        if not txt_files:
            txt_files = sorted(glob.glob(os.path.join(scene_dir, "*.txt")))
        if not txt_files:
            print(f"Error: No .txt files found in {scene_dir}")
            sys.exit(1)

        print(f"Scene: {path} ({len(txt_files)} graph file(s))")
        for i, txt_path in enumerate(txt_files):
            manager = read_graph(txt_path)
            print(f"\n--- [{i+1}/{len(txt_files)}] {os.path.basename(txt_path)} ---")
            print_summary(manager)
            is_last = (i == len(txt_files) - 1)
            view_graph(manager, title=f"GCS Graph - {os.path.basename(txt_path)}", block=is_last)
    else:
        if not os.path.exists(path):
            print(f"Error: File not found: {path}")
            sys.exit(1)

        manager = read_graph(path)
        print(f"GCS Graph loaded from: {path}")
        print_summary(manager)

        if mode == "--summary":
            pass
        elif mode == "--viewer":
            print("\nOpening matplotlib 3D viewer...")
            view_graph(manager, title=f"GCS Graph - {os.path.basename(path)}")
        elif mode == "--server":
            out_path = dump_graph(manager, path)
            print(f"Dumped graph to: {out_path}")
            web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "display", "web")
            if out_path:
                import shutil
                dest = os.path.join(web_dir, os.path.basename(out_path))
                shutil.copy2(out_path, dest)
                print(f"Copied graph file to: {dest}")
            print("\nStarting web server...")
            start_server(directory=web_dir, port=8000)
        else:
            print(f"Unknown mode: {mode}")
            print("Use --viewer, --server, --scene, or --summary")


if __name__ == "__main__":
    main()
