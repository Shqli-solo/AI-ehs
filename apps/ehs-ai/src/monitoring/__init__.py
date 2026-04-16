# apps/ehs-ai/src/monitoring/__init__.py
"""监控模块

提供 Prometheus 指标定义和监控中间件
"""
from .prometheus import (
    # API 请求指标
    http_requests_total,
    http_request_duration_seconds,
    http_request_size_bytes,
    http_response_size_bytes,

    # 业务指标
    alert_reports_total,
    alert_processing_results_total,
    risk_level_distribution,
    plan_search_results_count,

    # Agent 执行指标
    agent_execution_duration_seconds,
    agent_executions_total,
    llm_tokens_total,

    # GraphRAG 检索指标
    rag_search_duration_seconds,
    rag_search_results_count,
    rag_search_hit_rate,

    # 系统健康指标
    active_connections,
    system_running,
    dependency_health,

    # 辅助函数
    register_custom_metrics,
    get_metric_family,
    reset_metrics_for_testing,
)

from .metrics import (
    MetricsMiddleware,
    get_metrics_handler,
    track_alert_report,
    track_agent_execution,
    track_rag_search,
    track_business_operation,
    update_system_health,
    update_dependency_health,
    alert_processed_successfully,
    alert_processing_failed,
)

__all__ = [
    # 指标
    'http_requests_total',
    'http_request_duration_seconds',
    'http_request_size_bytes',
    'http_response_size_bytes',
    'alert_reports_total',
    'alert_processing_results_total',
    'risk_level_distribution',
    'plan_search_results_count',
    'agent_execution_duration_seconds',
    'agent_executions_total',
    'llm_tokens_total',
    'rag_search_duration_seconds',
    'rag_search_results_count',
    'rag_search_hit_rate',
    'active_connections',
    'system_running',
    'dependency_health',

    # 辅助函数
    'register_custom_metrics',
    'get_metric_family',
    'reset_metrics_for_testing',

    # 中间件和装饰器
    'MetricsMiddleware',
    'get_metrics_handler',
    'track_alert_report',
    'track_agent_execution',
    'track_rag_search',
    'track_business_operation',

    # 健康检查
    'update_system_health',
    'update_dependency_health',
    'alert_processed_successfully',
    'alert_processing_failed',
]
