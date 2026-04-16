# apps/ehs-ai/src/ports/secondary/storage.py
"""存储接口定义 - Secondary Ports"""
from abc import ABC, abstractmethod
from typing import Optional


class StoragePort(ABC):
    """存储端口接口 - 定义存储操作的契约"""

    @abstractmethod
    def search(self, query: str, top_k: int = 20) -> list:
        """
        检索数据

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        pass


class VectorStoragePort(StoragePort):
    """向量存储端口接口"""

    @abstractmethod
    def search_by_vector(self, embedding: list, top_k: int = 20) -> list:
        """
        向量相似度检索

        Args:
            embedding: 向量嵌入
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        pass

    @abstractmethod
    def encode(self, text: str) -> list:
        """
        将文本编码为向量

        Args:
            text: 输入文本

        Returns:
            向量嵌入
        """
        pass


class TextStoragePort(StoragePort):
    """文本存储端口接口（如 Elasticsearch）"""

    @abstractmethod
    def search(self, query: str, event_type: Optional[str] = None, top_k: int = 20) -> list:
        """
        文本检索（支持事件类型过滤）

        Args:
            query: 查询文本
            event_type: 事件类型
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        pass
