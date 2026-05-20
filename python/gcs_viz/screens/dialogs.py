from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Static, Input, Button, Select, Label
from textual.validation import Number
from gcs_viz.algebra import GCSGraph, GeometryType, ConstraintType, VALID_CONSTRAINT_SIGNATURES
from gcs_viz.color_scheme import GEOMETRY_NAMES, CONSTRAINT_NAMES


class AddRigidSetDialog(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Cancel")]

    def __init__(self, graph: GCSGraph):
        super().__init__()
        self.graph = graph

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Add Rigid Set", classes="section-label")
            with Horizontal(classes="field-row"):
                yield Label("RS ID:")
                yield Input(placeholder="auto", id="rs-id-input")
            with Horizontal(classes="btn-row"):
                yield Button("Add", id="confirm-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="default")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            id_input = self.query_one("#rs-id-input", Input)
            rs_id = None
            if id_input.value.strip():
                try:
                    rs_id = int(id_input.value)
                except ValueError:
                    rs_id = None
            self.dismiss(rs_id)
        else:
            self.dismiss(None)


class AddGeometryDialog(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Cancel")]

    def __init__(self, graph: GCSGraph):
        super().__init__()
        self.graph = graph

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Add Geometry", classes="section-label")
            with Horizontal(classes="field-row"):
                yield Label("Type:")
                yield Select(
                    [(name, str(int(t))) for t, name in GEOMETRY_NAMES.items()],
                    value=str(int(GeometryType.Point)),
                    id="geom-type-select"
                )
            with Horizontal(classes="field-row"):
                yield Label("RS ID:")
                rs_options = [(f"RS {rs.id}", str(rs.id)) for rs in self.graph.rigid_sets]
                yield Select(rs_options, value=str(self.graph.rigid_sets[0].id) if self.graph.rigid_sets else "0", id="geom-rs-select")
            with Horizontal(classes="field-row"):
                yield Label("X:")
                yield Input(value="0", id="geom-x")
            with Horizontal(classes="field-row"):
                yield Label("Y:")
                yield Input(value="0", id="geom-y")
            with Horizontal(classes="field-row"):
                yield Label("Z:")
                yield Input(value="0", id="geom-z")
            with Horizontal(classes="btn-row"):
                yield Button("Add", id="confirm-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="default")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            try:
                geom_type = GeometryType(int(self.query_one("#geom-type-select", Select).value))
                rs_id = int(self.query_one("#geom-rs-select", Select).value)
                x = float(self.query_one("#geom-x", Input).value or "0")
                y = float(self.query_one("#geom-y", Input).value or "0")
                z = float(self.query_one("#geom-z", Input).value or "0")
                v = [x, y, z, 0.0, 0.0, 0.0]
                self.dismiss({"type": geom_type, "rs_id": rs_id, "v": v})
            except (ValueError, TypeError) as e:
                self.dismiss(None)
        else:
            self.dismiss(None)


class AddConstraintDialog(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Cancel")]

    def __init__(self, graph: GCSGraph):
        super().__init__()
        self.graph = graph

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Add Constraint", classes="section-label")
            with Horizontal(classes="field-row"):
                yield Label("Type:")
                yield Select(
                    [(name, str(int(t))) for t, name in CONSTRAINT_NAMES.items()],
                    value=str(int(ConstraintType.Distance)),
                    id="const-type-select"
                )
            with Horizontal(classes="field-row"):
                yield Label("Geom 1:")
                geom_options = [(f"G{g.id} ({GEOMETRY_NAMES.get(g.type, '?')})", str(g.id)) for g in self.graph.geometries]
                yield Select(geom_options, value=str(self.graph.geometries[0].id) if self.graph.geometries else "0", id="const-g1-select")
            with Horizontal(classes="field-row"):
                yield Label("Geom 2:")
                g2_default = str(self.graph.geometries[-1].id) if len(self.graph.geometries) > 1 else str(self.graph.geometries[0].id) if self.graph.geometries else "0"
                yield Select(geom_options, value=g2_default, id="const-g2-select")
            with Horizontal(classes="field-row"):
                yield Label("Value:")
                yield Input(value="0", id="const-value")
            with Horizontal(classes="btn-row"):
                yield Button("Add", id="confirm-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="default")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            try:
                ctype = ConstraintType(int(self.query_one("#const-type-select", Select).value))
                g1_id = int(self.query_one("#const-g1-select", Select).value)
                g2_id = int(self.query_one("#const-g2-select", Select).value)
                value = float(self.query_one("#const-value", Input).value or "0")
                self.dismiss({"type": ctype, "geometry_ids": [g1_id, g2_id], "value": value})
            except (ValueError, TypeError) as e:
                self.dismiss(None)
        else:
            self.dismiss(None)
