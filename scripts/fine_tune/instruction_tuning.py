"""
指令微调 - Qwen-7B

训练目标：规范化结构化 JSON 输出
基础模型：Qwen-7B-Chat (或 HuggingFace 等效)
数据：data/fine_tune/instruction/train.jsonl

用法：
    python scripts/fine_tune/instruction_tuning.py
"""

import sys
import logging
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.fine_tune.train_config import TrainingConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
    from datasets import load_dataset
    from peft import LoraConfig, get_peft_model, TaskType
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("transformers/peft 未安装，仅做配置检查")


def load_instruction_data(data_path: str):
    """加载指令微调数据"""
    dataset = load_dataset("json", data_files=data_path, split="train")
    return dataset


def format_instruction_sample(example):
    """格式化为模型输入"""
    prompt = f"Human: {example['instruction']}\n{example['input']}\n\nAssistant: "
    return {
        "text": prompt + example["output"],
        "prompt": prompt,
        "response": example["output"],
    }


def train(config: TrainingConfig):
    """执行指令微调"""
    if not HAS_TRANSFORMERS:
        logger.info("跳过训练（transformers 未安装）")
        return

    # 加载数据
    train_ds = load_instruction_data(config.train_file)
    train_ds = train_ds.map(format_instruction_sample)

    # 加载模型和 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        config.base_model,
        trust_remote_code=True,
    )
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        config.base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )

    # LoRA 配置
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 训练参数
    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        save_total_limit=3,
        fp16=True,
        remove_unused_columns=False,
    )

    def tokenize_fn(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=config.max_length,
            padding=False,
        )

    tokenized_ds = train_ds.map(tokenize_fn, batched=True, remove_columns=train_ds.column_names)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds,
        tokenizer=tokenizer,
    )

    trainer.train()
    model.save_pretrained(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)
    logger.info(f"模型已保存到 {config.output_dir}")


def main():
    config = TrainingConfig(
        base_model="Qwen/Qwen-7B-Chat",
        output_dir=str(ROOT / "models" / "qwen-ehs-instruct"),
        train_file=str(ROOT / "data" / "fine_tune" / "instruction" / "train.jsonl"),
        eval_file=str(ROOT / "data" / "fine_tune" / "instruction" / "eval.jsonl"),
        num_epochs=3,
        batch_size=4,
        max_length=1024,
    )
    train(config)


if __name__ == "__main__":
    main()
