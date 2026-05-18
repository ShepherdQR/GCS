# UI-UX Pro Max Skill 深度分析

## 来源
开源 AI 设计智能技能包，专为 Claude Code、Cursor、GitHub Copilot 等 AI 编程工具设计。

## 核心数据资产

| 资产类型 | 数量 | 说明 |
|----------|------|------|
| UI 风格 | 57 种 | 从极简主义到赛博朋克 |
| 行业配色方案 | 96 种 | 覆盖金融、医疗、教育等 |
| 字体搭配 | 57 种 | 展示字体+正文字体组合 |
| UX 最佳实践 | 99 条 | 跨平台通用准则 |
| 行业推理规则 | 100 条 | 反模式过滤 |

## 核心能力

### 1. 智能设计系统生成
```
需求分析 → 提取产品类型、风格关键词、行业领域
多领域检索 → 并行搜索UI风格、配色方案、字体搭配、页面结构
推理引擎匹配 → 基于BM25排名算法，从设计数据库中智能匹配
完整设计系统输出 → 样式、颜色、字体、动画、反模式
```

### 2. 技术栈适配（13种）
- Web：React、Next.js、Vue、Nuxt.js、Svelte、HTML+Tailwind
- 移动端：SwiftUI、React Native、Flutter
- 其他：Astro、shadcn/ui、Jetpack Compose

### 3. 反模式过滤
内置 100 条行业特定反模式规则：
- 金融行业：避免AI紫色/粉色渐变（缺乏专业感）
- 医疗行业：禁用高对比度动画（可能引发光敏性癫痫）
- 儿童产品：禁用暗色主题

## 设计系统输出结构

```
Design System Output:
├── Style Tokens
│   ├── Colors (primary, secondary, accent, neutral)
│   ├── Typography (heading, body, mono)
│   ├── Spacing (scale: 4px base)
│   └── Border Radius / Shadow
├── Component Patterns
│   ├── Layout Templates
│   ├── Navigation Patterns
│   └── Data Display Patterns
├── Animation Guidelines
│   ├── Entrance Animations
│   ├── Transition Patterns
│   └── Micro-interactions
└── Anti-Patterns
    ├── Industry-Specific Bans
    └── Universal Design Violations
```

## 典型案例

### SaaS 产品着陆页
- UI风格：极简主义 + Hero-Centric 布局
- 配色：主色深蓝(#003366)，CTA绿色(#22C55E)
- 字体：Inter(主) + Montserrat(标题)
- 页面结构：Hero区 → 特性展示 → 客户Logo → 定价表 → FAQ

### 医疗健康仪表板
- UI风格：Glassmorphism + 数据可视化优先
- 配色：主色浅蓝(#E6F7FF)，辅助白色(#FFFFFF)
- UX优化：大字号表格行高(48px)，错误状态红色(#EF4444)

## 关键洞察

1. **数据驱动设计决策**：不是凭感觉，而是从结构化数据库中检索匹配
2. **行业感知**：不同行业有不同的设计约束和禁忌
3. **反模式机制**：知道"不该做什么"比"该做什么"更重要
4. **技术栈适配**：同一设计系统可以映射到不同技术实现
5. **BM25 排名算法**：用信息检索方法匹配设计风格，确保最佳匹配

## 对 UI 架构师 Skill 的启示

- UI 架构师应该内置行业知识库
- 反模式列表是架构师 skill 的核心防护机制
- 设计系统应该有结构化的 token 体系
- 技术栈适配能力让架构师 skill 跨平台可用
- 推理引擎模式可以用于自动匹配最佳设计方案
