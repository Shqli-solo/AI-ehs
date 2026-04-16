# apps/ehs-ai/src/container.py
"""依赖注入容器 - 六边形架构核心"""
from typing import Optional, Any
from dataclasses import dataclass

from src.core.config import settings


@dataclass
class ContainerConfig:
    """容器配置"""
    # Elasticsearch
    es_url: str = "http://localhost:9200"
    es_index: str = "ehs_plans"

    # Milvus
    milvus_url: str = "localhost"
    milvus_port: int = 19530
    milvus_collection: str = "ehs_plans"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"

    # LLM
    llm_endpoint: str = "http://localhost:8080/v1/chat/completions"

    # Reranker
    reranker_model: str = "BAAI/bge-reranker-base"


class DIContainer:
    """
    依赖注入容器

    职责：
    1. 注册和管理所有依赖
    2. 支持 Mock/真实实现切换
    3. 提供单一获取入口

    使用示例：
    ```python
    # 使用真实实现
    container = DIContainer()
    container.use_real_implementations()

    # 或使用 Mock
    container = DIContainer()
    container.use_mock_implementations()

    # 获取服务
    graph_rag = container.get_graph_rag()
    workflow = container.get_workflow()
    ```
    """

    def __init__(self, config: Optional[ContainerConfig] = None):
        """初始化容器"""
        self._config = config or ContainerConfig()
        self._instances = {}
        self._use_mock = False

    def use_real_implementations(self):
        """使用真实实现"""
        self._use_mock = False
        return self

    def use_mock_implementations(self):
        """使用 Mock 实现"""
        self._use_mock = True
        return self

    def get_graph_rag(self):
        """获取 GraphRAG 实例"""
        if "graph_rag" not in self._instances:
            if self._use_mock:
                from tests.mocks import MockGraphRAG
                self._instances["graph_rag"] = MockGraphRAG()
            else:
                from src.core.graph_rag import GraphRAGCore
                from src.adapters.secondary.elasticsearch import ElasticsearchAdapter
                from src.adapters.secondary.milvus import MilvusAdapter

                es_adapter = ElasticsearchAdapter(
                    url=self._config.es_url,
                    index=self._config.es_index
                )

                milvus_adapter = MilvusAdapter(
                    url=self._config.milvus_url,
                    port=self._config.milvus_port,
                    collection=self._config.milvus_collection,
                    embedding_model=self._config.embedding_model
                )

                self._instances["graph_rag"] = GraphRAGCore(
                    text_storage=es_adapter,
                    vector_storage=milvus_adapter
                )

        return self._instances["graph_rag"]

    def get_workflow(self):
        """获取工作流实例"""
        if "workflow" not in self._instances:
            if self._use_mock:
                from tests.mocks import MockRiskAgent, MockSearchAgent, create_mock_workflow
                risk_agent = MockRiskAgent()
                search_agent = MockSearchAgent()
                self._instances["workflow"] = create_mock_workflow(risk_agent, search_agent)
            else:
                from src.core.agents.workflow import create_workflow, RiskAgentPort, SearchAgentPort
                from src.core.agents.risk_agent import RiskAgent
                from src.core.agents.search_agent import SearchAgent

                risk_agent = RiskAgent(llm_endpoint=self._config.llm_endpoint)
                search_agent = SearchAgent(graph_rag=self.get_graph_rag())

                self._instances["workflow"] = create_workflow(
                    risk_agent=risk_agent,
                    search_agent=search_agent
                )

        return self._instances["workflow"]

    def get_risk_agent(self):
        """获取 RiskAgent 实例"""
        if "risk_agent" not in self._instances:
            if self._use_mock:
                from tests.mocks import MockRiskAgent
                self._instances["risk_agent"] = MockRiskAgent()
            else:
                from src.core.agents.risk_agent import RiskAgent
                self._instances["risk_agent"] = RiskAgent(
                    llm_endpoint=self._config.llm_endpoint
                )

        return self._instances["risk_agent"]

    def get_search_agent(self):
        """获取 SearchAgent 实例"""
        if "search_agent" not in self._instances:
            if self._use_mock:
                from tests.mocks import MockSearchAgent
                self._instances["search_agent"] = MockSearchAgent()
            else:
                from src.core.agents.search_agent import SearchAgent
                self._instances["search_agent"] = SearchAgent(
                    graph_rag=self.get_graph_rag()
                )

        return self._instances["search_agent"]

    def get_elasticsearch_adapter(self):
        """获取 Elasticsearch 适配器"""
        if "es_adapter" not in self._instances:
            from src.adapters.secondary.elasticsearch import ElasticsearchAdapter
            self._instances["es_adapter"] = ElasticsearchAdapter(
                url=self._config.es_url,
                index=self._config.es_index
            )
        return self._instances["es_adapter"]

    def get_milvus_adapter(self):
        """获取 Milvus 适配器"""
        if "milvus_adapter" not in self._instances:
            from src.adapters.secondary.milvus import MilvusAdapter
            self._instances["milvus_adapter"] = MilvusAdapter(
                url=self._config.milvus_url,
                port=self._config.milvus_port,
                collection=self._config.milvus_collection,
                embedding_model=self._config.embedding_model
            )
        return self._instances["milvus_adapter"]

    def clear(self):
        """清除所有缓存实例"""
        self._instances.clear()


# 全局单例
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """获取全局容器实例"""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def reset_container():
    """重置容器（用于测试）"""
    global _container
    _container = None
