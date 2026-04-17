"""通用训练配置"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TrainingConfig:
    """训练参数配置"""
    base_model: str = ""
    output_dir: str = ""
    num_epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 2e-5
    max_length: int = 512
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    train_file: str = ""
    eval_file: str = ""
    device: str = "cuda"
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 50
    seed: int = 42
    gradient_accumulation_steps: int = 1
