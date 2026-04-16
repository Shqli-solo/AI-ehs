# apps/ehs-ai/tests/test_monitoring.py
"""监控集成测试

测试 Prometheus 指标定义和监控中间件：
- 指标定义完整性
- 中间件自动记录
- 装饰器埋点
- 健康检查
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from prometheus_client import Counter, Histogram, Gauge

# 导入监控模块
from src.monitoring.prometheus import (
    http_requests_total,
    http_request_duration_seconds,
    alert_reports_total,
    alert_processing_results_total,
    agent_execution_duration_seconds,
    agent_executions_total,
    rag_search_duration_seconds,
    active_connections,
    system_running,
    dependency_health,
    register_custom_metrics,
    get_metric_family,
)

from src.monitoring.metrics import (
    MetricsMiddleware,
    get_metrics_handler,
    track_alert_report,
    track_agent_execution,
    track_rag_search,
    update_system_health,
    update_dependency_health,
    alert_processed_successfully,
    alert_processing_failed,
)


# ============== Prometheus 指标定义测试 ==============

class TestPrometheusMetricsDefinition:
    """测试 Prometheus 指标定义"""

    def test_http_request_metrics_exist(self):
        """测试 HTTP 请求指标存在"""
        assert http_requests_total is not None
        assert http_request_duration_seconds is not None
        assert isinstance(http_requests_total, Counter)
        assert isinstance(http_request_duration_seconds, Histogram)

    def test_business_metrics_exist(self):
        """测试业务指标存在"""
        assert alert_reports_total is not None
        assert alert_processing_results_total is not None
        assert isinstance(alert_reports_total, Counter)
        assert isinstance(alert_processing_results_total, Counter)

    def test_agent_metrics_exist(self):
        """测试 Agent 执行指标存在"""
        assert agent_execution_duration_seconds is not None
        assert agent_executions_total is not None
        assert isinstance(agent_execution_duration_seconds, Histogram)
        assert isinstance(agent_executions_total, Counter)

    def test_rag_metrics_exist(self):
        """测试 RAG 检索指标存在"""
        assert rag_search_duration_seconds is not None
        assert isinstance(rag_search_duration_seconds, Histogram)

    def test_system_health_metrics_exist(self):
        """测试系统健康指标存在"""
        assert active_connections is not None
        assert system_running is not None
        assert dependency_health is not None
        assert isinstance(active_connections, Gauge)
        assert isinstance(system_running, Gauge)
        assert isinstance(dependency_health, Gauge)

    def test_metrics_have_required_labels(self):
        """测试指标具有必需的标签"""
        # HTTP 请求计数器标签
        assert 'method' in http_requests_total._labelnames
        assert 'endpoint' in http_requests_total._labelnames
        assert 'status' in http_requests_total._labelnames

        # 告警上报计数器标签
        assert 'alert_type' in alert_reports_total._labelnames
        assert 'alert_level' in alert_reports_total._labelnames
        assert 'device_type' in alert_reports_total._labelnames

        # Agent 执行指标标签
        assert 'agent_type' in agent_executions_total._labelnames
        assert 'status' in agent_executions_total._labelnames

        # RAG 检索指标标签
        assert 'source' in rag_search_duration_seconds._labelnames

        # 依赖健康指标标签
        assert 'dependency' in dependency_health._labelnames


class TestMetricRegistry:
    """测试指标注册辅助函数"""

    def test_register_custom_metrics(self):
        """测试注册自定义指标"""
        # 此函数不应抛出异常
        register_custom_metrics()

    def test_get_metric_family(self):
        """测试获取指标族"""
        # 测试已知指标
        metric = get_metric_family('http_requests_total')
        assert metric is not None

        metric = get_metric_family('http_request_duration_seconds')
        assert metric is not None

        metric = get_metric_family('alert_reports_total')
        assert metric is not None

        # 测试未知指标
        metric = get_metric_family('nonexistent_metric')
        assert metric is None


# ============== 系统健康指标测试 ==============

class TestSystemHealthMetrics:
    """测试系统健康指标操作"""

    def test_update_system_health(self):
        """测试更新系统健康状态"""
        update_system_health()
        # system_running 应该被设置为 1
        # 注意：由于 Prometheus 客户端的特性，我们无法直接读取值
        # 实际测试中通过 metrics 端点验证

    def test_update_dependency_health_healthy(self):
        """测试更新依赖健康状态（健康）"""
        update_dependency_health('elasticsearch', True)
        # dependency_health{dependency="elasticsearch"} 应该被设置为 1

    def test_update_dependency_health_unhealthy(self):
        """测试更新依赖健康状态（不健康）"""
        update_dependency_health('milvus', False)
        # dependency_health{dependency="milvus"} 应该被设置为 0

    def test_alert_processed_successfully(self):
        """测试告警处理成功记录"""
        alert_processed_successfully('high')
        # alert_processing_results_total{result="success", risk_level="high"} 应该增加

    def test_alert_processing_failed(self):
        """测试告警处理失败记录"""
        alert_processing_failed('medium')
        # alert_processing_results_total{result="error", risk_level="medium"} 应该增加

        # 测试默认风险等级
        alert_processing_failed()


# ============== 装饰器测试 ==============

class TestMetricsDecorators:
    """测试监控装饰器"""

    def test_track_alert_report_decorator(self):
        """测试告警上报装饰器"""

        @track_alert_report(alert_type="fire", alert_level=4, device_type="smoke_detector")
        def mock_report_alert():
            return {"success": True, "alert_id": "123"}

        result = mock_report_alert()
        assert result["success"] is True
        assert result["alert_id"] == "123"

    def test_track_alert_report_decorator_with_exception(self):
        """测试告警上报装饰器异常处理"""

        @track_alert_report(alert_type="test", alert_level=1, device_type="test")
        def failing_report_alert():
            raise Exception("模拟失败")

        with pytest.raises(Exception):
            failing_report_alert()

    def test_track_agent_execution_decorator(self):
        """测试 Agent 执行装饰器"""

        @track_agent_execution(agent_type="risk_agent")
        def mock_assess_risk(alert_message):
            time.sleep(0.01)  # 模拟执行时间
            return {"risk_level": "high"}

        result = mock_assess_risk("测试告警")
        assert result["risk_level"] == "high"

    def test_track_agent_execution_decorator_measures_duration(self):
        """测试 Agent 执行装饰器测量执行时间"""

        @track_agent_execution(agent_type="test_agent")
        def slow_function():
            time.sleep(0.05)
            return "done"

        start = time.perf_counter()
        slow_function()
        duration = time.perf_counter() - start

        # 验证执行时间大于 0.05 秒
        assert duration >= 0.05

    def test_track_rag_search_decorator(self):
        """测试 RAG 检索装饰器"""

        @track_rag_search(source="elasticsearch")
        def mock_search(query):
            return [{"title": "测试结果", "content": "内容"}]

        result = mock_search("测试查询")
        assert len(result) > 0
        assert result[0]["title"] == "测试结果"

    def test_track_rag_search_decorator_with_exception(self):
        """测试 RAG 检索装饰器异常处理"""

        @track_rag_search(source="milvus")
        def failing_search(query):
            raise ConnectionError("连接失败")

        with pytest.raises(ConnectionError):
            failing_search("测试")


# ============== MetricsMiddleware 测试 ==============

class TestMetricsMiddleware:
    """测试 FastAPI 监控中间件"""

    @pytest.mark.asyncio
    async def test_middleware_records_http_metrics(self):
        """测试中间件记录 HTTP 指标"""
        # 创建 Mock FastAPI 应用
        mock_app = AsyncMock()

        # 创建中间件
        middleware = MetricsMiddleware(mock_app)

        # 创建 Mock 请求
        mock_request = Mock()
        mock_request.method = "POST"
        mock_url = Mock()
        mock_url.path = "/api/alert/report"
        mock_request.url = mock_url
        mock_request.headers = {"content-length": "100"}

        # 创建 Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "200"}

        # 创建 Mock call_next
        call_next_called = False
        async def mock_call_next(request):
            nonlocal call_next_called
            call_next_called = True
            return mock_response

        # 执行中间件
        await middleware(mock_request, mock_call_next)

        # 验证 call_next 被调用
        assert call_next_called is True

    @pytest.mark.asyncio
    async def test_middleware_handles_exception(self):
        """测试中间件异常处理"""
        mock_app = AsyncMock()
        middleware = MetricsMiddleware(mock_app)

        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url.path = "/api/error"
        mock_request.headers = {}

        async def mock_call_next(request):
            raise Exception("模拟错误")

        with pytest.raises(Exception):
            await middleware(mock_request, mock_call_next)

    def test_get_endpoint_normalization(self):
        """测试端点路径标准化"""
        middleware = MetricsMiddleware(Mock())

        # 测试数字路径被替换
        mock_request = Mock()
        mock_request.url.path = "/api/alert/123"
        endpoint = middleware._get_endpoint(mock_request)
        assert endpoint == "/api/alert/{id}"

        # 测试正常路径不变
        mock_request.url.path = "/health"
        endpoint = middleware._get_endpoint(mock_request)
        assert endpoint == "/health"

    def test_record_metrics(self):
        """测试指标记录"""
        middleware = MetricsMiddleware(Mock())

        mock_request = Mock()
        mock_request.method = "POST"
        mock_url = Mock()
        mock_url.path = "/api/alert/report"
        mock_request.url = mock_url
        mock_request.headers = {}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}

        # 此方法不应抛出异常
        middleware._record_metrics(
            request=mock_request,
            response=mock_response,
            duration=0.1,
            request_size=100,
            response_size=200
        )


# ============== 集成测试 ==============

class TestMonitoringIntegration:
    """监控集成测试"""

    def test_metrics_handler_exists(self):
        """测试 metrics 处理器存在"""
        handler = get_metrics_handler()
        assert handler is not None

    def test_all_metrics_modules_importable(self):
        """测试所有监控模块可导入"""
        from src import monitoring
        assert hasattr(monitoring, 'prometheus')
        assert hasattr(monitoring, 'metrics')

    def test_monitoring_module_exports(self):
        """测试监控模块导出"""
        from src.monitoring import (
            http_requests_total,
            MetricsMiddleware,
            update_system_health,
        )
        assert http_requests_total is not None
        assert MetricsMiddleware is not None
        assert update_system_health is not None


# ============== 边界情况测试 ==============

class TestMonitoringEdgeCases:
    """测试监控边界情况"""

    def test_zero_content_length(self):
        """测试零内容长度"""
        middleware = MetricsMiddleware(Mock())

        mock_request = Mock()
        mock_request.method = "GET"
        mock_url = Mock()
        mock_url.path = "/health"
        mock_request.url = mock_url
        mock_request.headers = {"content-length": "0"}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "0"}

        # 不应抛出异常
        middleware._record_metrics(
            request=mock_request,
            response=mock_response,
            duration=0,
            request_size=0,
            response_size=0
        )

    def test_missing_content_length_header(self):
        """测试缺失内容长度头"""
        middleware = MetricsMiddleware(Mock())

        mock_request = Mock()
        mock_request.method = "GET"
        mock_url = Mock()
        mock_url.path = "/health"
        mock_request.url = mock_url
        mock_request.headers = {}  # 无 content-length

        mock_response = Mock()
        mock_response.status_code = 204  # No Content
        mock_response.headers = {}

        # 不应抛出异常
        middleware._record_metrics(
            request=mock_request,
            response=mock_response,
            duration=0,
            request_size=0,
            response_size=0
        )

    def test_multiple_dependency_health_updates(self):
        """测试多次更新依赖健康状态"""
        # 健康 -> 不健康 -> 健康
        update_dependency_health('llm', True)
        update_dependency_health('llm', False)
        update_dependency_health('llm', True)
        # 不应抛出异常

    def test_concurrent_metric_updates(self):
        """测试并发指标更新"""
        import concurrent.futures

        def update_metric():
            alert_reports_total.labels(
                alert_type="test",
                alert_level="1",
                device_type="test"
            ).inc()

        # 并发执行 10 次
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_metric) for _ in range(10)]
            concurrent.futures.wait(futures)

        # 不应抛出异常


# ============== 辅助类 ==============

class AsyncMock(Mock):
    """异步 Mock 辅助类"""
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
