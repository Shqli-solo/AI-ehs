# apps/ehs-ai/src/monitoring/prometheus.py
"""Prometheus 指标定义

定义 EHS 系统的所有监控指标，包括：
- API 请求指标（QPS、延迟、错误率）
- 业务指标（告警数量、风险等级分布）
- 系统指标（Agent 执行时间、RAG 检索性能）
"""
from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Optional


# ============== API 请求指标 ==============

# HTTP 请求计数器
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# HTTP 请求延迟直方图（秒）
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

# HTTP 请求大小直方图（字节）
http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000)
)

# HTTP 响应大小直方图（字节）
http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000)
)


# ============== 业务指标 ==============

# 告警上报计数器
alert_reports_total = Counter(
    'alert_reports_total',
    'Total alert reports received',
    ['alert_type', 'alert_level', 'device_type']
)

# 告警处理结果计数器
alert_processing_results_total = Counter(
    'alert_processing_results_total',
    'Total alert processing results',
    ['result', 'risk_level']
)

# 风险等级分布
risk_level_distribution = Gauge(
    'risk_level_distribution',
    'Distribution of risk levels by count',
    ['risk_level']
)

# 预案检索数量
plan_search_results_count = Gauge(
    'plan_search_results_count',
    'Number of emergency plans returned',
    ['source']
)


# ============== Agent 执行指标 ==============

# Agent 执行时间
agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution time in seconds',
    ['agent_type', 'status'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

# Agent 执行计数器
agent_executions_total = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['agent_type', 'status']
)

# LLM Token 使用量
llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'type']  # type: prompt, completion
)


# ============== GraphRAG 检索指标 ==============

# 检索延迟
rag_search_duration_seconds = Histogram(
    'rag_search_duration_seconds',
    'GraphRAG search latency in seconds',
    ['source', 'status'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# 检索结果数量
rag_search_results_count = Gauge(
    'rag_search_results_count',
    'Number of search results returned',
    ['source']
)

# 检索命中率
rag_search_hit_rate = Gauge(
    'rag_search_hit_rate',
    'Search hit rate by source',
    ['source']
)


# ============== 系统健康指标 ==============

# 活跃连接数
active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# 系统运行状态
system_running = Gauge(
    'system_running',
    'Whether the system is running (1=running, 0=stopped)'
)

# 外部依赖健康状态
dependency_health = Gauge(
    'dependency_health',
    'External dependency health status (1=healthy, 0=unhealthy)',
    ['dependency']
)


# ============== 指标注册辅助函数 ==============

def register_custom_metrics():
    """
    注册自定义指标

    所有指标在导入时自动注册，此函数用于确保注册完成
    """
    # Prometheus Python 客户端在定义指标时自动注册
    # 此函数保留用于未来的扩展
    pass


def get_metric_family(metric_name: str):
    """
    获取指标族

    Args:
        metric_name: 指标名称

    Returns:
        指标族对象或 None
    """
    metrics_map = {
        'http_requests_total': http_requests_total,
        'http_request_duration_seconds': http_request_duration_seconds,
        'alert_reports_total': alert_reports_total,
        'agent_execution_duration_seconds': agent_execution_duration_seconds,
        'rag_search_duration_seconds': rag_search_duration_seconds,
        'active_connections': active_connections,
        'system_running': system_running,
    }
    return metrics_map.get(metric_name)


def reset_metrics_for_testing():
    """
    重置所有指标（仅用于测试）

    注意：此函数仅应在测试环境中使用
    """
    # Counter 不能被重置，只能重新创建
    # 这里提供测试辅助函数
    pass
