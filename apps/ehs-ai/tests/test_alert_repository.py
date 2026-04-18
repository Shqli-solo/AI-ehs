import pytest
import os
import tempfile

pytestmark = pytest.mark.skipif(
    not os.environ.get("TEST_PG_HOST"),
    reason="PostgreSQL not available (set TEST_PG_HOST to enable)"
)

from src.adapters.secondary.alert_repository import AlertRepository


@pytest.fixture
def repo():
    """使用临时数据库的 repository（通过 TEST_PG_HOST 连接）"""
    host = os.environ.get("TEST_PG_HOST", "localhost")
    r = AlertRepository(
        database="ehs_test",
        user="ehs",
        password="ehs123",
        host=host,
        port=5432,
    )
    yield r
    # 清理测试数据
    try:
        conn = r._get_conn()
        try:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("DELETE FROM alerts")
        finally:
            r._release_conn(conn)
    except Exception:
        pass


def test_save_and_get(repo):
    """测试保存和查询"""
    repo.save_alert({
        "alert_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
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
    assert alerts[0]["alert_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    assert alerts[0]["alert_content"] == "测试告警内容"


def test_list_with_pagination(repo):
    """测试分页"""
    for i in range(5):
        repo.save_alert({
            "alert_id": f"00000000-0000-0000-0000-00000000000{i}",
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


def test_filter_by_status(repo):
    """测试按状态过滤"""
    repo.save_alert({"alert_id": "11111111-1111-1111-1111-111111111111", "device_id": "D1", "device_type": "T", "alert_type": "T", "alert_content": "C", "location": "L", "alert_level": 1, "risk_level": "low", "status": "pending", "plans": []})
    repo.save_alert({"alert_id": "22222222-2222-2222-2222-222222222222", "device_id": "D2", "device_type": "T", "alert_type": "T", "alert_content": "C", "location": "L", "alert_level": 1, "risk_level": "low", "status": "resolved", "plans": []})

    pending = repo.list_alerts(status="pending")
    assert len(pending) == 1


def test_stats(repo):
    """测试统计"""
    for i in range(3):
        repo.save_alert({"alert_id": f"33333333-3333-3333-3333-33333333333{i}", "device_id": f"D{i}", "device_type": "T", "alert_type": "T", "alert_content": "C", "location": "L", "alert_level": 1, "risk_level": "low", "status": "pending" if i < 2 else "resolved", "plans": []})

    stats = repo.get_stats()
    assert stats["total"] >= 3
    assert stats["pending"] >= 2
    assert stats["resolved"] >= 1
