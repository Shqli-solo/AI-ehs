# EHS Monorepo

> EHS 智能安保决策中台 - Monorepo 架构

## 目录结构

```
mianshi/
├── apps/
│   ├── admin-console/     # Next.js 14 + TypeScript + Tailwind + Shadcn 前端
│   ├── ehs-business/      # Java Spring Boot + COLA + gRPC 业务服务
│   └── ehs-ai/            # Python FastAPI + LangGraph + PyTorch AI 服务
├── scripts/
│   ├── setup.sh           # 开发环境设置脚本
│   └── run-tests.sh       # 测试运行脚本
├── package.json           # Root package.json (pnpm workspace)
├── pnpm-workspace.yaml    # pnpm workspace 配置
├── tsconfig.json          # TypeScript 基础配置
├── Makefile               # Make 命令入口
└── .gitignore             # Git ignore 规则
```

## 快速开始

### 前置要求

- Node.js 18+
- pnpm 9.0+
- Python 3.11+
- Poetry 1.7+
- Java 17+ (可选，用于 Java 服务)
- Maven 3.8+ (可选，用于 Java 服务)

### 安装

```bash
# 克隆项目
git clone https://github.com/Shqli-solo/AI-ehs.git
cd mianshi

# 运行设置脚本
./scripts/setup.sh

# 或者使用 make
make install
```

### 开发

```bash
# 启动前端开发服务器
make dev

# 启动 Python AI 服务
make dev:backend

# 启动 Java 业务服务
make dev:java

# 启动所有服务
make dev:all
```

### 测试

```bash
# 运行所有测试
make test

# 运行前端测试
make test:frontend

# 运行 Python 测试
make test:python

# 运行 Java 测试
make test:java

# 运行测试覆盖率
make test:coverage
```

### 构建

```bash
# 构建所有服务
make build

# 构建前端
make build:frontend

# 构建 Python 服务
make build:python

# 构建 Java 服务
make build:java
```

## 技术栈

### 前端 (@ehs/admin-console)

- **框架**: Next.js 14
- **语言**: TypeScript 5
- **样式**: TailwindCSS + Shadcn UI
- **测试**: Vitest + Testing Library

### Java 服务 (@ehs/ehs-business)

- **框架**: Spring Boot 3.2
- **架构**: COLA 4.4 (阿里开放平台架构)
- **通信**: gRPC 1.62
- **数据库**: PostgreSQL + JPA

### Python AI 服务 (@ehs/ehs-ai)

- **框架**: FastAPI 0.110
- **AI 编排**: LangGraph + LangChain
- **向量数据库**: Milvus 2.4
- **检索**: Elasticsearch 8.12
- **重排序**: BGE-Reranker (Sentence Transformers)
- **深度学习**: PyTorch 2.2

## 架构说明

本 Monorepo 项目采用微服务架构，包含三个主要子项目：

1. **前端管理控制台**: 提供用户界面，包括告警管理、预案检索、数据可视化等功能
2. **Java 业务服务**: 核心业务逻辑处理，提供 RESTful API 和 gRPC 接口
3. **Python AI 服务**: AI 推理和检索引擎，包括 GraphRAG、Multi-Agent 工作流

## 配置说明

### pnpm Workspace

```yaml
packages:
  - 'apps/*'
```

### 环境变量

前端环境变量位于 `apps/admin-console/.env.local`
Python AI 服务环境变量位于 `apps/ehs-ai/.env`

## 开发规范

- 使用 pnpm 作为包管理器
- 使用 Poetry 管理 Python 依赖
- 使用 Maven 管理 Java 依赖
- 提交前运行 `make test` 确保测试通过
- 使用 `make lint` 和 `make format` 保持代码风格一致

## License

MIT
