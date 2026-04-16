# apps/ehs-ai/src/core/agents/output_validators.py
"""LLM 输出结构化验证 - 核心域

使用 Pydantic 进行数据结构验证，确保 LLM 输出符合预期格式。
支持错误降级处理，当验证失败时提供 fallback 机制。
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, ValidationError
import re


# ============== 风险评估输出模型 ==============

class RiskAssessment(BaseModel):
    """风险评估结果模型"""
    risk_level: Literal["low", "medium", "high", "unknown"] = Field(
        default="unknown",
        description="风险等级"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="置信度 (0-1)"
    )
    factors: List[str] = Field(
        default_factory=list,
        description="风险因素列表"
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="建议操作列表"
    )

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """验证置信度范围"""
        if not (0.0 <= v <= 1.0):
            return max(0.0, min(1.0, v))
        return v

    @field_validator('factors', 'recommended_actions')
    @classmethod
    def validate_lists(cls, v: List[str]) -> List[str]:
        """验证列表不为空"""
        if not v:
            return ["需要进一步分析"]
        return [item.strip() for item in v if item.strip()]


# ============== 预案检索输出模型 ==============

class EmergencyPlan(BaseModel):
    """应急预案模型"""
    title: str = Field(..., description="预案标题")
    content: str = Field(..., description="预案内容")
    risk_level: Literal["low", "medium", "high", "unknown"] = Field(
        default="unknown",
        description="适用风险等级"
    )
    source: str = Field(default="unknown", description="预案来源")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="匹配分数")

    @field_validator('score')
    @classmethod
    def validate_score(cls, v: float) -> float:
        """验证分数范围"""
        if not (0.0 <= v <= 1.0):
            return max(0.0, min(1.0, v))
        return v


# ============== 验证器类 ==============

class OutputValidator:
    """LLM 输出验证器基类"""

    @staticmethod
    def validate_with_fallback(
        model_class: type[BaseModel],
        data: Any,
        fallback_data: Optional[Dict[str, Any]] = None
    ) -> BaseModel:
        """
        验证数据，失败时使用 fallback

        Args:
            model_class: Pydantic 模型类
            data: 待验证的数据
            fallback_data:  fallback 数据

        Returns:
            验证后的模型实例
        """
        try:
            return model_class.model_validate(data)
        except (ValidationError, ValueError, TypeError) as e:
            if fallback_data:
                try:
                    return model_class.model_validate(fallback_data)
                except (ValidationError, ValueError, TypeError):
                    return model_class()
            return model_class()


class RiskAssessmentValidator(OutputValidator):
    """风险评估输出验证器"""

    @staticmethod
    def validate(
        raw_data: Any,
        fallback_assessment: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        """
        验证风险评估输出

        Args:
            raw_data: 原始 LLM 输出（dict 或 JSON 字符串）
            fallback_assessment: fallback 风险评估数据

        Returns:
            验证后的 RiskAssessment
        """
        # 如果是字符串，尝试解析 JSON
        if isinstance(raw_data, str):
            import json
            try:
                raw_data = json.loads(raw_data)
            except json.JSONDecodeError:
                # 从文本中提取 JSON
                extracted = RiskAssessmentValidator._extract_json_from_text(raw_data)
                if extracted:
                    raw_data = extracted
                else:
                    raw_data = {}

        # 检查数据是否包含至少一个有效字段
        if not isinstance(raw_data, dict) or not raw_data:
            # 数据无效，使用 fallback
            pass  # raw_data 保持为空 dict 或无效数据

        # 检查是否包含关键字段，如果没有则使用 fallback
        valid_keys = {"risk_level", "confidence", "factors", "recommended_actions"}
        has_valid_data = any(key in raw_data for key in valid_keys)

        default_fallback = {
            "risk_level": "unknown",
            "confidence": 0.0,
            "factors": ["无法解析 LLM 输出"],
            "recommended_actions": ["建议人工介入评估"]
        }

        if not has_valid_data:
            # 数据无效，使用 fallback
            if fallback_assessment is None:
                fallback_assessment = default_fallback
            return RiskAssessmentValidator.validate_with_fallback(
                RiskAssessment, fallback_assessment, None
            )

        if fallback_assessment is None:
            fallback_assessment = default_fallback

        return RiskAssessmentValidator.validate_with_fallback(
            RiskAssessment, raw_data, fallback_assessment
        )

    @staticmethod
    def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取 JSON"""
        import json

        # 尝试匹配 JSON 对象
        patterns = [
            r'\{[^{}]*\}',  # 简单 JSON 对象
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # 嵌套 JSON 对象
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue

        # 如果无法提取 JSON，尝试提取关键字段
        result = {}

        risk_match = re.search(
            r'风险等级 [::\s]*(low|medium|high|unknown|高 | 中 | 低)|'
            r'risk[_\s]*level[::\s]*(low|medium|high|unknown)',
            text, re.IGNORECASE
        )
        if risk_match:
            risk_map = {
                'high': 'high', '高': 'high',
                'medium': 'medium', '中': 'medium',
                'low': 'low', '低': 'low',
                'unknown': 'unknown'
            }
            matched = risk_match.group(1) or risk_match.group(2)
            result['risk_level'] = risk_map.get(matched.lower(), 'unknown')

        conf_match = re.search(r'置信度 [::\s]*(\d+)%|confidence[::\s]*(\d+)%', text, re.IGNORECASE)
        if conf_match:
            result['confidence'] = int(conf_match.group(1) or conf_match.group(2)) / 100

        return result if result else None


class EmergencyPlanValidator(OutputValidator):
    """应急预案输出验证器"""

    @staticmethod
    def validate_list(
        raw_data: Any,
        fallback_plans: Optional[List[Dict[str, Any]]] = None
    ) -> List[EmergencyPlan]:
        """
        验证预案列表输出

        Args:
            raw_data: 原始输出（列表或 JSON 字符串）
            fallback_plans: fallback 预案列表

        Returns:
            验证后的 EmergencyPlan 列表
        """
        # 如果是字符串，尝试解析 JSON
        if isinstance(raw_data, str):
            import json
            try:
                raw_data = json.loads(raw_data)
            except json.JSONDecodeError:
                raw_data = []

        if not isinstance(raw_data, list):
            raw_data = [raw_data] if raw_data else []

        default_fallback = [
            {
                "title": "默认应急预案",
                "content": "1. 记录事件 2. 评估情况 3. 采取适当措施",
                "risk_level": "unknown",
                "source": "system",
                "score": 0.5
            }
        ]

        if fallback_plans is None:
            fallback_plans = default_fallback

        results = []
        for item in raw_data:
            try:
                plan = EmergencyPlan.model_validate(item)
                results.append(plan)
            except (ValidationError, ValueError, TypeError):
                continue

        if not results and fallback_plans:
            for item in fallback_plans:
                try:
                    plan = EmergencyPlan.model_validate(item)
                    results.append(plan)
                except (ValidationError, ValueError, TypeError):
                    continue

        if not results:
            results.append(EmergencyPlan.model_validate(default_fallback[0]))

        return results


# ============== 规则引擎 Fallback ==============

class RuleBasedFallback:
    """基于规则的降级处理"""

    # 风险关键词映射
    RISK_KEYWORDS = {
        "high": [
            "火灾", "爆炸", "泄漏", "中毒", "伤亡", "严重", "紧急",
            "重大", "危险", "事故", "灾难", "伤亡", "死亡"
        ],
        "medium": [
            "异常", "故障", "报警", "警告", "注意", "风险",
            "隐患", "问题", "异常", "偏离"
        ],
        "low": [
            "正常", "常规", "例行", "检查", "巡检", "轻微",
            "一般", "普通", "日常"
        ]
    }

    # 建议操作映射
    RECOMMENDED_ACTIONS = {
        "high": [
            "立即启动应急响应",
            "疏散相关人员",
            "通知应急管理部门",
            "启动应急预案",
            "持续监控事态发展"
        ],
        "medium": [
            "通知相关部门处理",
            "加强监控频率",
            "准备应急资源",
            "记录事件详情"
        ],
        "low": [
            "记录事件",
            "常规处理",
            "定期跟踪"
        ]
    }

    @classmethod
    def assess_risk(cls, alert_message: str) -> RiskAssessment:
        """
        基于规则的风险评估（LLM 失败时的 fallback）

        Args:
            alert_message: 告警消息

        Returns:
            RiskAssessment 实例
        """
        risk_level = "unknown"
        max_matches = 0

        for level, keywords in cls.RISK_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in alert_message)
            if matches > max_matches:
                max_matches = matches
                risk_level = level

        confidence = min(0.8, 0.3 + (max_matches * 0.15))

        return RiskAssessment(
            risk_level=risk_level,
            confidence=confidence,
            factors=[f"检测到{max_matches}个{risk_level}风险关键词"],
            recommended_actions=cls.RECOMMENDED_ACTIONS.get(risk_level, ["建议人工分析"])[:3]
        )

    @classmethod
    def get_default_plans(cls, risk_level: str) -> List[EmergencyPlan]:
        """
        获取默认预案（检索失败时的 fallback）

        Args:
            risk_level: 风险等级

        Returns:
            EmergencyPlan 列表
        """
        default_plans = {
            "high": [
                EmergencyPlan(
                    title="重大事故应急预案",
                    content="1. 立即启动应急响应 2. 疏散人员 3. 通知相关部门 4. 等待专业救援",
                    risk_level="high",
                    source="system",
                    score=0.5
                )
            ],
            "medium": [
                EmergencyPlan(
                    title="中等风险处置流程",
                    content="1. 通知相关部门 2. 现场处置 3. 持续监控 4. 事后总结",
                    risk_level="medium",
                    source="system",
                    score=0.5
                )
            ],
            "low": [
                EmergencyPlan(
                    title="低风险常规处理",
                    content="1. 记录事件 2. 常规处置 3. 定期跟踪",
                    risk_level="low",
                    source="system",
                    score=0.5
                )
            ]
        }

        return default_plans.get(risk_level, default_plans["medium"])
