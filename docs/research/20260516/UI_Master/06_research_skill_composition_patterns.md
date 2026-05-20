# Skill 组合模式与设计工作流深度分析

## 来源
综合 Anthropic Skills 生态、skill0 平台、前端 Design Skills 组合实践。

## Skills 的三层架构

```
System Prompt（全局规则）
    ↓ 管全局
Skill（具体动作标准）
    ↓ 管细节
Design System（审美标准）
    ↓ 管输出质量
```

## 设计能力四分类模型

| 分类 | 核心能力 | 代表 Skill | 解决问题 |
|------|----------|-----------|----------|
| 生成 | 从0创建界面 | Taste / UI UX Pro Max | 没有设计图时的界面创建 |
| 规范 | 统一设计标准 | UI Skills / Vercel Guidelines | 杂乱UI的整理统一 |
| 还原 | 精确实现设计稿 | Impeccable | 设计稿到代码的精确还原 |
| 系统 | 规模化复用 | Designer / Stitch / Anthropic | 团队级设计能力基础设施 |

## 角色与 Skill 组合建议

| 角色 | 推荐 Skill 组合 | 核心目标 |
|------|-----------------|----------|
| 独立/个人开发者 | Taste Skill + UI UX Pro Max | 从0快速生成产品界面 |
| 非前端工程师 | UI Design Brain | 使用成熟设计模式 |
| 初级前端开发者 | UI Skills + Impeccable | 提升代码还原度 |
| 高级前端/架构师 | Vercel Guidelines + Anthropic frontend-design | 建立工程化设计规范 |
| 技术团队负责人 | Designer Skills Collection + stitch-skills | 设计能力规模化复用 |

## Skill 组合工作流

### 工作流1：从0到1的界面生成
```
Step 1: /frontend-design → 确定美学方向+生成代码
Step 2: /baseline-ui → 去除"AI味"，优化间距/字体/状态
Step 3: /fixing-accessibility → 键盘导航、焦点环、语义标签
Step 4: /fixing-motion-performance → 动效性能、尊重 reduced-motion
```

### 工作流2：存量UI优化
```
Step 1: /web-design-guidelines → 审查现有设计
Step 2: /ui-skills → 统一规范、修复基础问题
Step 3: /ui-design-brain → 替换临时结构为成熟模式
Step 4: /impeccable → 细节修正
```

### 工作流3：设计系统建设
```
Step 1: /frontend-design → 定义设计方向
Step 2: /designer-skills → 建立完整设计系统
Step 3: /stitch-skills → 自动化执行和组合
Step 4: /vercel-guidelines → 工程化审计标准
```

## Skill 的技术本质

```
Skills = 规则(Rules) + 上下文(Context) + 工具(MCP)
```

- **Rules**：解决"怎么做"的问题（标准与约束）
- **Context**：解决"在哪做"的问题（代码、文档、当前状态）
- **MCP**：解决"拿什么做"的问题（外部连接与能力）

## Skill 评估框架（skill-creator 新版）

### 三代理评估系统
1. **Grader（阅卷老师）**：按评分标准逐项打分
2. **Comparator（盲评评委）**：有skill vs 无skill的盲评比较
3. **Analyzer（数据分析师）**：多轮评分后汇总分析规律

### 防过拟合机制
- Train/Test 分割（60/40）
- 训练集上迭代改进
- 测试集验证泛化能力

### 描述触发优化
- 自动生成多个版本的 description
- 用测试句子逐版本测触发准确率
- 选择最优版本

## SKILL.md 标准结构

```yaml
---
name: skill-name
description: |
  何时使用此技能的描述
  包含什么能力的描述
---
```

```markdown
# 执行指令

## 触发条件
什么情况下应该使用此技能

## 读取顺序
先读什么，后读什么

## 工作模式
- Mode A: ...
- Mode B: ...

## Non-Negotiables
不可协商的约束

## 执行步骤
1. Step 1
2. Step 2
...

## 默认行为
没有额外context时的行为
```

## 关键洞察

1. **Skill 是可组合的**：多个 Skill 协同工作比单个 Skill 更强大
2. **工作流编排**：Skill 的价值在于编排成完整工作流
3. **评估驱动**：好的 Skill 需要评估、迭代、优化
4. **四分类模型**：生成→规范→还原→系统，覆盖设计全生命周期
5. **角色匹配**：不同角色需要不同的 Skill 组合
6. **Non-Negotiables**：不可协商的约束是 Skill 的核心保障

## 对 UI 架构师 Skill 的启示

- UI 架构师 skill 应该是可组合的，能与其他 skill 协同
- 应该定义清晰的工作流编排能力
- 内置评估机制，确保输出质量
- 按角色提供不同的 skill 变体
- Non-Negotiables 机制确保关键约束不被违反
- 标准化的 SKILL.md 结构确保可移植性
