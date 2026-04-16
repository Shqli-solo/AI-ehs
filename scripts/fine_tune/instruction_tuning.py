#!/usr/bin/env python3
"""
指令微调训练脚本

基于 LoRA 的指令微调，支持：
- 数据加载与预处理
- LoRA 配置
- TensorBoard 日志记录
- 早停（Early Stopping）
- 检查点（Checkpoint）保存与恢复
"""

import os
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    HfArgumentParser,
)
from peft import (
    LoraConfig,
    TaskType,
    get_peft_model,
    prepare_model_for_kbit_training,
    PeftModel,
)
from datasets import load_from_disk, Dataset

# 导入自定义模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.ehs_ai.models.instruction_model import InstructionTuningModel
from src.ehs_ai.models.callbacks import (
    EarlyStoppingCallback,
    CheckpointCallback,
    TrainingProgressCallback,
)


@dataclass
class ModelArguments:
    """模型参数"""
    model_name_or_path: str = field(
        default="Qwen/Qwen2.5-1.5B-Instruct",
        metadata={"help": "预训练模型名称或路径"}
    )
    use_lora: bool = field(
        default=True,
        metadata={"help": "是否使用 LoRA"}
    )
    lora_r: int = field(
        default=8,
        metadata={"help": "LoRA 秩"}
    )
    lora_alpha: int = field(
        default=32,
        metadata={"help": "LoRA alpha 参数"}
    )
    lora_dropout: float = field(
        default=0.1,
        metadata={"help": "LoRA dropout"}
    )
    load_in_4bit: bool = field(
        default=False,
        metadata={"help": "是否使用 4bit 量化"}
    )


@dataclass
class DataArguments:
    """数据参数"""
    data_path: str = field(
        default="data/processed/instruction_tuning.json",
        metadata={"help": "训练数据路径"}
    )
    validation_split: float = field(
        default=0.1,
        metadata={"help": "验证集比例"}
    )
    max_seq_length: int = field(
        default=512,
        metadata={"help": "最大序列长度"}
    )
    overwrite_cache: bool = field(
        default=False,
        metadata={"help": "是否覆盖缓存"}
    )


@dataclass
class TrainingArgs(TrainingArguments):
    """训练参数"""
    output_dir: str = field(
        default="outputs/instruction_tuning",
        metadata={"help": "输出目录"}
    )
    num_train_epochs: int = field(
        default=3,
        metadata={"help": "训练轮数"}
    )
    per_device_train_batch_size: int = field(
        default=4,
        metadata={"help": "训练批大小"}
    )
    per_device_eval_batch_size: int = field(
        default=4,
        metadata={"help": "评估批大小"}
    )
    learning_rate: float = field(
        default=2e-4,
        metadata={"help": "学习率"}
    )
    warmup_ratio: float = field(
        default=0.03,
        metadata={"help": "预热比例"}
    )
    logging_steps: int = field(
        default=10,
        metadata={"help": "日志记录步数"}
    )
    save_steps: int = field(
        default=100,
        metadata={"help": "保存步数"}
    )
    eval_steps: int = field(
        default=100,
        metadata={"help": "评估步数"}
    )
    early_stopping_patience: int = field(
        default=3,
        metadata={"help": "早停 patience"}
    )
    resume_from_checkpoint: bool = field(
        default=False,
        metadata={"help": "是否从检查点恢复"}
    )
    report_to: str = field(
        default="tensorboard",
        metadata={"help": "日志报告工具"}
    )


class InstructionDataset:
    """指令微调数据集"""

    def __init__(
        self,
        data_path: str,
        tokenizer: AutoTokenizer,
        max_seq_length: int = 512,
    ):
        self.data_path = data_path
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length

    def load_data(self) -> Dataset:
        """加载数据"""
        # 加载 JSON 数据
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 转换为 Dataset
        dataset = Dataset.from_list(data)
        return dataset

    def format_sample(self, sample: Dict[str, Any]) -> str:
        """
        格式化样本为训练文本

        使用 ChatML 格式或模型特定格式
        """
        instruction = sample.get("instruction", "")
        input_text = sample.get("input", "")
        output = sample.get("output", "")

        # 构建输入文本
        if input_text:
            prompt = f"""### Instruction:
{instruction}

### Input:
{input_text}

### Response:
{output}"""
        else:
            prompt = f"""### Instruction:
{instruction}

### Response:
{output}"""

        return prompt

    def tokenize(self, sample: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """
        对样本进行分词

        Args:
            sample: 数据样本

        Returns:
            分词后的张量
        """
        formatted_text = self.format_sample(sample)

        # 分词
        encoding = self.tokenizer(
            formatted_text,
            truncation=True,
            max_length=self.max_seq_length,
            padding="max_length",
            return_tensors="pt",
        )

        # 准备标签（用于计算损失）
        input_ids = encoding["input_ids"][0]
        attention_mask = encoding["attention_mask"][0]

        # 标签与输入相同（因果语言建模）
        labels = input_ids.clone()
        # 将 padding 部分的 label 设为 -100（不计入损失）
        labels[attention_mask == 0] = -100

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }

    def prepare(self) -> Dataset:
        """准备数据集"""
        print(f"Loading data from: {self.data_path}")
        dataset = self.load_data()
        print(f"Loaded {len(dataset)} samples")

        # 对数据集进行分词
        print("Tokenizing dataset...")
        tokenized_dataset = dataset.map(
            self.tokenize,
            remove_columns=dataset.column_names,
            desc="Tokenizing"
        )

        return tokenized_dataset


