# 制度型 Agent 使用与新增规范

## 当前制作状态

制度型 agent 体系已经建立，但还没有全部制作完成。

当前完成范围：

- 已建立目录：`docs/agentic/institutional-agents/`。
- 已建立总览：`README.md`，包含命名范式、角色等级和候选角色体系。
- 已制作 4 个 seed 角色：
  - `I001 刀匠: 淬炼-锻打`
  - `I002 裁缝: 裁剪-缝合`
  - `I003 Atelier Steward: Calibrate-Review`
  - `I004 Art Director: Frame-Judge`
- 已提供新增角色模板：`templates/standing-agent-card.md`。
- `I001` 已有 Step 47 真实 filled example。

尚未完成范围：

- 候选角色表中的 `舵手`、`磨镜师`、`铸印官`、`验收官`、`值夜官`、
  `复盘官`、`校雠者`、`策展人`、`铺路官`、`账房`、`法度官`、`园丁`
  还没有创建独立子目录。
- 核心 seed 角色正在补 examples；I001 和 I002 已有首批 invoke prompt、
  output template、refusal eval，且各有一个真实 example。
- 制度型 agent 还没有接入自动化工具或强制质量门。

这是有意为之。制度型 agent 不是角色名清单，而是经过真实使用、可留下产物、
能降低风险的项目制度。没有证据的角色只能保持 candidate 状态。

## 适用边界

制度型 agent 用来处理跨会话、跨任务、跨文档的项目运行问题。

适合调用制度型 agent 的场景：

- 一个问题不属于单个 solver 模块，而属于项目工作方式；
- 需要整理多会话历史、经验、复盘、验收、风险或治理；
- 需要把探索中出现的做法升级为可复用机制；
- 需要独立的检查、校准、编排或归档角色；
- 需要为未来 agent 留下可检索、可执行、可复查的耐久产物。

不适合调用制度型 agent 的场景：

- 单个函数、测试或模块边界内的小实现问题；
- 已有 GCS module skill 明确覆盖的专业设计问题；
- 只需要一次普通总结，不需要耐久产物；
- 角色无法定义输入、输出、守则或归档位置；
- 只是为了让会话更有仪式感。

## 使用规范

### 1. 先判断是否需要制度型 agent

每次准备调用前，先回答四个问题：

1. 这是单次执行问题，还是跨会话制度问题？
2. 是否存在一个明确的耐久产物？
3. 未来 agent 是否能从这个产物中节省时间或降低风险？
4. 是否已有更合适的 module agent、skill、runbook 或工具？

只有前 3 个问题为是，并且第 4 个问题为否或需要配合时，才调用制度型 agent。

### 2. 选择最小必要角色

一次会话默认只调用 1 个主制度型 agent。需要多个角色时，必须说明顺序和交接。

常见选择：

| 需要 | 首选角色 | 产物 |
| --- | --- | --- |
| 从探索中提炼经验 | `刀匠: 淬炼-锻打` | 经验记录、skill 候选、检查表 |
| 整理多会话历史 | `裁缝: 裁剪-缝合` | 时间线、历史 brief、缺口清单 |
| 宽问题分派和收束 | `舵手: 分派-收束` candidate | 编排 brief、综合报告 |
| 工作完成前独立审查 | `验收官: 举证-放行` candidate | review findings、gate decision |
| 失败或回归复盘 | `复盘官: 归因-修复` candidate | postmortem、action items |
| 质量标准不清 | `磨镜师: 评估-校准` candidate | rubric、scorecard |
| 文档与代码互相矛盾 | `校雠者: 对读-纠偏` candidate | 一致性报告 |

如果所需角色仍是 candidate，不要假装它已经成熟。可以临时按 candidate 执行，
但本次会话结束后要判断是否值得创建 seed 子目录。

### 3. 调用时必须给出输入包

制度型 agent 不能凭印象工作。调用时至少提供：

- 目标：本次希望角色解决什么制度问题；
- 范围：时间范围、任务范围、文档范围或模块范围；
- 原料：报告、diff、task card、research note、质量门结果、用户修正；
- 输出位置：产物应落在哪个目录或文档；
- 约束：哪些内容不能改、哪些判断只能标为不确定。

推荐调用格式：

```text
调用 <角色名>。

目标：<要解决的制度问题>
范围：<时间/任务/文档/模块范围>
原料：
- <artifact path or summary>
- <artifact path or summary>
期望产物：<经验记录/时间线/review findings/rubric/...>
输出位置：<path>
约束：
- <guardrail>
- <guardrail>
```

### 4. 执行时保持角色契约

制度型 agent 必须按自己的 README 执行：

- 先读角色 README；
- 明确原料是否足够；
- 区分事实、决策、偏好、假设和未解问题；
- 产物必须有证据链接或来源说明；
- 不确定内容必须标注，不得编造因果；
- 涉及 solver contract 或模块边界时，交给对应 module agent 或
  `gcs-architecture-steward`。

### 5. 产物必须归档

制度型 agent 的最小完成条件不是“对话里说清楚”，而是有耐久产物。

归档规则：

| 产物类型 | 位置 |
| --- | --- |
| 可复用经验 | `docs/agentic/experience/` |
| 多会话时间线 | `docs/agentic/institutional-agents/<role>/examples/` 或相关专题目录 |
| 完成任务报告 | `docs/completed-tasks/` |
| 角色契约更新 | `docs/agentic/institutional-agents/<role>/README.md` |
| prompt/template/eval | 对应角色的 `prompts/`、`templates/`、`evals/` |
| 架构规则 | `docs/architecture/`，并交给架构 steward |

