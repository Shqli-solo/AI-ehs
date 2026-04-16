# apps/ehs-ai/src/core/llm/base.py
"""
LLM 适配器抽象基类 - Port（六边形架构）

设计目标：
- 让上层 Agent 代码与具体 LLM 实现解耦
- 支持 Ollama、OpenAI、Claude、本地 Mock 等多种后端
- 统一的聊天接口，返回结构化响应
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    model: str = ""
    usage: Dict[str, int] = None
    raw: Any = None  # 原始响应对象

    def json(self) -> str:
        """返回内容（兼容旧的 .json() 调用）"""
        return self.content


class LLMAdapter(ABC):
    """
    LLM 适配器抽象基类（Secondary Port）

    所有 LLM 后端必须实现此接口：
    - OllamaAdapter
    - OpenAIAdapter
    - ClaudeAdapter
    - MockAdapter
    """

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        发送聊天请求

        Args:
            messages: 聊天消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他模型特定参数

        Returns:
            LLM 响应
        """
        ...

    @abstractmethod
    async def chat_json(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送聊天请求，期望返回 JSON

        Args:
            messages: 聊天消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他模型特定参数

        Returns:
            解析后的 JSON 字典
        """
        ...
