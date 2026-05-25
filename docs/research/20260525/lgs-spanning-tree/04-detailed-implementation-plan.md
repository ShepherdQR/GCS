# LGS Spanning-Tree Method Detailed Implementation Plan For GCS

Date: 2026-05-25
Status: proposed detailed plan
Owner: `gcs-decomposition-planning-steward`
Architecture reviewers: `gcs-architecture-steward`, `gcs-constraint-semantics-steward`, `gcs-numeric-engine-steward`, `gcs-diagnostics-certification-steward`, `gcs-quality-steward`

## 目标

把 LGS 论文中的 spanning-tree modeling method 转化为 GCS 中可验证、可回滚、可逐步实现的 planner strategy。

目标不是一次性复刻 LGS 3D。目标是先建立一种保守的 GCS 实现路线：

```text
rigid-set incidence facts
  -> rigid-set pair constraint grouping
  -> pattern-supported absorbed constraints
  -> maximum-weight spanning forest
  -> explicit closure residual set
  -> optional reduced NumericTask
  -> diagnostics revalidation
  -> runtime commit only after ordinary verification
```

## 关键结论

1. 先做 contract-only planner evidence，不立刻改变数值求解。
2. tree edge 上的 constraint 只有在 pattern 明确支持并能生成安全 parameterization 时才可以被 absorbed。
3. 非 tree edge 或 unsupported pattern 必须进入 closure residual set，或者返回 `UnsupportedPlanReport`。
4. 所有 active constraints 必须在报告中被 partition 成 exactly one of:
   - `absorbed_constraints`
   - `closure_constraints`
   - `unsupported_constraints`
5. numeric engine 只能消费 planner 输出的 reduced task，不拥有 spanning-tree planning policy。
6. diagnostics 必须重新验证 absorbed constraints 和 closure residuals，不能把 planner evidence 当成最终正确性证明。

## 当前完成状态确认

`rigid-set spanning-tree plan contracts` 尚未完成。当前仓库状态是：

- 已完成：LGS spanning-tree paper analysis、GCS adoption proposal、feasibility analysis、本文详细实施计划。
- 未完成：`RigidSetSpanningForestPlan` 或等价 planner contract 类型尚未进入 `src/gcs/decomposition_planner/`。
- 未完成：`SpanningTreePattern` 或等价 pattern metadata 尚未进入 `src/gcs/constraint_catalog/`。
- 未完成：rigid-set pair constraint grouping、maximum-weight spanning forest builder、absorbed/closure/unsupported partition validator 尚未实现。
- 未完成：相关 contract tests 尚未加入 `tests/contracts/*`。

确认方式：

```bat
rg -n "RigidSetSpanning|SpanningTreePattern|spanning_tree|absorbed_constraint|closure_constraint|RigidSetTreeEdge" src tests docs\research\20260525\lgs-spanning-tree
```

观察结果：命中只出现在 `docs/research/20260525/lgs-spanning-tree/` 的研究和计划文档中，没有出现在 `src/` 或 `tests/`。因此 contracts 仍是下一步任务，不是本次已完成实现。

## 非目标

- 不在第一阶段修改 solver runtime commit 语义。
- 不在第一阶段实现完整 LGS 3D pattern catalog。
- 不把 Euler angle 或某个 rotation order 固化为公开长期契约。
- 不把 spanning tree 误称为 tree-decomposable constructibility proof。
- 不让 planner 计算 residual 或 Jacobian。
- 不让 numeric engine 决定哪些 constraints 可以从 residual system 中删除。
- 不做 hidden fallback。任何 fallback 必须成为结构化 report evidence。

## 现有依据

