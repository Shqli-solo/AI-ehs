"""
EHS 风险分类器配置

不依赖 PyTorch 的纯配置模块，用于测试和配置管理。
"""

from typing import Dict


class RiskClassifierConfig:
    """风险分类器配置类"""

    def __init__(
        self,
        model_name: str = "bert-base-chinese",
        num_labels: int = 4,
        hidden_dim: int = 256,
        dropout: float = 0.3,
        num_layers: int = 2,
    ):
        self.model_name = model_name
        self.num_labels = num_labels
        self.hidden_dim = hidden_dim
        self.dropout = dropout
        self.num_layers = num_layers

        # 风险等级标签映射
        self.label2text = {
            0: "LOW",
            1: "MEDIUM",
            2: "HIGH",
            3: "CRITICAL",
        }
        self.text2label = {v: k for k, v in self.label2text.items()}

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "model_name": self.model_name,
            "num_labels": self.num_labels,
            "hidden_dim": self.hidden_dim,
            "dropout": self.dropout,
            "num_layers": self.num_layers,
            "label2text": self.label2text,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RiskClassifierConfig":
        """从字典创建"""
        return cls(
            model_name=data.get("model_name", "bert-base-chinese"),
            num_labels=data.get("num_labels", 4),
            hidden_dim=data.get("hidden_dim", 256),
            dropout=data.get("dropout", 0.3),
            num_layers=data.get("num_layers", 2),
        )
