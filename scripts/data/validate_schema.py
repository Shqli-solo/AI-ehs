#!/usr/bin/env python3
"""
EHS 预案数据验证脚本

功能：
1. 空样本检测 - 检查数据是否为空
2. 重复样本检测 - 检查是否有重复的预案
3. 格式错误检测 - 验证 JSON 结构和字段格式
4. 数据质量报告 - 输出详细的质量分析报告

使用方法：
    python scripts/data/validate_schema.py data/raw/plans/sample_plans.json
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


class DataValidator:
    """EHS 预案数据验证器"""

    def __init__(self, schema: Dict[str, Any] = None):
        """初始化验证器

        Args:
            schema: JSON Schema 定义（可选）
        """
        self.schema = schema
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.stats: Dict[str, Any] = {}

    def load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """加载 JSON 数据文件

        Args:
            file_path: JSON 文件路径

        Returns:
            解析后的数据列表

        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON 解析失败
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"数据文件不存在：{file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("数据格式错误：根元素必须是数组")

        return data

    def validate_empty_samples(self, data: List[Dict[str, Any]]) -> bool:
        """检测空样本

        Args:
            data: 数据列表

        Returns:
            是否通过检测（无空样本返回 True）
        """
        print("\n[1] 空样本检测...")
        passed = True

        for i, item in enumerate(data):
            if not item:
                self.errors.append({
                    "type": "empty_sample",
                    "index": i,
                    "message": f"索引 {i} 处的样本为空对象"
                })
                passed = False
            elif not isinstance(item, dict):
                self.errors.append({
                    "type": "invalid_type",
                    "index": i,
                    "message": f"索引 {i} 处的样本不是 JSON 对象"
                })
                passed = False
            else:
                # 检查必填字段是否为空
                required_fields = ["id", "title", "event_type", "risk_level", "content", "actions"]
                for field in required_fields:
                    if field in item and not item[field]:
                        self.errors.append({
                            "type": "empty_field",
                            "index": i,
                            "field": field,
                            "message": f"样本 {item.get('id', i)} 的必填字段 '{field}' 为空"
                        })
                        passed = False

        if passed:
            print("    [OK] 通过：未发现空样本")
        else:
            print(f"    [FAIL] 失败：发现 {len([e for e in self.errors if e['type'] in ['empty_sample', 'empty_field', 'invalid_type']])} 个空样本问题")

        return passed

    def validate_duplicate_samples(self, data: List[Dict[str, Any]]) -> bool:
        """检测重复样本

        Args:
            data: 数据列表

        Returns:
            是否通过检测（无重复样本返回 True）
        """
        print("\n[2] 重复样本检测...")
        passed = True

        # 检查 ID 重复
        ids = [item.get("id") for item in data if item.get("id")]
        duplicate_ids = set([x for x in ids if ids.count(x) > 1])

        if duplicate_ids:
            for dup_id in duplicate_ids:
                self.errors.append({
                    "type": "duplicate_id",
                    "id": dup_id,
                    "message": f"预案 ID '{dup_id}' 重复"
                })
            passed = False

        # 检查标题重复
        titles = [item.get("title") for item in data if item.get("title")]
        duplicate_titles = set([x for x in titles if titles.count(x) > 1])

        if duplicate_titles:
            for dup_title in duplicate_titles:
                self.warnings.append({
                    "type": "duplicate_title",
                    "title": dup_title,
                    "message": f"预案标题 '{dup_title}' 重复（可能合理，需人工确认）"
                })
                print(f"    [WARN] 警告：标题 '{dup_title}' 重复")

        # 检查内容相似度（简单哈希比较）
        content_hashes = {}
        for i, item in enumerate(data):
            content = item.get("content", "")
            content_hash = hash(content)
            if content_hash in content_hashes:
                self.warnings.append({
                    "type": "similar_content",
                    "index1": content_hashes[content_hash],
                    "index2": i,
                    "message": f"样本 {i} 与样本 {content_hashes[content_hash]} 内容完全相同"
                })
            else:
                content_hashes[content_hash] = i

        if passed:
            print("    [OK] 通过：未发现 ID 重复")
        else:
            print(f"    [FAIL] 失败：发现 {len(duplicate_ids)} 个重复 ID")

        return passed

    def validate_format(self, data: List[Dict[str, Any]]) -> bool:
        """检测格式错误

        Args:
            data: 数据列表

        Returns:
            是否通过检测
        """
        print("\n[3] 格式错误检测...")
        passed = True

        # 字段格式定义
        validators = {
            "id": (lambda x: re.match(r'^PLAN-\d{4}$', x) is not None, "必须是 PLAN-XXXX 格式"),
            "event_type": (
                lambda x: x in ["fire", "gas_leak", "temperature_abnormal", "intrusion",
                               "power_failure", "chemical_spill", "earthquake", "flood"],
                "必须是预定义的事件类型之一"
            ),
            "risk_level": (
                lambda x: x in ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                "必须是 LOW/MEDIUM/HIGH/CRITICAL 之一"
            ),
            "version": (lambda x: re.match(r'^\d+\.\d+\.\d+$', x) is not None, "必须是 X.Y.Z 格式"),
            "last_updated": (self._validate_iso_datetime, "必须是 ISO 8601 日期时间格式"),
        }

        # 数值范围验证
        range_validators = {
            "actions": (lambda x: isinstance(x, list) and len(x) >= 3, "actions 数组至少需要 3 个元素"),
            "content": (lambda x: isinstance(x, str) and 50 <= len(x) <= 5000, "content 长度必须在 50-5000 字符之间"),
            "title": (lambda x: isinstance(x, str) and 5 <= len(x) <= 100, "title 长度必须在 5-100 字符之间"),
        }

        for i, item in enumerate(data):
            item_id = item.get("id", f"索引 {i}")

            # 字段格式验证
            for field, (validator, error_msg) in validators.items():
                if field in item:
                    if not validator(item[field]):
                        self.errors.append({
                            "type": "invalid_format",
                            "index": i,
                            "field": field,
                            "sample_id": item_id,
                            "value": str(item[field])[:50],
                            "message": f"样本 {item_id} 的 '{field}' 字段格式错误：{error_msg}"
                        })
                        passed = False

            # 数值范围验证
            for field, (validator, error_msg) in range_validators.items():
                if field in item:
                    if not validator(item[field]):
                        self.errors.append({
                            "type": "out_of_range",
                            "index": i,
                            "field": field,
                            "sample_id": item_id,
                            "message": f"样本 {item_id} 的 '{field}' 字段超出范围：{error_msg}"
                        })
                        passed = False

            # actions 数组内元素验证
            if "actions" in item and isinstance(item["actions"], list):
                for j, action in enumerate(item["actions"]):
                    if not isinstance(action, dict):
                        self.errors.append({
                            "type": "invalid_action",
                            "index": i,
                            "action_index": j,
                            "sample_id": item_id,
                            "message": f"样本 {item_id} 的第 {j} 个 action 不是对象"
                        })
                        passed = False
                    elif not all(k in action for k in ["step", "action", "role"]):
                        self.errors.append({
                            "type": "missing_action_field",
                            "index": i,
                            "action_index": j,
                            "sample_id": item_id,
                            "message": f"样本 {item_id} 的第 {j} 个 action 缺少必填字段"
                        })
                        passed = False

        if passed:
            print("    [OK] 通过：所有字段格式正确")
        else:
            print(f"    [FAIL] 失败：发现 {len([e for e in self.errors if e['type'] in ['invalid_format', 'out_of_range', 'invalid_action', 'missing_action_field']])} 个格式错误")

        return passed

    def _validate_iso_datetime(self, value: str) -> bool:
        """验证 ISO 8601 日期时间格式

        Args:
            value: 待验证的日期字符串

        Returns:
            是否有效
        """
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            return False

    def generate_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成数据质量报告

        Args:
            data: 数据列表

        Returns:
            报告字典
        """
        self.stats = {
            "total_samples": len(data),
            "valid_samples": len(data) - len(set(e["index"] for e in self.errors if "index" in e)),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "error_types": {},
            "event_type_distribution": {},
            "risk_level_distribution": {}
        }

        # 统计错误类型
        for error in self.errors:
            error_type = error.get("type", "unknown")
            self.stats["error_types"][error_type] = self.stats["error_types"].get(error_type, 0) + 1

        # 统计事件类型分布
        for item in data:
            event_type = item.get("event_type", "unknown")
            self.stats["event_type_distribution"][event_type] = \
                self.stats["event_type_distribution"].get(event_type, 0) + 1

            risk_level = item.get("risk_level", "unknown")
            self.stats["risk_level_distribution"][risk_level] = \
                self.stats["risk_level_distribution"].get(risk_level, 0) + 1

        return {
            "passed": len(self.errors) == 0,
            "timestamp": datetime.now().isoformat(),
            "statistics": self.stats,
            "errors": self.errors,
            "warnings": self.warnings
        }

    def validate(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        """执行完整验证流程

        Args:
            file_path: 数据文件路径

        Returns:
            (是否通过，报告字典)
        """
        print("=" * 60)
        print("EHS 预案数据验证")
        print("=" * 60)
        print(f"文件：{file_path}")

        # 加载数据
        try:
            data = self.load_data(file_path)
            print(f"加载成功：{len(data)} 条记录")
        except Exception as e:
            print(f"加载失败：{e}")
            return False, {"passed": False, "error": str(e)}

        # 执行验证
        empty_passed = self.validate_empty_samples(data)
        duplicate_passed = self.validate_duplicate_samples(data)
        format_passed = self.validate_format(data)

        # 生成报告
        report = self.generate_report(data)

        # 输出总结
        print("\n" + "=" * 60)
        print("验证总结")
        print("=" * 60)
        print(f"总样本数：{self.stats.get('total_samples', 0)}")
        print(f"有效样本数：{self.stats.get('valid_samples', 0)}")
        print(f"错误数：{self.stats.get('error_count', 0)}")
        print(f"警告数：{self.stats.get('warning_count', 0)}")

        # 事件类型分布
        print("\n事件类型分布:")
        for event_type, count in sorted(self.stats.get('event_type_distribution', {}).items()):
            print(f"  - {event_type}: {count}")

        # 风险等级分布
        print("\n风险等级分布:")
        for risk_level, count in sorted(self.stats.get('risk_level_distribution', {}).items()):
            print(f"  - {risk_level}: {count}")

        overall_passed = empty_passed and duplicate_passed and format_passed
        print("\n" + "=" * 60)
        if overall_passed:
            print("[OK] 验证通过：数据质量良好")
        else:
            print("[FAIL] 验证失败：请修复上述错误")
        print("=" * 60)

        return overall_passed, report


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法：python validate_schema.py <数据文件路径>")
        print("示例：python validate_schema.py data/raw/plans/sample_plans.json")
        sys.exit(1)

    file_path = sys.argv[1]

    # 创建验证器并执行验证
    validator = DataValidator()
    passed, report = validator.validate(file_path)

    # 保存报告
    report_path = Path(file_path).parent / "validation_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n验证报告已保存至：{report_path}")

    # 返回退出码
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
