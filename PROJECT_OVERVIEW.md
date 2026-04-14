# EHS 智能安保决策中台 - 项目概览

> **阶段 1 MVP 完成时间**: 2026-04-14  
> **版本**: v1.0.1  
> **状态**: ✅ 阶段 1 完成 - 已发布

---

## 项目目标

构建生产级开源 GitHub 项目，95% 覆盖简历中的 OpenClaw 和广汽 EHS 中台项目经历。

**核心价值主张**:
- 事故响应时间：45min → 8min（82% 提升）
- 复杂场景问答准确率：82% → 95%（13 个百分点提升）
- 人工复核工作量：减少 70%
- 年度规避潜在损失：1500 万+

---

## 阶段 1 MVP 完成清单

| Task | 功能模块 | 文件数 | 测试数 | 状态 |
|------|----------|--------|--------|------|
| 1.2 | 项目骨架搭建 | 8 | - | ✅ |
| 1.2.5 | DX 补充（.env + docker-compose） | 3 | - | ✅ |
| 1.3 | GraphRAG 检索引擎 | 7 | 16 | ✅ |
| 1.4 | Multi-Agent 编排 | 4 | 10 | ✅ |
| 1.5 | 前端告警管理页面 | 18 | - | ✅ |
| 1.6 | REST API | 3 | 9 | ✅ |
| **合计** | - | **43** | **35** | **✅** |

---

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端（React 18）                      │
│  ┌─────────────┐  ┌─────────────┐                       │
│  │AlertList    │  │SimulateAlert│                       │
│  └─────────────┘  └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Python AI Service（FastAPI）                │
│  ┌─────────────────────────────────────────────────┐    │
│  │  REST API Layer                                  │    │
│  │  - /api/alert/report   (告警上报)                │    │
│  │  - /api/plan/search    (预案检索)                │    │
│  │  - /health             (健康检查)                │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Multi-Agent Orchestration (LangGraph)          │    │
│  │  - RiskAgent      (风险感知)                     │    │
│  │  - SearchAgent    (预案检索)                     │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │  GraphRAG Engine                                 │    │
│  │  - ES Searcher      (BM25 检索)                  │    │
│  │  - Milvus Searcher  (向量检索)                   │    │
│  │  - BGE-Reranker     (重排序)                      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              外部依赖（Docker Compose）                  │
│  - Elasticsearch 8.x    (文档检索)                       │
│  - Milvus 2.x           (向量数据库)                     │
│  - BGE-Reranker         (重排序模型)                     │
└─────────────────────────────────────────────────────────┘
```

---

## 核心能力验证

### GraphRAG 检索
- ✅ ES BM25 检索（支持降级处理）
- ✅ Milvus 向量检索（支持降级处理）
- ✅ BGE-Reranker 重排序
- ✅ 三路召回融合

### Multi-Agent 编排
- ✅ RiskAgent（风险感知，含 LLM JSON fallback）
- ✅ SearchAgent（预案检索）
- ✅ LangGraph 状态机（顺序执行：风险感知 → 预案检索）
- ✅ 错误降级处理

### REST API
- ✅ 告警上报接口（含 Pydantic 输入验证）
- ✅ 预案检索接口
- ✅ 健康检查接口
- ✅ CORS 跨域支持
- ✅ XSS/注入防护

### 前端页面
- ✅ 告警列表（支持 Mock 数据）
- ✅ 模拟上报组件（4 个预设场景按钮）
- ✅ Loading/Error/Empty 状态
- ✅ Ant Design + TailwindCSS

---

## 快速启动

### 前置要求
- Node.js 18+
- Python 3.11
- Docker Desktop

### 启动后端

```bash
cd python-ai-service

# 安装依赖
pip install -r requirements.txt

# 复制配置
cp .env.example .env

# 运行服务
python -m uvicorn src.api.rest:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端

```bash
cd admin-console

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

### 使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 测试运行

```bash
cd python-ai-service

