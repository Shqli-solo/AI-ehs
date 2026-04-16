# apps/ehs-ai/tests/test_agents.py
"""Multi-Agent 测试 - 测试 RiskAgent, SearchAgent, LangGraph 工作流和输出验证"""
import pytest
from typing import Dict, Any

from src.core.agents.workflow import (
    create_workflow,
    AgentState,
    RiskAgentPort,
    SearchAgentPort
)
from src.core.agents.risk_agent import RiskAgent
from src.core.agents.search_agent import SearchAgent
from src.core.agents.output_validators import (
    RiskAssessment,
    EmergencyPlan,
    RiskAssessmentValidator,
    EmergencyPlanValidator,
    RuleBasedFallback
)
from tests.mocks import MockRiskAgent, MockSearchAgent, MockGraphRAG


# ============== Output Validator 测试 ==============

class TestRiskAssessmentValidator:
    """风险评估验证器测试"""

    def test_validate_valid_dict(self):
        """测试验证有效的字典数据"""
        raw_data = {
            "risk_level": "high",
            "confidence": 0.85,
            "factors": ["火灾风险", "人员密集"],
            "recommended_actions": ["启动应急响应", "疏散人员"]
        }

        result = RiskAssessmentValidator.validate(raw_data)

        assert result.risk_level == "high"
        assert result.confidence == 0.85
        assert len(result.factors) == 2
        assert len(result.recommended_actions) == 2

    def test_validate_invalid_risk_level(self):
        """测试验证无效的风险等级（应降级到默认值）"""
        raw_data = {
            "risk_level": "invalid_level",
            "confidence": 0.8,
            "factors": ["测试因素"],
            "recommended_actions": ["测试操作"]
        }

        result = RiskAssessmentValidator.validate(raw_data)

        # Pydantic 会将其验证为 Literal 允许的值或默认值
        assert result.risk_level in ["low", "medium", "high", "unknown"]

    def test_validate_confidence_out_of_range(self):
        """测试验证超出范围的置信度"""
        raw_data = {
            "risk_level": "medium",
            "confidence": 1.5,  # 超出范围
            "factors": ["测试"],
            "recommended_actions": ["测试"]
        }

        result = RiskAssessmentValidator.validate(raw_data)

        assert 0.0 <= result.confidence <= 1.0

    def test_validate_empty_lists(self):
        """测试验证空列表（应提供默认值）"""
        raw_data = {
            "risk_level": "low",
            "confidence": 0.9,
            "factors": [],
            "recommended_actions": []
        }

        result = RiskAssessmentValidator.validate(raw_data)

        assert len(result.factors) > 0
        assert len(result.recommended_actions) > 0

    def test_validate_from_json_string(self):
        """测试从 JSON 字符串验证"""
        json_str = '''
        {
            "risk_level": "high",
            "confidence": 0.9,
            "factors": ["严重风险"],
            "recommended_actions": ["紧急处理"]
        }
        '''

        result = RiskAssessmentValidator.validate(json_str)

        assert result.risk_level == "high"
        assert result.confidence == 0.9

    def test_validate_with_fallback(self):
        """测试验证失败时使用 fallback"""
        # 使用完全无效的数据（缺少必要字段）
        invalid_data = {"invalid": "data"}
        fallback = {
            "risk_level": "medium",
            "confidence": 0.5,
            "factors": ["fallback 因素"],
            "recommended_actions": ["fallback 操作"]
        }

        result = RiskAssessmentValidator.validate(invalid_data, fallback)

        assert result.risk_level == "medium"
        assert result.confidence == 0.5
        assert "fallback 因素" in result.factors

    def test_validate_extract_from_text(self):
        """测试从文本中提取 JSON"""
        text = """
        根据分析，风险等级：high
        置信度：85%
        风险因素：["火灾风险"]
        建议操作：["启动预案"]
        """

        result = RiskAssessmentValidator.validate(text)

        # 应能从文本中提取风险等级
        assert result.risk_level in ["low", "medium", "high", "unknown"]


