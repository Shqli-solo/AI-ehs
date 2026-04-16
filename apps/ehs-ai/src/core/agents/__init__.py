# apps/ehs-ai/src/core/agents/__init__.py
"""Agents 模块

Multi-Agent LangGraph 工作流，包含：
- RiskAgent: 风险感知 Agent
- SearchAgent: 预案检索 Agent
- output_validators: LLM 输出结构化验证（Pydantic）
- workflow: LangGraph 工作流编排
"""
from src.core.agents.workflow import (
    AgentState,
    RiskAgentPort,
    SearchAgentPort,
    create_workflow,
    create_risk_perception_node,
    create_plan_retrieval_node,
)
from src.core.agents.risk_agent import RiskAgent
from src.core.agents.search_agent import SearchAgent
from src.core.agents.output_validators import (
    RiskAssessment,
    EmergencyPlan,
    RiskAssessmentValidator,
    EmergencyPlanValidator,
    RuleBasedFallback,
    OutputValidator,
)

__all__ = [
    # 状态和端口
    "AgentState",
    "RiskAgentPort",
    "SearchAgentPort",
    # 工作流
    "create_workflow",
    "create_risk_perception_node",
    "create_plan_retrieval_node",
    # Agent 实现
    "RiskAgent",
    "SearchAgent",
    # 输出验证
    "RiskAssessment",
    "EmergencyPlan",
    "RiskAssessmentValidator",
    "EmergencyPlanValidator",
    "RuleBasedFallback",
    "OutputValidator",
]
