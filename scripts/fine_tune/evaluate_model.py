#!/usr/bin/env python3
"""
风险分级模型评估脚本

评估训练好的风险分类模型，生成:
- 混淆矩阵报告
- F1 分数 (macro, weighted)
- 准确率、精确率、召回率
- 过拟合检测报告
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field

import torch
import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ehs_ai.models.risk_classifier import (
    RiskClassifierModel,
    create_risk_classifier,
)


@dataclass
class EvalArguments:
    """评估参数"""
    model_path: str = field(
        default="outputs/risk_classification/best_model",
        metadata={"help": "模型路径"}
    )
    data_path: str = field(
        default="data/processed/risk_classification.json",
        metadata={"help": "评估数据路径"}
    )
    output_dir: str = field(
        default="outputs/risk_classification/evaluation",
        metadata={"help": "评估结果输出目录"}
    )
    batch_size: int = field(
        default=32,
        metadata={"help": "评估批大小"}
    )
    overfitting_threshold: float = field(
        default=0.1,
        metadata={"help": "过拟合检测阈值"}
    )


class RiskClassificationEvaluator:
    """风险分类评估器"""

    def __init__(
        self,
        model: RiskClassifierModel,
        label2text: Dict[int, str],
        text2label: Dict[str, int],
        args: EvalArguments,
    ):
        self.model = model
        self.label2text = label2text
        self.text2label = text2label
        self.args = args
        self.num_labels = len(label2text)

    def load_data(self, data_path: str) -> List[Dict[str, Any]]:
        """加载评估数据"""
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def prepare_data(
        self,
        data: List[Dict[str, Any]],
    ) -> Tuple[List[str], List[int]]:
        """准备评估数据"""
        texts = []
        labels = []

        for item in data:
            text = item.get("text", item.get("input", ""))
            label = item.get("label", "")

            # 转换标签为数字
            if isinstance(label, int):
                label_int = label
            else:
                label_int = self.text2label.get(str(label).upper(), 0)

            texts.append(text)
            labels.append(label_int)

        return texts, labels

    def evaluate(
        self,
        texts: List[str],
        labels: List[int],
        batch_size: int = 32,
    ) -> Dict[str, Any]:
        """评估模型"""
        all_predictions = []

        # 分批预测
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_preds = self.model.predict_batch(batch_texts)
            batch_labels = [
                self.label2text[p] if isinstance(p, int) else p
                for p in batch_preds
            ]
            batch_indices = [
                self.text2label.get(pred, 0) for pred in batch_labels
            ]
            all_predictions.extend(batch_indices)

        # 计算指标
        metrics = self.compute_metrics(labels, all_predictions)

        # 生成混淆矩阵报告
        confusion_report = self.generate_confusion_matrix_report(labels, all_predictions)

        return {
            "metrics": metrics,
            "confusion_report": confusion_report,
            "predictions": all_predictions,
            "true_labels": labels,
        }

    def compute_metrics(
        self,
        true_labels: List[int],
        predictions: List[int],
    ) -> Dict[str, float]:
        """计算评估指标"""
        accuracy = accuracy_score(true_labels, predictions)
        precision_macro = precision_score(
            true_labels, predictions, average="macro", zero_division=0
        )
        precision_weighted = precision_score(
            true_labels, predictions, average="weighted", zero_division=0
        )
        recall_macro = recall_score(
            true_labels, predictions, average="macro", zero_division=0
        )
        recall_weighted = recall_score(
            true_labels, predictions, average="weighted", zero_division=0
        )
        f1_macro = f1_score(
            true_labels, predictions, average="macro", zero_division=0
        )
        f1_weighted = f1_score(
            true_labels, predictions, average="weighted", zero_division=0
        )

        # 每个类别的 F1 分数
        f1_per_class = f1_score(
            true_labels, predictions, average=None, zero_division=0
        )

        return {
            "accuracy": accuracy,
            "precision_macro": precision_macro,
            "precision_weighted": precision_weighted,
            "recall_macro": recall_macro,
            "recall_weighted": recall_weighted,
            "f1_macro": f1_macro,
            "f1_weighted": f1_weighted,
            "f1_per_class": {
                self.label2text[i]: float(f1)
                for i, f1 in enumerate(f1_per_class)
            },
        }

    def generate_confusion_matrix_report(
        self,
        true_labels: List[int],
        predictions: List[int],
    ) -> str:
        """生成混淆矩阵报告"""
        # 混淆矩阵
        cm = confusion_matrix(true_labels, predictions)

        # 分类报告
        report = classification_report(
            true_labels,
            predictions,
            target_names=[
                self.label2text[i] for i in range(self.num_labels)
            ],
            digits=4,
        )

        # 格式化输出
        lines = [
            "=" * 70,
            "混淆矩阵 (Confusion Matrix)",
            "=" * 70,
        ]

        # 表头
        header = "                " + "  ".join(f"{self.label2text[i]:>12}" for i in range(self.num_labels))
        lines.append(header)
        lines.append("Actual " + "-" * 66)

        # 矩阵内容
        for i in range(self.num_labels):
            row = f"{self.label2text[i]:<8}        " + "  ".join(f"{cm[i][j]:>12}" for j in range(self.num_labels))
            lines.append(row)

        lines.append("")
        lines.append("=" * 70)
        lines.append("F1 分数和分类报告")
        lines.append("=" * 70)
        lines.append(report)
        lines.append("=" * 70)

        return "\n".join(lines)

    def check_overfitting(
        self,
        train_result: Dict[str, Any],
        test_result: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """检查过拟合"""
        train_acc = train_result["metrics"]["accuracy"]
        test_acc = test_result["metrics"]["accuracy"]
        diff = train_acc - test_acc

        is_overfitting = diff > self.args.overfitting_threshold

        if is_overfitting:
            message = (
                f"⚠️  检测到过拟合！\n"
                f"  训练集准确率：{train_acc:.4f}\n"
                f"  测试集准确率：{test_acc:.4f}\n"
                f"  差异：{diff:.4f} > {self.args.overfitting_threshold:.2f}"
            )
        else:
            message = (
                f"✓ 过拟合检测通过\n"
                f"  训练集准确率：{train_acc:.4f}\n"
                f"  测试集准确率：{test_acc:.4f}\n"
                f"  差异：{diff:.4f} <= {self.args.overfitting_threshold:.2f}"
            )

        return is_overfitting, message

    def save_report(self, results: Dict[str, Any], output_path: str):
        """保存评估报告"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        report = {
            "metrics": results["metrics"],
            "summary": {
                "accuracy": results["metrics"]["accuracy"],
                "f1_macro": results["metrics"]["f1_macro"],
                "f1_weighted": results["metrics"]["f1_weighted"],
            },
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"评估报告已保存至：{output_path}")


