from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional
import json
import copy


class GeometryType(IntEnum):
    Point = 0
    Line = 1
    Plane = 2


class ConstraintType(IntEnum):
    Coincident = 0
    Parallel = 1
    Perpendicular = 2
    Distance = 3
    Angle = 4


VALID_CONSTRAINT_SIGNATURES = {
    ConstraintType.Coincident: [
        (GeometryType.Point, GeometryType.Point),
        (GeometryType.Point, GeometryType.Line),
        (GeometryType.Point, GeometryType.Plane),
    ],
    ConstraintType.Parallel: [
        (GeometryType.Line, GeometryType.Line),
        (GeometryType.Line, GeometryType.Plane),
        (GeometryType.Plane, GeometryType.Plane),
    ],
    ConstraintType.Perpendicular: [
        (GeometryType.Line, GeometryType.Line),
        (GeometryType.Line, GeometryType.Plane),
        (GeometryType.Plane, GeometryType.Plane),
    ],
    ConstraintType.Distance: [
        (GeometryType.Point, GeometryType.Point),
        (GeometryType.Point, GeometryType.Line),
        (GeometryType.Point, GeometryType.Plane),
        (GeometryType.Line, GeometryType.Line),
        (GeometryType.Line, GeometryType.Plane),
        (GeometryType.Plane, GeometryType.Plane),
    ],
    ConstraintType.Angle: [
        (GeometryType.Line, GeometryType.Line),
        (GeometryType.Line, GeometryType.Plane),
        (GeometryType.Plane, GeometryType.Plane),
    ],
}

DOF_GEOMETRY = {GeometryType.Point: 3, GeometryType.Line: 6, GeometryType.Plane: 6}
DOF_REMOVED_CONSTRAINT = {
    ConstraintType.Coincident: 3,
    ConstraintType.Parallel: 2,
    ConstraintType.Perpendicular: 1,
    ConstraintType.Distance: 1,
    ConstraintType.Angle: 1,
}


@dataclass
class RigidSet:
    id: int
    geometry_ids: List[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"id": self.id, "geometry_ids": list(self.geometry_ids)}

    @classmethod
    def from_dict(cls, d: dict) -> "RigidSet":
        return cls(id=d["id"], geometry_ids=list(d.get("geometry_ids", [])))


@dataclass
class Geometry:
    id: int
    type: GeometryType
    rigid_set_id: int
    v: List[float] = field(default_factory=lambda: [0.0] * 6)

    def to_dict(self) -> dict:
        return {"id": self.id, "type": int(self.type), "rigid_set_id": self.rigid_set_id, "v": list(self.v)}

    @classmethod
    def from_dict(cls, d: dict) -> "Geometry":
        return cls(id=d["id"], type=GeometryType(d["type"]), rigid_set_id=d["rigid_set_id"], v=list(d.get("v", [0.0] * 6)))


@dataclass
class Constraint:
    id: int
    type: ConstraintType
    geometry_ids: List[int] = field(default_factory=list)
    value: float = 0.0

    def to_dict(self) -> dict:
        return {"id": self.id, "type": int(self.type), "geometry_ids": list(self.geometry_ids), "value": self.value}

    @classmethod
    def from_dict(cls, d: dict) -> "Constraint":
        return cls(id=d["id"], type=ConstraintType(d["type"]), geometry_ids=list(d.get("geometry_ids", [])), value=d.get("value", 0.0))