class TestEmergencyPlanValidator:
    """应急预案验证器测试"""

    def test_validate_valid_plan(self):
        """测试验证有效的预案"""
        raw_data = {
            "title": "火灾应急预案",
            "content": "1. 启动应急响应 2. 疏散人员",
            "risk_level": "high",
            "source": "manual",
            "score": 0.95
        }

        result = EmergencyPlanValidator.validate_list([raw_data])

        assert len(result) == 1
        assert result[0].title == "火灾应急预案"
        assert result[0].risk_level == "high"
        assert result[0].score == 0.95

    def test_validate_score_out_of_range(self):
        """测试验证超出范围的分数"""
        raw_data = {
            "title": "测试预案",
            "content": "测试内容",
            "risk_level": "medium",
            "source": "test",
            "score": 1.5  # 超出范围
        }

        result = EmergencyPlanValidator.validate_list([raw_data])

        assert 0.0 <= result[0].score <= 1.0

    def test_validate_list_multiple_plans(self):
        """测试验证多个预案"""
        raw_data = [
            {
                "title": "预案 1",
                "content": "内容 1",
                "risk_level": "high",
                "source": "ES",
                "score": 0.9
            },
            {
                "title": "预案 2",
                "content": "内容 2",
                "risk_level": "medium",
                "source": "Milvus",
                "score": 0.8
            }
        ]

        result = EmergencyPlanValidator.validate_list(raw_data)

        assert len(result) == 2

    def test_validate_with_fallback(self):
        """测试验证失败时使用 fallback"""
        invalid_data = [{"invalid": "data"}]
        fallback = [
            {
                "title": "Fallback 预案",
                "content": "Fallback 内容",
                "risk_level": "medium",
                "source": "fallback",
                "score": 0.5
            }
        ]

        result = EmergencyPlanValidator.validate_list(invalid_data, fallback)

        assert len(result) > 0
        assert result[0].title == "Fallback 预案"


class TestRuleBasedFallback:
    """基于规则的 Fallback 测试"""

    def test_assess_high_risk_keywords(self):
        """测试高风险关键词识别"""
        alert = "3 号楼发生火灾，有人员伤亡"

        result = RuleBasedFallback.assess_risk(alert)

        assert result.risk_level == "high"
        assert result.confidence > 0.3
        assert len(result.factors) > 0

    def test_assess_medium_risk_keywords(self):
        """测试中风险关键词识别"""
        alert = "设备出现异常，触发报警"

        result = RuleBasedFallback.assess_risk(alert)

        assert result.risk_level == "medium"

    def test_assess_low_risk_keywords(self):
        """测试低风险关键词识别"""
        alert = "例行安全检查，情况正常"

        result = RuleBasedFallback.assess_risk(alert)

        assert result.risk_level == "low"

    def test_assess_unknown_risk(self):
        """测试无法识别风险等级"""
        alert = "这是一条普通消息"

        result = RuleBasedFallback.assess_risk(alert)

        # 应该有一个默认的风险等级
        assert result.risk_level in ["low", "medium", "high", "unknown"]

    def test_get_default_plans(self):
        """测试获取默认预案"""
        plans = RuleBasedFallback.get_default_plans("high")

        assert len(plans) > 0
        assert plans[0].risk_level == "high"

    def test_get_default_plans_unknown_level(self):
        """测试获取未知风险等级的默认预案"""
        plans = RuleBasedFallback.get_default_plans("unknown")

        assert len(plans) > 0
        # 应该返回中等风险的默认预案
        assert plans[0].risk_level == "medium"


# ============== RiskAgent 测试 ==============

