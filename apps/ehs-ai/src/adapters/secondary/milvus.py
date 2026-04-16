# apps/ehs-ai/src/adapters/secondary/milvus.py
"""Milvus 向量检索适配器 - Secondary Adapter"""
from typing import List, Dict, Any, Optional
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer

from src.ports.secondary.storage import VectorStoragePort


class MilvusAdapter(VectorStoragePort):
    """
    Milvus 向量检索适配器

    实现 VectorStoragePort 接口，提供向量相似度检索能力
    """

    def __init__(self, url: str, port: int, collection: str, embedding_model: str):
        """
        初始化 Milvus 适配器

        Args:
            url: Milvus 服务地址
            port: Milvus 端口
            collection: Collection 名称
            embedding_model: Embedding 模型名称
        """
        self._collection_name = collection
        self._embedding_model = SentenceTransformer(embedding_model)

        # 连接 Milvus
        self._client = connections.connect(host=url, port=port)

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """
        向量检索（自动将 query 转换为向量）

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        embedding = self.encode(query)
        return self.search_by_vector(embedding, top_k)

    def search_by_vector(self, embedding: List[float], top_k: int = 20) -> List[Dict[str, Any]]:
        """
        向量相似度检索

        Args:
            embedding: 向量嵌入
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        try:
            collection = Collection(self._collection_name)
            search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}

            results = collection.search(
                data=[embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["content", "metadata"]
            )

            result_list = [
                {
                    "id": hit.entity.get("id"),
                    "content": hit.entity.get("content"),
                    "score": hit.score,
                    "metadata": hit.entity.get("metadata", {})
                }
                for hit in results[0]
            ]
            return result_list
        except Exception:
            # 降级：返回空结果
            return []

    def encode(self, text: str) -> List[float]:
        """
        将文本编码为向量

        Args:
            text: 输入文本

        Returns:
            向量嵌入
        """
        return self._embedding_model.encode(text).tolist()
