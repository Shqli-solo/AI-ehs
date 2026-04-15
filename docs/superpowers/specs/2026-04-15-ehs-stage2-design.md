# EHS 智能安保决策中台 - 阶段 2 设计文档

> **版本**: v2.0.0-draft  
> **创建日期**: 2026-04-15  
> **作者**: AI + 开发者  
> **状态**: DRAFT  
> **模式**: 渐进式重构  
> **TOGAF ADM 阶段**: A-H 完整覆盖  
> **DDD**: 战略设计 + 战术设计  

---

## 1. 项目概述

### 1.1 阶段 1 回顾

阶段 1 MVP（v1.0.1）已完成：
- ✅ GraphRAG 检索引擎（ES + Milvus 两路召回 + Reranker）
- ✅ Multi-Agent 编排（RiskAgent + SearchAgent，LangGraph）
- ✅ 前端告警管理页面（React 18 + Ant Design）
- ✅ REST API（FastAPI）
- ✅ Docker Compose 部署
- ✅ 端到端测试验证（4 场景通过）

**阶段 1 技术债务：**
- Mock 数据（FakeListLLM，无真实数据库）
- 无单元测试（覆盖率 ~0%）
- 架构分层不清晰（缺少六边形/DDD）
- 无模型微调（无 PyTorch/Transformers）
- 无本地模型部署（无 vLLM/TensorRT）
- 无 RAG 评估（无 Ragas/LangFuse）
- 无监控（无 Prometheus/Grafana）

### 1.2 阶段 2 目标

**从 MVP 到生产级**，完整覆盖简历技能：

| 技能类别 | 具体技术 | 简历体现 |
|---------|---------|---------|
| **前端** | Next.js 14 + TS + Tailwind + Shadcn | 7 个完整页面，参考 Dify |
| **后端架构** | Java COLA + DDD + gRPC + Spring Boot | 六边形架构、领域建模 |
| **AI 服务** | Python 六边形 + GraphRAG + Multi-Agent | RAG + Agent 编排 |
| **深度学习** | PyTorch + Transformers + 微调 | 指令微调、风险分级、合规检查 |
| **模型部署** | vLLM + TensorRT | 高性能推理服务 |
| **RAG 评估** | Ragas + LangFuse | Faithfulness > 0.9 |
| **监控** | Prometheus + Grafana | 全指标监控 |
| **部署** | Docker + K8s Helm + GitHub Actions | CI/CD 完整流水线 |
| **架构方法论** | TOGAF ADM + DDD | 企业架构能力 |

### 1.3 核心价值主张

- **事故响应时间**: 45min → 8min（82% 提升）
- **问答准确率**: 82% → 95%（13 个百分点）
- **人工复核**: 减少 70%
- **代码覆盖率**: 0% → 80%+
- **架构成熟度**: MVP → 生产级

---

## 2. 架构设计

### 2.1 系统上下文图（TOGAF 阶段 C）

```
┌─────────────────┐
│   用户 (EHS 总监)  │
│   值班经理       │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────────────────────────────┐
│                    前端应用层                            │
│              Next.js 14 + TypeScript                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │Dashboard│ │告警管理  │ │预案管理  │ │知识库   │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                   │
│  │Agent 编排│ │模型管理  │ │系统设置  │                   │
│  └─────────┘ └─────────┘ └─────────┘                   │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (HTTP)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Java 业务服务层 (COLA 架构)                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Client 层：gRPC Client (调用 Python AI 服务)       │   │
│  │  Interface 层：REST Controller + DTO             │   │
│  │  Domain 层：实体 + 值对象 + 聚合根 + 领域服务       │   │
│  │  Infrastructure 层：MySQL + gRPC + 事件发布        │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │ gRPC (Protocol Buffers)
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Python AI 服务层 (六边形架构)                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  驱动适配器：REST API (FastAPI)                  │   │
│  │  核心域：GraphRAG + Multi-Agent (LangGraph)      │   │
│  │  被驱动适配器：ES/Milvus/Neo4j/vLLM/TensorRT     │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│Elasticsearch│ │   Milvus    │ │    Neo4j    │
│ (文档检索)   │ │ (向量检索)   │ │  (图谱检索)  │
└─────────────┘ └─────────────┘ └─────────────┘
```

### 2.2 六边形架构（Python AI 服务）

