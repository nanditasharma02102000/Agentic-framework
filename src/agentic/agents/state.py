from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import copy


class SharedState(BaseModel):
    """
    Blackboard / shared memory for multi-agent systems.
    Agents read/write keys; messages and artifacts are versioned lightly.
    """

    data: Dict[str, Any] = Field(default_factory=dict)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any, agent: str = "system") -> None:
        self.data[key] = value
        self.history.append(
            {
                "op": "set",
                "key": key,
                "agent": agent,
                "ts": datetime.utcnow().isoformat(),
            }
        )

    def update(self, mapping: Dict[str, Any], agent: str = "system") -> None:
        for k, v in mapping.items():
            self.set(k, v, agent=agent)

    def append_message(self, agent: str, role: str, content: str) -> None:
        self.messages.append(
            {
                "agent": agent,
                "role": role,
                "content": content,
                "ts": datetime.utcnow().isoformat(),
            }
        )

    def set_artifact(self, name: str, value: Any, agent: str = "system") -> None:
        self.artifacts[name] = value
        self.history.append(
            {
                "op": "artifact",
                "name": name,
                "agent": agent,
                "ts": datetime.utcnow().isoformat(),
            }
        )

    def snapshot(self) -> Dict[str, Any]:
        return {
            "data": copy.deepcopy(self.data),
            "artifacts": copy.deepcopy(self.artifacts),
            "messages": list(self.messages),
        }

    def summary_for_prompt(self, max_msgs: int = 20) -> str:
        lines = ["### Shared State"]
        if self.data:
            lines.append("Keys: " + ", ".join(f"{k}={repr(v)[:80]}" for k, v in self.data.items()))
        if self.artifacts:
            lines.append("Artifacts: " + ", ".join(self.artifacts.keys()))
        recent = self.messages[-max_msgs:]
        if recent:
            lines.append("Recent messages:")
            for m in recent:
                lines.append(f"  [{m['agent']}] {m['role']}: {m['content'][:200]}")
        return "\n".join(lines) if len(lines) > 1 else "### Shared State\n(empty)"
