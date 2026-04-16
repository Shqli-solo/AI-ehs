# apps/ehs-ai/src/core/config.py
"""配置管理"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


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

    # CORS - 生产环境使用环境变量配置
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://ehs.example.com"

    # JWT 认证
    JWT_SECRET: str = "change-this-secret-in-production"
    JWT_EXPIRATION_MINUTES: int = 60

    # 认证开关（开发环境可关闭认证）
    AUTH_ENABLED: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        """解析 CORS 来源列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
