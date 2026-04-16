"""
风险分类器测试模块

测试风险分级模型的各个组件：
- 模型初始化
- 风险预测
- 混淆矩阵和 F1 分数计算
- 过拟合检测
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到路径 (mianshi 目录)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRiskClassifierConfig:
    """风险分类器配置测试"""

    def test_config_initialization(self):
        """测试配置初始化"""
        # 从不依赖 torch 的模块导入
        from src.ehs_ai.models.risk_classifier_config import RiskClassifierConfig

        config = RiskClassifierConfig(
            model_name="bert-base-chinese",
            num_labels=4,
            hidden_dim=256,
            dropout=0.3,
        )

        assert config.model_name == "bert-base-chinese"
        assert config.num_labels == 4
        assert config.hidden_dim == 256
        assert config.dropout == 0.3
        assert len(config.label2text) == 4
        assert config.label2text[0] == "LOW"
        assert config.label2text[3] == "CRITICAL"

    def test_label_mapping(self):
        """测试标签映射"""
        # 从不依赖 torch 的模块导入
        from src.ehs_ai.models.risk_classifier_config import RiskClassifierConfig

        config = RiskClassifierConfig()

        # 测试正向映射
        assert config.label2text[0] == "LOW"
        assert config.label2text[1] == "MEDIUM"
        assert config.label2text[2] == "HIGH"
        assert config.label2text[3] == "CRITICAL"

        # 测试反向映射
        assert config.text2label["LOW"] == 0
        assert config.text2label["CRITICAL"] == 3

    def test_to_dict(self):
        """测试转换为字典"""
        from src.ehs_ai.models.risk_classifier_config import RiskClassifierConfig

        config = RiskClassifierConfig(
            model_name="test-model",
            num_labels=4,
            hidden_dim=128,
        )

        config_dict = config.to_dict()

        assert config_dict["model_name"] == "test-model"
        assert config_dict["num_labels"] == 4
        assert config_dict["hidden_dim"] == 128
        assert "label2text" in config_dict

    def test_from_dict(self):
        """测试从字典创建"""
        from src.ehs_ai.models.risk_classifier_config import RiskClassifierConfig

        data = {
            "model_name": "test-model",
            "num_labels": 4,
            "hidden_dim": 128,
            "dropout": 0.2,
        }

        config = RiskClassifierConfig.from_dict(data)

        assert config.model_name == "test-model"
        assert config.num_labels == 4
        assert config.hidden_dim == 128
        assert config.dropout == 0.2


class TestRiskClassifier:
    """风险分类器模型测试"""

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_model_initialization(self):
        """测试模型初始化"""
        from src.ehs_ai.models.risk_classifier import RiskClassifier, RiskClassifierConfig

        config = RiskClassifierConfig(
            model_name="bert-base-chinese",
            num_labels=4,
            hidden_dim=128,
            dropout=0.1,
        )

        model = RiskClassifier(config)

        assert model.config.num_labels == 4
        assert model.config.hidden_dim == 128

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_forward_pass(self):
        """测试前向传播"""
        import torch
        from src.ehs_ai.models.risk_classifier import RiskClassifier, RiskClassifierConfig

        config = RiskClassifierConfig(num_labels=4)
        model = RiskClassifier(config)

        # 创建模拟输入
        batch_size = 2
        seq_len = 32
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        attention_mask = torch.ones((batch_size, seq_len))

        # 前向传播（无标签）
        outputs = model.forward(input_ids, attention_mask)
        assert "logits" in outputs
        assert outputs["logits"].shape == (batch_size, 4)
        assert "loss" not in outputs

        # 前向传播（有标签）
        labels = torch.tensor([0, 2])
        outputs = model.forward(input_ids, attention_mask, labels)
        assert "logits" in outputs
        assert "loss" in outputs
        assert outputs["loss"].dim() == 0

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_predict_method(self):
        """测试预测方法"""
        import torch
        from src.ehs_ai.models.risk_classifier import RiskClassifier, RiskClassifierConfig

        config = RiskClassifierConfig(num_labels=4)
        model = RiskClassifier(config)

        batch_size = 2
        seq_len = 32
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        attention_mask = torch.ones((batch_size, seq_len))

        predicted, probs = model.predict(input_ids, attention_mask)

        assert predicted.shape == (batch_size,)
        assert probs.shape == (batch_size, 4)
        assert all(0 <= p <= 1 for row in probs.tolist() for p in row)
        # 验证概率和为 1
        for prob_row in probs.tolist():
            assert abs(sum(prob_row) - 1.0) < 1e-5

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_compute_metrics(self):
        """测试指标计算"""
        import torch
        from src.ehs_ai.models.risk_classifier import RiskClassifier, RiskClassifierConfig

        config = RiskClassifierConfig(num_labels=4)
        model = RiskClassifier(config)

        predictions = torch.tensor([0, 1, 2, 3, 0, 1])
        labels = torch.tensor([0, 1, 2, 2, 0, 3])

        metrics = model.compute_metrics(predictions, labels)

        assert "accuracy" in metrics
        assert "f1_macro" in metrics
        assert "f1_weighted" in metrics
        assert 0 <= metrics["accuracy"] <= 1
        assert 0 <= metrics["f1_macro"] <= 1

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_detect_overfitting(self):
        """测试过拟合检测"""
        from src.ehs_ai.models.risk_classifier import RiskClassifier, RiskClassifierConfig

        config = RiskClassifierConfig(num_labels=4)
        model = RiskClassifier(config)

        # 测试过拟合情况
        is_overfitting, message = model.detect_overfitting(
            train_accuracy=0.95,
            test_accuracy=0.70,
            threshold=0.1,
        )
        assert is_overfitting is True
        assert "过拟合" in message

        # 测试正常情况
        is_overfitting, message = model.detect_overfitting(
            train_accuracy=0.85,
            test_accuracy=0.80,
            threshold=0.1,
        )
        assert is_overfitting is False
        assert "通过" in message or "Overfitting" not in message

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_generate_confusion_matrix_report(self):
        """测试混淆矩阵报告生成"""
        import torch
        from src.ehs_ai.models.risk_classifier import RiskClassifier, RiskClassifierConfig

        config = RiskClassifierConfig(num_labels=4)
        model = RiskClassifier(config)

        predictions = torch.tensor([0, 1, 2, 3, 0, 1, 2, 3])
        labels = torch.tensor([0, 1, 2, 2, 0, 3, 1, 3])

        report = model.generate_confusion_matrix_report(predictions, labels)

        assert "混淆矩阵" in report or "Confusion Matrix" in report
        assert "LOW" in report
        assert "CRITICAL" in report
        assert "F1" in report or "f1" in report


class TestRiskClassifierModel:
    """风险分类器封装模型测试"""

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_risk_classifier_model_initialization(self):
        """测试封装模型初始化"""
        from src.ehs_ai.models.risk_classifier import RiskClassifierModel

        model = RiskClassifierModel(
            model_name="bert-base-chinese",
            num_labels=4,
            hidden_dim=128,
            dropout=0.1,
        )

        assert model.config.num_labels == 4
        assert model.tokenizer is not None
        assert model.model is not None

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_tokenize_batch(self):
        """测试批量分词"""
        import torch
        from src.ehs_ai.models.risk_classifier import RiskClassifierModel

        model = RiskClassifierModel()

        texts = ["测试文本 1", "测试文本 2"]
        inputs = model.tokenize_batch(texts, max_length=64)

        assert "input_ids" in inputs
        assert "attention_mask" in inputs
        assert inputs["input_ids"].shape[0] == 2
        assert inputs["input_ids"].shape[1] <= 64

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_predict_risk_level(self):
        """测试单条风险预测"""
        from src.ehs_ai.models.risk_classifier import RiskClassifierModel

        model = RiskClassifierModel()

        risk_label, probs = model.predict_risk_level("车间温度正常，环境安全")

        assert risk_label in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert isinstance(probs, dict)
        assert len(probs) == 4
        assert all(0 <= p <= 1 for p in probs.values())
        assert abs(sum(probs.values()) - 1.0) < 1e-5

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_predict_batch(self):
        """测试批量预测"""
        from src.ehs_ai.models.risk_classifier import RiskClassifierModel

        model = RiskClassifierModel()

        texts = [
            "车间温度正常",
            "发现烟雾",
            "发生火灾",
        ]
        predictions = model.predict_batch(texts)

        assert len(predictions) == 3
        assert all(pred in ["LOW", "MEDIUM", "HIGH", "CRITICAL"] for pred in predictions)

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_evaluate(self):
        """测试评估方法"""
        from src.ehs_ai.models.risk_classifier import RiskClassifierModel

        model = RiskClassifierModel()

        texts = ["安全", "危险", "紧急"] * 10
        labels = [0, 2, 3] * 10

        results = model.evaluate(texts, labels, batch_size=8)

        assert "metrics" in results
        assert "confusion_report" in results
        assert "predictions" in results
        assert "labels" in results
        assert "accuracy" in results["metrics"]

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_check_overfitting(self):
        """测试过拟合检查"""
        from src.ehs_ai.models.risk_classifier import RiskClassifierModel

        model = RiskClassifierModel()

        train_texts = ["安全"] * 50
        train_labels = [0] * 50
        test_texts = ["安全"] * 20
        test_labels = [0] * 20

        is_overfitting, message, metrics = model.check_overfitting(
            train_texts, train_labels,
            test_texts, test_labels,
            threshold=0.1,
        )

        assert "train_accuracy" in metrics
        assert "test_accuracy" in metrics
        assert "accuracy_diff" in metrics
        assert isinstance(is_overfitting, bool)

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_save_and_load_model(self):
        """测试模型保存和加载"""
        from src.ehs_ai.models.risk_classifier import RiskClassifierModel

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建并保存模型
            model1 = RiskClassifierModel()
            save_path = os.path.join(tmpdir, "test_model")
            model1.save_model(save_path)

            # 验证保存的文件存在
            assert os.path.exists(os.path.join(save_path, "risk_classifier.pt"))
            assert os.path.exists(os.path.join(save_path, "config.json"))

            # 加载模型
            model2 = RiskClassifierModel()
            model2.load_model(save_path)

            # 验证加载后的模型配置一致
            assert model2.config.model_name == model1.config.model_name
            assert model2.config.num_labels == model1.config.num_labels


class TestCreateRiskClassifier:
    """工厂函数测试"""

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_create_risk_classifier(self):
        """测试工厂函数"""
        from src.ehs_ai.models.risk_classifier import create_risk_classifier, RiskClassifierModel

        model = create_risk_classifier(
            model_name="bert-base-chinese",
            num_labels=4,
            hidden_dim=128,
            dropout=0.1,
        )

        assert isinstance(model, RiskClassifierModel)
        assert model.config.num_labels == 4
        assert model.config.hidden_dim == 128


class TestIntegration:
    """集成测试"""

    @pytest.mark.skip(reason="需要 torch 环境和预训练模型")
    def test_end_to_end_prediction(self):
        """测试端到端预测流程"""
        from src.ehs_ai.models.risk_classifier import RiskClassifierModel

        model = RiskClassifierModel()

        # 低风险文本
        low_risk_text = "车间环境正常，设备运行良好，无异常告警"
        low_label, low_probs = model.predict_risk_level(low_risk_text)
        assert low_label in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        # 高风险文本
        high_risk_text = "发生火灾，火势蔓延，需要紧急疏散"
        high_label, high_probs = model.predict_risk_level(high_risk_text)
        assert high_label in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        # 批量预测
        texts = [low_risk_text, high_risk_text]
        predictions = model.predict_batch(texts)
        assert len(predictions) == 2


class TestDataFormat:
    """数据格式测试"""

    def test_risk_label_format(self):
        """测试风险标签格式"""
        from src.ehs_ai.models.risk_classifier_config import RiskClassifierConfig

        config = RiskClassifierConfig()

        # 验证标签映射完整性
        expected_labels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        for i, label in enumerate(expected_labels):
            assert config.label2text[i] == label
            assert config.text2label[label] == i

    def test_sample_data_format(self):
        """测试样本数据格式"""
        from src.ehs_ai.models.risk_classifier_config import RiskClassifierConfig

        config = RiskClassifierConfig()

        # 模拟样本数据
        sample = {
            "text": "测试文本",
            "label": "HIGH",
        }

        # 验证标签转换
        label_str = sample["label"]
        label_int = config.text2label.get(label_str.upper(), 0)
        assert label_int == 2

        # 验证反向转换
        label_back = config.label2text[label_int]
        assert label_back == "HIGH"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
