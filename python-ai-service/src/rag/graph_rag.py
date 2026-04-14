# python-ai-service/src/rag/graph_rag.py
"""GraphRAG 检索器 - 两路召回 + 重排序"""
from src.rag.es_search import ESSearcher
from src.rag.milvus_search import MilvusSearcher
from src.rag.reranker import BGEReranker
from src.core.logging import log


class GraphRAGSearcher:
    """GraphRAG 检索器 - 两路召回 + 重排序"""

    def __init__(self):
        self.es_searcher = ESSearcher()
        self.milvus_searcher = MilvusSearcher()
        self.reranker = BGEReranker()
        log.info("GraphRAG 检索器初始化完成")

    def search(self, query: str, event_type: str = None, top_k: int = 5) -> list:
        """
        三路召回检索

        1. ES BM25 文本检索
        2. Milvus 向量相似度检索
        3. 合并去重
        4. BGE-Reranker 重排序

        Args:
            query: 查询文本
            event_type: 事件类型（如 fire, gas_leak）
            top_k: 返回结果数量

        Returns:
            重排序后的 Top-K 结果
        """
        # 1. ES BM25 召回
        es_results = self.es_searcher.search(query, event_type, top_k=20)
        log.debug(f"ES 返回 {len(es_results)} 条结果")

        # 2. Milvus 向量召回
        milvus_results = self.milvus_searcher.search(query, top_k=20)
        log.debug(f"Milvus 返回 {len(milvus_results)} 条结果")

        # 3. 合并去重（按 content 去重）
        all_results = self._merge_results(es_results, milvus_results)
        log.debug(f"合并后 {len(all_results)} 条结果")

        # 4. BGE-Reranker 重排序
        documents = [r["content"] for r in all_results]
        reranked = self.reranker.rerank(query, documents, top_k=top_k)

        log.info(f"GraphRAG 检索完成，返回 {len(reranked)} 条结果")
        return reranked

    def _merge_results(self, es_results: list, milvus_results: list) -> list:
        """合并并去重检索结果"""
        seen = {}

        # 先添加 ES 结果
        for result in es_results:
            content = result["content"]
            if content not in seen:
                seen[content] = result

        # 再添加 Milvus 结果（不重复的）
        for result in milvus_results:
            content = result["content"]
            if content not in seen:
                seen[content] = result

        return list(seen.values())
