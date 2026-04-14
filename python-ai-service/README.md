# EHS 智能安保决策中台 - Python AI 服务

## 架构说明

基于 FastAPI + LangGraph + GraphRAG 的 AI 服务，提供：
- GraphRAG 知识检索（ES + Milvus + Neo4j）
- Multi-Agent 协同编排
- LLMOps 评估

## 快速开始

### 方式一：Docker Compose 启动（推荐）

```bash
# 复制配置模板
cp .env.example .env

# 启动所有服务（Elasticsearch + Milvus + AI Service）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式二：本地开发

```bash
# 复制配置模板
cp .env.example .env

# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn src.api.rest:app --reload --host 0.0.0.0 --port 8000
```

### 运行测试
```bash
pytest tests/ -v
```

## 目录结构
```
src/
├── api/       # REST API
├── core/      # 核心配置
├── rag/       # GraphRAG 引擎
├── agents/    # Multi-Agent 编排
└── shared/    # 共享模块
```
