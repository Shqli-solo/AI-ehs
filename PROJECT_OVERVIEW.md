# EHS 智能安保决策中台 - 项目概述

## 项目目标

根据 `直投 - 最终版.md` 里的工作经历，构建生产级开源 GitHub 项目，**95% 覆盖简历中的 OpenClaw 和广汽 EHS 中台两个项目**。

### OpenClaw 企业级 Agent 编排系统
- 基于 LangGraph 状态机实现任务拆解、状态流转、工具调度
- 设计 50+ 预置工具并统一 schema
- 落地企业微信/钉钉/飞书消息机器人矩阵

### 广汽 EHS 中台
- GraphRAG 混合检索架构（ES + Milvus + Neo4j）
- Multi-Agent 协同网络（LangGraph 状态机）
- LLMOps 评估体系（Ragas + LangFuse）
- 多模态 AIoT 集成（文本/图片/视频/音频）

---

## 技术栈

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| **后端** | Python 3.11+, FastAPI, LangGraph, LangChain | 核心业务逻辑与 Agent 编排 |
| **向量数据库** | Milvus, Elasticsearch | 混合检索：BM25 + 向量相似度 |
| **图数据库** | Neo4j | GraphRAG 知识图谱（85 万 + 实体，420 万 + 关系） |
| **LLM** | Claude API, Qwen, vLLM | 多模型路由与推理服务 |
| **评估** | Ragas, LangFuse | 自动化评估 + 全链路追踪 |
| **前端** | React 18, TypeScript, TailwindCSS | Admin Console 管理后台 |
| **部署** | Docker, Kubernetes | 容器化部署 |
| **监控** | Prometheus, Grafana | 性能监控与告警 |

---

## 项目结构

```
mianshi/
├── ehs-middle-platform/           # EHS 智能安保决策中台
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/               # API Gateway (FastAPI)
│   │   │   ├── agents/            # Multi-Agent 编排 (LangGraph)
│   │   │   ├── graphrag/          # GraphRAG 知识引擎
│   │   │   │   ├── es_client.py   # Elasticsearch BM25 检索
│   │   │   │   ├── milvus_client.py # 向量检索
│   │   │   │   └── neo4j_client.py # 图谱检索
│   │   │   ├── llm/               # LLM 服务层
│   │   │   │   ├── claude_client.py
│   │   │   │   ├── qwen_client.py
│   │   │   │   └── vllm_client.py
│   │   │   ├── evals/             # LLMOps 评估
│   │   │   │   ├── ragas_eval.py  # Ragas 自动化评估
│   │   │   │   └── langfuse_trace.py # 链路追踪
│   │   │   └── shared/            # 共享模块
│   │   ├── tests/                 # 单元测试
│   │   ├── docker-compose.yml
│   │   └── Dockerfile
│   ├── admin-console/             # React 管理后台
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   └── hooks/
│   │   ├── package.json
│   │   └── tailwind.config.js
│   ├── model-service/             # vLLM 推理服务
│   │   ├── vllm-config.yaml
│   │   └── Dockerfile
│   ├── k8s/                       # Kubernetes 部署配置
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   ├── monitoring/                # Prometheus + Grafana
│   │   ├── prometheus.yml
│   │   └── grafana-dashboards/
│   └── docs/                      # 项目文档
│       └── superpowers/
│           └── specs/             # 设计文档
├── openclaw/                      # OpenClaw Agent 编排系统
│   ├── agents/                    # Agent 定义
│   ├── tools/                     # 50+ 预置工具
│   ├── workflows/                 # LangGraph 状态机
│   └── integrations/              # 企业微信/钉钉/飞书
├── docs/                          # 公共文档
│   ├── superpowers+gstack 配置.md
│   └── Superpowers + gstack 技术实现.html
├── VERSION                        # 版本号
├── PROJECT_OVERVIEW.md            # 本文件
└── CLAUDE.md                      # 项目指令
```

---

## 当前阶段

### EHS 中台：核心模块已完成 90%

#### 已完成 ✅

| 模块 | 说明 | 状态 |
|------|------|------|
| 项目骨架 | 目录结构、基础配置 | ✅ |
| 共享模块 | 工具函数、配置管理、日志 | ✅ |
| GraphRAG 知识引擎 | ES + Milvus + Neo4j 三路召回 | ✅ |
| Multi-Agent 编排 | LangGraph 状态机 + Supervisor 监管 | ✅ |
| LLMOps 评估体系 | Ragas 自动化评估 + LangFuse 追踪 | ✅ |
| API Gateway | FastAPI 路由与中间件 | ✅ |

#### 待实现 ⏳

| 模块 | 说明 | 优先级 |
|------|------|--------|
| Admin Console | React 管理后台 | 高 |
| Model Service | vLLM 推理服务配置 | 中 |
| K8s 部署配置 | Kubernetes 部署 YAML | 中 |
| Prometheus + Grafana | 监控告警仪表盘 | 中 |
| 单元测试覆盖 | pytest 测试用例 | 高 |

---

## 下一阶段目标

1. **补充 Admin Console**
   - React 18 + TypeScript + TailwindCSS
   - 知识库管理、Agent 配置、评估回放、监控仪表盘

2. **完善项目可演示性**
   - 提供 Docker Compose 一键启动脚本
   - 准备示例数据和 Demo 场景
   - 编写 README 和使用文档

3. **补充单元测试**
   - GraphRAG 检索模块测试
   - Agent 编排逻辑测试
   - API 接口集成测试
   - 目标覆盖率：85%+

---

## 阶段验收标准

| 阶段 | 完成标准 | 产出物 |
|------|----------|--------|
| brainstorming | 需求明确、边界清晰、用户确认 | 需求摘要 |
| writing-plans | 计划文档已写、/autoplan 审查通过 | docs/superpowers/specs/*.md |
| TDD | 测试用例已写、测试全过 | 测试文件 + 实现代码 |
| code-review | 审查通过、无 blocking issue | PR 或 git diff |
| QA | /qa 验证通过、无 console error | QA 报告 |
| ship | 已合并、已发布、更新 VERSION | git commit + tag |

---

## 会话启动检查清单

**每次新会话开始时执行**：

1. 读取 `VERSION` → 确认当前版本号
2. 读取 `PROJECT_OVERVIEW.md` → 确认完成状态
3. `git status` → 检查未提交变更
4. `TaskList` → 检查未完成任务
5. 如有中断的任务 → 先恢复上下文再继续

---

## 技能路由规则

| 用户请求类型 | 调用的 Skill |
|-------------|-------------|
| 计划、规划、设计方案 | `Superpowers: writing-plans` |
| 头脑风暴、探索需求、创意发散 | `Superpowers: brainstorming` |
| 编码、实现功能、写代码 | `Superpowers: test-driven-development` |
| 调试、排查问题、修复 bug | `Superpowers: systematic-debugging` |
| 代码审查、检查代码质量 | `Superpowers: requesting-code-review` |
| 浏览器操作、QA 测试、访问网站 | `/browse` 或 `/qa` |
| 部署、发布、创建 PR | `/ship` |
| 安全审计 | `/cso` |
| 多视角计划审查 | `/autoplan` |