```
┌─────────────────────────────────────────────────────────┐
│                   驱动适配器 (Driving)                   │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │  REST API    │  │  gRPC Server │                     │
│  │  (FastAPI)   │  │  (可选)       │                     │
│  └──────────────┘  └──────────────┘                     │
└────────────────────┬────────────────────────────────────┘
                     │ 端口 (Ports)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                     核心域 (Domain)                      │
│  ┌───────────────────────────────────────────────────┐ │
│  │  GraphRAG Engine                                   │ │
│  │  - ES Searcher (BM25)                             │ │
│  │  - Milvus Searcher (向量)                          │ │
│  │  - Neo4j Searcher (图谱)                          │ │
│  │  - BGE-Reranker (重排序)                          │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Multi-Agent Orchestration (LangGraph)            │ │
│  │  - RiskAgent (风险感知)                            │ │
│  │  - SearchAgent (预案检索)                         │ │
│  │  - PlannerAgent (规划，阶段 3)                     │ │
│  │  - ExecutorAgent (执行，阶段 3)                    │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Model Service (模型服务)                          │ │
│  │  - vLLM Inference (Qwen)                          │ │
│  │  - TensorRT Inference (BGE-Reranker)             │ │
│  │  - HuggingFace Transformers                       │ │
│  └───────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │ 端口 (Ports)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  被驱动适配器 (Driven)                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐  │
│  │    ES   │ │ Milvus  │ │  Neo4j  │ │   MinIO     │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────────┘  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐  │
│  │ vLLM    │ │TensorRT │ │ LangFuse│ │  Prometheus │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.3 COLA 架构（Java 业务服务）

```
┌─────────────────────────────────────────────────────────┐
│                    Client 层                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │  gRPC Client (调用 Python AI 服务)                 │   │
│  │  - RiskAssessmentClient                         │   │
│  │  - PlanSearchClient                             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Interface 层                            │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ REST Controller│  │  DTO/VO     │                    │
│  │ (Spring MVC) │  │  (数据传输)   │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Domain 层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Entity    │  │  Value Obj  │  │  Aggregate  │    │
│  │  (实体)      │  │  (值对象)    │  │  (聚合根)    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Domain Service (领域服务)              │   │
│  │  - AlertService (告警服务)                       │   │
│  │  - PlanService (预案服务)                        │   │
│  │  - WorkflowService (工作流服务)                  │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Domain Event (领域事件)                  │   │
│  │  - AlertCreatedEvent                            │   │
│  │  - PlanUpdatedEvent                             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure 层                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  MySQL Repo │  │  gRPC Impl  │  │  Event Pub  │    │
│  │  (数据持久化)│  │  (RPC 实现)   │  │  (事件发布)  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 2.4 数据架构（DDD）

**核心领域模型：**

```
┌─────────────────────────────────────────────────────────┐
│  Alert (告警聚合根)                                      │
│  ─────────────────────────────────────────────────────  │
│  - alertId: AlertId (值对象)                            │
│  - deviceId: DeviceId (值对象)                          │
│  - alertType: AlertType (枚举)                          │
│  - alertContent: string                                 │
│  - riskLevel: RiskLevel (枚举)                          │
│  - location: Location (值对象)                          │
│  - createdAt: Instant                                   │
│  - status: AlertStatus (枚举)                           │
│                                                          │
│  + assignRiskLevel(level): void                         │
│  + associatePlans(plans): void                          │
│  + markAsProcessing(): void                             │
│  + markAsResolved(): void                               │
└─────────────────────────────────────────────────────────┘
                        │
                        │ 关联
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Plan (预案聚合根)                                       │
│  ─────────────────────────────────────────────────────  │
│  - planId: PlanId                                       │
│  - title: string                                        │
│  - content: string                                      │
│  - riskLevel: RiskLevel                                 │
│  - version: int                                         │
│  - embedding: vector (Milvus)                           │
│  - keywords: list<string> (ES)                          │
│  - relations: list<PlanRelation> (Neo4j)                │
│                                                          │
│  + updateContent(content): void                         │
│  + publish(): void                                      │
│  + archive(): void                                      │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 微调方案

### 3.1 微调目标

| 微调类型 | 基础模型 | 训练目标 | 输入 | 输出 |
|---------|---------|---------|------|------|
| **指令微调** | Qwen-7B-Chat | 规范化输出格式 | 告警内容 + 指令 | 结构化 JSON（风险等级 + 处置建议） |
| **风险分级** | BERT-base | 分类风险等级 | 告警文本 | high/medium/low |
| **合规检查** | RoBERTa | 二分类（合规/不合规） | 预案文本 + 规则 | pass/fail + 原因 |
| **术语 Embedding** | BGE-base-zh | EHS 术语适配 | EHS 术语对 | 向量空间优化 |

### 3.2 训练数据准备

**数据来源：**
- 公开 EHS 预案（应急管理部、企业公示文档）
- LLM 生成变体（场景扩展、边缘案例）
- 人工校验（确保质量）

**数据规模：**
| 微调类型 | 训练样本 | 验证样本 | 测试样本 |
|---------|---------|---------|---------|
| 指令微调 | 500 | 100 | 100 |
| 风险分级 | 1000 | 200 | 200 |
| 合规检查 | 300 | 60 | 60 |
| 术语 Embedding | 2000 术语对 | - | - |

### 3.3 训练流程

```
原始数据 → 清洗 → 标注 → 格式转换 → 训练 → 评估 → 导出
   │                                              │
   └─────────────── LLM 生成增强 ─────────────────┘
