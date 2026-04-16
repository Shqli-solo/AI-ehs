# 监控集成指南

## 概述

EHS 系统使用 Prometheus + Grafana 进行监控，包括：
- API 请求指标（QPS、延迟、错误率）
- 业务指标（告警数量、风险等级分布）
- Agent 执行指标
- GraphRAG 检索性能指标
- 系统健康指标

## 文件结构

```
apps/ehs-ai/src/monitoring/
├── __init__.py          # 模块导出
├── prometheus.py        # Prometheus 指标定义
└── metrics.py           # 监控中间件和装饰器

infra/
├── prometheus.yml       # Prometheus 配置
└── grafana/
    └── dashboards/
        └── ehs-overview.json  # Grafana Dashboard
```

## 指标定义

### API 请求指标

| 指标名称 | 类型 | 描述 | 标签 |
|---------|------|------|------|
| `http_requests_total` | Counter | HTTP 请求总数 | method, endpoint, status |
| `http_request_duration_seconds` | Histogram | HTTP 请求延迟 | method, endpoint |
| `http_request_size_bytes` | Histogram | HTTP 请求大小 | method, endpoint |
| `http_response_size_bytes` | Histogram | HTTP 响应大小 | method, endpoint |

### 业务指标

| 指标名称 | 类型 | 描述 | 标签 |
|---------|------|------|------|
| `alert_reports_total` | Counter | 告警上报总数 | alert_type, alert_level, device_type |
| `alert_processing_results_total` | Counter | 告警处理结果 | result, risk_level |
| `risk_level_distribution` | Gauge | 风险等级分布 | risk_level |

### Agent 执行指标

| 指标名称 | 类型 | 描述 | 标签 |
|---------|------|------|------|
| `agent_execution_duration_seconds` | Histogram | Agent 执行时间 | agent_type, status |
| `agent_executions_total` | Counter | Agent 执行总数 | agent_type, status |
| `llm_tokens_total` | Counter | LLM Token 使用量 | model, type |

### GraphRAG 检索指标

| 指标名称 | 类型 | 描述 | 标签 |
|---------|------|------|------|
| `rag_search_duration_seconds` | Histogram | RAG 检索延迟 | source, status |
| `rag_search_results_count` | Gauge | 检索结果数量 | source |
| `rag_search_hit_rate` | Gauge | 检索命中率 | source |

### 系统健康指标

| 指标名称 | 类型 | 描述 | 标签 |
|---------|------|------|------|
| `active_connections` | Gauge | 活跃连接数 | - |
| `system_running` | Gauge | 系统运行状态 | - |
| `dependency_health` | Gauge | 外部依赖健康状态 | dependency |

## 使用方法

### 1. 添加中间件到 FastAPI

```python
from fastapi import FastAPI
from src.monitoring.metrics import MetricsMiddleware, get_metrics_handler

app = FastAPI()

# 添加监控中间件
app.add_middleware(MetricsMiddleware)

# 添加 metrics 端点
@app.get("/metrics")
def metrics():
    return get_metrics_handler()()
```

### 2. 使用装饰器记录业务指标

```python
from src.monitoring.metrics import track_alert_report, track_agent_execution

@track_alert_report(alert_type="fire", alert_level=4, device_type="smoke_detector")
async def report_alert(request: AlertReportRequest):
    ...

@track_agent_execution(agent_type="risk_agent")
def assess_risk(alert_message: str):
    ...
```

### 3. 更新依赖健康状态

```python
from src.monitoring.metrics import update_dependency_health, update_system_health

# 启动时
update_system_health()
update_dependency_health('elasticsearch', True)
update_dependency_health('milvus', True)

# 健康检查失败时
update_dependency_health('llm', False)
```

### 4. 使用上下文管理器

```python
from src.monitoring.metrics import track_business_operation

with track_business_operation("plan_generation", {"risk_level": "high"}):
    generate_plans()
```

## Prometheus 配置

Prometheus 配置已定义在 `infra/prometheus.yml`，会自动抓取以下服务：

- `ehs-ai-service:9092` - Python AI 服务
- `ehs-business-service:8080` - Java 业务服务
- `elasticsearch:9200` - Elasticsearch
- `milvus:9091` - Milvus
- `minio:9000` - MinIO

## Grafana Dashboard

导入 `infra/grafana/dashboards/ehs-overview.json` 到 Grafana，包含：

- 系统概览（Stat 面板）
- QPS 趋势图
- API 延迟（P50/P95）
- 告警等级分布
- 告警类型分布
- Agent 执行延迟
- RAG 检索延迟
- 外部依赖健康状态

## 运行测试

```bash
cd apps/ehs-ai
python -m pytest tests/test_monitoring.py -v
```

## 访问 Metrics 端点

启动服务后，访问 `http://localhost:8000/metrics` 查看 Prometheus 格式指标。

## 告警规则（待添加）

可在 Prometheus 中添加告警规则：

```yaml
groups:
  - name: ehs_alerts
    rules:
      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        annotations:
          summary: "EHS 系统错误率超过 5%"
```
