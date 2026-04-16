#!/usr/bin/env python3
"""
术语 Embedding 微调训练脚本

基于对比学习（Contrastive Learning）的术语 Embedding 微调，支持：
- 同义词/上下位词对训练
- InfoNCE 损失函数
- 硬负例挖掘（Hard Negative Mining）
- TensorBoard 日志记录
- 模型评估与验证
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
from transformers import AutoTokenizer, AutoModel
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig


@dataclass
class ModelArguments:
    """模型参数"""
    model_name_or_path: str = field(
        default="BAAI/bge-base-zh-v1.5",
        metadata={"help": "预训练模型名称或路径"}
    )
    embedding_dim: int = field(
        default=768,
        metadata={"help": "Embedding 维度"}
    )
    max_seq_length: int = field(
        default=512,
        metadata={"help": "最大序列长度"}
    )


@dataclass
class DataArguments:
    """数据参数"""
    data_path: str = field(
        default="data/processed/embedding_terms.json",
        metadata={"help": "训练数据路径"}
    )
    test_split: float = field(
        default=0.2,
        metadata={"help": "测试集比例"}
    )
    val_split: float = field(
        default=0.1,
        metadata={"help": "验证集比例"}
    )
    hard_negative_mining: bool = field(
        default=True,
        metadata={"help": "是否使用硬负例挖掘"}
    )
    seed: int = field(
        default=42,
        metadata={"help": "随机种子"}
    )


@dataclass
class TrainingArgs:
    """训练参数"""
    output_dir: str = field(
        default="outputs/embedding_tuning",
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
    temperature: float = field(
        default=0.07,
        metadata={"help": "InfoNCE 损失温度参数"}
    )
    early_stopping_patience: int = field(
        default=3,
        metadata={"help": "早停 patience"}
    )
    save_steps: int = field(
        default=1,
        metadata={"help": "保存步数（以 epoch 为单位）"}
    )
    logging_steps: int = field(
        default=10,
        metadata={"help": "日志记录步数"}
    )
    similarity_threshold: float = field(
        default=0.5,
        metadata={"help": "相似度阈值"}
    )


class TermPairDataset(Dataset):
    """术语对数据集"""

    def __init__(
        self,
        data: List[Dict[str, Any]],
        tokenizer: AutoTokenizer,
        max_seq_length: int = 512,
    ):
        self.data = data
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.data[idx]

        # 获取术语对
        anchor_text = item.get("anchor", item.get("term1", ""))
        positive_text = item.get("positive", item.get("term2", ""))

        # 获取负例（可选）
        negative_texts = item.get("negatives", [])

        # 分词
        anchor_encoding = self.tokenizer(
            anchor_text,
            max_length=self.max_seq_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        positive_encoding = self.tokenizer(
            positive_text,
            max_length=self.max_seq_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        result = {
            "anchor_input_ids": anchor_encoding["input_ids"].squeeze(0),
            "anchor_attention_mask": anchor_encoding["attention_mask"].squeeze(0),
            "positive_input_ids": positive_encoding["input_ids"].squeeze(0),
            "positive_attention_mask": positive_encoding["attention_mask"].squeeze(0),
        }

        # 添加负例
        if negative_texts:
            negative_encodings = self.tokenizer(
                negative_texts,
                max_length=self.max_seq_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            result["negative_input_ids"] = negative_encodings["input_ids"]
            result["negative_attention_mask"] = negative_encodings["attention_mask"]

        return result


class ContrastiveLoss(nn.Module):
    """
    对比损失（InfoNCE Loss）

    用于训练 Embedding 模型，使相似术语的向量更接近，不相似的更远离。
    """

    def __init__(self, temperature: float = 0.07):
        super().__init__()
        self.temperature = temperature
        self.cross_entropy = nn.CrossEntropyLoss()

    def forward(
        self,
        anchor_embeddings: torch.Tensor,
        positive_embeddings: torch.Tensor,
        negative_embeddings: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        计算对比损失

        Args:
            anchor_embeddings: Anchor 向量 (batch_size, dim)
            positive_embeddings: Positive 向量 (batch_size, dim)
            negative_embeddings: Negative 向量 (batch_size, n_negatives, dim)

        Returns:
            损失值
        """
        batch_size = anchor_embeddings.size(0)

        # 归一化
        anchor_embeddings = nn.functional.normalize(anchor_embeddings, p=2, dim=1)
        positive_embeddings = nn.functional.normalize(positive_embeddings, p=2, dim=1)

        if negative_embeddings is not None:
            # 有负例的情况
            n_negatives = negative_embeddings.size(1)

            # 归一化负例
            negative_embeddings = nn.functional.normalize(negative_embeddings, p=2, dim=2)

            # 计算相似度矩阵
            # positive similarities: (batch_size,)
            pos_sim = (anchor_embeddings * positive_embeddings).sum(dim=1) / self.temperature

            # negative similarities: (batch_size, n_negatives)
            neg_sim = torch.bmm(
                anchor_embeddings.unsqueeze(1),
                negative_embeddings.transpose(1, 2)
            ).squeeze(1) / self.temperature

            # 构建 logits 和 labels
            # logits: (batch_size, 1 + n_negatives)
            logits = torch.cat([pos_sim.unsqueeze(1), neg_sim], dim=1)
            labels = torch.zeros(batch_size, dtype=torch.long, device=anchor_embeddings.device)

            loss = self.cross_entropy(logits, labels)
        else:
            # 无负例的情况（只有 anchor-positive 对）
            # 使用 batch 内其他样本作为负例
            all_embeddings = torch.cat([anchor_embeddings, positive_embeddings], dim=0)
            sim_matrix = torch.matmul(all_embeddings, all_embeddings.T) / self.temperature

            # 对角线元素是正例对
            labels = torch.arange(batch_size, dtype=torch.long, device=anchor_embeddings.device)

            # 构造扩展的 labels
            extended_labels = torch.cat([labels, labels + batch_size], dim=0)

            loss = self.cross_entropy(sim_matrix, extended_labels)

        return loss