```

**训练脚本：**
```bash
# 指令微调
python scripts/fine_tune/instruction_tuning.py \
  --base_model Qwen/Qwen-7B-Chat \
  --data_dir data/instruction/ \
  --output_dir models/qwen-ehs-instruct

# 风险分级
python scripts/fine_tune/risk_classification.py \
  --base_model bert-base-chinese \
  --data_dir data/risk/ \
  --output_dir models/bert-risk-classifier

# 术语 Embedding
python scripts/fine_tune/embedding_tuning.py \
  --base_model BAAI/bge-base-zh-v1.5 \
  --data_dir data/embedding/ \
  --output_dir models/bge-ehs
```

### 3.4 模型部署

**vLLM 部署（Qwen-7B）：**
```bash
python -m vllm.entrypoints.api_server \
  --model models/qwen-ehs-instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1
```

**TensorRT 部署（BGE-Reranker）：**
```bash
# 导出 ONNX
python -m optimum.exporters.onnx \
  --model models/bge-ehs-reranker \
  --task feature-extraction \
  --output models/bge-ehs-reranker-onnx/

# 构建 TensorRT Engine
trtexec --onnx=models/bge-ehs-reranker-onnx/model.onnx \
  --saveEngine=models/bge-ehs-reranker-trt/engine.plan
```

---

## 4. 前端设计

### 4.1 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Next.js | 14.x | 应用框架（App Router） |
| TypeScript | 5.x | 类型系统 |
| TailwindCSS | 3.x | 样式 |
| Shadcn/UI | latest | 组件库 |
| React Query | 5.x | 数据获取 |
| Zod | latest | 表单验证 |

**参考项目：** [Dify 前端](https://github.com/langgenius/dify)

### 4.2 页面列表（7 个）

| 页面 | 路由 | 功能 |
|------|------|------|
| Dashboard | `/` | 概览、统计图表、实时告警 |
| 告警管理 | `/alerts` | 列表、详情、处置记录 |
| 预案管理 | `/plans` | 预案 CRUD、版本管理 |
| 知识库管理 | `/knowledge` | 文档上传、向量化、检索测试 |
| Agent 编排 | `/agents` | 工作流配置、节点编辑 |
| 模型管理 | `/models` | 模型配置、微调记录、评估报告 |
| 系统设置 | `/settings` | API Key、日志、系统信息 |

### 4.3 组件结构

```
src/
├── app/                    # Next.js App Router
│   ├── layout.tsx
│   ├── page.tsx           # Dashboard
│   ├── alerts/
│   ├── plans/
│   ├── knowledge/
│   ├── agents/
│   ├── models/
│   └── settings/
├── components/
│   ├── ui/                # Shadcn 基础组件
│   ├── alert/             # 告警相关组件
│   ├── plan/              # 预案相关组件
│   └── common/            # 通用组件
├── hooks/                 # 自定义 Hooks
├── lib/                   # 工具函数
├── services/              # API 调用
└── types/                 # TypeScript 类型
```

---

## 5. 测试策略

### 5.1 测试金字塔

```
           /\
          /  \      E2E 测试 (Playwright)
         /----\     - 10 个核心场景
        /      \    - 覆盖率：10%
       /--------\
      /          \   集成测试
     /------------\  - GraphRAG 检索
    /              \ - Agent 编排
   /----------------\ - gRPC 通信
  /                  \- 覆盖率：20%
 /--------------------\