| Path | 用途 |
| --- | --- |
| `docs/research/papers/LGS/ershov.pdf` | LGS spanning-tree modeling primary source |
| `docs/research/20260525/lgs-spanning-tree/01-paper-analysis.md` | paper analysis |
| `docs/research/20260525/lgs-spanning-tree/02-gcs-adoption-proposal.md` | architecture proposal |
| `docs/research/20260525/lgs-spanning-tree/03-feasibility-analysis.md` | feasibility analysis |
| `docs/architecture/20-solver-pipeline/decomposition-planning.md` | planner boundary |
| `docs/architecture/30-contracts/solver-contracts.md` | planner, numeric, diagnostics, runtime contracts |
| `src/gcs/decomposition_planner/` | current planner surface |
| `src/gcs/incidence_graph/` | current incidence and rigid-body graph surface |
| `src/gcs/constraint_catalog/` | current constraint definition and validation surface |
| `src/gcs/numeric_engine/` | current `NumericTask` and report surface |

## 总体里程碑

| Milestone | 名称 | 目标 | 是否改变求解行为 |
| --- | --- | --- | --- |
| M1 | Contract-only tree plan | 增加 spanning-tree plan evidence 和 tests | No |
| M2 | Pattern catalog v0 | 声明极小安全 pattern 集合 | No |
| M3 | Fixture corpus | 生成 chain/cycle/unsupported fixtures | No |
| M4 | Reduced task prototype | 生成 reduced `NumericTask`，可先不作为默认路径 | Limited opt-in |
| M5 | Diagnostics revalidation | re-check absorbed/closure constraints | Yes, opt-in |
| M6 | Empirical gate | 比较维度、残差、rank、时间、成功率 | No product default |
| M7 | Production decision | 决定默认策略、fallback、长期 API | Possible |

## M1: Contract-Only Tree Plan

### 目标

让 GCS 能在不改变 numeric solve 的前提下，生成并验证一个 rigid-set spanning forest plan。

### 输入

- `ModelSnapshot`
- `IncidenceIndices`
- `RigidBodyGraph`
- `SolveIntent`
- optional diagnostic hints

### 输出

新增 planner evidence，不影响当前 `CoverPlan` 的基本行为：

```text
RigidSetSpanningForestPlan
  nodes
  candidate_edges
  selected_tree_edges
  absorbed_constraint_ids
  closure_constraint_ids
  unsupported_constraint_ids
  root_rigid_set_ids
  deterministic_tie_break_trace
  pattern_report
  unsupported_report
```

### 建议契约草案

```cpp
struct SpanningTreePatternId {
    std::string value;
};

enum class SpanningTreeConstraintDisposition {
    absorbed_by_tree_pattern,
    closure_residual,
    unsupported,
};

struct RigidSetPairConstraintGroup {
    kernel::RigidSetId first_rigid_set_id;
    kernel::RigidSetId second_rigid_set_id;
    std::vector<kernel::ConstraintId> constraint_ids;
};

struct SpanningTreePatternMatch {
    SpanningTreePatternId pattern_id;
    kernel::RigidSetId parent_rigid_set_id;
    kernel::RigidSetId child_rigid_set_id;
    std::vector<kernel::ConstraintId> absorbed_constraint_ids;
    std::vector<kernel::ConstraintId> closure_constraint_ids;
    std::vector<kernel::ConstraintId> unsupported_constraint_ids;
    int removed_rotational_dof;
    int removed_translational_dof;
    int weight;
    bool supported;
    std::string unsupported_code;
};

struct RigidSetTreeEdge {
    int edge_id;
    kernel::RigidSetId parent_rigid_set_id;
    kernel::RigidSetId child_rigid_set_id;
    SpanningTreePatternMatch pattern_match;
};

struct RigidSetSpanningForestPlan {
    std::vector<kernel::RigidSetId> rigid_set_ids;
    std::vector<RigidSetTreeEdge> selected_edges;
    std::vector<kernel::ConstraintId> absorbed_constraint_ids;
    std::vector<kernel::ConstraintId> closure_constraint_ids;
    std::vector<kernel::ConstraintId> unsupported_constraint_ids;
    kernel::StageReport report;
};
```

这些类型可放在 `decomposition_planner`，但 pattern metadata 本身应由 `constraint_catalog` 或其相邻语义层提供。

