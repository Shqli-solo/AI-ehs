---
name: must-follow-superpowers-gstack-workflow
description: 用户强烈要求遵循 Superpowers + gstack 流程，禁止跳过流程直接写代码
type: feedback
---

**规则：** 必须先查表确定调用的 Skill，不得跳过流程直接编码。

**Why:** 用户明确要求使用 Superpowers + gstack 的标准工作流（plan → review → TDD → QA → ship），直接写代码被视为没有原则、不专业。即使用户之前批评过项目质量，也不能以此为借口跳过流程。

**How to apply:** 收到编码任务时：
1. 先 `git status` + `TaskList` + 读取 CLAUDE.md 确认状态
2. 查表确定要用的 Skill（如 /office-hours → brainstorming → /autoplan → writing-plans → TDD）
3. 用 Skill 工具调用对应流程
4. 任何阶段不得跳过前置阶段