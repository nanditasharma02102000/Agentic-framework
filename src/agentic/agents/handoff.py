from __future__ import annotations

from typing import Any, Dict, List, Optional
from agentic.core.registry import Tool, tool
from agentic.core.types import Message, Role


def make_handoff_tool(
    target_agents: Dict[str, str],
    description: Optional[str] = None,
) -> Tool:
    """
    Create a `handoff` tool that an agent can call to transfer control.

    target_agents: {agent_name: short description}
    When called, the tool returns a structured handoff signal that the
    orchestrator intercepts (it does not execute another LLM call itself).
    """
    names = list(target_agents.keys())
    desc_lines = [f"- {n}: {d}" for n, d in target_agents.items()]
    full_desc = description or (
        "Transfer the current task to another specialist agent. "
        "Choose the best agent for the remaining work.\n"
        "Available agents:\n" + "\n".join(desc_lines)
    )

    @tool(name="handoff", description=full_desc)
    def handoff(target_agent: str, reason: str, context: str = "") -> str:
        """
        target_agent: name of the agent to hand off to
        reason: why this agent is better suited
        context: optional extra context to pass along
        """
        if target_agent not in names:
            return f"Error: unknown agent '{target_agent}'. Valid: {names}"
        return (
            f"__HANDOFF__\n"
            f"target={target_agent}\n"
            f"reason={reason}\n"
            f"context={context}"
        )

    return handoff


def parse_handoff(content: str) -> Optional[Dict[str, str]]:
    """Parse tool result or message content for a handoff signal."""
    if not content or "__HANDOFF__" not in content:
        return None
    result: Dict[str, str] = {}
    for line in content.splitlines():
        if line.startswith("target="):
            result["target"] = line[len("target=") :]
        elif line.startswith("reason="):
            result["reason"] = line[len("reason=") :]
        elif line.startswith("context="):
            result["context"] = line[len("context=") :]
    if "target" in result:
        return result
    return None
