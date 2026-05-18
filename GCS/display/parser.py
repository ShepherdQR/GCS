import os
from model.graph import (
    GeometryType,
    ConstraintType,
    RigidSet,
    Geometry,
    Constraint,
    Manager,
)


def read_graph(path: str) -> Manager:
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

    manager = Manager()

    num_rigid = next_int()
    for _ in range(num_rigid):
        rs_id = next_int()
        manager.rigid_sets.append(RigidSet(id=rs_id))

    num_geom = next_int()
    for _ in range(num_geom):
        gid = next_int()
        type_int = next_int()
        rs_id = next_int()
        g = Geometry(id=gid, type=GeometryType(type_int), rigid_set_id=rs_id)
        manager.geometries.append(g)
        rs = manager.find_rigid_set(rs_id)
        if rs is not None:
            rs.geometry_ids.append(gid)

    num_const = next_int()
    for _ in range(num_const):
        cid = next_int()
        type_int = next_int()
        num_conn = next_int()
        gids = [next_int() for _ in range(num_conn)]
        c = Constraint(id=cid, type=ConstraintType(type_int), geometry_ids=gids)
        manager.constraints.append(c)

    for _ in range(len(manager.geometries)):
        gid = next_int()
        g = manager.find_geometry(gid)
        if g is not None:
            for k in range(6):
                g.v[k] = next_float()

    while idx < len(tokens):
        cid = next_int()
        val = next_float()
        c = manager.find_constraint(cid)
        if c is not None:
            c.value = val

    return manager


def dump_graph(manager: Manager, input_path: str) -> str:
    if not input_path:
        return ""

    base = os.path.basename(input_path)
    name, _ = os.path.splitext(base)
    out_name = name + "_graph.txt"

    out_dir = os.path.join(os.path.dirname(input_path), "..", "x64", "Debug")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, out_name)

    with open(out_path, "w") as f:
        f.write(f"{len(manager.rigid_sets)}\n")
        rs_ids = " ".join(str(rs.id) for rs in manager.rigid_sets)
        f.write(f"{rs_ids}\n")

        f.write(f"{len(manager.geometries)}\n")
        for g in manager.geometries:
            f.write(f"{g.id} {int(g.type)} {g.rigid_set_id}\n")

        f.write(f"{len(manager.constraints)}\n")
        for c in manager.constraints:
            gids = " ".join(str(gid) for gid in c.geometry_ids)
            f.write(f"{c.id} {int(c.type)} {len(c.geometry_ids)} {gids}\n")

        f.write("\n")
        for g in manager.geometries:
            vals = " ".join(f"{v}" for v in g.v)
            f.write(f"{g.id} {vals}\n")

        f.write("\n")
        for c in manager.constraints:
            f.write(f"{c.id} {c.value}\n")

    return out_path


def print_summary(manager: Manager):
    print(f"Rigid Sets ({len(manager.rigid_sets)}):")
    for rs in manager.rigid_sets:
        gids = " ".join(str(gid) for gid in rs.geometry_ids)
        print(f"  RS id={rs.id} geometries: {gids}")

    print(f"Geometries ({len(manager.geometries)}):")
    for g in manager.geometries:
        from model.graph import type_name_geometry
        vals = " ".join(f"{v}" for v in g.v)
        print(f"  G id={g.id} type={type_name_geometry(g.type)} rs={g.rigid_set_id} values: {vals}")

    print(f"Constraints ({len(manager.constraints)}):")
    for c in manager.constraints:
        from model.graph import type_name_constraint
        gids = " ".join(str(gid) for gid in c.geometry_ids)
        print(f"  C id={c.id} type={type_name_constraint(c.type)} connects: {gids} value={c.value}")
