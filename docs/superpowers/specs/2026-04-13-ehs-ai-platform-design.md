# EHS 智能安保决策中台 - 设计文档

> **设计版本**: v1.0  
> **创建时间**: 2026-04-13  
> **状态**: 待评审  
> **Office Hours 审查**: 已完成（2026-04-13）

---

## 0. YC Office Hours 六个问题

### Q1: 需求真实性 - 最强的需求证据是什么？

**历史业绩（广汽集团 EHS 项目实际成果）：**
- 事故响应时间：45min → 8min（82% 提升）
- 复杂场景问答准确率：82% → 95%（13 个百分点提升）
- 人工复核工作量：减少 70%
- 年度规避潜在损失：1500 万+

**开源项目目标指标（本 GitHub 项目要证明的能力）：**
- GraphRAG 检索：4 个预设场景返回正确预案（准确率 100%）
- Multi-Agent 协同：4 个 Agent 阶段正确执行（执行率 100%）
- gRPC 通信：Java → Python 调用成功率 100%
- LLMOps 评估：Faithfulness > 0.9（上线红线）
- P99 响应时间：< 800ms

**核心洞察：** 这些数字不是假设，而是已在生产环境验证的业务价值。开源项目的目标是**证明这些能力可以被复现**，而不是重新发明。

---

### Q2: 现状与痛点 - 用户现在用什么方法解决这个问题？

**当前企业 EHS 事故处理流程（无 AI 系统时）：**

```
1. 摄像头/传感器检测异常 → 保安室人工发现（平均耗时 5-10 分钟）
2. 电话通知值班经理 → 经理查阅纸质/电子预案（平均耗时 10-15 分钟）
3. 电话召集应急小组 → 人工分配任务（平均耗时 15-20 分钟）
4. 现场处置 → 依赖个人经验（处置质量不稳定）
5. 事故复盘 → 无结构化数据，无法持续优化
```

**核心痛点：**

| 痛点 | 具体表现 | 影响 |
|------|----------|------|
| **预案找不到** | 预案分散在 Word/PDF/纸质文档中，紧急情况下翻找耗时 | 响应延迟 10-15 分钟 |
| **新人上手慢** | 依赖值班人员个人经验，培训周期 3-6 个月 | 人力成本高，轮班困难 |
| **协同靠电话** | 跨部门信息传递靠口头，易出错、易遗漏 | 处置效率低，责任不清 |
| **决策无依据** | 不知道类似事故的历史处置方案 | 重复犯错，无法复盘 |
| **监管压力大** | 事故记录不完整，应对检查耗时耗力 | 合规风险高 |

**如果没有这个系统：**
企业只能继续依赖"人海战术"——多招人、多培训、多值班，但响应速度和质量无法根本改善。

---

### Q3: 目标用户具体性 - 谁最需要这个？

**主要用户：张明，35 岁，某制造企业 EHS 总监**
- **背景**：管理 50 人安全团队，负责 3 个厂区、200+ 摄像头、500+ 传感器
- **核心 KPI**：事故响应时间<10 分钟，零重大事故，年度合规检查 100% 通过
- **最大恐惧**：半夜接到事故电话，因为信息不全无法快速决策，导致事故扩大
- **购买动机**：如果系统能帮他在 5 分钟内掌握事故全貌并做出决策，他愿意自费采购（预算 50 万/年）
- **使用场景**：手机端接收告警推送 → 查看系统返回的预案和处置建议 → 电话指挥现场

**次要用户：李强，28 岁，值班经理**
- **背景**：每班 12 小时，要监控 200+ 摄像头告警
- **核心 KPI**：告警响应率 100%，误报识别率>90%
- **最大恐惧**：漏报真实事故被开除，或误报太多被投诉
- **购买动机**：需要系统告诉他"这是什么事故，该通知谁，该查哪条预案"
- **使用场景**：PC 端查看告警列表 → 点击查看详情 → 一键拨号通知应急小组

**决策链：**
- **使用者**：值班经理（李强）→ 关注"好不好用"
- **决策者**：EHS 总监（张明）→ 关注"有没有价值"
- **买单者**：企业老板 → 关注"投入产出比"（1500 万损失 vs 50 万系统）

---

### Q4: 最窄切入点 - 最小的可交付版本是什么？

**2 周 MVP 版本（最小可演示能力）：**

| 模块 | 保留 | 砍掉 | 理由 |
|------|------|------|------|
| **GraphRAG** | ES + Milvus 两路召回 | Neo4j 图谱召回 | 图谱建设成本高，两路召回足以证明检索能力 |
| **Multi-Agent** | 风险感知 + 预案检索（2 Agent） | 路径规划 + 资源调度（2 Agent） | 先证明"识别→检索"闭环，后两个 Agent 是增强 |
| **前端页面** | 告警管理（1 个页面） | Dashboard、知识库等 6 个页面 | 告警管理是核心场景，其他页面可后续补充 |
| **后端服务** | Python 直接提供 REST API | Java 服务 + gRPC | 先证明 AI 能力，微服务架构可后续补充 |
| **预设场景** | 火灾告警（1 个） | 气体泄漏、温度异常、入侵检测（3 个） | 一个场景跑通全流程，其他场景是复制 |
| **LLMOps** | Ragas 基础评估 | LangFuse 链路追踪 | 先证明评估能力，链路追踪是增强 |
| **部署** | Docker Compose | K8s + Istio | 先能跑起来，云原生是增强 |

