# EHS 微调脚本

## 数据生成

```bash
python scripts/fine_tune/generate_data.py [--seed 42] [--output-dir data/fine_tune]
```

生成 4 类微调数据：
- **指令微调**: Qwen-7B 指令跟随，结构化 JSON 输出
- **风险分级**: BERT 三分类（low/medium/high）
- **合规检查**: RoBERTa 二分类（合规/不合规）
- **术语 Embedding**: BGE 对比学习

## 训练

### 指令微调 (Qwen-7B LoRA)

```bash
python scripts/fine_tune/instruction_tuning.py
```

- 基础模型: Qwen-7B-Chat
- 方法: LoRA (r=16, alpha=32)
- 输出: `models/qwen-ehs-instruct/`

### 风险分级 (BERT)

```bash
python scripts/fine_tune/risk_classification.py
```

- 基础模型: bert-base-chinese
- 任务: 三分类
- 输出: `models/bert-risk-classifier/`

### 合规检查 (RoBERTa)

```bash
python scripts/fine_tune/compliance_check.py
```

- 基础模型: hfl/chinese-roberta-wwm-ext
- 任务: 二分类
- 输出: `models/roberta-compliance-checker/`

### 术语 Embedding (BGE)

```bash
python scripts/fine_tune/embedding_tuning.py
```

- 基础模型: BAAI/bge-base-zh-v1.5
- 方法: Sentence Transformer 对比学习
- 输出: `models/bge-ehs/`

## 测试

```bash
pytest scripts/fine_tune/tests/test_generate_data.py -v
```

## 配置

所有训练参数可通过 `scripts/fine_tune/train_config.py` 中的 `TrainingConfig` 调整。
