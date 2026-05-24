"""Shared GCS visual tokens and compatibility aliases."""

GCS_TOKENS = {
    "surface.paper": "#F7F4EC",
    "surface.panel": "#FFFEFA",
    "surface.panel.subtle": "#EFEDE6",
    "surface.panel.muted": "#E8DFD0",
    "surface.canvas": "#FBFAF5",
    "surface.table.selected": "#EAD9CF",
    "surface.track": "#EFEBE2",
    "text.primary": "#181715",
    "text.secondary": "#5F5B53",
    "text.muted": "#8B867A",
    "text.inverse": "#FAF9F5",
    "rule.default": "#D8D1C4",
    "rule.soft": "#ECE7DD",
    "rule.strong": "#C9BDAA",
    "rule.axis": "#8B867A",
    "evidence.domain.fill": "#E7EDF8",
    "evidence.domain.stroke": "#435F8C",
    "evidence.graph.fill": "#EFE7F3",
    "evidence.graph.stroke": "#765D87",
    "evidence.planner.fill": "#E3F0E4",
    "evidence.planner.stroke": "#477861",
    "evidence.numeric.fill": "#EDF2DF",
    "evidence.numeric.stroke": "#5E7D43",
    "evidence.diagnostic.fill": "#F6E7CF",
    "evidence.diagnostic.stroke": "#A36B32",
    "evidence.failure.fill": "#F3DDD7",
    "evidence.failure.stroke": "#A94C43",
    "evidence.boundary.fill": "#EFEDE6",
    "evidence.boundary.stroke": "#777166",
    "state.focus": "#C8643F",
    "state.focus.active": "#B85F45",
    "state.ok": "#4B8A64",
    "state.info": "#6A8FB5",
    "state.warning": "#B88746",
    "state.error": "#B8574E",
    "state.pending": "#8B867A",
    "state.replay.current": "#C8643F",
    "state.violation": "#A94C43",
    "geometry.point.color": "#334C78",
    "geometry.point.marker": "o",
    "geometry.line.marker": "D",
    "geometry.plane.marker": "s",
    "geometry.point.nodeSize": 300,
    "geometry.line.nodeSize": 390,
    "geometry.plane.nodeSize": 480,
    "constraint.default.color": "#8B867A",
    "constraint.emphasis.color": "#B97834",
    "constraint.type.coincident.color": "#B8574E",
    "constraint.type.coincident.lineStyle": "dotted",
    "constraint.type.coincident.graphStyle": "dotted",
    "constraint.type.parallel.color": "#788C5D",
    "constraint.type.parallel.lineStyle": "dashed",
    "constraint.type.parallel.graphStyle": "dashed",
    "constraint.type.perpendicular.color": "#66738F",
    "constraint.type.perpendicular.lineStyle": "dashdot",
    "constraint.type.perpendicular.graphStyle": "dashdot",
    "constraint.type.distance.color": "#B88746",
    "constraint.type.distance.lineStyle": "solid",
    "constraint.type.distance.graphStyle": "solid",
    "constraint.type.angle.color": "#7C617B",
    "constraint.type.angle.lineStyle": (0, (3, 2)),
    "constraint.type.angle.graphStyle": "dashed",
    "rigidSet.palette.01": "#587C7A",
    "rigidSet.palette.02": "#B88746",
    "rigidSet.palette.03": "#7C617B",
    "rigidSet.palette.04": "#788C5D",
    "rigidSet.palette.05": "#C66E4E",
    "rigidSet.palette.06": "#66738F",
    "rigidSet.palette.07": "#8A8178",
    "rigidSet.palette.08": "#9A7A5F",
    "rigidSet.palette.09": "#5F7D9A",
    "rigidSet.palette.10": "#A86E73",
    "rigidSet.palette.11": "#6F8B72",
    "rigidSet.palette.12": "#9B8A5F",
    "rigidSet.palette.13": "#6E6A86",
    "rigidSet.palette.14": "#A06F4F",
    "rigidSet.palette.15": "#557D8A",
    "figure.font.sans": "Anthropic Sans, Inter, Segoe UI, Arial, sans-serif",
    "figure.font.serif": "Anthropic Serif, Georgia, Cambria, Times New Roman, serif",
    "figure.radius.panel": 8,
    "figure.radius.card": 6,
    "figure.radius.small": 4,
    "figure.radius.pill": 12,
    "figure.stroke.default": 1.1,
    "figure.stroke.grid": 1.0,
    "figure.stroke.arrow": 1.4,
    "figure.stroke.constraint": 2.4,
}