### 详细任务

1. 在 `incidence_graph` 中补齐 rigid-set pair grouping。
   - 输入为 validated `ModelSnapshot`。
   - constraint 的 entity subjects 如果跨多个 rigid set，则进入 pair group。
   - same-rigid-set constraints 不应成为 tree edge candidate。
   - malformed or missing rigid-set references 生成 typed report。

2. 在 `decomposition_planner` 中实现 deterministic candidate edge construction。
   - 每个 rigid-set pair group 产生一个 candidate edge。
   - edge weight 来自 pattern match 的 removed DOF。
   - unsupported group 的 weight 为 0 或不参与 tree selection，但 constraints 必须进入 closure/unsupported evidence。

3. 实现 maximum-weight spanning forest builder。
   - 允许 disconnected graph，输出 forest。
   - 使用 deterministic Kruskal 或 equivalent algorithm。
   - sort key:
     - higher weight first;
     - lower first rigid-set id;
     - lower second rigid-set id;
     - lexical pattern id;
     - lower smallest constraint id。
   - 记录 tie-break trace，方便测试和 report。

4. 将 forest plan 挂到 `PlannerOutput`。
   - 第一阶段可作为新字段或 `StageReport` evidence，不改变 numeric task。
   - `CoverPlan` 仍保持当前 component/whole-model strategy。
   - plan report 必须明确说明 `not_used_for_numeric_task_yet`。

5. 增加 validation tool。
   - 验证每个 active constraint 出现在 exactly one disposition。
   - 验证 tree edges acyclic。
   - 验证每个 selected tree edge 有 supported pattern。
   - 验证 unsupported constraints 产生 report code。

### M1 验收测试

新增或扩展 `tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp`：

- `planner_groups_constraints_by_rigid_set_pair_deterministically`
- `planner_spanning_forest_selects_maximum_weight_edges`
- `planner_spanning_forest_tie_break_is_deterministic`
- `planner_spanning_forest_keeps_cycle_edges_as_closure_constraints`
- `planner_spanning_forest_partitions_every_active_constraint_once`
- `planner_spanning_forest_reports_unsupported_pattern`
- `planner_spanning_forest_does_not_change_existing_component_cover_behavior`

### M1 完成定义

- Contract tests pass。
- Current planner behavior unchanged unless explicitly inspecting new tree-plan evidence。
- No numeric behavior change。
- No lower module imports boundary modules。

## M2: Pattern Catalog V0

### 目标

定义极小、保守、可测试的 spanning-tree pattern catalog。

### 原则

- Pattern 是 constraint semantics 的一部分，不是 planner 私有技巧。
- Pattern 必须声明:
  - supported constraint kinds;
  - required geometry signatures;
  - direction sensitivity;
  - removed rotational/translational DOF;
  - absorbed residual dimension;
  - unsupported and degeneracy codes;
  - canonical transform availability。

### 建议 v0 pattern

只选择最容易证明、fixture 简单、方向歧义少的 pattern。最终集合需要由 `gcs-constraint-semantics-steward` 审查。

候选:

1. `parallel` between line/plane-like entities across two rigid sets。
2. `distance` between point-like subjects across two rigid sets。
3. `coincident` between point-like subjects across two rigid sets。

如果当前 entity model 不足以表达 LGS 论文中的 plane-plane distance 或 line-line coincidence canonical rules，则不要把这些作为 v0。

### 详细任务

1. 增加 pattern definition table。
2. 增加 pattern matcher。
3. 增加 child/parent orientation selector。
4. 为 unsupported signatures 生成 stable report code。
5. 为 same-rigid-set or malformed cases 生成 stable report code。

### M2 report code 草案

```text
planner.spanning_tree.pattern_supported
planner.spanning_tree.pattern_unsupported
planner.spanning_tree.same_rigid_set_not_tree_edge
planner.spanning_tree.direction_unsupported
planner.spanning_tree.canonical_position_unsupported
planner.spanning_tree.constraint_left_as_closure_residual
```