没有归档产物的调用，只能算讨论，不算制度型 agent 完成了一次工作。

### 6. 调用后做一次闭环判断

每次调用结束时，记录或至少回答：

- 这次角色产物是否可被未来会话直接使用；
- 是否暴露了新角色、新模板、新 eval 或 skill patch 的需要；
- 是否有未关闭风险或缺口；
- 是否应该把角色从 seed 升级为 practiced，或从 candidate 升级为 seed。

## 新增 Agent 规范

新增制度型 agent 的推荐路径不是直接手写角色卡，而是先用
[`GENERATION-PIPELINE.md`](GENERATION-PIPELINE.md) 做一次生成审查。用户可以只给
一段模糊描述，再用
[`templates/role-card-generator-prompt.md`](templates/role-card-generator-prompt.md)
生成角色卡、调用 prompt、产物模板和基本 eval。

### 1. 新增前先做必要性审查

新增制度型 agent 之前，必须满足至少两项：

- 同类问题已经出现两次以上；
- 该问题跨越多个会话、文档、模块或任务；
- 现有角色不能自然覆盖；
- 该角色能留下明确产物；
- 该角色能降低明显风险、节省大量恢复上下文时间，或提升验收质量；
- 用户明确提出长期需要。

如果只满足一项，先把它写入候选角色表，不创建子目录。

### 2. 不新增的情况

以下情况禁止新增角色：

- 只是现有角色的同义词；
- 只是一个一次性任务；
- 只有人格设定，没有产物契约；
- 无法定义触发条件；
- 无法定义守则和拒绝项；
- 会和 module agent 抢架构所有权；
- 会鼓励保存原始聊天而不是提炼产物。

### 3. 新增流程

新增一个 seed 角色必须按以下步骤：

1. 在 `README.md` 的候选角色表中确认或新增 candidate。
2. 说明为什么现有角色无法覆盖。
3. 使用 `templates/standing-agent-card.md` 创建子目录：

   ```text
   docs/agentic/institutional-agents/NNN-short-role-slug/README.md
   ```

4. 在角色 README 中写清：
   - 名字解读；
   - 使命；
   - 触发节奏；
   - 原料；
   - 产物；
   - 操作循环；
   - 守则；
   - 交接；
   - 种子 prompt；
   - 成长待办。
5. 在总览 README 的种子角色索引中登记。
6. 若角色来自真实会话，链接对应 task、completed-task、experience 或 research evidence。
7. 自检：该角色是否能被一个未来 agent 只读 README 就正确执行。

如果目标是制作“切实可用”的 agent，而不是只创建 seed 角色卡，应同时创建：

```text
prompts/invoke.md
templates/output.md
evals/basic-eval.md
```

其中 `invoke.md` 定义调用输入包，`output.md` 定义主要产物格式，
`basic-eval.md` 定义一个正例和一个反例。

### 4. 命名规范

显示名采用：

```text
<工艺身份>: <转化动作>-<校验或收束动作>
```

命名必须同时给出：

- 中文显示名；
- plain-language 功能副标题；
- ASCII slug；
- 不超过 2 句话的名字解读；
- 与现有角色的区别。

禁止使用只表达性格或氛围的名字。名字必须暗示职责、材料、动作和产物。

### 5. 编号规范

使用 `NNN-short-role-slug`：

- `001`、`002` 已被刀匠和裁缝占用；
- 新角色使用下一个未占用编号；
- 编号一旦创建不重排；
- slug 使用小写英文和连字符；
- slug 表示角色，不表示某一次任务。

### 6. 等级升级规范

制度型 agent 等级如下：

| 等级 | 升级条件 |
| --- | --- |
| candidate | 有名字、使命和潜在价值，记录在总览候选表 |
| seed | 有独立子目录和完整 README 契约 |
| practiced | 至少两次真实调用，并有 examples 或 completed-task 链接 |
| promoted | 有可复用 prompts、templates 或 evals |
| institutional | 被 lifecycle runbook、skill、toolkit 或质量门引用 |

升级必须基于证据，不基于喜欢某个名字。

### 7. 评审清单

新增或升级角色前，用这张清单审查：

- 这个角色解决的是长期制度问题吗？
- 输入是否明确？
- 输出是否可归档、可检索、可复用？
- 是否有至少一个拒绝项？
- 是否会覆盖已有角色职责？
- 是否会越过 module agent 的所有权？
- 是否能用 10 分钟读 README 后正确执行？
- 是否有证据说明它值得存在？

如果任一关键项为否，保持 candidate，不创建或不升级。

## 推荐调用节奏

| 节奏 | 建议角色 | 目的 |
| --- | --- | --- |
| 每个非平凡任务结束时 | `刀匠`，按需 | 判断是否有可复用经验 |
| 每 3 到 5 个相关会话后 | `裁缝` | 编制专题时间线 |
| 大型任务启动前 | `铸印官` 或 `舵手` candidate | 反推成功状态或编排分工 |
| 重要改动完成前 | `验收官` candidate | 独立证据审查 |
| 质量失败后 | `复盘官` candidate | 无责复盘和行动项 |
| 每周或里程碑前 | `值夜官` candidate | 巡检漂移、CI、风险和陈旧任务 |

## 最小可行制度

当前阶段先执行这三条：

1. 长探索结束后，优先调用 `刀匠: 淬炼-锻打`，看是否产出经验记录或 skill 候选。
2. 连续多会话推进同一主题后，调用 `裁缝: 裁剪-缝合`，形成可续接时间线。
3. 任何新制度型 agent 都先进入 candidate，只有真实会话证明它有产物价值，才创建子目录。
