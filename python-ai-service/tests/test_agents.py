# python-ai-service/tests/test_agents.py
"""Multi-Agent 编排测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestRiskAgent:
    """风险感知 Agent 测试"""

    def test_assess_fire_alert(self):
        """测试火灾告警风险评估"""
        from src.agents.risk_agent import RiskAgent

        with patch('src.agents.risk_agent.httpx.Client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "risk_level": "high",
                "confidence": 0.92,
                "factors": ["烟雾浓度超标", "温度异常升高"],
                "recommended_actions": ["启动消防泵", "疏散人员"]
            }
            mock_response.status_code = 200
            mock_client.return_value.post.return_value = mock_response

            agent = RiskAgent()
            result = agent.assess("烟雾浓度超标，温度异常升高")

            assert isinstance(result, dict)
            assert result["risk_level"] in ["low", "medium", "high"]
            assert "confidence" in result
            assert "factors" in result

    def test_assess_returns_structured_result(self):
        """测试返回结构化结果"""
        from src.agents.risk_agent import RiskAgent
        from src.agents.risk_agent import RiskAssessment

        with patch('src.agents.risk_agent.httpx.Client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "risk_level": "medium",
                "confidence": 0.85,
                "factors": ["设备温度偏高"],
                "recommended_actions": ["继续监控"]
            }
            mock_response.status_code = 200
            mock_client.return_value.post.return_value = mock_response

            agent = RiskAgent()
            result = agent.assess("设备温度偏高")

            # 验证返回结构
            assert "risk_level" in result
            assert "confidence" in result
            assert "factors" in result
            assert "recommended_actions" in result

    def test_assess_handles_llm_non_json_response(self):
        """测试 LLM 非 JSON 响应时的 fallback 处理"""
        from src.agents.risk_agent import RiskAgent

        with patch('src.agents.risk_agent.httpx.Client') as mock_client:
            # 模拟 LLM 返回非 JSON 文本
            mock_response = Mock()
            mock_response.text = "根据分析，这是一个高风险情况，风险等级：high"
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_client.return_value.post.return_value = mock_response

            agent = RiskAgent()
            result = agent.assess("高风险情况")

            # 验证 fallback 后仍有合理返回
            assert isinstance(result, dict)
            assert "risk_level" in result

    def test_assess_returns_default_on_error(self):
        """测试异常时返回默认值（降级处理）"""
        from src.agents.risk_agent import RiskAgent

        with patch('src.agents.risk_agent.httpx.Client') as mock_client:
            mock_client.return_value.post.side_effect = Exception("Connection failed")

            agent = RiskAgent()
            result = agent.assess("测试告警")

            # 验证异常时返回默认值
            assert isinstance(result, dict)
            assert result["risk_level"] == "unknown"
            assert result["confidence"] == 0.0


class TestSearchAgent:
    """预案检索 Agent 测试"""

    def test_search_returns_plan(self):
        """测试预案检索返回结果"""
        from src.agents.search_agent import SearchAgent

        with patch('src.agents.search_agent.GraphRAGSearcher') as mock_searcher:
            mock_searcher.return_value.search.return_value = [
                {
                    "content": "火灾应急预案：1.启动消防泵 2.疏散人员 3.通知消防队",
                    "score": 0.95,
                    "metadata": {"event_type": "fire", "risk_level": "high"}
                }
            ]

            agent = SearchAgent()
            result = agent.search("火灾应急预案")

            assert isinstance(result, list)
            assert len(result) > 0
            assert "content" in result[0]

    def test_search_with_risk_filter(self):
        """测试风险等级过滤"""
        from src.agents.search_agent import SearchAgent

        with patch('src.agents.search_agent.GraphRAGSearcher') as mock_searcher:
            mock_searcher.return_value.search.return_value = [
                {
                    "content": "高风险预案内容",
                    "score": 0.95,
                    "metadata": {"risk_level": "high"}
                },
                {
                    "content": "低风险预案内容",
                    "score": 0.85,
                    "metadata": {"risk_level": "low"}
                }
            ]

            agent = SearchAgent()
            result = agent.search("预案", risk_level="high")

            # 验证只返回高风险预案
            assert all(r["metadata"].get("risk_level") == "high" for r in result)

    def test_search_returns_empty_on_error(self):
        """测试异常时返回空列表（降级处理）"""
        from src.agents.search_agent import SearchAgent

        with patch('src.agents.search_agent.GraphRAGSearcher') as mock_searcher:
            mock_searcher.return_value.search.side_effect = Exception("Search failed")

            agent = SearchAgent()
            result = agent.search("测试查询")

            assert isinstance(result, list)
            assert len(result) == 0


class TestAgentWorkflow:
    """LangGraph 工作流测试"""

    def test_workflow_executes_sequentially(self):
        """测试工作流顺序执行：风险感知 → 预案检索"""
        from src.agents.workflow import create_workflow, AgentState

        with patch('src.agents.workflow.RiskAgent') as mock_risk:
            with patch('src.agents.workflow.SearchAgent') as mock_search:
                mock_risk.return_value.assess.return_value = {
                    "risk_level": "high",
                    "confidence": 0.9,
                    "factors": ["烟雾浓度超标"],
                    "recommended_actions": ["启动预案"]
                }
                mock_search.return_value.search.return_value = [
                    {"content": "火灾应急预案", "score": 0.95}
                ]

                workflow = create_workflow()
                initial_state: AgentState = {
                    "alert_message": "烟雾浓度超标",
                    "risk_assessment": None,
                    "emergency_plans": [],
                    "error": None
                }

                result = workflow.invoke(initial_state)

                # 验证顺序执行
                assert result["risk_assessment"] is not None
                assert result["emergency_plans"] is not None
                assert len(result["emergency_plans"]) > 0

    def test_workflow_handles_errors(self):
        """测试工作流错误处理"""
        from src.agents.workflow import create_workflow, AgentState

        with patch('src.agents.workflow.RiskAgent') as mock_risk:
            mock_risk.return_value.assess.side_effect = Exception("RiskAgent failed")

            workflow = create_workflow()
            initial_state: AgentState = {
                "alert_message": "测试告警",
                "risk_assessment": None,
                "emergency_plans": [],
                "error": None
            }

            result = workflow.invoke(initial_state)

            # 验证错误被捕获并记录
            assert result["error"] is not None or result["risk_assessment"] is not None

    def test_workflow_state_validation(self):
        """测试 AgentState 类型验证"""
        from src.agents.workflow import AgentState

        # 验证 TypedDict 结构
        state: AgentState = {
            "alert_message": "测试",
            "risk_assessment": None,
            "emergency_plans": [],
            "error": None
        }

        assert "alert_message" in state
        assert "risk_assessment" in state
        assert "emergency_plans" in state
        assert "error" in state
