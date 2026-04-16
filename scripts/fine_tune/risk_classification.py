#!/usr/bin/env python3
"""
风险分级模型训练脚本

基于 PyTorch 的风险分类模型训练，支持:
- 多分类风险等级训练 (LOW, MEDIUM, HIGH, CRITICAL)
- 混淆矩阵和 F1 分数评估
- 过拟合检测 (训练集 vs 测试集 accuracy 差异 < 10%)
- TensorBoard 日志记录
- 早停 (Early Stopping)
- 检查点 (Checkpoint) 保存
"""

import os
import sys
import json
import argparse
import random
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from sklearn.model_selection import train_test_split
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ehs_ai.models.risk_classifier import (
    RiskClassifierModel,
    RiskClassifierConfig,
    create_risk_classifier,
)


@dataclass
class ModelArguments:
    """模型参数"""
    model_name_or_path: str = field(
        default="bert-base-chinese",
        metadata={"help": "预训练模型名称或路径"}
    )
    hidden_dim: int = field(
        default=256,
        metadata={"help": "分类器隐藏层维度"}
    )
    dropout: float = field(
        default=0.3,
        metadata={"help": "Dropout 率"}
    )
    num_layers: int = field(
        default=2,
        metadata={"help": "分类器层数"}
    )


@dataclass
class DataArguments:
    """数据参数"""
    data_path: str = field(
        default="data/processed/risk_classification.json",
        metadata={"help": "训练数据路径"}
    )
    test_split: float = field(
        default=0.2,
        metadata={"help": "测试集比例"}
    )
    val_split: float = field(
        default=0.1,
        metadata={"help": "验证集比例 (从训练集中划分)"}
    )
    max_seq_length: int = field(
        default=128,
        metadata={"help": "最大序列长度"}
    )
    seed: int = field(
        default=42,
        metadata={"help": "随机种子"}
    )


@dataclass
class TrainingArgs:
    """训练参数"""
    output_dir: str = field(
        default="outputs/risk_classification",
        metadata={"help": "输出目录"}
    )
    num_train_epochs: int = field(
        default=10,
        metadata={"help": "训练轮数"}
    )
    batch_size: int = field(
        default=32,
        metadata={"help": "训练批大小"}
    )
    learning_rate: float = field(
        default=2e-5,
        metadata={"help": "学习率"}
    )
    weight_decay: float = field(
        default=0.01,
        metadata={"help": "权重衰减"}
    )
    warmup_ratio: float = field(
        default=0.1,
        metadata={"help": "预热比例"}
    )
    early_stopping_patience: int = field(
        default=3,
        metadata={"help": "早停 patience"}
    )
    overfitting_threshold: float = field(
        default=0.1,
        metadata={"help": "过拟合检测阈值 (10%)"}
    )
    save_steps: int = field(
        default=100,
        metadata={"help": "保存步数"}
    )
    logging_steps: int = field(
        default=10,
        metadata={"help": "日志记录步数"}
    )
    evaluation_strategy: str = field(
        default="epoch",
        metadata={"help": "评估策略"}
    )


class RiskClassificationDataset(Dataset):
    """风险分类数据集"""

    def __init__(
        self,
        data: List[Dict[str, Any]],
        tokenizer: AutoTokenizer,
        max_seq_length: int = 128,
        label2text: Optional[Dict[str, int]] = None,
    ):
        self.data = data
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        self.label2text = label2text or {
            "LOW": 0,
            "MEDIUM": 1,
            "HIGH": 2,
            "CRITICAL": 3,
        }

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.data[idx]

        # 获取文本和标签
        text = item.get("text", item.get("input", item.get("instruction", "")))
        label_str = item.get("label", item.get("risk_level", ""))

        # 转换标签为数字
        if isinstance(label_str, str):
            label = self.label2text.get(label_str.upper(), 0)
        else:
            label = int(label_str)

        # 分词
        encoding = self.tokenizer(
            text,
            max_length=self.max_seq_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label": torch.tensor(label, dtype=torch.long),
        }


