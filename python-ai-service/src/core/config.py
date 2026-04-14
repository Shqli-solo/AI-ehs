# python-ai-service/src/core/config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置管理"""

    # 服务配置
    SERVICE_NAME: str = "ehs-ai-service"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Elasticsearch 配置
    ES_URL: str = "http://localhost:9200"
    ES_INDEX: str = "ehs-documents"

    # Milvus 配置
    MILVUS_URL: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "ehs-vectors"

    # Neo4j 配置
    NEO4J_URL: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # 模型配置
    RERANK_MODEL: str = "BAAI/bge-reranker-base"
    EMBEDDING_MODEL: str = "BAAI/bge-base-zh-v1.5"

    # 检索配置
    TOP_K: int = 5
    RERANK_TOP_K: int = 20

    class Config:
        env_file = ".env"


settings = Settings()