### M2 验收测试

- `catalog_declares_spanning_tree_pattern_metadata`
- `pattern_match_rejects_wrong_geometry_signature`
- `pattern_match_rejects_same_rigid_set_constraints`
- `pattern_match_reports_direction_sensitive_unsupported_case`
- `pattern_match_reports_removed_dof_and_absorbed_constraints`

### M2 完成定义

- Pattern metadata 是版本化、可测试、可报告的。
- Planner 只消费 pattern capability，不硬编码几何语义。
- Unsupported pattern 不会进入 absorbed set。

## M3: Fixture Corpus

### 目标

建立最小 fixture corpus，用来证明 contract-only plan 和后续 reduced numeric task。

### Fixture classes

1. two rigid sets, one supported tree constraint。
2. three rigid sets, cycle with one closure constraint。
3. disconnected forest with two components。
4. unsupported pattern case。
5. same-rigid-set constraint case。
6. over-constrained pair group。
7. under-constrained chain。
8. fixed boundary root selection case。

### 推荐路径

```text
fixtures/contracts/planning/spanning_tree/
  two_rigid_sets_supported.gcs.json
  three_rigid_set_cycle.gcs.json
  disconnected_forest.gcs.json
  unsupported_pattern.gcs.json
  same_rigid_set_constraint.gcs.json
  overconstrained_pair_group.gcs.json
  underconstrained_chain.gcs.json
  fixed_boundary_root.gcs.json
```

### 每个 fixture metadata

```json
{
  "schema_version": "gcs.contract_fixture.v1",
  "module_owner": "decomposition_planner",
  "expected_status": "ok|unsupported|warning",
  "expected_absorbed_constraints": [],
  "expected_closure_constraints": [],
  "expected_unsupported_constraints": [],
  "expected_report_codes": [],
  "seed": 0
}
```

### M3 验收测试

- fixture load/validate passes。
- expected partition matches planner output。
- malformed fixtures fail with typed report codes。

## M4: Reduced NumericTask Prototype

### 目标

在 opt-in 模式下生成 reduced `NumericTask`，仅用于实验，不作为默认求解路径。

### 输入

- `RigidSetSpanningForestPlan`
- `CoverPlan`
- `GaugePolicy`
- `ModelSnapshot`
- `ConstraintCatalog`

### 输出

```text
ReducedNumericTask
  original_context_snapshot
  reduced_parameter_blocks
  active_closure_equations
  absorbed_constraint_evidence
  transform_chain_map
  full_dimension
  reduced_free_dimension
  frozen_dimension
```

### 关键设计

1. public contract 不暴露 Euler angle 细节。
2. `NumericTask.parameterization` 可先使用:

```text
rigid_set_relative_spanning_tree_v1
```

3. reduced variable IDs 必须能映射回:
   - rigid set;
   - tree edge;
   - parent rigid set;
   - child rigid set;
   - absorbed constraints;
   - downstream entity subjects。

4. 第一版 Jacobian 可以 finite difference。
5. condition estimate 只有在 reduced free Jacobian 非 rank-deficient 时报告。

### 详细任务

1. 定义 reduced parameter block。
2. 定义 transform-chain evaluator。
3. 将 tree-edge relative parameters 映射为 descendant entity states。
4. 对 closure constraints 调用 `constraint_catalog` residual evaluator。
5. 输出 residual blocks，保留 original constraint IDs。
6. 输出 rank evidence:
   - original full variable dimension;
   - reduced free variable dimension;
   - frozen boundary dimension;
   - residual dimension;
   - rank;
   - nullity;
   - singular/under/over flags。

### M4 验收测试

- `numeric_reduced_task_preserves_closure_constraint_ids`
- `numeric_reduced_task_reports_full_and_reduced_dimensions`
- `numeric_reduced_task_keeps_absorbed_constraints_out_of_active_equations`
- `numeric_reduced_task_maps_reduced_variables_to_rigid_sets`
- `numeric_reduced_task_finite_difference_jacobian_dimensions_match`

