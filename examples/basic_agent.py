"""
Basic example: shell + file tools with any provider.
Set OPENAI_API_KEY or ANTHROPIC_API_KEY.
"""

import asyncio
import os
from agentic import Agent, OpenAIProvider, AnthropicProvider, LiteLLMProvider
from agentic.tools import ShellTool, FileTool, WebFetchTool


async def main():
    # Choose provider
    if os.getenv("OPENAI_API_KEY"):
        provider = OpenAIProvider(model="gpt-4o-mini")
    elif os.getenv("ANTHROPIC_API_KEY"):
        provider = AnthropicProvider(model="claude-sonnet-4-20250514")
    else:
        # fallback – will fail without key, but shows the API
        provider = LiteLLMProvider(model="gpt-4o-mini")

    shell = ShellTool(timeout=30)
    files = FileTool(root=".")
    web = WebFetchTool()

    agent = Agent(
        provider=provider,
        tools=[shell, files, web],
        system_prompt=(
            "You are a capable coding and research agent. "
            "You have shell, file, and web_fetch tools. "
            "Always prefer tools over guessing. Be concise."
        ),
        max_steps=8,
    )

    result = await agent.run(
        "List the files in the current directory, then read the README.md if it exists and summarize it in 3 bullet points."
    )
    print("=== Final Answer ===")
    print(result.final_message.content)
    print("\n=== Tools used ===")
    for tr in result.tool_calls_executed:
        print(f"- {tr.name}: {tr.content[:120]}...")


if __name__ == "__main__":
    asyncio.run(main())
