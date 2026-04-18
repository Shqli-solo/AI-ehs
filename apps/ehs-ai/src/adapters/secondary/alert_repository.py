"""SQLite 告警存储层

职责：告警记录的持久化和查询
"""
import sqlite3
import json
import logging
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT UNIQUE NOT NULL,
    device_id TEXT NOT NULL,
    device_type TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    alert_content TEXT NOT NULL,
    location TEXT NOT NULL,
    alert_level INTEGER NOT NULL,
    risk_level TEXT NOT NULL DEFAULT 'unknown',
    status TEXT NOT NULL DEFAULT 'pending',
    plans TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


class AlertRepository:
    """告警 SQLite 仓储"""

    def __init__(self, db_path: str = "data/ehs_alerts.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化数据库表"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = self._get_conn()
        try:
            conn.execute(CREATE_TABLE_SQL)
            conn.commit()
        finally:
            conn.close()

    def save_alert(self, alert: Dict[str, Any]) -> str:
        """
        保存告警记录

        Args:
            alert: 包含 alert_id, device_id, device_type, alert_type,
                   alert_content, location, alert_level, risk_level, status, plans

        Returns:
            alert_id
        """
        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT OR REPLACE INTO alerts
                   (alert_id, device_id, device_type, alert_type, alert_content,
                    location, alert_level, risk_level, status, plans, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    alert["alert_id"],
                    alert["device_id"],
                    alert["device_type"],
                    alert["alert_type"],
                    alert["alert_content"],
                    alert["location"],
                    alert["alert_level"],
                    alert.get("risk_level", "unknown"),
                    alert.get("status", "pending"),
                    json.dumps(alert.get("plans", []), ensure_ascii=False),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
            return alert["alert_id"]
        finally:
            conn.close()

    def list_alerts(
        self,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        查询告警列表

        Args:
            status: 按状态过滤（可选）
            risk_level: 按风险等级过滤（可选）
            page: 页码（从 1 开始）
            page_size: 每页数量

        Returns:
            告警列表，按创建时间倒序
        """
        conn = self._get_conn()
        try:
            query = "SELECT * FROM alerts WHERE 1=1"
            params: list = []

            if status:
                query += " AND status = ?"
                params.append(status)
            if risk_level:
                query += " AND risk_level = ?"
                params.append(risk_level)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([page_size, (page - 1) * page_size])

            rows = conn.execute(query, params).fetchall()
            return [self._row_to_dict(row) for row in rows]
        finally:
            conn.close()

    def count_alerts(
        self,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
    ) -> int:
        """查询告警总数"""
        conn = self._get_conn()
        try:
            query = "SELECT COUNT(*) FROM alerts WHERE 1=1"
            params: list = []

            if status:
                query += " AND status = ?"
                params.append(status)
            if risk_level:
                query += " AND risk_level = ?"
                params.append(risk_level)

            return conn.execute(query, params).fetchone()[0]
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """获取告警统计"""
        conn = self._get_conn()
        try:
            row = conn.execute(
                """SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
                    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                    SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed
                   FROM alerts"""
            ).fetchone()
            return {
                "total": row[0] or 0,
                "pending": row[1] or 0,
                "processing": row[2] or 0,
                "resolved": row[3] or 0,
                "closed": row[4] or 0,
            }
        finally:
            conn.close()

    def update_status(self, alert_id: str, status: str) -> bool:
        """更新告警状态"""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "UPDATE alerts SET status = ?, updated_at = ? WHERE alert_id = ?",
                (status, datetime.now(timezone.utc).isoformat(), alert_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """将 sqlite3.Row 转换为 dict"""
        d = dict(row)
        try:
            d["plans"] = json.loads(d.get("plans", "[]"))
        except (json.JSONDecodeError, TypeError):
            d["plans"] = []
        return d
