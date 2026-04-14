# python-ai-service/tests/test_api.py
"""REST API 测试"""
import pytest
from fastapi.testclient import TestClient


class TestAlertAPI:
    """告警 API 测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from src.api.rest import app
        return TestClient(app)

    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ehs-ai-service"
        assert "timestamp" in data

    def test_alert_report(self, client):
        """测试告警上报接口"""
        payload = {
            "device_id": "CAMERA-001",
            "device_type": "camera",
            "alert_type": "fire",
            "alert_content": "生产车间 A 区检测到浓烟，能见度低于 5 米",
            "location": "生产车间 A 区",
            "alert_level": 4
        }

        response = client.post("/api/alert/report", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "alert_id" in data
        assert "plans" in data
        assert len(data["plans"]) > 0

    def test_plan_search(self, client):
        """测试预案检索接口"""
        payload = {
            "query": "火灾应急预案",
            "event_type": "fire",
            "top_k": 3
        }

        response = client.post("/api/plan/search", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "plans" in data
        assert len(data["plans"]) > 0
        assert data["query"] == "火灾应急预案"


class TestAlertAPIValidation:
    """告警 API 输入验证测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from src.api.rest import app
        return TestClient(app)

    def test_alert_report_empty_device_id(self, client):
        """测试设备 ID 为空时的验证"""
        payload = {
            "device_id": "",
            "device_type": "camera",
            "alert_type": "fire",
            "alert_content": "测试内容",
            "location": "测试位置",
            "alert_level": 2
        }

        response = client.post("/api/alert/report", json=payload)
        assert response.status_code == 422

    def test_alert_report_invalid_level(self, client):
        """测试告警级别无效时的验证"""
        payload = {
            "device_id": "CAMERA-001",
            "device_type": "camera",
            "alert_type": "fire",
            "alert_content": "测试内容",
            "location": "测试位置",
            "alert_level": 5  # 无效级别
        }

        response = client.post("/api/alert/report", json=payload)
        assert response.status_code == 422

    def test_alert_report_xss_content(self, client):
        """测试 XSS 注入内容的验证"""
        payload = {
            "device_id": "CAMERA-001",
            "device_type": "camera",
            "alert_type": "fire",
            "alert_content": "<script>alert('xss')</script>",
            "location": "测试位置",
            "alert_level": 2
        }

        response = client.post("/api/alert/report", json=payload)
        assert response.status_code == 422

    def test_alert_report_content_too_long(self, client):
        """测试内容超长时的验证"""
        payload = {
            "device_id": "CAMERA-001",
            "device_type": "camera",
            "alert_type": "fire",
            "alert_content": "a" * 3000,  # 超过 2000 字符限制
            "location": "测试位置",
            "alert_level": 2
        }

        response = client.post("/api/alert/report", json=payload)
        assert response.status_code == 422

    def test_plan_search_empty_query(self, client):
        """测试查询为空时的验证"""
        payload = {
            "query": "",
            "event_type": "fire",
            "top_k": 5
        }

        response = client.post("/api/plan/search", json=payload)
        assert response.status_code == 422

    def test_plan_search_top_k_exceeded(self, client):
        """测试 top_k 超出限制时的验证"""
        payload = {
            "query": "测试查询",
            "event_type": "fire",
            "top_k": 50  # 超过 20 限制
        }

        response = client.post("/api/plan/search", json=payload)
        # 应该自动截断到 20 或返回 422
        assert response.status_code in [200, 422]
