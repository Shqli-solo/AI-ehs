# python-ai-service/src/rag/es_search.py
"""Elasticsearch BM25 检索器"""
from elasticsearch import Elasticsearch
from src.core.logging import log
from src.core.config import settings


class ESSearcher:
    """Elasticsearch BM25 检索器"""

    def __init__(self, index: str = None):
        self.index = index or settings.ES_INDEX
        self.client = Elasticsearch([settings.ES_URL])
        log.info(f"ES 检索器初始化，index={self.index}")

    def search(self, query: str, event_type: str = None, top_k: int = 20) -> list:
        """
        ES BM25 文本检索

        Args:
            query: 查询文本
            event_type: 事件类型（如 fire, gas_leak）
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        must_clause = {"match": {"content": query}}

        if event_type:
            query_dict = {
                "query": {
                    "bool": {
                        "must": must_clause,
                        "filter": {"term": {"event_type": event_type}}
                    }
                },
                "size": top_k
            }
        else:
            query_dict = {
                "query": must_clause,
                "size": top_k
            }

        try:
            response = self.client.search(index=self.index, body=query_dict)
            results = [
                {
                    "id": hit["_id"],
                    "content": hit["_source"].get("content", ""),
                    "score": hit["_score"],
                    "metadata": hit["_source"].get("metadata", {})
                }
                for hit in response["hits"]["hits"]
            ]
            log.info(f"ES 检索返回 {len(results)} 条结果")
            return results
        except Exception as e:
            log.error(f"ES 检索失败：{e}")
            # 降级：返回空结果，不中断整个检索流程
            return []