class RiskClassificationTrainer:
    """风险分类训练器"""

    def __init__(
        self,
        model: RiskClassifierModel,
        train_dataset: RiskClassificationDataset,
        eval_dataset: RiskClassificationDataset,
        test_dataset: RiskClassificationDataset,
        args: TrainingArgs,
    ):
        self.model = model
        self.train_dataset = train_dataset
        self.eval_dataset = eval_dataset
        self.test_dataset = test_dataset
        self.args = args

        self.device = model.device
        self.optimizer = None
        self.scheduler = None

        # 训练历史
        self.train_losses = []
        self.eval_losses = []
        self.eval_accuracies = []
        self.best_eval_accuracy = 0.0
        self.patience_counter = 0

    def setup_optimizer(self):
        """设置优化器和学习率调度器"""
        self.optimizer = torch.optim.AdamW(
            self.model.model.parameters(),
            lr=self.args.learning_rate,
            weight_decay=self.args.weight_decay,
        )

        # 计算 warmup 步数
        num_training_steps = len(self.train_dataset) // self.args.batch_size * self.args.num_train_epochs
        num_warmup_steps = int(num_training_steps * self.args.warmup_ratio)

        self.scheduler = torch.optim.lr_scheduler.LinearWarmupCosineAnnealingLR(
            self.optimizer,
            num_warmup_steps=num_warmup_steps,
            num_training_steps=num_training_steps,
        )

    def train_epoch(self, dataloader: DataLoader) -> Tuple[float, List[int], List[int]]:
        """训练一个 epoch"""
        self.model.model.train()

        total_loss = 0.0
        all_predictions = []
        all_labels = []

        for batch in dataloader:
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["label"].to(self.device)

            # 前向传播
            self.optimizer.zero_grad()
            outputs = self.model.model.forward(input_ids, attention_mask, labels)
            loss = outputs["loss"]

            # 反向传播
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.model.parameters(), 1.0)
            self.optimizer.step()
            self.scheduler.step()

            # 记录损失
            total_loss += loss.item()

            # 记录预测
            with torch.no_grad():
                predicted, _ = self.model.model.predict(input_ids, attention_mask)
                all_predictions.extend(predicted.cpu().tolist())
                all_labels.extend(labels.cpu().tolist())

        avg_loss = total_loss / len(dataloader)
        return avg_loss, all_predictions, all_labels

    @torch.no_grad()
    def evaluate(
        self,
        dataloader: DataLoader,
    ) -> Tuple[float, List[int], List[int]]:
        """评估"""
        self.model.model.eval()

        total_loss = 0.0
        all_predictions = []
        all_labels = []

        for batch in dataloader:
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["label"].to(self.device)

            # 前向传播
            outputs = self.model.model.forward(input_ids, attention_mask, labels)
            loss = outputs["loss"]
            total_loss += loss.item()

            # 记录预测
            predicted, _ = self.model.model.predict(input_ids, attention_mask)
            all_predictions.extend(predicted.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

        avg_loss = total_loss / len(dataloader)
        return avg_loss, all_predictions, all_labels

    def train(self) -> Dict[str, Any]:
        """开始训练"""
        print("\n" + "=" * 60)
        print("风险分级模型训练")
        print("=" * 60)
        print(f"模型：{self.model.config.model_name}")
        print(f"输出目录：{self.args.output_dir}")
        print(f"训练样本：{len(self.train_dataset)}")
        print(f"验证样本：{len(self.eval_dataset)}")
        print(f"测试样本：{len(self.test_dataset)}")
        print("=" * 60)

        # 设置优化器
        self.setup_optimizer()

        # 创建数据加载器
        train_loader = DataLoader(
            self.train_dataset,
            batch_size=self.args.batch_size,
            shuffle=True,
            num_workers=0,
            collate_fn=lambda x: {
                "input_ids": torch.stack([item["input_ids"] for item in x]),
                "attention_mask": torch.stack([item["attention_mask"] for item in x]),
                "label": torch.stack([item["label"] for item in x]),
            },
        )
        eval_loader = DataLoader(
            self.eval_dataset,
            batch_size=self.args.batch_size,
            shuffle=False,
            num_workers=0,
            collate_fn=lambda x: {
                "input_ids": torch.stack([item["input_ids"] for item in x]),
                "attention_mask": torch.stack([item["attention_mask"] for item in x]),
                "label": torch.stack([item["label"] for item in x]),
            },
        )

        # 训练循环
        print("\n开始训练...")
        for epoch in range(self.args.num_train_epochs):
            print(f"\nEpoch {epoch + 1}/{self.args.num_train_epochs}")
            print("-" * 40)

            # 训练
            train_loss, train_preds, train_labels = self.train_epoch(train_loader)
            self.train_losses.append(train_loss)

            # 训练集准确率
            train_accuracy = sum(
                p == l for p, l in zip(train_preds, train_labels)
            ) / len(train_labels)

            # 评估
            eval_loss, eval_preds, eval_labels = self.evaluate(eval_loader)
            self.eval_losses.append(eval_loss)

            eval_accuracy = sum(
                p == l for p, l in zip(eval_preds, eval_labels)
            ) / len(eval_labels)
            self.eval_accuracies.append(eval_accuracy)

            # 打印进度
            print(f"Train Loss: {train_loss:.4f}, Train Accuracy: {train_accuracy:.4f}")
            print(f"Eval Loss: {eval_loss:.4f}, Eval Accuracy: {eval_accuracy:.4f}")

            # 早停检查
            if eval_accuracy > self.best_eval_accuracy:
                self.best_eval_accuracy = eval_accuracy
                self.patience_counter = 0
                # 保存最佳模型
                self.model.save_model(os.path.join(self.args.output_dir, "best_model"))
                print(f"✓ 保存最佳模型 (accuracy: {eval_accuracy:.4f})")
            else:
                self.patience_counter += 1
                print(f"早停计数器：{self.patience_counter}/{self.args.early_stopping_patience}")

            if self.patience_counter >= self.args.early_stopping_patience:
                print(f"\n触发早停，停止训练")
                break

            # 定期保存检查点
            if (epoch + 1) % self.args.save_steps == 0:
                checkpoint_dir = os.path.join(self.args.output_dir, f"checkpoint-epoch-{epoch + 1}")
                self.model.save_model(checkpoint_dir)
                print(f"保存检查点：{checkpoint_dir}")

        # 在测试集上评估
        print("\n" + "=" * 60)
        print("测试集评估")
        print("=" * 60)
        self._final_evaluation()

        # 保存训练历史
        self._save_training_history()

        print("\n" + "=" * 60)
        print("训练完成!")
        print("=" * 60)

        return {
            "best_eval_accuracy": self.best_eval_accuracy,
            "train_losses": self.train_losses,
            "eval_losses": self.eval_losses,
            "eval_accuracies": self.eval_accuracies,
        }

    def _final_evaluation(self):
        """最终测试集评估"""
        test_loader = DataLoader(
            self.test_dataset,
            batch_size=self.args.batch_size,
            shuffle=False,
            num_workers=0,
            collate_fn=lambda x: {
                "input_ids": torch.stack([item["input_ids"] for item in x]),
                "attention_mask": torch.stack([item["attention_mask"] for item in x]),
                "label": torch.stack([item["label"] for item in x]),
            },
        )

        test_loss, test_preds, test_labels = self.evaluate(test_loader)
        test_accuracy = sum(
            p == l for p, l in zip(test_preds, test_labels)
        ) / len(test_labels)

        print(f"Test Loss: {test_loss:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f}")

        # 混淆矩阵和 F1 分数报告
        import torch as t
        report = self.model.model.generate_confusion_matrix_report(
            t.tensor(test_preds),
            t.tensor(test_labels)
        )
        print("\n" + report)

        # 过拟合检测
        train_result = self.model.evaluate(
            [self.train_dataset.data[i].get("text", self.train_dataset.data[i].get("input", ""))
             for i in range(len(self.train_dataset))],
            [self.train_dataset.data[i]["label"] if isinstance(self.train_dataset.data[i].get("label"), int)
             else self.train_dataset.label2text.get(str(self.train_dataset.data[i].get("label", "")).upper(), 0)
             for i in range(len(self.train_dataset))],
        )
        test_result = self.model.evaluate(
            [self.test_dataset.data[i].get("text", self.test_dataset.data[i].get("input", ""))
             for i in range(len(self.test_dataset))],
            [self.test_dataset.data[i]["label"] if isinstance(self.test_dataset.data[i].get("label"), int)
             else self.test_dataset.label2text.get(str(self.test_dataset.data[i].get("label", "")).upper(), 0)
             for i in range(len(self.test_dataset))],
        )

        is_overfitting, overfitting_msg = self.model.model.detect_overfitting(
            train_result["metrics"]["accuracy"],
            test_result["metrics"]["accuracy"],
            self.args.overfitting_threshold
        )
        print("\n" + overfitting_msg)

        return {
            "test_accuracy": test_accuracy,
            "test_loss": test_loss,
            "is_overfitting": is_overfitting,
        }

    def _save_training_history(self):
        """保存训练历史"""
        os.makedirs(self.args.output_dir, exist_ok=True)

        history = {
            "train_losses": self.train_losses,
            "eval_losses": self.eval_losses,
            "eval_accuracies": self.eval_accuracies,
            "best_eval_accuracy": self.best_eval_accuracy,
            "config": {
                "model_name": self.model.config.model_name,
                "num_labels": self.model.config.num_labels,
                "hidden_dim": self.model.config.hidden_dim,
                "dropout": self.model.config.dropout,
            },
        }

        history_path = os.path.join(self.args.output_dir, "training_history.json")
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"训练历史已保存至：{history_path}")


