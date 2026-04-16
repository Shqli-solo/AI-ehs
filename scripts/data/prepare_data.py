#!/usr/bin/env python3
"""
EHS 预案数据准备脚本

功能：
1. 加载样本预案数据
2. 生成指令微调数据（Instruction Tuning）
3. 生成风险分级训练数据
4. 生成术语 Embedding 训练数据
5. 数据格式转换和导出

使用方法：
    # 生成所有训练数据
    python scripts/data/prepare_data.py --input data/raw/plans/sample_plans.json --output data/processed

    # 仅生成指令微调数据
    python scripts/data/prepare_data.py --input data/raw/plans/sample_plans.json --output data/processed --task instruction

    # 预览数据
    python scripts/data/prepare_data.py --input data/raw/plans/sample_plans.json --preview
"""

import argparse
import json
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


class DataPreparation:
    """EHS 预案数据准备器"""

    def __init__(self, input_path: str, output_dir: str):
        """初始化数据准备器

        Args:
            input_path: 输入数据文件路径
            output_dir: 输出目录
        """
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data: List[Dict[str, Any]] = []
        self.stats: Dict[str, Any] = {}

    def load_data(self) -> List[Dict[str, Any]]:
        """加载输入数据"""
        print(f"加载数据：{self.input_path}")
        with open(self.input_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"成功加载 {len(self.data)} 条预案记录")
        return self.data

    def generate_instruction_data(self) -> List[Dict[str, Any]]:
        """生成指令微调数据

        基于预案数据生成 instruction-input-output 三元组，用于微调 LLM。
        包含多种任务类型：
        - 预案检索：根据事件描述检索相关预案
        - 风险评估：根据事件描述评估风险等级
        - 行动建议：根据事件生成应急处置步骤
        - 知识问答：关于 EHS 预案的问答

        Returns:
            指令微调数据列表
        """
        print("\n[1] 生成指令微调数据...")
        instruction_data = []

        for plan in self.data:
            plan_id = plan.get("id", "UNKNOWN")
            event_type = plan.get("event_type", "unknown")
            risk_level = plan.get("risk_level", "MEDIUM")
            content = plan.get("content", "")
            actions = plan.get("actions", [])
            title = plan.get("title", "")

            # 任务 1: 预案检索
            instruction_data.append({
                "instruction": f"请找到关于'{event_type}'事件的应急预案。",
                "input": f"事件类型：{event_type}\n事件描述：{content[:100]}...",
                "output": f"《{title}》\n\n风险等级：{risk_level}\n\n处置步骤：\n" + "\n".join([
                    f"{i+1}. {a.get('action', '')}" for i, a in enumerate(actions[:3])
                ]),
                "task_type": "plan_retrieval",
                "source_plan_id": plan_id
            })

            # 任务 2: 风险评估
            instruction_data.append({
                "instruction": "请评估以下事件的风险等级，并说明理由。",
                "input": f"事件类型：{event_type}\n事件详情：{content[:200]}...",
                "output": f"风险等级：{risk_level}\n\n评估理由：该事件属于{self._get_event_type_cn(event_type)}类别，根据 EHS 标准，此类事件通常被评定为{self._get_risk_level_cn(risk_level)}风险。需要立即启动相应的应急预案。",
                "task_type": "risk_assessment",
                "source_plan_id": plan_id
            })

            # 任务 3: 行动建议生成
            instruction_data.append({
                "instruction": "请列出应对该事件的应急处置步骤。",
                "input": f"事件类型：{event_type}\n风险等级：{risk_level}",
                "output": "\n".join([
                    f"步骤{a.get('step', i+1)}: {a.get('action', '')} (执行角色：{a.get('role', '未知')})"
                    for i, a in enumerate(actions)
                ]),
                "task_type": "action_generation",
                "source_plan_id": plan_id
            })

            # 任务 4: 知识问答
            instruction_data.append({
                "instruction": f"什么是{self._get_event_type_cn(event_type)}？如何应急处置？",
                "input": "",
                "output": f"{content}\n\n应急处置要点：\n" + "\n".join([
                    f"- {a.get('action', '')}" for a in actions[:5]
                ]),
                "task_type": "knowledge_qa",
                "source_plan_id": plan_id
            })

        print(f"   生成 {len(instruction_data)} 条指令微调数据")
        return instruction_data

    def generate_risk_classification_data(self) -> List[Dict[str, Any]]:
        """生成风险分级训练数据

        生成用于训练风险分类模型的数据，包含事件描述和风险等级标签。

        Returns:
            风险分级数据列表
        """
        print("\n[2] 生成风险分级训练数据...")
        risk_data = []

        risk_level_to_label = {
            "LOW": 0,
            "MEDIUM": 1,
            "HIGH": 2,
            "CRITICAL": 3
        }

        for plan in self.data:
            event_type = plan.get("event_type", "unknown")
            risk_level = plan.get("risk_level", "MEDIUM")
            content = plan.get("content", "")
            title = plan.get("title", "")

            # 创建多个训练样本
            risk_data.append({
                "text": f"{title}。{content}",
                "label": risk_level_to_label.get(risk_level, 1),
                "risk_level": risk_level,
                "event_type": event_type,
                "source_plan_id": plan.get("id")
            })

            # 增强样本：仅使用内容
            risk_data.append({
                "text": content,
                "label": risk_level_to_label.get(risk_level, 1),
                "risk_level": risk_level,
                "event_type": event_type,
                "source_plan_id": plan.get("id")
            })

            # 增强样本：事件类型 + 内容摘要
            risk_data.append({
                "text": f"事件类型：{event_type}。{content[:200]}",
                "label": risk_level_to_label.get(risk_level, 1),
                "risk_level": risk_level,
                "event_type": event_type,
                "source_plan_id": plan.get("id")
            })

        print(f"   生成 {len(risk_data)} 条风险分级数据（含增强）")
        return risk_data

    def generate_embedding_data(self) -> List[Dict[str, Any]]:
        """生成术语 Embedding 训练数据

        生成用于训练术语嵌入模型的数据对，包含：
        - 同义词对：相同概念的不同表达
        - 上下位词对：概念与类别的关系
        - 相关词对：语义相关的术语

        Returns:
            Embedding 训练数据列表
        """
        print("\n[3] 生成术语 Embedding 训练数据...")
        embedding_data = []

        # EHS 术语映射
        event_type_synonyms = {
            "fire": ["火灾", "火情", "火警", "燃烧事故", "消防事件"],
            "gas_leak": ["气体泄漏", "燃气泄漏", "甲烷泄漏", "可燃气体泄漏"],
            "temperature_abnormal": ["温度异常", "机房过热", "高温告警", "温度超标"],
            "intrusion": ["入侵", "非法闯入", "安防告警", "周界报警"],
            "power_failure": ["停电", "电力故障", "断电", "供电中断"],
            "chemical_spill": ["化学品泄漏", "危化品泄漏", "液体泄漏", "化学事故"],
            "earthquake": ["地震", "震灾", "地质灾害"],
            "flood": ["洪水", "水灾", "洪涝", "进水"]
        }

        risk_level_synonyms = {
            "LOW": ["低风险", "轻微风险", "一般风险", "可接受风险"],
            "MEDIUM": ["中等风险", "注意风险", "需关注"],
            "HIGH": ["高风险", "严重风险", "需立即处理"],
            "CRITICAL": ["危急风险", "极高风险", "灾难性风险", "紧急状态"]
        }

        # 生成同义词对（相似度高）
        for plan in self.data:
            event_type = plan.get("event_type", "")
            risk_level = plan.get("risk_level", "")
            content = plan.get("content", "")

            if event_type in event_type_synonyms:
                synonyms = event_type_synonyms[event_type]
                for i in range(len(synonyms)):
                    for j in range(i + 1, len(synonyms)):
                        embedding_data.append({
                            "text1": synonyms[i],
                            "text2": synonyms[j],
                            "label": 1.0,  # 相似
                            "pair_type": "synonym",
                            "category": "event_type"
                        })

            if risk_level in risk_level_synonyms:
                synonyms = risk_level_synonyms[risk_level]
                for i in range(len(synonyms)):
                    for j in range(i + 1, len(synonyms)):
                        embedding_data.append({
                            "text1": synonyms[i],
                            "text2": synonyms[j],
                            "label": 1.0,
                            "pair_type": "synonym",
                            "category": "risk_level"
                        })

            # 生成内容 - 事件类型对
            if event_type in event_type_synonyms:
                for synonym in event_type_synonyms[event_type]:
                    embedding_data.append({
                        "text1": content[:100],
                        "text2": synonym,
                        "label": 0.8,  # 相关
                        "pair_type": "related",
                        "category": "content_event"
                    })

        # 生成负样本（不相关对）
        event_types = list(event_type_synonyms.keys())
        for i in range(min(len(event_types), 5)):
            for j in range(i + 1, min(len(event_types), 5)):
                if event_types[i] != event_types[j]:
                    syn1 = event_type_synonyms[event_types[i]][0]
                    syn2 = event_type_synonyms[event_types[j]][0]
                    embedding_data.append({
                        "text1": syn1,
                        "text2": syn2,
                        "label": 0.0,  # 不相似
                        "pair_type": "negative",
                        "category": "cross_event"
                    })

        print(f"   生成 {len(embedding_data)} 条 Embedding 训练数据")
        return embedding_data

    def _get_event_type_cn(self, event_type: str) -> str:
        """获取事件类型的中文名称"""
        mapping = {
            "fire": "火灾",
            "gas_leak": "气体泄漏",
            "temperature_abnormal": "温度异常",
            "intrusion": "入侵检测",
            "power_failure": "电力故障",
            "chemical_spill": "化学品泄漏",
            "earthquake": "地震",
            "flood": "洪水"
        }
        return mapping.get(event_type, event_type)

    def _get_risk_level_cn(self, risk_level: str) -> str:
        """获取风险等级的中文名称"""
        mapping = {
            "LOW": "低风险",
            "MEDIUM": "中等风险",
            "HIGH": "高风险",
            "CRITICAL": "危急风险"
        }
        return mapping.get(risk_level, risk_level)

    def save_data(self, filename: str, data: List[Any]) -> str:
        """保存数据到文件"""
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"   已保存：{output_path}")
        return str(output_path)

    def prepare_all(self) -> Dict[str, str]:
        """执行完整数据准备流程

        Returns:
            输出文件路径字典
        """
        # 加载数据
        self.load_data()

        # 生成各类训练数据
        instruction_data = self.generate_instruction_data()
        risk_data = self.generate_risk_classification_data()
        embedding_data = self.generate_embedding_data()

        # 保存数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = {
            "instruction": self.save_data(f"instruction_tuning_{timestamp}.json", instruction_data),
            "risk_classification": self.save_data(f"risk_classification_{timestamp}.json", risk_data),
            "embedding": self.save_data(f"embedding_training_{timestamp}.json", embedding_data)
        }

        # 生成统计报告
        self.stats = {
            "input_file": str(self.input_path),
            "output_dir": str(self.output_dir),
            "timestamp": timestamp,
            "input_count": len(self.data),
            "output_counts": {
                "instruction": len(instruction_data),
                "risk_classification": len(risk_data),
                "embedding": len(embedding_data)
            },
            "output_files": output_files
        }

        # 保存统计报告
        stats_path = self.output_dir / f"preparation_stats_{timestamp}.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        print(f"\n统计报告已保存：{stats_path}")

        return output_files

    def preview(self):
        """预览数据"""
        self.load_data()
        print("\n" + "=" * 60)
        print("数据预览")
        print("=" * 60)

        # 显示前 3 条记录的摘要
        for i, plan in enumerate(self.data[:3]):
            print(f"\n[样本 {i+1}]")
            print(f"  ID: {plan.get('id', 'N/A')}")
            print(f"  标题：{plan.get('title', 'N/A')}")
            print(f"  事件类型：{plan.get('event_type', 'N/A')}")
            print(f"  风险等级：{plan.get('risk_level', 'N/A')}")
            print(f"  内容摘要：{plan.get('content', '')[:100]}...")
            print(f"  处置步骤数：{len(plan.get('actions', []))}")

        print("\n" + "=" * 60)
        print(f"总样本数：{len(self.data)}")
        print("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="EHS 预案数据准备工具")
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入数据文件路径（JSON 格式）"
    )
    parser.add_argument(
        "--output", "-o",
        default="data/processed",
        help="输出目录（默认：data/processed）"
    )
    parser.add_argument(
        "--task", "-t",
        choices=["all", "instruction", "risk", "embedding"],
        default="all",
        help="生成的数据类型（默认：all）"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="仅预览数据，不生成文件"
    )

    args = parser.parse_args()

    # 创建数据准备器
    preparer = DataPreparation(args.input, args.output)

    # 预览模式
    if args.preview:
        preparer.preview()
        return

    # 执行数据准备
    print("=" * 60)
    print("EHS 预案数据准备")
    print("=" * 60)

    if args.task == "all":
        output_files = preparer.prepare_all()
        print("\n" + "=" * 60)
        print("生成文件列表")
        print("=" * 60)
        for task_type, file_path in output_files.items():
            print(f"  - {task_type}: {file_path}")
    else:
        preparer.load_data()
        if args.task == "instruction":
            data = preparer.generate_instruction_data()
            preparer.save_data("instruction_preview.json", data)
        elif args.task == "risk":
            data = preparer.generate_risk_classification_data()
            preparer.save_data("risk_preview.json", data)
        elif args.task == "embedding":
            data = preparer.generate_embedding_data()
            preparer.save_data("embedding_preview.json", data)

    print("\n数据准备完成！")


if __name__ == "__main__":
    main()
