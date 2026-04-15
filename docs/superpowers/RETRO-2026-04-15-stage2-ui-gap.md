# 阶段 2 流程疏漏记录

> **记录日期**: 2026-04-15  
> **阶段**: brainstorming → writing-plans  
> **疏漏类型**: UI/UX 设计审查缺失

---

## 疏漏描述

**问题**: 阶段 2 的 brainstorming 和 /autoplan 审查过程中，**没有提供 UI 线框图和交互流程原型**，直接进入了 writing-plans 阶段。

**影响范围**:
- Design Review 视角缺少视觉化依据
- 前端 Task 验收标准不够具体
- 用户无法在编码前预览界面效果

---

## 根本原因分析

### 1. Brainstorming Skill 的 Visual Companion 规则未触发

根据 brainstorming skill 规定：
> When you anticipate that upcoming questions will involve visual content (mockups, layouts, diagrams), offer it once for consent

**实际情况**:
- 阶段 2 设计包含 **7 个前端页面**（Dashboard、告警列表、预案管理、模拟上报、设备监控、报告生成、系统设置）
- 设计文档中只有 ASCII 架构图，**无页面线框图**
- 没有主动询问用户是否打开浏览器 companion

**为什么会遗漏**:
1. 过度关注技术架构（Monorepo、六边形、gRPC、微调模型）
2. 误以为 ASCII 架构图足够表达设计意图
3. 没有严格遵循 brainstorming skill 的 checklist

### 2. /autoplan 审查未识别 UI 缺失

/autoplan 的 Design Review 视角本应发现：
- 7 个页面无具体布局设计
- UI 状态（Loading/Empty/Error/Success）未定义
- 响应式/无障碍设计缺失

**实际情况**: Design Review 发现了问题，但以**文本形式**提出，而非要求补充视觉稿。

---

## 补救措施

### 已完成
1. ✅ 创建 UI 线框图文档 `docs/superpowers/specs/2026-04-15-ehs-stage2-ui-wireframes.md`
2. ✅ 使用浏览器 companion 渲染 4 个页面的可交互原型
3. ✅ 补充 7 个页面的 ASCII 线框图
4. ✅ 绘制用户交互流程图
5. ✅ 定义 UI 状态规范（Loading/Empty/Error/Success）
6. ✅ 定义响应式断点和无障碍设计要求

### 待补充（执行阶段）
- [ ] Figma/Excalidraw 高保真原型
- [ ] 交互原型演示视频
- [ ] 设计令牌（Design Tokens）JSON 导出

---

## 流程改进建议

### 对 brainstorming skill 的改进

**检查点增加**:
```
□ 是否包含 UI 页面？ → 是 → 必须提供视觉稿（ASCII/HTML/Figma）
□ 是否涉及用户交互？ → 是 → 必须提供交互流程图
□ 是否有复杂布局？ → 是 → 必须使用 browser companion 渲染
```

**强制执行**:
- Brainstorming 结束前，必须询问："是否要查看 UI 线框图？我可以打开浏览器展示。"
- Design Review 视角必须检查视觉稿完整性

### 对 writing-plans skill 的改进

**前置条件检查**:
```
□ Design 文档是否包含 UI 线框图？
□ 如果没有，暂停并提醒用户补充
```

### 对 /autoplan skill 的改进

**Design Review 检查清单增加**:
- [ ] UI 线框图完整性（所有页面覆盖）
- [ ] 交互流程图
- [ ] UI 状态定义（Loading/Empty/Error/Success/Partial）
- [ ] 响应式断点设计
- [ ] 无障碍设计规范

---

## 经验教训

### 核心教训

**"视觉化成本极低时，必须视觉化"**

- AI 生成 HTML 原型的边际成本接近于 0
- 用户看 10 秒原型胜过读 1000 字描述
- 编码前发现设计问题，修复成本是编码后的 1/10

### 类比

> 就像建筑师不会只给客户看文字描述就开工，一定会提供蓝图和效果图。  
> UI 线框图就是软件开发的"建筑蓝图"。

### 量化影响

| 阶段 | 发现问题的成本 | 修复成本 |
|------|--------------|---------|
| Design 阶段（线框图） | 5 分钟修改 ASCII | 0 代码改动 |
| 编码后（PR Review） | 30 分钟审查 | 2-4 小时重构 |
| 上线后（用户反馈） | 1 周发现 | 8-20 小时 + 用户流失 |

---

## 该项目后续应用

**阶段 2 执行时**:
1. 前端 Task 1.2 必须参考线框图文档
2. UI 组件开发以 HTML 原型为基准
3. 验收标准包含"与线框图一致性检查"

**未来项目**:
1. brainstorming 输出必须包含 `*-ui-wireframes.md`
2. /autoplan 审查必须检查视觉稿
3. writing-plans 必须链接到具体线框图

---

## 相关文件

- UI 线框图：`docs/superpowers/specs/2026-04-15-ehs-stage2-ui-wireframes.md`
- 设计文档：`docs/superpowers/specs/2026-04-15-ehs-stage2-design.md`
- 实施计划：`docs/superpowers/plans/2026-04-15-ehs-stage2-plan.md`

---

## 复盘点检

**阶段 1 是否有此问题？**

阶段 1 MVP 只有 1 个告警列表页面，且使用了 Ant Design 默认样式，**UI 设计复杂度低**，所以未暴露此问题。

**阶段 2 为何必须补充？**

阶段 2 有 **7 个完整页面**，涉及：
- 多状态管理（告警处理流程）
- 复杂交互（预案预览抽屉、设备详情弹窗）
- 数据可视化（趋势图、分布图）
- 响应式布局（移动/平板/桌面）

**不补充的后果**:
- 前端开发靠猜
- Review 标准模糊
- 用户体验不一致

---

**记录人**: AI Assistant  
**审核状态**: 待用户确认  
**改进措施状态**: 已应用到当前项目
