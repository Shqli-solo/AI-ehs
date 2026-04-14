# python-ai-service/src/agents/risk_agent.py
"""风险感知 Agent - 基于 LLM 的风险评估"""
import re
import httpx
from typing import TypedDict, Any
from src.core.logging import log
from src.core.config import settings


class RiskAssessment(TypedDict):
    """风险评估结果"""
    risk_level: str  # low, medium, high, unknown
    confidence: float
    factors: list[str]
    recommended_actions: list[str]


class RiskAgent:
    """
    风险感知 Agent

    负责分析告警信息，评估风险等级，提供建议操作。
    使用 LLM 进行语义理解，支持非 JSON 响应的 fallback 处理。
    """

    def __init__(self, llm_endpoint: str = None):
        """
        初始化 RiskAgent

        Args:
            llm_endpoint: LLM 服务地址，默认使用配置
        """
        self.llm_endpoint = llm_endpoint or "http://localhost:8080/v1/chat/completions"
        log.info(f"RiskAgent 初始化完成，LLM 端点：{self.llm_endpoint}")

    def assess(self, alert_message: str) -> RiskAssessment:
        """
        评估告警风险

        Args:
            alert_message: 告警消息文本

        Returns:
            风险评估结果
        """
        try:
            log.info(f"开始风险评估：{alert_message}")

            # 调用 LLM 进行风险评估
            response = self._call_llm(alert_message)

            # 尝试解析 JSON 响应
            result = self._parse_response(response)

            log.info(f"风险评估完成：risk_level={result['risk_level']}, confidence={result['confidence']}")
            return result

        except Exception as e:
            log.error(f"风险评估失败：{e}")
            # 降级处理：返回默认值，不抛出异常
            return self._get_default_assessment()

    def _call_llm(self, alert_message: str) -> Any:
        """
        调用 LLM 服务

        Args:
            alert_message: 告警消息

        Returns:
            LLM 响应
        """
        prompt = f"""你是一个专业的 EHS 风险评估专家。请分析以下告警信息，评估风险等级。

告警信息：{alert_message}

请以 JSON 格式返回评估结果：
{{
    "risk_level": "low|medium|high",
    "confidence": 0.0-1.0,
    "factors": ["风险因素 1", "风险因素 2"],
    "recommended_actions": ["建议操作 1", "建议操作 2"]
}}

只返回 JSON，不要其他内容。"""

        with httpx.Client() as client:
            response = client.post(
                self.llm_endpoint,
                json={
                    "model": "ehs-risk-assessment",
                    "messages": [
                        {"role": "system", "content": "你是 EHS 风险评估专家，只返回 JSON 格式的风险评估结果。"},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response

    def _parse_response(self, response: Any) -> RiskAssessment:
        """
        解析 LLM 响应

        Args:
            response: LLM 响应对象

        Returns:
            风险评估结果
        """
        try:
            # 尝试直接解析 JSON
            data = response.json()
            return {
                "risk_level": data.get("risk_level", "unknown"),
                "confidence": float(data.get("confidence", 0.0)),
                "factors": data.get("factors", []),
                "recommended_actions": data.get("recommended_actions", [])
            }
        except (ValueError, KeyError) as e:
            # JSON 解析失败，尝试从文本中提取
            log.warning(f"JSON 解析失败，尝试 fallback 解析：{e}")
            return self._extract_risk_level(response.text)

    def _extract_risk_level(self, text: str) -> RiskAssessment:
        """
        从非 JSON 文本中提取风险等级（fallback 方法）

        Args:
            text: LLM 返回的文本

        Returns:
            风险评估结果
        """
        # 风险等级映射
        risk_map = {
            "high": "high",
            "高风险": "high",
            "medium": "medium",
            "中风险": "medium",
            "中": "medium",
            "low": "low",
            "低风险": "low",
            "低": "low"
        }

        # 尝试提取风险等级
        risk_level = "unknown"

        # 匹配常见模式
        patterns = [
            r'风险等级 [::\s]*(high|medium|low|高 | 中 | 低)',
            r'risk[_:]*level[::\s]*(high|medium|low)',
            r'(high|medium|low|高 | 中 | 低) 风险',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                matched_text = match.group(1).lower()
                risk_level = risk_map.get(matched_text, "unknown")
                break

        # 提取置信度（如果有数字）
        confidence = 0.5  # 默认置信度
        conf_match = re.search(r'(\d{2})%|\b(0\.\d+)\b', text)
        if conf_match:
            if '%' in conf_match.group():
                confidence = float(conf_match.group().replace('%', '')) / 100
            else:
                confidence = float(conf_match.group())

        log.info(f"Fallback 解析成功：risk_level={risk_level}")

        return {
            "risk_level": risk_level,
            "confidence": confidence,
            "factors": ["从文本中提取的风险因素"],
            "recommended_actions": ["建议进一步分析"]
        }

    def _get_default_assessment(self) -> RiskAssessment:
        """
        获取默认风险评估（异常时的降级处理）

        Returns:
            默认风险评估结果
        """
        return {
            "risk_level": "unknown",
            "confidence": 0.0,
            "factors": [],
            "recommended_actions": ["建议人工介入评估"]
        }
