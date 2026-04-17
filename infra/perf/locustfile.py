"""EHS 性能测试 - Locust

模拟真实用户行为，验证系统性能指标：
- P99 响应时间 < 800ms
- 吞吐量 > 100 req/s
- 错误率 < 1%

使用方式:
    locust -f locustfile.py --host=http://localhost:8000
    locust -f locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 5m
"""
from locust import HttpUser, task, between, events
import json
import logging

logger = logging.getLogger(__name__)


class AlertUser(HttpUser):
    """模拟告警上报用户 - 高频操作"""
    wait_time = between(1, 3)

    @task(3)
    def report_alert(self):
        """告警上报 - 核心接口"""
        self.client.post(
            "/api/alert/report",
            json={
                "device_id": "DEV-001",
                "device_type": "smoke_detector",
                "alert_type": "fire",
                "alert_content": "A栋3楼烟感探测器检测到烟雾浓度超标，请立即处理",
                "location": "A栋3楼",
                "alert_level": 3,
            },
            name="/api/alert/report"
        )

    @task(5)
    def search_plans(self):
        """预案检索 - 最高频查询"""
        self.client.post(
            "/api/plan/search",
            json={
                "query": "火灾应急预案",
                "event_type": "fire",
                "top_k": 5,
            },
            name="/api/plan/search"
        )

    @task(2)
    def get_alerts(self):
        """获取告警列表 - 带分页"""
        self.client.get(
            "/api/alert/list?status=pending&page=1&page_size=10",
            name="/api/alert/list"
        )

    @task(1)
    def health_check(self):
        """健康检查 - 心跳探测"""
        self.client.get("/health", name="/health")


class DashboardUser(HttpUser):
    """模拟 Dashboard 用户 - 低频浏览"""
    wait_time = between(3, 8)

    @task(3)
    def get_stats(self):
        """获取今日统计"""
        self.client.get("/api/stats/today", name="/api/stats/today")

    @task(2)
    def get_knowledge_graph(self):
        """获取知识图谱"""
        self.client.get("/api/graph", name="/api/graph")

    @task(1)
    def search_plans(self):
        """预案检索"""
        self.client.post(
            "/api/plan/search",
            json={
                "query": "气体泄漏应急处置",
                "top_k": 3,
            },
            name="/api/plan/search"
        )
