# CLAUDE.md 改进计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建一个符合 Anthropic 官方最佳实践、同时保留现有 Superpowers + gstack 分工的 CLAUDE.md 配置

**Architecture:** 采用分层结构 - 根目录 CLAUDE.md 保持精简（核心路由规则），详细配置拆分为独立文档

**Tech Stack:** Claude Code, Superpowers skills, gstack skills, MCP hooks

---

## 改进原则

基于 Anthropic 官方最佳实践和社区经验：

1. **Keep it concise** - 核心 CLAUDE.md 保持在 60 行以内
2. **Update regularly** - 建立维护机制
3. **Include examples** - 提供代码示例
4. **Specify constraints** - 明确约束条件
5. **Document decisions** - 记录设计决策

---

## 任务分解

### Task 1: 创建项目概述文档

**Files:**
- Create: `PROJECT_OVERVIEW.md`

- [ ] **Step 1: 创建项目概述文档**

```markdown
# 面试准备项目概述

## 项目目标
根据直投 - 最终版.md 里的工作经历，构建生产级开源 GitHub 项目
目标：95% 覆盖简历中的 OpenClaw 和广汽 EHS 中台两个项目

## 技术栈
- **后端**: Python 3.11+, FastAPI, LangGraph, LangChain
- **向量数据库**: Milvus, Elasticsearch
- **图数据库**: Neo4j
- **LLM**: Claude API, vLLM
- **评估**: Ragas, LangFuse
- **前端**: React 18, TypeScript
- **部署**: Docker, Kubernetes
- **监控**: Prometheus, Grafana

## 项目结构
```
mianshi/
├── CLAUDE.md              # Claude Code 配置（精简版）
├── PROJECT_OVERVIEW.md    # 项目概述（本文档）
├── docs/
│   ├── superpowers/       # Superpowers 计划文档
│   └── specs/             # 功能规格说明
├── src/
│   ├── core/              # 核心模块
│   ├── agents/            # Multi-Agent 编排
│   ├── rag/               # GraphRAG 知识引擎
│   └── api/               # API Gateway
├── tests/                 # 测试用例
└── deployments/           # K8s 部署配置
```

## 当前阶段
EHS 中台：核心模块已完成 90%，处于补充功能 + 优化阶段

## 下一阶段目标
- 补充 Admin Console（React 管理后台）
- 完善项目可演示性
```

- [ ] **Step 2: 提交**

```bash
git add PROJECT_OVERVIEW.md
git commit -m "docs: add project overview"
```

---

### Task 2: 精简核心 CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 重写 CLAUDE.md（精简到 60 行以内）**

```markdown
## 项目说明
面试准备项目 - 构建生产级开源 GitHub 项目，95% 覆盖简历中的 OpenClaw 和广汽 EHS 中台

## Skill Routing (关键配置)

| 请求类型 | 调用的 Skill |
|---------|-------------|
| 计划/规划/设计 | `Superpowers: writing-plans` |
| 头脑风暴/创意发散 | `Superpowers: brainstorming` |
| 编码/实现 | `Superpowers: test-driven-development` |
| 调试/排查问题 | `Superpowers: systematic-debugging` |
| 代码审查 | `Superpowers: requesting-code-review` |
| 浏览器/QA 测试 | `/browse` 或 `/qa` |
| 部署/发布 | `/ship` |
| 安全审计 | `/cso` |
| 多视角审查 | `/autoplan` |

**第一反应原则**: 收到请求后，**先查表确定 Skill**，再行动。

## 阶段流程
brainstorming → writing-plans → TDD → code-review → QA → ship

**任何阶段不得跳过前置阶段**。

## 会话启动检查
1. `git status` → 检查未提交变更
2. `TaskList` → 检查未完成任务
3. 读取 `PROJECT_OVERVIEW.md` → 确认项目状态

---
详细配置：docs/superpowers/README.md
```

- [ ] **Step 2: 提交**

```bash
git add CLAUDE.md
git commit -m "refactor: simplify CLAUDE.md to core routing rules"
```

---

### Task 3: 创建详细配置文档

**Files:**
- Create: `docs/superpowers/README.md`

- [ ] **Step 1: 创建详细配置文档**