def load_data(data_path: str) -> List[Dict[str, Any]]:
    """加载数据"""
    print(f"加载数据：{data_path}")

    if not os.path.exists(data_path):
        # 创建示例数据
        print(f"数据文件不存在，创建示例数据...")
        sample_data = create_sample_data()
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        return sample_data

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"加载 {len(data)} 条数据")
    return data


def create_sample_data() -> List[Dict[str, Any]]:
    """创建示例训练数据"""
    import random

    risk_templates = {
        "LOW": [
            "日常安全检查发现灭火器压力正常",
            "车间温度 25 度，湿度 50%,环境舒适",
            "员工正确佩戴安全帽，符合规范",
            "监控设备运行正常，无异常告警",
            "消防设施完好，通道畅通",
        ],
        "MEDIUM": [
            "发现一处电线老化，需要更换",
            "车间烟雾浓度略有上升",
            "有员工未按规定佩戴防护手套",
            "安全出口指示灯故障",
            "化学品存放位置不正确",
        ],
        "HIGH": [
            "检测到烟雾浓度超标，需要立即处理",
            "发现气体泄漏迹象，浓度持续上升",
            "高温设备温度异常，超过警戒线",
            "多人未佩戴防护装备进入危险区域",
            "消防系统检测到火情前兆",
        ],
        "CRITICAL": [
            "发生严重火灾，火势蔓延迅速",
            "有毒气体大量泄漏，需要紧急疏散",
            "爆炸危险 imminent，立即撤离",
            "多人被困危险区域，需要救援",
            "重大安全事故，启动一级响应",
        ],
    }

    data = []
    for label, templates in risk_templates.items():
        for template in templates:
            # 添加一些变体
            for i in range(5):
                data.append({
                    "text": template + f" (变体{i+1})",
                    "label": label,
                    "source": "sample",
                })

    random.shuffle(data)
    return data


