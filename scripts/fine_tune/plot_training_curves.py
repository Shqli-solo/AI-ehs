#!/usr/bin/env python3
"""
训练曲线可视化脚本

从 TensorBoard 日志或训练历史中读取数据，生成训练曲线图。
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def load_training_history(history_path: str) -> Dict[str, Any]:
    """
    加载训练历史

    Args:
        history_path: training_history.json 路径

    Returns:
        训练历史字典
    """
    with open(history_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_metrics(log_history: List[Dict]) -> Dict[str, List]:
    """
    从日志历史中提取指标

    Args:
        log_history: Trainer 日志历史

    Returns:
        指标字典
    """
    train_losses = []
    train_steps = []
    eval_losses = []
    eval_steps = []
    learning_rates = []
    epochs = []

    for entry in log_history:
        if "loss" in entry:
            # 训练损失
            train_losses.append(entry["loss"])
            train_steps.append(entry.get("step", 0))
            if "learning_rate" in entry:
                learning_rates.append(entry["learning_rate"])
            if "epoch" in entry:
                epochs.append(entry["epoch"])

        if "eval_loss" in entry:
            # 评估损失
            eval_losses.append(entry["eval_loss"])
            eval_steps.append(entry.get("step", 0))

    return {
        "train_losses": train_losses,
        "train_steps": train_steps,
        "eval_losses": eval_losses,
        "eval_steps": eval_steps,
        "learning_rates": learning_rates,
        "epochs": epochs,
    }


def plot_training_curves(
    metrics: Dict[str, List],
    output_dir: str,
    title: str = "Instruction Tuning Training Curves"
):
    """
    绘制训练曲线

    Args:
        metrics: 指标字典
        output_dir: 输出目录
        title: 图表标题
    """
    os.makedirs(output_dir, exist_ok=True)

    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16)

    # 1. 训练损失和评估损失
    ax1 = axes[0, 0]
    if metrics["train_losses"]:
        ax1.plot(
            metrics["train_steps"],
            metrics["train_losses"],
            "b-",
            label="Train Loss",
            linewidth=2,
            marker="o",
            markersize=3,
        )
    if metrics["eval_losses"]:
        ax1.plot(
            metrics["eval_steps"],
            metrics["eval_losses"],
            "r-",
            label="Eval Loss",
            linewidth=2,
            marker="s",
            markersize=3,
        )
    ax1.set_xlabel("Training Steps")
    ax1.set_ylabel("Loss")
    ax1.set_title("Training & Evaluation Loss")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. 学习率变化
    ax2 = axes[0, 1]
    if metrics["learning_rates"]:
        steps = metrics["train_steps"][: len(metrics["learning_rates"])]
        ax2.plot(
            steps,
            metrics["learning_rates"],
            "g-",
            label="Learning Rate",
            linewidth=2,
        )
        ax2.set_xlabel("Training Steps")
        ax2.set_ylabel("Learning Rate")
        ax2.set_title("Learning Rate Schedule")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

    # 3. 训练损失（按 epoch）
    ax3 = axes[1, 0]
    if metrics["epochs"] and metrics["train_losses"]:
        # 只取 epochs 和 losses 的交集
        min_len = min(len(metrics["epochs"]), len(metrics["train_losses"]))
        ax3.plot(
            metrics["epochs"][:min_len],
            metrics["train_losses"][:min_len],
            "b-o",
            label="Train Loss per Epoch",
            linewidth=2,
        )
        ax3.set_xlabel("Epoch")
        ax3.set_ylabel("Loss")
        ax3.set_title("Loss per Epoch")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

    # 4. 评估损失趋势
    ax4 = axes[1, 1]
    if metrics["eval_losses"]:
        eval_epochs = [
            i * (metrics["epochs"][-1] / len(metrics["eval_losses"]))
            if metrics["epochs"]
            else i
            for i in range(1, len(metrics["eval_losses"]) + 1)
        ]
        ax4.plot(
            eval_epochs,
            metrics["eval_losses"],
            "r-s",
            label="Eval Loss",
            linewidth=2,
        )
        # 标记最佳点
        best_idx = metrics["eval_losses"].index(min(metrics["eval_losses"]))
        ax4.scatter(
            [eval_epochs[best_idx]],
            [metrics["eval_losses"][best_idx]],
            color="green",
            s=100,
            label=f"Best: {metrics['eval_losses'][best_idx]:.4f}",
            zorder=5,
        )
        ax4.set_xlabel("Epoch")
        ax4.set_ylabel("Eval Loss")
        ax4.set_title("Evaluation Loss Trend")
        ax4.legend()
        ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    # 保存图表
    output_path = os.path.join(output_dir, "training_curves.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"训练曲线图已保存至：{output_path}")

    plt.close()


def plot_loss_comparison(
    metrics: Dict[str, List],
    output_dir: str
):
    """
    绘制损失对比图（训练 vs 评估）

    Args:
        metrics: 指标字典
        output_dir: 输出目录
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    if metrics["train_losses"]:
        ax.plot(
            metrics["train_steps"],
            metrics["train_losses"],
            "b-",
            alpha=0.7,
            label="Train Loss",
        )
    if metrics["eval_losses"]:
        ax.plot(
            metrics["eval_steps"],
            metrics["eval_losses"],
            "r-",
            alpha=0.7,
            label="Eval Loss",
        )

    ax.set_xlabel("Training Steps")
    ax.set_ylabel("Loss")
    ax.set_title("Training vs Evaluation Loss Comparison")
    ax.legend()
    ax.grid(True, alpha=0.3)

    output_path = os.path.join(output_dir, "loss_comparison.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"损失对比图已保存至：{output_path}")
    plt.close()


def generate_summary(metrics: Dict[str, List]) -> Dict[str, Any]:
    """
    生成训练摘要

    Args:
        metrics: 指标字典

    Returns:
        摘要字典
    """
    summary = {}

    if metrics["train_losses"]:
        summary["train_loss"] = {
            "initial": metrics["train_losses"][0] if metrics["train_losses"] else None,
            "final": metrics["train_losses"][-1] if metrics["train_losses"] else None,
            "min": min(metrics["train_losses"]),
            "max": max(metrics["train_losses"]),
        }

    if metrics["eval_losses"]:
        best_idx = metrics["eval_losses"].index(min(metrics["eval_losses"]))
        summary["eval_loss"] = {
            "initial": metrics["eval_losses"][0] if metrics["eval_losses"] else None,
            "final": metrics["eval_losses"][-1] if metrics["eval_losses"] else None,
            "min": min(metrics["eval_losses"]),
            "best_step": metrics["eval_steps"][best_idx] if metrics.get("eval_steps") and best_idx < len(metrics["eval_steps"]) else None,
        }

    if metrics["learning_rates"]:
        summary["learning_rate"] = {
            "initial": metrics["learning_rates"][0] if metrics["learning_rates"] else None,
            "final": metrics["learning_rates"][-1] if metrics["learning_rates"] else None,
        }

    return summary


def print_summary(summary: Dict[str, Any]):
    """打印训练摘要"""
    print("\n" + "=" * 50)
    print("训练摘要")
    print("=" * 50)

    if "train_loss" in summary:
        print(f"\n训练损失:")
        print(f"  初始：{summary['train_loss']['initial']:.4f}")
        print(f"  最终：{summary['train_loss']['final']:.4f}")
        print(f"  最小：{summary['train_loss']['min']:.4f}")
        print(f"  最大：{summary['train_loss']['max']:.4f}")
        if summary['train_loss']['initial'] and summary['train_loss']['final']:
            reduction = (summary['train_loss']['initial'] - summary['train_loss']['final']) / summary['train_loss']['initial'] * 100
            print(f"  下降：{reduction:.2f}%")

    if "eval_loss" in summary:
        print(f"\n评估损失:")
        print(f"  初始：{summary['eval_loss']['initial']:.4f}")
        print(f"  最终：{summary['eval_loss']['final']:.4f}")
        print(f"  最佳：{summary['eval_loss']['min']:.4f} (step {summary['eval_loss']['best_step']})")

    if "learning_rate" in summary:
        print(f"\n学习率:")
        print(f"  初始：{summary['learning_rate']['initial']:.2e}")
        print(f"  最终：{summary['learning_rate']['final']:.2e}")

    print("\n" + "=" * 50)


def main():
    parser = argparse.ArgumentParser(description="训练曲线可视化工具")
    parser.add_argument(
        "--history_path",
        type=str,
        default="outputs/instruction_tuning/training_history.json",
        help="训练历史文件路径"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="outputs/instruction_tuning/visualizations",
        help="输出目录"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="EHS 指令微调训练曲线",
        help="图表标题"
    )

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.history_path):
        print(f"错误：训练历史文件不存在：{args.history_path}")
        return 1

    # 加载训练历史
    print(f"加载训练历史：{args.history_path}")
    history = load_training_history(args.history_path)

    # 提取指标
    log_history = history.get("log_history", [])
    metrics = extract_metrics(log_history)

    # 打印摘要
    summary = generate_summary(metrics)
    print_summary(summary)

    # 绘制图表
    print("\n生成可视化图表...")
    plot_training_curves(metrics, args.output_dir, title=args.title)
    plot_loss_comparison(metrics, args.output_dir)

    # 保存摘要
    summary_path = os.path.join(args.output_dir, "training_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"训练摘要已保存至：{summary_path}")

    print("\n可视化完成!")
    return 0


if __name__ == "__main__":
    exit(main())
