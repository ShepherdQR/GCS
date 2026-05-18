from enum import IntEnum
from dataclasses import dataclass, field


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


@dataclass
class RigidSet:
    id: int
    geometry_ids: list = field(default_factory=list)


@dataclass
class Geometry:
    id: int
    type: GeometryType
    rigid_set_id: int
    v: list = field(default_factory=lambda: [0.0] * 6)


@dataclass
class Constraint:
    id: int
    type: ConstraintType
    geometry_ids: list = field(default_factory=list)
    value: float = 0.0


@dataclass
class Manager:
    rigid_sets: list = field(default_factory=list)
    geometries: list = field(default_factory=list)
    constraints: list = field(default_factory=list)

    def find_geometry(self, gid: int):
        for g in self.geometries:
            if g.id == gid:
                return g
        return None

    def find_constraint(self, cid: int):
        for c in self.constraints:
            if c.id == cid:
                return c
        return None

    def find_rigid_set(self, rsid: int):
        for rs in self.rigid_sets:
            if rs.id == rsid:
                return rs
        return None

    def geometries_in_rigid_set(self, rsid: int):
        rs = self.find_rigid_set(rsid)
        if rs is None:
            return []
        return [self.find_geometry(gid) for gid in rs.geometry_ids]


def type_name_geometry(t: GeometryType) -> str:
    names = {
        GeometryType.Point: "Point",
        GeometryType.Line: "Line",
        GeometryType.Plane: "Plane",
    }
    return names.get(t, "Unknown")


def type_name_constraint(t: ConstraintType) -> str:
    names = {
        ConstraintType.Coincident: "Coincident",
        ConstraintType.Parallel: "Parallel",
        ConstraintType.Perpendicular: "Perpendicular",
        ConstraintType.Distance: "Distance",
        ConstraintType.Angle: "Angle",
    }
    return names.get(t, "Unknown")


def dof_geometry(t: GeometryType) -> int:
    dof_map = {
        GeometryType.Point: 3,
        GeometryType.Line: 6,
        GeometryType.Plane: 6,
    }
    return dof_map.get(t, 0)


def dof_removed_constraint(t: ConstraintType) -> int:
    removed_map = {
        ConstraintType.Coincident: 3,
        ConstraintType.Parallel: 2,
        ConstraintType.Perpendicular: 1,
        ConstraintType.Distance: 1,
        ConstraintType.Angle: 1,
    }
    return removed_map.get(t, 0)
