#!/usr/bin/env python3
"""
指令微调数据验证脚本

验证数据集的质量，检测：
- 空样本
- 重复样本
- 格式错误
- 长度异常
- 内容质量问题
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter


class DataValidator:
    """数据验证器"""

    def __init__(self, data_path: str):
        """
        初始化验证器

        Args:
            data_path: 数据文件路径（JSON 格式）
        """
        self.data_path = Path(data_path)
        self.data: List[Dict] = []
        self.validation_results: Dict[str, Any] = {
            "total_samples": 0,
            "valid_samples": 0,
            "empty_samples": [],
            "duplicate_samples": [],
            "format_errors": [],
            "length_issues": [],
            "quality_warnings": [],
        }

    def load_data(self) -> bool:
        """加载数据"""
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            print(f"[OK] 成功加载 {len(self.data)} 条样本")
            return True
        except Exception as e:
            print(f"[ERROR] 数据加载失败：{e}")
            return False

    def validate_empty_samples(self) -> int:
        """
        检测空样本

        检查 instruction 和 output 是否为空或只包含空白字符。
        """
        empty_count = 0
        for i, sample in enumerate(self.data):
            instruction = sample.get("instruction", "").strip()
            output = sample.get("output", "").strip()

            if not instruction:
                self.validation_results["empty_samples"].append({
                    "index": i,
                    "reason": "instruction 为空",
                    "sample": sample
                })
                empty_count += 1
            elif not output:
                self.validation_results["empty_samples"].append({
                    "index": i,
                    "reason": "output 为空",
                    "sample": sample
                })
                empty_count += 1

        return empty_count

    def validate_duplicates(self) -> int:
        """
        检测重复样本

        检查 instruction + input 组合是否重复。
        """
        seen = {}
        duplicate_count = 0

        for i, sample in enumerate(self.data):
            key = f"{sample.get('instruction', '')}|||{sample.get('input', '')}"

            if key in seen:
                self.validation_results["duplicate_samples"].append({
                    "current_index": i,
                    "previous_index": seen[key],
                    "instruction": sample.get("instruction", "")[:50] + "...",
                    "sample": sample
                })
                duplicate_count += 1
            else:
                seen[key] = i

        return duplicate_count

    def validate_format(self) -> int:
        """
        检测格式错误

        检查必需字段是否存在，类型是否正确。
        """
        required_fields = ["instruction", "output"]
        optional_fields = ["input", "task_type", "source_plan_id"]
        format_error_count = 0

        for i, sample in enumerate(self.data):
            errors = []

            # 检查必需字段
            for field in required_fields:
                if field not in sample:
                    errors.append(f"缺少必需字段：{field}")

            # 检查字段类型
            if not isinstance(sample.get("instruction", ""), str):
                errors.append("instruction 必须是字符串类型")
            if not isinstance(sample.get("output", ""), str):
                errors.append("output 必须是字符串类型")

            if errors:
                self.validation_results["format_errors"].append({
                    "index": i,
                    "errors": errors,
                    "sample": sample
                })
                format_error_count += 1

        return format_error_count

    def validate_length(self, min_instruction_len: int = 5, max_length: int = 2000) -> int:
        """
        检测长度异常

        Args:
            min_instruction_len: instruction 最小长度
            max_length: 最大长度限制
        """
        length_issue_count = 0

        for i, sample in enumerate(self.data):
            issues = []
            instruction_len = len(sample.get("instruction", "").strip())
            output_len = len(sample.get("output", "").strip())
            input_len = len(sample.get("input", "").strip())

            # 检查过短
            if instruction_len < min_instruction_len:
                issues.append(f"instruction 过短 ({instruction_len} < {min_instruction_len})")

            # 检查过长
            if instruction_len > max_length:
                issues.append(f"instruction 过长 ({instruction_len} > {max_length})")
            if output_len > max_length:
                issues.append(f"output 过长 ({output_len} > {max_length})")
            if input_len > max_length * 5:
                issues.append(f"input 过长 ({input_len} > {max_length * 5})")

            if issues:
                self.validation_results["length_issues"].append({
                    "index": i,
                    "issues": issues,
                    "lengths": {
                        "instruction": instruction_len,
                        "output": output_len,
                        "input": input_len
                    }
                })
                length_issue_count += 1

        return length_issue_count

    def validate_quality(self) -> int:
        """
        检测内容质量问题

        检查：
        - 重复字符（如 "aaaaa"）
        - 占位符文本（如 "xxx", "..."）
        - 特殊字符过多
        """
        quality_warning_count = 0

        for i, sample in enumerate(self.data):
            warnings = []
            instruction = sample.get("instruction", "")
            output = sample.get("output", "")

            # 检查重复字符模式
            if self._has_repeated_chars(instruction, threshold=10):
                warnings.append("instruction 包含大量重复字符")
            if self._has_repeated_chars(output, threshold=20):
                warnings.append("output 包含大量重复字符")

            # 检查占位符
            if "xxx" in instruction.lower() or "..." in instruction:
                warnings.append("instruction 可能包含占位符")
            if "xxx" in output.lower() or "..." in output[:100]:
                warnings.append("output 可能包含占位符")

            # 检查 task_type 有效性
            valid_task_types = [
                "plan_retrieval", "risk_assessment", "action_generation",
                "knowledge_qa", "general"
            ]
            task_type = sample.get("task_type", "")
            if task_type and task_type not in valid_task_types:
                warnings.append(f"未知 task_type: {task_type}")

            if warnings:
                self.validation_results["quality_warnings"].append({
                    "index": i,
                    "warnings": warnings,
                    "instruction_preview": instruction[:50],
                    "output_preview": output[:50]
                })
                quality_warning_count += 1

        return quality_warning_count

    def _has_repeated_chars(self, text: str, threshold: int = 10) -> bool:
        """检查是否包含大量重复字符"""
        if len(text) < threshold:
            return False

        # 检查连续重复字符
        char_counts = Counter(text)
        for char, count in char_counts.items():
            if char.isalnum() and count > len(text) * 0.5 and count > threshold:
                return True
        return False

    def run_all_validations(self) -> Dict[str, Any]:
        """运行所有验证"""
        print("\n开始数据验证...")
        print("=" * 50)

        # 加载数据
        if not self.load_data():
            return self.validation_results

        self.validation_results["total_samples"] = len(self.data)

        # 执行各项验证
        empty_count = self.validate_empty_samples()
        print(f"\n1. 空样本检测：{empty_count} 个")

        duplicate_count = self.validate_duplicates()
        print(f"2. 重复样本检测：{duplicate_count} 个")

        format_error_count = self.validate_format()
        print(f"3. 格式错误检测：{format_error_count} 个")

        length_issue_count = self.validate_length()
        print(f"4. 长度异常检测：{length_issue_count} 个")

        quality_warning_count = self.validate_quality()
        print(f"5. 内容质量检测：{quality_warning_count} 个")

        # 计算有效样本数
        invalid_indices = set()
        for item in self.validation_results["empty_samples"]:
            invalid_indices.add(item["index"])
        for item in self.validation_results["format_errors"]:
            invalid_indices.add(item["index"])

        self.validation_results["valid_samples"] = len(self.data) - len(invalid_indices)
        valid_rate = self.validation_results["valid_samples"] / len(self.data) * 100 if self.data else 0

        print("\n" + "=" * 50)
        print(f"验证完成!")
        print(f"  总样本数：{self.validation_results['total_samples']}")
        print(f"  有效样本数：{self.validation_results['valid_samples']}")
        print(f"  有效率：{valid_rate:.2f}%")

        return self.validation_results

    def save_report(self, output_path: str) -> None:
        """保存验证报告"""
        # 简化报告（移除完整 sample 以减小文件大小）
        simplified_results = {
            "summary": {
                "total_samples": self.validation_results["total_samples"],
                "valid_samples": self.validation_results["valid_samples"],
                "empty_samples_count": len(self.validation_results["empty_samples"]),
                "duplicate_samples_count": len(self.validation_results["duplicate_samples"]),
                "format_errors_count": len(self.validation_results["format_errors"]),
                "length_issues_count": len(self.validation_results["length_issues"]),
                "quality_warnings_count": len(self.validation_results["quality_warnings"]),
            },
            "empty_samples": self.validation_results["empty_samples"][:10],  # 只保留前 10 个
            "duplicate_samples": self.validation_results["duplicate_samples"][:10],
            "format_errors": self.validation_results["format_errors"][:10],
            "length_issues": self.validation_results["length_issues"][:10],
            "quality_warnings": self.validation_results["quality_warnings"][:10],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(simplified_results, f, ensure_ascii=False, indent=2)
        print(f"\n验证报告已保存至：{output_path}")

    def print_summary(self) -> None:
        """打印摘要报告"""
        print("\n" + "=" * 50)
        print("数据验证摘要")
        print("=" * 50)

        if self.validation_results["empty_samples"]:
            print("\n[WARNING] 空样本示例:")
            for item in self.validation_results["empty_samples"][:3]:
                print(f"  [{item['index']}] {item['reason']}")

        if self.validation_results["duplicate_samples"]:
            print("\n[WARNING] 重复样本示例:")
            for item in self.validation_results["duplicate_samples"][:3]:
                print(f"  [{item['current_index']}] {item['instruction']}")

        if self.validation_results["format_errors"]:
            print("\n[WARNING] 格式错误示例:")
            for item in self.validation_results["format_errors"][:3]:
                print(f"  [{item['index']}] {', '.join(item['errors'])}")

        if self.validation_results["quality_warnings"]:
            print("\n[WARNING] 质量警告示例:")
            for item in self.validation_results["quality_warnings"][:3]:
                print(f"  [{item['index']}] {', '.join(item['warnings'])}")


def main():
    parser = argparse.ArgumentParser(description="指令微调数据验证工具")
    parser.add_argument(
        "--data_path",
        type=str,
        default="data/processed/instruction_tuning.json",
        help="数据文件路径"
    )
    parser.add_argument(
        "--output_report",
        type=str,
        default="data/processed/validation_report.json",
        help="验证报告输出路径"
    )
    parser.add_argument(
        "--min_instruction_length",
        type=int,
        default=5,
        help="instruction 最小长度"
    )
    parser.add_argument(
        "--max_length",
        type=int,
        default=2000,
        help="最大长度限制"
    )

    args = parser.parse_args()

    # 创建验证器
    validator = DataValidator(args.data_path)

    # 运行验证
    results = validator.run_all_validations()

    # 打印摘要
    validator.print_summary()

    # 保存报告
    validator.save_report(args.output_report)

    # 返回状态码
    if results["valid_samples"] == 0:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
