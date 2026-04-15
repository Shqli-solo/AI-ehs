# EHS 智能安保决策中台 - 阶段 2 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从 MVP (v1.0.1) 升级到生产级系统，实现 Monorepo 架构、真实 LLM 集成、微调模型、完整测试覆盖、CI/CD、K8s Helm 部署。

**Architecture:** Monorepo 包含 3 个项目 (Next.js 前端、Java COLA 业务服务、Python 六边形 AI 服务)，通过 REST + gRPC 通信，部署在 K8s 集群。

**Tech Stack:** Next.js 14 + TypeScript + Tailwind + Shadcn, Java 17 + Spring Boot + COLA + gRPC, Python 3.11 + FastAPI + LangGraph + PyTorch + vLLM, Docker + K8s Helm + GitHub Actions, Prometheus + Grafana + LangFuse

---

## Wave 并行方案

| Wave | 任务 | 预计时间 | 依赖 |
|------|------|---------|------|
| **Wave 1** | 数据准备 + 前端 (Mock) + 文档 (初稿) + Docker 基础 | 2-3 天 | 无 |
| **Wave 2** | 微调模型训练 | 3-5 天 | 数据准备 |
| **Wave 3** | Python AI 服务集成 + 前端改真实 API + Java 服务 (Mock) | 5-7 天 | 微调模型 |
| **Wave 4** | Java gRPC 集成 + 监控集成 | 2-3 天 | Python 服务 |
| **Wave 5** | K8s Helm 验证 + E2E 测试 + 性能测试 | 2-3 天 | 全部服务 |

**总工期：16-21 天（关键路径）**

---

## Wave 1: 数据准备 + 前端 (Mock) + 文档 + Docker 基础 (2-3 天)

### Task 1.1: Monorepo 项目骨架搭建

**Files:**
- Create: `apps/admin-console/package.json`
- Create: `apps/ehs-business/pom.xml`
- Create: `apps/ehs-ai/pyproject.toml`
- Create: `package.json` (workspace root)
- Create: `.gitignore`
- Create: `Makefile` (DX)
- Create: `scripts/setup.sh` (DX)
- Create: `scripts/run-tests.sh` (DX)
- Test: `tests/test_monorepo.py`

**验收标准:**
- Monorepo 目录结构正确
- 三个子项目配置完整
- Makefile 提供 `make dev`, `make test`, `make build` 入口
- scripts 目录包含 setup 和测试运行脚本
- 测试通过

**工作量:** 2 小时

### Task 1.2: 前端 Next.js 项目初始化

**Files:**
- Create: `apps/admin-console/src/app/layout.tsx`
- Create: `apps/admin-console/src/app/page.tsx`
- Create: `apps/admin-console/tsconfig.json`
- Create: `apps/admin-console/next.config.js`
- Create: `apps/admin-console/tailwind.config.js`
- Create: `apps/admin-console/src/components/ui/button.tsx`
- Create: `apps/admin-console/src/lib/design-tokens.ts` (Design)
- Create: `apps/admin-console/docs/wireframes.md` (Design - 7 个页面线框图)
- Test: `apps/admin-console/src/app/page.test.tsx`

**验收标准:**
- Dashboard 页面渲染正常
- Mock 数据展示正确
- UI 状态规范定义（Loading 骨架屏/Empty 插画 + 文案/Error Banner+ 重试/Success Toast）
- 统一使用 Shadcn/UI 组件库
- 7 个页面线框图（ASCII 或 Excalidraw）
- 响应式断点定义（mobile: <640px, tablet: 640-1024px, desktop: >1024px）
- 无障碍设计（WCAG 2.1 AA 合规，键盘导航，对比度≥4.5:1）
- 设计令牌（颜色/字体/间距/图标系统）
- 测试通过

**工作量:** 3.5 小时

### Task 1.3: EHS 预案数据准备

**Files:**
- Create: `scripts/data/prepare_data.py`
- Create: `scripts/data/templates/ehs_plan_template.json`
- Create: `scripts/data/validate_schema.py` (Eng - 数据验证)
- Create: `data/raw/plans/sample_plans.json`
- Test: `tests/test_data_prep.py`

**验收标准:**
- 样本预案数据格式正确
- 数据脚本运行成功
- 生成指令微调和风险分级数据
- 数据验证脚本检测空样本、重复样本、格式错误
- LLM 生成数据需人工校验（预留 2-3 天数据准备时间）

**工作量:** 8 小时（含数据校验）

### Task 1.4: Docker Compose 基础配置