class EmbeddingTrainer:
    """Embedding 训练器"""

    def __init__(
        self,
        model: EmbeddingModel,
        train_dataset: TermPairDataset,
        eval_dataset: TermPairDataset,
        test_dataset: TermPairDataset,
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
        self.best_eval_loss = float("inf")
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

    def train_epoch(
        self,
        dataloader: DataLoader,
        criterion: ContrastiveLoss,
    ) -> Tuple[float, List]:
        """训练一个 epoch"""
        self.model.model.train()

        total_loss = 0.0
        all_results = []

        for batch in dataloader:
            # 移动到设备
            anchor_input_ids = batch["anchor_input_ids"].to(self.device)
            anchor_attention_mask = batch["anchor_attention_mask"].to(self.device)
            positive_input_ids = batch["positive_input_ids"].to(self.device)
            positive_attention_mask = batch["positive_attention_mask"].to(self.device)

            # 获取负例
            negative_input_ids = batch.get("negative_input_ids")
            negative_attention_mask = batch.get("negative_attention_mask")

            self.optimizer.zero_grad()

            # 获取 Anchor 和 Positive 向量
            with torch.autocast(device_type=self.device.type if self.device.type != "cpu" else "cpu"):
                anchor_outputs = self.model.model(
                    input_ids=anchor_input_ids,
                    attention_mask=anchor_attention_mask,
                )
                anchor_embeddings = anchor_outputs.last_hidden_state[:, 0, :]

                positive_outputs = self.model.model(
                    input_ids=positive_input_ids,
                    attention_mask=positive_attention_mask,
                )
                positive_embeddings = positive_outputs.last_hidden_state[:, 0, :]

                # 获取 Negative 向量
                negative_embeddings = None
                if negative_input_ids is not None:
                    batch_size = negative_input_ids.size(0)
                    n_negatives = negative_input_ids.size(1)

                    # 重塑为 (batch_size * n_negatives, seq_len)
                    neg_input_ids = negative_input_ids.view(-1, negative_input_ids.size(-1))
                    neg_attention_mask = negative_attention_mask.view(-1, negative_attention_mask.size(-1))

                    neg_outputs = self.model.model(
                        input_ids=neg_input_ids,
                        attention_mask=neg_attention_mask,
                    )
                    neg_embeddings = neg_outputs.last_hidden_state[:, 0, :]

                    # 重塑回 (batch_size, n_negatives, dim)
                    negative_embeddings = neg_embeddings.view(batch_size, n_negatives, -1)

                # 计算损失
                loss = criterion(anchor_embeddings, positive_embeddings, negative_embeddings)

            # 反向传播
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.model.parameters(), 1.0)
            self.optimizer.step()
            self.scheduler.step()

            total_loss += loss.item()
            all_results.append({
                "loss": loss.item(),
            })

        avg_loss = total_loss / len(dataloader)
        return avg_loss, all_results

    @torch.no_grad()
    def evaluate(
        self,
        dataloader: DataLoader,
        criterion: ContrastiveLoss,
    ) -> Tuple[float, List]:
        """评估"""
        self.model.model.eval()

        total_loss = 0.0
        all_results = []

        for batch in dataloader:
            anchor_input_ids = batch["anchor_input_ids"].to(self.device)
            anchor_attention_mask = batch["anchor_attention_mask"].to(self.device)
            positive_input_ids = batch["positive_input_ids"].to(self.device)
            positive_attention_mask = batch["positive_attention_mask"].to(self.device)

            negative_input_ids = batch.get("negative_input_ids")
            negative_attention_mask = batch.get("negative_attention_mask")

            anchor_outputs = self.model.model(
                input_ids=anchor_input_ids,
                attention_mask=anchor_attention_mask,
            )
            anchor_embeddings = anchor_outputs.last_hidden_state[:, 0, :]

            positive_outputs = self.model.model(
                input_ids=positive_input_ids,
                attention_mask=positive_attention_mask,
            )
            positive_embeddings = positive_outputs.last_hidden_state[:, 0, :]

            negative_embeddings = None
            if negative_input_ids is not None:
                batch_size = negative_input_ids.size(0)
                n_negatives = negative_input_ids.size(1)

                neg_input_ids = negative_input_ids.view(-1, negative_input_ids.size(-1))
                neg_attention_mask = negative_attention_mask.view(-1, negative_attention_mask.size(-1))

                neg_outputs = self.model.model(
                    input_ids=neg_input_ids,
                    attention_mask=neg_attention_mask,
                )
                neg_embeddings = neg_outputs.last_hidden_state[:, 0, :]
                negative_embeddings = neg_embeddings.view(batch_size, n_negatives, -1)

            loss = criterion(anchor_embeddings, positive_embeddings, negative_embeddings)
            total_loss += loss.item()
            all_results.append({
                "loss": loss.item(),
            })

        avg_loss = total_loss / len(dataloader)
        return avg_loss, all_results

    def train(self) -> Dict[str, Any]:
        """开始训练"""
        print("\n" + "=" * 60)
        print("术语 Embedding 微调训练")
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
            collate_fn=self._collate_fn,
        )
        eval_loader = DataLoader(
            self.eval_dataset,
            batch_size=self.args.batch_size,
            shuffle=False,
            num_workers=0,
            collate_fn=self._collate_fn,
        )

        # 创建损失函数
        criterion = ContrastiveLoss(temperature=self.args.temperature)

        # 训练循环
        print("\n开始训练...")
        for epoch in range(self.args.num_train_epochs):
            print(f"\nEpoch {epoch + 1}/{self.args.num_train_epochs}")
            print("-" * 40)

            # 训练
            train_loss, train_results = self.train_epoch(train_loader, criterion)
            self.train_losses.append(train_loss)

            # 评估
            eval_loss, eval_results = self.evaluate(eval_loader, criterion)
            self.eval_losses.append(eval_loss)

            # 打印进度
            print(f"Train Loss: {train_loss:.4f}")
            print(f"Eval Loss: {eval_loss:.4f}")

            # 早停检查
            if eval_loss < self.best_eval_loss:
                self.best_eval_loss = eval_loss
                self.patience_counter = 0
                # 保存最佳模型
                self.model.save_model(os.path.join(self.args.output_dir, "best_model"))
                print(f"✓ 保存最佳模型 (eval_loss: {eval_loss:.4f})")
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
            "best_eval_loss": self.best_eval_loss,
            "train_losses": self.train_losses,
            "eval_losses": self.eval_losses,
        }

    def _collate_fn(self, batch):
        """批量数据整理"""
        anchor_input_ids = torch.stack([item["anchor_input_ids"] for item in batch])
        anchor_attention_mask = torch.stack([item["anchor_attention_mask"] for item in batch])
        positive_input_ids = torch.stack([item["positive_input_ids"] for item in batch])
        positive_attention_mask = torch.stack([item["positive_attention_mask"] for item in batch])

        result = {
            "anchor_input_ids": anchor_input_ids,
            "anchor_attention_mask": anchor_attention_mask,
            "positive_input_ids": positive_input_ids,
            "positive_attention_mask": positive_attention_mask,
        }

        # 处理负例
        if "negative_input_ids" in batch[0] and batch[0]["negative_input_ids"] is not None:
            max_negatives = max(item["negative_input_ids"].size(0) for item in batch)
            negative_input_ids_list = []
            negative_attention_mask_list = []

            for item in batch:
                neg_ids = item["negative_input_ids"]
                neg_mask = item["negative_attention_mask"]

                # Padding 到最大负例数
                if neg_ids.size(0) < max_negatives:
                    pad_size = max_negatives - neg_ids.size(0)
                    pad_ids = torch.zeros(
                        pad_size, neg_ids.size(1),
                        dtype=neg_ids.dtype
                    )
                    pad_mask = torch.zeros(
                        pad_size, neg_mask.size(1),
                        dtype=neg_mask.dtype
                    )
                    neg_ids = torch.cat([neg_ids, pad_ids], dim=0)
                    neg_mask = torch.cat([neg_mask, pad_mask], dim=0)

                negative_input_ids_list.append(neg_ids)
                negative_attention_mask_list.append(neg_mask)

            result["negative_input_ids"] = torch.stack(negative_input_ids_list)
            result["negative_attention_mask"] = torch.stack(negative_attention_mask_list)

        return result

    def _final_evaluation(self):
        """最终测试集评估"""
        test_loader = DataLoader(
            self.test_dataset,
            batch_size=self.args.batch_size,
            shuffle=False,
            num_workers=0,
            collate_fn=self._collate_fn,
        )

        criterion = ContrastiveLoss(temperature=self.args.temperature)
        test_loss, _ = self.evaluate(test_loader, criterion)

        print(f"Test Loss: {test_loss:.4f}")

        return {
            "test_loss": test_loss,
        }

    def _save_training_history(self):
        """保存训练历史"""
        os.makedirs(self.args.output_dir, exist_ok=True)

        history = {
            "train_losses": self.train_losses,
            "eval_losses": self.eval_losses,
            "best_eval_loss": self.best_eval_loss,
            "config": {
                "model_name": self.model.config.model_name,
                "max_seq_length": self.model.config.max_seq_length,
                "temperature": self.args.temperature,
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
    # EHS 术语对示例
    term_pairs = [
        # 同义词对
        {"anchor": "火灾", "positive": "火情", "relation": "synonym", "negatives": ["水灾", "地震"]},
        {"anchor": "泄漏", "positive": "泄露", "relation": "synonym", "negatives": ["爆炸", "燃烧"]},
        {"anchor": "危险", "positive": "风险", "relation": "synonym", "negatives": ["安全", "防护"]},
        {"anchor": "事故", "positive": "事件", "relation": "synonym", "negatives": ["预防", "应急"]},
        {"anchor": "烟雾", "positive": "烟尘", "relation": "synonym", "negatives": ["火焰", "高温"]},

        # 上下位词对
        {"anchor": "气体泄漏", "positive": "氯气泄漏", "relation": "hypernym", "negatives": ["固体泄漏", "液体泄漏"]},
        {"anchor": "火灾", "positive": "电气火灾", "relation": "hypernym", "negatives": ["水灾", "地震"]},
        {"anchor": "化学品事故", "positive": "硫酸泄漏", "relation": "hypernym", "negatives": ["机械事故", "电气事故"]},
        {"anchor": "中毒", "positive": "一氧化碳中毒", "relation": "hypernym", "negatives": ["烧伤", "割伤"]},
        {"anchor": "爆炸", "positive": "气体爆炸", "relation": "hypernym", "negatives": ["火灾", "泄漏"]},

        # 相关术语
        {"anchor": "灭火器", "positive": "干粉灭火器", "relation": "related", "negatives": ["消防栓", "水带"]},
        {"anchor": "防护服", "positive": "防化服", "relation": "related", "negatives": ["安全帽", "手套"]},
        {"anchor": "应急预案", "positive": "疏散预案", "relation": "related", "negatives": ["培训计划", "检查记录"]},
        {"anchor": "风险评估", "positive": "隐患排查", "relation": "related", "negatives": ["事故报告", "整改通知"]},
        {"anchor": "安全培训", "positive": "应急演练", "relation": "related", "negatives": ["设备维护", "定期检查"]},
    ]

    # 添加更多变体
    data = []
    for pair in term_pairs:
        for i in range(3):
            data.append({
                "anchor": pair["anchor"] + f" {i + 1}",
                "positive": pair["positive"] + f" {i + 1}",
                "relation": pair["relation"],
                "negatives": pair["negatives"],
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
    from sklearn.model_selection import train_test_split

    # 先划分出测试集
    train_data, test_data = train_test_split(
        data,
        test_size=test_split,
        random_state=seed,
    )

    # 再从训练集中划分出验证集
    val_ratio = val_split / (1 - test_split)
    train_data, eval_data = train_test_split(
        train_data,
        test_size=val_ratio,
        random_state=seed,
    )

    return list(train_data), list(eval_data), list(test_data)


def main():
    parser = argparse.ArgumentParser(description="术语 Embedding 微调训练")

    # 模型参数
    parser.add_argument("--model-name", type=str, default="BAAI/bge-base-zh-v1.5")
    parser.add_argument("--max-seq-length", type=int, default=512)

    # 数据参数
    parser.add_argument("--data-path", type=str, default="data/processed/embedding_terms.json")
    parser.add_argument("--test-split", type=float, default=0.2)
    parser.add_argument("--val-split", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)

    # 训练参数
    parser.add_argument("--output-dir", type=str, default="outputs/embedding_tuning")
    parser.add_argument("--num-epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--temperature", type=float, default=0.07)
    parser.add_argument("--early-stopping-patience", type=int, default=3)
    parser.add_argument("--similarity-threshold", type=float, default=0.5)

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
    config = EmbeddingConfig(
        model_name=args.model_name,
        max_seq_length=args.max_seq_length,
        similarity_threshold=args.similarity_threshold,
    )
    model = EmbeddingModel(config)
    model.load_model()

    # 4. 创建数据集
    tokenizer = model.tokenizer

    train_dataset = TermPairDataset(train_data, tokenizer, args.max_seq_length)
    eval_dataset = TermPairDataset(eval_data, tokenizer, args.max_seq_length)
    test_dataset = TermPairDataset(test_data, tokenizer, args.max_seq_length)

    # 5. 创建训练器
    training_args = TrainingArgs(
        output_dir=args.output_dir,
        num_train_epochs=args.num_epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        temperature=args.temperature,
        early_stopping_patience=args.early_stopping_patience,
        similarity_threshold=args.similarity_threshold,
    )

    trainer = EmbeddingTrainer(
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
    print(f"最佳验证损失：{results['best_eval_loss']:.4f}")


if __name__ == "__main__":
    main()
