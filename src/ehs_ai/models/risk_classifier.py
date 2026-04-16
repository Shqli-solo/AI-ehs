"""
EHS 风险分级模型定义

基于 PyTorch 的风险分类模型，支持:
- 多分类风险等级预测 (LOW, MEDIUM, HIGH, CRITICAL)
- 混淆矩阵和 F1 分数计算
- 过拟合检测 (训练集 vs 测试集 accuracy 差异检测)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Any, List, Tuple
from transformers import AutoModel, AutoTokenizer
from sklearn.metrics import confusion_matrix, f1_score, classification_report
import numpy as np

from .risk_classifier_config import RiskClassifierConfig


class RiskClassifier(nn.Module):
    """
    风险分类器模型类

    基于预训练语言模型的分类器，支持:
    - 风险等级多分类
    - 训练/评估模式切换
    - 过拟合检测
    """

    def __init__(self, config: RiskClassifierConfig):
        super().__init__()
        self.config = config

        # 加载预训练模型
        self.base_model = AutoModel.from_pretrained(config.model_name)
        hidden_size = self.base_model.config.hidden_size

        # 分类头
        self.classifier = nn.Sequential(
            nn.Dropout(config.dropout),
            nn.Linear(hidden_size, config.hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(config.hidden_dim),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim, config.num_labels),
        )

        # 损失函数
        self.loss_fn = nn.CrossEntropyLoss()

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        """
        前向传播

        Args:
            input_ids: 输入 token IDs, shape (batch_size, seq_len)
            attention_mask: 注意力掩码，shape (batch_size, seq_len)
            labels: 标签 (可选), shape (batch_size,)

        Returns:
            包含 logits 和 loss (如果提供 labels) 的字典
        """
        # 获取 [CLS] token 表示
        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )
        cls_embedding = outputs.last_hidden_state[:, 0, :]  # (batch_size, hidden_size)

        # 分类
        logits = self.classifier(cls_embedding)  # (batch_size, num_labels)

        result = {"logits": logits}

        # 计算损失
        if labels is not None:
            loss = self.loss_fn(logits, labels.view(-1))
            result["loss"] = loss

        return result

    def predict(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        预测风险等级

        Args:
            input_ids: 输入 token IDs
            attention_mask: 注意力掩码

        Returns:
            (predicted_labels, probabilities) 元组
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(input_ids, attention_mask)
            logits = outputs["logits"]
            probs = F.softmax(logits, dim=-1)
            predicted = torch.argmax(logits, dim=-1)
        return predicted, probs

    def compute_metrics(
        self,
        predictions: torch.Tensor,
        labels: torch.Tensor,
    ) -> Dict[str, float]:
        """
        计算评估指标

        Args:
            predictions: 预测标签
            labels: 真实标签

        Returns:
            包含 accuracy, f1, precision, recall 的字典
        """
        from sklearn.metrics import accuracy_score, precision_score, recall_score

        preds = predictions.cpu().numpy()
        true_labels = labels.cpu().numpy()

        accuracy = accuracy_score(true_labels, preds)
        f1_macro = f1_score(true_labels, preds, average="macro")
        f1_weighted = f1_score(true_labels, preds, average="weighted")
        precision_macro = precision_score(true_labels, preds, average="macro", zero_division=0)
        recall_macro = recall_score(true_labels, preds, average="macro", zero_division=0)

        return {
            "accuracy": accuracy,
            "f1_macro": f1_macro,
            "f1_weighted": f1_weighted,
            "precision_macro": precision_macro,
            "recall_macro": recall_macro,
        }

    def detect_overfitting(
        self,
        train_accuracy: float,
        test_accuracy: float,
        threshold: float = 0.1,
    ) -> Tuple[bool, str]:
        """
        检测过拟合

        Args:
            train_accuracy: 训练集准确率
            test_accuracy: 测试集准确率
            threshold: 过拟合判定阈值 (默认 10%)

        Returns:
            (is_overfitting, message) 元组
        """
        diff = train_accuracy - test_accuracy
        is_overfitting = diff > threshold

        if is_overfitting:
            message = (
                f"⚠️  检测到过拟合！"
                f"训练集准确率 ({train_accuracy:.2%}) - 测试集准确率 ({test_accuracy:.2%}) = {diff:.2%} > {threshold:.0%}"
            )
        else:
            message = (
                f"✓ 过拟合检测通过"
                f"训练集准确率 ({train_accuracy:.2%}) - 测试集准确率 ({test_accuracy:.2%}) = {diff:.2%} <= {threshold:.0%}"
            )

        return is_overfitting, message

    def generate_confusion_matrix_report(
        self,
        predictions: torch.Tensor,
        labels: torch.Tensor,
    ) -> str:
        """
        生成混淆矩阵报告

        Args:
            predictions: 预测标签
            labels: 真实标签

        Returns:
            格式化的混淆矩阵和 F1 分数报告字符串
        """
        preds = predictions.cpu().numpy()
        true_labels = labels.cpu().numpy()

        # 混淆矩阵
        cm = confusion_matrix(true_labels, preds)

        # 分类报告
        report = classification_report(
            true_labels,
            preds,
            target_names=[self.config.label2text[i] for i in range(self.config.num_labels)],
            digits=4,
        )

        # 格式化输出
        lines = [
            "=" * 60,
            "混淆矩阵 (Confusion Matrix)",
            "=" * 60,
        ]

        # 表头
        header = "Predicted ->  " + "  ".join(f"{self.config.label2text[i]:>10}" for i in range(self.config.num_labels))
        lines.append(header)
        lines.append("-" * 60)

        # 矩阵内容
        for i in range(self.config.num_labels):
            row = f"Actual {self.config.label2text[i]:<8}  " + "  ".join(f"{cm[i][j]:>10}" for j in range(self.config.num_labels))
            lines.append(row)

        lines.append("")
        lines.append("=" * 60)
        lines.append("F1 分数和分类报告")
        lines.append("=" * 60)
        lines.append(report)
        lines.append("=" * 60)

        return "\n".join(lines)


class RiskClassifierModel:
    """
    风险分类器模型封装类

    提供模型训练、评估、预测的高级接口
    """

    def __init__(
        self,
        model_name: str = "bert-base-chinese",
        num_labels: int = 4,
        hidden_dim: int = 256,
        dropout: float = 0.3,
        num_layers: int = 2,
        device: Optional[str] = None,
    ):
        self.config = RiskClassifierConfig(
            model_name=model_name,
            num_labels=num_labels,
            hidden_dim=hidden_dim,
            dropout=dropout,
            num_layers=num_layers,
        )

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = RiskClassifier(self.config).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # 训练历史
        self.train_history = {
            "train_losses": [],
            "train_accuracies": [],
            "eval_losses": [],
            "eval_accuracies": [],
        }

    def tokenize_batch(
        self,
        texts: List[str],
        max_length: int = 128,
        padding: str = "max_length",
        truncation: bool = True,
    ) -> Dict[str, torch.Tensor]:
        """
        批量文本分词

        Args:
            texts: 文本列表
            max_length: 最大序列长度
            padding: 填充策略
            truncation: 是否截断

        Returns:
            包含 input_ids 和 attention_mask 的字典
        """
        return self.tokenizer(
            texts,
            max_length=max_length,
            padding=padding,
            truncation=truncation,
            return_tensors="pt",
        )

    def predict_risk_level(self, text: str) -> Tuple[str, Dict[str, float]]:
        """
        预测单条文本的风险等级

        Args:
            text: 输入文本

        Returns:
            (risk_label, probabilities_dict) 元组
        """
        self.model.eval()

        # 分词
        inputs = self.tokenize_batch([text])
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)

        # 预测
        predicted, probs = self.model.predict(input_ids, attention_mask)

        # 获取结果
        risk_label = self.config.label2text[predicted[0].item()]
        probs_dict = {
            self.config.label2text[i]: probs[0][i].item()
            for i in range(self.config.num_labels)
        }

        return risk_label, probs_dict

    def predict_batch(self, texts: List[str]) -> List[str]:
        """
        批量预测风险等级

        Args:
            texts: 文本列表

        Returns:
            风险标签列表
        """
        self.model.eval()

        # 分词
        inputs = self.tokenize_batch(texts)
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)

        # 预测
        predicted, _ = self.model.predict(input_ids, attention_mask)

        # 转换为标签
        return [
            self.config.label2text[p.item()]
            for p in predicted
        ]

    def evaluate(
        self,
        texts: List[str],
        labels: List[int],
        batch_size: int = 32,
    ) -> Dict[str, Any]:
        """
        评估模型性能

        Args:
            texts: 文本列表
            labels: 标签列表
            batch_size: 批大小

        Returns:
            包含各项指标的字典
        """
        self.model.eval()

        all_predictions = []
        all_labels = []
        total_loss = 0.0
        num_batches = 0

        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_labels = labels[i:i + batch_size]

            # 分词
            inputs = self.tokenize_batch(batch_texts)
            input_ids = inputs["input_ids"].to(self.device)
            attention_mask = inputs["attention_mask"].to(self.device)
            label_tensor = torch.tensor(batch_labels, dtype=torch.long).to(self.device)

            # 前向传播
            with torch.no_grad():
                outputs = self.model.forward(input_ids, attention_mask, label_tensor)
                total_loss += outputs["loss"].item()
                predicted, _ = self.model.predict(input_ids, attention_mask)

            all_predictions.append(predicted.cpu())
            all_labels.append(label_tensor.cpu())
            num_batches += 1

        # 合并结果
        all_predictions = torch.cat(all_predictions, dim=0)
        all_labels = torch.cat(all_labels, dim=0)
        avg_loss = total_loss / num_batches

        # 计算指标
        metrics = self.model.compute_metrics(all_predictions, all_labels)
        metrics["eval_loss"] = avg_loss

        # 混淆矩阵报告
        confusion_report = self.model.generate_confusion_matrix_report(all_predictions, all_labels)

        return {
            "metrics": metrics,
            "confusion_report": confusion_report,
            "predictions": all_predictions,
            "labels": all_labels,
        }

    def check_overfitting(
        self,
        train_texts: List[str],
        train_labels: List[int],
        test_texts: List[str],
        test_labels: List[int],
        threshold: float = 0.1,
    ) -> Tuple[bool, str, Dict[str, float]]:
        """
        检查过拟合

        Args:
            train_texts: 训练文本
            train_labels: 训练标签
            test_texts: 测试文本
            test_labels: 测试标签
            threshold: 过拟合阈值

        Returns:
            (is_overfitting, message, metrics_dict) 元组
        """
        # 评估训练集
        train_result = self.evaluate(train_texts, train_labels)
        train_accuracy = train_result["metrics"]["accuracy"]

        # 评估测试集
        test_result = self.evaluate(test_texts, test_labels)
        test_accuracy = test_result["metrics"]["accuracy"]

        # 检测过拟合
        is_overfitting, message = self.model.detect_overfitting(
            train_accuracy, test_accuracy, threshold
        )

        metrics = {
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy,
            "accuracy_diff": train_accuracy - test_accuracy,
            "threshold": threshold,
        }

        return is_overfitting, message, metrics

    def save_model(self, output_dir: str) -> None:
        """保存模型"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        # 保存模型权重
        torch.save(self.model.state_dict(), os.path.join(output_dir, "risk_classifier.pt"))

        # 保存分词器
        self.tokenizer.save_pretrained(output_dir)

        # 保存配置
        import json
        config_path = os.path.join(output_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump({
                "model_name": self.config.model_name,
                "num_labels": self.config.num_labels,
                "hidden_dim": self.config.hidden_dim,
                "dropout": self.config.dropout,
                "label2text": self.config.label2text,
            }, f, indent=2, ensure_ascii=False)

        print(f"Model saved to: {output_dir}")

    def load_model(self, model_path: str) -> None:
        """加载模型"""
        import os
        import json

        # 加载配置
        config_path = os.path.join(model_path, "config.json")
        with open(config_path, "r", encoding="utf-utf-8") as f:
            config = json.load(f)

        # 重新初始化
        self.config = RiskClassifierConfig(
            model_name=config["model_name"],
            num_labels=config["num_labels"],
            hidden_dim=config.get("hidden_dim", 256),
            dropout=config.get("dropout", 0.3),
        )

        # 加载权重
        model_weights_path = os.path.join(model_path, "risk_classifier.pt")
        self.model.load_state_dict(torch.load(model_weights_path, map_location=self.device))

        # 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        print(f"Model loaded from: {model_path}")


def create_risk_classifier(
    model_name: str = "bert-base-chinese",
    num_labels: int = 4,
    hidden_dim: int = 256,
    dropout: float = 0.3,
    **kwargs
) -> RiskClassifierModel:
    """
    创建风险分类器的工厂函数

    Args:
        model_name: 预训练模型名称
        num_labels: 分类数量
        hidden_dim: 隐藏层维度
        dropout: dropout 率
        **kwargs: 其他参数

    Returns:
        RiskClassifierModel 实例
    """
    return RiskClassifierModel(
        model_name=model_name,
        num_labels=num_labels,
        hidden_dim=hidden_dim,
        dropout=dropout,
        **kwargs
    )
