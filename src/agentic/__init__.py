"""Agentic Framework – full agentic AI runtime."""

from agentic.core.types import Message, Role, ToolCall, ToolResult, AgentEvent, AgentResult
from agentic.core.registry import Tool, ToolRegistry, tool

def __getattr__(name: str):
    # Core agent
    if name == "Agent":
        from agentic.agents.agent import Agent
        return Agent
    # Multi-agent
    if name in (
        "SharedState", "SequentialPipeline", "ConcurrentTeam",
        "SupervisorOrchestrator", "HandoffOrchestrator", "MultiAgentResult",
        "OrchestrationPattern", "make_handoff_tool",
    ):
        from agentic import agents as _agents
        return getattr(_agents, name)
    # Providers
    if name == "BaseProvider":
        from agentic.providers.base import BaseProvider
        return BaseProvider
    if name == "OpenAIProvider":
        from agentic.providers.openai import OpenAIProvider
        return OpenAIProvider
    if name == "AnthropicProvider":
        from agentic.providers.anthropic import AnthropicProvider
        return AnthropicProvider
    if name == "LiteLLMProvider":
        from agentic.providers.litellm_provider import LiteLLMProvider
        return LiteLLMProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__version__ = "0.1.0"
__all__ = [
    "Message", "Role", "ToolCall", "ToolResult", "AgentEvent", "AgentResult",
    "Tool", "ToolRegistry", "tool",
    "Agent",
    "SharedState", "SequentialPipeline", "ConcurrentTeam",
    "SupervisorOrchestrator", "HandoffOrchestrator", "MultiAgentResult",
    "OrchestrationPattern", "make_handoff_tool",
    "BaseProvider", "OpenAIProvider", "AnthropicProvider", "LiteLLMProvider",
]
