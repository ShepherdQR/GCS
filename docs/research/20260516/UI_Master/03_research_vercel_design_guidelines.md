# Vercel Web Design Guidelines Skill 深度分析

## 来源
Vercel 官方出品的网页设计指南，包含 100+ 条 UI/UX 规则。

## 核心定位
将 Vercel 工程团队的设计智慧转化为可执行的规则，帮助开发者创建符合现代网页设计标准的应用。

## 四大审查维度

### 1. 布局审查（Layout Audit）
- 页面结构合理性
- 对齐方式和间距一致性
- 响应式断点处理
- 网格系统使用规范

### 2. 可访问性分析（Accessibility Audit）
- 色彩对比度（WCAG AA/AAA 标准）
- ARIA 标签完整性
- 键盘导航支持
- 屏幕阅读器兼容性

### 3. 用户体验评估（UX Evaluation）
- 交互流程合理性
- 反馈机制完整性
- 用户引导设计
- 错误状态处理

### 4. 性能与质量（Performance & Quality）
- 渲染性能
- 动画流畅度
- 加载状态设计
- 渐进增强策略

## 规则体系结构

```
Web Design Guidelines
├── Layout Rules
│   ├── Grid System (12-column / 16-column)
│   ├── Spacing Scale (4px base unit)
│   ├── Breakpoint Strategy
│   └── Container Max-Width
├── Typography Rules
│   ├── Font Size Scale
│   ├── Line Height Standards
│   ├── Font Weight Hierarchy
│   └── Text Truncation Strategy
├── Color Rules
│   ├── Primary/Secondary/Accent
│   ├── Semantic Colors (success/warning/error/info)
│   ├── Dark Mode Mapping
│   └── Contrast Ratios
├── Component Rules
│   ├── Button States (default/hover/active/disabled/loading)
│   ├── Form Input States
│   ├── Card Layout Standards
│   └── Navigation Patterns
├── Interaction Rules
│   ├── Hover/Focus States
│   ├── Loading States
│   ├── Error States
│   └── Empty States
└── Accessibility Rules
    ├── Keyboard Navigation
    ├── Screen Reader Support
    ├── Focus Management
    └── ARIA Attributes
```

## 与 Vercel React Best Practices 的协同

| 技能 | 关注点 | 协同方式 |
|------|--------|----------|
| vercel-react-best-practices | 代码性能 | 45条优化规则，8大类别 |
| web-design-guidelines | 设计质量 | 100+条UI/UX规则 |
| vercel-composition-patterns | 组件架构 | 复合组件模式 |

## 审查触发方式

```
请帮我审查这个登录页面的设计，确保它符合Vercel的设计指南。
```

AI 会自动：
1. 检查布局结构
2. 验证可访问性
3. 评估用户体验
4. 输出改进建议

## 关键洞察

1. **规则可执行化**：将设计智慧转化为 AI 可执行的检查规则
2. **多维度审查**：不是单一视角，而是布局+可访问性+UX+性能的综合评估
3. **状态完整性**：强调所有交互状态的完整覆盖（default/hover/active/disabled/loading/error/empty）
4. **与工程实践结合**：设计指南与代码最佳实践协同工作
5. **渐进式标准**：从基础合规到高级优化的分层标准

## 对 UI 架构师 Skill 的启示

- UI 架构师应该具备多维度审查能力
- 状态完整性是架构师必须关注的重点
- 设计规则应该与工程规则协同
- 审查机制应该是自动化的，而非依赖人工检查
- 分层标准让架构师可以在不同质量级别上工作
