# scripts/fine_tune/embedding_tuning.py
"""
术语 Embedding 微调 - BGE

训练目标：EHS 术语对比学习优化
基础模型：BAAI/bge-base-zh-v1.5
数据：data/fine_tune/embedding/term_pairs.jsonl
方法：Sentence Transformer 对比学习

用法：
    python scripts/fine_tune/embedding_tuning.py
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
    from sentence_transformers import (
        SentenceTransformer,
        InputExample,
        losses,
        SentencesDataset,
        evaluation,
    )
    from torch.utils.data import DataLoader
    HAS_ST = True
except ImportError:
    HAS_ST = False
    logger.warning("sentence-transformers 未安装，仅做配置检查")


def load_term_pairs(data_path: str):
    """加载术语对数据"""
    pairs = []
    with open(data_path, encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            pairs.append(item)
    return pairs


def train(config: TrainingConfig):
    """执行术语 Embedding 微调"""
    if not HAS_ST:
        logger.info("跳过训练（sentence-transformers 未安装）")
        return

    # 加载数据
    pairs = load_term_pairs(config.train_file)

    train_examples = []
    for pair in pairs:
        # label: 1=related, 0=unrelated
        label = pair["related"]
        train_examples.append(
            InputExample(texts=[pair["term_a"], pair["term_b"]], label=float(label))
        )

    # 加载模型
    model = SentenceTransformer(config.base_model)

    # 创建数据集和 DataLoader
    dataset = SentencesDataset(train_examples, model)
    loader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True)

    # 损失函数 - 对比损失
    train_loss = losses.CosineSimilarityLoss(model)

    # 评估器
    dev_pairs = load_term_pairs(config.eval_file) if config.eval_file else []
    if dev_pairs:
        dev_examples = [
            InputExample(texts=[p["term_a"], p["term_b"]], label=float(p["related"]))
            for p in dev_pairs
        ]
        evaluator = evaluation.EmbeddingSimilarityEvaluator.from_input_examples(
            dev_examples, name="ehs-eval"
        )
    else:
        evaluator = None

    # 训练
    model.fit(
        train_objectives=[(loader, train_loss)],
        epochs=config.num_epochs,
        warmup_steps=int(len(loader) * config.warmup_ratio * config.num_epochs),
        output_path=config.output_dir,
        evaluator=evaluator,
        evaluation_steps=100,
    )

    logger.info(f"模型已保存到 {config.output_dir}")


def main():
    config = TrainingConfig(
        base_model="BAAI/bge-base-zh-v1.5",
        output_dir=str(ROOT / "models" / "bge-ehs"),
        train_file=str(ROOT / "data" / "fine_tune" / "embedding" / "train.jsonl"),
        eval_file=str(ROOT / "data" / "fine_tune" / "embedding" / "eval.jsonl"),
        num_epochs=3,
        batch_size=32,
    )
    train(config)


if __name__ == "__main__":
    main()
