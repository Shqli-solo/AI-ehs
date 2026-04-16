# TOGAF 阶段 D: 技术架构 (Technology Architecture)

> **版本**: v1.0  
> **创建日期**: 2026-04-16  
> **状态**: 初稿  
> **关联计划**: [阶段 2 实施计划](../superpowers/plans/2026-04-15-ehs-stage2-plan.md)

---

## 1. 文档概述

### 1.1 目的
本文档定义 EHS 智能安保决策中台的技术架构，包括技术栈、基础设施、部署架构和运维体系。

### 1.2 范围
- **技术栈**: 编程语言、框架、中间件
- **基础设施**: 计算、存储、网络
- **部署架构**: 容器化、编排、环境
- **运维体系**: 监控、日志、告警、CI/CD

---

## 2. 技术栈总览

### 2.1 技术选型矩阵
| 层次 | 技术 | 版本 | 选型理由 |
|------|------|------|----------|
| **前端** | Next.js | 14.x | SSR + App Router + 生态完善 |
| | TypeScript | 5.x | 类型安全 + 开发体验 |
| | Shadcn/UI | latest | 现代化设计 + 可定制 |
| | TailwindCSS | 3.x | 原子化 CSS + 高效开发 |
| **业务服务** | Java | 17.x | LTS + 企业级生态 |
| | Spring Boot | 3.x | 成熟框架 + 自动配置 |
| | COLA | 4.x | 清晰分层 + 阿里最佳实践 |
| | gRPC | 1.x | 高效 RPC + 多语言支持 |
| **AI 服务** | Python | 3.11.x | AI 生态 + 类型提示 |
| | FastAPI | 0.x | 高性能 + 自动文档 |
| | LangGraph | latest | Agent 编排 + 状态机 |
| | PyTorch | 2.x | 深度学习框架 |
| | vLLM | latest | 高性能 LLM 推理 |
| **数据存储** | MySQL | 8.x | 关系型数据库标准 |
| | Elasticsearch | 8.x | 全文检索 + 日志存储 |
| | Milvus | 2.x | 向量数据库 |
| | Neo4j | 5.x | 图数据库 |
| | Redis | 7.x | 缓存 + Session 存储 |
| | MinIO | latest | S3 兼容对象存储 |
| **基础设施** | Docker | latest | 容器化标准 |
| | Kubernetes | 1.x | 容器编排标准 |
| | Helm | 3.x | K8s 包管理 |
| **监控运维** | Prometheus | 2.x | 指标采集标准 |
| | Grafana | 10.x | 可视化仪表盘 |
| | LangFuse | latest | LLM 链路追踪 |
| | Loki | 2.x | 日志聚合 |
| **CI/CD** | GitHub Actions | latest | 原生集成 + 免费额度 |

