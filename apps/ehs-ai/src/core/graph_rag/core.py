# apps/ehs-ai/src/core/graph_rag/core.py
"""GraphRAG 核心检索逻辑 - 核心域

GraphRAG = 知识图谱检索 + 传统检索（BM25 + 向量）+ Reranking
"""
from typing import Optional, List, Dict, Any

from src.ports.secondary.storage import TextStoragePort, VectorStoragePort
from src.core.graph_rag.knowledge_graph import KnowledgeGraph


class GraphRAGCore:
    """GraphRAG 核心检索器 - 核心域"""

    def __init__(
        self,
        text_storage: TextStoragePort,
        vector_storage: VectorStoragePort,
        knowledge_graph: Optional[KnowledgeGraph] = None,
        reranker: Optional[Any] = None
    ):
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
        """GraphRAG 增强检索"""
        graph_context = []
        enriched_query = query

        if self._knowledge_graph:
            subgraph = self._knowledge_graph.retrieve_subgraph(query, top_k=3)
            graph_context = subgraph
            enriched_query = self._knowledge_graph.enrich_query(query)
            self._knowledge_graph.get_related_plans(query)

        text_results = self._text_storage.search(enriched_query, event_type, top_k=20)
        vector_results = self._vector_storage.search(enriched_query, top_k=20)
        merged_results = self._merge_results(text_results, vector_results)

        if self._reranker and merged_results:
            documents = [r["content"] for r in merged_results]
            final_results = self._reranker.rerank(query, documents, top_k=top_k)
        else:
            final_results = merged_results[:top_k]

        if graph_context:
            for result in final_results:
                result["graph_context"] = self._extract_relevant_graph_context(
                    graph_context, result
                )

        return final_results

    def get_graph_insights(self, query: str) -> Dict[str, Any]:
        """获取图谱洞察信息"""
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
        for result in text_results:
            content = result.get("content", "")
            if content and content not in seen:
                seen[content] = result
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
            if node_name in result_content or node_name in result_title:
                relevant.append({
                    "name": node.get("name"),
                    "type": node.get("type"),
                    "relations": node.get("relations", []),
                })
        return relevant
