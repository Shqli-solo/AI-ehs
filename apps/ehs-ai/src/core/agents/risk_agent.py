# apps/ehs-ai/src/core/agents/risk_agent.py
"""风险感知 Agent - 核心域

使用 LLM 适配器（模型无关）进行风险评估，
支持多级 fallback：LLM → 验证器 → 规则引擎
"""
from typing import Dict, Any

from src.core.agents.workflow import RiskAgentPort
from src.core.agents.output_validators import (
    RiskAssessmentValidator,
    RiskAssessment,
    RuleBasedFallback
)
from src.core.llm.base import LLMAdapter, ChatMessage


class RiskAgent(RiskAgentPort):
    """
    风险感知 Agent 实现

    依赖注入 LLM 适配器，与具体模型实现解耦。

    降级策略：
    1. LLM 调用成功 + 验证通过 → 返回 LLM 结果
    2. LLM 调用成功 + 验证失败 → 使用验证器 fallback
    3. LLM 调用失败 → 使用规则引擎 fallback
    """

    def __init__(self, llm_adapter: LLMAdapter):
        """
        初始化 RiskAgent

        Args:
            llm_adapter: LLM 适配器实例
        """
        self.llm_adapter = llm_adapter

    def assess(self, alert_message: str) -> Dict[str, Any]:
        """
        评估告警风险

        Args:
            alert_message: 告警消息

        Returns:
            风险评估结果
        """
        try:
            messages = [
                ChatMessage(
                    role="system",
                    content="你是 EHS 风险评估专家，请分析告警信息，评估风险等级。"
                ),
                ChatMessage(
                    role="user",
                    content=self._build_prompt(alert_message)
                ),
            ]

            raw_data = self.llm_adapter.chat_json(
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )

            # 使用验证器验证 LLM 输出
            assessment = RiskAssessmentValidator.validate(raw_data)
            return self._to_dict(assessment)

        except Exception as e:
            # LLM 服务不可用或其他错误，降级到规则引擎
            print(f"[RiskAgent] LLM 调用失败: {e}，降级到规则引擎")
            rule_result = RuleBasedFallback.assess_risk(alert_message)
            return self._to_dict(rule_result)

    def _build_prompt(self, alert_message: str) -> str:
        """构建风险评估提示词"""
        return f"""请分析以下告警信息，评估风险等级。

告警信息：{alert_message}

请以 JSON 格式返回评估结果：
{{
    "risk_level": "low|medium|high|critical|unknown",
    "confidence": 0.0-1.0,
    "factors": ["风险因素 1", "风险因素 2"],
    "recommended_actions": ["建议操作 1", "建议操作 2"]
}}

只返回 JSON，不要其他内容。"""

    def _to_dict(self, assessment: RiskAssessment) -> Dict[str, Any]:
        """将 RiskAssessment 转换为字典"""
        return {
            "risk_level": assessment.risk_level,
            "confidence": assessment.confidence,
            "factors": assessment.factors,
            "recommended_actions": assessment.recommended_actions
        }