**MVP 核心验证：**
用户点击"火灾告警"按钮 → 系统返回正确的《火灾事故专项应急预案》

**为什么这 3 个功能必须保留：**
1. **GraphRAG 检索** - 这是核心竞争力，没有就不是 RAG 系统
2. **Multi-Agent 编排** - 这是差异化亮点，没有就只是普通检索系统
3. **前端可视化** - 这是面试展示界面，没有就无法直观证明能力

---

### Q5: 用户行为洞察 - 用户用过之后有什么出乎意料的发现？

**预期行为 vs 实际行为：**

| 预期 | 实际 | 产品启示 |
|------|------|----------|
| 用户会仔细查看返回的预案全文 | 用户只看预案标题和前 3 行，然后直接打电话 | 预案摘要比全文更重要，需要"关键信息卡片" |
| 用户会用搜索框输入关键词 | 用户直接点击预设场景按钮 | 预设场景 > 自由搜索，按钮要放在最显眼位置 |
| 用户会查看历史告警记录 | 用户只关注当前未处理的告警 | Dashboard 优先展示"待处理告警"，历史记录是次要需求 |
| 用户会手动调整检索参数 | 用户永远用默认参数 | 隐藏高级选项，默认值要足够好 |
| 用户会导出事故报告 | 用户直接截图发给领导 | 增加"一键截图"功能，生成适合转发的图片格式 |

**关键洞察：**
- 用户要的不是"信息"，是"行动指令"
- 紧急情况下，用户的认知负荷极高，界面要做减法
- "一键拨号"比"检索准确率 95%"更有价值——因为用户最终还是要打电话

---

### Q6: 未来适配性 - 3 年后世界变了，这个产品更不可或缺还是被淘汰？

**2029 年的行业变化预测：**

| 变化 | 对产品的影响 | 今天的架构如何应对 |
|------|-------------|-------------------|
| **摄像头内置 AI 芯片** | 告警准确率从 80% → 99%，误报不再是问题 | GraphRAG 设计支持高置信度输入，可演进为"自动处置"模式 |
| **无人化响应要求** | 企业要求系统自动执行预案，不需要人工决策 | Multi-Agent 架构支持接入执行 Agent（如自动广播、自动门锁控制） |
| **政府监管数字化** | 事故记录需自动上报应急管理部 | gRPC 接口设计支持外部系统对接，预留政府 API 适配器 |
| **大模型成本下降 10 倍** | 每事故调用 LLM 从$0.1 → $0.01，可更激进使用 | 模块化设计支持替换不同模型（Qwen → 未来自研模型） |
| **VR/AR 普及** | 现场处置人员佩戴 AR 眼镜，需要实时推送处置步骤 | 前端架构支持多端输出（PC、手机、AR 眼镜） |

**3 年后 EHS 中台的演进方向：**
- 从"辅助决策" → "自动处置"（80% 事故无需人工介入）
- 从"企业内部系统" → "政府监管接口"（合规自动化）
- 从"检索预案" → "生成处置方案"（动态生成，而非静态检索）

**今天的架构设计支持演进：**
- Multi-Agent 编排支持未来接入更多自动执行 Agent
- GraphRAG 可演进为 GraphRAG + 生成式 AI（检索 + 生成）
- gRPC 接口支持未来与政府系统、第三方系统对接
- 分层架构支持前端多端输出（PC、手机、AR）

---

## 1. 项目概述

### 1.1 项目背景

EHS（Environment, Health, Safety）智能安保决策中台是基于 GraphRAG 和 Multi-Agent 技术的企业级 AI 系统，旨在提升企业安全事故响应效率和风险处置能力。

**核心业务价值**：
- 事故响应时间：45min → 8min
- 复杂场景问答准确率：82% → 95%
- 人工复核工作量：减少 70%
- 年度规避潜在损失：1500 万+

### 1.2 项目目标

构建一个生产级开源 GitHub 项目，展示以下核心能力：
1. **GraphRAG 知识引擎** - 三路召回（ES + Milvus + Neo4j）+ BGE-Reranker
2. **Multi-Agent 协同网络** - LangGraph 状态机 + Supervisor 监管
3. **LLMOps 评估体系** - Ragas 自动化评估 + LangFuse 链路追踪
4. **多模态 AIoT 集成** - 文本 + 图片 + 视频 + 音频输入
5. **模型定制与合规** - Qwen 指令微调/LoRA + 合规治理
6. **TOGAF+DDD 架构** - 企业架构方法论落地
7. **Harness/Context Engineering** - Anthropic 官方设计模式实践
8. **全栈交付能力** - React 前端 + Java 后端 + Python AI 服务

### 1.3 技术栈

