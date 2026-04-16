# apps/ehs-ai/src/core/agents/search_agent.py
"""预案检索 Agent - 核心域"""
from typing import Optional, List, Dict, Any

from src.core.agents.workflow import SearchAgentPort
from src.core.graph_rag import GraphRAGCore
from src.core.agents.output_validators import (
    EmergencyPlanValidator,
    EmergencyPlan,
    RuleBasedFallback
)


class SearchAgent(SearchAgentPort):
    """
    预案检索 Agent 实现

    负责根据风险等级和事件类型，检索相应的应急预案。
    使用 GraphRAG 进行混合检索，支持 pydantic 验证和 fallback 处理。

    降级策略：
    1. GraphRAG 检索成功 + 验证通过 → 返回检索结果
    2. GraphRAG 检索成功 + 验证失败 → 使用验证器 fallback
    3. GraphRAG 检索失败 → 使用规则引擎 fallback
    """

    def __init__(self, graph_rag: GraphRAGCore):
        """
        初始化 SearchAgent

        Args:
            graph_rag: GraphRAG 实例
        """
        self._graph_rag = graph_rag

    def search(self, query: str, risk_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        检索应急预案

        Args:
            query: 查询文本
            risk_level: 风险等级

        Returns:
            预案列表
        """
        try:
            results = self._graph_rag.search(query, top_k=5)

            if risk_level:
                results = self._filter_by_risk_level(results, risk_level)

            # 使用验证器验证检索结果
            plans = EmergencyPlanValidator.validate_list(results)
            return [self._to_dict(plan) for plan in plans]

        except Exception as e:
            # 检索失败，降级到规则引擎
            print(f"[SearchAgent] 检索失败：{e}，降级到规则引擎")
            if risk_level:
                fallback_plans = RuleBasedFallback.get_default_plans(risk_level)
            else:
                fallback_plans = RuleBasedFallback.get_default_plans("medium")
            return [self._to_dict(plan) for plan in fallback_plans]

    def _filter_by_risk_level(
        self,
        results: List[Dict[str, Any]],
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """根据风险等级过滤预案"""
        if not risk_level:
            return results

        filtered = []
        for result in results:
            metadata = result.get("metadata", {})
            result_risk = metadata.get("risk_level", "")

            if not result_risk or result_risk == risk_level:
                filtered.append(result)

        return filtered if filtered else results

    def _to_dict(self, plan: EmergencyPlan) -> Dict[str, Any]:
        """将 EmergencyPlan 转换为字典"""
        return {
            "title": plan.title,
            "content": plan.content,
            "risk_level": plan.risk_level,
            "source": plan.source,
            "score": plan.score
        }
