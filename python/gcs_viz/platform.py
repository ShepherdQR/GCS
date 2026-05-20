import os
import sys

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_DIR = os.path.normpath(os.path.join(PACKAGE_DIR, ".."))
REPO_ROOT = os.path.normpath(os.path.join(PYTHON_DIR, ".."))
FIXTURE_SCENE_DIR = os.path.join(REPO_ROOT, "fixtures", "scene")

sys.path.insert(0, PYTHON_DIR)

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, Static, Button, Input, Select, Label,
    DataTable, TabbedContent, TabPane, Tree, TextArea, ListView, ListItem,
)
from textual.reactive import reactive
from textual import work
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.markdown import Markdown

from gcs_viz.algebra import (
    GCSGraph, GeometryType, ConstraintType, RigidSet, Geometry, Constraint,
    DOF_GEOMETRY, DOF_REMOVED_CONSTRAINT, VALID_CONSTRAINT_SIGNATURES,
    read_graph_file, write_graph_file,
)
from gcs_viz.color_scheme import RIGID_SET_COLORS, CONSTRAINT_COLORS, GEOMETRY_NAMES, CONSTRAINT_NAMES, GCS_THEME
from gcs_viz.event_store import EventStore
from gcs_viz.engine_bridge import EngineBridge
from gcs_viz.screens.dialogs import AddRigidSetDialog, AddGeometryDialog, AddConstraintDialog


class DOFIndicator(Static):
    dof_value = reactive(0)

    def render(self) -> Text:
        if self.dof_value == 0:
            return Text(f"  Net DOF: 0 (Well-constrained) ✓  ", style="bold green")
        elif self.dof_value > 0:
            return Text(f"  Net DOF: {self.dof_value} (Under-constrained) ⚠  ", style="bold yellow")
        else:
            return Text(f"  Net DOF: {self.dof_value} (Over-constrained) ✗  ", style="bold red")


class StatusBar(Static):
    status_text = reactive("Ready")
    graph_info = reactive("No graph")

    def render(self) -> Text:
        return Text(f"  {self.status_text}  |  {self.graph_info}  ", style="white on #16213e")


