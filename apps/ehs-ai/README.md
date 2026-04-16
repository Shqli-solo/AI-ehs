# EHS AI Service

EHS 智能安保决策中台 - AI 服务（六边形架构）

## 架构概述

本项目采用六边形架构（Hexagonal Architecture），也称为端口和适配器架构（Ports and Adapters）。

### 目录结构

```
apps/ehs-ai/
├── src/
│   ├── core/                      # 核心域（业务逻辑）
│   │   ├── graph_rag.py           # GraphRAG 检索引擎
│   │   ├── agents/
│   │   │   ├── workflow.py        # Multi-Agent 工作流编排
│   │   │   ├── risk_agent.py      # 风险感知 Agent
│   │   │   └── search_agent.py    # 预案检索 Agent
│   │   └── config.py              # 配置管理
│   ├── adapters/
│   │   ├── primary/               # 主适配器（驱动适配器）
│   │   │   └── rest_api.py        # FastAPI REST API
│   │   └── secondary/             # 被驱动适配器
│   │       ├── elasticsearch.py   # ES 文本检索适配器
│   │       └── milvus.py          # Milvus 向量检索适配器
│   ├── ports/
│   │   └── secondary/
│   │       └── storage.py         # 存储端口接口定义
│   └── container.py               # 依赖注入容器
├── tests/
│   ├── __init__.py
│   ├── mocks.py                   # Mock 实现
│   └── test_hexagonal.py          # 六边形架构测试
├── docs/
│   ├── api/
│   │   └── openapi.yaml           # OpenAPI 规范
│   └── api-examples.md            # API 使用示例
└── pyproject.toml
```

### 架构分层说明

#### 核心域（Core Domain）
- **GraphRAGCore**: 两路召回 + 重排序的检索引擎
- **RiskAgent**: 基于 LLM 的风险评估 Agent
- **SearchAgent**: 预案检索 Agent
- **Workflow**: LangGraph 编排的工作流

#### 端口（Ports）
- **TextStoragePort**: 文本存储接口
- **VectorStoragePort**: 向量存储接口

#### 适配器（Adapters）
- **REST API**: FastAPI 主适配器，处理 HTTP 请求
- **ElasticsearchAdapter**: ES 文本检索实现
- **MilvusAdapter**: Milvus 向量检索实现

#### 依赖注入容器（DI Container）
- 支持 Mock/真实实现切换
- 统一管理和组装所有依赖

## 快速开始

### 安装依赖

```bash
cd apps/ehs-ai
pip install -r requirements.txt
```

### 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件配置服务地址
```

### 运行服务

```bash
python -m uvicorn src.adapters.primary.rest_api:app --reload --host 0.0.0.0 --port 8000
```

### 运行测试

```bash
pytest tests/test_hexagonal.py -v
```

## API 接口

### 健康检查
```bash
GET /health
```

### 告警上报
```bash
POST /api/alert/report
Content-Type: application/json

{
  "device_id": "DEV-001",
  "device_type": "烟雾探测器",
  "alert_type": "fire",
  "alert_content": "3 号楼 2 层检测到浓烟",
  "location": "3 号楼 2 层",
  "alert_level": 3
}
```

### 预案检索
```bash
POST /api/plan/search
Content-Type: application/json

{
  "query": "火灾应急处置",
  "event_type": "fire",
  "top_k": 5
}
```

## OpenAPI 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

或查看静态文档：
- [OpenAPI Spec](docs/api/openapi.yaml)
- [API 使用示例](docs/api-examples.md)

## 依赖注入使用示例

### 使用真实实现

```python
from src.container import DIContainer

container = DIContainer()
container.use_real_implementations()

# 获取服务
graph_rag = container.get_graph_rag()
workflow = container.get_workflow()
```

### 使用 Mock 实现

```python
from src.container import DIContainer

container = DIContainer()
container.use_mock_implementations()

# 获取 Mock 服务
graph_rag = container.get_graph_rag()
workflow = container.get_workflow()
```

## 测试覆盖

```
Name                                      Stmts   Miss  Cover
-------------------------------------------------------------
src/core/graph_rag.py                        26      2    92%
src/core/agents/workflow.py                  39      5    87%
src/container.py                             85     31    64%
src/ports/secondary/storage.py                5      0   100%
```

## 技术栈

- **Python 3.11+**
- **FastAPI**: REST API 框架
- **LangGraph**: Agent 工作流编排
- **Pydantic**: 数据验证
- **Elasticsearch**: 文本检索
- **Milvus**: 向量数据库
- **Sentence Transformers**: Embedding 编码
- **pytest**: 单元测试

## 架构优势

1. **可测试性**: 通过 Mock 实现，无需真实依赖即可测试
2. **可扩展性**: 新增存储实现只需实现对应端口接口
3. **可替换性**: 可以轻松替换底层实现（如 ES → OpenSearch）
4. **清晰分离**: 核心业务逻辑与外部依赖完全解耦
