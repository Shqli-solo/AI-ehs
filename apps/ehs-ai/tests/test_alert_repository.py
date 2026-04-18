import pytest
import os
import tempfile
from src.adapters.secondary.alert_repository import AlertRepository


@pytest.fixture
def repo():
    """创建临时数据库的 repository"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    r = AlertRepository(path)
    yield r
    os.unlink(path)


def test_save_and_get(repo):
    """测试保存和查询"""
    repo.save_alert({
        "alert_id": "test-001",
        "device_id": "DEV-001",
        "device_type": "烟雾传感器",
        "alert_type": "烟火告警",
        "alert_content": "测试告警内容",
        "location": "A栋1楼",
        "alert_level": 3,
        "risk_level": "high",
        "status": "pending",
        "plans": []
    })

    alerts = repo.list_alerts()
    assert len(alerts) == 1
    assert alerts[0]["alert_id"] == "test-001"
    assert alerts[0]["alert_content"] == "测试告警内容"


def test_list_with_pagination(repo):
    """测试分页"""
    for i in range(5):
        repo.save_alert({
            "alert_id": f"test-{i:03d}",
            "device_id": f"DEV-{i:03d}",
            "device_type": "测试",
            "alert_type": "测试",
            "alert_content": f"内容{i}",
            "location": "位置",
            "alert_level": 1,
            "risk_level": "low",
            "status": "pending",
            "plans": []
        })

    page1 = repo.list_alerts(page=1, page_size=2)
    assert len(page1) == 2
    assert page1[0]["alert_id"] == "test-004"  # DESC order


def test_filter_by_status(repo):
    """测试按状态过滤"""
    repo.save_alert({"alert_id": "a1", "device_id": "D1", "device_type": "T", "alert_type": "T", "alert_content": "C", "location": "L", "alert_level": 1, "risk_level": "low", "status": "pending", "plans": []})
    repo.save_alert({"alert_id": "a2", "device_id": "D2", "device_type": "T", "alert_type": "T", "alert_content": "C", "location": "L", "alert_level": 1, "risk_level": "low", "status": "resolved", "plans": []})

    pending = repo.list_alerts(status="pending")
    assert len(pending) == 1
    assert pending[0]["alert_id"] == "a1"


def test_stats(repo):
    """测试统计"""
    for i in range(3):
        repo.save_alert({"alert_id": f"s{i}", "device_id": f"D{i}", "device_type": "T", "alert_type": "T", "alert_content": "C", "location": "L", "alert_level": 1, "risk_level": "low", "status": "pending" if i < 2 else "resolved", "plans": []})

    stats = repo.get_stats()
    assert stats["total"] == 3
    assert stats["pending"] == 2
    assert stats["resolved"] == 1


def test_stats_empty(repo):
    """测试空库统计"""
    stats = repo.get_stats()
    assert stats["total"] == 0
