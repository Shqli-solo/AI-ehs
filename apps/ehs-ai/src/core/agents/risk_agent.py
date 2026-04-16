# apps/ehs-ai/src/core/agents/risk_agent.py
"""风险感知 Agent - 核心域"""
import httpx
from typing import Dict, Any, Optional

from src.core.agents.workflow import RiskAgentPort
from src.core.config import settings
from src.core.agents.output_validators import (
    RiskAssessmentValidator,
    RiskAssessment,
    RuleBasedFallback
)


class RiskAgent(RiskAgentPort):
    """
    风险感知 Agent 实现

    负责分析告警信息，评估风险等级，提供建议操作。
    使用 LLM 进行语义理解，支持 pydantic 验证和多级 fallback 处理。

    降级策略：
    1. LLM 调用成功 + 验证通过 → 返回 LLM 结果
    2. LLM 调用成功 + 验证失败 → 使用验证器 fallback
    3. LLM 调用失败 → 使用规则引擎 fallback
    """

    def __init__(self, llm_endpoint: Optional[str] = None):
        """
        初始化 RiskAgent

        Args:
            llm_endpoint: LLM 服务地址
        """
        self.llm_endpoint = llm_endpoint or settings.LLM_ENDPOINT

    def assess(self, alert_message: str) -> Dict[str, Any]:
        """
        评估告警风险

        Args:
            alert_message: 告警消息

        Returns:
            风险评估结果
        """
        try:
            response = self._call_llm(alert_message)
            raw_data = response.json()

            # 使用验证器验证 LLM 输出
            assessment = RiskAssessmentValidator.validate(raw_data)
            return self._to_dict(assessment)

        except httpx.RequestError as e:
            # LLM 服务不可用，降级到规则引擎
            print(f"[RiskAgent] LLM 请求失败：{e}，降级到规则引擎")
            rule_result = RuleBasedFallback.assess_risk(alert_message)
            return self._to_dict(rule_result)

        except Exception as e:
            # 其他错误，降级到规则引擎
            print(f"[RiskAgent] 处理错误：{e}，降级到规则引擎")
            rule_result = RuleBasedFallback.assess_risk(alert_message)
            return self._to_dict(rule_result)

    def _call_llm(self, alert_message: str) -> httpx.Response:
        """调用 LLM 服务"""
        prompt = f"""你是一个专业的 EHS 风险评估专家。请分析以下告警信息，评估风险等级。

告警信息：{alert_message}

请以 JSON 格式返回评估结果：
{{
    "risk_level": "low|medium|high|unknown",
    "confidence": 0.0-1.0,
    "factors": ["风险因素 1", "风险因素 2"],
    "recommended_actions": ["建议操作 1", "建议操作 2"]
}}

只返回 JSON，不要其他内容。"""

        with httpx.Client() as client:
            response = client.post(
                self.llm_endpoint,
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是 EHS 风险评估专家，只返回 JSON 格式的风险评估结果。"
                        },
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response

    def _to_dict(self, assessment: RiskAssessment) -> Dict[str, Any]:
        """将 RiskAssessment 转换为字典"""
        return {
            "risk_level": assessment.risk_level,
            "confidence": assessment.confidence,
            "factors": assessment.factors,
            "recommended_actions": assessment.recommended_actions
        }