**Files:**
- Create: `infra/docker-compose.yml`
- Create: `infra/docker/ehs-ai/Dockerfile`
- Create: `infra/docker/admin-console/Dockerfile`
- Create: `infra/docker/ehs-business/Dockerfile`
- Create: `docs/getting-started.md` (DX - 5 分钟快速入门)
- Test: `tests/test_docker.py`

**验收标准:**
- Docker Compose 配置完整
- 所有 Dockerfile 可构建
- getting-started.md 包含 5 分钟快速入门（复制 - 粘贴 - 运行 - 验证）
- 测试通过

**工作量:** 2 小时

### Task 1.5: TOGAF 架构文档 (初稿)

**Files:**
- Create: `docs/togaf/01-architecture-vision.md`
- Create: `docs/togaf/02-business-architecture.md`
- Create: `docs/togaf/03-information-systems-architecture.md`
- Create: `docs/togaf/04-technology-architecture.md`

**验收标准:**
- TOGAF 4 个阶段文档完整
- 内容覆盖设计文档要求

**工作量:** 2 小时

---

## Wave 2: 微调模型训练 (3-5 天)

### Task 2.1: 指令微调训练脚本

**Files:**
- Create: `scripts/fine_tune/instruction_tuning.py`
- Create: `src/ehs-ai/models/instruction_model.py`
- Create: `src/ehs-ai/models/callbacks.py` (Eng - 早停/checkpoint)
- Create: `scripts/fine_tune/plot_training_curves.py` (Eng - 损失可视化)
- Test: `tests/test_instruction_tuning.py`

**验收标准:**
- 数据集加载正确
- 训练脚本可运行
- LoRA 配置正确
- 数据验证脚本检测空样本、重复样本、格式错误
- 训练曲线实时记录（TensorBoard/MLflow）
- 早停条件：validation_loss 连续 3 epoch 不下降
- 每 epoch 保存 checkpoint，支持断点恢复

**工作量:** 8 小时（含调参和监控）

### Task 2.2: 风险分级模型训练

**Files:**
- Create: `scripts/fine_tune/risk_classification.py`
- Create: `src/ehs-ai/models/risk_classifier.py`
- Create: `scripts/fine_tune/evaluate_model.py` (Eng - 模型评估)
- Test: `tests/test_risk_classifier.py`

**验收标准:**
- 模型可预测风险等级
- 训练脚本可运行
- 测试通过
- 过拟合检测：训练集 vs 测试集 accuracy 差异 < 10%
- 混淆矩阵和 F1 分数报告

**工作量:** 6 小时

### Task 2.3: 术语 Embedding 微调

**Files:**
- Create: `scripts/fine_tune/embedding_tuning.py`
- Create: `src/ehs-ai/models/embedding_model.py`
- Create: `scripts/fine_tune/evaluate_embedding.py` (Eng - 相似度评估)
- Test: `tests/test_embedding_model.py`

**验收标准:**
- Embedding 模型可编码文本
- 相似度排序正确
- 测试通过
- 术语对数据质量验证（同义词、上下位词）
- 相似度评估报告（top-1/top-5 准确率）

**工作量:** 6 小时

---

## Wave 3: Python AI 服务集成 + 前端真实 API + Java 服务 (5-7 天)

### Task 3.1: Python AI 服务六边形重构

**Files:**
- Create: `apps/ehs-ai/src/core/graph_rag.py`
- Create: `apps/ehs-ai/src/core/agents/workflow.py`
- Create: `apps/ehs-ai/src/adapters/primary/rest_api.py`
- Create: `apps/ehs-ai/src/adapters/secondary/elasticsearch.py`
- Create: `apps/ehs-ai/src/adapters/secondary/milvus.py`
- Create: `apps/ehs-ai/src/container.py` (Eng - DI 容器)
- Create: `apps/ehs-ai/src/ports/secondary/storage.py` (Eng - 接口定义)
- Create: `docs/api/openapi.yaml` (DX - API 文档)
- Create: `docs/api-examples.md` (DX - API 使用示例)
- Test: `apps/ehs-ai/tests/test_hexagonal.py`

**验收标准:**
- 六边形架构清晰分离
- 核心域、驱动适配器、被驱动适配器职责明确
- 依赖注入容器实现（支持 Mock/真实实现切换）
- 接口定义明确（Ports 目录）
- OpenAPI spec 导出到 `docs/api/openapi.yaml`
- API 使用示例文档（curl + Python SDK）
- 测试通过

**工作量:** 6 小时

### Task 3.2: Multi-Agent LangGraph 工作流

