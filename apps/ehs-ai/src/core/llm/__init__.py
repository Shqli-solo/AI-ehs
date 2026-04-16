# apps/ehs-ai/src/core/llm/__init__.py
"""LLM 适配器模块 - 模型无关的抽象层"""
from src.core.llm.base import LLMAdapter, LLMResponse, ChatMessage

__all__ = ["LLMAdapter", "LLMResponse", "ChatMessage"]