RIGID_SET_COLORS = [
    GCS_TOKENS[f"rigidSet.palette.{index:02d}"]
    for index in range(1, 16)
]

GEOMETRY_NAMES = {0: "Point", 1: "Line", 2: "Plane"}
CONSTRAINT_NAMES = {
    0: "Coincident",
    1: "Parallel",
    2: "Perpendicular",
    3: "Distance",
    4: "Angle",
}

CONSTRAINT_TYPE_TOKENS = {
    0: "constraint.type.coincident",
    1: "constraint.type.parallel",
    2: "constraint.type.perpendicular",
    3: "constraint.type.distance",
    4: "constraint.type.angle",
}

CONSTRAINT_COLORS = {
    type_id: GCS_TOKENS[f"{token}.color"]
    for type_id, token in CONSTRAINT_TYPE_TOKENS.items()
}

GEOMETRY_MARKERS = {
    0: GCS_TOKENS["geometry.point.marker"],
    1: GCS_TOKENS["geometry.line.marker"],
    2: GCS_TOKENS["geometry.plane.marker"],
}

GEOMETRY_NODE_SIZES = {
    0: GCS_TOKENS["geometry.point.nodeSize"],
    1: GCS_TOKENS["geometry.line.nodeSize"],
    2: GCS_TOKENS["geometry.plane.nodeSize"],
}

CONSTRAINT_LINE_STYLES = {
    type_id: GCS_TOKENS[f"{token}.lineStyle"]
    for type_id, token in CONSTRAINT_TYPE_TOKENS.items()
}

CONSTRAINT_GRAPH_LINE_STYLES = {
    type_id: GCS_TOKENS[f"{token}.graphStyle"]
    for type_id, token in CONSTRAINT_TYPE_TOKENS.items()
}

STATE_COLORS = {
    "focus": GCS_TOKENS["state.focus"],
    "focus_active": GCS_TOKENS["state.focus.active"],
    "selected": GCS_TOKENS["state.focus"],
    "replay_current": GCS_TOKENS["state.replay.current"],
    "solved": GCS_TOKENS["state.ok"],
    "ok": GCS_TOKENS["state.ok"],
    "info": GCS_TOKENS["state.info"],
    "warning": GCS_TOKENS["state.warning"],
    "error": GCS_TOKENS["state.error"],
    "pending": GCS_TOKENS["state.pending"],
    "violated": GCS_TOKENS["state.violation"],
}

GCS_THEME = {
    "bg_window": GCS_TOKENS["surface.paper"],
    "bg_primary": GCS_TOKENS["surface.paper"],
    "bg_panel": GCS_TOKENS["surface.panel.subtle"],
    "bg_panel_alt": GCS_TOKENS["surface.panel.muted"],
    "bg_canvas": GCS_TOKENS["surface.canvas"],
    "bg_table": GCS_TOKENS["surface.panel"],
    "bg_table_selected": GCS_TOKENS["surface.table.selected"],
    "text_primary": GCS_TOKENS["text.primary"],
    "text_secondary": GCS_TOKENS["text.secondary"],
    "text_muted": GCS_TOKENS["text.muted"],
    "text_on_accent": GCS_TOKENS["text.inverse"],
    "accent": STATE_COLORS["focus"],
    "accent_active": STATE_COLORS["focus_active"],
    "info": STATE_COLORS["info"],
    "success": STATE_COLORS["solved"],
    "warning": STATE_COLORS["warning"],
    "error": STATE_COLORS["error"],
    "border": GCS_TOKENS["rule.default"],
    "border_strong": GCS_TOKENS["rule.strong"],
    "grid": GCS_TOKENS["rule.soft"],
    "axis": GCS_TOKENS["rule.axis"],
    "constraint_default": GCS_TOKENS["constraint.default.color"],
}
