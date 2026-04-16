# apps/ehs-ai/src/core/graph_rag.py
"""GraphRAG 核心检索逻辑 - 核心域

GraphRAG = 知识图谱检索 + 传统检索（BM25 + 向量）+ Reranking

为什么用 GraphRAG 而不是传统 RAG？
- 传统 RAG 只能检索独立文档片段，无法理解实体间的关系
- GraphRAG 通过知识图谱发现隐含的关联风险
- 例："A 栋火灾" → 传统 RAG 返回 A 栋预案
  GraphRAG 返回 A 栋预案 + "A 栋与 B 栋有连廊" + "B 栋有化学品仓库"
"""
from typing import Optional, List, Dict, Any

from src.ports.secondary.storage import TextStoragePort, VectorStoragePort
from src.core.graph_rag.knowledge_graph import KnowledgeGraph


class GraphRAGCore:
    """
    GraphRAG 核心检索器 - 核心域

    检索流程：
    1. 知识图谱检索相关子图
    2. 将子图上下文注入查询
    3. 传统三路召回（BM25 + 向量 + rerank）
    4. 在结果中附加图谱关系信息
    """

    def __init__(
        self,
        text_storage: TextStoragePort,
        vector_storage: VectorStoragePort,
        knowledge_graph: Optional[KnowledgeGraph] = None,
        reranker: Optional[Any] = None
    ):
        """
        初始化 GraphRAG 核心

        Args:
            text_storage: 文本存储适配器
            vector_storage: 向量存储适配器
            knowledge_graph: 知识图谱（可选，提供图谱增强检索）
            reranker: 重排序服务（可选）
        """
        self._text_storage = text_storage
        self._vector_storage = vector_storage
        self._knowledge_graph = knowledge_graph
        self._reranker = reranker

    def search(
        self,
        query: str,
        event_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        GraphRAG 增强检索

        1. 知识图谱检索相关子图
        2. 增强查询
        3. 文本检索（BM25）
        4. 向量检索（相似度）
        5. 合并去重
        6. 重排序
        7. 附加图谱关系信息
        """
        graph_context = []
        enriched_query = query

        # 1. 知识图谱增强（如果有）
        if self._knowledge_graph:
            # 检索相关子图
            subgraph = self._knowledge_graph.retrieve_subgraph(query, top_k=3)
            graph_context = subgraph

            # 增强查询
            enriched_query = self._knowledge_graph.enrich_query(query)

            # 获取相关预案
            graph_plans = self._knowledge_graph.get_related_plans(query)

        # 2. 文本检索（使用增强后的查询）
        text_results = self._text_storage.search(enriched_query, event_type, top_k=20)

        # 3. 向量检索
        vector_results = self._vector_storage.search(enriched_query, top_k=20)

        # 4. 合并去重
        merged_results = self._merge_results(text_results, vector_results)

        # 5. 重排序
        if self._reranker and merged_results:
            documents = [r["content"] for r in merged_results]
            final_results = self._reranker.rerank(query, documents, top_k=top_k)
        else:
            final_results = merged_results[:top_k]

        # 6. 附加图谱关系信息
        if graph_context:
            for result in final_results:
                result["graph_context"] = self._extract_relevant_graph_context(
                    graph_context, result
                )

        return final_results

    def get_graph_insights(self, query: str) -> Dict[str, Any]:
        """
        获取图谱洞察信息（用于前端展示）

        Args:
            query: 查询文本

        Returns:
            图谱相关信息，包括关联实体、风险路径等
        """
        if not self._knowledge_graph:
            return {"available": False}

        subgraph = self._knowledge_graph.retrieve_subgraph(query, top_k=5, max_depth=3)
        related_plans = self._knowledge_graph.get_related_plans(query)

        return {
            "available": True,
            "subgraph": subgraph,
            "related_plans": related_plans,
            "enriched_query": self._knowledge_graph.enrich_query(query),
        }

    def _merge_results(
        self,
        text_results: List[Dict[str, Any]],
        vector_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """合并并去重检索结果"""
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

    def _extract_relevant_graph_context(
        self,
        graph_context: List[Dict],
        result: Dict[str, Any]
    ) -> List[Dict]:
        """提取与检索结果相关的图谱上下文"""
        relevant = []
        result_content = result.get("content", "").lower()
        result_title = result.get("title", "").lower()

        for node in graph_context:
            node_name = node.get("name", "").lower()
            # 如果图谱实体在结果中被提及，认为是相关的
            if node_name in result_content or node_name in result_title:
                relevant.append({
                    "name": node.get("name"),
                    "type": node.get("type"),
                    "relations": node.get("relations", []),
                })

        return relevant