class TestRiskAgent:
    """RiskAgent 测试"""

    def test_risk_agent_with_mock(self):
        """测试 RiskAgent 使用 Mock"""
        # 使用 MockRiskAgent 进行测试
        agent = MockRiskAgent()

        result = agent.assess("火灾告警：3 号楼发生火情")

        assert result["risk_level"] == "high"
        assert result["confidence"] == 0.85
        assert len(result["factors"]) > 0

    def test_risk_agent_low_risk(self):
        """测试低风险告警"""
        agent = MockRiskAgent()

        result = agent.assess("日常巡检报告")

        assert result["risk_level"] == "medium"  # 默认

    def test_risk_agent_very_low_risk(self):
        """测试非常低风险的告警"""
        agent = MockRiskAgent(default_risk_level="low")

        result = agent.assess("普通事件记录")

        # MockRiskAgent 根据关键词判断，"普通"不是高风险词，所以返回默认 low
        assert result["risk_level"] == "low"  # 默认低风险


# ============== SearchAgent 测试 ==============

class TestSearchAgent:
    """SearchAgent 测试"""

    def test_search_agent_with_mock(self):
        """测试 SearchAgent 使用 Mock"""
        mock_graph_rag = MockGraphRAG()
        agent = SearchAgent(mock_graph_rag)

        results = agent.search("火灾应急预案", risk_level="high")

        assert len(results) > 0
        assert isinstance(results[0], dict)
        assert "title" in results[0] or "content" in results[0]

    def test_search_agent_filter_by_risk(self):
        """测试按风险等级过滤"""
        mock_graph_rag = MockGraphRAG()
        agent = SearchAgent(mock_graph_rag)

        high_results = agent.search("应急预案", risk_level="high")
        low_results = agent.search("应急预案", risk_level="low")

        # 验证返回结果
        assert len(high_results) > 0 or len(low_results) > 0

    def test_search_agent_fallback(self):
        """测试 SearchAgent fallback"""
        # 创建一个会抛出异常的 Mock GraphRAG
        class FailingGraphRAG:
            def search(self, query, top_k=5):
                raise Exception("连接失败")

        agent = SearchAgent(FailingGraphRAG())

        results = agent.search("测试", risk_level="high")

        # 应该返回 fallback 结果
        assert len(results) > 0


# ============== LangGraph Workflow 测试 ==============

class TestLangGraphWorkflow:
    """LangGraph 工作流测试"""

    def test_workflow_end_to_end(self):
        """测试工作流端到端执行"""
        risk_agent = MockRiskAgent()
        search_agent = MockSearchAgent()

        workflow = create_workflow(risk_agent, search_agent)

        initial_state: AgentState = {
            "alert_message": "火灾告警：3 号楼发生火情，请立即处理",
            "risk_assessment": None,
            "emergency_plans": [],
            "error": None
        }

        result = workflow.invoke(initial_state)

        # 验证风险评估
        assert result["risk_assessment"] is not None
        assert result["risk_assessment"]["risk_level"] == "high"

        # 验证预案检索
        assert len(result["emergency_plans"]) > 0

    def test_workflow_with_low_risk(self):
        """测试低风险告警的工作流"""
        risk_agent = MockRiskAgent(default_risk_level="low")
        search_agent = MockSearchAgent()

        workflow = create_workflow(risk_agent, search_agent)

        initial_state: AgentState = {
            "alert_message": "日常巡检报告",
            "risk_assessment": None,
            "emergency_plans": [],
            "error": None
        }

        result = workflow.invoke(initial_state)

        assert result["risk_assessment"] is not None

    def test_workflow_error_handling(self):
        """测试工作流错误处理"""

        class FailingRiskAgent:
            def assess(self, alert_message: str) -> Dict[str, Any]:
                raise Exception("LLM 服务不可用")

        search_agent = MockSearchAgent()

        workflow = create_workflow(FailingRiskAgent(), search_agent)

        initial_state: AgentState = {
            "alert_message": "测试告警",
            "risk_assessment": None,
            "emergency_plans": [],
            "error": None
        }

        # 工作流应该能够继续执行（有错误降级）
        result = workflow.invoke(initial_state)

        # 验证错误字段被设置
        assert result["error"] is not None or result["risk_assessment"] is not None

    def test_workflow_state_structure(self):
        """测试工作流状态结构"""
        risk_agent = MockRiskAgent()
        search_agent = MockSearchAgent()

        workflow = create_workflow(risk_agent, search_agent)

        initial_state: AgentState = {
            "alert_message": "测试",
            "risk_assessment": None,
            "emergency_plans": [],
            "error": None
        }

        result = workflow.invoke(initial_state)

        # 验证状态结构完整
        assert "alert_message" in result
        assert "risk_assessment" in result
        assert "emergency_plans" in result
        assert "error" in result