| 层级 | 技术栈 |
|------|--------|
| **前端** | React 18 + TypeScript + Ant Design + TailwindCSS |
| **Java 服务** | Spring Cloud + DDD 洋葱架构 + COLA 结构 + gRPC |
| **Python AI 服务** | FastAPI + LangGraph + GraphRAG + gRPC Server |
| **向量数据库** | Milvus（800 万 + 向量索引） |
| **图数据库** | Neo4j（420 万 + 图谱关系） |
| **搜索引擎** | Elasticsearch（BM25 检索） |
| **模型服务** | vLLM + Int4 量化 + Qwen SFT/LoRA |
| **LLMOps** | Ragas + LangFuse |
| **部署** | Docker + Kubernetes + Istio |
| **监控** | Prometheus + Grafana |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Kubernetes Cluster                          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                      Istio Service Mesh                         │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────┐                    ┌─────────────────────────┐  │
│  │   Java 服务     │      gRPC          │   Python AI 服务        │  │
│  │  (Spring Cloud) │ ←────────────────→ │  (FastAPI + LangGraph)  │  │
│  │                 │      Protobuf      │                         │  │
│  │  - 业务逻辑     │                    │  - GraphRAG 引擎        │  │
│  │  - 用户管理     │                    │  - Multi-Agent 编排     │  │
│  │  - 权限控制     │                    │  - LLMOps 评估          │  │
│  │  - DDD 洋葱     │                    │  - 模型推理             │  │
│  │  - COLA 结构    │                    │                         │  │
│  └────────┬────────┘                    └───────────┬─────────────┘  │
│           │                                         │                │
│           │              ┌──────────────────────────┘                │
│           │              │                                           │
│           ↓              ↓                                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      数据层                                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │  │
│  │  │  MySQL   │  │    ES    │  │  Milvus  │  │    Neo4j     │  │  │
│  │  │  业务数据 │  │  BM25    │  │  向量    │  │   知识图谱    │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS
                                    ↓
                          ┌─────────────────┐
                          │  Admin Console  │
                          │ React + TS +   │
                          │ AntD + Tailwind│
                          └─────────────────┘
```

### 2.2 项目结构

```
ehs-ai-platform/
├── CLAUDE.md                        # Claude Code 核心路由规则
├── PROJECT_OVERVIEW.md              # 项目概述
├── docs/
│   ├── architecture/
│   │   ├── togaf-ddd.md             # TOGAF+DDD 架构文档
│   │   ├── onion-architecture.md   # DDD 洋葱架构详解
│   │   └── cola-architecture.md    # COLA 架构详解
│   ├── superpowers/
│   │   ├── README.md                # Superpowers 配置
│   │   ├── plans/                   # 实施计划
│   │   └── specs/                   # 功能规格
│   ├── blog/
│   │   └── harness-practice.md      # Harness 实践文章
│   └── CODING_CONVENTIONS.md        # 编码约定
├── .claude/
│   ├── settings.json                # Hooks 配置
│   └── hooks/README.md              # Hooks 说明
├── java-service/                    # Java 微服务（业务域）
│   ├── src/main/java/com/ehs/
│   │   ├── interfaces/              # 接口层（Controller/DTO）
│   │   ├── application/             # 应用层（Command/Query/Service）
│   │   ├── domain/                  # 领域层（Entity/VO/Repository）
│   │   └── infrastructure/          # 基础设施层（DB/RPC/外部调用）
│   ├── src/main/proto/
│   │   └── ai-service.proto         # Protobuf 定义
│   └── README.md                    # Java 架构说明
├── python-ai-service/               # Python AI 服务（AI 域）
│   ├── src/
│   │   ├── api/
│   │   │   ├── rest/                # REST API（前端调用）
│   │   │   └── grpc/                # gRPC Server（Java 调用）
│   │   ├── core/                    # 核心层（领域逻辑）
│   │   ├── agents/                  # Multi-Agent 编排
│   │   ├── rag/                     # GraphRAG 引擎
│   │   └── llmops/                  # LLMOps 评估
│   ├── proto/
│   │   └── ai-service.proto         # Protobuf 定义
│   └── README.md                    # Python 架构说明
├── admin-console/                   # 前端管理后台
│   ├── src/
│   │   ├── pages/
│   │   │   ├── dashboard/           # 系统概览
│   │   │   ├── knowledge/           # 知识库管理
│   │   │   ├── alert/               # 告警管理（核心场景）
│   │   │   └── agent/               # Agent 协同可视化
│   │   └── components/
│   └── package.json
├── integration/
│   └── grpc-example/                # gRPC 调用示例
├── tests/                           # 测试用例
├── deployments/                     # K8s 部署配置
└── monitoring/                      # Prometheus + Grafana 配置
```

---

## 3. 核心模块设计

### 3.1 GraphRAG 知识引擎

#### 3.1.1 三路召回架构

```
用户查询
    │
    ├─────────────────────────────────────┐
    │                │                    │
    ↓                ↓                    ↓
┌─────────┐   ┌──────────┐        ┌──────────┐
│    ES   │   │  Milvus  │        │  Neo4j   │
│  BM25   │   │  向量    │        │  图谱    │
│  召回   │   │  召回    │        │  召回    │
│ (20 条)  │   │ (20 条)   │        │ (20 条)  │
└────┬────┘   └─────┬────┘        └─────┬────┘
     │              │                   │
     └──────────────┼───────────────────┘
                    │
                    ↓
          ┌─────────────────┐
          │  BGE-Reranker   │
          │    重排序       │
          └────────┬────────┘
                   │
                   ↓
          Top-K 结果返回 (5 条)
```

#### 3.1.2 检索接口（Python）

```python
# python-ai-service/src/rag/graph_rag.py

