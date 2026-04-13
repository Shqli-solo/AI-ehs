# Superpowers + gstack 配置指南

本文档详细说明 Superpowers（思考与流程层）与 gstack（执行与外部世界层）的分工协作机制。

---

## 分工原则

| 层级 | 职责 | 触发方式 |
|------|------|----------|
| **Superpowers**（思考与流程层） | 计划、头脑风暴、调试、TDD、验证、代码审查 | 自动触发 |
| **gstack**（执行与外部世界层） | 浏览器操作、QA 测试、发布、部署、Canary、安全审计 | 斜杠命令手动触发 |

### 详细分工

| 任务类型 | 负责层 | 具体技能/命令 |
|----------|--------|---------------|
| 计划撰写 | Superpowers | `writing-plans` |
| 计划多视角审查 | gstack | `/autoplan` |
| 编码实现 | Superpowers | `test-driven-development` |
| 调试排查 | Superpowers | `systematic-debugging` |
| 真实环境验证 | gstack | `/qa` |
| 代码审查 | Superpowers | `requesting-code-review` |
| 发布合并 | gstack | `/ship` |
| 安全审计 | gstack | `/cso` |

---

## 浏览器规则

**唯一入口**：使用 `/browse` 作为所有浏览器操作的唯一入口。

**禁止事项**：
- ❌ 禁止使用 `mcp__claude-in-chrome__*` 操作浏览器
- ❌ 禁止使用 `mcp__plugin_chrome-devtools-*` 操作浏览器

**原因**：确保浏览器操作的可控性和一致性，避免状态混乱。

---

## 任务管理

### 强制要求

**所有多步骤任务必须使用 `TaskCreate` 追踪。**

### 管理要点

1. **brainstorming 完成后** → 立即创建任务列表
2. **每个阶段开始前** → `TaskUpdate` 标记为 `in_progress`
3. **每个阶段完成后** → `TaskUpdate` 标记为 `completed`
4. **会话恢复时** → `TaskList` 检查未完成任务

### 任务依赖关系

```
brainstorming
    ↓
writing-plans
    ↓
TDD
    ↓
code-review
    ↓
QA
    ↓
ship
```

**依赖规则**：
- `writing-plans` 必须在 `brainstorming` 完成后创建
- `TDD` 必须在 `writing-plans` 审查通过后开始
- `code-review` 必须在 `TDD` 完成后进行
- `QA` 必须在 `code-review` 通过后进行
- `ship` 必须在 `QA` 通过后进行

---

## 阶段验收标准

| 阶段 | 完成标准 | 产出物 |
|------|----------|--------|
| **brainstorming** | 需求明确、边界清晰、用户确认 | 需求摘要（对话记录） |
| **writing-plans** | 计划文档已写、`/autoplan` 审查通过 | `docs/superpowers/specs/*.md` |
| **TDD** | 测试用例已写、测试全过 | 测试文件 + 实现代码 |
| **code-review** | 审查通过、无 blocking issue | PR 或 git diff |
| **QA** | `/qa` 验证通过、无 console error | QA 报告 |
| **ship** | 已合并、已发布、更新 VERSION | git commit + tag |

**任何阶段不得跳过前置阶段。**

---

## 违规信号

出现以下想法时**立即停止**并查表调用对应 Skill：

| 违规想法 | 正确做法 |
|----------|----------|
| "这个简单，直接写就行" | → STOP → 查表调用 `TDD` |
| "我只是解释一下概念" | → STOP → 确认是否涉及代码/实现 |
| "先快速试一下" | → STOP → 先写测试 |

---

## Available gstack Skills

| 技能 | 用途 |
|------|------|
| `/browse` | 浏览器操作入口 |
| `/qa` | QA 测试 |
| `/qa-only` | 仅 QA 报告 |
| `/ship` | 发布合并 |
| `/land-and-deploy` | 部署发布 |
| `/canary` | Canary 监控 |
| `/cso` | 安全审计 |
| `/autoplan` | 多视角计划审查 |
| `/setup-browser-cookies` | 浏览器 Cookie 配置 |
| `/setup-deploy` | 部署配置 |
| `/benchmark` | 性能基准测试 |
| `/retro` | 项目回顾 |
| `/investigate` | 调查分析 |
| `/document-release` | 发布文档 |
| `/pair-agent` | 配对代理 |
| `/careful` | 安全守卫 |
| `/freeze` | 目录冻结 |
| `/guard` | 全安全模式 |
| `/unfreeze` | 解除冻结 |
| `/gstack-upgrade` | gstack 升级 |
| `/learn` | 学习管理 |
| `/design-review` | 设计审查 |
| `/design-consultation` | 设计咨询 |
| `/design-shotgun` | 多设计方案 |
| `/design-html` | HTML 设计 |

---

## 参考资料

- [Superpowers 官方文档](https://github.com/anthropics/superpowers)
- [gstack 官方文档](https://github.com/anthropics/gstack)

---

## 会话启动检查清单

**每次新会话开始时执行**：

1. 读取 `VERSION` → 确认当前版本号
2. 读取 `PROJECT_OVERVIEW.md` → 确认完成状态
3. `git status` → 检查未提交变更
4. `TaskList` → 检查未完成任务
5. 如有中断的任务 → 先恢复上下文再继续
