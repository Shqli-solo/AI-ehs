# python-ai-service/src/rag/milvus_search.py
"""Milvus 向量检索器"""
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer
from src.core.logging import log
from src.core.config import settings


class MilvusSearcher:
    """Milvus 向量检索器"""

    def __init__(self, collection: str = None):
        self.collection_name = collection or settings.MILVUS_COLLECTION
        self.client = connections.connect(
            host=settings.MILVUS_URL,
            port=settings.MILVUS_PORT
        )
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        log.info(f"Milvus 检索器初始化，collection={self.collection_name}")

    def search(self, query: str, top_k: int = 20) -> list:
        """
        向量检索（自动将 query 转换为向量）

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        embedding = self.embedding_model.encode(query).tolist()
        return self.search_by_vector(embedding, top_k)

    def search_by_vector(self, embedding: list, top_k: int = 20) -> list:
        """
        向量相似度检索

        Args:
            embedding: 向量嵌入（768 维）
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        try:
            collection = Collection(self.collection_name)
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
            log.info(f"Milvus 检索返回 {len(result_list)} 条结果")
            return result_list
        except Exception as e:
            log.error(f"Milvus 检索失败：{e}")
            # 降级：返回空结果，不中断整个检索流程
            return []
