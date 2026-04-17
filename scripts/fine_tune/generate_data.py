"""
微调数据生成器
生成 4 类微调数据：指令微调、风险分级、合规检查、术语 Embedding

用法：
    python scripts/fine_tune/generate_data.py [--seed 42] [--output-dir data/fine_tune]
"""

import json
import random
import os
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

SEED_DIR = Path(__file__).parent.parent.parent / "data" / "seed"

# Risk-appropriate recommendation mapping
RISK_RECOMMENDATIONS = {
    "high": [
        "立即启动应急预案，疏散人员，联系消防部门",
        "启动紧急疏散程序，拨打119报警，关闭通风系统",
        "立即切断危险区域电源，组织人员撤离",
    ],
    "medium": [
        "启动通风系统，通知维护人员检查泄漏源，持续监控",
        "检查设备运行状态，启动备用系统，监控数据变化",
        "派遣人员现场确认，调取监控录像记录",
    ],
    "low": [
        "派遣人员现场确认是否为误报",
        "记录数据并安排定期巡检，无需紧急处置",
        "检查传感器状态，校准读数",
    ],
}

# ============================================
# 1. 指令微调数据
# ============================================

INSTRUCTION_TEMPLATES = [
    {
        "instruction": "根据以下告警内容，评估风险等级并给出处置建议。以 JSON 格式输出，包含 risk_level (high/medium/low) 和 recommendation 字段。",
        "scenarios": [
            {
                "input": "A栋3楼东区烟感探测器检测到烟雾浓度超标，当前读数0.85%obs/m，阈值1.0",
                "output": json.dumps({"risk_level": "high", "recommendation": "立即启动火灾应急预案，疏散3楼人员，联系消防部门，关闭通风系统防止火势蔓延"}, ensure_ascii=False),
            },
            {
                "input": "B车间东区气体检测仪检测到可燃气体浓度12.5ppm，阈值50ppm",
                "output": json.dumps({"risk_level": "medium", "recommendation": "启动通风系统，通知设备维护人员检查泄漏源，持续监控浓度变化"}, ensure_ascii=False),
            },
            {
                "input": "C仓库2层温度传感器检测到46.2°C，阈值45°C",
                "output": json.dumps({"risk_level": "medium", "recommendation": "检查温控系统运行状态，启动备用冷却系统，监控温度变化趋势"}, ensure_ascii=False),
            },
            {
                "input": "D区西南角红外探测器检测到未授权人员入侵",
                "output": json.dumps({"risk_level": "high", "recommendation": "通知就近安保人员前往现场，调取监控录像，必要时封锁出口并报警"}, ensure_ascii=False),
            },
            {
                "input": "E栋地下车库B区烟雾探测器触发报警，确认无明火",
                "output": json.dumps({"risk_level": "low", "recommendation": "派遣人员现场确认是否为误报，检查探测器状态"}, ensure_ascii=False),
            },
        ],
    },
    {
        "instruction": "根据以下告警内容，评估风险等级。输出 JSON，包含 risk_level 和 reasoning。",
        "scenarios": [
            {
                "input": "生产车间多处烟感同时报警，伴随温度异常升高",
                "output": json.dumps({"risk_level": "high", "reasoning": "多处烟感同时报警且温度异常升高，高度疑似火灾，需立即疏散和灭火"}, ensure_ascii=False),
            },
            {
                "input": "单一温度传感器读数略高于阈值0.5度",
                "output": json.dumps({"risk_level": "low", "reasoning": "轻微超标，可能为传感器漂移，需校准但不需要紧急处置"}, ensure_ascii=False),
            },
        ],
    },
]


# ============================================
# 2. 风险分级数据
# ============================================

RISK_SAMPLES = [
    ("单一传感器轻微超标，无其他异常", 0),
    ("温度传感器读数略高于阈值", 0),
    ("烟雾探测器偶发报警，确认为误报", 0),
    ("设备在线率正常，无异常告警", 0),
    ("例行巡检发现设备老化，建议更换", 0),
    ("气体浓度达到预警值，需关注", 1),
    ("温度异常升高，启动冷却系统", 1),
    ("烟雾浓度超标，需现场确认", 1),
    ("气体泄漏浓度接近阈值", 1),
    ("多处传感器数据异常", 1),
    ("车间可燃气体浓度超过安全标准", 2),
    ("A栋发生火灾，多处烟感报警", 2),
    ("有毒气体泄漏，需立即疏散", 2),
    ("未授权人员入侵核心区域", 2),
    ("爆炸风险，化学品温度失控", 2),
]