# 运行所有测试
pytest -v

# 运行特定模块测试
pytest tests/test_graph_rag.py -v
pytest tests/test_agents.py -v
pytest tests/test_api.py -v
```

---

## 项目结构

```
mianshi/
├── python-ai-service/
│   ├── src/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── rest.py              # FastAPI REST API
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # 配置管理
│   │   │   └── logging.py           # 日志配置
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── risk_agent.py        # 风险感知 Agent
│   │   │   ├── search_agent.py      # 预案检索 Agent
│   │   │   └── workflow.py          # LangGraph 工作流
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── es_search.py         # ES 检索器
│   │   │   ├── milvus_search.py     # Milvus 检索器
│   │   │   ├── reranker.py          # BGE-Reranker
│   │   │   └── graph_rag.py         # GraphRAG 主检索器
│   │   └── shared/
│   │       ├── __init__.py
│   │       └── models.py            # Pydantic 数据模型
│   ├── tests/
│   │   ├── test_graph_rag.py        # GraphRAG 测试 (16 用例)
│   │   ├── test_agents.py           # Agent 测试 (10 用例)
│   │   └── test_api.py              # API 测试 (9 用例)
│   ├── .env.example
│   ├── Dockerfile
│   ├── README.md
│   └── requirements.txt
├── admin-console/
│   ├── src/
│   │   ├── pages/alert/
│   │   │   ├── AlertList.tsx        # 告警列表组件
│   │   │   ├── SimulateAlert.tsx    # 模拟上报组件
│   │   │   └── index.ts
│   │   ├── types/
│   │   │   └── alert.ts             # TypeScript 类型
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── README.md
├── docker-compose.yml
├── docs/
│   ├── superpowers/
│   │   ├── product-brief.md         # 产品简报
│   │   ├── README.md                # Superpowers 配置
│   │   ├── specs/                   # 设计文档
│   │   └── plans/                   # 实施计划
│   └── EHS 中台技术架构图.png
├── CLAUDE.md
└── PROJECT_OVERVIEW.md              # 本文件
```

---

## 关键设计决策

### 1. 为什么选择两路召回而非三路（Neo4j 图谱）？
**决策**: 图谱建设成本高，ES + Milvus 两路召回足以证明 MVP 能力。Neo4j 推迟到阶段 2。

### 2. 为什么所有检索器都要降级处理？
**决策**: 生产环境要求——外部依赖（ES/Milvus/LLM）可能不可用，系统应优雅降级而非 500 错误。

### 3. 为什么 RiskAgent 需要 `_extract_risk_level` fallback 方法？
**决策**: LLM 可能返回非 JSON 响应，必须从中提取风险等级，保证系统可用性。

### 4. 为什么前端使用 Mock 数据？
**决策**: 阶段 1 聚焦 UI/UX 和核心流程验证，阶段 2 连接真实 API。

### 5. 为什么 API 需要 Pydantic 输入验证？
**决策**: 安全边界——防止 XSS/注入攻击，验证字段长度和格式。

---

## 下一步（阶段 2）

- [ ] Neo4j 图谱检索（第三路召回）
- [ ] 真实 LLM 集成（替换 Mock）
- [ ] Java 服务 + gRPC（微服务架构）
- [ ] 完整前端页面（7 个页面）
- [ ] K8s + Istio 部署
- [ ] LangFuse 链路追踪
- [ ] 更多预设场景（气体泄漏、温度异常、入侵检测）

---

## 参考资料

- [设计文档](docs/superpowers/specs/)
- [产品简报](docs/superpowers/product-brief.md)
- [实施计划](docs/superpowers/plans/2026-04-13-ehs-stage1-mvp-plan.md)
- [Superpowers 配置](docs/superpowers/README.md)

---

**Last Updated**: 2026-04-14  
**Git Branch**: master  
**Latest Commit**: 0674613