### 2.2 技术雷达
```
┌─────────────────────────────────────────────────────────────────┐
│                        技术雷达                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  采纳 (Adopt)                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Next.js, TypeScript, Java 17, Spring Boot, Python 3.11  │   │
│  │ FastAPI, MySQL, Redis, Docker, Kubernetes, Prometheus   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  试用 (Trial)                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ LangGraph, vLLM, Milvus, Shadcn/UI, COLA                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  评估 (Assess)                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Neo4j, Helm, Grafana Loki, LangFuse                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  持有 (Hold)                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ jQuery, AngularJS, Python 2.x, MySQL 5.x                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 基础设施架构

### 3.1 容器化架构
```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker 容器架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ admin-console   │  │ ehs-business    │  │ ehs-ai          │ │
│  │ Node.js 18      │  │ Java 17         │  │ Python 3.11     │ │
│  │ :3000           │  │ :8080           │  │ :8000           │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
│  依赖容器：                                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ MySQL   │ │  Redis  │ │    ES   │ │ Milvus  │ │  Neo4j  │  │
│  │ :3306   │ │ :6379   │ │ :9200   │ │ :19530  │ │ :7687   │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│                                                                  │
│  监控容器：                                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Prometheus  │ │  Grafana    │ │   LangFuse  │              │
│  │ :9090       │ │ :3000       │ │ :3001       │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Docker Compose 配置
```yaml
# infra/docker-compose.yml
version: '3.8'

services:
  # 应用服务
  admin-console:
    build: ./docker/admin-console
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://ehs-business:8080
    depends_on:
      - ehs-business

  ehs-business:
    build: ./docker/ehs-business
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=mysql://root:password@mysql:3306/ehs
      - GRPC_AI_URL=ehs-ai:8000
    depends_on:
      - mysql
      - ehs-ai

  ehs-ai:
    build: ./docker/ehs-ai
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - MILVUS_URL=milvus:19530
      - ES_URL=http://elasticsearch:9200
    depends_on:
      - milvus
      - elasticsearch

  # 数据存储
  mysql:
    image: mysql:8.0
    volumes:
      - mysql-data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=ehs

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

  elasticsearch:
    image: elasticsearch:8.11.0
    volumes:
      - es-data:/usr/share/elasticsearch/data
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false

  milvus:
    image: milvusdb/milvus:v2.3.0
    volumes:
      - milvus-data:/var/lib/milvus
    depends_on:
      - etcd
      - minio

  neo4j:
    image: neo4j:5.14
    volumes:
      - neo4j-data:/data
    environment:
      - NEO4J_AUTH=neo4j/password

  # 监控
  prometheus:
    image: prom/prometheus:v2.48.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:10.2.0
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3001:3000"

volumes:
  mysql-data:
  redis-data:
  es-data:
  milvus-data:
  neo4j-data:
  prometheus-data:
  grafana-data:
```

