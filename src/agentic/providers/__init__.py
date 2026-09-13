from agentic.providers.base import BaseProvider

def __getattr__(name: str):
    if name == "OpenAIProvider":
        from agentic.providers.openai import OpenAIProvider
        return OpenAIProvider
    if name == "AnthropicProvider":
        from agentic.providers.anthropic import AnthropicProvider
        return AnthropicProvider
    if name == "LiteLLMProvider":
        from agentic.providers.litellm_provider import LiteLLMProvider
        return LiteLLMProvider
    raise AttributeError(name)

__all__ = ["BaseProvider", "OpenAIProvider", "AnthropicProvider", "LiteLLMProvider"]
