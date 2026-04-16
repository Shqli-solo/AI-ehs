"""
EHS AI 模型包

导出所有模型和配置类。
"""

from .risk_classifier_config import RiskClassifierConfig
from .embedding_model import EmbeddingConfig, EmbeddingModel, create_embedding_model

__all__ = [
    "RiskClassifierConfig",
    "EmbeddingConfig",
    "EmbeddingModel",
    "create_embedding_model",
]

# 延迟导入依赖 torch 的模块
def __getattr__(name):
    """延迟导入，避免 torch 在导入时即加载"""
    if name in ("RiskClassifier", "RiskClassifierModel", "create_risk_classifier"):
        try:
            from . import risk_classifier
            return getattr(risk_classifier, name)
        except ImportError as e:
            raise ImportError(f"{name} requires torch: {e}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

