# AI 开发者深度使用指南
## 算法工程师 / AI 全栈开发 / AI 应用架构师

> **适合人群**：算法工程师、AI 全栈开发、AI 应用架构师
> **阅读时间**：15 分钟 | **难度**：小白友好

---

## 一、角色定位与核心场景

### 🧠 算法工程师

| 场景 | 推荐命令/功能 | 提效倍数 |
|------|---------------|----------|
| 数据预处理代码生成 | `/init` + 自然语言描述 | 5-10x |
| 模型训练脚本调试 | `/debug` + 错误日志 | 3-5x |
| 实验配置管理 | CLAUDE.md 记录实验参数 | 2-3x |
| 论文代码复现 | 上传论文 PDF + `/explain` | 5-8x |

### 🚀 AI 全栈开发

| 场景 | 推荐命令/功能 | 提效倍数 |
|------|---------------|----------|
| 前端页面生成 | 描述需求 + `/plan` | 10-20x |
| API 接口开发 | MCP 连接数据库 + 自然语言 | 5-10x |
| 测试用例编写 | `/test` + 覆盖率要求 | 3-5x |
| 部署脚本配置 | Docker/K8s 配置生成 | 5-8x |

### 🏗️ AI 应用架构师

| 场景 | 推荐命令/功能 | 提效倍数 |
|------|---------------|----------|
| 架构设计评审 | `/review` + 架构图 | 3-5x |
| 技术选型分析 | 自然语言对比 + `/docs` | 5-10x |
| 安全审计 | `/security-review` | 5-8x |
| 团队规范制定 | `/init` 生成 CLAUDE.md | 5-10x |

---

## 二、核心功能详解（小白都能懂）

### 1. CLAUDE.md — AI 的"项目说明书"

**什么是 CLAUDE.md？**

简单说，就是告诉 AI：这个项目怎么跑、怎么写代码、怎么测试。

**示例配置**：
```markdown
# 项目规范

## 技术栈
- 前端：Next.js 14 + TypeScript + Tailwind
- 后端：FastAPI + PostgreSQL
- AI：Anthropic Claude API

## 代码风格
- 函数式优先
- 所有函数必须有类型注解
- 禁止使用 any 类型

## 测试要求
- 单元测试覆盖率 > 80%
- 所有 API 必须有集成测试
```

**怎么用？**

在项目根目录运行：`/init`
AI 会自动生成 CLAUDE.md 草稿！

---

### 2. MCP — AI 的"外部工具接口"

**什么是 MCP？**

让 Claude 能连接数据库、调用 API、读写文件的协议。

**典型配置**：
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
  }
}
```

**效果**：

配置后可以直接说："帮我查一下 users 表里有多少用户"，AI 会自动执行 SQL！

---

### 3. Plan Mode — AI 的"三思而后行"

**什么时候用？**
- 重构大型模块
- 添加核心功能
- 修复复杂 Bug

**怎么用？**
1. 输入：`/plan` 或设置 `--permission-mode=plan`
2. AI 先输出完整计划
3. 你确认后再执行

---

## 三、工作流模板

### 算法工程师日常

```
早上到公司 → /resume 恢复会话
           → /status 看昨晚实验结果
           → 让 AI 分析日志找出问题
           → 修改训练脚本
           → 启动新实验

下午 → 让 AI 生成可视化代码
     → 生成实验报告草稿
     → /commit 提交代码
```

### 全栈开发日常

```
需求评审后 → /plan 撰写实现计划
          → AI 生成前端页面
          → AI 生成后端 API
          → AI 生成测试用例
          → 运行测试 /test
          → 修复问题
          → /commit → /github pr create
```

### 架构师日常

```
新项目启动 → /init 生成项目规范
          → /plan 架构设计方案
          → /review 代码审查
          → /security-review 安全审计
          → /insights 生成项目报告
```

---

## 四、避坑指南

| 坑 | 解决方案 |
|----|----------|
| 上下文超限 | 定期 `/compact` 压缩 |
| AI 乱改代码 | 用 `--permission-mode=plan` 先审核 |
| 忘记会话内容 | 用 `/resume <session-id>` 恢复 |
| 权限太松 | 用 `--allowed-tools` 限制工具 |
| 模型太贵 | 简单任务用 `-m haiku` |

---

## 五、内置斜杠命令大全

### 通用高频命令

| 命令 | 用途 |
|------|------|
| `/status` | 查看当前状态（模式/目录/权限） |
| `/resume` | 恢复历史会话（支持搜索） |
| `/compact` | 压缩上下文（节省 token） |
| `/clear` | 清空当前上下文 |
| `/extensions` | 管理 MCP 扩展 |
| `/allow` | 管理工具权限 |
| `/ide` | 连接 IDE（VSCode/JetBrains） |
| `/models` | 切换模型 |
| `/theme` | 切换主题 |
| `/quit` 或 `/exit` | 退出 Claude Code |

### 开发者命令

| 命令 | 用途 |
|------|------|
| `/diff` | 查看本次会话所有代码变更 |
| `/commit` | Git 提交（可编辑 message） |
| `/chat` | 切换到纯聊天模式（不调用工具） |
| `/bugreport` | 生成详细 bug 报告 |

### 架构师命令

| 命令 | 用途 |
|------|------|
| `/review` | PR 代码审查 |
| `/security-review` | 安全审计 |
| `/insights` | 生成会话报告（决策/变更/原因） |
| `/team-onboarding` | 生成团队上手指南 |

---

## 参考来源

- [Claude Code 官方最佳实践](https://easyclaude.com/post/claude-code-official-best-practices)
- [CSDN 深度技术指南](https://aicoding.csdn.net/6965a3ed6554f1331aa19f41.html)
- [腾讯云全攻略](https://cloud.tencent.com/developer/article/2616765)
- [GitHub 企业级最佳实践](https://github.com/KimYx0207/Claude-Code-x-OpenClaw-Guide-Zh)
