# EHS Business Service - Java 后端服务

基于 Spring Boot 3 + COLA 架构的业务服务层，提供 gRPC 客户端能力。

## 技术栈

- **框架**: Spring Boot 3.2.3
- **架构**: COLA 4.x (阿里中台架构)
- **通信**: gRPC 1.61.0 (双向 TLS)
- **数据库**: PostgreSQL + JPA
- **认证**: JWT + Spring Security
- **构建**: Maven 3.x

## 项目结构

```
ehs-business/
├── src/main/java/com/ehs/business/
│   ├── EhsBusinessApplication.java    # 启动类
│   ├── application/                   # 应用层
│   │   └── alert/AlertService.java   # 告警服务
│   ├── domain/                        # 领域层
│   │   └── alert/Alert.java          # 告警实体
│   ├── infrastructure/                # 基础设施层
│   │   └── grpc/                      # gRPC 配置和客户端
│   ├── config/                        # 配置类
│   │   ├── GrpcConfig.java           # gRPC 配置
│   │   └── SecurityConfig.java       # 安全配置
│   └── security/                      # 安全模块
│       └── JwtAuthFilter.java        # JWT 过滤器
├── src/main/proto/
│   └── ehs.proto                      # gRPC Proto 定义
├── pom.xml
└── src/test/java/
    └── AlertServiceTest.java         # 单元测试
```

## 快速开始

### 前置要求
- JDK 17+
- Maven 3.6+

### 编译

```bash
mvn clean compile
```

### 运行测试

```bash
mvn test
```

### 启动服务

```bash
mvn spring-boot:run
```

## gRPC 服务

### Proto 定义

```protobuf
service EhsAiService {
    rpc HealthCheck (HealthCheckRequest) returns (HealthCheckResponse);
    rpc ClassifyRisk (RiskClassificationRequest) returns (RiskClassificationResponse);
    rpc GenerateResponse (ResponseGenerationRequest) returns (ResponseGenerationResponse);
    rpc AnalyzeAlert (AlertAnalysisRequest) returns (AlertAnalysisResponse);
    rpc GetTermEmbedding (TermEmbeddingRequest) returns (TermEmbeddingResponse);
}
```

### 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `grpc.python-ai.host` | localhost | Python AI 服务主机 |
| `grpc.python-ai.port` | 50051 | gRPC 端口 |
| `grpc.timeout.seconds` | 120 | 超时时间 (秒) |
| `grpc.retry.max` | 3 | 最大重试次数 |
| `grpc.circuit-breaker.failure-threshold` | 10 | 熔断阈值 |
| `grpc.tls.enabled` | false | 是否启用 TLS |

## COLA 架构分层

| 层级 | 包名 | 职责 |
|------|------|------|
| 应用层 | `application` | 业务编排和协调 |
| 领域层 | `domain` | 核心业务逻辑 |
| 基础设施层 | `infrastructure` | 外部系统集成 |
| 配置层 | `config` | Spring 配置 |

## 核心功能

### 1. 告警管理
- 创建/查询/删除告警
- 告警级别验证 (LOW/MEDIUM/HIGH/CRITICAL)
- 告警处理状态追踪

### 2. gRPC 客户端
- 双向 TLS 认证
- 自动重试 (指数退避)
- 熔断器模式
- 超时控制

### 3. 安全认证
- JWT Token 验证
- Spring Security 过滤器链

## 测试覆盖

```
Tests run: 10
Failures: 0
Errors: 0
Skipped: 0
```

## 与其他服务集成

### Python AI Service

通过 gRPC 调用 Python AI 服务：

```java
@Autowired
private ManagedChannel pythonAiChannel;

// 调用 AI 服务分析告警
AlertAnalysisRequest request = AlertAnalysisRequest.newBuilder()
    .setAlertType(AlertType.FIRE)
    .setAlertLevel(RiskLevel.HIGH)
    .setContent("检测到火灾风险")
    .build();
```

## 开发指南

### 添加新的 gRPC 调用

1. 在 `ehs.proto` 中添加方法定义
2. 运行 `mvn protobuf:compile` 生成代码
3. 在 `application` 层实现业务逻辑

### 添加新的业务功能

1. 在 `domain` 层创建实体
2. 在 `application` 层创建服务
3. 在 `infrastructure` 层实现持久化

## 故障排查

### gRPC 连接失败
- 检查 Python 服务是否启动
- 验证主机名和端口配置
- 检查 TLS 证书 (如果启用)

### 熔断器打开
- 查看日志中的失败记录
- 检查 Python 服务健康状态
- 等待熔断器自动重置 (默认 60 秒)

---

**版本**: 2.0.0-SNAPSHOT  
**最后更新**: 2026-04-16