def find_latest_checkpoint(output_dir: str) -> Optional[str]:
    """查找最新的检查点"""
    if not os.path.exists(output_dir):
        return None

    checkpoints = []
    for item in os.listdir(output_dir):
        if item.startswith("checkpoint-"):
            checkpoints.append(os.path.join(output_dir, item))

    if not checkpoints:
        return None

    # 按步数排序
    checkpoints.sort(key=lambda x: int(x.split("-")[-1]))
    return checkpoints[-1]


def train(args: tuple):
    """训练函数"""
    model_args, data_args, training_args = args

    print("=" * 60)
    print("指令微调训练")
    print("=" * 60)
    print(f"模型：{model_args.model_name_or_path}")
    print(f"数据：{data_args.data_path}")
    print(f"输出：{training_args.output_dir}")
    print(f"LoRA: r={model_args.lora_r}, alpha={model_args.lora_alpha}")
    print(f"4bit 量化：{model_args.load_in_4bit}")
    print("=" * 60)

    # 1. 加载模型
    print("\n1. 加载模型...")
    model_wrapper = InstructionTuningModel(
        model_name=model_args.model_name_or_path,
        lora_r=model_args.lora_r,
        lora_alpha=model_args.lora_alpha,
        lora_dropout=model_args.lora_dropout,
        load_in_4bit=model_args.load_in_4bit,
    )
    model_wrapper.load_model()
    model_wrapper.apply_lora()

    model = model_wrapper.get_model()
    tokenizer = model_wrapper.get_tokenizer()

    # 2. 加载数据
    print("\n2. 加载数据...")
    dataset = InstructionDataset(
        data_path=data_args.data_path,
        tokenizer=tokenizer,
        max_seq_length=data_args.max_seq_length,
    )
    full_dataset = dataset.prepare()

    # 划分训练集和验证集
    split = full_dataset.train_test_split(
        test_size=data_args.validation_split,
        seed=42,
    )
    train_dataset = split["train"]
    eval_dataset = split["test"]

    print(f"训练集：{len(train_dataset)} 样本")
    print(f"验证集：{len(eval_dataset)} 样本")

    # 3. 配置回调
    print("\n3. 配置回调...")
    callbacks = [
        EarlyStoppingCallback(patience=training_args.early_stopping_patience),
        CheckpointCallback(
            output_dir=training_args.output_dir,
            save_every_epoch=True,
            save_total_limit=3,
        ),
        TrainingProgressCallback(log_every_steps=training_args.logging_steps),
    ]

    # 4. 创建 Trainer
    print("\n4. 创建 Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,  # 因果语言建模
        ),
        callbacks=callbacks,
    )

    # 5. 从检查点恢复（可选）
    if training_args.resume_from_checkpoint:
        latest_checkpoint = find_latest_checkpoint(training_args.output_dir)
        if latest_checkpoint:
            print(f"\n从检查点恢复：{latest_checkpoint}")
            trainer.train(resume_from_checkpoint=latest_checkpoint)
        else:
            print("未找到检查点，从头开始训练")
            trainer.train()
    else:
        # 6. 开始训练
        print("\n5. 开始训练...")
        trainer.train()

    # 7. 保存模型
    print("\n6. 保存模型...")
    os.makedirs(training_args.output_dir, exist_ok=True)
    model_wrapper.save_adapter(training_args.output_dir)
    tokenizer.save_pretrained(training_args.output_dir)
    print(f"模型已保存至：{training_args.output_dir}")

    # 8. 保存训练历史
    print("\n7. 保存训练历史...")
    history_path = os.path.join(training_args.output_dir, "training_history.json")
    # 从 trainer 状态获取历史
    history = {
        "log_history": trainer.state.log_history,
        "global_step": trainer.state.global_step,
        "epoch": trainer.state.epoch,
    }
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    print(f"训练历史已保存至：{history_path}")

    print("\n" + "=" * 60)
    print("训练完成!")
    print("=" * 60)


def main():
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingArgs))

    # 解析命令行参数
    if len(sys.argv) == 1:
        # 使用默认参数
        model_args = ModelArguments()
        data_args = DataArguments()
        training_args = TrainingArgs()
        args = (model_args, data_args, training_args)
    else:
        args = parser.parse_args_into_dataclasses()

    train(args)


if __name__ == "__main__":
    main()
