# apps/ehs-ai/src/core/agents/workflow.py
"""Multi-Agent 工作流 - 核心域"""
from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    """Agent 状态"""
    alert_message: str  # 告警消息
    risk_assessment: Optional[Dict[str, Any]]  # 风险评估结果
    emergency_plans: List[Dict[str, Any]]  # 检索到的应急预案
    error: Optional[str]  # 错误信息


class RiskAgentPort:
    """风险感知 Agent 端口接口"""

    def assess(self, alert_message: str) -> Dict[str, Any]:
        """
        评估告警风险

        Args:
            alert_message: 告警消息

        Returns:
            风险评估结果
        """
        raise NotImplementedError


class SearchAgentPort:
    """预案检索 Agent 端口接口"""

    def search(self, query: str, risk_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        检索应急预案

        Args:
            query: 查询文本
            risk_level: 风险等级

        Returns:
            预案列表
        """
        raise NotImplementedError


def create_risk_perception_node(risk_agent: RiskAgentPort):
    """
    创建风险感知节点

    Args:
        risk_agent: 风险感知 Agent 实例

    Returns:
        节点函数
    """
    def risk_perception_node(state: AgentState) -> AgentState:
        """风险感知节点"""
        try:
            assessment = risk_agent.assess(state["alert_message"])
            return {**state, "risk_assessment": assessment}
        except Exception as e:
            return {
                **state,
                "error": f"RiskAgent: {str(e)}",
                "risk_assessment": {
                    "risk_level": "unknown",
                    "confidence": 0.0,
                    "factors": [],
                    "recommended_actions": []
                }
            }

    return risk_perception_node


def create_plan_retrieval_node(search_agent: SearchAgentPort):
    """
    创建预案检索节点

    Args:
        search_agent: 预案检索 Agent 实例

    Returns:
        节点函数
    """
    def plan_retrieval_node(state: AgentState) -> AgentState:
        """预案检索节点"""
        try:
            if not state.get("risk_assessment"):
                return state

            risk_level = state["risk_assessment"].get("risk_level", "unknown")
            query = f"{risk_level}风险 应急预案"
            plans = search_agent.search(query, risk_level=risk_level)

            return {**state, "emergency_plans": plans}
        except Exception as e:
            return {
                **state,
                "error": state.get("error", "") + f"; SearchAgent: {str(e)}",
                "emergency_plans": []
            }

    return plan_retrieval_node


def create_workflow(
    risk_agent: RiskAgentPort,
    search_agent: SearchAgentPort
) -> StateGraph:
    """
    创建 LangGraph 工作流

    Args:
        risk_agent: 风险感知 Agent
        search_agent: 预案检索 Agent

    Returns:
        编译后的工作流
    """
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("risk_perception", create_risk_perception_node(risk_agent))
    workflow.add_node("plan_retrieval", create_plan_retrieval_node(search_agent))

    # 设置入口
    workflow.set_entry_point("risk_perception")

    # 添加边
    workflow.add_edge("risk_perception", "plan_retrieval")
    workflow.add_edge("plan_retrieval", END)

    return workflow.compile()