### M4 完成定义

- Reduced task opt-in path compiles and tests pass。
- Existing default numeric path unchanged。
- Reduced report is inspectable even if solve is not yet product-ready。

## M5: Diagnostics Revalidation

### 目标

确保 reduced solve 后的全局结果仍通过 GCS 诊断契约，而不是只相信 tree parameterization。

### 需要诊断的证据

- absorbed tree constraints residual re-check；
- closure residuals；
- boundary agreement；
- gauge consistency；
- rank evidence full/reduced mapping；
- unsupported constraints；
- naturality distance or movement summary。

### 详细任务

1. 增加 `SpanningTreePlanDiagnosticInput`。
2. 对 absorbed constraints 重新计算 residual。
3. 对 closure constraints 读取 numeric residual report。
4. 比较 reduced local section 与 original entity states。
5. 对 unsupported or failed canonical cases 生成 obstruction。
6. 让 runtime 的 public report projection 能看见这些 evidence。

### M5 验收测试

- `diagnostics_revalidates_absorbed_spanning_tree_constraints`
- `diagnostics_reports_closure_residual_failures`
- `diagnostics_reports_spanning_tree_unsupported_obstruction`
- `diagnostics_preserves_full_and_reduced_rank_evidence`
- `runtime_rejects_reduced_solve_when_absorbed_constraint_revalidation_fails`

### M5 完成定义

- Diagnostics 可解释 reduced solve 成功或失败。
- Runtime 不会因为 reduced numeric success 单独 commit。

## M6: Naturality And Gauge

### 目标

把 LGS paper 中的 naturality 转化成 GCS 可报告的 root/gauge/initialization policy。

### 设计要求

- root rigid set 选择必须 deterministic。
- 如果 `SolveIntent.fixed_entity_ids` 命中某 rigid set，优先作为 root。
- 否则选择最低 stable rigid-set id。
- zero reduced variables 应尽量表示 "keep current sketch"。
- 如果不能保证 naturality，报告:

```text
planner.spanning_tree.naturality_not_guaranteed
```

### 详细任务

1. 定义 `SpanningTreeRootPolicy`。
2. 定义 natural initial reduced parameter computation。
3. 定义 movement-distance summary。
4. 将 root/gauge policy 写入 `GaugePolicy` 或 adjacent planner evidence。
5. 增加 diagnostics consistency check。

### M6 验收测试

- `planner_spanning_tree_root_prefers_fixed_rigid_set`
- `planner_spanning_tree_root_tie_break_is_deterministic`
- `numeric_zero_reduced_variables_preserve_satisfied_tree_constraints`
- `diagnostics_reports_naturality_not_guaranteed`

## M7: Empirical Gate And Production Decision

### 目标

用 evidence 决定是否默认启用该 strategy。

### 指标

每个 fixture/corpus case 记录:

- original variable dimension;
- reduced variable dimension;
- original residual dimension;
- closure residual dimension;
- absorbed constraint count;
- unsupported constraint count;
- rank/nullity full view;
- rank/nullity reduced view;
- max absorbed residual after solve;
- max closure residual after solve;
- iteration count;
- solve time;
- accepted/rejected status;
- obstruction report codes。

### 比较策略

```text
baseline current numeric path
vs
spanning-tree reduced opt-in path
```

### production gate

默认启用前必须满足:

- supported fixtures 中 dimension 明确下降；
- absorbed constraints revalidation 全部通过；
- closure residuals 符合 tolerance；
- unsupported fixtures 全部 typed unsupported；
- runtime commit only after diagnostics；
- no hidden fallback；
- full CTest pass；
- quality gate pass。

## 推荐实施顺序

### Step 1: `RigidSetPairConstraintGroup`

Scope:

- `incidence_graph`
- contract tests

Deliverable:

- deterministic rigid-set pair grouping。

Why first:

- 这是 spanning-tree method 的结构入口。
- 不需要 numeric 或 pattern catalog。

### Step 2: pattern match contract stubs

