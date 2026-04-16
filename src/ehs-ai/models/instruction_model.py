"""
EHS 指令微调模型定义

基于 LoRA 的指令微调模型，支持多种预训练语言模型。
"""

import torch
import torch.nn as nn
from typing import Optional, Dict, Any
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer


class InstructionTuningModel:
    """
    指令微调模型类

    封装 LoRA 微调的核心逻辑，支持:
    - 基础模型加载
    - LoRA 配置与应用
    - 训练/评估模式切换
    """

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
        lora_r: int = 8,
        lora_alpha: int = 16,
        lora_dropout: float = 0.05,
        target_modules: Optional[list] = None,
        load_in_4bit: bool = False,
        device_map: str = "auto"
    ):
        """
        初始化指令微调模型

        Args:
            model_name: 预训练模型名称
            lora_r: LoRA 秩
            lora_alpha: LoRA alpha 参数
            lora_dropout: LoRA dropout
            target_modules: 应用 LoRA 的目标模块
            load_in_4bit: 是否使用 4bit 量化加载
            device_map: 设备映射策略
        """
        self.model_name = model_name
        self.lora_config = {
            "r": lora_r,
            "lora_alpha": lora_alpha,
            "lora_dropout": lora_dropout,
            "target_modules": target_modules or self._get_default_target_modules(),
            "bias": "none",
            "task_type": TaskType.CAUSAL_LM,
        }
        self.load_in_4bit = load_in_4bit
        self.device_map = device_map

        self.model = None
        self.tokenizer = None
        self.peft_model = None

    def _get_default_target_modules(self) -> list:
        """获取默认的目标模块列表"""
        return [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]

    def load_model(self) -> None:
        """加载预训练模型和分词器"""
        print(f"Loading model: {self.model_name}")

        # 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            padding_side="right",
        )

        # 设置 pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 加载模型
        if self.load_in_4bit:
            from transformers import BitsAndBytesConfig
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=bnb_config,
                device_map=self.device_map,
                trust_remote_code=True,
                torch_dtype=torch.float16,
            )
            self.model = prepare_model_for_kbit_training(self.model)
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map=self.device_map,
                trust_remote_code=True,
                torch_dtype=torch.float16,
            )

        print(f"Model loaded successfully: {self.model_name}")

    def apply_lora(self) -> None:
        """应用 LoRA 适配器"""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        lora_config = LoraConfig(**self.lora_config)
        self.peft_model = get_peft_model(self.model, lora_config)

        # 打印可训练参数
        self.peft_model.print_trainable_parameters()
        print("LoRA adapter applied successfully")

    def get_model(self):
        """获取模型实例"""
        return self.peft_model if self.peft_model else self.model

    def get_tokenizer(self):
        """获取分词器"""
        return self.tokenizer

    def set_train_mode(self) -> None:
        """设置为训练模式"""
        model = self.get_model()
        if model:
            model.train()

    def set_eval_mode(self) -> None:
        """设置为评估模式"""
        model = self.get_model()
        if model:
            model.eval()

    def save_adapter(self, output_dir: str) -> None:
        """保存 LoRA 适配器"""
        if self.peft_model:
            self.peft_model.save_pretrained(output_dir)
            print(f"LoRA adapter saved to: {output_dir}")
        else:
            print("No PEFT model to save")

    def load_adapter(self, adapter_path: str) -> None:
        """加载 LoRA 适配器"""
        from peft import PeftModel
        if self.model is None:
            raise RuntimeError("Base model not loaded")
        self.peft_model = PeftModel.from_pretrained(self.model, adapter_path)
        print(f"LoRA adapter loaded from: {adapter_path}")


def create_instruction_model(
    model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
    lora_r: int = 8,
    lora_alpha: int = 32,
    lora_dropout: float = 0.1,
    **kwargs
) -> InstructionTuningModel:
    """
    创建指令微调模型的工厂函数

    Args:
        model_name: 预训练模型名称
        lora_r: LoRA 秩
        lora_alpha: LoRA alpha 参数
        lora_dropout: LoRA dropout
        **kwargs: 其他参数

    Returns:
        InstructionTuningModel 实例
    """
    return InstructionTuningModel(
        model_name=model_name,
        lora_r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        **kwargs
    )
