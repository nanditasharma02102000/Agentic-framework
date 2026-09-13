# Agentic Framework

**Full-featured open agentic AI framework** with:

- Multi-provider LLMs (OpenAI, Anthropic, LiteLLM, local via Ollama, etc.)
- Native tool calling + custom tools
- Shell execution + safe file read/write
- Browser automation (Playwright + optional browser-use)
- Computer-use primitives (screenshot, click, type, scroll)
- Full **MCP** (Model Context Protocol) client & server support
- ReAct / tool-loop agents, multi-agent orchestration hooks
- Memory (short-term + simple persistent)
- Streaming, retries, observability hooks
- CLI + Python API

## Quick Start

```bash
pip install -e ".[all]"
playwright install chromium   # for browser tools
```

```python
from agentic import Agent, OpenAIProvider
from agentic.tools import ShellTool, FileTool, BrowserTool

agent = Agent(
    provider=OpenAIProvider(model="gpt-4o"),
    tools=[ShellTool(), FileTool(), BrowserTool()],
    system_prompt="You are a capable autonomous agent with shell, files, and browser access.",
)

result = await agent.run("List files in the current directory, then open https://example.com and summarize the title.")
print(result)
```

## Architecture

```
agentic/
├── core/          # Agent loop, messages, tool registry, events
├── providers/     # LLM providers (OpenAI, Anthropic, LiteLLM wrapper)
├── tools/         # Built-in tools (shell, file, browser, computer, web)
├── mcp/           # MCP client + server adapters
├── browser/       # Playwright / browser-use integration
├── computer/      # Screenshot + action primitives
├── memory/        # Conversation + simple vector-ish store
└── agents/        # High-level Agent, MultiAgent, etc.
```

## Features Status

| Feature              | Status          | Notes                                      |
|----------------------|-----------------|--------------------------------------------|
| Tool calling         | ✅ Full         | OpenAI/Anthropic style + custom            |
| Shell / FS           | ✅ Full         | Sandboxed options, timeout, cwd            |
| Browser              | ✅ Core         | Playwright; browser-use optional           |
| Computer use         | ✅ Primitives   | Screenshot, mouse, keyboard (Linux/X11)    |
| MCP Client           | ✅              | Connect to any MCP server (stdio/SSE/HTTP) |
| MCP Server           | ✅              | Expose your tools as MCP server            |
| Multi-provider       | ✅              | LiteLLM + native clients                   |
| Streaming            | ✅              | Token + tool events                        |
| Memory               | ✅ Basic        | Conversation + simple key-value            |
| Multi-agent          | ✅ Full         | Sequential, Concurrent, Supervisor, Handoff |

## MCP Example

```python
from agentic.mcp import MCPClient

async with MCPClient("stdio://npx -y @modelcontextprotocol/server-filesystem /tmp") as client:
    tools = await client.list_tools()
    result = await client.call_tool("read_file", {"path": "/tmp/hello.txt"})
```

## Multi-Agent

```python
from agentic import SequentialPipeline, ConcurrentTeam, SupervisorOrchestrator, HandoffOrchestrator

# Sequential: researcher → writer → critic
pipeline = SequentialPipeline(agents={...}, order=["researcher", "writer", "critic"])
result = await pipeline.run("...")

# Concurrent specialists + synthesizer
team = ConcurrentTeam(agents={...}, synthesizer=synth)

# Supervisor routes to workers via handoff tool
orch = SupervisorOrchestrator(supervisor=sup, workers={...})

# Peer-to-peer handoffs
orch = HandoffOrchestrator(agents={...}, entry_agent="triage")
```

See `examples/multi_agent.py` for full demos.

## License

MIT
