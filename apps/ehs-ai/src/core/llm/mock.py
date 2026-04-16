# apps/ehs-ai/src/core/llm/mock.py
"""
Mock LLM 适配器 - 用于测试
"""
import json
from typing import List, Dict, Any

from src.core.llm.base import LLMAdapter, LLMResponse, ChatMessage


class MockLLMAdapter(LLMAdapter):
    """
    Mock LLM 适配器

    返回预设响应，不实际调用 LLM。
    用于测试和开发环境。
    """

    def __init__(self, json_response: Dict[str, Any] = None):
        self._json_response = json_response or {
            "risk_level": "high",
            "confidence": 0.85,
            "factors": ["烟雾检测", "温度异常"],
            "recommended_actions": ["启动火灾应急预案", "疏散人员"],
        }

    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        return LLMResponse(
            content=json.dumps(self._json_response, ensure_ascii=False),
            model="mock-llm",
            usage={"prompt_tokens": 0, "completion_tokens": 0},
        )

    async def chat_json(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        return self._json_response.copy()
