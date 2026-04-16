"""
EHS 智能安保决策中台 - Locust 负载测试脚本

测试场景:
1. 健康检查接口 (/health)
2. 告警上报接口 (/api/alert/report)
3. 预案检索接口 (/api/plan/search)

性能指标:
- P95 延迟 < 800ms
- 错误率 < 1%
- 50 并发用户
"""

import random
from locust import HttpUser, task, between, events
from typing import Optional


class AlertReportTask:
    """告警上报测试任务"""

    # 预设告警场景
    ALERT_SCENARIOS = [
        {
            "alert_type": "fire",
            "alert_level": 4,
            "location": "1 号楼生产车间",
            "alert_content": "烟雾探测器检测到浓烟，温度异常升高"
        },
        {
            "alert_type": "gas_leak",
            "alert_level": 5,
            "location": "2 号楼化学品仓库",
            "alert_content": "可燃气体浓度超标，达到爆炸下限"
        },
        {
            "alert_type": "temperature",
            "alert_level": 3,
            "location": "3 号楼配电室",
            "alert_content": "设备温度异常，超过安全阈值"
        },
        {
            "alert_type": "intrusion",
            "alert_level": 2,
            "location": "厂区周界",
            "alert_content": "红外对射探测器触发，检测到入侵行为"
        },
        {
            "alert_type": "water_leak",
            "alert_level": 3,
            "location": "地下室泵房",
            "alert_content": "漏水检测绳报警，检测到积水"
        }
    ]

    @classmethod
    def get_random_scenario(cls) -> dict:
        return random.choice(cls.ALERT_SCENARIOS)


class PlanSearchTask:
    """预案检索测试任务"""

    # 预设检索查询
    SEARCH_QUERIES = [
        {"query": "火灾应急处置流程", "event_type": "fire"},
        {"query": "气体泄漏应急处理", "event_type": "gas_leak"},
        {"query": "设备温度异常处理", "event_type": "temperature"},
        {"query": "入侵事件应对措施", "event_type": "intrusion"},
        {"query": "漏水事故应急预案", "event_type": "water_leak"},
        {"query": "化学品泄漏处置", "event_type": "chemical"},
        {"query": "电力故障应急处理", "event_type": "power"},
        {"query": "自然灾害应急响应", "event_type": "natural_disaster"},
    ]

    @classmethod
    def get_random_query(cls) -> dict:
        return random.choice(cls.SEARCH_QUERIES)


class EHSPerformanceTest(HttpUser):
    """
    EHS 系统性能测试 - 模拟用户行为

    配置:
    - 50 并发用户
    - 思考时间 1-3 秒
    - 权重分配：告警上报 40%, 预案检索 40%, 健康检查 20%
    """

    wait_time = between(1, 3)  # 思考时间 1-3 秒

    # 测试数据
    alert_scenarios = AlertReportTask.ALERT_SCENARIOS
    search_queries = PlanSearchTask.SEARCH_QUERIES

    def on_start(self):
        """测试开始时的初始化"""
        self.client.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @task(4)
    def report_alert(self):
        """
        任务：告警上报

        模拟 AIoT 设备上报告警事件
        """
        scenario = AlertReportTask.get_random_scenario()

        request_data = {
            "alert_type": scenario["alert_type"],
            "alert_level": scenario["alert_level"],
            "location": scenario["location"],
            "alert_content": scenario["alert_content"],
            "device_id": f"device_{random.randint(1000, 9999)}",
            "timestamp": f"2024-04-{random.randint(1, 30):02d}T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00Z"
        }

        with self.client.post(
            "/api/alert/report",
            json=request_data,
            catch_response=True,
            name="/api/alert/report"
        ) as response:
            try:
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        response.success()
                    else:
                        response.failure(f"业务失败：{data.get('message', 'unknown')}")
                else:
                    response.failure(f"HTTP {response.status_code}")
            except Exception as e:
                response.failure(f"解析错误：{str(e)}")

    @task(4)
    def search_plan(self):
        """
        任务：预案检索

        模拟用户搜索应急预案
        """
        query_info = PlanSearchTask.get_random_query()

        request_data = {
            "query": query_info["query"],
            "event_type": query_info["event_type"],
            "top_k": random.randint(3, 10)
        }

        with self.client.post(
            "/api/plan/search",
            json=request_data,
            catch_response=True,
            name="/api/plan/search"
        ) as response:
            try:
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        plans = data.get("plans", [])
                        if len(plans) > 0:
                            response.success()
                        else:
                            response.success()  # 无结果也是正常情况
                    else:
                        response.failure(f"业务失败：{data.get('message', 'unknown')}")
                else:
                    response.failure(f"HTTP {response.status_code}")
            except Exception as e:
                response.failure(f"解析错误：{str(e)}")

    @task(2)
    def health_check(self):
        """
        任务：健康检查

        模拟系统健康检查
        """
        self.client.get(
            "/health",
            catch_response=True,
            name="/health"
        )

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """测试开始时的全局初始化"""
        print("\n" + "="*60)
        print("EHS 智能安保决策中台 - Locust 性能测试")
        print("="*60)
        print(f"目标 P95 延迟：< 800ms")
        print(f"目标错误率：< 1%")
        print(f"并发用户数：50")
        print("="*60 + "\n")


# 性能阈值检查
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时的统计和阈值检查"""
    stats = environment.stats

    print("\n" + "="*60)
    print("性能测试报告摘要")
    print("="*60)

    # 总体统计
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures
    error_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0

    print(f"总请求数：{total_requests}")
    print(f"总失败数：{total_failures}")
    print(f"错误率：{error_rate:.2f}%")

    # P95 延迟
    p95 = stats.total.get_response_time_percentile(0.95)
    print(f"P95 延迟：{p95:.2f}ms")

    # 阈值检查
    print("\n阈值检查:")
    p95_pass = p95 < 800
    error_pass = error_rate < 1

    print(f"  P95 < 800ms: {'✓ PASS' if p95_pass else '✗ FAIL'} ({p95:.2f}ms)")
    print(f"  错误率 < 1%: {'✓ PASS' if error_pass else '✗ FAIL'} ({error_rate:.2f}%)")

    if p95_pass and error_pass:
        print("\n✓ 性能测试通过")
    else:
        print("\n✗ 性能测试未通过")
    print("="*60 + "\n")


# HTML 报告生成配置
def setup_locust_events():
    """设置 Locust 事件监听器"""
    pass


if __name__ == "__main__":
    import os
    os.system("locust -f locustfile.py --headless -u 50 -r 5 -t 60s --html=report.html")
