from __future__ import annotations

from typing import Dict, List, Optional
from agentic.core.types import Message


class SimpleMemory:
    """In-memory conversation + key-value store."""

    def __init__(self, max_messages: int = 50) -> None:
        self.messages: List[Message] = []
        self.kv: Dict[str, str] = {}
        self.max_messages = max_messages

    def add(self, msg: Message) -> None:
        self.messages.append(msg)
        if len(self.messages) > self.max_messages:
            system = [m for m in self.messages if m.role.value == "system"]
            rest = [m for m in self.messages if m.role.value != "system"]
            self.messages = system + rest[-(self.max_messages - len(system)) :]

    def get_history(self) -> List[Message]:
        return list(self.messages)

    def set(self, key: str, value: str) -> None:
        self.kv[key] = value

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.kv.get(key, default)

    def clear(self) -> None:
        self.messages.clear()
        self.kv.clear()
