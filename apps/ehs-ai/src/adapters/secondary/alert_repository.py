"""PostgreSQL 告警存储层

职责：告警记录的持久化和查询
使用 psycopg2 连接池，支持生产级并发
"""
import json
import logging
from typing import List, Dict, Any, Optional

import psycopg2
from psycopg2 import pool

logger = logging.getLogger(__name__)


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_id UUID UNIQUE NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    alert_content TEXT NOT NULL,
    location VARCHAR(200) NOT NULL,
    alert_level INTEGER NOT NULL CHECK (alert_level BETWEEN 1 AND 4),
    risk_level VARCHAR(20) NOT NULL DEFAULT 'unknown',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    plans JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)",
    "CREATE INDEX IF NOT EXISTS idx_alerts_risk_level ON alerts(risk_level)",
    "CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC)",
]


class AlertRepository:
    """告警 PostgreSQL 仓储"""

    def __init__(
        self,
        database: str = "ehs",
        user: str = "ehs",
        password: str = "ehs123",
        host: str = "localhost",
        port: int = 5432,
        minconn: int = 1,
        maxconn: int = 10,
    ):
        self._pool = pool.SimpleConnectionPool(
            minconn, maxconn,
            dbname=database, user=user, password=password,
            host=host, port=port,
        )
        self._init_db()

    def _get_conn(self):
        return self._pool.getconn()

    def _release_conn(self, conn):
        self._pool.putconn(conn)

    def _init_db(self):
        """初始化数据库表和索引"""
        conn = self._get_conn()
        try:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_SQL)
                for idx_sql in CREATE_INDEXES_SQL:
                    cur.execute(idx_sql)
        finally:
            self._release_conn(conn)

    def save_alert(self, alert: Dict[str, Any]) -> str:
        """保存告警记录"""
        conn = self._get_conn()
        try:
            conn.autocommit = False
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO alerts
                       (alert_id, device_id, device_type, alert_type, alert_content,
                        location, alert_level, risk_level, status, plans)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                       ON CONFLICT (alert_id) DO UPDATE SET
                           status = EXCLUDED.status,
                           risk_level = EXCLUDED.risk_level,
                           plans = EXCLUDED.plans,
                           updated_at = NOW()""",
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
                    ),
                )
            conn.commit()
            return alert["alert_id"]
        except Exception:
            conn.rollback()
            raise
        finally:
            self._release_conn(conn)

    def list_alerts(
        self,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List[Dict[str, Any]]:
        """查询告警列表"""
        conn = self._get_conn()
        try:
            query = "SELECT * FROM alerts WHERE 1=1"
            params: list = []

            if status:
                query += " AND status = %s"
                params.append(status)
            if risk_level:
                query += " AND risk_level = %s"
                params.append(risk_level)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                return [self._row_to_dict(dict(zip(cols, row))) for row in rows]
        finally:
            self._release_conn(conn)

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
                query += " AND status = %s"
                params.append(status)
            if risk_level:
                query += " AND risk_level = %s"
                params.append(risk_level)

            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()[0]
        finally:
            self._release_conn(conn)

    def get_stats(self) -> Dict[str, Any]:
        """获取告警统计"""
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE status = 'pending') as pending,
                        COUNT(*) FILTER (WHERE status = 'processing') as processing,
                        COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
                        COUNT(*) FILTER (WHERE status = 'closed') as closed
                    FROM alerts
                """)
                row = cur.fetchone()
                return {
                    "total": row[0] or 0,
                    "pending": row[1] or 0,
                    "processing": row[2] or 0,
                    "resolved": row[3] or 0,
                    "closed": row[4] or 0,
                }
        finally:
            self._release_conn(conn)

    def update_status(self, alert_id: str, status: str) -> bool:
        """更新告警状态"""
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE alerts SET status = %s, updated_at = NOW() WHERE alert_id = %s",
                    (status, alert_id),
                )
            conn.commit()
            return cur.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            self._release_conn(conn)

    def close(self):
        """关闭连接池"""
        self._pool.closeall()

    @staticmethod
    def _row_to_dict(row: dict) -> Dict[str, Any]:
        """将行数据转换为 dict"""
        d = dict(row)
        for key in ("created_at", "updated_at"):
            if key in d and d[key]:
                d[key] = d[key].isoformat()
        try:
            d["plans"] = json.loads(d.get("plans", "[]")) if isinstance(d.get("plans"), str) else d.get("plans", [])
        except (json.JSONDecodeError, TypeError):
            d["plans"] = []
        return d