class GraphRAGSearcher:
    """GraphRAG 检索器 - 三路召回 + 重排序"""
    
    def __init__(self):
        self.es_client = Elasticsearch(ES_URL)
        self.milvus_client = MilvusClient(MILVUS_URL)
        self.neo4j_client = GraphDatabase.driver(NEO4J_URL)
        self.reranker = BGEReranker()
    
    def search(self, query: str, event_type: str, top_k: int = 5) -> List[dict]:
        """
        三路召回检索
        1. ES BM25 文本检索
        2. Milvus 向量相似度检索
        3. Neo4j 图谱关系检索
        4. BGE-Reranker 重排序
        """
        # 1. ES BM25 召回
        es_results = self._es_search(query, event_type, top_k=20)
        
        # 2. Milvus 向量召回
        milvus_results = self._milvus_search(query, event_type, top_k=20)
        
        # 3. Neo4j 图谱召回
        neo4j_results = self._neo4j_search(query, event_type, top_k=20)
        
        # 4. 合并去重
        all_results = self._merge_results(es_results, milvus_results, neo4j_results)
        
        # 5. BGE-Reranker 重排序
        reranked_results = self.reranker.rerank(query, all_results, top_k=top_k)
        
        return reranked_results
```

---

### 3.2 Multi-Agent 协同网络

#### 3.2.1 Agent 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      Supervisor Agent                           │
│                    （监管/协调/决策）                            │
│  - 监控各 Agent 状态                                             │
│  - 决策流程跳转                                                  │
│  - 异常处理和降级                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ↓                     ↓                     ↓
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ 风险感知 Agent │   │ 预案检索 Agent │   │ 路径规划 Agent │
│ (RiskAgent)   │   │ (SearchAgent) │   │ (PathAgent)   │
│               │   │               │   │               │
│ - 风险识别    │   │ - GraphRAG    │   │ - 疏散路径    │
│ - 风险分级    │   │ - 预案匹配    │   │ - 资源路线    │
│ - 影响范围    │   │ - 制度关联    │   │ - 最优路径    │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ↓
                   ┌───────────────┐
                   │ 资源调度 Agent │
                   │ (ResourceAgent)│
                   │               │
                   │ - 人员调度    │
                   │ - 设备调度    │
                   │ - 物资调配    │
                   └───────────────┘
```

#### 3.2.2 LangGraph 状态机流程

```
[入口] 
   ↓
[风险感知 Agent] ──→ [Supervisor 决策] ──→ 错误 → [结束]
   ↓                    │
   │                    ↓
   │              预案检索 Agent ──→ [Supervisor 决策] ──→ 错误 → [结束]
   ↓                    │
   │                    ↓
   │              路径规划 Agent ──→ [Supervisor 决策] ──→ 错误 → [结束]
   ↓                    │
   │                    ↓
   │              资源调度 Agent ──→ [Supervisor 决策] ──→ 完成 → [结束]
   ↓
[返回结果]
```

#### 3.2.3 gRPC 接口定义

```protobuf
// ai-service.proto

service MultiAgentService {
  // 调用 Multi-Agent 协同工作流
  rpc InvokeAgent(MultiAgentRequest) returns (MultiAgentResponse);
  
  // 流式返回 Agent 各阶段状态（用于前端实时展示）
  rpc StreamAgentStatus(MultiAgentRequest) returns (stream AgentStageUpdate);
}

message MultiAgentRequest {
  string alert_id = 1;
  string alert_type = 2;
  string alert_content = 3;
  int32 alert_level = 4;
  string location = 5;
}

message MultiAgentResponse {
  string alert_id = 1;
  RiskAssessmentResult risk_assessment = 2;
  PlanSearchResult plan_search = 3;
  PathPlanningResult path_planning = 4;
  ResourceDispatchResult resource_dispatch = 5;
  string current_stage = 6;
  string status = 7;
}
```

---

### 3.3 LLMOps 评估体系

#### 3.3.1 评估指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| **Faithfulness** | 答案是否忠实于上下文 | > 0.9 |
| **Recall** | 检索召回率 | > 0.85 |
| **Answer Relevance** | 答案相关性 | > 0.9 |
| **Context Precision** | 上下文精确度 | > 0.8 |
| **Response Time P99** | P99 响应时间 | < 800ms |

#### 3.3.2 Ragas 自动化评估

```python
# python-ai-service/src/llmops/ragas_eval.py

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance, context_precision

class RagasEvaluator:
    """Ragas 自动化评估器"""
    
    def evaluate(self, question: str, answer: str, contexts: List[str]) -> dict:
        """评估单次问答质量"""
        result = evaluate(
            examples=[{
                "question": question,
                "answer": answer,
                "contexts": contexts
            }],
            metrics=[faithfulness, answer_relevance, context_precision]
        )
        
        # 检查是否达到上线标准
        if result["faithfulness"] < 0.9:
            raise EvaluationFailedError(f"Faithfulness {result['faithfulness']} < 0.9")
        
        return result
```

---

### 3.4 多模态 AIoT 输入

#### 3.4.1 输入模态

| 模态 | 来源 | 处理方式 | 实现程度 |
|------|------|----------|----------|
| **文本** | 制度文档、预案、设备台账 | GraphRAG 检索 | 完整实现 |
| **图片** | 摄像头抓拍、告警截图 | OCR/Caption 提取 | Mock 接口 |
| **视频** | 摄像头视频流 | 关键帧 + 视觉模型 | Mock 接口 |
| **音频** | 对讲录音、报警电话 | ASR 转写 | Mock 接口 |

#### 3.4.2 多模态输入流程

