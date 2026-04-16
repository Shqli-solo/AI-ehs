# apps/ehs-ai/tests/mocks.py
"""Mock 实现 - 用于测试"""
from typing import Optional, List, Dict, Any

from src.core.agents.workflow import RiskAgentPort, SearchAgentPort, create_workflow, AgentState


class MockRiskAgent(RiskAgentPort):
    """Mock 风险感知 Agent"""

    def __init__(self, default_risk_level: str = "medium"):
        self.default_risk_level = default_risk_level

    def assess(self, alert_message: str) -> Dict[str, Any]:
        """Mock 风险评估"""
        # 简单规则：根据关键词判断风险
        if any(kw in alert_message for kw in ["火灾", "爆炸", "严重"]):
            risk_level = "high"
        elif any(kw in alert_message for kw in ["泄漏", "异常"]):
            risk_level = "medium"
        else:
            risk_level = self.default_risk_level

        return {
            "risk_level": risk_level,
            "confidence": 0.85,
            "factors": ["基于关键词分析"],
            "recommended_actions": ["启动相应应急预案"]
        }


class MockSearchAgent(SearchAgentPort):
    """Mock 预案检索 Agent"""

    def __init__(self):
        self._mock_plans = {
            "high": [
                {
                    "title": "重大事故应急预案",
                    "content": "1. 立即启动应急响应 2. 疏散人员 3. 通知相关部门",
                    "risk_level": "high",
                    "source": "Mock",
                    "score": 0.95
                }
            ],
            "medium": [
                {
                    "title": "中等风险应急预案",
                    "content": "1. 启动预案 2. 组织处置 3. 持续监控",
                    "risk_level": "medium",
                    "source": "Mock",
                    "score": 0.90
                }
            ],
            "low": [
                {
                    "title": "低风险处置流程",
                    "content": "1. 记录事件 2. 常规处置 3. 事后总结",
                    "risk_level": "low",
                    "source": "Mock",
                    "score": 0.85
                }
            ]
        }

    def search(self, query: str, risk_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mock 预案检索"""
        if risk_level and risk_level in self._mock_plans:
            return self._mock_plans[risk_level]
        return self._mock_plans.get("medium", [])


class MockGraphRAG:
    """Mock GraphRAG"""

    def __init__(self):
        self._mock_results = [
            {
                "id": "plan-001",
                "content": "火灾事故专项应急预案",
                "score": 0.95,
                "metadata": {"risk_level": "high", "source": "ES"}
            },
            {
                "id": "plan-002",
                "content": "气体泄漏应急处置流程",
                "score": 0.90,
                "metadata": {"risk_level": "medium", "source": "Milvus"}
            }
        ]

    def search(self, query: str, event_type: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Mock 检索"""
        return self._mock_results[:top_k]


class MockElasticsearchAdapter:
    """Mock Elasticsearch 适配器"""

    def __init__(self, url: str, index: str):
        pass

    def search(self, query: str, event_type: Optional[str] = None, top_k: int = 20) -> List[Dict[str, Any]]:
        return [
            {"id": "es-1", "content": "ES 结果 1", "score": 0.9, "metadata": {}},
            {"id": "es-2", "content": "ES 结果 2", "score": 0.8, "metadata": {}}
        ]


class MockMilvusAdapter:
    """Mock Milvus 适配器"""

    def __init__(self, url: str, port: int, collection: str, embedding_model: str):
        pass

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        return [
            {"id": "milvus-1", "content": "Milvus 结果 1", "score": 0.92, "metadata": {}},
            {"id": "milvus-2", "content": "Milvus 结果 2", "score": 0.85, "metadata": {}}
        ]

    def search_by_vector(self, embedding: List[float], top_k: int = 20) -> List[Dict[str, Any]]:
        return self.search("", top_k)

    def encode(self, text: str) -> List[float]:
        return [0.1] * 768


def create_mock_workflow(
    risk_agent: Optional[RiskAgentPort] = None,
    search_agent: Optional[SearchAgentPort] = None
):
    """创建 Mock 工作流"""
    if risk_agent is None:
        risk_agent = MockRiskAgent()
    if search_agent is None:
        search_agent = MockSearchAgent()
    return create_workflow(risk_agent, search_agent)
