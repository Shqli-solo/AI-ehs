# apps/ehs-ai/src/core/config.py
"""配置管理"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "EHS AI Service"
    APP_VERSION: str = "2.0.0"

    # Elasticsearch
    ES_URL: str = "http://localhost:9200"
    ES_INDEX: str = "ehs_plans"

    # Milvus
    MILVUS_URL: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "ehs_plans"

    # Embedding 模型
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"

    # Reranker 模型
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"

    # LLM
    LLM_ENDPOINT: str = "http://localhost:8080/v1/chat/completions"
    LLM_MODEL: str = "ehs-risk-assessment"

    # 日志
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
