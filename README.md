# EHS 智能安保决策中台

> 基于 GraphRAG + Multi-Agent + 多模态的智能安保决策系统

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)](https://fastapi.tiangolo.com/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2-brightgreen)](https://spring.io/projects/spring-boot)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    Admin Console (Next.js)                   │
│  告警管理 │ 预案检索 │ 知识图谱可视化 │ 多模态上报           │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST
┌───────────────────────▼─────────────────────────────────────┐
│              EHS AI Service (Python + FastAPI)               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  GraphRAG 增强检索                                   │    │
│  │  ┌──────────────┐  ┌────────────┐  ┌─────────────┐  │    │
│  │  │ Knowledge    │  │ BM25       │  │ Vector      │  │    │
│  │  │ Graph (NX)   │──►│ (ES)       │  │ (Milvus)    │  │    │
│  │  └──────────────┘  └────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  LangGraph Multi-Agent Workflow                      │    │
│  │  Risk Perception → Plan Retrieval → Output          │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Ollama Qwen3 │  │ MinIO        │  │ PostgreSQL       │  │
│  │ (LLM)        │  │ (Multimodal) │  │ (Business Data)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │ gRPC
┌───────────────────────▼─────────────────────────────────────┐
│           EHS Business Service (Java + Spring Boot)          │
│  COLA 架构 │ JWT Auth │ JPA │ gRPC Client                   │
└─────────────────────────────────────────────────────────────┘
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14, TypeScript, TailwindCSS |
| AI 服务 | Python 3.11, FastAPI, LangGraph, Pydantic, NetworkX |
| 业务服务 | Java 17, Spring Boot 3.2, COLA 4.x, gRPC |
| LLM | Ollama + Qwen3-7B |
| 检索 | Elasticsearch (BM25) + Milvus (向量) |
| 知识图谱 | NetworkX (GraphRAG) |
| 多模态 | MinIO (图片/视频存储) |
| 数据库 | PostgreSQL 16 |
| 部署 | Docker Compose |

## 快速开始

### 1. 启动所有服务

```bash
./scripts/start.sh
```

### 2. 拉取 LLM 模型（首次）

```bash
./scripts/start.sh --pull-model
```

### 3. 导入种子数据

```bash
./scripts/start.sh --seed
```

### 4. 访问系统

- 前端管理控制台: http://localhost:3000
- AI 服务 API: http://localhost:8000/health
- 业务服务 API: http://localhost:8080/actuator/health
- MinIO 控制台: http://localhost:9001 (minioadmin/minioadmin)
- Elasticsearch: http://localhost:9200

## 核心特性

### GraphRAG vs 传统 RAG

**传统 RAG 的局限：**
- 只能检索独立文档片段，无法理解实体间的关系
- 例："A 栋 3 楼火灾" → 只能找到包含这些词的文档
- 但无法回答："A 栋和 B 栋之间有连廊，火势会蔓延吗？需要疏散哪些区域？"

**GraphRAG 的优势：**
- 构建知识图谱：建筑 → 楼层 → 房间 → 设备 → 危险源 → 应急预案
- 查询时先检索相关子图，再结合子图上下文进行 RAG
- "A 栋火灾" → 发现 "A 栋与 B 栋有连廊" → "B 栋有化学品仓库，需要额外疏散"

### 多模态告警

支持上传图片 + 文本描述 + 传感器数据的多模态告警输入：
1. 上传图片到 MinIO 存储
2. 多模态 LLM 分析图片内容（识别火焰、烟雾等）
3. 合并图片分析结果 + 文本告警 → RiskAgent 风险评估
4. 返回风险等级和关联预案

### 知识图谱可视化

前端 `/graph` 页面展示园区知识图谱：
- 建筑、楼层、设备、危险源的关系可视化
- 查询相关子图
- 风险路径高亮

### 模型微调

提供完整的 LoRA 微调流程：
1. 从种子数据生成 instruction-tuning 格式数据
2. 使用 unsloth/LLaMA-Factory 进行 LoRA 微调
3. 导出为 GGUF 格式，导入 Ollama 使用

## 项目结构

```
mianshi/
├── apps/
│   ├── ehs-ai/              # Python AI 服务（FastAPI）
│   │   ├── src/
│   │   │   ├── core/        # 核心域
│   │   │   │   ├── graph_rag/       # GraphRAG 模块
│   │   │   │   │   ├── knowledge_graph.py  # 知识图谱
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── graph_rag.py     # GraphRAG 核心检索
│   │   │   │   ├── agents/          # Multi-Agent 工作流
│   │   │   │   └── config.py        # 配置管理
│   │   │   ├── adapters/
│   │   │   │   ├── primary/         # 主适配器（REST API）
│   │   │   │   └── secondary/       # 次级适配器（ES, Milvus, MinIO）
│   │   │   └── container.py         # 依赖注入容器
│   │   └── Dockerfile
│   ├── ehs-business/        # Java 业务服务（Spring Boot）
│   │   └── Dockerfile
│   └── admin-console/       # 前端管理控制台（Next.js）
│       └── Dockerfile
├── data/
│   └── seed/                # 种子数据
│       ├── plans.jsonl          # 30+ 预案
│       ├── alerts.jsonl         # 20+ 告警
│       └── knowledge_graph.json # 知识图谱数据
├── scripts/
│   ├── start.sh             # 启动脚本
│   ├── pull_model.sh        # 拉取 LLM 模型
│   ├── seed_data.py         # 数据导入脚本
│   └── fine_tune.py         # 微调脚本
├── docker-compose.yml       # 全栈 Docker Compose
├── .env.example             # 环境变量模板
└── README.md                # 本文件
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/auth/login` | 用户登录 |
| POST | `/api/alert/report` | 告警上报 |
| POST | `/api/alert/report/multimodal` | 多模态告警上报 |
| POST | `/api/plan/search` | 预案检索（GraphRAG） |
| GET | `/api/alert/list` | 告警列表 |
| GET | `/api/stats/today` | 今日统计 |
| GET | `/api/graph` | 知识图谱数据 |
| GET | `/api/graph/buildings/{name}/connected` | 建筑关联查询 |

## 开发

### Python 服务

```bash
cd apps/ehs-ai
poetry install
poetry run uvicorn src.adapters.primary.rest_api:app --reload --host 0.0.0.0 --port 8000
```

### Java 服务

```bash
cd apps/ehs-business
mvn spring-boot:run
```

### 前端

```bash
cd apps/admin-console
pnpm install
pnpm dev
```

## 面试演示流程

```bash
# 1. 启动所有服务
./scripts/start.sh

# 2. 等待 Ollama 模型就绪（首次需要下载模型）
./scripts/start.sh --pull-model

# 3. 导入种子数据
./scripts/start.sh --seed

# 4. 打开前端: http://localhost:3000

# 5. 演示流程:
#    a. 查看告警列表（真实数据，非 mock）
#    b. 告警上报 → AI 分析 → 返回风险等级和预案
#    c. 预案检索（对比 GraphRAG vs 传统 RAG 效果）
#    d. 知识图谱可视化页面（展示 GraphRAG 价值）
#    e. 多模态告警（上传图片 → AI 分析）
#    f. 讲解架构：COLA + 六边形 + LangGraph + GraphRAG
```

## 微

```bash
# 生成微调数据
python scripts/fine_tune.py generate

# 生成训练脚本
python scripts/fine_tune.py train

# 生成 GGUF 导出配置
python scripts/fine_tune.py export

# 执行全部
python scripts/fine_tune.py all
```

## License

MIT

**GitHub:** https://github.com/Shqli-solo/AI-ehs