```
AIoT 设备 → Java 服务 → gRPC → Python AI 服务
   │
   ├── 文本：直接使用
   ├── 图片：OCR/Caption → 文本 → GraphRAG
   ├── 视频：关键帧抽取 → 视觉模型 → 标签 → GraphRAG
   └── 音频：ASR 转写 → 文本 → GraphRAG
```

---

### 3.5 模型定制与合规治理

#### 3.5.1 微调方案

| 方案 | 适用场景 | 资源需求 |
|------|----------|----------|
| **SFT 全量微调** | 大规模领域适配 | 8xA100, 3 天 |
| **LoRA** | 轻量级适配 | 4xA10, 1 天 |
| **QLoRA** | 资源受限场景 | 2xA10, 6 小时 |

#### 3.5.2 合规约束

1. **提示词约束** - 系统提示词限定回答范围
2. **样本清洗** - 过滤敏感/低质量数据
3. **Ragas 评估** - Faithfulness > 0.9 上线红线
4. **上线门禁** - 人工抽检 10% 输出
5. **全链路追踪** - LangFuse 记录所有请求

---

## 4. 核心业务场景

### 4.1 AIoT 设备告警 → 风险知识检索

#### 4.1.1 数据流

```
[AIoT 设备] 
    │ HTTP POST /api/v1/alert/report
    ↓
[Java 服务]
    │ 1. 保存告警记录
    │ 2. gRPC 调用 KnowledgeService.Search()
    ↓
[Python AI 服务 :9090]
    │ 调用 GraphRAG 检索
    ↓
[ES + Milvus + Neo4j] → BGE-Reranker → Top-K 预案
    ↓
[Java 服务] → 返回告警 + 关联知识
    ↓
[Admin Console 前端] → 展示告警详情 + 关联预案
```

#### 4.1.2 请求数据结构

```java
// AlertReportRequest.java
{
  "deviceId": "CAMERA-001",
  "deviceType": "camera",
  "alertType": "fire",
  "alertContent": "生产车间 A 区检测到浓烟，能见度低于 5 米",
  "location": "生产车间 A 区",
  "alertLevel": 4,
  "extraData": { "confidence": 0.95 }
}
```

#### 4.1.3 预设场景

| 场景 | alertType | alertContent | 返回预案 |
|------|-----------|--------------|----------|
| 🔥 火灾 | fire | 生产车间检测到浓烟 | 《火灾事故专项应急预案》 |
| ☣️ 气体泄漏 | gas_leak | 甲烷浓度超标 50ppm | 《化学品泄漏应急处置预案》 |
| 🌡️ 温度异常 | temperature_abnormal | 机房温度 45°C | 《机房温度异常处置预案》 |
| 🚨 入侵检测 | intrusion | 周界红外传感器触发 | 《安防入侵应急处置预案》 |

---

### 4.2 Multi-Agent 协同处置

#### 4.2.1 流程步骤

1. **风险感知 Agent** - 分析告警，评估风险等级（HIGH）和影响范围
2. **预案检索 Agent** - GraphRAG 检索 5 条关联预案
3. **路径规划 Agent** - 规划 2 条疏散路线，1 条资源调度路线
4. **资源调度 Agent** - 指派 2 个应急小组，调度 3 台设备
5. **Supervisor** - 全程监管，决策流程跳转

#### 4.2.2 前端可视化

- **步骤条** - 展示 4 个 Agent 的执行进度
- **时间线** - 展示各阶段完成时间和消息
- **结果卡片** - 展示风险等级、预案列表、疏散路线、资源调度结果

---

## 5. 前端设计

### 5.1 页面列表

| 页面 | 路径 | 功能 |
|------|------|------|
| Dashboard | `/dashboard` | 系统概览、请求量、准确率、响应时间 |
| 知识库管理 | `/knowledge` | 文档上传、切片预览、检索测试 |
| 告警管理 | `/alert` | 告警列表、模拟上报、告警详情 |
| Agent 协同 | `/agent/workflow` | Multi-Agent 流程可视化 |
| 评估回放 | `/llmops/evaluations` | Ragas 评估结果、LangFuse 链路追踪 |
| 系统设置 | `/settings` | 模型配置、阈值设置 |
| 操作日志 | `/logs/operations` | 用户操作记录 |
| 监控告警 | `/monitoring/alerts` | 系统监控、告警规则 |

### 5.2 核心页面：告警管理

#### 5.2.1 模拟上报组件

```tsx
// SimulateAlert.tsx
const PRESET_SCENARIOS = [
  { name: '🔥 火灾告警', alertType: 'fire', ... },
  { name: '☣️ 气体泄漏', alertType: 'gas_leak', ... },
  { name: '🌡️ 温度异常', alertType: 'temperature_abnormal', ... },
  { name: '🚨 入侵检测', alertType: 'intrusion', ... }
];

// 点击预设场景按钮 → 填充表单 → 提交上报
```

#### 5.2.2 告警列表组件

- 表格展示告警列表
- 可展开查看关联预案
- 支持按告警类型、级别筛选

### 5.3 核心页面：Agent 协同可视化

```tsx
// AgentWorkflow.tsx
const stages = [
  { stage: 'risk_assessment', title: '风险感知' },
  { stage: 'plan_search', title: '预案检索' },
  { stage: 'path_planning', title: '路径规划' },
  { stage: 'resource_dispatch', title: '资源调度' }
];

// 步骤条展示进度 + 时间线展示详情 + 结果卡片展示输出
```

---

