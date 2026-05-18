import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

os.environ["GCS_GUI"] = "1"

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from gcs_viz.algebra import (
    GCSGraph, GeometryType, ConstraintType,
    read_graph_file, write_graph_file,
)
from gcs_viz.color_scheme import GEOMETRY_NAMES, CONSTRAINT_NAMES, GCS_THEME
from gcs_viz.event_store import EventStore
from gcs_viz.engine_bridge import EngineBridge
from gcs_viz.visualizer import build_3d_on_figure, build_graph_on_figure, build_three_view_on_figure
from gcs_viz.screens.dialogs_tk import AddRigidSetDialog, AddGeometryDialog, AddConstraintDialog, DeleteConfirmDialog, EditConstraintDialog, HistoryReplayDialog


class GCSPlatformGUI:
    def __init__(self):
        self.graph = GCSGraph()
        self.event_store = EventStore()
        self.engine = EngineBridge()
        self.scene_id = "default"
        self.current_view = "3d"

        self.root = tk.Tk()
        self.root.title("GCS Platform — Geometric Constraint Solver")
        self.root.geometry("1280x800")
        self.root.minsize(960, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        style = ttk.Style()
        style.configure("DOF.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Section.TLabel", font=("Segoe UI", 9, "bold"))
        style.configure("Status.TLabel", font=("Consolas", 9))
        style.configure("Log.TLabel", font=("Consolas", 9))
        style.configure("Action.TButton", padding=4)

        self._build_ui()

    def _on_close(self):
        self.root.destroy()
        sys.exit(0)

    def _build_ui(self):
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        left_frame = ttk.Frame(main_paned, width=300)
        main_paned.add(left_frame, weight=0)

        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        self._build_left_panel(left_frame)
        self._build_right_panel(right_frame)
        self._build_status_bar()

    def _build_left_panel(self, parent):
        canvas = tk.Canvas(parent, width=290, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        pad = {"padx": 6, "pady": 2}

        dof_frame = ttk.LabelFrame(scroll_frame, text="DOF Status")
        dof_frame.pack(fill=tk.X, **pad)
        self.dof_label = ttk.Label(dof_frame, text="  Net DOF: 0 (Empty)  ", style="DOF.TLabel")
        self.dof_label.pack(fill=tk.X, padx=4, pady=4)

        rs_frame = ttk.LabelFrame(scroll_frame, text="Rigid Sets")
        rs_frame.pack(fill=tk.X, **pad)
        self.rs_tree = ttk.Treeview(rs_frame, columns=("id", "geoms"), show="headings", height=3)
        self.rs_tree.heading("id", text="ID")
        self.rs_tree.heading("geoms", text="Geom IDs")
        self.rs_tree.column("id", width=40)
        self.rs_tree.column("geoms", width=200)
        self.rs_tree.pack(fill=tk.X, padx=4, pady=2)
        btn_frame = ttk.Frame(rs_frame)
        btn_frame.pack(fill=tk.X, padx=4, pady=2)
        ttk.Button(btn_frame, text="+ Add RS", style="Action.TButton", command=self._add_rigid_set).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        ttk.Button(btn_frame, text="- Remove", style="Action.TButton", command=self._del_rigid_set).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        geom_frame = ttk.LabelFrame(scroll_frame, text="Geometries")
        geom_frame.pack(fill=tk.X, **pad)
        self.geom_tree = ttk.Treeview(geom_frame, columns=("id", "type", "rs", "pos"), show="headings", height=4)
        self.geom_tree.heading("id", text="ID")
        self.geom_tree.heading("type", text="Type")
        self.geom_tree.heading("rs", text="RS")
        self.geom_tree.heading("pos", text="Position")
        self.geom_tree.column("id", width=30)
        self.geom_tree.column("type", width=50)
        self.geom_tree.column("rs", width=30)
        self.geom_tree.column("pos", width=130)
        self.geom_tree.pack(fill=tk.X, padx=4, pady=2)
        btn_frame2 = ttk.Frame(geom_frame)
        btn_frame2.pack(fill=tk.X, padx=4, pady=2)
        ttk.Button(btn_frame2, text="+ Add Geometry", style="Action.TButton", command=self._add_geometry).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        ttk.Button(btn_frame2, text="- Remove", style="Action.TButton", command=self._del_geometry).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        const_frame = ttk.LabelFrame(scroll_frame, text="Constraints")
        const_frame.pack(fill=tk.X, **pad)
        self.const_tree = ttk.Treeview(const_frame, columns=("id", "type", "geoms", "val"), show="headings", height=3)
        self.const_tree.heading("id", text="ID")
        self.const_tree.heading("type", text="Type")
        self.const_tree.heading("geoms", text="Geoms")
        self.const_tree.heading("val", text="Value")
        self.const_tree.column("id", width=30)
        self.const_tree.column("type", width=80)
        self.const_tree.column("geoms", width=60)
        self.const_tree.column("val", width=60)
        self.const_tree.pack(fill=tk.X, padx=4, pady=2)
        self.const_tree.bind("<Double-1>", self._on_const_double_click)
        btn_frame3 = ttk.Frame(const_frame)
        btn_frame3.pack(fill=tk.X, padx=4, pady=2)
        ttk.Button(btn_frame3, text="+ Add Constraint", style="Action.TButton", command=self._add_constraint).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        ttk.Button(btn_frame3, text="✏ Edit", style="Action.TButton", command=self._edit_constraint).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        ttk.Button(btn_frame3, text="- Remove", style="Action.TButton", command=self._del_constraint).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        action_frame = ttk.LabelFrame(scroll_frame, text="Actions")
        action_frame.pack(fill=tk.X, **pad)

        ttk.Button(action_frame, text="⚡ Solve", style="Action.TButton", command=self._solve).pack(fill=tk.X, padx=4, pady=2)
        ttk.Button(action_frame, text="🎬 Replay History", style="Action.TButton", command=self._replay_history).pack(fill=tk.X, padx=4, pady=2)

        sep = ttk.Separator(action_frame, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, padx=4, pady=4)

        btn_row1 = ttk.Frame(action_frame)
        btn_row1.pack(fill=tk.X, padx=4, pady=1)
        ttk.Button(btn_row1, text="💾 Save", command=self._save).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        ttk.Button(btn_row1, text="📂 Load", command=self._load).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

    def _build_right_panel(self, parent):
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, padx=2, pady=2)

        self.view_var = tk.StringVar(value="3d")
        views = [("3D View", "3d"), ("Graph", "graph"), ("Three-View", "3view")]
        for text, val in views:
            ttk.Radiobutton(toolbar_frame, text=text, variable=self.view_var, value=val, command=self._on_view_change).pack(side=tk.LEFT, padx=4)

        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(toolbar_frame, text="🔄 Refresh", command=self._refresh_canvas).pack(side=tk.LEFT, padx=4)

        self.fig = plt.figure(figsize=(8, 6), dpi=100)
        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=parent)
        self.toolbar = NavigationToolbar2Tk(self.canvas_widget, parent)
        self.toolbar.update()
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self._draw_welcome()

    def _build_status_bar(self):
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=2, pady=2)

        self.status_label = ttk.Label(status_frame, text="  RS:0  G:0  C:0  DOF:0  [Empty]", style="Status.TLabel", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)

        self.log_label = tk.Label(status_frame, text="  Ready", font=("Consolas", 9), anchor=tk.W, bg="#1a1a2e", fg="#a0a0a0", padx=4, pady=2)
        self.log_label.pack(fill=tk.X)

    def _log_info(self, msg):
        self.log_label.config(text=f"  ℹ {msg}", fg="#00bfff")

    def _log_warning(self, msg):
        self.log_label.config(text=f"  ⚠ {msg}", fg="#ffc107")

    def _log_error(self, msg):
        self.log_label.config(text=f"  ✗ {msg}", fg="#ff5252")

    def _log_success(self, msg):
        self.log_label.config(text=f"  ✓ {msg}", fg="#00e676")

    def _draw_welcome(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.axis("off")
        welcome = (
            "GCS Platform — Geometric Constraint Solver\n\n"
            "Quick Start:\n"
            "1. Add Rigid Sets\n"
            "2. Add Geometries (Point / Line / Plane)\n"
            "3. Add Constraints (Distance / Angle / ...)\n"
            "4. Click Solve to compute\n"
            "5. Switch views: 3D / Graph / Three-View\n\n"
            "Data Model:\n"
            "  Point: 3 DOF  |  Line: 6 DOF  |  Plane: 6 DOF\n"
            "  Coincident(-3) | Parallel(-2) | Perpendicular(-1)\n"
            "  Distance(-1) | Angle(-1)\n\n"
            "DOF Status Rule (3D Rigid Body):\n"
            "  1 RS: WellConstrained if DOF=6\n"
            "  N RS: WellConstrained if DOF=6*(N-1)"
        )
        ax.text(0.5, 0.5, welcome, ha="center", va="center", fontsize=11, family="monospace",
                transform=ax.transAxes, color="#333333")
        self.canvas_widget.draw()

    def _refresh_tables(self):
        for item in self.rs_tree.get_children():
            self.rs_tree.delete(item)
        for rs in self.graph.rigid_sets:
            gids = ",".join(str(gid) for gid in rs.geometry_ids) or "—"
            self.rs_tree.insert("", tk.END, values=(rs.id, gids))

        for item in self.geom_tree.get_children():
            self.geom_tree.delete(item)
        for g in self.graph.geometries:
            type_name = GEOMETRY_NAMES.get(g.type, "?")
            if g.type == GeometryType.Point:
                pos = f"({g.v[0]:.3f},{g.v[1]:.3f},{g.v[2]:.3f})"
            elif g.type == GeometryType.Line:
                pos = f"({g.v[0]:.2f}→{g.v[3]:.2f},...)"
            else:
                pos = f"({g.v[0]:.2f},{g.v[1]:.2f},{g.v[2]:.2f})"
            self.geom_tree.insert("", tk.END, values=(g.id, type_name, g.rigid_set_id, pos))

        for item in self.const_tree.get_children():
            self.const_tree.delete(item)
        for c in self.graph.constraints:
            type_name = CONSTRAINT_NAMES.get(c.type, "?")
            gids = ",".join(str(gid) for gid in c.geometry_ids)
            val = f"{c.value:.3f}" if c.value != 0 else "—"
            self.const_tree.insert("", tk.END, values=(c.id, type_name, gids, val))

        self._update_dof()
        self._update_status_info()

    def _update_dof(self):
        dof = self.graph.compute_dof()
        status = self.graph.classify_dof_status()
        if status == "WellConstrained":
            self.dof_label.config(text=f"  Net DOF: {dof} (Well-constrained) ✓  ", foreground="green")
        elif status == "UnderConstrained":
            self.dof_label.config(text=f"  Net DOF: {dof} (Under-constrained) ⚠  ", foreground="#cc8800")
        elif status == "OverConstrained":
            self.dof_label.config(text=f"  Net DOF: {dof} (Over-constrained) ✗  ", foreground="red")
        else:
            self.dof_label.config(text="  Net DOF: — (Empty)  ", foreground="gray")

    def _update_status_info(self):
        n_rs = len(self.graph.rigid_sets)
        n_g = len(self.graph.geometries)
        n_c = len(self.graph.constraints)
        dof = self.graph.compute_dof()
        status = self.graph.classify_dof_status()
        self.status_label.config(text=f"  RS:{n_rs}  G:{n_g}  C:{n_c}  DOF:{dof}  [{status}]")

    def _on_view_change(self):
        self._refresh_canvas()

    def _refresh_canvas(self):
        if not self.graph.geometries:
            self._draw_welcome()
            return

        view = self.view_var.get()
        try:
            if view == "3d":
                build_3d_on_figure(self.graph, self.fig)
            elif view == "graph":
                build_graph_on_figure(self.graph, self.fig)
            elif view == "3view":
                build_three_view_on_figure(self.graph, self.fig)
            self.canvas_widget.draw()
        except Exception as e:
            self._log_error(f"View error: {e}")

    def _add_rigid_set(self):
        dialog = AddRigidSetDialog(self.root, self.graph)
        if dialog.result is not None:
            rs_id = dialog.result
            self.graph.add_rigid_set(rs_id)
            self.graph.history.append({"action": "AddRigidSet", "payload": {"id": rs_id}})
            self.event_store.append(self.scene_id, "RigidSetAdded", {"id": rs_id})
            self._refresh_tables()
            self._log_info(f"Added RS {rs_id}")

    def _del_rigid_set(self):
        if not self.graph.rigid_sets:
            self._log_warning("No rigid sets to remove")
            return
        rs_id = self.graph.rigid_sets[-1].id
        dialog = DeleteConfirmDialog(self.root, f"Rigid Set {rs_id}")
        if dialog.result:
            self.graph.remove_rigid_set(rs_id)
            self.graph.history.append({"action": "RemoveRigidSet", "payload": {"id": rs_id}})
            self.event_store.append(self.scene_id, "RigidSetRemoved", {"id": rs_id})
            self._refresh_tables()
            self._refresh_canvas()
            self._log_info(f"Removed RS {rs_id}")

    def _add_geometry(self):
        if not self.graph.rigid_sets:
            self._log_warning("Add a Rigid Set first!")
            return
        dialog = AddGeometryDialog(self.root, self.graph)
        if dialog.result is not None:
            r = dialog.result
            geom_id = self.graph.next_geometry_id()
            self.graph.add_geometry(r["type"], r["rs_id"], v=r["v"], geom_id=geom_id)
            self.graph.history.append({"action": "AddGeometry", "payload": {"id": geom_id, "type": int(r["type"]), "rigid_set_id": r["rs_id"], "v": r["v"]}})
            self.event_store.append(self.scene_id, "GeometryAdded", {
                "id": geom_id, "type": int(r["type"]), "rigid_set_id": r["rs_id"], "v": r["v"]
            })
            self._refresh_tables()
            self._refresh_canvas()
            self._log_info(f"Added G{geom_id} ({GEOMETRY_NAMES.get(r['type'], '?')}) in RS{r['rs_id']}")

    def _del_geometry(self):
        if not self.graph.geometries:
            self._log_warning("No geometries to remove")
            return
        gid = self.graph.geometries[-1].id
        dialog = DeleteConfirmDialog(self.root, f"Geometry {gid}")
        if dialog.result:
            self.graph.remove_geometry(gid)
            self.graph.history.append({"action": "RemoveGeometry", "payload": {"id": gid}})
            self.event_store.append(self.scene_id, "GeometryRemoved", {"id": gid})
            self._refresh_tables()
            self._refresh_canvas()
            self._log_info(f"Removed G{gid}")

    def _add_constraint(self):
        if len(self.graph.geometries) < 2:
            self._log_warning("Need at least 2 geometries for a constraint")
            return
        dialog = AddConstraintDialog(self.root, self.graph)
        if dialog.result is not None:
            r = dialog.result
            cid = self.graph.next_constraint_id()
            self.graph.add_constraint(r["type"], r["geometry_ids"], value=r["value"], cid=cid)
            self.graph.history.append({"action": "AddConstraint", "payload": {"id": cid, "type": int(r["type"]), "geometry_ids": r["geometry_ids"], "value": r["value"]}})
            self.event_store.append(self.scene_id, "ConstraintAdded", {
                "id": cid, "type": int(r["type"]), "geometry_ids": r["geometry_ids"], "value": r["value"]
            })
            self._refresh_tables()
            self._refresh_canvas()
            self._log_info(f"Added C{cid} ({CONSTRAINT_NAMES.get(r['type'], '?')})")

    def _del_constraint(self):
        if not self.graph.constraints:
            self._log_warning("No constraints to remove")
            return
        cid = self.graph.constraints[-1].id
        dialog = DeleteConfirmDialog(self.root, f"Constraint {cid}")
        if dialog.result:
            self.graph.remove_constraint(cid)
            self.graph.history.append({"action": "RemoveConstraint", "payload": {"id": cid}})
            self.event_store.append(self.scene_id, "ConstraintRemoved", {"id": cid})
            self._refresh_tables()
            self._refresh_canvas()
            self._log_info(f"Removed C{cid}")

    def _edit_constraint(self):
        selected = self.const_tree.selection()
        if not selected:
            if self.graph.constraints:
                self._log_info("Select a constraint first, or double-click to edit")
            else:
                self._log_warning("No constraints to edit")
            return
        item = self.const_tree.item(selected[0])
        cid = int(item["values"][0])
        self._do_edit_constraint(cid)

    def _on_const_double_click(self, event):
        item_id = self.const_tree.identify_row(event.y)
        if not item_id:
            return
        item = self.const_tree.item(item_id)
        cid = int(item["values"][0])
        self._do_edit_constraint(cid)

    def _do_edit_constraint(self, cid: int):
        c = self.graph.find_constraint(cid)
        if c is None:
            self._log_error(f"Constraint {cid} not found")
            return
        dialog = EditConstraintDialog(self.root, self.graph, cid)
        if dialog.result is not None:
            new_value = dialog.result["value"]
            c.value = new_value
            self.graph.history.append({"action": "UpdateConstraint", "payload": {"id": cid, "value": new_value}})
            self.event_store.append(self.scene_id, "ConstraintUpdated", {"id": cid, "value": new_value})
            self._refresh_tables()
            self._log_info(f"Updated C{cid} value={new_value:.3f}, solving...")
            self._solve()

    def _solve(self):
        if not self.graph.geometries:
            self._log_warning("Nothing to solve — add geometries first")
            return

        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scene", "_tui_temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, "solve_input.json")
        write_graph_file(self.graph, temp_path)

        self.graph.history.append({"action": "Solve", "payload": {}})

        if self.engine.is_available():
            self._log_info("Solving...")
            self.root.update_idletasks()

            def run_solve():
                result = self.engine.solve(temp_path)
                self.root.after(0, lambda: self._on_solve_done(result, temp_path))

            threading.Thread(target=run_solve, daemon=True).start()
        else:
            self._log_error(f"GCS.exe not found at {self.engine.exe_path}")

    def _on_solve_done(self, result, temp_path):
        if "error" in result:
            self._log_error(f"Solve error: {result['error']}")
            return

        output = result.get("output", "")
        self.event_store.append(self.scene_id, "SolveCompleted", {"input": temp_path})

        is_well = "Global status: WellConstrained" in output
        is_under = "Global status: UnderConstrained" in output
        is_over = "Global status: OverConstrained" in output
        all_satisfied = ">>> All constraints satisfied <<<" in output
        some_violated = ">>> Some constraints VIOLATED <<<" in output

        graph_file = self._find_output_graph(temp_path)
        if graph_file and os.path.exists(graph_file):
            try:
                solved = read_graph_file(graph_file)
                updated = 0
                for g in solved.geometries:
                    og = self.graph.find_geometry(g.id)
                    if og:
                        og.v = list(g.v)
                        updated += 1
                self._refresh_tables()
                self._refresh_canvas()
            except Exception as e:
                self._refresh_canvas()
                self._log_warning(f"Output graph read error: {e}")
        else:
            self._refresh_canvas()

        constraint_info = self._parse_satisfaction(output)

        if all_satisfied:
            status_text = "Well-constrained ✓" if is_well else ("Under-constrained ⚠" if is_under else "Solved ✓")
            self._log_success(f"Solve completed — {status_text} | All constraints satisfied | {constraint_info}")
        elif some_violated:
            status_text = "Well-constrained" if is_well else ("Under-constrained" if is_under else "Over-constrained")
            self._log_error(f"Solve completed — {status_text} ✗ | Some constraints VIOLATED | {constraint_info}")
        elif is_over:
            self._log_error("Solve completed — Over-constrained ✗ (remove constraints or check conflicts)")
        else:
            self._log_info(f"Solve completed — status unknown")

    def _parse_satisfaction(self, output: str) -> str:
        satisfied = 0
        violated = 0
        for line in output.split("\n"):
            stripped = line.strip()
            if stripped.endswith("SATISFIED"):
                satisfied += 1
            elif stripped.endswith("VIOLATED"):
                violated += 1
        total = satisfied + violated
        if total == 0:
            return ""
        if violated == 0:
            return f"{satisfied}/{total} OK"
        return f"{satisfied} OK, {violated} VIOLATED"

    def _find_output_graph(self, input_path: str) -> str:
        base = os.path.splitext(os.path.basename(input_path))[0]
        input_dir = os.path.dirname(input_path)
        if input_path.endswith(".json"):
            return os.path.join(input_dir, base + "_graph.json")
        return os.path.join(input_dir, base + "_graph.txt")

    def _save(self):
        filepath = filedialog.asksaveasfilename(
            title="Save GCS Model",
            defaultextension=".json",
            filetypes=[("GCS Model (JSON)", "*.json"), ("GCS Graph (TXT)", "*.txt"), ("All Files", "*.*")],
            initialdir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scene", "saved"),
        )
        if filepath:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            write_graph_file(self.graph, filepath)
            self.event_store.append(self.scene_id, "ModelSaved", {"path": filepath})
            self._log_success(f"Saved to {filepath}")

    def _load(self):
        filepath = filedialog.askopenfilename(
            title="Load GCS Model",
            filetypes=[("GCS Model (JSON)", "*.json"), ("GCS Graph (TXT)", "*.txt"), ("All Files", "*.*")],
            initialdir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scene"),
        )
        if filepath:
            try:
                self.graph = read_graph_file(filepath)
                self.event_store.append(self.scene_id, "GraphLoaded", {"path": filepath})
                self._refresh_tables()
                self._refresh_canvas()
                self._log_success(f"Loaded {os.path.basename(filepath)} ({len(self.graph.history)} history steps)")
            except Exception as e:
                self._log_error(f"Load error: {e}")

    def _replay_history(self):
        if not self.graph.history:
            self._log_warning("No history to replay")
            return
        HistoryReplayDialog(self.root, self.graph)

    def run(self):
        self._refresh_tables()
        self.root.mainloop()


def main():
    app = GCSPlatformGUI()
    app.run()


if __name__ == "__main__":
    main()
