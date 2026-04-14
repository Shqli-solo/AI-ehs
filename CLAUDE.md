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

**第一反应原则**: 收到请求后，**第一个动作**是查表确定 Skill，而不是直接回答或执行。

## 阶段流程（完整顺序 - 超级重要）

**实际执行流程（12 阶段）：**
```
/office-hours → brainstorming → writing-plans → TDD → code-review → QA → /cso → ship → canary → benchmark → document-release → retro
```

**详细说明：**

| 阶段 | 技能 | 说明 | 是否必须 |
|------|------|------|----------|
| 0. /office-hours | `/office-hours` | 产品创意、需求澄清、价值判断 | ✅ 必须 |
| 1. brainstorming | `Superpowers: brainstorming` | 创意发散、需求细化 | ✅ 必须 |
| 2. writing-plans | `Superpowers: writing-plans` + `/autoplan` | 撰写实施计划、多视角审查 | ✅ 必须 |
| 3. TDD | `Superpowers: test-driven-development` | 测试驱动开发 | ✅ 必须 |
| 4. code-review | `Superpowers: requesting-code-review` | 代码审查 | ✅ 必须 |
| 5. QA | `/qa` 或 `/browse` | 浏览器测试、端到端验证 | ✅ 必须 |
| 6. /cso | `/cso` | 安全审计 | ✅ 必须 |
| 7. ship | `/ship` | 发布上线 | ✅ 必须 |
| 8. canary | `/canary` | 金丝雀发布（小流量验证） | ⚠️ 可选 |
| 9. benchmark | `/benchmark` | 性能基准测试 | ⚠️ 可选 |
| 10. document-release | `document-release` | 文档同步更新 | ✅ 必须 |
| 11. retro | `/retro` | 项目复盘 | ✅ 必须 |

**铁律：**
1. 任何阶段不得跳过前置阶段
2. 每个阶段完成后必须通过验证门（verification gate）
3. 发现问题必须回退到对应阶段修复

## 会话启动检查
1. `git status` → 检查未提交变更
2. `TaskList` → 检查未完成任务
3. 读取 `PROJECT_OVERVIEW.md` → 确认项目状态

---
详细配置：docs/superpowers/README.md
记住，后续所有项目的git commit,commit的消息使用中文