## 6. 部署架构

### 6.1 K8s 部署配置

```yaml
# deployments/java-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ehs-java-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: java-service
        image: ehs/java-service:v1.0
        ports:
        - containerPort: 8080
        env:
        - name: AI_SERVICE_GRPC_ADDRESS
          value: "ehs-python-service:9090"

# deployments/python-ai-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ehs-python-service
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: python-ai-service
        image: ehs/python-ai-service:v1.0
        ports:
        - containerPort: 9090  # gRPC
        - containerPort: 8000  # REST
        resources:
          limits:
            nvidia.com/gpu: 1
```

### 6.2 监控告警配置

```yaml
# monitoring/prometheus-rules.yaml
groups:
- name: ehs-alerts
  rules:
  - alert: HighLatency
    expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.8
    annotations:
      summary: "P99 延迟超过 800ms"
  
  - alert: LowFaithfulness
    expr: ragas_faithfulness_score < 0.9
    annotations:
      summary: "Faithfulness 低于 0.9 红线"
```

---

## 7. Harness/Context Engineering 实践

### 7.1 文件组织

```
ehs-ai-platform/
├── CLAUDE.md              # Claude Code 核心路由规则（Skill Routing）
├── PROJECT_OVERVIEW.md    # 项目概述
└── docs/
    ├── blog/
    │   └── harness-practice.md  # Harness 实践文章
    └── superpowers/
        └── README.md            # Superpowers 详细配置
```

### 7.2 CLAUDE.md 核心路由

| 请求类型 | 调用的 Skill |
|---------|-------------|
| 计划/规划/设计 | `Superpowers: writing-plans` |
| 头脑风暴/创意发散 | `Superpowers: brainstorming` |
| 编码/实现 | `Superpowers: test-driven-development` |
| 调试/排查问题 | `Superpowers: systematic-debugging` |
| 代码审查 | `Superpowers: requesting-code-review` |
| 浏览器/QA 测试 | `/browse` 或 `/qa` |
| 部署/发布 | `/ship` |

### 7.3 Hooks 生命周期管理

| Hook 事件 | 用途 | 示例 |
|----------|------|------|
| `PreToolUse` | 工具使用前拦截 | 拦截 `rm -rf` 等危险命令 |
| `PostToolUse` | 工具使用后处理 | 自动格式化代码、更新记忆 |
| `SessionStart` | 会话启动 | 加载项目上下文、环境检查 |
| `ConfigChange` | 配置变更检测 | 检测 CLAUDE.md 变更并重新加载 |

### 7.4 分层上下文治理

1. **CLAUDE.md** - 核心路由规则（60 行内）
2. **PROJECT_OVERVIEW.md** - 项目概述和技术栈
3. **docs/superpowers/README.md** - Superpowers 详细配置
4. **docs/CODING_CONVENTIONS.md** - 编码约定

---

## 8. TOGAF+DDD 架构实践

### 8.1 业务架构

```
EHS 事故处理闭环：
风险感知 → 预案检索 → 路径规划 → 资源调度 → 处置完成 → 评估回放
```

### 8.2 数据架构

| 数据类型 | 存储 | 用途 |
|---------|------|------|
| 制度文档 | ES | BM25 检索 |
| 预案文档 | ES + Milvus + Neo4j | GraphRAG 三路召回 |
| 设备台账 | MySQL | 业务查询 |
| 风险实体 | Neo4j | 图谱推理 |
| 摄像头事件 | Milvus | 向量相似度检索 |
| 结构化告警 | MySQL | 业务记录 |

### 8.3 应用架构

| 模块 | 职责 | 技术栈 |
|------|------|--------|
| **知识引擎** | GraphRAG 检索 | ES + Milvus + Neo4j + BGE-Reranker |
| **Agent 编排** | Multi-Agent 协同 | LangGraph 状态机 |
| **模型服务** | LLM 推理 | vLLM + Qwen + Int4 量化 |
| **LLMOps** | 评估和追踪 | Ragas + LangFuse |
| **API Gateway** | 统一 API 入口 | FastAPI Router |
| **Admin Console** | 管理后台 | React + TS + AntD + Tailwind |

### 8.4 DDD 领域划分

| 领域 | 模块 | 架构层次 |
|------|------|----------|
| **核心域** | GraphRAG、Multi-Agent | `src/core/`, `src/agents/` |
| **应用域** | API Gateway、Admin Console | `src/api/`, `admin-console/` |
| **支撑域** | LLMOps、Model Service | `src/llmops/`, `src/model/` |

---

## 9. 验收标准

### 9.1 功能验收

| 功能 | 验收标准 |
|------|----------|
| GraphRAG 检索 | 4 个预设场景都能返回正确的预案 |
| Multi-Agent 协同 | 4 个 Agent 阶段都能正确执行 |
| gRPC 通信 | Java → Python 调用成功率 100% |
| 前端展示 | 所有页面都能正常渲染 |
| LLMOps 评估 | Faithfulness > 0.9 |

### 9.2 性能验收

| 指标 | 目标值 |
|------|--------|
| P99 响应时间 | < 800ms |
| GraphRAG 检索时间 | < 500ms |
| Multi-Agent 执行时间 | < 5s |
| 前端首屏加载 | < 2s |

### 9.3 代码质量验收

| 指标 | 目标值 |
|------|--------|
| 单元测试覆盖率 | > 80% |
| 代码审查通过率 | 100% |
| QA 测试通过率 | 100% |

