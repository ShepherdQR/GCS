import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_DIR = os.path.normpath(os.path.join(PACKAGE_DIR, ".."))
REPO_ROOT = os.path.normpath(os.path.join(PYTHON_DIR, ".."))
FIXTURE_SCENE_DIR = os.path.join(REPO_ROOT, "fixtures", "scene")

sys.path.insert(0, PYTHON_DIR)

os.environ["GCS_GUI"] = "1"

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from gcs_viz.algebra import (
    GCSGraph, GeometryType, ConstraintType,
    read_graph_file, write_graph_file,
)
from gcs_viz.color_scheme import GEOMETRY_NAMES, CONSTRAINT_NAMES, GCS_THEME, STATE_COLORS
from gcs_viz.event_store import EventStore
from gcs_viz.engine_bridge import EngineBridge
from gcs_viz.viewer_bridge import build_history_graph, graph_summary, render_graph_view, render_message
from gcs_viz.screens.dialogs_tk import AddRigidSetDialog, AddGeometryDialog, AddConstraintDialog, DeleteConfirmDialog, EditConstraintDialog


class GCSPlatformGUI:
    def __init__(self):
        self.graph = GCSGraph()
        self.event_store = EventStore()
        self.engine = EngineBridge()
        self.scene_id = "default"
        self.current_view = "3d"
        self.current_model_name = "Untitled"
        self._history_replay_job = None
        self._history_replay_history = []
        self._history_replay_index = -1
        self._history_replay_view = None

        self.root = tk.Tk()
        self.root.title("GCS Platform — Geometric Constraint Solver")
        self.root.geometry("1280x800")
        self.root.minsize(960, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.replay_speed_var = tk.DoubleVar(value=1.0)
        self.replay_speed_label_var = tk.StringVar(value="Replay Speed: 1.00x")
        self.model_name_var = tk.StringVar(value="Model: Untitled")
        self.summary_model_var = tk.StringVar(value="Untitled")
        self.summary_counts_var = tk.StringVar(value="RS 0   G 0   C 0")
        self.summary_dof_var = tk.StringVar(value="Net DOF: 0")
        self.summary_status_var = tk.StringVar(value="Status: Empty")
        self.replay_state_var = tk.StringVar(value="Replay ready")
        self.replay_step_var = tk.StringVar(value="Step 0 / 0")
        self.replay_action_var = tk.StringVar(value="No active replay")
        self.replay_progress_var = tk.DoubleVar(value=0.0)
        self.solve_summary_var = tk.StringVar(value="Solve idle")
        self.solve_state_var = tk.StringVar(value="idle")
        self._last_solve_report = None

        style = ttk.Style()
        self._configure_theme(style)

        self._build_ui()

    def _on_close(self):
        self._cancel_history_replay()
        self.root.destroy()
        sys.exit(0)

    def _build_ui(self):
        self.root.configure(bg=GCS_THEME["bg_window"])
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        left_frame = ttk.Frame(main_paned, width=320)
        main_paned.add(left_frame, weight=0)

        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        self._build_inspector_panel(left_frame)
        self._build_right_panel(right_frame)
        self._build_status_bar()

    def _build_inspector_panel(self, parent):
        parent.configure(width=320)
        parent.pack_propagate(False)

        shell = ttk.Frame(parent)
        shell.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        summary_frame = ttk.LabelFrame(shell, text="Model Summary")
        summary_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(summary_frame, textvariable=self.summary_model_var, style="SummaryName.TLabel").pack(
            fill=tk.X, padx=8, pady=(6, 2)
        )
        ttk.Label(summary_frame, textvariable=self.summary_counts_var, style="SummaryValue.TLabel").pack(
            fill=tk.X, padx=8, pady=1
        )
        self.dof_label = ttk.Label(summary_frame, textvariable=self.summary_dof_var, style="DOF.TLabel")
        self.dof_label.pack(fill=tk.X, padx=8, pady=1)
        ttk.Label(summary_frame, textvariable=self.summary_status_var, style="SummaryValue.TLabel").pack(
            fill=tk.X, padx=8, pady=(1, 6)
        )

        browser_frame = ttk.LabelFrame(shell, text="Object Browser")
        browser_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        self.object_notebook = ttk.Notebook(browser_frame)
        self.object_notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        rs_frame = ttk.Frame(self.object_notebook)
        self.object_notebook.add(rs_frame, text="Rigid Sets")
        self.rs_tree = ttk.Treeview(rs_frame, columns=("id", "geoms"), show="headings", height=8)
        self.rs_tree.heading("id", text="ID")
        self.rs_tree.heading("geoms", text="Geom IDs")
        self.rs_tree.column("id", width=42, stretch=False)
        self.rs_tree.column("geoms", width=210)
        self.rs_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))
        rs_tools = ttk.Frame(rs_frame)
        rs_tools.pack(fill=tk.X, padx=4, pady=(0, 4))
        ttk.Button(rs_tools, text="Add RS", style="Action.TButton", command=self._add_rigid_set).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        ttk.Button(rs_tools, text="Remove", style="Action.TButton", command=self._del_rigid_set).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        geom_frame = ttk.Frame(self.object_notebook)
        self.object_notebook.add(geom_frame, text="Geometries")
        self.geom_tree = ttk.Treeview(geom_frame, columns=("id", "type", "rs", "pos"), show="headings", height=8)
        self.geom_tree.heading("id", text="ID")
        self.geom_tree.heading("type", text="Type")
        self.geom_tree.heading("rs", text="RS")
        self.geom_tree.heading("pos", text="Position")
        self.geom_tree.column("id", width=34, stretch=False)
        self.geom_tree.column("type", width=58, stretch=False)
        self.geom_tree.column("rs", width=34, stretch=False)
        self.geom_tree.column("pos", width=150)
        self.geom_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))
        geom_tools = ttk.Frame(geom_frame)
        geom_tools.pack(fill=tk.X, padx=4, pady=(0, 4))
        ttk.Button(geom_tools, text="Add Geometry", style="Action.TButton", command=self._add_geometry).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        ttk.Button(geom_tools, text="Remove", style="Action.TButton", command=self._del_geometry).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        const_frame = ttk.Frame(self.object_notebook)
        self.object_notebook.add(const_frame, text="Constraints")
        self.const_tree = ttk.Treeview(const_frame, columns=("id", "type", "geoms", "val"), show="headings", height=8)
        self.const_tree.heading("id", text="ID")
        self.const_tree.heading("type", text="Type")
        self.const_tree.heading("geoms", text="Geoms")
        self.const_tree.heading("val", text="Value")
        self.const_tree.column("id", width=34, stretch=False)
        self.const_tree.column("type", width=86)
        self.const_tree.column("geoms", width=62, stretch=False)
        self.const_tree.column("val", width=62, stretch=False)
        self.const_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))
        self.const_tree.bind("<Double-1>", self._on_const_double_click)
        const_tools = ttk.Frame(const_frame)
        const_tools.pack(fill=tk.X, padx=4, pady=(0, 4))
        ttk.Button(const_tools, text="Add Constraint", style="Action.TButton", command=self._add_constraint).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        ttk.Button(const_tools, text="Edit", style="Action.TButton", command=self._edit_constraint).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        ttk.Button(const_tools, text="Remove", style="Action.TButton", command=self._del_constraint).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        command_frame = ttk.LabelFrame(shell, text="Commands")
        command_frame.pack(fill=tk.X)
        ttk.Button(command_frame, text="Solve", style="Primary.TButton", command=self._solve).pack(fill=tk.X, padx=4, pady=(6, 2))
        ttk.Button(command_frame, text="Replay History", style="Action.TButton", command=self._replay_history).pack(fill=tk.X, padx=4, pady=2)

        speed_frame = ttk.Frame(command_frame)
        speed_frame.pack(fill=tk.X, padx=4, pady=(2, 4))
        ttk.Label(speed_frame, textvariable=self.replay_speed_label_var).pack(anchor=tk.W)
        ttk.Scale(
            speed_frame,
            from_=0.25,
            to=4.0,
            variable=self.replay_speed_var,
            command=self._on_replay_speed_change,
        ).pack(fill=tk.X, pady=(2, 0))

        ttk.Separator(command_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=4, pady=4)
        file_tools = ttk.Frame(command_frame)
        file_tools.pack(fill=tk.X, padx=4, pady=(1, 6))
        ttk.Button(file_tools, text="Save", command=self._save).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        ttk.Button(file_tools, text="Load", command=self._load).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

    def _build_left_panel_legacy_unused(self, parent):
        """Legacy stacked inspector retained only for comparison during P3."""
        canvas = tk.Canvas(parent, width=290, highlightthickness=0, bg=GCS_THEME["bg_panel"])
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

        speed_frame = ttk.Frame(action_frame)
        speed_frame.pack(fill=tk.X, padx=4, pady=(2, 4))
        ttk.Label(speed_frame, textvariable=self.replay_speed_label_var).pack(anchor=tk.W)
        ttk.Scale(
            speed_frame,
            from_=0.25,
            to=4.0,
            variable=self.replay_speed_var,
            command=self._on_replay_speed_change,
        ).pack(fill=tk.X, pady=(2, 0))

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
        ttk.Button(toolbar_frame, text="Refresh", command=self._refresh_canvas).pack(side=tk.LEFT, padx=4)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Label(toolbar_frame, textvariable=self.model_name_var, style="Section.TLabel").pack(side=tk.LEFT, padx=4)

        replay_frame = ttk.Frame(parent)
        replay_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        ttk.Label(replay_frame, textvariable=self.replay_state_var, style="RailTitle.TLabel").pack(side=tk.LEFT, padx=(4, 8))
        ttk.Label(replay_frame, textvariable=self.replay_step_var, style="Rail.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(replay_frame, textvariable=self.replay_action_var, style="Rail.TLabel").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Progressbar(replay_frame, variable=self.replay_progress_var, maximum=100, length=140).pack(side=tk.LEFT, padx=8)
        ttk.Button(replay_frame, text="Stop", command=self._stop_history_replay).pack(side=tk.LEFT, padx=(0, 4))

        solve_frame = ttk.Frame(parent)
        solve_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        ttk.Label(solve_frame, textvariable=self.solve_summary_var, style="Rail.TLabel").pack(fill=tk.X, padx=4)

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

        self.log_label = tk.Label(
            status_frame,
            text="  Ready",
            font=("Consolas", 9),
            anchor=tk.W,
            bg=GCS_THEME["bg_panel_alt"],
            fg=GCS_THEME["text_secondary"],
            padx=4,
            pady=2,
        )
        self.log_label.pack(fill=tk.X)

    def _log_info(self, msg):
        self.log_label.config(text=f"  INFO {msg}", fg=STATE_COLORS["info"])

    def _log_warning(self, msg):
        self.log_label.config(text=f"  WARN {msg}", fg=STATE_COLORS["warning"])

    def _log_error(self, msg):
        self.log_label.config(text=f"  ERR  {msg}", fg=STATE_COLORS["error"])

    def _log_success(self, msg):
        self.log_label.config(text=f"  OK   {msg}", fg=STATE_COLORS["solved"])

    def _configure_theme(self, style):
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        font_ui = ("Segoe UI", 9)
        style.configure(".", background=GCS_THEME["bg_window"], foreground=GCS_THEME["text_primary"], font=font_ui)
        style.configure("TFrame", background=GCS_THEME["bg_window"])
        style.configure("TNotebook", background=GCS_THEME["bg_panel"], bordercolor=GCS_THEME["border"])
        style.configure(
            "TNotebook.Tab",
            background=GCS_THEME["bg_panel_alt"],
            foreground=GCS_THEME["text_secondary"],
            padding=(8, 4),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", GCS_THEME["bg_table"])],
            foreground=[("selected", GCS_THEME["text_primary"]), ("active", STATE_COLORS["focus_active"])],
        )
        style.configure("TLabelframe", background=GCS_THEME["bg_panel"], bordercolor=GCS_THEME["border"], relief=tk.SOLID)
        style.configure(
            "TLabelframe.Label",
            background=GCS_THEME["bg_panel"],
            foreground=GCS_THEME["text_secondary"],
            font=("Segoe UI", 9, "bold"),
        )
        style.configure("TLabel", background=GCS_THEME["bg_window"], foreground=GCS_THEME["text_primary"])
        style.configure("DOF.TLabel", font=("Segoe UI", 11, "bold"), background=GCS_THEME["bg_panel"])
        style.configure("SummaryName.TLabel", font=("Segoe UI", 10, "bold"), background=GCS_THEME["bg_panel"], foreground=GCS_THEME["text_primary"])
        style.configure("SummaryValue.TLabel", font=("Consolas", 9), background=GCS_THEME["bg_panel"], foreground=GCS_THEME["text_secondary"])
        style.configure("Section.TLabel", font=("Segoe UI", 9, "bold"), foreground=GCS_THEME["text_secondary"])
        style.configure("RailTitle.TLabel", font=("Segoe UI", 9, "bold"), background=GCS_THEME["bg_window"], foreground=GCS_THEME["text_primary"])
        style.configure("Rail.TLabel", font=("Consolas", 9), background=GCS_THEME["bg_window"], foreground=GCS_THEME["text_secondary"])
        style.configure("Status.TLabel", font=("Consolas", 9), background=GCS_THEME["bg_panel_alt"], foreground=GCS_THEME["text_secondary"])
        style.configure("Log.TLabel", font=("Consolas", 9))
        style.configure(
            "Action.TButton",
            padding=4,
            background=GCS_THEME["bg_panel_alt"],
            foreground=GCS_THEME["text_primary"],
            bordercolor=GCS_THEME["border"],
            focuscolor=GCS_THEME["border"],
        )
        style.map(
            "Action.TButton",
            background=[("active", GCS_THEME["bg_table_selected"]), ("pressed", STATE_COLORS["focus"])],
            foreground=[("pressed", GCS_THEME["text_on_accent"])],
        )
        style.configure(
            "Primary.TButton",
            padding=5,
            background=STATE_COLORS["focus"],
            foreground=GCS_THEME["text_on_accent"],
            bordercolor=STATE_COLORS["focus_active"],
            focuscolor=STATE_COLORS["focus_active"],
        )
        style.map(
            "Primary.TButton",
            background=[("active", STATE_COLORS["focus_active"]), ("pressed", STATE_COLORS["focus_active"])],
            foreground=[("active", GCS_THEME["text_on_accent"]), ("pressed", GCS_THEME["text_on_accent"])],
        )
        style.configure(
            "TButton",
            background=GCS_THEME["bg_panel_alt"],
            foreground=GCS_THEME["text_primary"],
            bordercolor=GCS_THEME["border"],
            focuscolor=GCS_THEME["border"],
        )
        style.map("TButton", background=[("active", GCS_THEME["bg_table_selected"]), ("pressed", STATE_COLORS["focus"])])
        style.configure("TRadiobutton", background=GCS_THEME["bg_window"], foreground=GCS_THEME["text_secondary"])
        style.map("TRadiobutton", foreground=[("selected", GCS_THEME["text_primary"]), ("active", STATE_COLORS["focus_active"])])
        style.configure("Horizontal.TScale", background=GCS_THEME["bg_panel"], troughcolor=GCS_THEME["bg_panel_alt"])
        style.configure(
            "Treeview",
            background=GCS_THEME["bg_table"],
            fieldbackground=GCS_THEME["bg_table"],
            foreground=GCS_THEME["text_primary"],
            bordercolor=GCS_THEME["border"],
            rowheight=22,
        )
        style.configure(
            "Treeview.Heading",
            background=GCS_THEME["bg_panel_alt"],
            foreground=GCS_THEME["text_secondary"],
            bordercolor=GCS_THEME["border"],
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Treeview",
            background=[("selected", GCS_THEME["bg_table_selected"])],
            foreground=[("selected", GCS_THEME["text_primary"])],
        )

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
        self.fig.patch.set_facecolor(GCS_THEME["bg_canvas"])
        ax.set_facecolor(GCS_THEME["bg_canvas"])
        ax.text(0.5, 0.5, welcome, ha="center", va="center", fontsize=11, family="monospace",
                transform=ax.transAxes, color=GCS_THEME["text_secondary"])
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
            self.dof_label.config(text=f"  Net DOF: {dof} (Well-constrained) ✓  ", foreground=STATE_COLORS["solved"])
        elif status == "UnderConstrained":
            self.dof_label.config(text=f"  Net DOF: {dof} (Under-constrained) ⚠  ", foreground=STATE_COLORS["warning"])
        elif status == "OverConstrained":
            self.dof_label.config(text=f"  Net DOF: {dof} (Over-constrained) ✗  ", foreground=STATE_COLORS["error"])
        else:
            self.dof_label.config(text="  Net DOF: — (Empty)  ", foreground=GCS_THEME["text_muted"])

    def _update_status_info(self):
        summary = graph_summary(self.graph)
        self.summary_counts_var.set(
            f"RS {summary['rigid_sets']}   G {summary['geometries']}   C {summary['constraints']}"
        )
        self.summary_dof_var.set(f"Net DOF: {summary['dof']}")
        self.summary_status_var.set(f"Status: {summary['status']}")
        self.status_label.config(
            text=(
                f"  RS:{summary['rigid_sets']}  G:{summary['geometries']}  "
                f"C:{summary['constraints']}  DOF:{summary['dof']}  [{summary['status']}]"
            )
        )

    def _on_view_change(self):
        self._refresh_canvas()

    def _refresh_canvas(self):
        self._cancel_history_replay()
        self._draw_graph_on_canvas(self.graph, self.view_var.get(), use_welcome=True)

    def _set_current_model(self, filepath):
        self.current_model_name = os.path.basename(filepath) if filepath else "Untitled"
        self.model_name_var.set(f"Model: {self.current_model_name}")
        self.summary_model_var.set(self.current_model_name)

    def _draw_graph_on_canvas(self, graph: GCSGraph, view: str, use_welcome: bool = False, title=None, focus=None):
        if not graph.geometries:
            if use_welcome:
                self._draw_welcome()
            else:
                self.fig.clear()
                self.canvas_widget.draw()
            return

        try:
            render_graph_view(graph, self.fig, view, title=title, focus=focus)
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
            if not self.graph.geometries_span_rigid_sets(r["geometry_ids"]):
                self._log_warning("Constraint geometries must belong to different rigid sets")
                return
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

    def _set_solve_summary(self, state: str, message: str):
        self.solve_state_var.set(state)
        self.solve_summary_var.set(f"Solve {state}: {message}")

    def _parse_solve_report(self, output: str) -> dict:
        satisfied = 0
        violated = 0
        for line in output.split("\n"):
            stripped = line.strip()
            if stripped.endswith("SATISFIED"):
                satisfied += 1
            elif stripped.endswith("VIOLATED"):
                violated += 1

        total = satisfied + violated
        if "Global status: WellConstrained" in output:
            global_status = "Well-constrained"
        elif "Global status: UnderConstrained" in output:
            global_status = "Under-constrained"
        elif "Global status: OverConstrained" in output:
            global_status = "Over-constrained"
        else:
            global_status = "Unknown"

        if total == 0:
            state = "unknown"
            message = f"{global_status}; no constraint report"
        elif violated == 0:
            state = "success"
            message = f"{satisfied}/{total} constraints satisfied; {global_status}"
        else:
            state = "warning"
            message = f"{satisfied}/{total} satisfied, {violated} violated; {global_status}"

        return {
            "state": state,
            "message": message,
            "satisfied": satisfied,
            "violated": violated,
            "total": total,
            "global_status": global_status,
        }

    def _solve(self):
        if not self.graph.geometries:
            self._log_warning("Nothing to solve — add geometries first")
            return

        temp_dir = os.path.join(FIXTURE_SCENE_DIR, "_tui_temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, "solve_input.json")
        write_graph_file(self.graph, temp_path)

        self.graph.history.append({"action": "Solve", "payload": {}})

        if self.engine.is_available():
            self._set_solve_summary("running", "Solving current model...")
            self._log_info("Solving...")
            self.root.update_idletasks()

            def run_solve():
                result = self.engine.solve(temp_path)
                self.root.after(0, lambda: self._on_solve_done(result, temp_path))

            threading.Thread(target=run_solve, daemon=True).start()
        else:
            self._set_solve_summary("error", f"GCS.exe not found at {self.engine.exe_path}")
            self._log_error(f"GCS.exe not found at {self.engine.exe_path}")

    def _on_solve_done(self, result, temp_path):
        if "error" in result:
            self._set_solve_summary("error", result["error"])
            self._log_error(f"Solve error: {result['error']}")
            return

        output = result.get("output", "")
        report = self._parse_solve_report(output)
        self._last_solve_report = report
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

        self._set_solve_summary(report["state"], report["message"])
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
            initialdir=os.path.join(FIXTURE_SCENE_DIR, "saved"),
        )
        if filepath:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            write_graph_file(self.graph, filepath)
            self._set_current_model(filepath)
            self.event_store.append(self.scene_id, "ModelSaved", {"path": filepath})
            self._log_success(f"Saved to {filepath}")

    def _load(self):
        filepath = filedialog.askopenfilename(
            title="Load GCS Model",
            filetypes=[("GCS Model (JSON)", "*.json"), ("GCS Graph (TXT)", "*.txt"), ("All Files", "*.*")],
            initialdir=FIXTURE_SCENE_DIR,
        )
        if filepath:
            try:
                self.graph = read_graph_file(filepath)
                self._set_current_model(filepath)
                self.event_store.append(self.scene_id, "GraphLoaded", {"path": filepath})
                self._refresh_tables()
                self._refresh_canvas()
                self._log_success(f"Loaded {os.path.basename(filepath)} ({len(self.graph.history)} history steps)")
            except Exception as e:
                self._log_error(f"Load error: {e}")

    def _set_replay_state(self, state: str, step: str, action: str, progress: float):
        self.replay_state_var.set(state)
        self.replay_step_var.set(step)
        self.replay_action_var.set(action)
        self.replay_progress_var.set(max(0.0, min(100.0, progress)))

    def _stop_history_replay(self):
        if self._history_replay_job is None and not self._history_replay_history:
            return
        restore_view = self._history_replay_view or self.view_var.get()
        self._cancel_history_replay()
        self.view_var.set(restore_view)
        self._draw_graph_on_canvas(self.graph, restore_view, use_welcome=True)
        self._log_info("Replay stopped; restored current view")

    def _replay_history(self):
        if not self.graph.history:
            self._log_warning("No history to replay")
            return
        self._cancel_history_replay()
        self._history_replay_history = list(self.graph.history)
        self._history_replay_index = -1
        self._history_replay_view = self.view_var.get()

        self.fig.clear()
        self.canvas_widget.draw()
        speed = self._history_replay_speed()
        total = len(self._history_replay_history)
        self._set_replay_state("Replay running", f"Step 0 / {total}", "Clearing viewport", 0.0)
        self._log_info(f"Replay history: clearing view (0/{len(self._history_replay_history)}, {speed:.2f}x)")
        self._history_replay_job = self.root.after(self._history_replay_delay_ms(350), self._advance_history_replay)

    def _advance_history_replay(self):
        self._history_replay_job = None
        history = self._history_replay_history
        if not history:
            return

        next_index = self._history_replay_index + 1
        if next_index >= len(history):
            self._finish_history_replay()
            return

        self._history_replay_index = next_index
        entry = history[next_index]
        action = str(entry.get("action", "Unknown"))
        replay_graph = build_history_graph(history, next_index)
        focus = self._history_focus_from_entry(entry, replay_graph)
        title = f"Replay History - Step {next_index + 1}/{len(history)}: {action}"
        progress = ((next_index + 1) / len(history)) * 100.0
        self._set_replay_state(
            "Replay running",
            f"Step {next_index + 1} / {len(history)}",
            action,
            progress,
        )

        try:
            self._draw_graph_on_canvas(
                replay_graph,
                self._history_replay_view or self.view_var.get(),
                title=title,
                focus=focus,
            )
            speed = self._history_replay_speed()
            self._log_info(f"Replay history: step {next_index + 1}/{len(history)} {action} ({speed:.2f}x)")
        except Exception as exc:
            render_message(self.fig, f"Replay error:\n{exc}", title="Replay History")
            self.canvas_widget.draw()
            self._set_replay_state("Replay error", f"Step {next_index + 1} / {len(history)}", action, progress)
            self._log_error(f"Replay error: {exc}")
            self._history_replay_job = self.root.after(800, self._finish_history_replay)
            return

        self._history_replay_job = self.root.after(self._history_replay_delay_ms(650), self._advance_history_replay)

    def _history_focus_from_entry(self, entry: dict, graph: GCSGraph):
        action = entry.get("action")
        payload = entry.get("payload") or {}
        focus = {
            "mode": "replay",
            "rigid_set_ids": [],
            "geometry_ids": [],
            "constraint_ids": [],
        }

        def add_int(key, value):
            try:
                focus[key].append(int(value))
            except (TypeError, ValueError):
                pass

        if action in ("AddRigidSet", "RemoveRigidSet"):
            add_int("rigid_set_ids", payload.get("id"))
        elif action in ("AddGeometry", "RemoveGeometry"):
            add_int("geometry_ids", payload.get("id"))
            add_int("rigid_set_ids", payload.get("rigid_set_id"))
            try:
                geometry_id = int(payload.get("id"))
            except (TypeError, ValueError):
                geometry_id = None
            geometry = graph.find_geometry(geometry_id) if geometry_id is not None else None
            if geometry is not None:
                add_int("rigid_set_ids", geometry.rigid_set_id)
        elif action in ("AddConstraint", "RemoveConstraint", "UpdateConstraint"):
            constraint_id = payload.get("id")
            add_int("constraint_ids", constraint_id)
            geometry_ids = payload.get("geometry_ids")
            if geometry_ids is None and constraint_id is not None:
                try:
                    constraint = graph.find_constraint(int(constraint_id))
                except (TypeError, ValueError):
                    constraint = None
                geometry_ids = constraint.geometry_ids if constraint is not None else []
            for gid in geometry_ids or []:
                add_int("geometry_ids", gid)
                try:
                    geometry = graph.find_geometry(int(gid))
                except (TypeError, ValueError):
                    geometry = None
                if geometry is not None:
                    add_int("rigid_set_ids", geometry.rigid_set_id)

        for key, values in list(focus.items()):
            if key == "mode":
                continue
            focus[key] = sorted(set(values))
        return focus

    def _finish_history_replay(self):
        restore_view = self._history_replay_view or self.view_var.get()
        self._history_replay_job = None
        self._history_replay_history = []
        self._history_replay_index = -1
        self._history_replay_view = None
        self.view_var.set(restore_view)
        self._set_replay_state("Replay complete", "Step 0 / 0", "Current model restored", 100.0)
        self._draw_graph_on_canvas(self.graph, restore_view, use_welcome=True)
        self._log_success("Replay history complete; restored current view")

    def _cancel_history_replay(self):
        if self._history_replay_job is not None:
            try:
                self.root.after_cancel(self._history_replay_job)
            except tk.TclError:
                pass
        self._history_replay_job = None
        self._history_replay_history = []
        self._history_replay_index = -1
        self._history_replay_view = None
        self._set_replay_state("Replay ready", "Step 0 / 0", "No active replay", 0.0)

    def _on_replay_speed_change(self, value=None):
        speed = self._history_replay_speed()
        self.replay_speed_label_var.set(f"Replay Speed: {speed:.2f}x")

    def _history_replay_speed(self):
        try:
            speed = float(self.replay_speed_var.get())
        except (tk.TclError, ValueError):
            speed = 1.0
        return max(0.25, min(4.0, speed))

    def _history_replay_delay_ms(self, base_ms: int):
        return max(80, int(base_ms / self._history_replay_speed()))

    def run(self):
        self._refresh_tables()
        self.root.mainloop()


def main():
    app = GCSPlatformGUI()
    app.run()


if __name__ == "__main__":
    main()