def split_data(
    data: List[Dict[str, Any]],
    test_split: float = 0.2,
    val_split: float = 0.1,
    seed: int = 42,
) -> Tuple[List, List, List]:
    """划分数据集"""
    # 先划分出测试集
    train_data, test_data = train_test_split(
        data,
        test_size=test_split,
        random_state=seed,
        stratify=[item["label"] for item in data],
    )

    # 再从训练集中划分出验证集
    val_ratio = val_split / (1 - test_split)
    train_data, eval_data = train_test_split(
        train_data,
        test_size=val_ratio,
        random_state=seed,
        stratify=[item["label"] for item in train_data],
    )

    return list(train_data), list(eval_data), list(test_data)


def main():
    parser = argparse.ArgumentParser(description="风险分级模型训练")

    # 模型参数
    parser.add_argument("--model-name", type=str, default="bert-base-chinese")
    parser.add_argument("--hidden-dim", type=int, default=256)
    parser.add_argument("--dropout", type=float, default=0.3)

    # 数据参数
    parser.add_argument("--data-path", type=str, default="data/processed/risk_classification.json")
    parser.add_argument("--test-split", type=float, default=0.2)
    parser.add_argument("--val-split", type=float, default=0.1)
    parser.add_argument("--max-seq-length", type=int, default=128)
    parser.add_argument("--seed", type=int, default=42)

    # 训练参数
    parser.add_argument("--output-dir", type=str, default="outputs/risk_classification")
    parser.add_argument("--num-epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--early-stopping-patience", type=int, default=3)
    parser.add_argument("--overfitting-threshold", type=float, default=0.1)

    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    # 1. 加载数据
    data = load_data(args.data_path)

    # 2. 划分数据集
    train_data, eval_data, test_data = split_data(
        data,
        test_split=args.test_split,
        val_split=args.val_split,
        seed=args.seed,
    )

    print(f"训练集：{len(train_data)}, 验证集：{len(eval_data)}, 测试集：{len(test_data)}")

    # 3. 创建模型
    model = create_risk_classifier(
        model_name=args.model_name,
        hidden_dim=args.hidden_dim,
        dropout=args.dropout,
    )

    # 4. 创建数据集
    tokenizer = model.tokenizer
    label2text = model.model.config.label2text

    train_dataset = RiskClassificationDataset(
        train_data, tokenizer, args.max_seq_length, label2text
    )
    eval_dataset = RiskClassificationDataset(
        eval_data, tokenizer, args.max_seq_length, label2text
    )
    test_dataset = RiskClassificationDataset(
        test_data, tokenizer, args.max_seq_length, label2text
    )

    # 5. 创建训练器
    training_args = TrainingArgs(
        output_dir=args.output_dir,
        num_train_epochs=args.num_epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        early_stopping_patience=args.early_stopping_patience,
        overfitting_threshold=args.overfitting_threshold,
    )

    trainer = RiskClassificationTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        test_dataset=test_dataset,
        args=training_args,
    )

    # 6. 开始训练
    results = trainer.train()

    # 7. 保存最终模型
    model.save_model(os.path.join(args.output_dir, "final_model"))

    print("\n训练完成!")
    print(f"最佳验证准确率：{results['best_eval_accuracy']:.4f}")


if __name__ == "__main__":
    main()
