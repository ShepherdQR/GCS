# 5. Phase 1 推荐工具集

## 5.1 Tool 1：`generate_skeleton_graph`

生成一个普通图 skeleton。

### 输入

```json
{
  "num_vertices": 12,
  "target_property": "vertex_biconnected",
  "method": "cycle_plus_chords",
  "extra_edges": 6,
  "seed": 42
}
```

### 输出

```json
{
  "graph_id": "skeleton_001",
  "num_vertices": 12,
  "edges": [
    [0, 1],
    [1, 2],
    [2, 3]
  ],
  "generation_certificate": {
    "base": "cycle",
    "augmentation": "added_chords",
    "property_preserved": "adding_edges_preserves_vertex_biconnectivity"
  }
}
```

这个工具只生成普通图，不生成 GCS。

推荐最初使用：

```text
cycle + random chords
```

因为：

1. n-cycle 对 n ≥ 3 是点双连通；
2. 添加边不会破坏点双连通；
3. 因此生成器天然有 correctness certificate。

更高级的生成方法可以用：

```text
ear decomposition
```

因为经典结果是：

> 一个 2-vertex-connected graph 可以从一个 cycle 通过逐步添加 ears 得到。

因此你们可以有两个 generator mode：

```text
cycle_plus_chords
ear_decomposition
```

---

## 5.2 Tool 2：`lift_skeleton_to_gcs`

把普通图 skeleton 提升为 GCS constraint graph。

### 输入

```json
{
  "skeleton_graph_id": "skeleton_001",
  "geometry_type_policy": {
    "allowed_types": ["Point", "Line", "Plane"],
    "distribution": {
      "Point": 0.6,
      "Line": 0.3,
      "Plane": 0.1
    }
  },
  "constraint_type_policy": {
    "allowed_types": ["Distance", "Coincident", "Parallel", "Perpendicular", "Angle"],
    "respect_type_signature": true
  },
  "rigid_set_policy": {
    "num_rigid_sets": 3,
    "assignment": "random_balanced"
  },
  "seed": 43
}
```

### 输出

```json
{
  "gcs_graph_id": "gcs_001",
  "num_rigid_sets": 3,
  "num_geometries": 12,
  "num_constraints": 18,
  "status": "constructed"
}
```

这个工具的职责是：

```text
普通图边  ->  GCS constraint
普通图 vertex  ->  Geometry
Geometry 分配到 RigidSet
根据 Geometry type 选择合法 Constraint type
```

例如：

```text
edge (G1, G2)
```

可以变成：

```text
Constraint C7 connects G1, G2
type = Distance
```

但必须检查 type signature。

---

## 5.3 Tool 3：`project_gcs_graph`

把 GCS 图投影为普通图。

### 输入

```json
{
  "gcs_graph_id": "gcs_001",
  "projection": "geometry_primal"
}
```

### 输出

```json
{
  "projected_graph_id": "proj_001",
  "vertices": [0, 1, 2, 3],
  "edges": [[0, 1], [1, 2], [2, 3], [3, 0]],
  "projection_rule": "geometries sharing one constraint are connected"
}
```

建议支持三种 projection：

```text
geometry_primal
incidence_bipartite
rigidset_quotient
```

但 Phase 1 先只要求：

```text
geometry_primal
```

---

## 5.4 Tool 4：`check_vertex_biconnected`

检查普通图是否点双连通。

### 输入

```json
{
  "projected_graph_id": "proj_001"
}
```

### 输出

```json
{
  "is_vertex_biconnected": true,
  "num_connected_components": 1,
  "articulation_points": [],
  "biconnected_components": [
    {
      "id": 0,
      "vertices": [0, 1, 2, 3, 4, 5],
      "edges": [[0, 1], [1, 2]]
    }
  ],
  "certificate": {
    "algorithm": "Tarjan articulation point / biconnected components",
    "root_children_condition_satisfied": true,
    "lowlink_conditions_satisfied": true
  }
}
```

这个工具是核心 verifier。

agent 生成图之后，必须调用这个工具。
不能让 agent 自己判断图是否点双连通。

---

## 5.5 Tool 5：`validate_gcs_schema`

检查 GCS 数据结构合法性。

### 输入

```json
{
  "gcs_graph_id": "gcs_001"
}
```

### 输出

```json
{
  "valid": false,
  "violations": [
    {
      "type": "invalid_constraint_signature",
      "constraint_id": 7,
      "geometry_ids": [2, 5],
      "message": "Parallel constraint requires line-line, line-plane, or plane-plane signature."
    }
  ]
}
```

检查内容包括：