@dataclass
class GCSGraph:
    rigid_sets: List[RigidSet] = field(default_factory=list)
    geometries: List[Geometry] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    history: List[dict] = field(default_factory=list)

    def find_geometry(self, gid: int) -> Optional[Geometry]:
        for g in self.geometries:
            if g.id == gid:
                return g
        return None

    def find_constraint(self, cid: int) -> Optional[Constraint]:
        for c in self.constraints:
            if c.id == cid:
                return c
        return None

    def find_rigid_set(self, rsid: int) -> Optional[RigidSet]:
        for rs in self.rigid_sets:
            if rs.id == rsid:
                return rs
        return None

    def next_rigid_set_id(self) -> int:
        if not self.rigid_sets:
            return 0
        return max(rs.id for rs in self.rigid_sets) + 1

    def next_geometry_id(self) -> int:
        if not self.geometries:
            return 0
        return max(g.id for g in self.geometries) + 1

    def next_constraint_id(self) -> int:
        if not self.constraints:
            return 0
        return max(c.id for c in self.constraints) + 1

    def add_rigid_set(self, rs_id: Optional[int] = None) -> RigidSet:
        if rs_id is None:
            rs_id = self.next_rigid_set_id()
        rs = RigidSet(id=rs_id)
        self.rigid_sets.append(rs)
        return rs

    def add_geometry(self, geom_type: GeometryType, rigid_set_id: int, v: Optional[List[float]] = None, geom_id: Optional[int] = None) -> Geometry:
        if geom_id is None:
            geom_id = self.next_geometry_id()
        g = Geometry(id=geom_id, type=geom_type, rigid_set_id=rigid_set_id, v=v or [0.0] * 6)
        self.geometries.append(g)
        rs = self.find_rigid_set(rigid_set_id)
        if rs and geom_id not in rs.geometry_ids:
            rs.geometry_ids.append(geom_id)
        return g

    def add_constraint(self, ctype: ConstraintType, geometry_ids: List[int], value: float = 0.0, cid: Optional[int] = None) -> Constraint:
        if cid is None:
            cid = self.next_constraint_id()
        c = Constraint(id=cid, type=ctype, geometry_ids=geometry_ids, value=value)
        self.constraints.append(c)
        return c

    def remove_rigid_set(self, rs_id: int) -> bool:
        rs = self.find_rigid_set(rs_id)
        if rs is None:
            return False
        self.geometries = [g for g in self.geometries if g.rigid_set_id != rs_id]
        self.constraints = [c for c in self.constraints if not any(gid in rs.geometry_ids for gid in c.geometry_ids)]
        self.rigid_sets = [r for r in self.rigid_sets if r.id != rs_id]
        return True

    def remove_geometry(self, gid: int) -> bool:
        g = self.find_geometry(gid)
        if g is None:
            return False
        rs = self.find_rigid_set(g.rigid_set_id)
        if rs:
            rs.geometry_ids = [i for i in rs.geometry_ids if i != gid]
        self.constraints = [c for c in self.constraints if gid not in c.geometry_ids]
        self.geometries = [ge for ge in self.geometries if ge.id != gid]
        return True

    def remove_constraint(self, cid: int) -> bool:
        self.constraints = [c for c in self.constraints if c.id != cid]
        return True

    def compute_dof(self) -> int:
        geom_dof = sum(DOF_GEOMETRY.get(g.type, 0) for g in self.geometries)
        constraint_dof = sum(DOF_REMOVED_CONSTRAINT.get(c.type, 0) for c in self.constraints)
        return geom_dof - constraint_dof

    def classify_dof_status(self) -> str:
        if not self.geometries:
            return "Empty"
        dof = self.compute_dof()
        n_rs = len(self.rigid_sets)
        if n_rs <= 1:
            if dof == 6:
                return "WellConstrained"
            elif dof > 6:
                return "UnderConstrained"
            else:
                return "OverConstrained"
        else:
            if dof == 0:
                return "WellConstrained"
            elif dof > 0:
                return "UnderConstrained"
            else:
                return "OverConstrained"

    def validate_constraint_signature(self, c: Constraint) -> bool:
        if len(c.geometry_ids) < 2:
            return False
        g1 = self.find_geometry(c.geometry_ids[0])
        g2 = self.find_geometry(c.geometry_ids[1])
        if g1 is None or g2 is None:
            return False
        valid = VALID_CONSTRAINT_SIGNATURES.get(c.type, [])
        return (g1.type, g2.type) in valid or (g2.type, g1.type) in valid

    def to_dict(self) -> dict:
        return {
            "format_version": 1,
            "rigid_sets": [rs.to_dict() for rs in self.rigid_sets],
            "geometries": [g.to_dict() for g in self.geometries],
            "constraints": [c.to_dict() for c in self.constraints],
            "history": list(self.history),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GCSGraph":
        graph = cls()
        graph.rigid_sets = [RigidSet.from_dict(rs) for rs in d.get("rigid_sets", [])]
        graph.geometries = [Geometry.from_dict(g) for g in d.get("geometries", [])]
        graph.constraints = [Constraint.from_dict(c) for c in d.get("constraints", [])]
        graph.history = list(d.get("history", []))
        return graph

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "GCSGraph":
        return cls.from_dict(json.loads(json_str))

    def deep_copy(self) -> "GCSGraph":
        return copy.deepcopy(self)


def read_graph_file(path: str) -> GCSGraph:
    if path.endswith(".json"):
        return read_graph_json(path)
    with open(path, "r") as f:
        tokens = f.read().replace("\r", "").split()
    idx = 0

    def next_int():
        nonlocal idx
        val = int(tokens[idx])
        idx += 1
        return val

    def next_float():
        nonlocal idx
        val = float(tokens[idx])
        idx += 1
        return val

    graph = GCSGraph()
    num_rigid = next_int()
    for _ in range(num_rigid):
        rs_id = next_int()
        graph.rigid_sets.append(RigidSet(id=rs_id))

    num_geom = next_int()
    for _ in range(num_geom):
        gid = next_int()
        type_int = next_int()
        rs_id = next_int()
        g = Geometry(id=gid, type=GeometryType(type_int), rigid_set_id=rs_id)
        graph.geometries.append(g)
        rs = graph.find_rigid_set(rs_id)
        if rs is not None:
            rs.geometry_ids.append(gid)

    num_const = next_int()
    for _ in range(num_const):
        cid = next_int()
        type_int = next_int()
        num_conn = next_int()
        gids = [next_int() for _ in range(num_conn)]
        c = Constraint(id=cid, type=ConstraintType(type_int), geometry_ids=gids)
        graph.constraints.append(c)

    for _ in range(len(graph.geometries)):
        gid = next_int()
        g = graph.find_geometry(gid)
        if g is not None:
            for k in range(6):
                g.v[k] = next_float()

    while idx < len(tokens):
        cid = next_int()
        val = next_float()
        c = graph.find_constraint(cid)
        if c is not None:
            c.value = val

    return graph


def write_graph_file(graph: GCSGraph, path: str):
    if path.endswith(".json"):
        write_graph_json(graph, path)
        return
    with open(path, "w") as f:
        f.write(f"{len(graph.rigid_sets)}\n")
        rs_ids = " ".join(str(rs.id) for rs in graph.rigid_sets)
        f.write(f"{rs_ids}\n")

        f.write(f"{len(graph.geometries)}\n")
        for g in graph.geometries:
            f.write(f"{g.id} {int(g.type)} {g.rigid_set_id}\n")

        f.write(f"{len(graph.constraints)}\n")
        for c in graph.constraints:
            gids = " ".join(str(gid) for gid in c.geometry_ids)
            f.write(f"{c.id} {int(c.type)} {len(c.geometry_ids)} {gids}\n")

        f.write("\n")
        for g in graph.geometries:
            vals = " ".join(str(v) for v in g.v)
            f.write(f"{g.id} {vals}\n")

        f.write("\n")
        for c in graph.constraints:
            f.write(f"{c.id} {c.value}\n")


def read_graph_json(path: str) -> GCSGraph:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return GCSGraph.from_dict(data)


def write_graph_json(graph: GCSGraph, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(graph.to_dict(), f, indent=2, ensure_ascii=False)
        f.write("\n")
