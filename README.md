# EHS 智能安保决策中台

企业级 AI 安保决策平台，基于 GraphRAG + Multi-Agent 架构，提供智能检索、Agent 编排、LLMOps 评估等能力。

**当前版本：** v2.0.0 (2026-04-16)

**项目状态：** ✅ 阶段 2 完成 - Monorepo 架构 + 生产级配置

## 快速开始

### Docker Compose 启动（推荐）

```bash
# 复制配置模板
cp apps/ehs-ai/.env.example .env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

服务启动后访问：
- AI Service: http://localhost:8000
- Elasticsearch: http://localhost:9200
- Milvus: localhost:19530

### 本地开发

```bash
# 安装依赖
pnpm install

# 启动前端开发服务器
pnpm dev

# 启动 Python AI 服务
cd apps/ehs-ai && poetry install && poetry run uvicorn src.api.rest:app --reload

# 启动 Java 业务服务
cd apps/ehs-business && mvn spring-boot:run
```

## 项目结构

```
mianshi/
├── apps/
│   ├── admin-console/       # Next.js 前端管理控制台
│   ├── ehs-ai/              # Python AI 服务 (FastAPI + LangGraph)
│   └── ehs-business/        # Java 业务服务 (Spring Boot + COLA + gRPC)
├── tests/
│   └── e2e/                 # Playwright E2E 测试
├── scripts/
│   ├── setup.sh             # 开发环境设置脚本
│   └── run-tests.sh         # 测试运行脚本
├── infra/
│   ├── docker/              # Docker 配置
│   ├── k8s/                 # Kubernetes 配置
│   └── docker-compose.yml   # Docker Compose 配置
├── docs/                    # 项目文档
├── docker-compose.yml       # 根 Docker Compose
├── package.json             # Monorepo 根配置
├── pnpm-workspace.yaml      # pnpm workspace 配置
├── Makefile                 # Make 命令入口
├── README.md                # 本文件
├── PROJECT_OVERVIEW.md      # 项目概览
├── CHANGELOG.md             # 变更日志
└── CLAUDE.md                # Claude 配置
```

## 技术栈

| 类别 | 技术选型 |
|------|----------|
| 前端 | Next.js 14, TypeScript, TailwindCSS, Shadcn UI |
| Python AI | FastAPI, LangGraph, PyTorch, BGE-Reranker |
| Java | Spring Boot 3, COLA 4, gRPC |
| 向量库 | Milvus, Elasticsearch |
| 测试 | Playwright, pytest, JUnit |
| 部署 | Docker, Kubernetes, Helm |

## 核心功能

### GraphRAG 检索引擎
- ES BM25 检索（支持降级处理）
- Milvus 向量检索（支持降级处理）
- BGE-Reranker 重排序
- 三路召回融合

### Multi-Agent 编排
- RiskAgent（风险感知，含 LLM JSON fallback）
- SearchAgent（预案检索）
- LangGraph 状态机（顺序执行：风险感知 → 预案检索）
- 错误降级处理

### REST API
- 告警上报接口（含 Pydantic 输入验证）
- 预案检索接口
- 健康检查接口
- CORS 跨域支持
- JWT 认证（可选）

### 前端页面
- Dashboard 仪表盘
- 告警管理页面
- 预案检索页面
- Ant Design + TailwindCSS

## 测试

```bash
# 运行 E2E 测试
pnpm test:e2e

# Python 测试
cd apps/ehs-ai && poetry run pytest

# Java 测试
cd apps/ehs-business && mvn test

# 前端测试
cd apps/admin-console && npm test
```

## 文档

- [项目概述](PROJECT_OVERVIEW.md)
- [测试指南](测试指南.md)
- [变更日志](CHANGELOG.md)
- [开发规范](docs/CODING_CONVENTIONS.md)
- [Superpowers 配置](docs/superpowers/README.md)

## 变更日志

### v2.0.0 (2026-04-16)

**新增**
- ✅ Monorepo 架构 (pnpm workspace)
- ✅ Next.js 前端 (apps/admin-console)
- ✅ Python FastAPI 服务 (apps/ehs-ai)
- ✅ Java Spring Boot 服务 (apps/ehs-business)
- ✅ JWT 认证中间件
- ✅ CORS 安全配置
- ✅ gRPC 双向通信

**修复**
- ✅ E2E 测试 API Mock
- ✅ 代码审查 Critical Issues
- ✅ Java 编译依赖问题

**测试覆盖**
- ✅ E2E 测试：26/26 通过
- ✅ Python 测试：35 用例
- ✅ Java 测试：10/10 通过

### v1.0.1 (2026-04-14)

- ✅ 阶段 1 MVP 完成
- ✅ GraphRAG 检索引擎
- ✅ Multi-Agent 编排
- ✅ 前端告警管理页面

## GitHub

https://github.com/Shqli-solo/AI-ehs

**PR #1:** [feat: 添加 JWT 认证和 CORS 安全配置](https://github.com/Shqli-solo/AI-ehs/pull/1)

---

License: MIT
