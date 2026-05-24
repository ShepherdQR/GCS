# 从模糊描述到可用制度型 Agent

## 目标

本流程解决一个核心问题：用户只给一段提示词、灵感、隐喻或模糊描述时，如何稳定
生成符合 GCS 约定的角色模板卡，并继续补齐材料，形成切实可调用的制度型 agent。

一句话流程：

```text
模糊描述 -> 意图提炼 -> 适配审查 -> 命名生成 -> 角色卡 -> 可执行材料 -> 使用证据 -> 升级
```

## 什么才算“切实可用”

一个制度型 agent 不是有名字就可用。至少满足以下条件，才算最小可用：

- 有独立角色卡：`README.md`。
- 有清晰触发条件：什么时候调用，什么时候不调用。
- 有输入包定义：调用者必须给哪些原料。
- 有输出产物定义：产物落在哪里，包含哪些字段。
- 有种子 prompt：未来会话能直接复制调用。
- 有守则和拒绝项：防止角色越权、泛化或编造。
- 有交接规则：知道何时交给 module agent、experience、completed-task 或 architecture。
- 有验收清单：调用完成后能判断产物是否可复用。

更成熟的 promoted agent 还应具备：

- `prompts/`：稳定调用提示词；
- `templates/`：产物模板；
- `examples/`：真实或模拟调用样例；
- `evals/`：能检验角色是否按契约工作的场景。

## 六阶段生成流水线

### 1. 意图提炼

先不要急着命名。把用户的模糊描述拆成六个字段：

| 字段 | 问题 |
| --- | --- |
| 痛点 | 这个角色要解决什么反复出现的问题？ |
| 场景 | 它在什么任务、周期或事件后被调用？ |
| 原料 | 它读取哪些文档、记录、diff、报告或摘要？ |
| 转化 | 它把输入变成什么？ |
| 产物 | 它必须留下什么耐久 artifact？ |
| 风险 | 如果没有这个角色，项目会损失什么？ |

如果信息不足，生成器最多问 3 个问题。若能合理假设，则先生成并标注
`Assumptions`，不要阻塞。

### 2. 适配审查

生成新角色前，先判断是否应复用已有角色：

| 判断 | 处理 |
| --- | --- |
| 已有角色能覆盖 | 不新增；建议更新已有角色 README、prompt 或 template |
| 是已有角色的子流程 | 不新增；加到现有角色的操作循环或模板 |
| 只是一项一次性任务 | 不新增；写 task card 或 execution plan |
| 缺少耐久产物 | 不新增；先要求定义产物 |
| 有独立触发、产物和风险 | 可生成 candidate 或 seed |

这一步是必要的。制度型 agent 的价值来自职责清晰，不来自数量多。

### 3. 命名生成

按 GCS 工坊制生成 3 到 5 个候选名：

```text
<工艺身份>: <转化动作>-<校验或收束动作>
```

每个名字必须给出：

- 功能副标题；
- 处理的原料；
- 产出的 artifact；
- 与已有角色的区别；
- 推荐或不推荐理由。

最终选择一个推荐名，并生成稳定 slug：

```text
NNN-short-role-slug
```

编号先用 `<next-id>` 占位，实际落盘时再按目录中的下一个编号确定。

### 4. 角色卡生成

使用 `templates/standing-agent-card.md` 填充角色卡。生成时必须完整覆盖：

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

角色卡语言要做到两层同时成立：

- 人能读出角色的味道和边界；
- agent 能按字段执行，不依赖氛围理解。

### 5. 可执行材料生成

如果目标是“切实可用”，不要停在角色卡。继续生成三类材料：

```text
prompts/<role>-invoke.md
templates/<role>-output.md
evals/<role>-basic-eval.md
```

最小材料要求：

- `prompts/`：给出可复制调用 prompt，包含输入包格式和输出要求。
- `templates/`：给出角色主要产物的 Markdown 模板。
- `evals/`：给出一个成功场景和一个应拒绝或降级处理的反例场景。

### 6. 使用证据与升级

第一次创建时，角色通常是 seed。使用后再升级：

- 调用 1 次，有产物：保留 seed，补 example。
- 调用 2 次以上，解决同类问题：升级 practiced。
- 有稳定 prompt/template/eval：升级 promoted。
- 被 runbook、toolkit、quality gate 或 lifecycle 引用：升级 institutional。

## 生成器输出格式

每次从模糊描述生成角色时，输出必须按这个顺序：

1. **Decision**：reuse existing | update existing | create candidate | create seed。
2. **Reasoning Summary**：为什么这样处理，最多 5 条。
3. **Distilled Intent**：痛点、场景、原料、转化、产物、风险。
4. **Naming Candidates**：3 到 5 个候选名。
5. **Recommended Role**：推荐名、功能副标题、slug。
6. **Role Card Markdown**：可直接写入 `README.md` 的内容。
7. **Invoke Prompt**：可直接写入 `prompts/` 的调用提示词。
8. **Output Template**：可直接写入 `templates/` 的产物模板。
9. **Basic Eval**：可直接写入 `evals/` 的基本测试场景。
10. **Next Actions**：需要创建或更新的文件列表。

## 从描述到文件的推荐落盘规则

如果生成器判断为 `create seed`：

```text
docs/agentic/institutional-agents/
  NNN-short-role-slug/
    README.md
    prompts/
      invoke.md
    templates/
      output.md
    evals/
      basic-eval.md
```

如果生成器判断为 `create candidate`：

- 只更新总览 README 的候选角色表；
- 不创建子目录；
- 记录缺少哪些证据。

如果生成器判断为 `update existing`：

- 更新对应角色 README；
- 或新增 prompts/templates/evals；
- 不创建新角色。

## 质量门

生成后的角色必须通过这 10 个问题：

1. 这个角色是否解决长期制度问题，而非一次性任务？
2. 它与现有角色的区别是否明确？
3. 触发条件是否具体？
4. 输入包是否具体？
5. 输出产物是否可归档、可检索、可复用？
6. 是否至少有 3 条守则或拒绝项？
7. 是否明确何时交接给其他 agent 或文档体系？
8. 种子 prompt 是否能直接复制使用？
9. 是否有一个正例 eval 和一个反例 eval？
10. 未来 agent 是否能只读该角色包就执行一次合格调用？

任一关键项为否，则保持 candidate 或补齐材料后再升级。
