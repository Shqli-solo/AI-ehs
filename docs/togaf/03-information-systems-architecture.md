# TOGAF 阶段 C: 信息系统架构 (Information Systems Architecture)

> **版本**: v1.0  
> **创建日期**: 2026-04-16  
> **状态**: 初稿  
> **关联计划**: [阶段 2 实施计划](../superpowers/plans/2026-04-15-ehs-stage2-plan.md)

---

## 1. 文档概述

### 1.1 目的
本文档定义 EHS 智能安保决策中台的信息系统架构，包括数据架构和应用架构。

### 1.2 范围
- **数据架构**: 数据模型、数据存储、数据流
- **应用架构**: 应用组件、接口、集成

---

## 2. 数据架构

### 2.1 数据域划分
| 数据域 | 描述 | 主要实体 | 存储方式 |
|--------|------|----------|----------|
| 告警数据 | 告警事件及处置记录 | Alert, AlertHistory | MySQL + ES |
| 预案数据 | 应急预案及版本 | Plan, PlanVersion | MySQL + ES + Milvus |
| 用户数据 | 用户信息及权限 | User, Role, Permission | MySQL + Redis |
| 设备数据 | 传感器及设备信息 | Device, Sensor | MySQL |
| 日志数据 | 系统日志和审计日志 | Log, AuditLog | ES |
| 模型数据 | AI 模型及训练数据 | Model, TrainingData | MinIO + MySQL |

### 2.2 核心数据模型

#### 2.2.1 告警 (Alert)
```
Alert
├── id: UUID                    # 告警 ID
├── title: String               # 告警标题
├── description: String         # 告警描述
├── riskLevel: Enum             # 风险等级 (LOW/MEDIUM/HIGH/CRITICAL)
├── status: Enum                # 状态 (PENDING/PROCESSING/RESOLVED/CLOSED)
├── location: String            # 发生地点
├── deviceIds: List<UUID>       # 关联设备 ID 列表
├── reportedAt: DateTime        # 上报时间
├── reportedBy: String          # 上报人
├── assignedTo: UUID            # 分配给的处理人
├── planId: UUID                # 关联预案 ID
├── disposition: String         # 处置结果
├── closedAt: DateTime          # 关闭时间
├── metadata: JSON              # 扩展元数据
└── createdAt/UpdatedAt: DateTime
```

#### 2.2.2 预案 (Plan)
```
Plan
├── id: UUID                    # 预案 ID
├── title: String               # 预案标题
├── category: Enum              # 分类 (FIRE/GAS/INTRUSION/...)
├── riskLevel: Enum             # 适用风险等级
├── content: Text               # 预案内容 (Markdown)
├── steps: List<Step>           # 处置步骤
├── version: Integer            # 版本号
├── status: Enum                # 状态 (DRAFT/PENDING/APPROVED/PUBLISHED)
├── tags: List<String>          # 标签
├── embeddings: Vector          # 向量嵌入 (Milvus)
├── authorId: UUID              # 作者 ID
├── approvedBy: UUID            # 审批人 ID
├── publishedAt: DateTime       # 发布时间
└── createdAt/UpdatedAt: DateTime

Step
├── order: Integer              # 步骤序号
├── action: String              # 行动描述
├── actor: String               # 执行人角色
├── timeout: Integer            # 超时时间 (秒)
└── checklist: List<String>     # 检查项
```

#### 2.2.3 用户 (User)
```
User
├── id: UUID                    # 用户 ID
├── username: String            # 用户名
├── email: String               # 邮箱
├── passwordHash: String        # 密码哈希
├── role: Enum                  # 角色 (SECURITY/ENGINEER/MANAGER/ADMIN)
├── permissions: List<String>   # 权限列表
├── department: String          # 部门
├── phone: String               # 电话
├── status: Enum                # 状态 (ACTIVE/INACTIVE/LOCKED)
├── lastLoginAt: DateTime       # 最后登录时间
└── createdAt/UpdatedAt: DateTime
```