def create_sample_eval_data() -> List[Dict[str, Any]]:
    """创建示例评估数据"""
    return [
        {"text": "日常安全检查发现灭火器压力正常", "label": "LOW"},
        {"text": "发现一处电线老化，需要更换", "label": "MEDIUM"},
        {"text": "检测到烟雾浓度超标，需要立即处理", "label": "HIGH"},
        {"text": "发生严重火灾，火势蔓延迅速", "label": "CRITICAL"},
        {"text": "车间温度 25 度，环境舒适", "label": "LOW"},
        {"text": "有员工未按规定佩戴防护手套", "label": "MEDIUM"},
        {"text": "发现气体泄漏迹象", "label": "HIGH"},
        {"text": "有毒气体大量泄漏，需要紧急疏散", "label": "CRITICAL"},
        {"text": "监控设备运行正常", "label": "LOW"},
        {"text": "安全出口指示灯故障", "label": "MEDIUM"},
        {"text": "高温设备温度异常", "label": "HIGH"},
        {"text": "爆炸危险，立即撤离", "label": "CRITICAL"},
        {"text": "消防设施完好，通道畅通", "label": "LOW"},
        {"text": "化学品存放位置不正确", "label": "MEDIUM"},
        {"text": "消防系统检测到火情前兆", "label": "HIGH"},
        {"text": "多人被困危险区域", "label": "CRITICAL"},
    ]