### 3.3 Kubernetes 部署架构
```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes 集群架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Ingress Controller (Nginx)                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  /          → admin-console (Service)                   │   │
│  │  /api/*     → ehs-business (Service)                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  命名空间：ehs-production                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Deployments:                                            │   │
│  │  ┌─────────────────┐  ┌─────────────────┐              │   │
│  │  │ admin-console   │  │ ehs-business    │              │   │
│  │  │ replicas: 3     │  │ replicas: 3     │              │   │
│  │  │ HPA: 3-10       │  │ HPA: 3-10       │              │   │
│  │  └─────────────────┘  └─────────────────┘              │   │
│  │  ┌─────────────────┐                                   │   │
│  │  │ ehs-ai          │                                   │   │
│  │  │ replicas: 2     │                                   │   │
│  │  │ HPA: 2-8        │                                   │   │
│  │  │ GPU: true       │                                   │   │
│  │  └─────────────────┘                                   │   │
│  │                                                          │   │
│  │  StatefulSets:                                           │   │
│  │  - MySQL (主从复制)                                       │   │
│  │  - Redis Cluster                                         │   │
│  │  - Elasticsearch                                         │   │
│  │  - Milvus                                                │   │
│  │  - Neo4j                                                 │   │
│  │                                                          │   │
│  │  ConfigMaps:                                             │   │
│  │  - app-config      (应用配置)                            │   │
│  │  - nginx-conf      (Nginx 配置)                          │   │
│  │                                                          │   │
│  │  Secrets:                                                │   │
│  │  - db-credentials  (数据库凭证)                          │   │
│  │  - api-keys        (API 密钥)                            │   │
│  │  - tls-certs       (TLS 证书)                            │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  命名空间：ehs-monitoring                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Prometheus Operator + Grafana Stack                     │   │
│  │  - Prometheus Cluster                                    │   │
│  │  - Alertmanager                                          │   │
│  │  - Grafana                                               │   │
│  │  - Loki (日志)                                           │   │
│  │  - Tempo (追踪)                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 Helm Chart 结构
```
infra/k8s/ehs-helm/
├── Chart.yaml              # Chart 元数据
├── values.yaml             # 默认配置值
├── values-dev.yaml         # 开发环境配置
├── values-prod.yaml        # 生产环境配置
├── templates/
│   ├── _helpers.tpl        # 模板助手函数
│   ├── namespace.yaml      # 命名空间
│   ├── configmap.yaml      # 配置
│   ├── secrets.yaml        # 密钥
│   │
│   │── # 前端
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── frontend-hpa.yaml
│   │
│   │── # 业务服务
│   ├── business-deployment.yaml
│   ├── business-service.yaml
│   ├── business-hpa.yaml
│   │
│   │── # AI 服务
│   ├── ai-deployment.yaml
│   ├── ai-service.yaml
│   ├── ai-hpa.yaml
│   │
│   │── # 数据库
│   ├── mysql-statefulset.yaml
│   ├── redis-statefulset.yaml
│   │
│   │── # 网络
│   ├── ingress.yaml
│   ├── networkpolicy.yaml
│   │
│   │── # 监控
│   ├── prometheus-rbac.yaml
│   ├── servicemonitor.yaml
│   │
│   └── # 弹性
│       ├── pdb.yaml        # Pod 离散预算
│       └── autoscaler.yaml # 自动伸缩
└── charts/                 # 子 Chart 依赖
```

---

## 4. 网络架构

### 4.1 网络拓扑
```
┌─────────────────────────────────────────────────────────────────┐
│                        网络拓扑                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Internet                                                        │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────┐                                                │
│  │   WAF       │  Web 应用防火墙                                  │
│  │  (Cloudflare)│                                               │
│  └─────────────┘                                                │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────┐                                                │
│  │  LB (SLB)   │  负载均衡                                       │
│  └─────────────┘                                                │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   VPC 私有网络                           │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │               DMZ 区 (公网)                       │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐              │   │   │
│  │  │  │   Ingress   │  │   Bastion   │              │   │   │
│  │  │  │  Controller │  │    Host     │              │   │   │
│  │  │  └─────────────┘  └─────────────┘              │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                          │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │              应用区 (私有)                        │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐              │   │   │
│  │  │  │  Frontend   │  │  Business   │              │   │   │
│  │  │  │   Pods      │  │   Pods      │              │   │   │
│  │  │  └─────────────┘  └─────────────┘              │   │   │
│  │  │  ┌─────────────┐                               │   │   │
│  │  │  │  AI Pods    │  (GPU Node)                   │   │   │
│  │  │  └─────────────┘                               │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                          │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │              数据区 (私有)                        │   │   │
│  │  │  ┌─────────────────────────────────────────┐   │   │
│  │  │  │  MySQL / Redis / ES / Milvus / Neo4j    │   │   │
│  │  │  └─────────────────────────────────────────┘   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                          │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │              监控区 (私有)                        │   │   │
│  │  │  ┌─────────────────────────────────────────┐   │   │
│  │  │  │  Prometheus / Grafana / Loki / Tempo    │   │   │
│  │  │  └─────────────────────────────────────────┘   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 NetworkPolicy 规则
```yaml
# 前端 Pods 网络策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-network-policy
spec:
  podSelector:
    matchLabels:
      app: admin-console
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 3000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: ehs-business
      ports:
        - protocol: TCP
          port: 8080

# 业务服务 Pods 网络策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: business-network-policy
spec:
  podSelector:
    matchLabels:
      app: ehs-business
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: admin-console
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: ehs-ai
      ports:
        - protocol: TCP
          port: 8000
    - to:
        - podSelector:
            matchLabels:
              app: mysql
      ports:
        - protocol: TCP
          port: 3306

# AI 服务 Pods 网络策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-network-policy
spec:
  podSelector:
    matchLabels:
      app: ehs-ai
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: ehs-business
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: milvus
      ports:
        - protocol: TCP
          port: 19530
    - to:
        - podSelector:
            matchLabels:
              app: elasticsearch
      ports:
        - protocol: TCP
          port: 9200
```

