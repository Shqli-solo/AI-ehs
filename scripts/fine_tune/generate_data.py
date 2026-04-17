"""
微调数据生成器
生成 4 类微调数据：指令微调、风险分级、合规检查、术语 Embedding
"""

import json
import random
import os
from pathlib import Path

random.seed(42)

SEED_DIR = Path(__file__).parent.parent.parent / "data" / "seed"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "fine_tune"

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


def generate_instruction_data():
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
    risk_levels = ["high", "medium", "low"]
    recommendations = [
        "立即启动应急预案，疏散人员",
        "通知维护人员检查设备",
        "持续监控并记录数据变化",
        "启动备用系统，确认故障范围",
    ]

    for _ in range(480):
        loc = random.choice(locations)
        alert = random.choice(alert_types)
        risk = random.choice(risk_levels)
        rec = random.choice(recommendations)
        train_data.append({
            "instruction": "根据以下告警内容，评估风险等级并给出处置建议。以 JSON 格式输出，包含 risk_level (high/medium/low) 和 recommendation 字段。",
            "input": f"{loc}{alert}，请评估风险",
            "output": json.dumps({"risk_level": risk, "recommendation": rec}, ensure_ascii=False),
        })

    random.shuffle(train_data)
    eval_data = train_data[:100]
    train_data = train_data[100:]
    return train_data, eval_data


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


def generate_risk_data():
    train_data = []
    eval_data = []

    for text, label in RISK_SAMPLES:
        train_data.append({"text": text, "label": label})

    templates_low = ["设备运行正常，{}传感器无异常", "巡检发现{}，无安全隐患", "{}读数在正常范围内"]
    templates_medium = ["{}超标，需要关注", "{}异常，启动处置流程", "检测到{}，正在确认中"]
    templates_high = ["{}达到危险值，立即疏散", "发生{}，启动应急预案", "{}风险极高，需紧急处置"]
    subjects = ["烟感", "温度", "气体", "入侵", "烟雾", "化学品", "压力", "湿度"]

    for _ in range(970):
        r = random.random()
        if r < 0.33:
            text = random.choice(templates_low).format(random.choice(subjects))
            label = 0
        elif r < 0.66:
            text = random.choice(templates_medium).format(random.choice(subjects))
            label = 1
        else:
            text = random.choice(templates_high).format(random.choice(subjects))
            label = 2
        train_data.append({"text": text, "label": label})

    random.shuffle(train_data)
    eval_data = train_data[:200]
    train_data = train_data[200:]
    return train_data, eval_data


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


def generate_compliance_data():
    train_data = []
    eval_data = []

    for plan, rule, result in COMPLIANCE_SAMPLES:
        train_data.append({"plan": plan, "rule": rule, "compliant": result})

    plan_templates_pass = ["发生{}后立即{}并{}", "检测到{}时启动{}并通知{}", "当{}超标时执行{}和{}"]
    plan_templates_fail = ["发生{}后不采取行动", "检测到{}时忽略告警", "当{}超标时继续作业"]
    rules_pass = ["预案需包含应急响应措施", "预案需包含人员疏散方案", "预案需包含设备处置流程"]
    rules_fail = ["预案缺少关键处置步骤", "预案未考虑人员安全", "预案未包含设备隔离措施"]
    events = ["火灾", "泄漏", "爆炸", "入侵", "温度异常"]
    actions_pass = ["疏散", "隔离", "通知", "灭火", "关闭阀门"]
    actions_fail = ["观察", "等待", "忽略", "继续"]

    for _ in range(280):
        r = random.random()
        if r < 0.7:
            plan = random.choice(plan_templates_pass).format(random.choice(events), random.choice(actions_pass), random.choice(actions_pass))
            rule = random.choice(rules_pass)
            result = 1
        else:
            plan = random.choice(plan_templates_fail).format(random.choice(events), random.choice(actions_fail))
            rule = random.choice(rules_fail)
            result = 0
        train_data.append({"plan": plan, "rule": rule, "compliant": result})

    random.shuffle(train_data)
    eval_data = train_data[:60]
    train_data = train_data[60:]
    return train_data, eval_data


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


def generate_embedding_data():
    all_pairs = list(EHS_TERM_PAIRS)

    terms_positive = [("烟感", "烟雾"), ("报警", "告警"), ("处置", "应急"), ("化学品", "危化品"), ("喷淋", "洒水"), ("通风", "排风"), ("警戒", "警戒线"), ("灭火", "消防"), ("安全", "防护"), ("监控", "监测")]
    terms_negative = [("火灾", "地震"), ("气体", "辐射"), ("温度", "湿度"), ("入侵", "火灾"), ("泄漏", "断电")]

    for a, b in terms_positive:
        all_pairs.append({"term_a": a, "term_b": b, "related": 1})
    for a, b in terms_negative:
        all_pairs.append({"term_a": a, "term_b": b, "related": 0})

    while len(all_pairs) < 2000:
        base = random.choice(EHS_TERM_PAIRS)
        suffix = random.choice(["传感器", "检测器", "报警器", "系统", "装置"])
        all_pairs.append({"term_a": base["term_a"] + suffix, "term_b": base["term_b"] + suffix, "related": base["related"]})

    random.shuffle(all_pairs)
    return all_pairs[:2000]


# ============================================
# 主函数
# ============================================

def main():
    os.makedirs(OUTPUT_DIR / "instruction", exist_ok=True)
    os.makedirs(OUTPUT_DIR / "risk", exist_ok=True)
    os.makedirs(OUTPUT_DIR / "compliance", exist_ok=True)
    os.makedirs(OUTPUT_DIR / "embedding", exist_ok=True)

    train, eval = generate_instruction_data()
    _write_jsonl(OUTPUT_DIR / "instruction" / "train.jsonl", train)
    _write_jsonl(OUTPUT_DIR / "instruction" / "eval.jsonl", eval)
    print(f"指令微调: train={len(train)}, eval={len(eval)}")

    train, eval = generate_risk_data()
    _write_jsonl(OUTPUT_DIR / "risk" / "train.jsonl", train)
    _write_jsonl(OUTPUT_DIR / "risk" / "eval.jsonl", eval)
    print(f"风险分级: train={len(train)}, eval={len(eval)}")

    train, eval = generate_compliance_data()
    _write_jsonl(OUTPUT_DIR / "compliance" / "train.jsonl", train)
    _write_jsonl(OUTPUT_DIR / "compliance" / "eval.jsonl", eval)
    print(f"合规检查: train={len(train)}, eval={len(eval)}")

    pairs = generate_embedding_data()
    _write_jsonl(OUTPUT_DIR / "embedding" / "term_pairs.jsonl", pairs)
    print(f"术语 Embedding: {len(pairs)} 对")

    print("\n所有数据生成完成！")


def _write_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