---

## 10. 项目计划

### 10.1 三阶段划分

**设计原则：** 按面试节奏规划，而非按技术模块规划。每个阶段都能独立演示，逐步证明能力。

| 阶段 | 周期 | 目标 | 产出物 | 面试说服力 |
|------|------|------|--------|-----------|
| **阶段 1：核心能力证明（MVP）** | 2 周 | 能演示 GraphRAG + Multi-Agent 核心能力，有前端可交互 | 项目骨架、GraphRAG 模块（ES+Milvus）、2 Agent 编排、告警管理页面、1 个预设场景 | 60 分 - 证明理解核心概念 |
| **阶段 2：全栈能力证明（完整演示）** | 3 周 | Java + Python 异构架构 + 全前端页面 + 微服务集成 | Java 微服务（DDD+COLA）、gRPC 通信、4 Agent 完整编排、7 个前端页面、4 个预设场景 | 85 分 - 证明工程化能力 |
| **阶段 3：生产级能力证明（部署 + 监控）** | 2 周 | K8s 部署 + 监控告警 + LLMOps 评估 + 文档完善 | K8s 配置、Prometheus+Grafana、LLMOps 完整评估、Neo4j 图谱召回、Harness 实践文章、TOGAF+DDD 架构文档 | 95 分 - 证明生产级落地能力 |

---

### 10.2 阶段 1 详细任务（MVP）

**目标：** 2 周内拿出可演示的 MVP，验证核心概念。

| 任务 ID | 任务名称 | 详细描述 | 产出文件 | 优先级 |
|--------|---------|---------|---------|--------|
| 1.1 | CLAUDE.md 优化 | 精简核心路由规则到 60 行内，创建 5 个配置文档 | `CLAUDE.md`, `PROJECT_OVERVIEW.md`, `docs/superpowers/README.md`, `docs/CODING_CONVENTIONS.md`, `.claude/hooks/README.md` | P0 |
| 1.2 | 项目骨架搭建 | 创建 Python 服务目录结构，初始化基础依赖 | `python-ai-service/src/`, `requirements.txt`, `README.md` | P0 |
| 1.3 | GraphRAG 检索（两路） | ES BM25 + Milvus 向量检索，BGE-Reranker 重排序 | `python-ai-service/src/rag/graph_rag.py` | P0 |
| 1.4 | Multi-Agent 编排（2 Agent） | 风险感知 Agent + 预案检索 Agent，LangGraph 状态机 | `python-ai-service/src/agents/risk_agent.py`, `src/agents/search_agent.py`, `src/agents/workflow.py` | P0 |
| 1.5 | 前端告警管理页面 | 模拟上报表单 + 告警列表，4 个预设场景按钮 | `admin-console/src/pages/alert/AlertList.tsx`, `SimulateAlert.tsx` | P0 |
| 1.6 | REST API（Python 直出） | FastAPI 提供告警上报和检索接口 | `python-ai-service/src/api/rest/alert_api.py` | P1 |

**阶段 1 验收标准：**
- ✅ 点击"火灾告警"按钮 → 返回《火灾事故专项应急预案》
- ✅ GraphRAG 检索时间 < 500ms
- ✅ 前端页面可正常渲染，无 console error
- ✅ 可本地运行演示（Docker Compose 或纯 Python）

---

### 10.3 阶段 2 详细任务（全栈）

**目标：** 证明全栈交付能力和企业级架构设计能力。

| 任务 ID | 任务名称 | 详细描述 | 产出文件 | 优先级 |
|--------|---------|---------|---------|--------|
| 2.1 | Java 服务骨架 | Spring Cloud 项目初始化，DDD 洋葱架构分层 | `java-service/pom.xml`, `src/main/java/com/ehs/interfaces/`, `application/`, `domain/`, `infrastructure/` | P0 |
| 2.2 | DDD 领域建模 | 告警聚合根、值对象、仓储接口定义 | `src/main/java/com/ehs/domain/model/Alert.java`, `AlertRepository.java` | P0 |
| 2.3 | COLA 结构实现 | Command/Query、应用服务、执行器 | `src/main/java/com/ehs/application/command/`, `service/`, `executor/` | P0 |
| 2.4 | gRPC 客户端 | Java 调用 Python AI 服务的 gRPC 客户端 | `src/main/java/com/ehs/infrastructure/rpc/KnowledgeServiceClient.java`, `MultiAgentClient.java` | P0 |
| 2.5 | Protobuf 定义 | Java ↔ Python 共享的接口定义 | `java-service/src/main/proto/ai-service.proto`, `python-ai-service/proto/ai-service.proto` | P0 |
| 2.6 | Java 告警接口 | 接收 AIoT 设备上报，调用 Python 检索预案 | `src/main/java/com/ehs/interfaces/controller/AlertController.java` | P0 |
| 2.7 | Multi-Agent 完整 4 Agent | 路径规划 Agent + 资源调度 Agent | `python-ai-service/src/agents/path_agent.py`, `src/agents/resource_agent.py` | P1 |
| 2.8 | 前端 7 个页面 | Dashboard、知识库、告警管理、Agent 协同、评估回放、系统设置、操作日志 | `admin-console/src/pages/` | P1 |
| 2.9 | 预设场景 4 个 | 火灾、气体泄漏、温度异常、入侵检测 | `admin-console/src/pages/alert/SimulateAlert.tsx` | P1 |
| 2.10 | TOGAF+DDD 架构文档 | 5 层架构文档（业务、数据、应用、技术、领域） | `docs/architecture/togaf-ddd.md`, `onion-architecture.md`, `cola-architecture.md` | P2 |

