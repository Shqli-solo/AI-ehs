# apps/ehs-ai/src/core/graph_rag.py
"""GraphRAG 核心检索逻辑 - 核心域"""
from typing import Optional, List, Dict, Any

from src.ports.secondary.storage import TextStoragePort, VectorStoragePort


class GraphRAGCore:
    """
    GraphRAG 核心检索器 - 核心域

    职责：
    1. 协调多个检索器（文本 + 向量）
    2. 合并去重检索结果
    3. 调用重排序服务

    依赖：
    - TextStoragePort: 文本检索端口（如 Elasticsearch）
    - VectorStoragePort: 向量检索端口（如 Milvus）
    - reranker: 重排序服务
    """

    def __init__(
        self,
        text_storage: TextStoragePort,
        vector_storage: VectorStoragePort,
        reranker: Optional[Any] = None
    ):
        """
        初始化 GraphRAG 核心

        Args:
            text_storage: 文本存储适配器
            vector_storage: 向量存储适配器
            reranker: 重排序服务（可选）
        """
        self._text_storage = text_storage
        self._vector_storage = vector_storage
        self._reranker = reranker

    def search(
        self,
        query: str,
        event_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        三路召回检索

        1. 文本检索（BM25）
        2. 向量检索（相似度）
        3. 合并去重
        4. 重排序

        Args:
            query: 查询文本
            event_type: 事件类型
            top_k: 返回结果数量

        Returns:
            重排序后的结果列表
        """
        # 1. 文本检索
        text_results = self._text_storage.search(query, event_type, top_k=20)

        # 2. 向量检索
        vector_results = self._vector_storage.search(query, top_k=20)

        # 3. 合并去重
        merged_results = self._merge_results(text_results, vector_results)

        # 4. 重排序
        if self._reranker and merged_results:
            documents = [r["content"] for r in merged_results]
            return self._reranker.rerank(query, documents, top_k=top_k)

        return merged_results[:top_k]

    def _merge_results(
        self,
        text_results: List[Dict[str, Any]],
        vector_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        合并并去重检索结果

        Args:
            text_results: 文本检索结果
            vector_results: 向量检索结果

        Returns:
            合并后的结果
        """
        seen = {}

        # 先添加文本检索结果
        for result in text_results:
            content = result.get("content", "")
            if content and content not in seen:
                seen[content] = result

        # 再添加向量检索结果（不重复的）
        for result in vector_results:
            content = result.get("content", "")
            if content and content not in seen:
                seen[content] = result

        return list(seen.values())
