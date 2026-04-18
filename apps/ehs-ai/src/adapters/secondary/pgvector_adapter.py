"""PostgreSQL pgvector 向量检索适配器

参考 Dify 设计：使用 pgvector 替代 Milvus 进行向量相似度搜索。
支持 cosine similarity 检索和向量 upsert。
"""
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2 import pool
import json
import logging

from src.ports.secondary.storage import VectorStoragePort

logger = logging.getLogger(__name__)

CREATE_PLANS_TABLE = """
CREATE TABLE IF NOT EXISTS ehs_ai.plans (
    id SERIAL PRIMARY KEY,
    plan_id UUID UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    event_type VARCHAR(50),
    risk_level VARCHAR(20),
    embedding vector(384),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

CREATE_IVF_INDEX = """
CREATE INDEX IF NOT EXISTS idx_plans_embedding
ON ehs_ai.plans USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)
"""


class PgVectorAdapter(VectorStoragePort):
    """pgvector 向量检索适配器"""

    def __init__(
        self,
        database: str = "ehs",
        user: str = "ehs",
        password: str = "ehs123",
        host: str = "localhost",
        port: int = 5432,
        embedding_model: str = "BAAI/bge-small-zh-v1.5",
    ):
        self._embedding_model = SentenceTransformer(embedding_model)
        self._pool = pool.SimpleConnectionPool(
            1, 5,
            dbname=database, user=user, password=password,
            host=host, port=port,
        )
        self._init_table()

    def _get_conn(self):
        return self._pool.getconn()

    def _release_conn(self, conn):
        self._pool.putconn(conn)

    def _init_table(self):
        conn = self._get_conn()
        try:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(CREATE_PLANS_TABLE)
                cur.execute(CREATE_IVF_INDEX)
        finally:
            self._release_conn(conn)

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """文本向量检索"""
        embedding = self.encode(query)
        return self.search_by_vector(embedding, top_k)

    def search_by_vector(self, embedding: List[float], top_k: int = 20) -> List[Dict[str, Any]]:
        """向量相似度检索 (cosine)"""
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                vec_str = json.dumps(embedding)
                cur.execute(
                    """SELECT plan_id, title, content, event_type, risk_level, metadata,
                              1 - (embedding <=> %s::vector) as similarity
                       FROM ehs_ai.plans
                       WHERE embedding IS NOT NULL
                       ORDER BY embedding <=> %s::vector
                       LIMIT %s""",
                    (vec_str, vec_str, top_k),
                )
                rows = cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                results = []
                for row in rows:
                    row_dict = dict(zip(cols, row))
                    results.append({
                        "id": row_dict["plan_id"],
                        "title": row_dict["title"],
                        "content": row_dict["content"],
                        "event_type": row_dict["event_type"],
                        "risk_level": row_dict["risk_level"],
                        "score": float(row_dict["similarity"]),
                        "metadata": row_dict["metadata"] or {},
                    })
                return results
        except Exception as e:
            logger.warning(f"pgvector 检索失败: {e}")
            return []
        finally:
            self._release_conn(conn)

    def upsert(self, plan_id: str, title: str, content: str, embedding: List[float], metadata: Dict[str, Any] = None):
        """插入或更新向量记录"""
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO ehs_ai.plans (plan_id, title, content, embedding, metadata)
                       VALUES (%s, %s, %s, %s::vector, %s)
                       ON CONFLICT (plan_id) DO UPDATE SET
                           title = EXCLUDED.title,
                           content = EXCLUDED.content,
                           embedding = EXCLUDED.embedding,
                           metadata = EXCLUDED.metadata""",
                    (plan_id, title, content, json.dumps(embedding), json.dumps(metadata or {})),
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.warning(f"pgvector 插入失败: {e}")
        finally:
            self._release_conn(conn)

    def encode(self, text: str) -> List[float]:
        """将文本编码为向量"""
        return self._embedding_model.encode(text).tolist()

    def close(self):
        """关闭连接池"""
        self._pool.closeall()
