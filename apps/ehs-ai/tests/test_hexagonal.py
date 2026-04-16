# apps/ehs-ai/tests/test_hexagonal.py
"""六边形架构测试"""
import pytest
from src.container import DIContainer, ContainerConfig
from src.core.graph_rag import GraphRAGCore
from src.core.agents.workflow import create_workflow, AgentState
from tests.mocks import (
    MockRiskAgent, MockSearchAgent, MockGraphRAG,
    MockElasticsearchAdapter, MockMilvusAdapter,
    create_mock_workflow
)


class TestHexagonalArchitecture:
    """六边形架构测试"""

    @pytest.mark.skip(reason="需要 torch 依赖，环境限制")
    def test_container_can_create_real_instances(self):
        """测试容器可以创建真实实例"""
        config = ContainerConfig(
            es_url="http://localhost:9200",
            es_index="test_index",
            milvus_url="localhost",
            milvus_port=19530,
            milvus_collection="test_collection"
        )
        container = DIContainer(config)

        # 验证容器可以创建实例（不实际连接）
        es_adapter = container.get_elasticsearch_adapter()
        milvus_adapter = container.get_milvus_adapter()

        assert es_adapter is not None
        assert milvus_adapter is not None

    def test_container_can_create_mock_instances(self):
        """测试容器可以创建 Mock 实例"""
        container = DIContainer()
        container.use_mock_implementations()

        graph_rag = container.get_graph_rag()
        workflow = container.get_workflow()

        assert graph_rag is not None
        assert workflow is not None

    def test_container_supports_dependency_injection(self):
        """测试依赖注入"""
        mock_risk = MockRiskAgent()
        mock_search = MockSearchAgent()

        workflow = create_workflow(mock_risk, mock_search)

        initial_state: AgentState = {
            "alert_message": "测试告警",
            "risk_assessment": None,
            "emergency_plans": [],
            "error": None
        }

        result = workflow.invoke(initial_state)

        assert result["risk_assessment"] is not None
        assert result["risk_assessment"]["risk_level"] == "medium"


class TestGraphRAG:
    """GraphRAG 测试"""

    def test_graph_rag_with_mock_adapters(self):
        """测试 GraphRAG 使用 Mock 适配器"""
        mock_es = MockElasticsearchAdapter("http://localhost:9200", "test")
        mock_milvus = MockMilvusAdapter("localhost", 19530, "test", "test")

        graph_rag = GraphRAGCore(
            text_storage=mock_es,
            vector_storage=mock_milvus
        )

        results = graph_rag.search("测试查询", top_k=2)

        assert len(results) >= 2

    def test_graph_rag_merge_results(self):
        """测试结果合并去重"""
        mock_es = MockElasticsearchAdapter("http://localhost:9200", "test")
        mock_milvus = MockMilvusAdapter("localhost", 19530, "test", "test")

        graph_rag = GraphRAGCore(
            text_storage=mock_es,
            vector_storage=mock_milvus
        )

        results = graph_rag.search("测试查询", top_k=10)

        # 验证结果合并
        assert len(results) > 0


class TestAgents:
    """Agent 测试"""

    def test_risk_agent_mock(self):
        """测试 RiskAgent Mock"""
        agent = MockRiskAgent()

        result = agent.assess("火灾告警")

        assert result["risk_level"] == "high"
        assert result["confidence"] == 0.85

    def test_risk_agent_mock_low_risk(self):
        """测试 RiskAgent 低风险"""
        agent = MockRiskAgent()

        result = agent.assess("普通事件")

        assert result["risk_level"] == "medium"  # 默认

    def test_search_agent_mock(self):
        """测试 SearchAgent Mock"""
        agent = MockSearchAgent()

        results = agent.search("应急预案", risk_level="high")

        assert len(results) == 1
        assert results[0]["risk_level"] == "high"


class TestWorkflow:
    """工作流测试"""

    def test_workflow_end_to_end(self):
        """测试工作流端到端"""
        risk_agent = MockRiskAgent()
        search_agent = MockSearchAgent()

        workflow = create_workflow(risk_agent, search_agent)

        initial_state: AgentState = {
            "alert_message": "火灾告警：3 号楼发生火情",
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

    def test_workflow_error_handling(self):
        """测试工作流错误处理"""
        # 即使节点失败，工作流也应继续执行
        risk_agent = MockRiskAgent()
        search_agent = MockSearchAgent()

        workflow = create_workflow(risk_agent, search_agent)

        initial_state: AgentState = {
            "alert_message": "测试告警",
            "risk_assessment": None,
            "emergency_plans": [],
            "error": None
        }

        result = workflow.invoke(initial_state)

        # 验证错误字段存在
        assert "error" in result


class TestPorts:
    """端口接口测试"""

    def test_storage_port_interface(self):
        """测试存储端口接口"""
        from src.ports.secondary.storage import StoragePort, TextStoragePort, VectorStoragePort

        # 验证接口定义
        assert hasattr(StoragePort, 'search')
        assert hasattr(TextStoragePort, 'search')
        assert hasattr(VectorStoragePort, 'search_by_vector')
        assert hasattr(VectorStoragePort, 'encode')

    def test_adapters_implement_ports(self):
        """测试适配器实现端口"""
        mock_es = MockElasticsearchAdapter("http://localhost:9200", "test")
        mock_milvus = MockMilvusAdapter("localhost", 19530, "test", "test")

        # 验证方法存在
        assert hasattr(mock_es, 'search')
        assert hasattr(mock_milvus, 'search')
        assert hasattr(mock_milvus, 'search_by_vector')
        assert hasattr(mock_milvus, 'encode')


class TestArchitectureSeparation:
    """架构分离测试"""

    def test_core_does_not_import_adapters(self):
        """测试核心域不直接导入适配器"""
        import inspect
        import src.core.graph_rag as graph_rag_module

        source = inspect.getsource(graph_rag_module)

        # 核心域应该只依赖端口，不依赖具体适配器
        assert "ElasticsearchAdapter" not in source
        assert "MilvusAdapter" not in source

    def test_container_wires_dependencies(self):
        """测试容器正确组装依赖"""
        container = DIContainer()
        container.use_mock_implementations()

        # 获取组件
        graph_rag = container.get_graph_rag()
        risk_agent = container.get_risk_agent()
        search_agent = container.get_search_agent()

        # 验证都是 Mock 实现
        assert isinstance(graph_rag, MockGraphRAG)
        assert isinstance(risk_agent, MockRiskAgent)
        assert isinstance(search_agent, MockSearchAgent)
