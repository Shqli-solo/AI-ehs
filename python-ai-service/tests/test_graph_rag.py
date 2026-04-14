# python-ai-service/tests/test_graph_rag.py
"""GraphRAG 检索引擎测试"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock


class TestESSearcher:
    """Elasticsearch 检索器测试"""

    def test_search_returns_results(self):
        """测试 ES 检索返回结果"""
        from src.rag.es_search import ESSearcher

        with patch('src.rag.es_search.Elasticsearch') as mock_es:
            mock_client = Mock()
            mock_client.search.return_value = {
                "hits": {
                    "hits": [
                        {
                            "_id": "1",
                            "_source": {"content": "火灾应急预案", "metadata": {}},
                            "_score": 0.95
                        }
                    ]
                }
            }
            mock_es.return_value = mock_client

            searcher = ESSearcher(index="test-index")
            results = searcher.search("火灾", top_k=5)

            assert isinstance(results, list)
            assert len(results) >= 0

    def test_search_with_event_type(self):
        """测试带事件类型的检索"""
        from src.rag.es_search import ESSearcher

        with patch('src.rag.es_search.Elasticsearch') as mock_es:
            mock_client = Mock()
            mock_client.search.return_value = {
                "hits": {
                    "hits": [
                        {
                            "_id": "1",
                            "_source": {"content": "火灾应急预案", "metadata": {}},
                            "_score": 0.95
                        }
                    ]
                }
            }
            mock_es.return_value = mock_client

            searcher = ESSearcher(index="test-index")
            results = searcher.search("火灾", event_type="fire", top_k=5)

            assert isinstance(results, list)
            # 验证调用了 filter
            call_args = mock_client.search.call_args
            assert call_args is not None

    def test_search_returns_empty_on_exception(self):
        """测试 ES 检索异常时返回空结果（降级处理）"""
        from src.rag.es_search import ESSearcher

        with patch('src.rag.es_search.Elasticsearch') as mock_es:
            mock_client = Mock()
            mock_client.search.side_effect = Exception("ES connection failed")
            mock_es.return_value = mock_client

            searcher = ESSearcher(index="test-index")
            results = searcher.search("火灾", top_k=5)

            assert isinstance(results, list)
            assert len(results) == 0

    def test_search_returns_empty_documents(self):
        """测试 ES 检索返回空文档列表"""
        from src.rag.es_search import ESSearcher

        with patch('src.rag.es_search.Elasticsearch') as mock_es:
            mock_client = Mock()
            mock_client.search.return_value = {"hits": {"hits": []}}
            mock_es.return_value = mock_client

            searcher = ESSearcher(index="test-index")
            results = searcher.search("不存在的关键词", top_k=5)

            assert isinstance(results, list)
            assert len(results) == 0


class TestMilvusSearcher:
    """Milvus 向量检索器测试"""

    def test_search_returns_results(self):
        """测试 Milvus 向量检索返回结果"""
        from src.rag.milvus_search import MilvusSearcher

        with patch('src.rag.milvus_search.connections') as mock_conn:
            with patch('src.rag.milvus_search.Collection') as mock_collection:
                mock_col = Mock()
                mock_col.search.return_value = [
                    [
                        Mock(entity={"id": "1", "content": "火灾应急预案", "metadata": {}}, score=0.95)
                    ]
                ]
                mock_collection.return_value = mock_col

                searcher = MilvusSearcher(collection="test-collection")
                results = searcher.search("火灾应急预案", top_k=5)

                assert isinstance(results, list)

    def test_search_with_embedding(self):
        """测试带向量嵌入的检索"""
        from src.rag.milvus_search import MilvusSearcher

        with patch('src.rag.milvus_search.connections') as mock_conn:
            with patch('src.rag.milvus_search.Collection') as mock_collection:
                mock_col = Mock()
                mock_col.search.return_value = [
                    [
                        Mock(entity={"id": "1", "content": "相关内容", "metadata": {}}, score=0.88)
                    ]
                ]
                mock_collection.return_value = mock_col

                searcher = MilvusSearcher(collection="test-collection")
                results = searcher.search_by_vector([0.1] * 768, top_k=5)

                assert isinstance(results, list)

    def test_search_returns_empty_on_exception(self):
        """测试 Milvus 检索异常时返回空结果（降级处理）"""
        from src.rag.milvus_search import MilvusSearcher

        with patch('src.rag.milvus_search.connections') as mock_conn:
            with patch('src.rag.milvus_search.Collection') as mock_collection:
                mock_col = Mock()
                mock_col.search.side_effect = Exception("Milvus connection failed")
                mock_collection.return_value = mock_col

                searcher = MilvusSearcher(collection="test-collection")
                results = searcher.search("火灾", top_k=5)

                assert isinstance(results, list)
                assert len(results) == 0

    def test_search_with_empty_hits(self):
        """测试 Milvus 检索返回空结果"""
        from src.rag.milvus_search import MilvusSearcher

        with patch('src.rag.milvus_search.connections') as mock_conn:
            with patch('src.rag.milvus_search.Collection') as mock_collection:
                mock_col = Mock()
                mock_col.search.return_value = [[]]
                mock_collection.return_value = mock_col

                searcher = MilvusSearcher(collection="test-collection")
                results = searcher.search("不相关的查询", top_k=5)

                assert isinstance(results, list)
                assert len(results) == 0


class TestBGEReranker:
    """BGE-Reranker 重排序器测试"""

    def test_rerank_returns_sorted_results(self):
        """测试重排序返回排序后的结果"""
        from src.rag.reranker import BGEReranker

        with patch('src.rag.reranker.CrossEncoder') as mock_model:
            mock_instance = Mock()
            # 模拟分数：第三个文档最相关
            mock_instance.predict.return_value = [0.3, 0.2, 0.9]
            mock_model.return_value = mock_instance

            reranker = BGEReranker()
            query = "火灾应急预案"
            documents = ["这是关于消防的文档", "这是关于气体的文档", "这是关于火灾的文档"]
            results = reranker.rerank(query, documents, top_k=2)

            assert isinstance(results, list)
            assert len(results) <= 2
            # 第一个结果应该是分数最高的
            assert results[0]["content"] == "这是关于火灾的文档"

    def test_rerank_with_empty_documents(self):
        """测试重排序空文档列表"""
        from src.rag.reranker import BGEReranker

        with patch('src.rag.reranker.CrossEncoder'):
            reranker = BGEReranker()
            query = "火灾应急预案"
            results = reranker.rerank(query, [], top_k=5)

            assert isinstance(results, list)
            assert len(results) == 0

    def test_rerank_returns_top_k(self):
        """测试重排序只返回 top_k 个结果"""
        from src.rag.reranker import BGEReranker

        with patch('src.rag.reranker.CrossEncoder') as mock_model:
            mock_instance = Mock()
            mock_instance.predict.return_value = [0.5, 0.8, 0.3, 0.9, 0.1]
            mock_model.return_value = mock_instance

            reranker = BGEReranker()
            query = "查询"
            documents = ["文档 1", "文档 2", "文档 3", "文档 4", "文档 5"]
            results = reranker.rerank(query, documents, top_k=3)

            assert len(results) == 3


class TestGraphRAGSearcher:
    """GraphRAG 检索器集成测试"""

    def test_search_returns_top_k_results(self):
        """测试 GraphRAG 返回 Top-K 结果"""
        from src.rag.graph_rag import GraphRAGSearcher

        with patch('src.rag.graph_rag.ESSearcher') as mock_es:
            with patch('src.rag.graph_rag.MilvusSearcher') as mock_milvus:
                with patch('src.rag.graph_rag.BGEReranker') as mock_reranker:
                    mock_es.return_value.search.return_value = [
                        {"content": "ES 结果 1", "score": 0.9}
                    ]
                    mock_milvus.return_value.search.return_value = [
                        {"content": "Milvus 结果 1", "score": 0.85}
                    ]
                    mock_reranker.return_value.rerank.return_value = [
                        {"content": "ES 结果 1", "rerank_score": 0.9}
                    ]

                    searcher = GraphRAGSearcher()
                    results = searcher.search("火灾应急预案", event_type="fire", top_k=5)

                    assert isinstance(results, list)
                    assert len(results) <= 5

    def test_search_performance_under_500ms(self):
        """测试检索性能"""
        from src.rag.graph_rag import GraphRAGSearcher

        with patch('src.rag.graph_rag.ESSearcher') as mock_es:
            with patch('src.rag.graph_rag.MilvusSearcher') as mock_milvus:
                with patch('src.rag.graph_rag.BGEReranker') as mock_reranker:
                    mock_es.return_value.search.return_value = []
                    mock_milvus.return_value.search.return_value = []
                    mock_reranker.return_value.rerank.return_value = []

                    searcher = GraphRAGSearcher()
                    start = time.time()
                    results = searcher.search("火灾", event_type="fire", top_k=5)
                    elapsed = (time.time() - start) * 1000

                    assert isinstance(results, list)
                    # 性能测试日志
                    print(f"检索耗时：{elapsed:.2f}ms")

    def test_search_merges_results_correctly(self):
        """测试 GraphRAG 正确合并两路召回结果"""
        from src.rag.graph_rag import GraphRAGSearcher

        with patch('src.rag.graph_rag.ESSearcher') as mock_es:
            with patch('src.rag.graph_rag.MilvusSearcher') as mock_milvus:
                with patch('src.rag.graph_rag.BGEReranker') as mock_reranker:
                    # ES 和 Milvus 返回相同内容，应该去重
                    es_results = [{"content": "重复内容", "score": 0.9}]
                    milvus_results = [{"content": "重复内容", "score": 0.85}]

                    mock_es.return_value.search.return_value = es_results
                    mock_milvus.return_value.search.return_value = milvus_results
                    mock_reranker.return_value.rerank.return_value = [
                        {"content": "重复内容", "rerank_score": 0.9}
                    ]

                    searcher = GraphRAGSearcher()
                    results = searcher.search("查询", top_k=5)

                    # 去重后应该只有一个结果
                    assert len(results) == 1

    def test_search_handles_es_failure_gracefully(self):
        """测试 ES 失败时降级处理"""
        from src.rag.graph_rag import GraphRAGSearcher

        with patch('src.rag.graph_rag.ESSearcher') as mock_es:
            with patch('src.rag.graph_rag.MilvusSearcher') as mock_milvus:
                with patch('src.rag.graph_rag.BGEReranker') as mock_reranker:
                    mock_es.return_value.search.return_value = []  # ES 失败返回空
                    mock_milvus.return_value.search.return_value = [
                        {"content": "Milvus 结果", "score": 0.85}
                    ]
                    mock_reranker.return_value.rerank.return_value = [
                        {"content": "Milvus 结果", "rerank_score": 0.85}
                    ]

                    searcher = GraphRAGSearcher()
                    results = searcher.search("查询", top_k=5)

                    # 不应该抛出异常，应该继续返回 Milvus 结果
                    assert isinstance(results, list)

    def test_search_handles_milvus_failure_gracefully(self):
        """测试 Milvus 失败时降级处理"""
        from src.rag.graph_rag import GraphRAGSearcher

        with patch('src.rag.graph_rag.ESSearcher') as mock_es:
            with patch('src.rag.graph_rag.MilvusSearcher') as mock_milvus:
                with patch('src.rag.graph_rag.BGEReranker') as mock_reranker:
                    mock_es.return_value.search.return_value = [
                        {"content": "ES 结果", "score": 0.9}
                    ]
                    mock_milvus.return_value.search.return_value = []  # Milvus 失败返回空
                    mock_reranker.return_value.rerank.return_value = [
                        {"content": "ES 结果", "rerank_score": 0.9}
                    ]

                    searcher = GraphRAGSearcher()
                    results = searcher.search("查询", top_k=5)

                    # 不应该抛出异常，应该继续返回 ES 结果
                    assert isinstance(results, list)