# ============================================
# 3. 合规检查数据
# ============================================

COMPLIANCE_SAMPLES = [
    ("发生火灾后立即启动喷淋系统并疏散人员", "火灾预案需包含疏散和灭火措施", 1),
    ("发现气体泄漏后立即关闭阀门并通风", "气体泄漏预案需包含隔离和通风", 1),
    ("发现气体泄漏后继续作业观察情况", "气体泄漏预案需包含隔离和通风", 0),
    ("温度异常时启动冷却系统并通知维护", "温度异常预案需包含降温和通知", 1),
    ("入侵检测后未采取任何措施", "入侵检测预案需包含人员派遣", 0),
]


# ============================================
# 4. 术语 Embedding 数据
# ============================================

EHS_TERM_PAIRS = [
    {"term_a": "火灾", "term_b": "火情", "related": 1},
    {"term_a": "火灾", "term_b": "泄漏", "related": 0},
    {"term_a": "气体泄漏", "term_b": "可燃气体", "related": 1},
    {"term_a": "烟感报警", "term_b": "烟雾检测", "related": 1},
    {"term_a": "温度异常", "term_b": "高温", "related": 1},
    {"term_a": "入侵检测", "term_b": "未授权进入", "related": 1},
    {"term_a": "应急预案", "term_b": "处置流程", "related": 1},
    {"term_a": "疏散", "term_b": "撤离", "related": 1},
    {"term_a": "火灾", "term_b": "入侵", "related": 0},
    {"term_a": "气体", "term_b": "温度", "related": 0},
]


def generate_instruction_data(rng: random.Random):
    train_data = []
    eval_data = []

    for template in INSTRUCTION_TEMPLATES:
        for scenario in template["scenarios"]:
            item = {
                "instruction": template["instruction"],
                "input": scenario["input"],
                "output": scenario["output"],
            }
            train_data.append(item)

    locations = ["A栋", "B车间", "C仓库", "D区", "E栋"]
    alert_types = ["烟感报警", "气体泄漏", "温度异常", "入侵检测", "烟雾报警"]

    for _ in range(480):
        loc = rng.choice(locations)
        alert = rng.choice(alert_types)
        risk = rng.choice(["high", "medium", "low"])
        rec = rng.choice(RISK_RECOMMENDATIONS[risk])
        train_data.append({
            "instruction": "根据以下告警内容，评估风险等级并给出处置建议。以 JSON 格式输出，包含 risk_level (high/medium/low) 和 recommendation 字段。",
            "input": f"{loc}{alert}，请评估风险",
            "output": json.dumps({"risk_level": risk, "recommendation": rec}, ensure_ascii=False),
        })

    # Use hand-authored seed samples (INSTRUCTION_TEMPLATES) for eval
    for template in INSTRUCTION_TEMPLATES:
        for scenario in template["scenarios"]:
            eval_data.append({
                "instruction": template["instruction"],
                "input": scenario["input"],
                "output": scenario["output"],
            })

    rng.shuffle(train_data)
    return train_data, eval_data


def generate_risk_data(rng: random.Random):
    train_data = []
    eval_data = []

    # Reserve hand-authored samples for eval
    for text, label in RISK_SAMPLES:
        eval_data.append({"text": text, "label": label})

    templates_low = ["设备运行正常，{}传感器无异常", "巡检发现{}，无安全隐患", "{}读数在正常范围内"]
    templates_medium = ["{}超标，需要关注", "{}异常，启动处置流程", "检测到{}，正在确认中"]
    templates_high = ["{}达到危险值，立即疏散", "发生{}，启动应急预案", "{}风险极高，需紧急处置"]
    subjects = ["烟感", "温度", "气体", "入侵", "烟雾", "化学品", "压力", "湿度"]

    for _ in range(970):
        r = rng.random()
        if r < 0.33:
            text = rng.choice(templates_low).format(rng.choice(subjects))
            label = 0
        elif r < 0.66:
            text = rng.choice(templates_medium).format(rng.choice(subjects))
            label = 1
        else:
            text = rng.choice(templates_high).format(rng.choice(subjects))
            label = 2
        train_data.append({"text": text, "label": label})

    rng.shuffle(train_data)
    return train_data, eval_data