**Files:**
- Create: `apps/ehs-ai/src/core/agents/risk_agent.py`
- Create: `apps/ehs-ai/src/core/agents/search_agent.py`
- Create: `apps/ehs-ai/src/core/agents/workflow.py`
- Create: `apps/ehs-ai/src/core/agents/output_validators.py` (Eng - LLM 输出验证)
- Test: `apps/ehs-ai/tests/test_agents.py`

**验收标准:**
- RiskAgent 可评估风险
- SearchAgent 可检索预案
- LangGraph 工作流正确编排
- LLM 输出结构化验证（使用 pydantic/instructor）
- 错误降级处理（LLM 失败时 fallback 到规则）
- 测试通过

**工作量:** 5 小时

### Task 3.3: 前端真实 API 集成

**Files:**
- Modify: `apps/admin-console/src/app/page.tsx`
- Create: `apps/admin-console/src/services/api.ts`
- Create: `apps/admin-console/src/hooks/use-alerts.ts`
- Create: `apps/admin-console/src/lib/api-errors.ts` (Eng - 错误码映射)
- Test: `apps/admin-console/src/services/api.test.ts`

**验收标准:**
- API 服务正确调用后端
- 自定义 Hook 可复用
- 错误处理完善（统一错误码映射）
- 错误消息包含"问题 + 原因 + 修复"结构
- 测试通过

**工作量:** 3.5 小时

### Task 3.4: Java COLA 服务骨架

**Files:**
- Create: `apps/ehs-business/src/main/java/com/ehs/business/EhsBusinessApplication.java`
- Create: `apps/ehs-business/src/main/java/com/ehs/business/application/alert/AlertService.java`
- Create: `apps/ehs-business/src/main/java/com/ehs/business/domain/alert/Alert.java`
- Create: `apps/ehs-business/src/main/java/com/ehs/business/infrastructure/grpc/PythonAiClient.java`
- Create: `apps/ehs-business/src/main/java/com/ehs/business/security/JwtAuthFilter.java` (Eng - JWT 认证)
- Create: `apps/ehs-business/src/main/java/com/ehs/business/config/SecurityConfig.java` (Eng - 安全配置)
- Test: `apps/ehs-business/src/test/java/com/ehs/business/AlertServiceTest.java`

**验收标准:**
- Spring Boot 可启动
- COLA 四层架构清晰
- gRPC Client 预留接口
- JWT 认证基础架构（Token 生成/验证/刷新）
- 安全配置（CORS、CSRF、认证过滤器）
- 测试通过

**工作量:** 5 小时

---

## Wave 4: Java gRPC 集成 + 监控集成 (2-3 天)

### Task 4.1: gRPC Proto 定义

**Files:**
- Create: `apps/ehs-business/src/main/proto/ehs.proto`
- Create: `apps/ehs-ai/src/proto/ehs.proto`
- Create: `apps/ehs-business/src/main/java/com/ehs/business/config/GrpcConfig.java` (Eng - 超时/重试/熔断)
- Create: `infra/docker/certs/README.md` (Eng - TLS 证书配置)
- Test: `tests/test_grpc_proto.py`

**验收标准:**
- Proto 定义完整
- Python gRPC Server 框架就绪
- Java gRPC Client 可调用
- gRPC 超时配置（Deadline 120s）
- 重试策略（Max 3 次，指数退避）
- 熔断器（连续 10 次失败后停止）
- TLS 双向认证配置说明
- 测试通过

**工作量:** 3.5 小时

### Task 4.2: Prometheus + Grafana 监控集成

**Files:**
- Create: `apps/ehs-ai/src/monitoring/prometheus.py`
- Create: `apps/ehs-ai/src/monitoring/metrics.py`
- Create: `infra/prometheus.yml`
- Create: `infra/grafana/dashboards/ehs-overview.json`
- Test: `apps/ehs-ai/tests/test_monitoring.py`

**验收标准:**
- Prometheus 指标定义完整
- Grafana Dashboard 可导入
- 监控中间件可集成到 API

**工作量:** 2.5 小时

---

## Wave 5: K8s Helm 验证 + E2E 测试 + 性能测试 (2-3 天)

### Task 5.1: K8s Helm Chart 完整配置

**Files:**
- Create: `infra/k8s/ehs-helm/Chart.yaml`
- Create: `infra/k8s/ehs-helm/values.yaml`
- Create: `infra/k8s/ehs-helm/templates/frontend-deployment.yaml`
- Create: `infra/k8s/ehs-helm/templates/java-deployment.yaml`
- Create: `infra/k8s/ehs-helm/templates/python-deployment.yaml`
- Create: `infra/k8s/ehs-helm/templates/hpa.yaml`
- Create: `infra/k8s/ehs-helm/templates/networkpolicy.yaml`
- Test: `tests/test_helm.py`