### 2.3 数据存储架构
```
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐                                                │
│  │   MySQL     │  业务数据                                       │
│  │             │  - 用户/权限                                    │
│  │             │  - 告警记录                                     │
│  │             │  - 预案元数据                                   │
│  │             │  - 设备信息                                     │
│  └─────────────┘                                                │
│                                                                  │
│  ┌─────────────┐                                                │
│  │Elasticsearch│  检索数据                                       │
│  │             │  - 告警全文检索                                 │
│  │             │  - 预案全文检索                                 │
│  │             │  - 日志存储                                     │
│  └─────────────┘                                                │
│                                                                  │
│  ┌─────────────┐                                                │
│  │   Milvus    │  向量数据                                       │
│  │             │  - 预案向量嵌入                                 │
│  │             │  - 告警向量嵌入                                 │
│  │             │  - 术语向量嵌入                                 │
│  └─────────────┘                                                │
│                                                                  │
│  ┌─────────────┐                                                │
│  │   Neo4j     │  图谱数据                                       │
│  │             │  - 事故 - 原因图谱                              │
│  │             │  - 预案 - 场景图谱                              │
│  │             │  - 设备 - 位置图谱                              │
│  └─────────────┘                                                │
│                                                                  │
│  ┌─────────────┐                                                │
│  │   Redis     │  缓存数据                                       │
│  │             │  - Session 缓存                                 │
│  │             │  - 热点数据缓存                                 │
│  │             │  - 分布式锁                                     │
│  └─────────────┘                                                │
│                                                                  │
│  ┌─────────────┐                                                │
│  │   MinIO     │  对象存储                                       │
│  │             │  - 模型文件                                     │
│  │             │  - 附件文件                                     │
│  │             │  - 备份数据                                     │
│  └─────────────┘                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 数据流图
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   传感器     │────▶│  告警上报     │────▶│  风险分级     │
│   Device     │     │   API        │     │   Agent      │
└──────────────┘     └──────────────┘     └──────────────┘
                              │                    │
                              ▼                    ▼
                       ┌──────────────┐    ┌──────────────┐
                       │   MySQL      │    │   LLM        │
                       │   写入告警    │    │   推理       │
                       └──────────────┘    └──────────────┘
                                                      │
                              ┌───────────────────────┘
                              ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   预案检索    │◀────│  结果融合    │◀────│  三路召回    │
│   Reranker   │     │   Fusion     │     │  ES/Milvus/Neo4j
└──────────────┘     └──────────────┘     └──────────────┘
         │
         ▼
┌──────────────┐     ┌──────────────┐
│   前端展示    │────▶│   处置执行    │
│   UI         │     │   Execute    │
└──────────────┘     └──────────────┘
```

---

## 3. 应用架构

### 3.1 应用组件图
```
┌─────────────────────────────────────────────────────────────────┐
│                        应用架构                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  前端应用 (Frontend Applications)                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Admin Console (Next.js 14)                              │   │
│  │  - Dashboard 页面                                        │   │
│  │  - 告警管理页面                                          │   │
│  │  - 预案管理页面                                          │   │
│  │  - 事故分析页面                                          │   │
│  │  - 系统配置页面                                          │   │
│  │  - 用户管理页面                                          │   │
│  │  - 监控仪表盘页面                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  业务应用 (Business Applications)                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  EHS Business Service (Java COLA)                        │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  Application Layer                               │    │   │
│  │  │  - AlertService / PlanService / UserService     │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  Domain Layer                                    │    │   │
│  │  │  - Alert / Plan / User 实体                      │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  Infrastructure Layer                            │    │   │
│  │  │  - MySQL Repository / gRPC Client               │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  AI 应用 (AI Applications)                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  EHS AI Service (Python FastAPI)                         │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  REST API Layer                                  │    │   │
│  │  │  - /api/alert/report                            │    │   │
│  │  │  - /api/plan/search                             │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  Core Layer (Hexagonal)                          │    │   │
│  │  │  - GraphRAG / Multi-Agent                        │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  Adapters Layer                                  │    │   │
│  │  │  - ES / Milvus / Neo4j / LLM                     │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 前端应用架构

#### 3.2.1 页面结构
| 页面 | 路由 | 功能 | 组件 |
|------|------|------|------|
| Dashboard | `/` | 总览仪表盘 | Dashboard, StatsCard, AlertChart |
| 告警列表 | `/alerts` | 告警管理 | AlertList, AlertDetail, AlertFilter |
| 预案检索 | `/plans` | 预案管理 | PlanList, PlanSearch, PlanDetail |
| 事故分析 | `/incidents` | 事故分析 | IncidentTimeline, RootCauseAnalysis |
| 系统配置 | `/settings` | 系统设置 | SystemConfig, DeviceConfig |
| 用户管理 | `/users` | 用户管理 | UserList, UserForm, RoleManager |
| 监控仪表盘 | `/monitoring` | 系统监控 | MetricsDashboard, HealthCheck, Logs |

#### 3.2.2 前端技术栈
| 层次 | 技术 | 说明 |
|------|------|------|
| 框架 | Next.js 14 | SSR + App Router |
| 语言 | TypeScript | 类型安全 |
| UI 组件 | Shadcn/UI | 现代化设计系统 |
| 样式 | TailwindCSS | 原子化 CSS |
| 状态管理 | React Query + Zustand | 服务端状态 + 客户端状态 |
| 表单 | React Hook Form + Zod | 表单验证 |
| 图表 | Recharts | 数据可视化 |

### 3.3 API 设计

#### 3.3.1 REST API 规范
```yaml
# 告警相关
POST   /api/alerts           # 上报告警
GET    /api/alerts           # 获取告警列表
GET    /api/alerts/{id}      # 获取告警详情
PUT    /api/alerts/{id}      # 更新告警
POST   /api/alerts/{id}/dispose  # 处置告警

