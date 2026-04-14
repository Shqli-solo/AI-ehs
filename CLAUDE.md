# EHS 智能安保决策中台 - 开发配置

面试准备项目 - 构建生产级开源 GitHub 项目，95% 覆盖简历中的 OpenClaw 和广汽 EHS 中台

## Skill Routing

| 请求类型 | 调用的 Skill |
|---------|-------------|
| 产品创意/需求澄清 | `/office-hours` |
| 头脑风暴/方案设计 | `Superpowers: brainstorming` |
| 计划撰写 | `Superpowers: writing-plans` |
| 多视角审查 | `/autoplan` |
| 编码实现 | `Superpowers: TDD` |
| 调试/修复 bug | `Superpowers: systematic-debugging` |
| 代码审查 | `Superpowers: requesting-code-review` |
| QA/浏览器测试 | `/qa` 或 `/browse` |
| 安全审计 | `/cso` |
| 发布上线 | `/ship` |
| 项目复盘 | `/retro` |

**第一反应原则**: 收到请求后，**第一个动作**是查表确定 Skill。

## 阶段流程

**完整顺序（15 阶段）：**
```
/office-hours → brainstorming → /autoplan → writing-plans → subagent-driven-development/TDD → QA → systematic-debugging → requesting-code-review → review → /cso → ship → canary → benchmark → document-release → retro
```

**铁律：** 任何阶段不得跳过前置阶段。QA 发现 bug → systematic-debugging → 重新 QA。

## 会话启动检查

1. `git status` → 检查未提交变更
2. `TaskList` → 检查未完成任务
3. 读取 `PROJECT_OVERVIEW.md` → 确认项目状态

## 详细文档

- 完整流程配置：[docs/superpowers/README.md](docs/superpowers/README.md)
- 测试指南：[测试指南.md](测试指南.md)
- 项目概览：[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

**Git 规范**: commit message 使用中文
