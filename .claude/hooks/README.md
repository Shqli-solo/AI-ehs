# Claude Code Hooks 配置指南

## 什么是 Hooks

Hooks 是 Claude Code 的自动化脚本，在特定事件发生时自动触发。通过配置 Hooks，可以实现：
- **自动化安全检查**：在执行危险命令前拦截并确认
- **自动格式化**：代码修改后自动运行格式化工具
- **环境初始化**：会话启动时自动加载项目上下文

---

## 当前配置的 Hooks

### 1. PreToolUse（工具使用前）
在工具执行**之前**触发，用于：
- 拦截危险命令（如 `rm -rf`、`DROP TABLE`）
- 确认敏感操作（如 force push、生产环境部署）
- 验证操作权限

### 2. PostToolUse（工具使用后）
在工具执行**之后**触发，用于：
- 自动格式化代码（Prettier、Black 等）
- 更新相关文件（如 VERSION、CHANGELOG）
- 运行测试用例

### 3. SessionStart（会话启动）
在会话**开始时**触发，用于：
- 自动执行环境检查
- 加载项目上下文（读取 CLAUDE.md、VERSION）
- 检查未完成任务（TaskList）

---

## 配置文件位置

| 类型 | 路径 |
|------|------|
| Hooks 配置 | `.claude/settings.json` |
| Hook 脚本 | `.claude/hooks/*.sh` |

---

## 添加新 Hook 的两种方法

### 方法一：使用 /hooks 命令（推荐）
```bash
/hooks add PreToolUse --command "your-command-here"
```

### 方法二：手动编辑 settings.json
在 `.claude/settings.json` 中添加：
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "name": "security-check",
        "command": "./.claude/hooks/security-check.sh",
        "when": "always"
      }
    ]
  }
}
```

---

## 安全钩子示例

以下是拦截危险 Git 命令的 PreToolUse 钩子配置：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "name": "git-force-push-warning",
        "type": "PreToolUse",
        "command": "bash -c 'if [[ \"$*\" == *\"--force\"* ]]; then echo \"WARNING: Force push detected! Confirm?\"; read confirm; if [[ \"$confirm\" != \"y\" ]]; then exit 1; fi; fi'",
        "matchTools": ["Bash"],
        "pattern": "git.*push.*--force"
      },
      {
        "name": "rm-recursive-warning",
        "type": "PreToolUse",
        "command": "echo \"Destructive operation detected. Proceed with caution.\"",
        "matchTools": ["Bash"],
        "pattern": "rm -rf"
      }
    ]
  }
}
```

---

## 参考资料

- [Claude Code Hooks 官方文档](https://docs.anthropic.com/claude-code/hooks)
- [Hooks 最佳实践](https://docs.anthropic.com/claude-code/hooks-best-practices)
