# python-ai-service/src/rag/reranker.py
"""BGE-Reranker 重排序器"""
from sentence_transformers import CrossEncoder
from src.core.logging import log
from src.core.config import settings


class BGEReranker:
    """BGE-Reranker 重排序器"""

    def __init__(self):
        self.model = CrossEncoder(settings.RERANK_MODEL)
        log.info("BGE-Reranker 初始化完成")

    def rerank(self, query: str, documents: list, top_k: int = 5) -> list:
        """
        对检索结果进行重排序

        Args:
            query: 查询文本
            documents: 待排序的文档列表
            top_k: 返回结果数量

        Returns:
            重排序后的结果
        """
        if not documents:
            return []

        # 构建评分对
        pairs = [[query, doc] for doc in documents]

        # 获取重排序分数
        scores = self.model.predict(pairs)

        # 组合结果
        results = [
            {"content": doc, "rerank_score": float(score)}
            for doc, score in zip(documents, scores)
        ]

        # 按分数降序排序
        results.sort(key=lambda x: x["rerank_score"], reverse=True)

        log.info(f"Reranker 完成，返回 Top-{top_k}")
        return results[:top_k]