/                      \  单元测试
\                      / - pytest (Python)
 \                    /  - JUnit (Java)
  \__________________/   - Vititest (前端)
                         - 覆盖率：50%
```

**总目标覆盖率：80%+**

### 5.2 性能测试

**工具：** Locust / k6

**测试场景：**
| 场景 | 并发用户 | 持续时间 | 目标 P99 |
|------|---------|---------|---------|
| 告警上报 | 100 | 5min | < 500ms |
| 预案检索 | 50 | 5min | < 800ms |
| 知识库查询 | 200 | 5min | < 300ms |

---

## 6. 基础设施

### 6.1 Docker Compose

```yaml
version: '3.8'
services:
  # 应用服务
  frontend:
    build: ./apps/admin-console
    ports:
      - "3000:3000"
  
  java-service:
    build: ./apps/ehs-business
    ports:
      - "8080:8080"
  
  python-ai:
    build: ./apps/ehs-ai
    ports:
      - "8000:8000"
  
  # 数据存储
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  
  milvus:
    image: milvusdb/milvus:v2.3.0
  
  neo4j:
    image: neo4j:5.14
  
  minio:
    image: minio/minio
  
  # 模型服务
  vllm:
    image: vllm/vllm-openai
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  # 监控
  prometheus:
    image: prom/prometheus
  
  grafana:
    image: grafana/grafana
  
  langfuse:
    image: langfuse/langfuse
```

### 6.2 K8s Helm Chart

**完整 Helm 配置：**
- Deployment + Service + ConfigMap + Secret
- Ingress（Nginx）
- HPA（自动扩缩容）
- PodDisruptionBudget
- NetworkPolicy
- Resource Quota + LimitRange
- 多环境 Values（dev/staging/prod）

---

## 7. CI/CD 流水线

### 7.1 GitHub Actions

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
      - name: Setup Node
        uses: actions/setup-node@v4
      - name: Setup Java
        uses: actions/setup-java@v4
      
      - name: Install Dependencies
        run: |
          pip install -r apps/ehs-ai/requirements.txt
          cd apps/admin-console && npm install
      
      - name: Run Tests
        run: |
          cd apps/ehs-ai && pytest --cov=src --cov-report=xml
          cd apps/admin-console && npm test
          cd apps/ehs-business && mvn test
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v4
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker Images
        run: |
          docker build -t ehs-frontend:$GITHUB_SHA ./apps/admin-console
          docker build -t ehs-java:$GITHUB_SHA ./apps/ehs-business
          docker build -t ehs-ai:$GITHUB_SHA ./apps/ehs-ai
      
      - name: Push to Docker Hub
        run: |
          docker push ehs-frontend:$GITHUB_SHA
          docker push ehs-java:$GITHUB_SHA
          docker push ehs-ai:$GITHUB_SHA
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Update K8s Deployment
        run: |
          helm upgrade ehs ./infra/k8s/ehs \
            --set image.tag=$GITHUB_SHA \
            --namespace ehs \
            --create-namespace
  
  release:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: v2.0.0
          generate_release_notes: true
```

---

## 8. LLMOps + MLOps 完整体系

### 8.1 LLMOps 评估体系

| 评估维度 | 工具 | 指标 | 用途 |
|---------|------|------|------|
| **RAG 质量** | Ragas + MLflow LLM Evaluate | Faithfulness, Context Precision, Groundedness | 无参考评估 + 内置 RAG 指标 |
| **Agent 质量** | AgentEvals | 任务完成率、轨迹合理性、工具使用效率 | 生产环境轨迹评估 |
| **模型性能** | 自定义评估脚本 | Accuracy, Precision, Recall, F1 | 微调模型质量 |
| **线上监控** | Prometheus + Grafana | P99 延迟、Token 消耗、错误率 | 实时性能监控 |
| **人工反馈** | RLHF 数据收集 | 用户满意度、thumbs up/down | 持续优化信号 |
| **A/B 测试** | 多模型对比 | 不同模型/Prompt 的效果差异 | 版本迭代决策 |
| **对抗测试** | Prompt 注入测试 | 安全性、鲁棒性 | 安全边界验证 |

