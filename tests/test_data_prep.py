#!/usr/bin/env python3
"""
EHS 预案数据准备测试

测试覆盖：
1. 数据验证脚本 - 空样本、重复样本、格式错误检测
2. 数据准备脚本 - 指令微调、风险分级、Embedding 数据生成
3. 数据质量 - 格式正确性、完整性

运行测试：
    python -m pytest tests/test_data_prep.py -v
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.data.validate_schema import DataValidator
from scripts.data.prepare_data import DataPreparation


class TestDataValidator:
    """数据验证器测试"""

    @pytest.fixture
    def validator(self):
        """创建验证器实例"""
        return DataValidator()

    @pytest.fixture
    def temp_data_file(self, tmp_path):
        """创建临时数据文件"""
        data = [
            {
                "id": "PLAN-0001",
                "title": "测试预案 1",
                "event_type": "fire",
                "risk_level": "HIGH",
                "content": "这是一个测试预案，用于验证数据格式是否正确。内容长度需要满足最低五十字以上的要求，所以需要添加更多的内容来确保长度足够。",
                "actions": [
                    {"step": 1, "action": "第一步行动描述", "role": "现场人员"},
                    {"step": 2, "action": "第二步行动描述", "role": "安全员"},
                    {"step": 3, "action": "第三步行动描述", "role": "指挥官"}
                ],
                "contacts": [{"name": "张三", "role": "主管", "phone": "138-0000-0000"}],
                "resources": ["灭火器"],
                "training_requirements": "年度培训要求",
                "last_updated": "2026-04-16T00:00:00Z",
                "version": "1.0.0"
            }
        ]
        file_path = tmp_path / "test_data.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return str(file_path)

    def test_validate_empty_samples_pass(self, validator, temp_data_file):
        """测试空样本检测 - 通过情况"""
        data = validator.load_data(temp_data_file)
        passed = validator.validate_empty_samples(data)
        assert passed is True
        assert len([e for e in validator.errors if e['type'] == 'empty_sample']) == 0

    def test_validate_empty_samples_fail(self, validator, tmp_path):
        """测试空样本检测 - 失败情况"""
        # 创建包含空样本的数据
        data = [
            {"id": "PLAN-0001", "title": "有效预案"},
            {},  # 空对象
            None  # None 值
        ]
        file_path = tmp_path / "empty_data.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        loaded_data = validator.load_data(str(file_path))
        passed = validator.validate_empty_samples(loaded_data)
        assert passed is False
        assert len(validator.errors) >= 2  # 至少检测到空对象和 None

    def test_validate_duplicate_samples_pass(self, validator, temp_data_file):
        """测试重复样本检测 - 通过情况"""
        data = validator.load_data(temp_data_file)
        passed = validator.validate_duplicate_samples(data)
        assert passed is True

    def test_validate_duplicate_samples_fail(self, validator, tmp_path):
        """测试重复样本检测 - 失败情况"""
        # 创建包含重复 ID 的数据
        data = [
            {
                "id": "PLAN-0001",
                "title": "预案 1",
                "event_type": "fire",
                "risk_level": "HIGH",
                "content": "测试内容 1",
                "actions": [
                    {"step": 1, "action": "行动 1", "role": "人员 1"},
                    {"step": 2, "action": "行动 2", "role": "人员 2"},
                    {"step": 3, "action": "行动 3", "role": "人员 3"}
                ]
            },
            {
                "id": "PLAN-0001",  # 重复 ID
                "title": "预案 2",
                "event_type": "gas_leak",
                "risk_level": "MEDIUM",
                "content": "测试内容 2",
                "actions": [
                    {"step": 1, "action": "行动 1", "role": "人员 1"},
                    {"step": 2, "action": "行动 2", "role": "人员 2"},
                    {"step": 3, "action": "行动 3", "role": "人员 3"}
                ]
            }
        ]
        file_path = tmp_path / "duplicate_data.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        loaded_data = validator.load_data(str(file_path))
        passed = validator.validate_duplicate_samples(loaded_data)
        assert passed is False
        assert len([e for e in validator.errors if e['type'] == 'duplicate_id']) == 1

    def test_validate_format_pass(self, validator, temp_data_file):
        """测试格式检测 - 通过情况"""
        data = validator.load_data(temp_data_file)
        passed = validator.validate_format(data)
        assert passed is True

    def test_validate_format_invalid_id(self, validator, tmp_path):
        """测试格式检测 - 无效 ID 格式"""
        data = [
            {
                "id": "INVALID-ID",  # 不符合 PLAN-XXXX 格式
                "title": "测试预案",
                "event_type": "fire",
                "risk_level": "HIGH",
                "content": "这是一个测试预案，内容长度需要满足最低要求五十字以上。",
                "actions": [
                    {"step": 1, "action": "行动 1", "role": "人员"},
                    {"step": 2, "action": "行动 2", "role": "人员"},
                    {"step": 3, "action": "行动 3", "role": "人员"}
                ]
            }
        ]
        file_path = tmp_path / "invalid_id.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        loaded_data = validator.load_data(str(file_path))
        passed = validator.validate_format(loaded_data)
        assert passed is False
        assert len([e for e in validator.errors if e['type'] == 'invalid_format']) >= 1

    def test_validate_format_invalid_event_type(self, validator, tmp_path):
        """测试格式检测 - 无效事件类型"""
        data = [
            {
                "id": "PLAN-0001",
                "title": "测试预案",
                "event_type": "invalid_type",  # 无效的事件类型
                "risk_level": "HIGH",
                "content": "这是一个测试预案，内容长度需要满足最低要求五十字以上。",
                "actions": [
                    {"step": 1, "action": "行动 1", "role": "人员"},
                    {"step": 2, "action": "行动 2", "role": "人员"},
                    {"step": 3, "action": "行动 3", "role": "人员"}
                ]
            }
        ]
        file_path = tmp_path / "invalid_event.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        loaded_data = validator.load_data(str(file_path))
        passed = validator.validate_format(loaded_data)
        assert passed is False

    def test_validate_format_invalid_risk_level(self, validator, tmp_path):
        """测试格式检测 - 无效风险等级"""
        data = [
            {
                "id": "PLAN-0001",
                "title": "测试预案",
                "event_type": "fire",
                "risk_level": "INVALID",  # 无效的风险等级
                "content": "这是一个测试预案，内容长度需要满足最低要求五十字以上。",
                "actions": [
                    {"step": 1, "action": "行动 1", "role": "人员"},
                    {"step": 2, "action": "行动 2", "role": "人员"},
                    {"step": 3, "action": "行动 3", "role": "人员"}
                ]
            }
        ]
        file_path = tmp_path / "invalid_risk.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        loaded_data = validator.load_data(str(file_path))
        passed = validator.validate_format(loaded_data)
        assert passed is False

    def test_validate_format_content_too_short(self, validator, tmp_path):
        """测试格式检测 - 内容太短"""
        data = [
            {
                "id": "PLAN-0001",
                "title": "测试预案",
                "event_type": "fire",
                "risk_level": "HIGH",
                "content": "太短",  # 少于 50 字符
                "actions": [
                    {"step": 1, "action": "行动 1", "role": "人员"},
                    {"step": 2, "action": "行动 2", "role": "人员"},
                    {"step": 3, "action": "行动 3", "role": "人员"}
                ]
            }
        ]
        file_path = tmp_path / "short_content.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        loaded_data = validator.load_data(str(file_path))
        passed = validator.validate_format(loaded_data)
        assert passed is False

    def test_validate_format_insufficient_actions(self, validator, tmp_path):
        """测试格式检测 - actions 数量不足"""
        data = [
            {
                "id": "PLAN-0001",
                "title": "测试预案",
                "event_type": "fire",
                "risk_level": "HIGH",
                "content": "这是一个测试预案，内容长度需要满足最低要求五十字以上。",
                "actions": [
                    {"step": 1, "action": "只有一个行动", "role": "人员"}
                ]  # 少于 3 个
            }
        ]
        file_path = tmp_path / "insufficient_actions.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        loaded_data = validator.load_data(str(file_path))
        passed = validator.validate_format(loaded_data)
        assert passed is False

    def test_validate_full_sample_data(self, validator):
        """测试完整样本数据验证"""
        sample_data_path = "data/raw/plans/sample_plans.json"
        if not Path(sample_data_path).exists():
            pytest.skip(f"样本数据文件不存在：{sample_data_path}")

        passed, report = validator.validate(sample_data_path)
        assert passed is True or len(validator.errors) == 0  # 允许警告


class TestDataPreparation:
    """数据准备脚本测试"""

    @pytest.fixture
    def sample_data(self):
        """样本数据"""
        return [
            {
                "id": "PLAN-0001",
                "title": "火灾事故专项应急预案",
                "event_type": "fire",
                "risk_level": "HIGH",
                "content": "这是一个火灾应急预案的详细内容描述，用于测试数据准备功能。",
                "actions": [
                    {"step": 1, "action": "发现火情立即报警", "role": "第一发现人", "timeout_seconds": 30},
                    {"step": 2, "action": "组织人员疏散", "role": "安全员", "timeout_seconds": 120},
                    {"step": 3, "action": "进行初期灭火", "role": "义务消防队", "timeout_seconds": 300}
                ],
                "contacts": [{"name": "张三", "role": "安全主管", "phone": "138-0000-0000"}],
                "resources": ["灭火器", "消防栓"],
                "training_requirements": "年度消防培训",
                "last_updated": "2026-04-16T00:00:00Z",
                "version": "1.0.0"
            },
            {
                "id": "PLAN-0002",
                "title": "气体泄漏应急处置预案",
                "event_type": "gas_leak",
                "risk_level": "CRITICAL",
                "content": "这是一个气体泄漏应急预案的详细内容描述，用于测试数据准备功能。",
                "actions": [
                    {"step": 1, "action": "关闭电源和明火", "role": "第一发现人", "timeout_seconds": 30},
                    {"step": 2, "action": "关闭泄漏源阀门", "role": "处置人员", "timeout_seconds": 120},
                    {"step": 3, "action": "疏散人员至上风处", "role": "安全员", "timeout_seconds": 300}
                ],
                "contacts": [{"name": "李四", "role": "气体主管", "phone": "138-0000-0001"}],
                "resources": ["防毒面具", "检测仪"],
                "training_requirements": "季度气体安全培训",
                "last_updated": "2026-04-16T00:00:00Z",
                "version": "1.0.0"
            }
        ]

    @pytest.fixture
    def temp_data_file(self, tmp_path, sample_data):
        """创建临时数据文件"""
        file_path = tmp_path / "sample_data.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False)
        return str(file_path)

    @pytest.fixture
    def output_dir(self, tmp_path):
        """创建输出目录"""
        output = tmp_path / "processed"
        output.mkdir()
        return str(output)

    def test_generate_instruction_data(self, temp_data_file, output_dir):
        """测试指令微调数据生成"""
        preparer = DataPreparation(temp_data_file, output_dir)
        preparer.load_data()
        data = preparer.generate_instruction_data()

        assert len(data) > 0
        # 每个预案应该生成 4 种任务类型的数据
        assert len(data) >= len(preparer.data) * 4

        # 检查数据结构
        for item in data:
            assert "instruction" in item
            assert "input" in item
            assert "output" in item
            assert "task_type" in item
            assert "source_plan_id" in item

        # 检查任务类型多样性
        task_types = set(item["task_type"] for item in data)
        assert "plan_retrieval" in task_types
        assert "risk_assessment" in task_types
        assert "action_generation" in task_types
        assert "knowledge_qa" in task_types

    def test_generate_risk_classification_data(self, temp_data_file, output_dir):
        """测试风险分级数据生成"""
        preparer = DataPreparation(temp_data_file, output_dir)
        preparer.load_data()
        data = preparer.generate_risk_classification_data()

        assert len(data) > 0

        # 检查数据结构
        for item in data:
            assert "text" in item
            assert "label" in item
            assert "risk_level" in item
            assert "event_type" in item
            # 标签应该是 0-3 的整数
            assert isinstance(item["label"], int)
            assert 0 <= item["label"] <= 3

    def test_generate_embedding_data(self, temp_data_file, output_dir):
        """测试 Embedding 数据生成"""
        preparer = DataPreparation(temp_data_file, output_dir)
        preparer.load_data()
        data = preparer.generate_embedding_data()

        assert len(data) > 0

        # 检查数据结构
        for item in data:
            assert "text1" in item
            assert "text2" in item
            assert "label" in item
            assert "pair_type" in item
            # 标签应该是 0.0-1.0 的浮点数
            assert isinstance(item["label"], float) or isinstance(item["label"], int)
            assert 0.0 <= item["label"] <= 1.0

    def test_prepare_all(self, temp_data_file, output_dir):
        """测试完整数据准备流程"""
        preparer = DataPreparation(temp_data_file, output_dir)
        output_files = preparer.prepare_all()

        # 检查输出文件
        assert "instruction" in output_files
        assert "risk_classification" in output_files
        assert "embedding" in output_files

        # 检查文件是否存在
        for file_path in output_files.values():
            assert Path(file_path).exists()

        # 检查统计报告
        stats_files = list(Path(output_dir).glob("preparation_stats_*.json"))
        assert len(stats_files) > 0

    def test_preview(self, temp_data_file, output_dir, capsys):
        """测试数据预览功能"""
        preparer = DataPreparation(temp_data_file, output_dir)
        preparer.preview()

        captured = capsys.readouterr()
        assert "数据预览" in captured.out
        assert "总样本数" in captured.out


class TestDataQuality:
    """数据质量测试"""

    def test_sample_plans_data_quality(self):
        """测试样本预案数据质量"""
        sample_path = "data/raw/plans/sample_plans.json"
        if not Path(sample_path).exists():
            pytest.skip(f"样本文件不存在：{sample_path}")

        with open(sample_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 检查基本质量
        assert len(data) >= 5, "样本数据应该至少有 5 条记录"

        # 检查每条记录
        for plan in data:
            # 必填字段
            assert "id" in plan, "缺少 id 字段"
            assert "title" in plan, "缺少 title 字段"
            assert "event_type" in plan, "缺少 event_type 字段"
            assert "risk_level" in plan, "缺少 risk_level 字段"
            assert "content" in plan, "缺少 content 字段"
            assert "actions" in plan, "缺少 actions 字段"

            # 格式验证
            assert plan["id"].startswith("PLAN-"), "ID 必须以 PLAN-开头"
            assert len(plan["actions"]) >= 3, "actions 至少需要 3 个元素"

    def test_no_duplicate_ids_in_sample(self):
        """测试样本数据无重复 ID"""
        sample_path = "data/raw/plans/sample_plans.json"
        if not Path(sample_path).exists():
            pytest.skip(f"样本文件不存在：{sample_path}")

        with open(sample_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        ids = [plan["id"] for plan in data if "id" in plan]
        assert len(ids) == len(set(ids)), "样本数据中存在重复 ID"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
