# apps/ehs-ai/src/adapters/secondary/elasticsearch.py
"""Elasticsearch 文本检索适配器 - Secondary Adapter"""
from typing import Optional, List, Dict, Any
from elasticsearch import Elasticsearch

from src.ports.secondary.storage import TextStoragePort


class ElasticsearchAdapter(TextStoragePort):
    """
    Elasticsearch 文本检索适配器

    实现 TextStoragePort 接口，提供 BM25 文本检索能力
    """

    def __init__(self, url: str, index: str):
        """
        初始化 Elasticsearch 适配器

        Args:
            url: Elasticsearch 服务地址
            index: 索引名称
        """
        self._url = url
        self._index = index
        self._client = Elasticsearch([url])

    def search(
        self,
        query: str,
        event_type: Optional[str] = None,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        ES BM25 文本检索

        Args:
            query: 查询文本
            event_type: 事件类型
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
            response = self._client.search(index=self._index, body=query_dict)
            results = [
                {
                    "id": hit["_id"],
                    "content": hit["_source"].get("content", ""),
                    "score": hit["_score"],
                    "metadata": hit["_source"].get("metadata", {})
                }
                for hit in response["hits"]["hits"]
            ]
            return results
        except Exception:
            # 降级：返回空结果，不中断流程
            return []
