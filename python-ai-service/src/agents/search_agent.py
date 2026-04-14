# python-ai-service/src/agents/search_agent.py
"""预案检索 Agent - 基于 GraphRAG 的预案检索"""
from typing import Optional
from src.core.logging import log
from src.rag.graph_rag import GraphRAGSearcher


class SearchAgent:
    """
    预案检索 Agent

    负责根据风险等级和事件类型，检索相应的应急预案。
    使用 GraphRAG 进行混合检索（BM25 + 向量相似度 + 重排序）。
    """

    def __init__(self):
        """初始化 SearchAgent"""
        self.searcher = GraphRAGSearcher()
        log.info("SearchAgent 初始化完成")

    def search(self, query: str, risk_level: Optional[str] = None, event_type: Optional[str] = None, top_k: int = 5) -> list:
        """
        检索应急预案

        Args:
            query: 查询文本
            risk_level: 风险等级过滤（low, medium, high）
            event_type: 事件类型（fire, gas_leak 等）
            top_k: 返回结果数量

        Returns:
            预案列表
        """
        try:
            log.info(f"开始检索预案：query={query}, risk_level={risk_level}, event_type={event_type}")

            # 使用 GraphRAG 检索
            results = self.searcher.search(query, event_type, top_k=top_k)

            # 根据风险等级过滤
            if risk_level:
                results = self._filter_by_risk_level(results, risk_level)

            log.info(f"预案检索完成，返回 {len(results)} 条结果")
            return results

        except Exception as e:
            log.error(f"预案检索失败：{e}")
            # 降级处理：返回空列表，不抛出异常
            return []

    def _filter_by_risk_level(self, results: list, risk_level: str) -> list:
        """
        根据风险等级过滤预案

        Args:
            results: 检索结果
            risk_level: 目标风险等级

        Returns:
            过滤后的结果
        """
        if not risk_level:
            return results

        filtered = []
        for result in results:
            metadata = result.get("metadata", {})
            result_risk = metadata.get("risk_level", "")

            # 风险等级匹配或无风险等级标注的预案都保留
            if not result_risk or result_risk == risk_level:
                filtered.append(result)

        # 如果过滤后为空，返回原始结果（降级）
        if not filtered:
            log.warning(f"风险等级过滤后无结果，返回全部 {len(results)} 条")
            return results

        return filtered
