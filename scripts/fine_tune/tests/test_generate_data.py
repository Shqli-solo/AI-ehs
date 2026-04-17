# scripts/fine_tune/tests/test_generate_data.py
"""微调数据生成器测试"""

import json
import pytest
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "fine_tune"


class TestInstructionData:
    def test_train_file_exists(self):
        assert (DATA_DIR / "instruction" / "train.jsonl").exists()

    def test_eval_file_exists(self):
        assert (DATA_DIR / "instruction" / "eval.jsonl").exists()

    def test_train_has_sufficient_samples(self):
        with open(DATA_DIR / "instruction" / "train.jsonl", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 300, f"Only {len(lines)} training samples"

    def test_eval_has_sufficient_samples(self):
        with open(DATA_DIR / "instruction" / "eval.jsonl", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 1, f"Only {len(lines)} eval samples"

    def test_format_is_valid(self):
        with open(DATA_DIR / "instruction" / "train.jsonl", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                assert "instruction" in item
                assert "input" in item
                assert "output" in item


class TestRiskData:
    def test_train_file_exists(self):
        assert (DATA_DIR / "risk" / "train.jsonl").exists()

    def test_train_has_sufficient_samples(self):
        with open(DATA_DIR / "risk" / "train.jsonl", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 500

    def test_labels_are_valid(self):
        with open(DATA_DIR / "risk" / "train.jsonl", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                assert item["label"] in [0, 1, 2]


class TestComplianceData:
    def test_train_file_exists(self):
        assert (DATA_DIR / "compliance" / "train.jsonl").exists()

    def test_labels_are_binary(self):
        with open(DATA_DIR / "compliance" / "train.jsonl", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                assert item["compliant"] in [0, 1]


class TestEmbeddingData:
    def test_train_file_exists(self):
        assert (DATA_DIR / "embedding" / "train.jsonl").exists()

    def test_eval_file_exists(self):
        assert (DATA_DIR / "embedding" / "eval.jsonl").exists()

    def test_has_sufficient_pairs(self):
        with open(DATA_DIR / "embedding" / "train.jsonl", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 1000

    def test_format_is_valid(self):
        with open(DATA_DIR / "embedding" / "train.jsonl", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                assert "term_a" in item
                assert "term_b" in item
                assert "related" in item
                assert item["related"] in [0, 1]
