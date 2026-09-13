from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolCall(BaseModel):
    id: str = Field(default_factory=lambda: f"call_{uuid.uuid4().hex[:12]}")
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    tool_call_id: str
    name: str
    content: str
    is_error: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Message(BaseModel):
    role: Role
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None  # for tool results
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_openai(self) -> Dict[str, Any]:
        msg: Dict[str, Any] = {"role": self.role.value}
        if self.content is not None:
            msg["content"] = self.content
        if self.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": __import__("json").dumps(tc.arguments),
                    },
                }
                for tc in self.tool_calls
            ]
        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id
        if self.name:
            msg["name"] = self.name
        return msg

    def to_anthropic(self) -> Dict[str, Any]:
        # Simplified; full conversion handled in provider
        if self.role == Role.TOOL:
            return {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": self.tool_call_id,
                        "content": self.content or "",
                    }
                ],
            }
        content: Any = self.content or ""
        if self.tool_calls:
            content = []
            if self.content:
                content.append({"type": "text", "text": self.content})
            for tc in self.tool_calls:
                content.append(
                    {
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.name,
                        "input": tc.arguments,
                    }
                )
        return {"role": "assistant" if self.role == Role.ASSISTANT else self.role.value, "content": content}


class AgentEvent(BaseModel):
    type: str  # "token", "tool_call", "tool_result", "message", "error", "done"
    data: Any = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentResult(BaseModel):
    final_message: Message
    messages: List[Message]
    tool_calls_executed: List[ToolResult] = Field(default_factory=list)
    usage: Dict[str, Any] = Field(default_factory=dict)
    events: List[AgentEvent] = Field(default_factory=list)
