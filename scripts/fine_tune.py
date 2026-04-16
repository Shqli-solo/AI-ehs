#!/usr/bin/env python3
"""
EHS 智能安保决策中台 - 模型微调脚本

职责：
1. 使用种子数据生成 instruction-tuning 格式数据
2. 提供 LoRA 微调训练代码框架
3. 导出为 Ollama 可导入的 GGUF 格式

用法:
    python scripts/fine_tune.py generate    # 生成微调数据
    python scripts/fine_tune.py train        # 训练（需安装 unsloth/LLaMA-Factory）
    python scripts/fine_tune.py export       # 导出 GGUF

微调说明：
- 基础模型: Qwen2.5-7B / Qwen3-7B
- 微调方法: LoRA (低秩适配)
- 工具: unsloth 或 LLaMA-Factory
- 数据量: 500-1000 条指令数据
- 输出: GGUF 格式，可直接导入 Ollama
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

SEED_DIR = Path(__file__).parent.parent / "data" / "seed"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "fine_tune"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================
# 指令微调数据生成
# ============================================

def generate_instruction_data() -> List[Dict[str, str]]:
    """
    生成 instruction-tuning 格式数据

    数据格式：
    {
        "instruction": "评估以下 EHS 告警的风险等级",
        "input": "A栋3楼检测到烟雾，温度38°C",
        "output": "风险等级: high\n置信度: 0.85\n因素: [...]\n建议: [...]"
    }
    """
    logger.info("生成指令微调数据...")
    instructions = []

    # 1. 从告警种子数据生成风险评估指令
    alerts_file = SEED_DIR / "alerts.jsonl"
    if alerts_file.exists():
        with open(alerts_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                alert = json.loads(line)

                # 风险评估指令
                instructions.append({
                    "instruction": "评估以下 EHS 告警的风险等级，并给出处置建议",
                    "input": (
                        f"告警类型: {alert['alert_type']}\n"
                        f"位置: {alert['location']}\n"
                        f"告警内容: {alert['alert_content']}\n"
                        f"设备类型: {alert['device_type']}"
                    ),
                    "output": (
                        f"风险等级: {['low', 'medium', 'high', 'critical'][alert['alert_level'] - 1]}\n"
                        f"置信度: 0.{alert['alert_level'] * 20 + 10}\n"
                        f"因素: ['{alert['alert_type']}', '{alert['location']}']\n"
                        f"建议: 立即启动相应的应急预案，通知相关人员"
                    ),
                })

    # 2. 从预案数据生成预案检索指令
    plans_file = SEED_DIR / "plans.jsonl"
    if plans_file.exists():
        with open(plans_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                plan = json.loads(line)

                # 预案检索指令
                instructions.append({
                    "instruction": "根据以下事件描述，检索最相关的应急预案",
                    "input": f"事件: {plan['event_type']}，位置: {plan['location']}",
                    "output": (
                        f"匹配预案: {plan['title']}\n"
                        f"风险等级: {plan['risk_level']}\n"
                        f"处置流程:\n{plan['content']}"
                    ),
                })

                # 预案生成指令
                instructions.append({
                    "instruction": "为以下场景编写应急处置流程",
                    "input": f"场景: {plan['location']}发生{plan['event_type']}",
                    "output": plan['content'],
                })

    # 3. 知识图谱关系查询指令
    kg_file = SEED_DIR / "knowledge_graph.json"
    if kg_file.exists():
        with open(kg_file, "r", encoding="utf-8") as f:
            kg_data = json.load(f)

        for example in kg_data.get("query_examples", []):
            instructions.append({
                "instruction": "根据知识图谱分析以下查询的关联风险",
                "input": f"查询: {example['query']}",
                "output": example['answer'],
            })

    logger.info(f"生成 {len(instructions)} 条指令数据")
    return instructions


def save_instruction_data(instructions: List[Dict[str, str]]):
    """保存指令数据为 JSONL 格式"""
    output_file = OUTPUT_DIR / "instructions.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for item in instructions:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    logger.info(f"指令数据已保存到: {output_file}")

    # 同时保存为 Alpaca 格式（LLaMA-Factory 兼容）
    alpaca_file = OUTPUT_DIR / "alpaca_data.json"
    with open(alpaca_file, "w", encoding="utf-8") as f:
        json.dump(instructions, f, ensure_ascii=False, indent=2)
    logger.info(f"Alpaca 格式数据已保存到: {alpaca_file}")


# ============================================
# 训练配置
# ============================================

TRAINING_CONFIG = {
    "base_model": "Qwen/Qwen2.5-7B",  # 或 Qwen3-7B
    "method": "lora",
    "lora_config": {
        "r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
    },
    "training_args": {
        "num_train_epochs": 3,
        "per_device_train_batch_size": 4,
        "gradient_accumulation_steps": 4,
        "learning_rate": 2e-4,
        "warmup_steps": 100,
        "logging_steps": 10,
        "save_steps": 500,
        "fp16": True,
        "optim": "adamw_torch",
    },
    "output_dir": str(OUTPUT_DIR / "lora_output"),
}


def generate_training_script():
    """生成训练脚本（基于 unsloth）"""
    script_path = OUTPUT_DIR / "train.py"

    content = '''#!/usr/bin/env python3
"""
EHS 领域模型 LoRA 微调训练脚本

