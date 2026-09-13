# Architecture

## Layers

1. **Providers** – abstract LLM interface (`BaseProvider`). Implementations:
   - `OpenAIProvider`
   - `AnthropicProvider`
   - `LiteLLMProvider` (100+ models)

2. **Tools & Registry** – `Tool` + `ToolRegistry`. Tools can be:
   - Decorated pure functions (`@tool`)
   - Classes that expose `.as_tool()` / `.as_tools()`
   - Remote tools via MCP client

3. **Agent Loop** – classic ReAct / tool-calling loop:
   - System + history + user → LLM
   - If tool_calls → execute (parallel) → append tool results → repeat
   - Until final text answer or max_steps

4. **MCP**
   - Client: connect to any MCP server and import its tools into a `ToolRegistry`
   - Server: expose a local `ToolRegistry` as an MCP server (stdio / HTTP)

5. **Browser / Computer**
   - Browser: Playwright session with navigate / click / type / extract / screenshot / eval
   - Computer: xdotool + screenshot primitives (Linux/X11). For production pair with a real computer-use runtime.

6. **Memory** – simple conversation window + KV store. Easy to swap for vector DB / Mem0 / etc.

## Extension points

- Add a new provider by subclassing `BaseProvider`
- Add tools by implementing `as_tool(s)` or using the `@tool` decorator
- Hook events with `on_event` callback
- Multi-agent: create multiple `Agent` instances and share a registry / memory

## Security notes

- Shell and File tools accept optional allow-lists / root sandboxes
- Always run untrusted agents in containers or remote sandboxes
- MCP servers should be authenticated in production

## Multi-Agent Orchestration

Four built-in patterns share the same `SharedState` blackboard and event stream.

### 1. SequentialPipeline
Agents run in a fixed order. Output of N becomes input of N+1.
```python
pipeline = SequentialPipeline(
    agents={"researcher": r, "writer": w, "critic": c},
    order=["researcher", "writer", "critic"],
)
result = await pipeline.run("...")
```

### 2. ConcurrentTeam
All specialists run in parallel; optional synthesizer merges results.
```python
team = ConcurrentTeam(agents={...}, synthesizer=synth)
result = await team.run("...", per_agent_prompts={...})
```

### 3. SupervisorOrchestrator
A supervisor LLM decides which worker to call via the `handoff` tool, sees results, and can re-plan until it emits a final answer.
```python
orch = SupervisorOrchestrator(supervisor=sup, workers={"coder": c, "researcher": r})
result = await orch.run("...")
```

### 4. HandoffOrchestrator
Peer-to-peer. Any agent can call `handoff(target_agent, reason, context)`. Control transfers until someone finishes without handoff (or max hops).
```python
orch = HandoffOrchestrator(agents={...}, entry_agent="triage")
result = await orch.run("...")
```

### SharedState
Blackboard with `get/set`, message log, and artifacts. Automatically injected into prompts as context.