def generate_compliance_data(rng: random.Random):
    train_data = []
    eval_data = []

    # Reserve hand-authored samples for eval
    for plan, rule, result in COMPLIANCE_SAMPLES:
        eval_data.append({"plan": plan, "rule": rule, "compliant": result})

    plan_templates_pass = ["发生{}后立即{}并{}", "检测到{}时启动{}并通知{}", "当{}超标时执行{}和{}"]
    plan_templates_fail = ["发生{}后不采取行动", "检测到{}时忽略告警", "当{}超标时继续作业"]
    rules_pass = ["预案需包含应急响应措施", "预案需包含人员疏散方案", "预案需包含设备处置流程"]
    rules_fail = ["预案缺少关键处置步骤", "预案未考虑人员安全", "预案未包含设备隔离措施"]
    events = ["火灾", "泄漏", "爆炸", "入侵", "温度异常"]
    actions_pass = ["疏散", "隔离", "通知", "灭火", "关闭阀门"]
    actions_fail = ["观察", "等待", "忽略", "继续"]

    for _ in range(280):
        r = rng.random()
        if r < 0.7:
            plan = rng.choice(plan_templates_pass).format(rng.choice(events), rng.choice(actions_pass), rng.choice(actions_pass))
            rule = rng.choice(rules_pass)
            result = 1
        else:
            plan = rng.choice(plan_templates_fail).format(rng.choice(events), rng.choice(actions_fail))
            rule = rng.choice(rules_fail)
            result = 0
        train_data.append({"plan": plan, "rule": rule, "compliant": result})

    rng.shuffle(train_data)
    return train_data, eval_data


def generate_embedding_data(rng: random.Random):
    all_pairs = list(EHS_TERM_PAIRS)

    terms_positive = [("烟感", "烟雾"), ("报警", "告警"), ("处置", "应急"), ("化学品", "危化品"), ("喷淋", "洒水"), ("通风", "排风"), ("警戒", "警戒线"), ("灭火", "消防"), ("安全", "防护"), ("监控", "监测")]
    terms_negative = [("火灾", "地震"), ("气体", "辐射"), ("温度", "湿度"), ("入侵", "火灾"), ("泄漏", "断电")]

    for a, b in terms_positive:
        all_pairs.append({"term_a": a, "term_b": b, "related": 1})
    for a, b in terms_negative:
        all_pairs.append({"term_a": a, "term_b": b, "related": 0})

    while len(all_pairs) < 2000:
        base = rng.choice(EHS_TERM_PAIRS)
        suffix = rng.choice(["传感器", "检测器", "报警器", "系统", "装置"])
        all_pairs.append({"term_a": base["term_a"] + suffix, "term_b": base["term_b"] + suffix, "related": base["related"]})

    rng.shuffle(all_pairs)
    # Split into train/eval (90/10)
    split = int(0.9 * len(all_pairs))
    return all_pairs[:split], all_pairs[split:]


def main():
    parser = argparse.ArgumentParser(description="EHS 微调数据生成器")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument("--output-dir", type=str, default=None, help="输出目录")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    output_dir = Path(args.output_dir) if args.output_dir else SEED_DIR.parent / "fine_tune"

    os.makedirs(output_dir / "instruction", exist_ok=True)
    os.makedirs(output_dir / "risk", exist_ok=True)
    os.makedirs(output_dir / "compliance", exist_ok=True)
    os.makedirs(output_dir / "embedding", exist_ok=True)

    train, eval = generate_instruction_data(rng)
    _write_jsonl(output_dir / "instruction" / "train.jsonl", train)
    _write_jsonl(output_dir / "instruction" / "eval.jsonl", eval)
    logger.info(f"指令微调: train={len(train)}, eval={len(eval)}")

    train, eval = generate_risk_data(rng)
    _write_jsonl(output_dir / "risk" / "train.jsonl", train)
    _write_jsonl(output_dir / "risk" / "eval.jsonl", eval)
    logger.info(f"风险分级: train={len(train)}, eval={len(eval)}")

    train, eval = generate_compliance_data(rng)
    _write_jsonl(output_dir / "compliance" / "train.jsonl", train)
    _write_jsonl(output_dir / "compliance" / "eval.jsonl", eval)
    logger.info(f"合规检查: train={len(train)}, eval={len(eval)}")

    train_pairs, eval_pairs = generate_embedding_data(rng)
    _write_jsonl(output_dir / "embedding" / "train.jsonl", train_pairs)
    _write_jsonl(output_dir / "embedding" / "eval.jsonl", eval_pairs)
    logger.info(f"术语 Embedding: train={len(train_pairs)}, eval={len(eval_pairs)}")

    logger.info("所有数据生成完成！")


def _write_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
