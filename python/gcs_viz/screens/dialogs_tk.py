import tkinter as tk
from tkinter import ttk
from gcs_viz.algebra import GCSGraph, GeometryType, ConstraintType
from gcs_viz.color_scheme import GEOMETRY_NAMES, CONSTRAINT_NAMES
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from gcs_viz.visualizer import build_3d_on_figure


class AddRigidSetDialog(tk.Toplevel):
    def __init__(self, parent, graph: GCSGraph):
        super().__init__(parent)
        self.graph = graph
        self.result = None

        self.title("Add Rigid Set")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="RS ID:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self._rs_id_var = tk.StringVar(value="auto")
        self._rs_id_entry = ttk.Entry(frame, textvariable=self._rs_id_var, width=20)
        self._rs_id_entry.grid(row=0, column=1, pady=4, padx=(8, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn_frame, text="OK", width=10, command=self._on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Cancel", width=10, command=self._on_cancel).pack(side=tk.LEFT, padx=4)

        self._center_on_parent(parent)
        self.wait_window()

    def _on_ok(self):
        raw = self._rs_id_var.get().strip()
        if raw and raw != "auto":
            try:
                self.result = int(raw)
            except ValueError:
                self.result = None
        else:
            self.result = None
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")


class AddGeometryDialog(tk.Toplevel):
    def __init__(self, parent, graph: GCSGraph):
        super().__init__(parent)
        self.graph = graph
        self.result = None

        self.title("Add Geometry")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Type:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self._type_var = tk.StringVar(value=GEOMETRY_NAMES[0])
        type_cb = ttk.Combobox(frame, textvariable=self._type_var,
                               values=list(GEOMETRY_NAMES.values()),
                               state="readonly", width=17)
        type_cb.grid(row=0, column=1, pady=4, padx=(8, 0))

        ttk.Label(frame, text="RS:").grid(row=1, column=0, sticky=tk.W, pady=4)
        rs_ids = [str(rs.id) for rs in graph.rigid_sets]
        self._rs_var = tk.StringVar(value=rs_ids[0] if rs_ids else "")
        rs_cb = ttk.Combobox(frame, textvariable=self._rs_var,
                             values=rs_ids, state="readonly", width=17)
        rs_cb.grid(row=1, column=1, pady=4, padx=(8, 0))

        self._coord_vars = {}
        for i, axis in enumerate(("X", "Y", "Z")):
            ttk.Label(frame, text=f"{axis}:").grid(row=2 + i, column=0, sticky=tk.W, pady=4)
            var = tk.StringVar(value="0")
            self._coord_vars[axis] = var
            ttk.Entry(frame, textvariable=var, width=20).grid(row=2 + i, column=1, pady=4, padx=(8, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn_frame, text="OK", width=10, command=self._on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Cancel", width=10, command=self._on_cancel).pack(side=tk.LEFT, padx=4)

        self._center_on_parent(parent)
        self.wait_window()

    def _on_ok(self):
        try:
            type_name = self._type_var.get()
            type_map = {v: k for k, v in GEOMETRY_NAMES.items()}
            geom_type = GeometryType(type_map[type_name])
            rs_id = int(self._rs_var.get())
            x = float(self._coord_vars["X"].get() or "0")
            y = float(self._coord_vars["Y"].get() or "0")
            z = float(self._coord_vars["Z"].get() or "0")
            self.result = {"type": geom_type, "rs_id": rs_id, "v": [x, y, z, 0.0, 0.0, 0.0]}
        except (ValueError, KeyError):
            self.result = None
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")


class AddConstraintDialog(tk.Toplevel):
    def __init__(self, parent, graph: GCSGraph):
        super().__init__(parent)
        self.graph = graph
        self.result = None

        self.title("Add Constraint")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Type:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self._type_var = tk.StringVar(value=CONSTRAINT_NAMES[3])
        type_cb = ttk.Combobox(frame, textvariable=self._type_var,
                               values=list(CONSTRAINT_NAMES.values()),
                               state="readonly", width=17)
        type_cb.grid(row=0, column=1, pady=4, padx=(8, 0))

        geom_options = [f"G{g.id} ({GEOMETRY_NAMES.get(g.type, '?')})" for g in graph.geometries]
        geom_ids = [str(g.id) for g in graph.geometries]
        self._geom_id_map = dict(zip(geom_options, geom_ids))

        ttk.Label(frame, text="Geom 1:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self._g1_var = tk.StringVar(value=geom_options[0] if geom_options else "")
        g1_cb = ttk.Combobox(frame, textvariable=self._g1_var,
                             values=geom_options, state="readonly", width=17)
        g1_cb.grid(row=1, column=1, pady=4, padx=(8, 0))

        ttk.Label(frame, text="Geom 2:").grid(row=2, column=0, sticky=tk.W, pady=4)
        g2_default = geom_options[-1] if len(geom_options) > 1 else (geom_options[0] if geom_options else "")
        self._g2_var = tk.StringVar(value=g2_default)
        g2_cb = ttk.Combobox(frame, textvariable=self._g2_var,
                             values=geom_options, state="readonly", width=17)
        g2_cb.grid(row=2, column=1, pady=4, padx=(8, 0))

        ttk.Label(frame, text="Value:").grid(row=3, column=0, sticky=tk.W, pady=4)
        self._value_var = tk.StringVar(value="0")
        ttk.Entry(frame, textvariable=self._value_var, width=20).grid(row=3, column=1, pady=4, padx=(8, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn_frame, text="OK", width=10, command=self._on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Cancel", width=10, command=self._on_cancel).pack(side=tk.LEFT, padx=4)

        self._center_on_parent(parent)
        self.wait_window()

    def _on_ok(self):
        try:
            type_name = self._type_var.get()
            type_map = {v: k for k, v in CONSTRAINT_NAMES.items()}
            ctype = ConstraintType(type_map[type_name])
            g1_id = int(self._geom_id_map[self._g1_var.get()])
            g2_id = int(self._geom_id_map[self._g2_var.get()])
            value = float(self._value_var.get() or "0")
            self.result = {"type": ctype, "geometry_ids": [g1_id, g2_id], "value": value}
        except (ValueError, KeyError):
            self.result = None
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")


class DeleteConfirmDialog(tk.Toplevel):
    def __init__(self, parent, item_info: str):
        super().__init__(parent)
        self.result = False

        self.title("Confirm Delete")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Are you sure you want to delete?").grid(row=0, column=0, columnspan=2, pady=4)
        ttk.Label(frame, text=item_info).grid(row=1, column=0, columnspan=2, pady=4)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn_frame, text="OK", width=10, command=self._on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Cancel", width=10, command=self._on_cancel).pack(side=tk.LEFT, padx=4)

        self._center_on_parent(parent)
        self.wait_window()

    def _on_ok(self):
        self.result = True
        self.destroy()

    def _on_cancel(self):
        self.result = False
        self.destroy()

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")


class EditConstraintDialog(tk.Toplevel):
    def __init__(self, parent, graph: GCSGraph, constraint_id: int):
        super().__init__(parent)
        self.graph = graph
        self.constraint_id = constraint_id
        self.result = None

        self.title("Edit Constraint")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        c = graph.find_constraint(constraint_id)
        if c is None:
            self.destroy()
            return

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=4)
        ttk.Label(frame, text=str(c.id)).grid(row=0, column=1, sticky=tk.W, pady=4, padx=(8, 0))

        ttk.Label(frame, text="Type:").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Label(frame, text=CONSTRAINT_NAMES.get(c.type, "?")).grid(row=1, column=1, sticky=tk.W, pady=4, padx=(8, 0))

        ttk.Label(frame, text="Geometries:").grid(row=2, column=0, sticky=tk.W, pady=4)
        gids = ", ".join(f"G{gid}" for gid in c.geometry_ids)
        ttk.Label(frame, text=gids).grid(row=2, column=1, sticky=tk.W, pady=4, padx=(8, 0))

        ttk.Label(frame, text="Value:").grid(row=3, column=0, sticky=tk.W, pady=4)
        self._value_var = tk.StringVar(value=str(c.value))
        ttk.Entry(frame, textvariable=self._value_var, width=20).grid(row=3, column=1, pady=4, padx=(8, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn_frame, text="OK", width=10, command=self._on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Cancel", width=10, command=self._on_cancel).pack(side=tk.LEFT, padx=4)

        self._center_on_parent(parent)
        self.wait_window()

    def _on_ok(self):
        try:
            value = float(self._value_var.get())
            self.result = {"id": self.constraint_id, "value": value}
        except ValueError:
            self.result = None
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")
