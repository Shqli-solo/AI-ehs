# apps/ehs-ai/src/core/llm/openai.py
"""
OpenAI LLM 适配器
"""
import json
import logging
from typing import List, Dict, Any

import httpx

from src.core.llm.base import LLMAdapter, LLMResponse, ChatMessage

logger = logging.getLogger(__name__)


class OpenAIAdapter(LLMAdapter):
    """
    OpenAI LLM 适配器
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str = "https://api.openai.com/v1/chat/completions",
        model: str = "gpt-4",
        timeout: float = 30.0,
    ):
        self._api_key = api_key
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
        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                self._endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
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
        json_messages = list(messages)
        json_messages.append(
            ChatMessage(role="system", content="请只返回 JSON 格式，不要其他内容。")
        )

        response = await self.chat(
            messages=json_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        text = response.content.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        raise ValueError(f"LLM 返回内容不是有效 JSON: {text[:200]}")