Scope:

- `constraint_catalog`
- `decomposition_planner`
- contract tests

Deliverable:

- pattern metadata shape；
- unsupported by default；
- no absorbed constraints until safe patterns exist。

Why second:

- 先建立 refusal semantics，避免后续 silent absorption。

### Step 3: maximum-weight spanning forest

Scope:

- `decomposition_planner`
- contract tests

Deliverable:

- deterministic tree selection；
- active constraint partition；
- structural report。

Why third:

- 这就是论文方法的 planner core，但仍不改变 solve。

### Step 4: v0 supported patterns

Scope:

- `constraint_catalog`
- `decomposition_planner`
- fixtures

Deliverable:

- 1-3 个极小安全 pattern。

Why fourth:

- 只有有了 tree builder 和 unsupported path，才适合打开少量 supported pattern。

### Step 5: reduced task opt-in

Scope:

- `numeric_engine`
- `diagnostics`
- contract tests

Deliverable:

- opt-in reduced `NumericTask` evidence。

Why fifth:

- Numeric work 风险高，必须在 planner evidence 稳定后做。

### Step 6: diagnostics and runtime integration

Scope:

- `diagnostics`
- `session_runtime`
- `viewer_bridge` only if public projection is needed

Deliverable:

- accepted/rejected status from ordinary GCS verification。

Why sixth:

- Reduced solve 不能绕过 runtime commit semantics。

## 质量门

每个 implementation PR 至少运行:

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\<task>\README.md
```

涉及 C++ contracts 后运行:

```bat
cmake --build out\build\clang-ninja
ctest --test-dir out\build\clang-ninja --output-on-failure
python tools\agentic_design\agentic_toolkit.py run-quality-gates
```

如果只改 docs/research，可跳过 build/CTest，但必须说明原因。

## 风险与缓解

| Risk | Severity | Mitigation |
| --- | --- | --- |
| constraint 被错误删除 | High | absorbed/closure/unsupported exactly-once partition tests |
| pattern 语义写进 planner | High | pattern metadata owned by constraint semantics |
| canonical position 不存在 | High | `canonical_position_unsupported` report |
| direction-sensitive pattern 出错 | High | parent/child orientation tests |
| reduced numeric report 难以解释 | Medium | reduced variable to rigid-set/entity/constraint map |
| Euler-like chart singularity | Medium | public contract abstract; singular chart report |
| performance 不如预期 | Medium | empirical gate before default enable |
| fallback 不透明 | High | fallback as report code, never hidden |

## 第一张后续任务卡建议

```text
Title:
Rigid-set spanning-tree plan contracts

Scope:
implementation

Risk:
medium

Owner:
gcs-decomposition-planning-steward

Specialists:
gcs-incidence-structure-steward
gcs-constraint-semantics-steward
gcs-quality-steward

Goal:
Add deterministic planner-side evidence for rigid-set maximum-weight spanning
forest planning, including rigid-set pair grouping, pattern match stubs,
absorbed/closure/unsupported constraint partitioning, and unsupported reports.
Do not change numeric solving.

Affected paths:
src/gcs/incidence_graph/
src/gcs/decomposition_planner/
src/gcs/constraint_catalog/
tests/contracts/incidence_graph/
tests/contracts/decomposition_planner/
tests/contracts/constraint_catalog/

Definition of done:
- rigid-set pair groups are deterministic;
- candidate edges have deterministic weights and tie breaks;
- selected forest is acyclic;
- every active cross-rigid-set constraint appears exactly once in
  absorbed/closure/unsupported evidence;
- unsupported cases return typed report codes;
- current component-cover behavior remains unchanged;
- focused contract tests pass.
```

## 最终推进建议

立即推进 M1，不要跳到 numeric optimization。M1 的价值是把论文方法变成 GCS 可审查的结构证据。一旦 constraint partition、unsupported reports 和 deterministic spanning forest 稳定，后续 pattern catalog 和 reduced numeric task 才有可靠落点。