**验收标准:**
- Helm Chart 结构完整
- 包含 HPA, PDB, NetworkPolicy
- 支持多环境 values 配置

**工作量:** 3.5 小时

### Task 5.2: E2E Playwright 测试

**Files:**
- Create: `tests/e2e/test_dashboard.spec.ts`
- Create: `tests/e2e/test_alerts.spec.ts`
- Create: `tests/e2e/test_plans.spec.ts`
- Create: `tests/e2e/playwright.config.ts`

**验收标准:**
- 10 个核心 E2E 场景覆盖
- 测试可通过 `npm run test:e2e` 运行

**工作量:** 2 小时

### Task 5.3: 性能测试 (Locust/k6)

**Files:**
- Create: `tests/performance/locustfile.py`
- Create: `tests/performance/k6/script.js`
- Create: `scripts/run_performance_test.sh`

**验收标准:**
- Locust 可运行 50 并发用户测试
- k6 阈值：P95 < 800ms, 错误率 < 1%
- 测试报告可生成

**工作量:** 2 小时

### Task 5.4: CI/CD GitHub Actions

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/release.yml`

**验收标准:**
- CI 流水线包含测试、构建、部署
- 覆盖 Python、Node、Java 三个项目

**工作量:** 1.5 小时

---

## 计划自审

### 1. Spec 覆盖率检查

| Spec 章节 | 对应 Task | 状态 |
|----------|-----------|------|
| 2. 架构设计 | Task 1.1, 3.1 | ✅ |
| 3. 微调方案 | Task 2.1, 2.2, 2.3 | ✅ |
| 4. 前端设计 | Task 1.2, 3.3 | ✅ |
| 5. 测试策略 | Task 5.2, 5.3 | ✅ |
| 6. 基础设施 | Task 1.4, 5.1 | ✅ |
| 7. CI/CD | Task 5.4 | ✅ |
| 8. LLMOps/MLOps | Task 4.2 | ✅ |
| 9. TOGAF 文档 | Task 1.5 | ✅ |

### 2. 依赖关系

```
Wave 1 (无依赖)
    ↓
Wave 2 (依赖数据准备)
    ↓
Wave 3 (依赖微调模型)
    ↓
Wave 4 (依赖 Python 服务)
    ↓
