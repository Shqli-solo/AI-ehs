---
name: 流程顺序 - brainstorming/office-hours 后必须执行 writing-plans
description: 完成 brainstorming 和 office-hours 后，不能直接执行任务，必须先调用 writing-plans 创建实施计划
type: feedback
---

**流程顺序错误坑点：** brainstorming 产出设计文档、office-hours 产出 product-brief.md 后，**不能直接开始执行任务**。

**正确流程：**
1. brainstorming → 设计文档（docs/superpowers/specs/*.md）
2. office-hours → product-brief.md
3. **writing-plans → 实施计划（docs/superpowers/plans/*.md）** ← 这一步不能跳过
4. subagent-driven-development / executing-plans → 按计划执行

**错误表现：** 在设计文档和 product-brief 完成后，直接开始创建任务、写代码。

**为什么错了：** writing-plans 会产出 TDD 风格的详细计划，包含：
- 每个任务的具体文件路径
- 每个步骤的代码/测试内容
- 精确的 git 提交命令
- 验收标准

跳过这一步会导致实施过程缺乏指导，容易偏离设计。

**How to apply：** 任何新阶段开始时（如阶段 1.2 项目骨架搭建），先调用 writing-plans 创建该阶段的实施计划，再执行。