```markdown
# Superpowers + gstack 配置详情

本文档是根目录 CLAUDE.md 的详细扩展。

## 分工原则

| 层级 | 负责内容 | 触发方式 |
|-----|---------|---------|
| Superpowers | 思考与流程层（plan、brainstorm、debug、TDD、verify、code review） | 自动触发 |
| gstack | 执行与外部世界层（浏览器、QA、ship、deploy、canary、安全审计） | 斜杠命令手动触发 |

## 浏览器规则
- 使用 `/browse` 作为唯一浏览器入口
- 禁止使用 `mcp__claude-in-chrome__*` 操作浏览器

## 任务管理

所有多步骤任务必须使用 TaskCreate 追踪：

1. brainstorming 完成后 → 立即创建任务列表
2. 每个阶段开始前 → TaskUpdate 标记为 in_progress
3. 每个阶段完成后 → TaskUpdate 标记为 completed
4. 会话恢复时 → TaskList 检查未完成任务

### 任务依赖关系
```
brainstorming → writing-plans → TDD → code-review → QA → ship
```

## 阶段验收标准

| 阶段 | 完成标准 | 产出物 |
|------|----------|--------|
| brainstorming | 需求明确、边界清晰、用户确认 | 需求摘要（对话记录） |
| writing-plans | 计划文档已写、/autoplan 审查通过 | docs/superpowers/specs/*.md |
| TDD | 测试用例已写、测试全过 | 测试文件 + 实现代码 |
| code-review | 审查通过、无 blocking issue | PR 或 git diff |
| QA | /qa 验证通过、无 console error | QA 报告 |
| ship | 已合并、已发布、更新 VERSION | git commit + tag |

## 违规信号

出现以下想法时立即停止：
- "这个简单，直接写就行" → STOP → 查表调用 TDD
- "我只是解释一下概念" → STOP → 确认是否涉及代码/实现
- "先快速试一下" → STOP → 先写测试

## Available gstack skills

/office-hours, /plan-ceo-review, /plan-eng-review,
/plan-design-review, /design-consultation, /design-shotgun, /design-html,
/review, /ship, /land-and-deploy, /canary, /benchmark, /browse, /qa,
/qa-only, /design-review, /setup-browser-cookies, /setup-deploy, /retro,
/investigate, /document-release, /codex, /cso, /autoplan, /pair-agent,
/careful, /freeze, /guard, /unfreeze, /gstack-upgrade, /learn
```

- [ ] **Step 2: 提交**

```bash
git add docs/superpowers/README.md
git commit -m "docs: create detailed superpowers configuration guide"
```

---

### Task 4: 创建 Hooks 配置文档

**Files:**
- Create: `.claude/hooks/README.md`

- [ ] **Step 1: 创建 Hooks 配置说明**

```markdown
# Hooks 配置说明

## 什么是 Hooks

Hooks 是 Claude Code 的自动化脚本，在特定事件发生时触发。

## 当前配置的 Hooks

### PreToolUse (工具使用前)
- 拦截危险命令（rm -rf, DROP TABLE 等）
- 确认敏感操作

### PostToolUse (工具使用后)
- 自动格式化代码
- 更新相关文件

### SessionStart (会话启动)
- 自动执行环境检查
- 加载项目上下文

## 配置文件位置
- Hooks 配置：`.claude/settings.json`
- Hook 脚本：`.claude/hooks/*.sh`

## 添加新 Hook

1. 使用 `/hooks` 命令交互式配置
2. 或手动编辑 `.claude/settings.json`

## 安全钩子示例

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {"tool": "Bash", "command": "rm.*-rf"},
        "command": "echo 'Warning: Destructive command detected. Proceed?' && read -r"
      }
    ]
  }
}
```

## 参考资料
- [官方 Hooks 文档](https://code.claude.com/docs/en/hooks)
- [Hooks 完整参考](https://code.claude.com/docs/en/hooks-reference)
```

- [ ] **Step 2: 提交**

```bash
git add .claude/hooks/README.md
git commit -m "docs: add hooks configuration guide"
```

---

### Task 5: 创建编码约定文档

**Files:**
- Create: `docs/CODING_CONVENTIONS.md`

- [ ] **Step 1: 创建编码约定文档**

```markdown
# 编码约定

## Python 代码风格

- 遵循 PEP 8
- 使用 4 空格缩进
- 函数名：snake_case
- 类名：PascalCase
- 常量：UPPER_CASE

## 类型注解

所有公共函数必须有类型注解：

```python
def process_user_data(user_id: str, options: dict[str, Any]) -> UserResult:
    """处理用户数据。
    
    Args:
        user_id: 用户唯一标识符
        options: 处理选项
        
    Returns:
        处理结果
    """
```

## 错误处理

```python
try:
    result = await api.call()
except APIError as e:
    logger.error(f"API 调用失败：{e}")
    raise ServiceUnavailableError("暂时无法处理请求") from e
```

## 测试约定

- 测试文件：`tests/<module>/test_<feature>.py`
- 使用 pytest
- 每个公共函数至少一个测试用例
- 测试命名：`test_<function>_<scenario>_<expected>`

## 提交信息

```
<type>: <subject>

<body>

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Type 类型
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 重构
- `docs`: 文档更新
- `test`: 测试相关

---

## 前端代码风格 (React)

- 使用 TypeScript
- 函数组件 + Hooks
- 组件名：PascalCase
- props 类型定义使用 interface
```

- [ ] **Step 2: 提交**

```bash
git add docs/CODING_CONVENTIONS.md
git commit -m "docs: add coding conventions guide"
```

---

## 自检验

- [ ] **Spec coverage:** 检查是否覆盖了所有需要补充的内容
  - [x] Anthropic 官方 CLAUDE.md 最佳实践
  - [x] Hooks/harness 最佳实践
  - [x] 与现有 Superpowers + gstack 配置结合

- [ ] **Placeholder scan:** 搜索计划中的 red flags
  - [x] 无 "TBD", "TODO", "implement later"
  - [x] 所有步骤都有具体内容和代码示例

- [ ] **Type consistency:** 检查文件名和路径一致性
  - [x] 所有文件路径一致
  - [x] 文档引用正确

---

## 执行选项

计划已保存到 `docs/superpowers/plans/2026-04-13-claude-md-improvement.md`。

**两个执行选项：**

1. **Subagent-Driven（推荐）** - 每个任务派遣独立 subagent 执行，任务间审查，快速迭代

2. **Inline Execution** - 在当前会话中批量执行任务，设置检查点

选择哪个方式？