def main():
    parser = argparse.ArgumentParser(description="风险分级模型评估")

    parser.add_argument(
        "--model-path",
        type=str,
        default="outputs/risk_classification/best_model",
        help="模型路径"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/processed/risk_classification.json",
        help="评估数据路径"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/risk_classification/evaluation",
        help="评估结果输出目录"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="评估批大小"
    )
    parser.add_argument(
        "--overfitting-threshold",
        type=float,
        default=0.1,
        help="过拟合检测阈值"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("风险分级模型评估")
    print("=" * 60)

    # 1. 加载模型
    print(f"\n1. 加载模型：{args.model_path}")

    # 检查模型是否存在
    if not os.path.exists(args.model_path):
        print(f"模型不存在：{args.model_path}")
        print("创建示例模型用于演示...")

        # 创建示例模型（未训练，仅用于演示）
        model = create_risk_classifier()
        label2text = model.model.config.label2text
        text2label = {v: k for k, v in label2text.items()}
    else:
        # 加载训练好的模型
        model = create_risk_classifier()
        model.load_model(args.model_path)
        label2text = model.model.config.label2text
        text2label = {v: k for k, v in label2text.items()}

    # 2. 创建评估器
    evaluator = RiskClassificationEvaluator(
        model=model,
        label2text=label2text,
        text2label=text2label,
        args=EvalArguments(
            model_path=args.model_path,
            data_path=args.data_path,
            output_dir=args.output_dir,
            batch_size=args.batch_size,
            overfitting_threshold=args.overfitting_threshold,
        ),
    )

    # 3. 加载数据
    print(f"\n2. 加载数据：{args.data_path}")

    if not os.path.exists(args.data_path):
        print(f"数据文件不存在，创建示例数据...")
        eval_data = create_sample_eval_data()
        os.makedirs(os.path.dirname(args.data_path), exist_ok=True)
        with open(args.data_path, "w", encoding="utf-8") as f:
            json.dump(eval_data, f, ensure_ascii=False, indent=2)
        print(f"示例数据已保存至：{args.data_path}")
    else:
        eval_data = evaluator.load_data(args.data_path)

    print(f"加载 {len(eval_data)} 条评估数据")

    # 4. 准备数据
    texts, labels = evaluator.prepare_data(eval_data)

    # 5. 执行评估
    print("\n3. 执行评估...")
    results = evaluator.evaluate(texts, labels, batch_size=args.batch_size)

    # 6. 打印结果
    print("\n" + "=" * 60)
    print("评估结果")
    print("=" * 60)

    metrics = results["metrics"]
    print(f"准确率 (Accuracy):    {metrics['accuracy']:.4f}")
    print(f"F1 分数 (Macro):       {metrics['f1_macro']:.4f}")
    print(f"F1 分数 (Weighted):    {metrics['f1_weighted']:.4f}")
    print(f"精确率 (Macro):       {metrics['precision_macro']:.4f}")
    print(f"召回率 (Macro):       {metrics['recall_macro']:.4f}")

    print("\n各类别 F1 分数:")
    for label, f1 in metrics["f1_per_class"].items():
        print(f"  {label}: {f1:.4f}")

    print("\n" + results["confusion_report"])

    # 7. 保存评估报告
    print("\n4. 保存评估报告...")
    report_path = os.path.join(args.output_dir, "evaluation_report.json")
    evaluator.save_report(results, report_path)

    # 8. 保存混淆矩阵报告
    confusion_report_path = os.path.join(args.output_dir, "confusion_matrix_report.txt")
    with open(confusion_report_path, "w", encoding="utf-8") as f:
        f.write(results["confusion_report"])
    print(f"混淆矩阵报告已保存至：{confusion_report_path}")

    print("\n" + "=" * 60)
    print("评估完成!")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