# 预案相关
GET    /api/plans            # 检索预案
GET    /api/plans/{id}       # 获取预案详情
POST   /api/plans            # 创建预案
PUT    /api/plans/{id}       # 更新预案
DELETE /api/plans/{id}       # 删除预案

# 用户相关
GET    /api/users            # 用户列表
POST   /api/users            # 创建用户
PUT    /api/users/{id}       # 更新用户
DELETE /api/users/{id}       # 删除用户

# 系统相关
GET    /api/health           # 健康检查
GET    /api/metrics          # 监控指标
GET    /api/logs             # 系统日志
```

#### 3.3.2 gRPC 服务定义
```protobuf
syntax = "proto3";

package ehs;

// AI 服务
service AIService {
  rpc AssessRisk(RiskRequest) returns (RiskResponse);
  rpc SearchPlans(PlanSearchRequest) returns (PlanSearchResponse);
}

// 业务服务
service BusinessService {
  rpc CreateAlert(AlertRequest) returns (AlertResponse);
  rpc GetAlert(AlertIdRequest) returns (AlertResponse);
  rpc ListAlerts(ListAlertsRequest) returns (ListAlertsResponse);
}

message RiskRequest {
  string alert_description = 1;
  map<string, string> context = 2;
}

message RiskResponse {
  string risk_level = 1;
  double confidence = 2;
  string reasoning = 3;
}

message PlanSearchRequest {
  string query = 1;
  int32 top_k = 2;
  repeated string filters = 3;
}

message PlanSearchResponse {
  repeated Plan plans = 1;
}

message Plan {
  string id = 1;
  string title = 2;
  string content = 3;
  double score = 4;
}
```

### 3.4 应用集成

#### 3.4.1 集成架构
```
┌─────────────────┐         ┌─────────────────┐
│  Admin Console  │────────▶│ EHS Business    │
│  (Next.js)      │  REST   │ (Java COLA)     │
└─────────────────┘         └─────────────────┘
                                     │
                                     │ gRPC
                                     ▼
                          ┌─────────────────┐
                          │ EHS AI          │
                          │ (Python FastAPI)│
                          └─────────────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     ▼               ▼               ▼
              ┌────────────┐  ┌────────────┐  ┌────────────┐
              │  Milvus    │  │     ES     │  │   Neo4j    │
              │  (向量)    │  │  (文档)    │  │   (图谱)   │
              └────────────┘  └────────────┘  └────────────┘
```

#### 3.4.2 集成模式
| 集成类型 | 模式 | 技术 | 说明 |
|----------|------|------|------|
| 前端→业务 | 同步请求/响应 | HTTP/REST | 用户操作驱动 |
| 业务→AI | 同步请求/响应 | gRPC | 低延迟，强类型 |
| AI→外部服务 | 同步请求/响应 | HTTP/gRPC | LLM/向量库调用 |
| 传感器→系统 | 异步消息 | MQTT/HTTP | 告警上报 |
| 系统→通知 | 异步消息 | WebSocket | 实时推送 |

---

## 4. 数据治理

### 4.1 数据质量管理
| 维度 | 要求 | 实现方式 |
|------|------|----------|
| 完整性 | 必填字段 100% 填充 | 输入验证，默认值 |
| 准确性 | 数据准确率>99% | 数据校验，人工复核 |
| 一致性 | 跨系统数据一致 | 事务保证，最终一致性 |
| 及时性 | 数据延迟<1s | 实时写入，流处理 |

### 4.2 数据安全
| 安全级别 | 数据类型 | 保护措施 |
|----------|----------|----------|
| 机密 | 密码/Token | 加密存储，哈希处理 |
| 敏感 | 用户信息 | 访问控制，脱敏展示 |
| 内部 | 业务数据 | 角色授权，审计日志 |
| 公开 | 公开信息 | 基础访问控制 |

### 4.3 数据生命周期
| 阶段 | 数据类型 | 保留策略 |
|------|----------|----------|
| 热数据 | 最近 30 天告警 | 在线存储，快速访问 |
| 温数据 | 30-90 天数据 | 近线存储，定期归档 |
| 冷数据 | 90 天以上 | 离线存储，压缩归档 |
| 过期数据 | 超保留期限 | 安全删除 |

---

## 5. 审批记录

| 角色 | 姓名 | 日期 | 状态 | 意见 |
|------|------|------|------|------|
| 数据架构师 | - | - | 待审批 | - |
| 应用架构师 | - | - | 待审批 | - |
| 技术负责人 | - | - | 待审批 | - |

---

**文档维护**: 本文档随系统演进而更新，重大变更需架构评审委员会审批。
