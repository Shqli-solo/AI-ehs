# EHS 智能安保决策中台 - 5 分钟快速入门

> **目标**: 5 分钟内在本地启动完整的 EHS 系统（包含所有依赖服务）  
> **适用**: 开发环境快速体验  
> **前置**: Docker Desktop 已安装并运行

---

## 步骤 1: 克隆项目 (30 秒)

```bash
git clone https://github.com/Shqli-solo/AI-ehs.git
cd AI-ehs
```

---

## 步骤 2: 一键启动所有服务 (30 秒)

```bash
# 使用 Docker Compose 启动所有服务（前端 + 后端 AI + 后端业务 + 基础设施）
docker-compose -f infra/docker-compose.yml up -d
```

**启动的服务列表**:
| 服务 | 端口 | 说明 |
|------|------|------|
| admin-console | http://localhost:3000 | 前端管理控制台 |
| ehs-ai-service | http://localhost:8000 | Python AI 服务 (FastAPI) |
| ehs-business-service | http://localhost:8080 | Java 业务服务 (Spring Boot) |
| elasticsearch | http://localhost:9200 | 文档检索引擎 |
| milvus | http://localhost:19530 | 向量数据库 |
| minio | http://localhost:9000 | 对象存储 |
| postgres | localhost:5432 | PostgreSQL 数据库 |
| prometheus | http://localhost:9090 | 监控指标 |
| grafana | http://localhost:3001 | 监控仪表盘 |

---

## 步骤 3: 验证服务运行状态 (2 分钟)

### 3.1 检查所有容器状态

```bash
docker-compose -f infra/docker-compose.yml ps
```

**预期输出**: 所有服务状态应为 `healthy` 或 `Up`

### 3.2 验证 AI 服务健康检查

```bash
curl http://localhost:8000/health
```

**预期响应**:
```json
{"status": "healthy", "service": "ehs-ai"}
```

### 3.3 验证业务服务健康检查

```bash
curl http://localhost:8080/actuator/health
```

**预期响应**:
```json
{"status": "UP"}
```

### 3.4 验证前端页面

打开浏览器访问：http://localhost:3000

**预期**: 看到 EHS 智能安保决策中台 Dashboard 页面

### 3.5 验证 Elasticsearch

```bash
curl http://localhost:9200/_cluster/health
```

**预期响应**:
```json
{"status": "green", "number_of_nodes": 1, ...}
```

### 3.6 验证 Milvus

```bash
curl http://localhost:19530/api/v1/health
```

**预期**: 返回健康状态信息

---

## 步骤 4: 测试核心功能 (2 分钟)

### 4.1 测试告警上报接口

```bash
curl -X POST http://localhost:8000/api/alert/report \
  -H "Content-Type: application/json" \
  -d '{
    "title": "车间烟雾报警",
    "description": "一号车间检测到异常烟雾",
    "location": "一号车间",
    "sensor_id": "SMOKE-001"
  }'
```

**预期响应**: 返回告警 ID 和处理状态

### 4.2 测试预案检索接口

```bash
curl -X POST http://localhost:8000/api/plan/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "气体泄漏应急处置",
    "risk_level": "high"
  }'
```

**预期响应**: 返回相关预案列表

### 4.3 查看服务日志

```bash
# 查看所有服务日志
docker-compose -f infra/docker-compose.yml logs -f

# 查看特定服务日志
docker-compose -f infra/docker-compose.yml logs -f ehs-ai-service
```

---

## 步骤 5: 访问监控仪表盘 (30 秒)

### 5.1 访问 Prometheus

打开浏览器：http://localhost:9090

**用途**: 查看系统指标、API 响应时间、请求量等

### 5.2 访问 Grafana

打开浏览器：http://localhost:3001

- 用户名：`admin`
- 密码：`admin`

**用途**: 查看可视化监控仪表盘

---

## 常见问题排查

### 问题 1: 容器启动失败

```bash
# 查看详细日志
docker-compose -f infra/docker-compose.yml logs <服务名>

# 重启特定服务
docker-compose -f infra/docker-compose.yml restart <服务名>
```

### 问题 2: 端口被占用

修改 `infra/docker-compose.yml` 中的端口映射，例如：
```yaml
ports:
  - "3001:3000"  # 将前端改为 3001 端口
```

### 问题 3: 内存不足

EHS 系统需要约 4GB 内存。如果内存不足：
1. 关闭不必要的服务
2. 调整 Elasticsearch JVM 内存（修改 ES_JAVA_OPTS）

### 问题 4: 服务健康检查失败

等待 30-60 秒，某些服务（如 Milvus）启动较慢。

---

## 清理与停止

```bash
# 停止所有服务（保留数据卷）
docker-compose -f infra/docker-compose.yml down

# 停止并删除数据卷（彻底清理）
docker-compose -f infra/docker-compose.yml down -v
```

---

## 下一步

- 📖 查看 [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) 了解项目架构
- 🔧 查看 [测试指南.md](../测试指南.md) 运行测试
- 📝 查看 API 文档：http://localhost:8000/docs

---

**恭喜！你已成功启动 EHS 智能安保决策中台！** 🎉
