# EHS 智能安保决策中台 - Python AI 服务

## 架构说明

基于 FastAPI + LangGraph + GraphRAG 的 AI 服务，提供：
- GraphRAG 知识检索（ES + Milvus + Neo4j）
- Multi-Agent 协同编排
- LLMOps 评估

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行服务
```bash
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
