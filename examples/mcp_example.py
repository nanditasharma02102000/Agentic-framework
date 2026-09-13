"""
Example: expose local tools as MCP server, or connect as client.
"""

import asyncio
from agentic.tools import ShellTool, FileTool
from agentic.mcp.server import create_mcp_server_from_tools
from agentic.core.registry import ToolRegistry


async def run_server():
    registry = ToolRegistry()
    registry.register(ShellTool().as_tool())
    for t in FileTool().as_tools():
        registry.register(t)

    server = create_mcp_server_from_tools(registry, name="agentic-local-tools")
    print("MCP server created. Run with: python -m mcp run ... or server.run()")
    # In real use:
    # server.run(transport="stdio")


if __name__ == "__main__":
    asyncio.run(run_server())