依赖:
    pip install unsloth transformers datasets accelerate peft

用法:
    python data/fine_tune/train.py
"""

import json
from datasets import Dataset
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer

# 配置
CONFIG = json.load(open("data/fine_tune/config.json"))

# 加载数据
def load_data(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

def format_example(example):
    """格式化指令数据为训练文本"""
    return (
        f"### Instruction:\\n{example['instruction']}\\n\\n"
        f"### Input:\\n{example['input']}\\n\\n"
        f"### Response:\\n{example['output']}"
    )

def main():
    # 加载指令数据
    data = load_data("data/fine_tune/instructions.jsonl")
    dataset = Dataset.from_list(data)
    dataset = dataset.map(lambda x: {"text": format_example(x)})

    # 加载基础模型
    model_name = CONFIG["base_model"]
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # 配置 LoRA
    lora_config = LoraConfig(
        r=CONFIG["lora_config"]["r"],
        lora_alpha=CONFIG["lora_config"]["lora_alpha"],
        lora_dropout=CONFIG["lora_config"]["lora_dropout"],
        target_modules=CONFIG["lora_config"]["target_modules"],
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 训练配置
    training_args = TrainingArguments(
        output_dir=CONFIG["output_dir"],
        num_train_epochs=CONFIG["training_args"]["num_train_epochs"],
        per_device_train_batch_size=CONFIG["training_args"]["per_device_train_batch_size"],
        gradient_accumulation_steps=CONFIG["training_args"]["gradient_accumulation_steps"],
        learning_rate=CONFIG["training_args"]["learning_rate"],
        warmup_steps=CONFIG["training_args"]["warmup_steps"],
        logging_steps=CONFIG["training_args"]["logging_steps"],
        save_steps=CONFIG["training_args"]["save_steps"],
        fp16=CONFIG["training_args"]["fp16"],
    )

    # 训练
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        dataset_text_field="text",
    )

    trainer.train()

    # 保存 LoRA 权重
    model.save_pretrained(CONFIG["output_dir"])
    tokenizer.save_pretrained(CONFIG["output_dir"])
    print("训练完成！LoRA 权重已保存。")

if __name__ == "__main__":
    main()
'''

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(content)

    # 保存训练配置
    config_path = OUTPUT_DIR / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(TRAINING_CONFIG, f, ensure_ascii=False, indent=2)

    logger.info(f"训练脚本已生成: {script_path}")
    logger.info(f"训练配置已生成: {config_path}")


def generate_modelfile():
    """生成 Ollama Modelfile（用于导入微调后的模型）"""
    modelfile = OUTPUT_DIR / "Modelfile"
    content = '''# EHS 智能安保决策中台 - 微调模型
# 用法:
#   1. 导出 GGUF: python scripts/fine_tune.py export
#   2. 创建 Ollama 模型: ollama create ehs-risk-assessment -f Modelfile
#   3. 运行: ollama run ehs-risk-assessment

FROM ./ehs-fine-tuned.gguf

# 系统提示词
SYSTEM """你是 EHS（环境、健康、安全）智能安保决策中台的 AI 助手。
你的职责是：
1. 评估告警风险等级（low/medium/high/critical）
2. 推荐相关应急预案
3. 分析事件关联风险
4. 提供处置建议

请始终使用专业、简洁的语言回答。"""

# 参数
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
'''

    with open(modelfile, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Ollama Modelfile 已生成: {modelfile}")


# ============================================
# GGUF 导出
# ============================================

def export_gguf():
    """导出为 GGUF 格式"""
    logger.info("GGUF 导出脚本框架")
    logger.info("实际导出需要使用 llama.cpp 的 convert-lora-to-gguf.py")
    logger.info("步骤:")
    logger.info("1. 合并 LoRA 权重到基础模型")
    logger.info("2. 使用 llama.cpp 转换为 GGUF")
    logger.info("3. 用 ollama create 导入")

    generate_modelfile()


# ============================================
# 主流程
# ============================================

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python scripts/fine_tune.py generate  # 生成微调数据")
        print("  python scripts/fine_tune.py train     # 生成训练脚本")
        print("  python scripts/fine_tune.py export    # 生成 GGUF 导出配置")
        print("  python scripts/fine_tune.py all       # 执行全部")
        return

    command = sys.argv[1]

    if command in ("generate", "all"):
        instructions = generate_instruction_data()
        save_instruction_data(instructions)

    if command in ("train", "all"):
        generate_training_script()

    if command in ("export", "all"):
        export_gguf()

    logger.info("完成！")


if __name__ == "__main__":
    main()
