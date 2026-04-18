# apps/ehs-ai/src/monitoring/metrics.py
"""监控指标中间件

FastAPI 中间件，用于自动收集和暴露监控指标：
- 自动记录 HTTP 请求指标
- 业务指标埋点
- Prometheus metrics 端点
"""
import time
import os
from typing import Callable, Awaitable
from contextlib import contextmanager

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry, multiprocess

from .prometheus import (
    http_requests_total,
    http_request_duration_seconds,
    http_request_size_bytes,
    http_response_size_bytes,
    alert_reports_total,
    alert_processing_results_total,
    agent_execution_duration_seconds,
    agent_executions_total,
    rag_search_duration_seconds,
    active_connections,
    system_running,
    dependency_health,
)


def get_metrics_handler():
    """
    获取 Prometheus metrics 端点处理器

    用于暴露在 /metrics 端点
    """
    def metrics_endpoint():
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi.responses import Response

        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    return metrics_endpoint


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Prometheus 监控指标中间件

    自动记录：
    - HTTP 请求总数
    - HTTP 请求延迟
    - HTTP 请求/响应大小
    - 活跃连接数
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # 记录活跃连接数 +1
        active_connections.inc()

        # 记录请求大小
        request_size = int(request.headers.get('content-length', 0))

        # 记录开始时间
        start_time = time.perf_counter()

        try:
            # 执行请求
            response = await call_next(request)

            # 记录结束时间
            duration = time.perf_counter() - start_time

            # 记录响应大小
            response_size = int(response.headers.get('content-length', 0))

            # 记录指标
            self._record_metrics(
                request=request,
                response=response,
                duration=duration,
                request_size=request_size,
                response_size=response_size
            )

            return response

        except Exception as e:
            # 记录异常指标
            http_requests_total.labels(
                method=request.method,
                endpoint=self._get_endpoint(request),
                status='500'
            ).inc()

            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=self._get_endpoint(request)
            ).observe(time.perf_counter() - start_time)

            raise

        finally:
            # 记录活跃连接数 -1
            active_connections.dec()

    def _record_metrics(
        self,
        request: Request,
        response: Response,
        duration: float,
        request_size: int,
        response_size: int
    ):
        """记录指标"""
        endpoint = self._get_endpoint(request)
        status = str(response.status_code)

        # 请求计数器
        http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status=status
        ).inc()

        # 请求延迟
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)

        # 请求大小
        if request_size > 0:
            http_request_size_bytes.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(request_size)

        # 响应大小
        if response_size > 0:
            http_response_size_bytes.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(response_size)

    def _get_endpoint(self, request: Request) -> str:
        """
        获取标准化的端点路径

        移除动态参数，如 /api/alert/123 -> /api/alert/{id}
        """
        path = request.url.path
        # 简单处理：将数字路径替换为 {id}
        import re
        # 确保 path 是字符串
        if not isinstance(path, str):
            path = str(path)
        normalized = re.sub(r'/\d+', '/{id}', path)
        return normalized


# ============== 业务指标埋点装饰器 ==============

def track_alert_report(alert_type: str, alert_level: int, device_type: str):
    """
    装饰器：跟踪告警上报

    使用示例：
    @track_alert_report(alert_type="fire", alert_level=4, device_type="smoke_detector")
    async def report_alert(request):
        ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                alert_reports_total.labels(
                    alert_type=alert_type,
                    alert_level=str(alert_level),
                    device_type=device_type
                ).inc()
                return result
            except Exception as e:
                alert_processing_results_total.labels(
                    result='error',
                    risk_level='unknown'
                ).inc()
                raise
        return wrapper
    return decorator


def track_agent_execution(agent_type: str):
    """
    装饰器：跟踪 Agent 执行

    使用示例：
    @track_agent_execution(agent_type="risk_agent")
    def assess_risk(self, alert_message):
        ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            status = 'success'
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.perf_counter() - start_time
                agent_execution_duration_seconds.labels(
                    agent_type=agent_type,
                    status=status
                ).observe(duration)
                agent_executions_total.labels(
                    agent_type=agent_type,
                    status=status
                ).inc()
        return wrapper
    return decorator


def track_rag_search(source: str):
    """
    装饰器：跟踪 RAG 检索

    使用示例：
    @track_rag_search(source="elasticsearch")
    def search(self, query):
        ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            status = 'success'
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.perf_counter() - start_time
                rag_search_duration_seconds.labels(
                    source=source,
                    status=status
                ).observe(duration)
        return wrapper
    return decorator


# ============== 上下文管理器 ==============

@contextmanager
def track_business_operation(operation_type: str, labels: dict = None):
    """
    上下文管理器：跟踪业务操作

    使用示例：
    with track_business_operation("plan_generation", {"risk_level": "high"}):
        generate_plans()
    """
    start_time = time.perf_counter()
    labels = labels or {}

    try:
        yield
        agent_executions_total.labels(
            agent_type=operation_type,
            status='success',
            **labels
        ).inc()
    except Exception as e:
        agent_executions_total.labels(
            agent_type=operation_type,
            status='error',
            **labels
        ).inc()
        raise
    finally:
        duration = time.perf_counter() - start_time
        agent_execution_duration_seconds.labels(
            agent_type=operation_type,
            status='success' if 'e' not in dir() else 'error',
            **labels
        ).observe(duration)


# ============== 系统健康检查 ==============

def update_system_health():
    """更新系统健康状态"""
    system_running.set(1)


def update_dependency_health(dependency: str, is_healthy: bool):
    """
    更新外部依赖健康状态

    Args:
        dependency: 依赖名称，如 'elasticsearch', 'milvus', 'llm'
        is_healthy: 是否健康
    """
    if is_healthy:
        dependency_health.labels(dependency=dependency).set(1)
    else:
        dependency_health.labels(dependency=dependency).set(0)


def alert_processed_successfully(risk_level: str):
    """记录告警处理成功"""
    alert_processing_results_total.labels(
        result='success',
        risk_level=risk_level
    ).inc()


def alert_processing_failed(risk_level: str = 'unknown'):
    """记录告警处理失败"""
    alert_processing_results_total.labels(
        result='error',
        risk_level=risk_level
    ).inc()
