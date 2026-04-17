"""
风险分级微调 - BERT

训练目标：三分类（low=0/medium=1/high=2）
基础模型：bert-base-chinese
数据：data/fine_tune/risk/train.jsonl

用法：
    python scripts/fine_tune/risk_classification.py
"""

import sys
import json
import logging
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.fine_tune.train_config import TrainingConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

try:
    import torch
    from torch.utils.data import Dataset
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer,
    )
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("transformers 未安装，仅做配置检查")


class RiskDataset(Dataset):
    """风险分级数据集"""

    def __init__(self, data_path: str, tokenizer, max_length: int = 128):
        self.examples = []
        with open(data_path, encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                self.examples.append(item)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        item = self.examples[idx]
        encoding = self.tokenizer(
            item["text"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(item["label"], dtype=torch.long),
        }


def train(config: TrainingConfig):
    """执行风险分级微调"""
    if not HAS_TRANSFORMERS:
        logger.info("跳过训练（transformers 未安装）")
        return

    tokenizer = AutoTokenizer.from_pretrained(config.base_model)
    model = AutoModelForSequenceClassification.from_pretrained(
        config.base_model,
        num_labels=3,  # low=0, medium=1, high=2
    )

    train_dataset = RiskDataset(config.train_file, tokenizer, config.max_length)

    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        save_total_limit=3,
        evaluation_strategy="no",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
    )

    trainer.train()
    model.save_pretrained(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)
    logger.info(f"模型已保存到 {config.output_dir}")


def main():
    config = TrainingConfig(
        base_model="bert-base-chinese",
        output_dir=str(ROOT / "models" / "bert-risk-classifier"),
        train_file=str(ROOT / "data" / "fine_tune" / "risk" / "train.jsonl"),
        eval_file=str(ROOT / "data" / "fine_tune" / "risk" / "eval.jsonl"),
        num_epochs=3,
        batch_size=16,
        max_length=128,
    )
    train(config)


if __name__ == "__main__":
    main()
