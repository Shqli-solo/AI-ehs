"""
EHS 术语 Embedding 模型定义

基于 BGE/BERT 的术语 Embedding 模型，支持：
- 文本编码生成向量
- 相似度计算与排序
- 同义词/上下位词验证
"""

import torch
import torch.nn as nn
from typing import Optional, Dict, Any, List, Tuple
from transformers import AutoTokenizer, AutoModel
import numpy as np


class EmbeddingConfig:
    """Embedding 模型配置"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-base-zh-v1.5",
        max_seq_length: int = 512,
        embedding_dim: int = 768,
        similarity_threshold: float = 0.5,
    ):
        """
        初始化 Embedding 配置

        Args:
            model_name: 预训练模型名称
            max_seq_length: 最大序列长度
            embedding_dim: Embedding 维度
            similarity_threshold: 相似度阈值
        """
        self.model_name = model_name
        self.max_seq_length = max_seq_length
        self.embedding_dim = embedding_dim
        self.similarity_threshold = similarity_threshold

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "model_name": self.model_name,
            "max_seq_length": self.max_seq_length,
            "embedding_dim": self.embedding_dim,
            "similarity_threshold": self.similarity_threshold,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmbeddingConfig":
        """从字典创建配置"""
        return cls(**data)


class EmbeddingModel:
    """
    Embedding 模型类

    封装文本编码和相似度计算的核心逻辑
    """

    def __init__(
        self,
        config: Optional[EmbeddingConfig] = None,
    ):
        """
        初始化 Embedding 模型

        Args:
            config: Embedding 配置
        """
        self.config = config or EmbeddingConfig()
        self.model_name = self.config.model_name
        self.max_seq_length = self.config.max_seq_length

        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load_model(self) -> None:
        """加载预训练模型和分词器"""
        print(f"Loading embedding model: {self.model_name}")

        # 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
        )

        # 加载模型
        self.model = AutoModel.from_pretrained(
            self.model_name,
            trust_remote_code=True,
        ).to(self.device)

        self.model.eval()
        print(f"Embedding model loaded: {self.model_name}")

    @torch.no_grad()
    def encode(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True,
    ) -> np.ndarray:
        """
        编码文本为向量

        Args:
            texts: 文本列表
            batch_size: 批大小
            normalize: 是否归一化向量

        Returns:
            Embedding 向量数组 (n_samples, embedding_dim)
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # 分词
            encoded = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=self.max_seq_length,
                return_tensors="pt",
            ).to(self.device)

            # 获取模型输出
            outputs = self.model(**encoded)

            # 使用 [CLS] token 作为句子表示
            cls_embeddings = outputs.last_hidden_state[:, 0, :]

            # 归一化
            if normalize:
                cls_embeddings = nn.functional.normalize(cls_embeddings, p=2, dim=1)

            all_embeddings.append(cls_embeddings.cpu().numpy())

        return np.vstack(all_embeddings)

    @torch.no_grad()
    def encode_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        编码单个文本为向量

        Args:
            text: 输入文本
            normalize: 是否归一化

        Returns:
            Embedding 向量 (embedding_dim,)
        """
        embeddings = self.encode([text], normalize=normalize)
        return embeddings[0]

    @staticmethod
    def compute_similarity(
        embeddings1: np.ndarray,
        embeddings2: np.ndarray,
    ) -> np.ndarray:
        """
        计算两组向量之间的余弦相似度

        Args:
            embeddings1: 第一组向量 (n1, dim)
            embeddings2: 第二组向量 (n2, dim)

        Returns:
            相似度矩阵 (n1, n2)
        """
        # 如果向量未归一化，先归一化
        embeddings1 = embeddings1 / (np.linalg.norm(embeddings1, axis=1, keepdims=True) + 1e-8)
        embeddings2 = embeddings2 / (np.linalg.norm(embeddings2, axis=1, keepdims=True) + 1e-8)

        # 计算余弦相似度
        similarity_matrix = np.dot(embeddings1, embeddings2.T)

        return similarity_matrix

    def compute_similarity_score(
        self,
        text1: str,
        text2: str,
    ) -> float:
        """
        计算两个文本之间的相似度分数

        Args:
            text1: 第一个文本
            text2: 第二个文本

        Returns:
            相似度分数 (0-1)
        """
        emb1 = self.encode_single(text1)
        emb2 = self.encode_single(text2)

        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-8)
        return float(similarity)

    def rank_by_similarity(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5,
    ) -> List[Tuple[str, float, int]]:
        """
        根据与查询的相似度对候选文本进行排序

        Args:
            query: 查询文本
            candidates: 候选文本列表
            top_k: 返回前 k 个结果

        Returns:
            排序后的列表 [(text, score, index), ...]
        """
        # 编码查询和候选
        query_emb = self.encode_single(query)
        candidate_embs = self.encode(candidates)

        # 计算相似度
        similarities = self.compute_similarity(
            query_emb.reshape(1, -1),
            candidate_embs,
        )[0]

        # 获取排序索引
        sorted_indices = np.argsort(similarities)[::-1]

        # 构建结果
        results = []
        for idx in sorted_indices[:top_k]:
            results.append((
                candidates[idx],
                float(similarities[idx]),
                int(idx),
            ))

        return results

    def evaluate_similarity_ranking(
        self,
        query_term_pairs: List[Tuple[str, str, List[str]]],
    ) -> Dict[str, float]:
        """
        评估相似度排序准确率

        Args:
            query_term_pairs: [(query, positive_term, negative_terms), ...]

        Returns:
            评估指标 {top-1 accuracy, top-5 accuracy, mrr}
        """
        top_1_correct = 0
        top_5_correct = 0
        reciprocal_ranks = []

        for query, positive_term, negative_terms in query_term_pairs:
            candidates = [positive_term] + negative_terms
            ranked = self.rank_by_similarity(query, candidates, top_k=len(candidates))

            # 找到正样本的排名
            rank = None
            for i, (text, score, idx) in enumerate(ranked):
                if text == positive_term:
                    rank = i + 1
                    break

            if rank is not None:
                if rank == 1:
                    top_1_correct += 1
                if rank <= 5:
                    top_5_correct += 1
                reciprocal_ranks.append(1.0 / rank)

        n_pairs = len(query_term_pairs)

        return {
            "top_1_accuracy": top_1_correct / n_pairs if n_pairs > 0 else 0.0,
            "top_5_accuracy": top_5_correct / n_pairs if n_pairs > 0 else 0.0,
            "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0,
        }

    def validate_term_pairs(
        self,
        term_pairs: List[Tuple[str, str, str]],
        pair_type: str = "synonym",
    ) -> Dict[str, Any]:
        """
        验证术语对数据质量

        Args:
            term_pairs: [(term1, term2, relation_type), ...]
            pair_type: 术语对类型 (synonym, hypernym, hyponym)

        Returns:
            验证报告
        """
        similarities = []
        below_threshold = []

        for term1, term2, relation in term_pairs:
            sim = self.compute_similarity_score(term1, term2)
            similarities.append(sim)

            if sim < self.config.similarity_threshold:
                below_threshold.append({
                    "term1": term1,
                    "term2": term2,
                    "relation": relation,
                    "similarity": sim,
                })

        avg_similarity = np.mean(similarities)
        std_similarity = np.std(similarities)

        return {
            "pair_type": pair_type,
            "total_pairs": len(term_pairs),
            "average_similarity": float(avg_similarity),
            "std_similarity": float(std_similarity),
            "min_similarity": float(np.min(similarities)),
            "max_similarity": float(np.max(similarities)),
            "below_threshold_count": len(below_threshold),
            "below_threshold_pairs": below_threshold,
        }

    def save_model(self, output_dir: str) -> None:
        """
        保存模型

        Args:
            output_dir: 输出目录
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")

        import os
        os.makedirs(output_dir, exist_ok=True)

        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        # 保存配置
        import json
        config_path = os.path.join(output_dir, "embedding_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.config.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"Model saved to: {output_dir}")

    def load_pretrained(self, model_dir: str) -> None:
        """
        加载预训练模型

        Args:
            model_dir: 模型目录
        """
        import os
        import json

        # 加载配置
        config_path = os.path.join(model_dir, "embedding_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            self.config = EmbeddingConfig.from_dict(config_data)

        self.model_name = self.config.model_name

        # 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)

        # 加载模型
        self.model = AutoModel.from_pretrained(model_dir).to(self.device)
        self.model.eval()

        print(f"Model loaded from: {model_dir}")


def create_embedding_model(
    model_name: str = "BAAI/bge-base-zh-v1.5",
    max_seq_length: int = 512,
    **kwargs
) -> EmbeddingModel:
    """
    创建 Embedding 模型的工厂函数

    Args:
        model_name: 预训练模型名称
        max_seq_length: 最大序列长度
        **kwargs: 其他参数

    Returns:
        EmbeddingModel 实例
    """
    config = EmbeddingConfig(
        model_name=model_name,
        max_seq_length=max_seq_length,
    )
    return EmbeddingModel(config)