---

## 5. 安全架构

### 5.1 安全分层
```
┌─────────────────────────────────────────────────────────────────┐
│                        安全架构                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  网络层安全                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  WAF / DDoS 防护 / TLS 1.3 / NetworkPolicy              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  应用层安全                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  JWT 认证 / RBAC 授权 / XSS 防护 / CSRF 防护 / 输入验证     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  数据层安全                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  加密存储 (AES-256) / 加密传输 (TLS) / 数据脱敏          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  运维层安全                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Bastion Host / 审计日志 / 最小权限 / 密钥轮转          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 认证授权流程
```
用户登录
   │
   ▼
┌─────────────┐
│ 输入凭证     │ 用户名 + 密码
└─────────────┘
   │
   ▼
┌─────────────┐
│ JWT 签发     │ 生成 Access Token + Refresh Token
└─────────────┘
   │
   ▼
┌─────────────┐
│ 请求携带     │ Authorization: Bearer <token>
└─────────────┘
   │
   ▼
┌─────────────┐
│ JWT 验证     │ 验证签名 + 有效期
└─────────────┘
   │
   ▼
┌─────────────┐
│ RBAC 授权    │ 检查用户角色 + 资源权限
└─────────────┘
   │
   ▼
┌─────────────┐
│ 访问资源     │ 允许/拒绝
└─────────────┘
```

### 5.3 gRPC TLS 双向认证
```yaml
# gRPC 服务器配置
grpc:
  server:
    tls:
      enabled: true
      cert-file: /etc/grpc/certs/server.crt
      key-file: /etc/grpc/certs/server.key
      client-ca-file: /etc/grpc/certs/ca.crt
      client-auth: REQUIRE  # 强制客户端证书认证

# gRPC 客户端配置
grpc:
  client:
    tls:
      enabled: true
      ca-file: /etc/grpc/certs/ca.crt
      cert-file: /etc/grpc/certs/client.crt
      key-file: /etc/grpc/certs/client.key
```

---

## 6. 可观测性架构

### 6.1 监控指标体系
| 指标类型 | 指标 | 采集方式 | 告警阈值 |
|----------|------|----------|----------|
| **基础设施** | CPU 使用率 | Prometheus | > 80% |
| | 内存使用率 | Prometheus | > 85% |
| | 磁盘使用率 | Prometheus | > 90% |
| **应用** | 请求 QPS | Prometheus | - |
| | 响应延迟 (P95) | Prometheus | > 800ms |
| | 错误率 | Prometheus | > 1% |
| **AI** | LLM 调用延迟 | LangFuse | > 5s |
| | Token 使用量 | LangFuse | - |
| | RAG 检索延迟 | Prometheus | > 500ms |
| **业务** | 告警响应时间 | 业务指标 | > 8min |
| | 处置完成率 | 业务指标 | < 95% |

### 6.2 Grafana 仪表盘
```
┌─────────────────────────────────────────────────────────────────┐
│                    Grafana 仪表盘布局                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  EHS 系统总览 (Dashboard Overview)                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ 系统健康度   │  │ 今日告警数   │  │ 平均响应时间 │            │
│  │    98.5%    │  │     24      │  │    6.2min   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              请求量趋势 (24h)                            │   │
│  │  ████████                                               │   │
│  │  ████████    ██████                                     │   │
│  │  ██████████████████    ████████                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  服务监控 (Service Metrics)                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Frontend    │  │ Business    │  │ AI Service  │            │
│  │ QPS: 120    │  │ QPS: 85     │  │ QPS: 45     │            │
│  │ P95: 250ms  │  │ P95: 380ms  │  │ P95: 620ms  │            │
│  │ Err: 0.1%   │  │ Err: 0.2%   │  │ Err: 0.5%   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  AI 模型监控 (AI Model Metrics)                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  LLM 调用延迟分布                                         │   │
│  │  ████████████████████                                   │   │
│  │                                                          │   │
│  │  RAG 检索命中率：92%                                      │   │
│  │  风险分级准确率：96%                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  资源使用 (Resource Usage)                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ CPU         │  │ Memory      │  │ GPU         │            │
│  │ ████░░░░░░  │  │ ██████░░░░  │  │ ███░░░░░░░  │            │
│  │ 42%         │  │ 65%         │  │ 28%         │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Prometheus 配置
```yaml
# infra/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'admin-console'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: admin-console
        action: keep

  - job_name: 'ehs-business'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: ehs-business
        action: keep

  - job_name: 'ehs-ai'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: ehs-ai
        action: keep

  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql-exporter:9104']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 6.4 LangFuse 集成
```python
# Python AI 服务 LangFuse 集成
from langfuse import Langfuse
from langfuse.decorators import observe, track

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

