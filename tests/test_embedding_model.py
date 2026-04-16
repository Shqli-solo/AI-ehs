"""
Embedding 模型测试模块

测试术语 Embedding 模型的各个组件：
- 模型配置
- 文本编码
- 相似度计算
- 排序准确性
- 术语对数据质量验证
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestEmbeddingConfig:
    """Embedding 配置测试"""

    def test_config_initialization(self):
        """测试配置初始化"""
        from src.ehs_ai.models.embedding_model import EmbeddingConfig

        config = EmbeddingConfig(
            model_name="BAAI/bge-base-zh-v1.5",
            max_seq_length=512,
            embedding_dim=768,
            similarity_threshold=0.5,
        )

        assert config.model_name == "BAAI/bge-base-zh-v1.5"
        assert config.max_seq_length == 512
        assert config.embedding_dim == 768
        assert config.similarity_threshold == 0.5

    def test_default_config(self):
        """测试默认配置"""
        from src.ehs_ai.models.embedding_model import EmbeddingConfig

        config = EmbeddingConfig()

        assert config.model_name == "BAAI/bge-base-zh-v1.5"
        assert config.max_seq_length == 512
        assert config.similarity_threshold == 0.5

    def test_to_dict(self):
        """测试转换为字典"""
        from src.ehs_ai.models.embedding_model import EmbeddingConfig

        config = EmbeddingConfig(
            model_name="test-model",
            max_seq_length=256,
            embedding_dim=512,
            similarity_threshold=0.6,
        )

        config_dict = config.to_dict()

        assert config_dict["model_name"] == "test-model"
        assert config_dict["max_seq_length"] == 256
        assert config_dict["embedding_dim"] == 512
        assert config_dict["similarity_threshold"] == 0.6

    def test_from_dict(self):
        """测试从字典创建配置"""
        from src.ehs_ai.models.embedding_model import EmbeddingConfig

        data = {
            "model_name": "test-model",
            "max_seq_length": 256,
            "embedding_dim": 512,
            "similarity_threshold": 0.6,
        }

        config = EmbeddingConfig.from_dict(data)

        assert config.model_name == "test-model"
        assert config.max_seq_length == 256
        assert config.embedding_dim == 512
        assert config.similarity_threshold == 0.6


class TestEmbeddingModel:
    """Embedding 模型测试"""

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_model_initialization(self):
        """测试模型初始化"""
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig(
            model_name="BAAI/bge-base-zh-v1.5",
            max_seq_length=256,
        )
        model = EmbeddingModel(config)

        assert model.config.model_name == "BAAI/bge-base-zh-v1.5"
        assert model.config.max_seq_length == 256
        assert model.model is None
        assert model.tokenizer is None

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_load_model(self):
        """测试模型加载"""
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig(
            model_name="BAAI/bge-base-zh-v1.5",
            max_seq_length=256,
        )
        model = EmbeddingModel(config)
        model.load_model()

        assert model.model is not None
        assert model.tokenizer is not None

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_encode_single(self):
        """测试单个文本编码"""
        import torch
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig(
            model_name="BAAI/bge-base-zh-v1.5",
            max_seq_length=256,
        )
        model = EmbeddingModel(config)
        model.load_model()

        text = "测试文本"
        embedding = model.encode_single(text)

        assert embedding.shape == (config.embedding_dim,)
        assert embedding.dtype == np.float32

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_encode_batch(self):
        """测试批量文本编码"""
        import numpy as np
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig(
            model_name="BAAI/bge-base-zh-v1.5",
            max_seq_length=256,
        )
        model = EmbeddingModel(config)
        model.load_model()

        texts = ["测试文本 1", "测试文本 2", "测试文本 3"]
        embeddings = model.encode(texts)

        assert embeddings.shape == (3, config.embedding_dim)
        assert embeddings.dtype == np.float32

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_compute_similarity_score(self):
        """测试相似度分数计算"""
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig()
        model = EmbeddingModel(config)
        model.load_model()

        # 相似文本
        text1 = "火灾"
        text2 = "火情"
        similarity = model.compute_similarity_score(text1, text2)

        assert 0 <= similarity <= 1

        # 不相似文本
        text3 = "灭火器"
        similarity_different = model.compute_similarity_score(text1, text3)

        # 相似文本的相似度应该高于不相似文本
        assert similarity > similarity_different

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_rank_by_similarity(self):
        """测试相似度排序"""
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig()
        model = EmbeddingModel(config)
        model.load_model()

        query = "火灾"
        candidates = ["火情", "水灾", "地震", "火焰"]

        results = model.rank_by_similarity(query, candidates, top_k=3)

        assert len(results) == 3
        assert all(isinstance(r, tuple) and len(r) == 3 for r in results)

        # 验证返回格式
        for text, score, idx in results:
            assert text in candidates
            assert 0 <= score <= 1
            assert 0 <= idx < len(candidates)

        # 结果应该按相似度降序排列
        scores = [r[1] for r in results]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_compute_similarity_matrix(self):
        """测试相似度矩阵计算"""
        import numpy as np
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig()
        model = EmbeddingModel(config)
        model.load_model()

        texts1 = ["火灾", "水灾"]
        texts2 = ["火情", "地震", "灭火器"]

        emb1 = model.encode(texts1)
        emb2 = model.encode(texts2)

        similarity_matrix = model.compute_similarity(emb1, emb2)

        assert similarity_matrix.shape == (2, 3)
        assert all(0 <= similarity_matrix[i][j] <= 1 for i in range(2) for j in range(3))


class TestEmbeddingEvaluation:
    """Embedding 评估测试"""

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_evaluate_similarity_ranking(self):
        """测试相似度排序评估"""
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig()
        model = EmbeddingModel(config)
        model.load_model()

        # 构建评估样本
        query_term_pairs = [
            ("火灾", "火情", ["水灾", "地震"]),
            ("泄漏", "泄露", ["爆炸", "燃烧"]),
            ("危险", "风险", ["安全", "防护"]),
        ]

        metrics = model.evaluate_similarity_ranking(query_term_pairs)

        assert "top_1_accuracy" in metrics
        assert "top_5_accuracy" in metrics
        assert "mrr" in metrics
        assert 0 <= metrics["top_1_accuracy"] <= 1
        assert 0 <= metrics["top_5_accuracy"] <= 1
        assert 0 <= metrics["mrr"] <= 1

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_validate_term_pairs(self):
        """测试术语对验证"""
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig(similarity_threshold=0.5)
        model = EmbeddingModel(config)
        model.load_model()

        term_pairs = [
            ("火灾", "火情", "synonym"),
            ("泄漏", "泄露", "synonym"),
            ("危险", "风险", "synonym"),
        ]

        report = model.validate_term_pairs(term_pairs, "synonym")

        assert report["pair_type"] == "synonym"
        assert report["total_pairs"] == 3
        assert "average_similarity" in report
        assert "std_similarity" in report
        assert "min_similarity" in report
        assert "max_similarity" in report
        assert "below_threshold_count" in report
        assert "below_threshold_pairs" in report

        assert 0 <= report["average_similarity"] <= 1
        assert report["below_threshold_count"] <= report["total_pairs"]


class TestEmbeddingModelSaveLoad:
    """模型保存加载测试"""

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_save_and_load_model(self):
        """测试模型保存和加载"""
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建并保存模型
            config = EmbeddingConfig(model_name="BAAI/bge-base-zh-v1.5")
            model1 = EmbeddingModel(config)
            model1.load_model()
            save_path = os.path.join(tmpdir, "test_model")
            model1.save_model(save_path)

            # 验证保存的文件存在
            assert os.path.exists(os.path.join(save_path, "config.json"))
            assert os.path.exists(os.path.join(save_path, "embedding_config.json"))

            # 加载模型
            model2 = EmbeddingModel(config)
            model2.load_pretrained(save_path)

            # 验证加载后的模型配置一致
            assert model2.config.model_name == model1.config.model_name
            assert model2.config.max_seq_length == model1.config.max_seq_length


class TestCreateEmbeddingModel:
    """工厂函数测试"""

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_create_embedding_model(self):
        """测试工厂函数"""
        from src.ehs_ai.models.embedding_model import create_embedding_model, EmbeddingModel

        model = create_embedding_model(
            model_name="BAAI/bge-base-zh-v1.5",
            max_seq_length=256,
        )

        assert isinstance(model, EmbeddingModel)
        assert model.config.model_name == "BAAI/bge-base-zh-v1.5"
        assert model.config.max_seq_length == 256


class TestIntegration:
    """集成测试"""

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_end_to_end_embedding_pipeline(self):
        """测试端到端 Embedding 流程"""
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig()
        model = EmbeddingModel(config)
        model.load_model()

        # 编码术语
        terms = ["火灾", "火情", "水灾", "地震"]
        embeddings = model.encode(terms)

        assert embeddings.shape == (4, config.embedding_dim)

        # 计算相似度
        similarity_matrix = model.compute_similarity(embeddings, embeddings)

        assert similarity_matrix.shape == (4, 4)

        # 对角线应该是 1（自身相似度）
        for i in range(4):
            assert abs(similarity_matrix[i][i] - 1.0) < 1e-5

        # 相似术语的相似度应该高于不相似术语
        assert similarity_matrix[0][1] > similarity_matrix[0][2]  # 火灾 - 火情 > 火灾 - 水灾
        assert similarity_matrix[0][1] > similarity_matrix[0][3]  # 火灾 - 火情 > 火灾 - 地震

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_ranking_with_real_ehs_terms(self):
        """测试真实 EHS 术语排序"""
        from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig

        config = EmbeddingConfig()
        model = EmbeddingModel(config)
        model.load_model()

        # 同义词测试
        query = "气体泄漏"
        candidates = ["泄露", "溢出", "爆炸", "燃烧"]
        results = model.rank_by_similarity(query, candidates, top_k=4)

        # "泄露"应该排在前面
        top_result = results[0][0]
        assert top_result in ["泄露", "泄漏"]

        # 上下位词测试
        query = "化学品事故"
        candidates = ["硫酸泄漏", "机械伤害", "触电", "火灾"]
        results = model.rank_by_similarity(query, candidates, top_k=4)

        # "硫酸泄漏"作为化学品事故应该排前面
        result_texts = [r[0] for r in results]
        assert "硫酸泄漏" in result_texts


class TestDataFormat:
    """数据格式测试"""

    def test_sample_data_format(self):
        """测试样本数据格式"""
        from src.ehs_ai.models.embedding_model import EmbeddingConfig

        config = EmbeddingConfig()

        # 模拟样本数据
        sample = {
            "anchor": "火灾",
            "positive": "火情",
            "relation": "synonym",
            "negatives": ["水灾", "地震"],
        }

        # 验证必填字段
        assert "anchor" in sample
        assert "positive" in sample
        assert "relation" in sample

        # 验证关系类型
        valid_relations = ["synonym", "hypernym", "hyponym", "related"]
        assert sample["relation"] in valid_relations

    def test_term_pair_format(self):
        """测试术语对格式"""
        # 术语对格式
        term_pair = ("火灾", "火情", "synonym")

        assert len(term_pair) == 3
        assert isinstance(term_pair[0], str)
        assert isinstance(term_pair[1], str)
        assert isinstance(term_pair[2], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
