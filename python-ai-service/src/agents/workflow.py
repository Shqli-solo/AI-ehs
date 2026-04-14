# python-ai-service/src/agents/workflow.py
"""LangGraph 状态机工作流 - RiskAgent + SearchAgent 编排"""
from typing import TypedDict, Optional, Annotated
from langgraph.graph import StateGraph, END
from src.core.logging import log
from src.agents.risk_agent import RiskAgent
from src.agents.search_agent import SearchAgent


class AgentState(TypedDict):
    """Agent 状态"""
    alert_message: str  # 告警消息
    risk_assessment: Optional[dict]  # 风险评估结果
    emergency_plans: list  # 检索到的应急预案
    error: Optional[str]  # 错误信息


def risk_perception_node(state: AgentState) -> AgentState:
    """
    风险感知节点

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    try:
        log.info("执行风险感知节点")
        agent = RiskAgent()
        assessment = agent.assess(state["alert_message"])
        return {
            **state,
            "risk_assessment": assessment
        }
    except Exception as e:
        log.error(f"风险感知节点失败：{e}")
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


def plan_retrieval_node(state: AgentState) -> AgentState:
    """
    预案检索节点

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    try:
        log.info("执行预案检索节点")

        # 如果风险评估失败，跳过预案检索
        if not state.get("risk_assessment"):
            log.warning("风险评估为空，跳过预案检索")
            return state

        agent = SearchAgent()
        risk_level = state["risk_assessment"].get("risk_level", "unknown")

        # 根据风险等级检索预案
        query = f"{risk_level}风险 应急预案"
        plans = agent.search(query, risk_level=risk_level)

        return {
            **state,
            "emergency_plans": plans
        }
    except Exception as e:
        log.error(f"预案检索节点失败：{e}")
        return {
            **state,
            "error": state.get("error", "") + f"; SearchAgent: {str(e)}",
            "emergency_plans": []
        }


def create_workflow() -> StateGraph:
    """
    创建 LangGraph 工作流

    工作流顺序：
    1. 风险感知（RiskAgent）
    2. 预案检索（SearchAgent）

    Returns:
        编译后的工作流
    """
    log.info("创建 LangGraph 工作流")

    # 创建状态图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("risk_perception", risk_perception_node)
    workflow.add_node("plan_retrieval", plan_retrieval_node)

    # 设置入口
    workflow.set_entry_point("risk_perception")

    # 添加边：风险感知 → 预案检索
    workflow.add_edge("risk_perception", "plan_retrieval")
    workflow.add_edge("plan_retrieval", END)

    # 编译工作流
    app = workflow.compile()
    log.info("LangGraph 工作流创建完成")

    return app