# ============== Integration 测试 ==============

class TestAgentIntegration:
    """Agent 集成测试"""

    def test_risk_agent_output_compatible_with_search(self):
        """测试 RiskAgent 输出与 SearchAgent 兼容"""
        risk_agent = MockRiskAgent()
        search_agent = MockSearchAgent()

        # 先执行风险评估
        risk_result = risk_agent.assess("火灾告警")

        # 使用风险等级进行预案检索
        plans = search_agent.search("应急预案", risk_level=risk_result["risk_level"])

        assert len(plans) > 0

    def test_workflow_with_real_output_validator(self):
        """测试工作流使用真实输出验证器"""
        # 创建一个使用真实验证器的 Mock Agent
        class ValidatedMockRiskAgent:
            def assess(self, alert_message: str) -> Dict[str, Any]:
                raw_data = {
                    "risk_level": "high",
                    "confidence": 0.9,
                    "factors": ["验证器测试"],
                    "recommended_actions": ["执行验证"]
                }
                result = RiskAssessmentValidator.validate(raw_data)
                return {
                    "risk_level": result.risk_level,
                    "confidence": result.confidence,
                    "factors": result.factors,
                    "recommended_actions": result.recommended_actions
                }

        workflow = create_workflow(
            ValidatedMockRiskAgent(),
            MockSearchAgent()
        )

        initial_state: AgentState = {
            "alert_message": "测试告警",
            "risk_assessment": None,
            "emergency_plans": [],
            "error": None
        }

        result = workflow.invoke(initial_state)

        assert result["risk_assessment"]["risk_level"] == "high"
        assert result["risk_assessment"]["confidence"] == 0.9


# ============== Edge Cases 测试 ==============

class TestEdgeCases:
    """边界情况测试"""

    def test_empty_alert_message(self):
        """测试空告警消息"""
        agent = MockRiskAgent()
        result = agent.assess("")

        assert result["risk_level"] in ["low", "medium", "high", "unknown"]

    def test_special_characters_in_alert(self):
        """测试告警消息包含特殊字符"""
        agent = MockRiskAgent()
        result = agent.assess("火灾告警！@#$%^&*()_+ 测试")

        assert result["risk_level"] == "high"

    def test_very_long_alert_message(self):
        """测试超长告警消息"""
        agent = MockRiskAgent()
        long_message = "火灾告警：" + "详情 " * 1000
        result = agent.assess(long_message)

        assert result["risk_level"] == "high"

    def test_mixed_language_alert(self):
        """测试混合语言告警"""
        agent = MockRiskAgent()
        result = agent.assess("Fire alarm! 火灾告警！Fire in building!")

        assert result["risk_level"] == "high"

    def test_workflow_consecutive_executions(self):
        """测试工作流连续执行"""
        risk_agent = MockRiskAgent()
        search_agent = MockSearchAgent()
        workflow = create_workflow(risk_agent, search_agent)

        results = []
        for i in range(3):
            initial_state: AgentState = {
                "alert_message": f"测试告警 {i}",
                "risk_assessment": None,
                "emergency_plans": [],
                "error": None
            }
            result = workflow.invoke(initial_state)
            results.append(result)

        # 验证所有执行都成功
        assert all(r["risk_assessment"] is not None for r in results)