Wave 5 (依赖全部服务)
```

### 3. 关键路径

**16-21 天关键路径:** Wave 1 → Wave 2 → Wave 3 → Wave 4 → Wave 5

---

## /autoplan 多视角审查报告

### 审查执行摘要

| 审查视角 | 执行状态 | Critical | High | Medium | 审查者 |
|----------|----------|----------|------|--------|--------|
| CEO Review | ✅ 完成 | 1 | 4 | 2 | 独立 CEO 顾问 |
| Eng Review | ✅ 完成 | 3 | 4 | 3 | 独立高级工程师 |
| Design Review | ✅ 完成 | 3 | 5 | 5 | 独立产品设计师 |
| DX Review | ✅ 完成 | 2 | 5 | 5 | 独立 DX 工程师 |

**用户决策：保持完整 18 Task 范围，将审查发现融入到现有 Task 验收标准中。**

---

### 关键发现及整合方案

#### CEO 审查 → 整合到 Task 1.3 和 Task 2.x

**发现：** 微调数据假设过于乐观（500 条数据 1 小时准备→实际需 2-3 天）

**整合方案：**
- Task 1.3 验收标准增加："LLM 生成数据需人工校验，预留 2-3 天数据准备时间"
- Task 2.1-2.3 工作量调整：3h → 8h（含数据校验）

---

#### Eng 审查 → 整合到 Task 1.1/3.1/3.4/4.1

**发现：**
1. 三服务通信架构循环依赖风险
2. 微调训练缺少数据验证/损失监控/早停
3. 认证授权完全缺失
4. 六边形架构缺少 DI 方案
5. gRPC 无超时/重试/熔断/TLS

**整合方案：**
- Task 1.1 增加：`apps/ehs-ai/src/container.py` (DI 容器)
- Task 2.1 增加：`scripts/fine_tune/validate_data.py` (数据验证)
- Task 2.1 增加：`src/ehs-ai/models/callbacks.py` (早停/checkpoint)
- Task 3.1 增加：依赖注入实现和测试
- Task 3.4 增加：JWT 认证基础 (`src/ehs-ai/src/security/auth.py`)
- Task 4.1 增加：gRPC 超时/重试/熔断配置
- Task 4.1 增加：gRPC TLS 双向认证

---

#### Design 审查 → 整合到 Task 1.2

**发现：**
1. UI 状态完全缺失（Loading/Empty/Error/Success/Partial）
2. Ant Design vs Shadcn 选型冲突
3. 7 个页面无具体布局
4. 响应式/无障碍设计缺失

**整合方案：**
- Task 1.2 验收标准增加：
  - "定义 UI 状态规范（Loading 骨架屏/Empty 插画+ 文案/Error Banner+ 重试/Success Toast）"
  - "统一使用 Shadcn/UI（阶段 1 Ant Design 逐步迁移）"
  - "7 个页面线框图（ASCII 或 Excalidraw）"
  - "响应式断点（mobile: <640px, tablet: 640-1024px, desktop: >1024px）"
  - "无障碍设计（WCAG 2.1 AA 合规，键盘导航，对比度≥4.5:1）"

---

#### DX 审查 → 整合到 Task 1.1/1.4/5.4

**发现：**
1. 无独立 API 文档（OpenAPI/Swagger）
2. 错误消息缺乏可操作性
3. 缺少 5 分钟快速入门
4. 无 scripts 目录
5. 错误响应格式不一致

**整合方案：**
- Task 1.1 增加：`Makefile`（`make dev`, `make test`, `make build`）
- Task 1.1 增加：`scripts/setup.sh`, `scripts/run-tests.sh`
- Task 1.4 增加：`docs/getting-started.md`（5 分钟快速入门）
- Task 3.1 增加：`docs/api-examples.md`（curl/Python SDK 示例）
- Task 3.1 增加：导出 OpenAPI spec 到 `docs/api/openapi.yaml`
- Task 4.2 增加：错误码系统（`EHS_API_001` 参数验证失败等）
- Task 5.4 增加：迁移指南 `docs/migration-guide.md`

---

### 决策审计追踪

| # | 阶段 | 决策 | 分类 | 原则 | 理由 |
|---|------|------|------|------|------|
| 1 | CEO | 保持完整范围 | User Challenge | 用户决定 | 用户有领域知识，相信执行能力可压缩工期 |
| 2 | Eng | 增加认证授权到 Task 3.4 | Mechanical | P1 (完整性) | 生产系统必需，不增加额外 Task |
| 3 | Eng | 增加 DI 容器到 Task 3.1 | Mechanical | P5 (明确) | 六边形架构必需依赖注入 |
| 4 | Design | 统一使用 Shadcn/UI | Taste | P5 (明确) | 与 Next.js 14 集成更好 |
| 5 | Design | 补充 UI 状态规范到 Task 1.2 | Mechanical | P1 (完整性) | 生产级系统基本要求 |
| 6 | DX | 增加 API 文档到 Task 3.1 | Mechanical | P1 (完整性) | API 是开发者主要接触点 |
| 7 | DX | 添加错误码系统到 Task 4.2 | Mechanical | P5 (明确) | 便于问题定位 |
| 8 | 全部 | 新增文件不增加 Task 数 | User Challenge | 用户决定 | 通过整合而非扩展实现 |

---

### 最终审批门

**计划摘要：**
EHS 智能安保决策中台阶段 2 实施计划，18 个 Task 保持不变，将审查发现的 42 个问题整合到现有 Task 验收标准中。

**用户决定：**
- ✅ 保持 18 Task 完整范围
- ✅ 不削减微调模型（3 种保留）
- ✅ 保持 K8s Helm 完整配置
- ✅ 保持前端 7 个页面
- ✅ 审查发现整合到现有 Task，不新增 Task

**调整后验收标准：** 每个 Task 增加审查发现的要素，工作量重新估算

**调整后工期：** 保持 16-21 天（依靠执行效率压缩）

---

### 用户挑战响应

| 挑战 | 你原来的方向 | 用户决定 | 执行策略 |
|------|-------------|---------|----------|
| 范围 | 18 Task 全覆盖 | ✅ 保持 | 并行执行 Wave，最大化效率 |
| 微调 | 3 种模型 | ✅ 保持 | 数据准备用 LLM 生成+交叉验证加速 |
| Java COLA | 完整四层架构 | ✅ 保持 | 作为架构能力展示，预留真实业务逻辑 |
| K8s | 完整 Helm Chart | ✅ 保持 | Helm 作为生产级部署能力证明 |


---

## 执行选项

**计划完成并保存到** `docs/superpowers/plans/2026-04-15-ehs-stage2-plan.md`

**两种执行选项：**

**1. Subagent-Driven (推荐)** - 为每个 Task 分派一个全新的 subagent，Task 之间进行审查，快速迭代

**2. Inline Execution** - 在本会话中使用 executing-plans 执行任务，批量执行并设置检查点

**选择哪种方式？**
