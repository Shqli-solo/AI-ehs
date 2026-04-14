# EHS 智能安保决策中台

企业级 AI 安保决策平台，基于 GraphRAG + Multi-Agent 架构，提供智能检索、Agent 编排、LLMOps 评估等能力。

**当前版本：** v1.0.1 (2026-04-14)

**项目状态：** ✅ 阶段 1 MVP 完成 - 支持端到端演示

## 快速开始

### Docker Compose 启动（推荐）

```bash
# 复制配置模板
cp python-ai-service/.env.example .env

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
cd python-ai-service
cp .env.example .env
pip install -r requirements.txt
uvicorn src.api.rest:app --reload
```

## 项目结构

```
mianshi/
├── python-ai-service/     # Python AI 服务
│   ├── src/
│   │   ├── api/          # REST API
│   │   ├── core/         # 核心配置
│   │   ├── rag/          # GraphRAG 引擎
│   │   ├── agents/       # Multi-Agent 编排
│   │   └── shared/       # 共享模块
│   ├── .env.example      # 配置模板
│   └── README.md
├── docker-compose.yml     # Docker 编排
├── docs/                  # 项目文档
└── PROJECT_OVERVIEW.md    # 项目概述
```

## 技术栈

| 类别 | 技术选型 |
|------|----------|
| 后端 | Python 3.11+, FastAPI, LangGraph |
| 向量库 | Milvus, Elasticsearch |
| 图数据库 | Neo4j |
| LLM | Claude API, Qwen, vLLM |
| 评估 | Ragas, LangFuse |

## 文档

- [项目概述](PROJECT_OVERVIEW.md)
- [超级能力配置](docs/superpowers/README.md)
- [测试指南](测试指南.md)
- [发布日志](CHANGELOG.md)
- [TODOs](TODOS.md)

## 变更日志

### v1.0.1 (2026-04-14)

**新增**
- ✅ Docker 配置和 docker-compose.yml
- ✅ 端到端测试验证
- ✅ 前端告警管理页面（React + Ant Design）
- ✅ Python FastAPI REST API
- ✅ GraphRAG 检索引擎（ES + Milvus + Reranker）
- ✅ Multi-Agent 编排（LangGraph）

**修复**
- ✅ TypeScript 编译错误
- ✅ 代码审查发现的问题

**下一步（阶段 2）**
- 接入真实数据库（Elasticsearch、Milvus）
- 替换 Mock 模型为真实 LLM
- 完善测试覆盖（目标 80%）
- CI/CD 流水线配置
