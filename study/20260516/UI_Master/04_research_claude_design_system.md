# Claude Design 的 Design-System-as-a-Skill 深度分析

## 来源
Anthropic 2026年4月推出的 Claude Design 产品，采用"设计系统即技能"的创新架构。

## 核心创新：Design-System-as-a-Skill

Claude Design 不是简单生成漂亮 UI，而是：
1. **强制定义和构建系统的各个部分**
2. **智能地让用户参与决策**
3. **将用户反馈视为迭代的关键输入**

## 双文件架构

### README.md — 系统的语义契约

```markdown
# Design System README

## Voice & Tone
一句话定义产品 voice，作为 tone 的功能性描述

## 文件索引
映射哪个文件包含什么，未来 agent 知道去哪里找

## 写作规则
大小写、代词、标点、表情符号使用，带实际示例和 few-shots

## 视觉基础
- 颜色：精确值和使用语义
- 字体：比例和字重
- 间距：scale 和使用规则
- 圆角：语义化命名
- 阴影：层级对应
- 动效：交互状态
每个决策附有理由注释

## 已知替代方案
- 哪个字体不能重新分发
- 哪个 token 有 fallback
- 哪个决策是近似值
- 哪里仍然缺少清晰度

## Non-Negotiables
不可协商的约束条件
```

### SKILL.md — Agent 的操作入口

```yaml
---
name: design-system
description: |
  何时使用此技能以及它包含什么的描述
---
```

```markdown
# 执行指令

## 读取顺序
1. 先读 README
2. 然后链接 token CSS
3. 然后探索 components

## 工作模式
- Quick Prototype：快速原型，简化规则
- Production Code：生产代码，完整规则

## Non-Negotiables
- voice 使用 sentence case
- 产品中从不使用表情符号
- 最小化阴影
- 不要夸张的动效

## 默认行为
如果有人调用 skill 而没有额外的 context，
询问他们想构建什么再执行。Agent 不假设。它询问。
```

## 完整项目结构

```
design-system/
├── README.md           ← 语义契约（人+agent可读）
├── SKILL.md            ← Agent 操作入口
├── tokens.css          ← CSS 变量（设计 token）
├── assets/             ← 图片、图标等资源
├── components/         ← 组件库
│   ├── Button/
│   ├── Card/
│   ├── Navigation/
│   └── ...
└── previews/           ← 组件预览/示例
```

## 关键设计原则

### 1. 语义契约优先
README 不是文档，是契约——所有定义身份的内容，以人和 agent 都能阅读的方式表达。

### 2. 渐进式加载
Agent 先读 README 获取全局上下文，再按需深入具体文件，避免 token 浪费。

### 3. 双模式工作
- Quick Prototype：快速验证想法，简化规则
- Production Code：完整规则，生产级质量

### 4. Non-Negotiables 机制
明确哪些约束不可协商，避免 agent 在关键决策上"自由发挥"。

### 5. 默认询问行为
没有足够 context 时不假设，而是询问用户。这防止了 agent 的"自作主张"。

## 关键洞察

1. **设计系统是 skill 的最高形态**：不是生成单个页面，而是生成整个设计系统作为可复用的 skill
2. **双文件分离**：语义契约(README)和操作指令(SKILL)分离，各司其职
3. **理由注释**：每个设计决策都附有理由，让 agent 理解"为什么"而非仅知道"是什么"
4. **已知限制透明化**：明确标注系统的局限和替代方案，避免 agent 在未知区域做出错误决策
5. **询问优于假设**：在不确定时询问用户，而非自行决策

## 对 UI 架构师 Skill 的启示

- UI 架构师 skill 应该生成完整的设计系统，而非单个页面
- 语义契约+操作指令的双文件模式是最佳实践
- 每个设计决策都需要理由注释
- Non-Negotiables 机制是架构师 skill 的核心约束
- 渐进式加载避免 token 浪费
- 默认询问行为防止 agent 过度自主
