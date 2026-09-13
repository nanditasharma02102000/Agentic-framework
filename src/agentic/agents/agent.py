from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Callable, List, Optional, Union
from agentic.core.types import (
    Message,
    Role,
    ToolCall,
    ToolResult,
    AgentEvent,
    AgentResult,
)
from agentic.core.registry import Tool, ToolRegistry
from agentic.providers.base import BaseProvider


class Agent:
    """
    Core ReAct-style agent with tool calling loop.
    Supports streaming events, max steps, system prompt, memory hooks.
    """

    def __init__(
        self,
        provider: BaseProvider,
        tools: Optional[List[Union[Tool, Any]]] = None,
        system_prompt: str = "You are a helpful autonomous agent. Use tools when needed to solve the user's request.",
        max_steps: int = 15,
        temperature: float = 0.0,
        on_event: Optional[Callable[[AgentEvent], None]] = None,
        name: str = "agent",
    ) -> None:
        self.name = name
        self.provider = provider
        self.system_prompt = system_prompt
        self.max_steps = max_steps
        self.temperature = temperature
        self.on_event = on_event
        self.registry = ToolRegistry()
        if tools:
            for t in tools:
                if isinstance(t, Tool):
                    self.registry.register(t)
                elif hasattr(t, "as_tool"):
                    self.registry.register(t.as_tool())
                elif hasattr(t, "as_tools"):
                    for tt in t.as_tools():
                        self.registry.register(tt)
                else:
                    raise TypeError(f"Unsupported tool type: {type(t)}")

    def _emit(self, event: AgentEvent) -> None:
        if self.on_event:
            self.on_event(event)

    async def run(
        self,
        user_input: str,
        history: Optional[List[Message]] = None,
    ) -> AgentResult:
        messages: List[Message] = []
        if self.system_prompt:
            messages.append(Message(role=Role.SYSTEM, content=self.system_prompt))
        if history:
            messages.extend(history)
        messages.append(Message(role=Role.USER, content=user_input))

        executed: List[ToolResult] = []
        events: List[AgentEvent] = []
        usage: dict = {}

        for step in range(self.max_steps):
            assistant_msg = await self.provider.chat(
                messages,
                tools=self.registry.list(),
                temperature=self.temperature,
            )
            messages.append(assistant_msg)
            evt = AgentEvent(type="message", data=assistant_msg)
            events.append(evt)
            self._emit(evt)

            if not assistant_msg.tool_calls:
                result = AgentResult(
                    final_message=assistant_msg,
                    messages=messages,
                    tool_calls_executed=executed,
                    usage=usage,
                    events=events,
                )
                self._emit(AgentEvent(type="done", data=result))
                return result

            tasks = [self.registry.execute(tc) for tc in assistant_msg.tool_calls]
            results = await asyncio.gather(*tasks)
            for tr in results:
                executed.append(tr)
                tool_msg = Message(
                    role=Role.TOOL,
                    content=tr.content,
                    tool_call_id=tr.tool_call_id,
                    name=tr.name,
                )
                messages.append(tool_msg)
                evt = AgentEvent(type="tool_result", data=tr)
                events.append(evt)
                self._emit(evt)

        final = Message(
            role=Role.ASSISTANT,
            content="Reached maximum tool-calling steps without a final answer.",
        )
        messages.append(final)
        return AgentResult(
            final_message=final,
            messages=messages,
            tool_calls_executed=executed,
            usage=usage,
            events=events,
        )

    async def stream(
        self,
        user_input: str,
        history: Optional[List[Message]] = None,
    ) -> AsyncIterator[AgentEvent]:
        """Streaming variant – yields AgentEvents."""
        result = await self.run(user_input, history=history)
        for e in result.events:
            yield e
        yield AgentEvent(type="done", data=result)
