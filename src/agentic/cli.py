from __future__ import annotations

import asyncio
import os
from typing import Optional
import typer
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer(help="Agentic Framework CLI")
console = Console()


@app.command()
def chat(
    prompt: str = typer.Argument(..., help="User prompt"),
    model: str = typer.Option("gpt-4o-mini", help="Model name"),
    provider: str = typer.Option("openai", help="openai | anthropic | litellm"),
    max_steps: int = typer.Option(10, help="Max tool steps"),
):
    """Run a one-shot agent with shell + file + web tools."""
    asyncio.run(_chat(prompt, model, provider, max_steps))


async def _chat(prompt: str, model: str, provider_name: str, max_steps: int):
    from agentic import Agent, OpenAIProvider, AnthropicProvider, LiteLLMProvider
    from agentic.tools import ShellTool, FileTool, WebFetchTool, WebSearchTool

    if provider_name == "openai":
        prov = OpenAIProvider(model=model)
    elif provider_name == "anthropic":
        prov = AnthropicProvider(model=model)
    else:
        prov = LiteLLMProvider(model=model)

    agent = Agent(
        provider=prov,
        tools=[ShellTool(), FileTool(), WebFetchTool(), WebSearchTool()],
        max_steps=max_steps,
    )

    def on_event(e):
        if e.type == "tool_result":
            console.print(f"[yellow]Tool {e.data.name}[/yellow]: {str(e.data.content)[:200]}...")
        elif e.type == "message" and e.data.content:
            console.print(f"[cyan]Assistant[/cyan]: {e.data.content[:300]}")

    agent.on_event = on_event
    result = await agent.run(prompt)
    console.print("\n[bold green]Final:[/bold green]")
    console.print(Markdown(result.final_message.content or "(no content)"))


@app.command()
def version():
    from agentic import __version__
    console.print(f"agentic-framework {__version__}")


if __name__ == "__main__":
    app()