@observe()
@track(name="risk_assessment")
async def assess_risk(alert_description: str) -> dict:
    """风险分级，自动追踪到 LangFuse"""
    generation = langfuse.generation(
        name="risk-assessment",
        input=alert_description,
        model="gpt-4"
    )
    
    result = await llm.generate(alert_description)
    
    generation.end(output=result)
    return result
```

---

## 7. CI/CD 架构

### 7.1 GitHub Actions 流水线
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=src --cov-report=xml

  test-node:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm test

  test-java:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - run: mvn test

  build-docker:
    needs: [test-python, test-node, test-java]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ehs-ai ./apps/ehs-ai
      - run: docker build -t ehs-business ./apps/ehs-business
      - run: docker build -t admin-console ./apps/admin-console

  deploy-dev:
    needs: build-docker
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4
      - run: helm upgrade --install ehs-dev ./infra/k8s/ehs-helm -f values-dev.yaml

  deploy-prod:
    needs: build-docker
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - run: helm upgrade --install ehs-prod ./infra/k8s/ehs-helm -f values-prod.yaml
```

### 7.2 发布流程
```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  代码提交 │────▶│   CI    │────▶│  构建   │────▶│  测试   │
│  PR/Merge│     │  检查   │     │  Docker │     │  自动化 │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
   │                                              │
   │                                              ▼
   │                                       ┌─────────┐
   │                                       │ Canary  │
   │                                       │ 金丝雀  │
   │                                       └─────────┘
   │                                              │
   ▼                                              ▼
┌─────────────────────────────────────────────────────────┐
│                      生产部署                            │
│  ┌─────────────┐     ┌─────────────┐                   │
│  │  Blue (v1)  │────▶│  Green (v2) │                   │
│  │  生产流量   │     │  逐步切流    │                   │
│  └─────────────┘     └─────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

---

## 8. 环境配置

### 8.1 环境矩阵
| 环境 | 用途 | 副本数 | 资源限制 | 访问范围 |
|------|------|--------|----------|----------|
| dev | 开发测试 | 1 | 低 | 内部 |
| staging | 预发布验证 | 2 | 中 | 内部 |
| prod | 生产环境 | 3+ | 高 | 公网 |

### 8.2 环境变量规范
```bash
# .env.example (AI 服务)

# LLM 配置
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# 向量数据库
MILVUS_URL=milvus:19530
MILVUS_COLLECTION=ehs_plans

# ES 配置
ES_URL=http://elasticsearch:9200
ES_INDEX=ehs_plans

# Neo4j 配置
NEO4J_URI=neo4j://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# 监控配置
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_HOST=http://langfuse:3000

# 服务配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
```

---

## 9. 审批记录

| 角色 | 姓名 | 日期 | 状态 | 意见 |
|------|------|------|------|------|
| 技术架构师 | - | - | 待审批 | - |
| 运维负责人 | - | - | 待审批 | - |
| 安全负责人 | - | - | 待审批 | - |
| 技术负责人 | - | - | 待审批 | - |

---

**文档维护**: 本文档随技术演进而更新，重大变更需架构评审委员会审批。
