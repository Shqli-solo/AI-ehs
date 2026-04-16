# 微信/飞书远程操控 Claude Code 完全指南

> **适合场景**：通勤路上、出差途中、不在电脑旁时，用手机给 Claude Code 下达命令

---

## 一、主流方案对比

| 方案 | 支持平台 | 配置难度 | 费用 | 安全性 |
|------|----------|----------|------|--------|
| **cc-connect** | 微信/飞书/钉钉 | ⭐⭐ 简单 | 免费 | 本地部署 |
| **Hapi** | 微信/飞书 | ⭐⭐⭐ 中等 | 免费 | 本地部署 |
| **OpenClaw/IMClaw** | 微信/飞书 | ⭐⭐⭐⭐ 较复杂 | 免费 | 完全自控 |
| **feishu-claudecode** | 飞书 | ⭐⭐ 简单 | 免费 | 本地部署 |

---

## 二、方案 A：cc-connect（推荐新手）

### 快速配置（10 分钟）

**Step 1：安装依赖**
```bash
npm install -g cc-connect
```

**Step 2：获取飞书/微信凭证**
- 飞书：登录 [飞书开放平台](https://open.feishu.cn/) → 创建企业自建应用
- 复制 `App ID` 和 `App Secret`

**Step 3：配置文件**
创建 `.env` 文件：
```env
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_APP_TOKEN=your_app_token
```

**Step 4：启动 Bridge**
```bash
cc-connect start
```

**Step 5：手机测试**
在飞书/微信中发送：`/status`
收到回复即配置成功！

---

## 三、方案 B：OpenClaw/IMClaw（推荐进阶）

### 核心优势
- ✅ 支持 **ACP 协议**（AI Communication Protocol）
- ✅ 可执行系统命令、浏览网页、管理文件、编写代码
- ✅ 数据隐私完全掌控，无需担心第三方

### 配置步骤
1. 克隆仓库：`git clone https://github.com/OpenClaw/IMClaw.git`
2. 安装依赖：`npm install`
3. 配置 `.env` 文件（微信/飞书凭证）
4. 启动服务：`npm run start`
5. 手机扫码绑定设备

详细教程：[OpenClaw 保姆级飞书对接指南](https://www.cnblogs.com/catchadmin/p/19592309)

---

## 四、手机可用的核心命令

```
/chat          → 切换到聊天模式
/status        → 查看当前状态
/resume        → 恢复历史会话
/commit        → 提交代码
/diff          → 查看变更
/compact       → 压缩上下文
/help          → 查看帮助
```

---

## 五、安全建议

1. **双重验证**：开启账号 + 链接验证
2. **白名单机制**：只允许特定账号访问
3. **命令审计**：定期查看执行日志
4. **敏感操作限制**：禁止 `rm -rf` 等危险命令

---

## 参考来源

- [cc-connect 知乎教程](https://zhuanlan.zhihu.com/p/2011382144056968276)
- [Hapi 腾讯云教程](https://cloud.tencent.com/developer/article/2645468)
- [OpenClaw 53AI 报道](https://www.53ai.com/news/Openclaw/2026032373016.html)
- [feishu-claudecode 知乎专栏](https://zhuanlan.zhihu.com/p/2003604523235698469)