**MLflow LLM Evaluate 集成：**
- 内置 RAG 指标：retrieval relevance, groundedness, context sufficiency
- 实验追踪：记录训练参数、指标
- 模型注册：版本管理、阶段切换（Staging → Production）

### 8.2 MLOps 完整流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    MLOps 数据飞轮                                │
└─────────────────────────────────────────────────────────────────┘

数据准备 → 模型训练 → 模型评估 → 模型注册 → 模型部署 → 模型监控
   │                                              │
   │         ▲                                    │
   │         │         用户反馈 (thumbs down)     │
   └─────────┴──────────────┬─────────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │  自动触发评估   │
                   │ (AgentEvals +  │
                   │    Ragas)      │
                   └────────┬───────┘
                            │
                            ▼
                   ┌────────────────┐
                   │ autoResearch   │
                   │ Prompt 自进化   │
                   └────────┬───────┘
                            │
                            ▼
                   ┌────────────────┐
                   │  A/B 测试验证   │
                   │  通过→部署      │
                   │  失败→回滚      │
                   └────────┬───────┘
                            │
                            ▼
                   用户反馈收集 (循环闭合)
```

**MLOps 工具链：**

| 环节 | 工具 | 用途 |
|------|------|------|
| 实验追踪 | MLflow | 记录训练参数、指标、超参数搜索 |
| 模型注册 | MLflow Model Registry | 版本管理、阶段切换（None→Staging→Production） |
| 模型部署 | vLLM / TensorRT Serving | 高性能推理服务 |
| 模型监控 | Prometheus + Evidently AI | 数据漂移、性能下降检测 |
| 持续训练 | GitHub Actions + DVC | 数据版本控制 + 自动重训练 |

**CI/CD 触发条件：**
- 新数据积累到阈值（如 100 条新反馈）→ 触发自动评估
- 评估分数低于阈值（如 Faithfulness < 0.9）→ 触发优化流程
- 优化完成 → 触发 A/B 验证 + 自动部署

### 8.3 Agent 评估方法论

**AgentEvals 集成方案：**

```python
from agentevals import AgentEvaluator

# 1. 定义评估任务
evaluator = AgentEvaluator(
    task_name="EHS 预案检索",
    expected_trajectory=[
        "parse_alert",
        "assess_risk",
        "search_policies",
        "rank_results",
        "format_response"
    ]
)

# 2. 评估 Agent 轨迹
result = evaluator.evaluate(agent_trajectory)

# 3. 输出指标
print(f"任务完成率：{result.task_completion_rate}")
print(f"轨迹合理性：{result.trajectory_score}")
print(f"工具使用效率：{result.tool_efficiency}")
```

**评估指标：**

| 方法 | 工具 | 指标 | 频率 |
|------|------|------|------|
| **任务完成率** | AgentEvals | 成功完成的任务 / 总任务 | 实时 |
| **轨迹评估** | AgentEvals | 步骤合理性、工具使用效率 | 实时 |
| **人工评估** | RLHF | 专家打分、偏好排序 | 每周 |
| **对抗测试** | Prompt 注入测试 | 安全性、鲁棒性 | 每月 |

### 8.4 autoResearch 轻量集成（Prompt 自进化）

**卡神 (Andrej Karpathy) autoResearch 核心思想：**
- 630 行代码，自主实验循环
- 5 分钟训练周期，单一评估指标，自动决策
- 让 AI 自主决定下一个优化方向

**EHS 场景集成方案：**

```python
# autoResearch 轻量级集成 - Prompt 自进化
def prompt_evolution_loop():
    # 1. 收集失败案例（thumbs down）
    failed_cases = collect_failed_interactions(threshold=0.7)
    
    # 2. autoResearch 分析并生成优化策略
    analysis = autoresearch.analyze(
        cases=failed_cases,
        metric="user_satisfaction"
    )
    
    # 3. 生成新 Prompt
    new_prompt = autoresearch.generate_prompt(
        analysis=analysis,
        current_prompt=current_system_prompt
    )
    
    # 4. A/B 测试验证
    ab_result = ab_test(
        control_prompt=current_system_prompt,
        variant_prompt=new_prompt,
        traffic_split=0.1  # 10% 流量
    )
    
    # 5. 通过则部署，失败则回滚
    if ab_result.improvement > 0.05:  # 5% 提升阈值
        deploy_prompt(new_prompt)
        log_improvement(ab_result)
    else:
        rollback_prompt()
        log_failure(ab_result)