class GCSPlatform(App):
    CSS = """
    Screen {
        layout: horizontal;
    }

    #sidebar {
        width: 28;
        min-width: 24;
        max-width: 36;
        dock: left;
        background: $surface;
        border-right: solid $primary;
    }

    #main-area {
        width: 1fr;
    }

    .sidebar-title {
        text-align: center;
        text-style: bold;
        padding: 1;
        background: $primary;
        color: $text;
    }

    .section-label {
        text-style: bold;
        padding: 1 0 0 1;
        color: $accent;
    }

    .action-btn {
        margin: 0 1;
        width: 100%;
    }

    .dof-bar {
        padding: 0 1;
        margin: 1 0;
        height: 3;
    }

    .status-bar {
        dock: bottom;
        height: 1;
    }

    #rs-list, #geom-list, #const-list {
        height: auto;
        max-height: 10;
        margin: 0 1;
    }

    #input-area {
        margin: 0 1;
    }

    .field-row {
        layout: horizontal;
        height: 3;
        margin: 0 0 1 0;
    }

    .field-row Input {
        width: 1fr;
    }

    .field-row Label {
        width: 8;
        padding: 1 1 0 0;
    }

    .field-row Select {
        width: 1fr;
    }

    .btn-row {
        layout: horizontal;
        height: 3;
        margin: 0 0 1 0;
    }

    .btn-row Button {
        width: 1fr;
        margin: 0 1;
    }

    #welcome {
        padding: 2 4;
    }

    DataTable {
        height: auto;
        max-height: 20;
    }

    Tree {
        height: auto;
        max-height: 15;
    }

    #dialog {
        padding: 1 2;
        background: $surface;
        border: solid $primary;
        width: 60;
        height: auto;
    }

    #dialog .section-label {
        text-align: center;
        padding: 1;
        margin-bottom: 1;
    }

    #dialog .field-row {
        layout: horizontal;
        height: 3;
        margin: 0 0 1 0;
    }

    #dialog .field-row Input {
        width: 1fr;
    }

    #dialog .field-row Label {
        width: 8;
        padding: 1 1 0 0;
    }

    #dialog .field-row Select {
        width: 1fr;
    }

    #dialog .btn-row {
        layout: horizontal;
        height: 3;
        margin: 1 0 0 0;
    }

    #dialog .btn-row Button {
        width: 1fr;
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("v", "view_3d", "3D View"),
        Binding("g", "view_graph", "Graph"),
        Binding("t", "view_three", "Three-View"),
        Binding("s", "solve", "Solve"),
        Binding("ctrl+s", "save_model", "Save"),
        Binding("ctrl+o", "load_model", "Load"),
    ]

    def __init__(self):
        super().__init__()
        self.graph = GCSGraph()
        self.event_store = EventStore()
        self.engine = EngineBridge()
        self.scene_id = "default"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("GCS Platform", classes="sidebar-title")
                yield DOFIndicator(classes="dof-bar")

                yield Label("▸ Rigid Sets", classes="section-label")
                yield DataTable(id="rs-list")

                with Horizontal(classes="btn-row"):
                    yield Button("+ RS", id="add-rs-btn", variant="success", classes="action-btn")
                    yield Button("- RS", id="del-rs-btn", variant="error", classes="action-btn")

                yield Label("▸ Geometries", classes="section-label")
                yield DataTable(id="geom-list")

                with Horizontal(classes="btn-row"):
                    yield Button("+ G", id="add-geom-btn", variant="success", classes="action-btn")
                    yield Button("- G", id="del-geom-btn", variant="error", classes="action-btn")

                yield Label("▸ Constraints", classes="section-label")
                yield DataTable(id="const-list")

                with Horizontal(classes="btn-row"):
                    yield Button("+ C", id="add-const-btn", variant="success", classes="action-btn")
                    yield Button("- C", id="del-const-btn", variant="error", classes="action-btn")

                yield Label("▸ Actions", classes="section-label")
                with Horizontal(classes="btn-row"):
                    yield Button("Solve", id="solve-btn", variant="primary", classes="action-btn")
                    yield Button("3D View", id="view3d-btn", variant="primary", classes="action-btn")
                with Horizontal(classes="btn-row"):
                    yield Button("Graph", id="viewgraph-btn", variant="primary", classes="action-btn")
                    yield Button("3-View", id="viewthree-btn", variant="primary", classes="action-btn")
                with Horizontal(classes="btn-row"):
                    yield Button("Save", id="save-btn", variant="default", classes="action-btn")
                    yield Button("Load", id="load-btn", variant="default", classes="action-btn")

            with Vertical(id="main-area"):
                yield self._build_welcome()

        yield StatusBar(classes="status-bar")

    def _build_welcome(self) -> Static:
        welcome = (
            "# GCS Platform — Geometric Constraint Solver\n\n"
            "## Quick Start\n\n"
            "1. **Add Rigid Sets** — Click `+ RS` to create rigid bodies\n"
            "2. **Add Geometries** — Click `+ G` to add Point/Line/Plane\n"
            "3. **Add Constraints** — Click `+ C` to define relationships\n"
            "4. **Solve** — Click `Solve` or press `S` to compute\n"
            "5. **Visualize** — Click `3D View`, `Graph`, or `3-View`\n\n"
            "## Keyboard Shortcuts\n\n"
            "| Key | Action |\n"
            "|-----|--------|\n"
            "| `V` | 3D View |\n"
            "| `G` | Constraint Graph |\n"
            "| `T` | Three-View |\n"
            "| `S` | Solve |\n"
            "| `Ctrl+S` | Save Model |\n"
            "| `Ctrl+O` | Load Model |\n"
            "| `Q` | Quit |\n\n"
            "## Data Model\n\n"
            "- **RigidSet**: A rigid body containing geometries\n"
            "- **Geometry**: Point(3 DOF), Line(6 DOF), Plane(6 DOF)\n"
            "- **Constraint**: Coincident(3), Parallel(2), Perpendicular(1), Distance(1), Angle(1)\n"
        )
        return Static(Markdown(welcome), id="welcome")

    def on_mount(self) -> None:
        self._refresh_tables()

    def _refresh_tables(self) -> None:
        self._refresh_rs_table()
        self._refresh_geom_table()
        self._refresh_const_table()
        self._update_dof()
        self._update_status()

    def _refresh_rs_table(self) -> None:
        table = self.query_one("#rs-list", DataTable)
        table.clear(columns=True)
        table.add_columns("ID", "Geom IDs")
        for rs in self.graph.rigid_sets:
            gids = ",".join(str(gid) for gid in rs.geometry_ids) or "—"
            table.add_row(str(rs.id), gids)

    def _refresh_geom_table(self) -> None:
        table = self.query_one("#geom-list", DataTable)
        table.clear(columns=True)
        table.add_columns("ID", "Type", "RS", "Position")
        for g in self.graph.geometries:
            type_name = GEOMETRY_NAMES.get(g.type, "?")
            if g.type == GeometryType.Point:
                pos = f"({g.v[0]:.1f},{g.v[1]:.1f},{g.v[2]:.1f})"
            elif g.type == GeometryType.Line:
                pos = f"({g.v[0]:.1f}→{g.v[3]:.1f},...)"
            else:
                pos = f"({g.v[0]:.1f},{g.v[1]:.1f},{g.v[2]:.1f})"
            table.add_row(str(g.id), type_name, str(g.rigid_set_id), pos)

    def _refresh_const_table(self) -> None:
        table = self.query_one("#const-list", DataTable)
        table.clear(columns=True)
        table.add_columns("ID", "Type", "Geoms", "Value")
        for c in self.graph.constraints:
            type_name = CONSTRAINT_NAMES.get(c.type, "?")
            gids = ",".join(str(gid) for gid in c.geometry_ids)
            val = f"{c.value:.2f}" if c.value != 0 else "—"
            table.add_row(str(c.id), type_name, gids, val)

    def _update_dof(self) -> None:
        dof = self.graph.compute_dof()
        self.query_one(DOFIndicator).dof_value = dof

    def _update_status(self) -> None:
        n_rs = len(self.graph.rigid_sets)
        n_g = len(self.graph.geometries)
        n_c = len(self.graph.constraints)
        dof = self.graph.compute_dof()
        status = self.query_one(StatusBar)
        status.graph_info = f"RS:{n_rs} G:{n_g} C:{n_c} DOF:{dof}"

    def _set_status(self, text: str) -> None:
        self.query_one(StatusBar).status_text = text

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id

        if btn_id == "add-rs-btn":
            await self._action_add_rigid_set()
        elif btn_id == "del-rs-btn":
            await self._action_del_rigid_set()
        elif btn_id == "add-geom-btn":
            await self._action_add_geometry()
        elif btn_id == "del-geom-btn":
            await self._action_del_geometry()
        elif btn_id == "add-const-btn":
            await self._action_add_constraint()
        elif btn_id == "del-const-btn":
            await self._action_del_constraint()
        elif btn_id == "solve-btn":
            self._action_solve()
        elif btn_id == "view3d-btn":
            self._action_view_3d()
        elif btn_id == "viewgraph-btn":
            self._action_view_graph()
        elif btn_id == "viewthree-btn":
            self._action_view_three()
        elif btn_id == "save-btn":
            await self._action_save()
        elif btn_id == "load-btn":
            await self._action_load()

    async def _action_add_rigid_set(self) -> None:
        def _on_rs_result(rs_id):
            if rs_id is not None:
                self.graph.add_rigid_set(rs_id)
                self.event_store.append(self.scene_id, "RigidSetAdded", {"id": rs_id})
                self._refresh_tables()
                self._set_status(f"Added RS {rs_id}")
        await self.push_screen(AddRigidSetDialog(self.graph), _on_rs_result)

    async def _action_del_rigid_set(self) -> None:
        if not self.graph.rigid_sets:
            self._set_status("No rigid sets to remove")
            return
        rs_id = self.graph.rigid_sets[-1].id
        self.graph.remove_rigid_set(rs_id)
        self.event_store.append(self.scene_id, "RigidSetRemoved", {"id": rs_id})
        self._refresh_tables()
        self._set_status(f"Removed RS {rs_id}")

    async def _action_add_geometry(self) -> None:
        if not self.graph.rigid_sets:
            self._set_status("Add a Rigid Set first!")
            return

        def _on_geom_result(result):
            if result is not None:
                geom_type = result["type"]
                rs_id = result["rs_id"]
                v = result["v"]
                geom_id = self.graph.next_geometry_id()
                self.graph.add_geometry(geom_type, rs_id, v=v, geom_id=geom_id)
                self.event_store.append(self.scene_id, "GeometryAdded", {
                    "id": geom_id, "type": int(geom_type), "rigid_set_id": rs_id, "v": v
                })
                self._refresh_tables()
                self._set_status(f"Added G{geom_id} ({GEOMETRY_NAMES.get(geom_type, '?')}) in RS{rs_id}")
        await self.push_screen(AddGeometryDialog(self.graph), _on_geom_result)

    async def _action_del_geometry(self) -> None:
        if not self.graph.geometries:
            self._set_status("No geometries to remove")
            return
        gid = self.graph.geometries[-1].id
        self.graph.remove_geometry(gid)
        self.event_store.append(self.scene_id, "GeometryRemoved", {"id": gid})
        self._refresh_tables()
        self._set_status(f"Removed G{gid}")

    async def _action_add_constraint(self) -> None:
        if len(self.graph.geometries) < 2:
            self._set_status("Need at least 2 geometries for a constraint")
            return

        def _on_const_result(result):
            if result is not None:
                ctype = result["type"]
                gids = result["geometry_ids"]
                value = result["value"]
                cid = self.graph.next_constraint_id()
                self.graph.add_constraint(ctype, gids, value=value, cid=cid)
                self.event_store.append(self.scene_id, "ConstraintAdded", {
                    "id": cid, "type": int(ctype), "geometry_ids": gids, "value": value
                })
                self._refresh_tables()
                self._set_status(f"Added C{cid} ({CONSTRAINT_NAMES.get(ctype, '?')}) G{gids[0]}↔G{gids[1]}")
        await self.push_screen(AddConstraintDialog(self.graph), _on_const_result)

    async def _action_del_constraint(self) -> None:
        if not self.graph.constraints:
            self._set_status("No constraints to remove")
            return
        cid = self.graph.constraints[-1].id
        self.graph.remove_constraint(cid)
        self.event_store.append(self.scene_id, "ConstraintRemoved", {"id": cid})
        self._refresh_tables()
        self._set_status(f"Removed C{cid}")

    def _action_solve(self) -> None:
        if not self.graph.geometries:
            self._set_status("Nothing to solve — add geometries first")
            return

        temp_dir = os.path.join(FIXTURE_SCENE_DIR, "_tui_temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, "solve_input.txt")
        write_graph_file(self.graph, temp_path)

        if self.engine.is_available():
            result = self.engine.solve(temp_path)
            if "error" in result:
                self._set_status(f"Solve error: {result['error']}")
            else:
                output = result.get("output", "")
                self._set_status(f"Solve completed! {output.strip()[-80:] if output else ''}")
                self.event_store.append(self.scene_id, "SolveCompleted", {"input": temp_path})
        else:
            self._set_status(f"GCS.exe not found at {self.engine.exe_path}. Save file manually.")
            self.event_store.append(self.scene_id, "SolveAttempted", {"input": temp_path, "note": "engine_not_available"})

    def _action_view_3d(self) -> None:
        if not self.graph.geometries:
            self._set_status("No geometries to visualize")
            return
        try:
            from gcs_viz.visualizer import _build_3d_figure
            fig = _build_3d_figure(self.graph)
            import tempfile, time
            path = os.path.join(tempfile.gettempdir(), f"gcs_3d_{time.strftime('%H%M%S')}.png")
            fig.savefig(path, dpi=100, bbox_inches="tight")
            self._set_status(f"3D view saved: {path}")
        except Exception as e:
            self._set_status(f"3D view error: {e}")

    def _action_view_graph(self) -> None:
        if not self.graph.geometries:
            self._set_status("No geometries to visualize")
            return
        try:
            from gcs_viz.visualizer import _build_constraint_graph_figure
            fig = _build_constraint_graph_figure(self.graph)
            import tempfile, time
            path = os.path.join(tempfile.gettempdir(), f"gcs_graph_{time.strftime('%H%M%S')}.png")
            fig.savefig(path, dpi=100, bbox_inches="tight")
            self._set_status(f"Graph view saved: {path}")
        except Exception as e:
            self._set_status(f"Graph view error: {e}")

    def _action_view_three(self) -> None:
        if not self.graph.geometries:
            self._set_status("No geometries to visualize")
            return
        try:
            from gcs_viz.visualizer import _build_three_view_figure
            fig = _build_three_view_figure(self.graph)
            import tempfile, time
            path = os.path.join(tempfile.gettempdir(), f"gcs_3view_{time.strftime('%H%M%S')}.png")
            fig.savefig(path, dpi=100, bbox_inches="tight")
            self._set_status(f"Three-view saved: {path}")
        except Exception as e:
            self._set_status(f"Three-view error: {e}")

    async def _action_save(self) -> None:
        scene_dir = os.path.join(FIXTURE_SCENE_DIR, "saved")
        os.makedirs(scene_dir, exist_ok=True)
        import time
        filename = f"gcs_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(scene_dir, filename)
        write_graph_file(self.graph, filepath)
        self.event_store.append(self.scene_id, "ModelSaved", {"path": filepath})
        self._set_status(f"Saved to {filepath}")

    async def _action_load(self) -> None:
        scene_dir = FIXTURE_SCENE_DIR
        if not os.path.isdir(scene_dir):
            self._set_status("No scene directory found")
            return
        txt_files = []
        for root, dirs, files in os.walk(scene_dir):
            for f in files:
                if f.endswith(".txt") and "_graph" not in f:
                    txt_files.append(os.path.join(root, f))
        if not txt_files:
            self._set_status("No .txt files found in fixtures/scene/")
            return
        latest = max(txt_files, key=os.path.getmtime)
        try:
            self.graph = read_graph_file(latest)
            self.event_store.append(self.scene_id, "GraphLoaded", {"path": latest})
            self._refresh_tables()
            self._set_status(f"Loaded {os.path.basename(latest)}")
        except Exception as e:
            self._set_status(f"Load error: {e}")

    def action_view_3d(self) -> None:
        self._action_view_3d()

    def action_view_graph(self) -> None:
        self._action_view_graph()

    def action_view_three(self) -> None:
        self._action_view_three()

    def action_solve(self) -> None:
        self._action_solve()

    async def action_save_model(self) -> None:
        await self._action_save()

    async def action_load_model(self) -> None:
        await self._action_load()


def main():
    app = GCSPlatform()
    app.run()


if __name__ == "__main__":
    main()
