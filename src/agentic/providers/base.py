from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional
from agentic.core.types import Message, ToolCall
from agentic.core.registry import Tool


class BaseProvider(ABC):
    """Abstract LLM provider."""

    def __init__(self, model: str, **kwargs: Any) -> None:
        self.model = model
        self.kwargs = kwargs

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Tool]] = None,
        tool_choice: str = "auto",
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Message:
        """Return a single assistant Message (may contain tool_calls)."""
        ...

    async def stream_chat(
        self,
        messages: List[Message],
        tools: Optional[List[Tool]] = None,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Yield events: {"type": "token", "text": ...} or {"type": "tool_call", ...}"""
        msg = await self.chat(messages, tools=tools, stream=False, **kwargs)
        if msg.content:
            yield {"type": "token", "text": msg.content}
        if msg.tool_calls:
            for tc in msg.tool_calls:
                yield {"type": "tool_call", "tool_call": tc}
        yield {"type": "done", "message": msg}