```text
id 唯一性
Geometry 是否属于某个 RigidSet
Constraint 引用的 Geometry 是否存在
Constraint arity 是否合法
Constraint type signature 是否合法
Line 是否退化
Plane normal 是否非零
Distance 是否非负
Angle 是否在合法范围内
```

---

## 5.6 Tool 6：`repair_gcs_graph`

修复不满足条件的图。

### 输入

```json
{
  "gcs_graph_id": "gcs_001",
  "target_repairs": [
    "fix_constraint_signature",
    "make_geometry_primal_vertex_biconnected"
  ],
  "repair_policy": "minimal_change"
}
```

### 输出

```json
{
  "repaired_gcs_graph_id": "gcs_001_repaired",
  "edits": [
    {
      "operation": "replace_constraint_type",
      "constraint_id": 7,
      "old_type": "Parallel",
      "new_type": "Angle"
    },
    {
      "operation": "add_constraint",
      "new_constraint_id": 18,
      "geometry_ids": [3, 8],
      "constraint_type": "Distance"
    }
  ],
  "repair_certificate": {
    "policy": "minimal_change",
    "post_validation_required": true
  }
}
```

Phase 1 可以先不追求最小修复，只要求修复后通过 verifier。

---

## 5.7 Tool 7：`serialize_gcs_graph`

输出你们定义的 GCS serialization。

### 输入

```json
{
  "gcs_graph_id": "gcs_001",
  "format": "custom_text_v1"
}
```

### 输出

```json
{
  "serialization": "...",
  "checksum": "abc123",
  "canonical": true
}
```

建议加入 canonical serialization。
否则同一个图可以有很多文本表示，后续测试很麻烦。

---

## 5.8 Tool 8：`generate_graph_report`

生成机器可读报告，不是自然语言报告。

### 输入

```json
{
  "gcs_graph_id": "gcs_001",
  "include": [
    "schema_validation",
    "projection_statistics",
    "biconnectivity_certificate",
    "constraint_type_histogram",
    "rigidset_summary"
  ]
}
```

### 输出

```json
{
  "graph_id": "gcs_001",
  "summary": {
    "num_rigid_sets": 3,
    "num_geometries": 12,
    "num_constraints": 18
  },
  "schema_valid": true,
  "geometry_primal_biconnected": true,
  "articulation_points": [],
  "constraint_type_histogram": {
    "Distance": 10,
    "Coincident": 3,
    "Parallel": 2,
    "Angle": 3
  }
}
```

agent 最后基于这个 report 写人类可读解释。

---

## 5.9 Tool 9：`assign_geometry_parameters`

为 GCS 图中的 Geometry 分配具体的坐标/参数值，以及为 Constraint 分配合理的约束值。

### 输入

```json
{
  "gcs_graph_id": "gcs_001",
  "layout": "circular",
  "layout_params": {
    "radius": 2.0,
    "center": [0, 0, 0],
    "plane": "xy"
  },
  "seed": 44
}
```

### 输出

```json
{
  "gcs_graph_id": "gcs_001",
  "geometries": [
    {
      "id": 0,
      "type": "Point",
      "rigid_set_id": 0,
      "v": [2.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    },
    {
      "id": 1,
      "type": "Line",
      "rigid_set_id": 1,
      "v": [1.0, 1.732, 0.0, 1.0, 2.732, 0.0]
    }
  ],
  "constraints": [
    {
      "id": 0,
      "type": "Distance",
      "geometry_ids": [0, 1],
      "value": 2.5
    }
  ],
  "status": "parameters_assigned"
}
```

这个工具的职责是：

```text
根据图的拓扑结构，为每个 Geometry 分配合理的参数值
  Point  -> (x, y, z, 0, 0, 0)
  Line   -> (x1, y1, z1, x2, y2, z2)  确保起点 != 终点
  Plane  -> (x, y, z, nx, ny, nz)      确保法向量 != 0

根据约束类型和连接的 Geometry 坐标，计算合理的约束值
  Distance -> 计算实际距离
  Angle    -> 计算实际角度
  其他     -> value = 0.0
```

支持的 layout 策略：

```text
circular    按环状排列（默认，适合点双连通图）
random      随机分散
grid        网格排列
```

这个工具应在 `lift_skeleton_to_gcs` 之后、`validate_gcs_schema` 之前调用。
它解决的核心问题是：`lift_skeleton_to_gcs` 只生成拓扑结构，所有参数为 0，
导致 Line 退化、Plane 法向量为零等 schema 违规。
通过此工具分配参数后，GCS 图应能通过 `validate_gcs_schema` 检查。

---