```

**集成复杂度：** 低（仅用于 Prompt 优化，不涉及模型训练）

**简历体现：**
- "基于 autoResearch 的 Prompt 自进化系统"
- "自动分析失败案例 → 生成优化策略 → A/B 验证 → 自动部署"

### 8.5 Grafana Dashboard

| Dashboard | 内容 | 受众 |
|----------|------|------|
| 系统概览 | CPU/Memory/QPS/错误率 | 运维 |
| 告警管理 | 告警数量/类型分布/处置时效 | 业务 |
| 模型性能 | 微调模型准确率/F1/漂移检测 | ML 工程师 |
| RAG 质量 | Faithfulness/Context Precision | ML 工程师 |
| Agent 轨迹 | 任务完成率/轨迹合理性 | 产品 + 技术 |
| 成本分析 | Token 消耗/LLM 调用成本 | 财务 + 技术 |

### 8.6 LangFuse 链路追踪

- 完整 LLM 调用链路（Token 流、延迟分解）
- Agent 轨迹可视化（步骤、工具调用）
- RAG 检索链路（召回→重排序→生成）
- 成本分析（按用户、按场景、按模型）

---

## 9. TOGAF ADM 文档规划

### 9.1 阶段 A：架构愿景

- 项目背景与范围
- 干系人分析
- 架构原则

### 9.2 阶段 B：业务架构

- 业务流程图
- 用例图
- 组织结构图

### 9.3 阶段 C：信息系统架构

- 数据架构图
- 应用架构图

### 9.4 阶段 D：技术架构

- 技术栈选型
- 部署架构图

### 9.5 阶段 E/F：机会分析与迁移规划

- 实施路线图
- 工作量估算

---

## 10. 开发顺序（Wave 并行）

| Wave | 任务 | 预计时间 | 依赖 |
|------|------|---------|------|
| **Wave 1** | 数据准备 + 前端 (Mock) + 文档 (初稿) + Docker 基础 | 2-3 天 | 无 |
| **Wave 2** | 微调模型训练 | 3-5 天 | 数据准备 |
| **Wave 3** | Python AI 服务集成 + 前端改真实 API + Java 服务 (Mock) | 5-7 天 | 微调模型 |
| **Wave 4** | Java gRPC 集成 + 监控集成 | 2-3 天 | Python 服务 |
| **Wave 5** | K8s Helm 验证 + E2E 测试 + 性能测试 | 2-3 天 | 全部服务 |

**总工期：16-21 天（关键路径）**

---

## 11. 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 微调数据质量不足 | 模型效果差 | 中 | LLM 生成 + 人工校验 |
| vLLM/TensorRT 部署失败 | 性能不达标 | 中 | 备选方案：HuggingFace 直接推理 |
| COLA 架构复杂度高 | 开发延期 | 中 | 参考官方示例，渐进引入 |
| 前端 7 页面工作量大 | 延期 | 高 | 优先核心页面（Dashboard + 告警管理） |
| K8s 配置复杂 | 部署失败 | 中 | 先用 Docker Compose 验证 |

---

## 12. 成功标准

| 维度 | 指标 | 目标值 |
|------|------|-------|
| **功能** | 预设场景通过率 | 100% |
| **质量** | 测试覆盖率 | 80%+ |
| **性能** | API P99 响应时间 | < 800ms |
| **RAG** | Ragas Faithfulness | > 0.9 |
| **架构** | TOGAF 文档完整度 | 100% |
| **部署** | K8s Helm 安装成功率 | 100% |

---

## 13. 附录

### 13.1 术语表

| 术语 | 定义 |
|------|------|
| GraphRAG | 基于图谱的 RAG 检索（ES + Milvus + Neo4j） |
| COLA | 阿里开源的应用架构框架 |
| DDD | 领域驱动设计 |
| TOGAF ADM | TOGAF 架构开发方法 |
| vLLM | 高性能 LLM 推理框架 |

### 13.2 参考资料

- [Dify 前端](https://github.com/langgenius/dify)
- [COLA 架构](https://github.com/alibaba/COLA)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [vLLM 文档](https://docs.vllm.ai/)
- [TOGAF 标准](https://www.opengroup.org/togaf)

---

**文档状态**: DRAFT  
**下一步**: 用户评审 → 修改 → 批准 → 进入 `writing-plans`