**阶段 2 验收标准：**
- ✅ AIoT 设备上报 → Java 接收 → gRPC 调用 Python → 返回告警 + 预案
- ✅ 4 个 Agent 阶段正确执行，前端可可视化展示
- ✅ 所有前端页面可正常渲染，路由可跳转
- ✅ Java 服务可独立编译运行，单元测试覆盖率 > 70%

---

### 10.4 阶段 3 详细任务（生产级）

**目标：** 证明生产级落地能力和架构师思维。

| 任务 ID | 任务名称 | 详细描述 | 产出文件 | 优先级 |
|--------|---------|---------|---------|--------|
| 3.1 | LLMOps 完整评估 | Ragas 四项指标 + LangFuse 链路追踪 | `python-ai-service/src/llmops/ragas_eval.py`, `langfuse_client.py` | P0 |
| 3.2 | GraphRAG 三路召回 | 添加 Neo4j 图谱检索 | `python-ai-service/src/rag/neo4j_search.py` | P1 |
| 3.3 | K8s 部署配置 | Java 和 Python 服务的 Deployment + Service + Ingress | `deployments/java-service.yaml`, `python-ai-service.yaml`, `ingress.yaml` | P1 |
| 3.4 | Prometheus 监控 | 指标采集配置，自定义业务指标 | `monitoring/prometheus-rules.yaml`, `prometheus-config.yaml` | P1 |
| 3.5 | Grafana 仪表盘 | 系统监控 + 业务监控仪表盘配置 | `monitoring/grafana/dashboards/ehs-overview.json` | P1 |
| 3.6 | Harness 实践文章 | 空窗期学习成果总结 | `docs/blog/harness-practice.md` | P2 |
| 3.7 | 项目 README | 安装、运行、演示说明，面试官指引 | `README.md` | P0 |
| 3.8 | 单元测试补充 | 核心模块测试用例，覆盖率提升至 80%+ | `tests/` | P1 |

**阶段 3 验收标准：**
- ✅ Ragas Faithfulness > 0.9，Recall > 0.85
- ✅ P99 响应时间 < 800ms
- ✅ 单元测试覆盖率 > 80%
- ✅ 可一键部署（`kubectl apply -f deployments/`）
- ✅ README 完整，面试官可直接克隆运行

---

### 10.5 依赖关系图

```
阶段 1（MVP）
    │
    ├──→ 阶段 2（全栈）
    │       │
    │       ├──→ 阶段 3（生产级）
    │       │
    │       └──→ 面试演示就绪
```

**关键路径：**
```
1.1 CLAUDE.md → 1.2 项目骨架 → 1.3 GraphRAG → 1.4 Multi-Agent → 1.5 前端
                                                      ↓
1.1 → 2.1 Java 骨架 → 2.2 DDD → 2.3 COLA → 2.4 gRPC → 2.6 告警接口
                                                      ↓
                              2.7 4 Agent → 3.1 LLMOps → 3.3 K8s → README
```

---

### 10.6 面试时间节点规划

| 时间点 | 目标 | 必须完成的任务 |
|--------|------|---------------|
| **第 2 周末** | MVP 可演示 | 阶段 1 全部（1.1~1.6） |
| **第 5 周末** | 全栈可展示 | 阶段 2 核心（2.1~2.9） |
| **第 7 周末** | 生产级完整 | 阶段 3 核心（3.1、3.3、3.5、3.7） |
| **面试前** | 文档完善 | TOGAF+DDD 文档、Harness 文章、README |

**弹性策略：**
- 如果时间紧张，优先保证**阶段 1 + 阶段 2 核心**（2.1~2.6）
- 阶段 3 的 Neo4j、K8s、Grafana 可以在面试时说"已设计，待部署"
- Harness 实践文章是差异化亮点，建议提前完成

---

## 11. 参考资料

### 技术文档
- [Anthropic Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code)
- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [GraphRAG 论文](https://arxiv.org/abs/2404.16130)
- [Ragas 评估框架](https://docs.ragas.io/)
- [LangFuse 链路追踪](https://langfuse.com/docs)
- [vLLM 推理服务](https://docs.vllm.ai/)

### 架构方法论
- [TOGAF 企业架构](https://www.opengroup.org/togaf)
- [DDD 领域驱动设计](https://domainlanguage.com/ddd/)
- [COLA 架构框架](https://github.com/alibaba/COLA)
- [DDD 洋葱架构](https://jeffreyfulton.ca/blog/onion-architecture)

### gRPC 与微服务
- [gRPC 官方文档](https://grpc.io/docs/)
- [Protobuf 语言指南](https://protobuf.dev/programming-guides/proto3/)
- [Spring Cloud gRPC](https://github.com/yidongnan/grpc-spring-boot-starter)

### 前端技术
- [React 18 官方文档](https://react.dev/)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)
- [Ant Design 组件库](https://ant.design/)
- [TailwindCSS 工具类](https://tailwindcss.com/docs)

### 部署与监控
- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [Prometheus 监控](https://prometheus.io/docs/)
- [Grafana 仪表盘](https://grafana.com/docs/)

---

**文档结束**