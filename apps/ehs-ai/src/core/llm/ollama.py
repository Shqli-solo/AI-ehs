# apps/ehs-ai/src/core/llm/ollama.py
"""
Ollama LLM 适配器

Ollama 支持 OpenAI 兼容 API（/v1/chat/completions），
也支持原生 API（/api/generate /api/chat）。
这里使用 OpenAI 兼容端点以保持统一格式。
"""
import json
import logging
from typing import List, Dict, Any, Optional

import httpx

from src.core.llm.base import LLMAdapter, LLMResponse, ChatMessage

logger = logging.getLogger(__name__)


class OllamaAdapter(LLMAdapter):
    """
    Ollama LLM 适配器

    使用 OpenAI 兼容端点: POST /v1/chat/completions
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:11434/v1/chat/completions",
        model: str = "qwen3:7b",
        timeout: float = 120.0,
    ):
        self._endpoint = endpoint
        self._model = model
        self._timeout = timeout

    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求"""
        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(self._endpoint, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        return LLMResponse(
            content=content,
            model=self._model,
            usage=data.get("usage"),
            raw=data,
        )

    async def chat_json(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """发送聊天请求，期望返回 JSON"""
        # 添加 JSON 格式提示
        json_messages = list(messages)
        json_messages.append(
            ChatMessage(
                role="system",
                content="请只返回 JSON 格式，不要其他内容。"
            )
        )

        response = await self.chat(
            messages=json_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        # 从响应中提取 JSON
        text = response.content.strip()
        # 尝试找到 JSON 块
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        raise ValueError(f"LLM 返回内容不是有效 JSON: {text[:200]}")
