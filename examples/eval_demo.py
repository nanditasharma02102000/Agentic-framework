"""Run eval harness against a deterministic mock-free smoke path (structure only without API key)."""

from __future__ import annotations

import asyncio
from agentic.eval import EvalCase, EvalHarness, contains_all, tool_called, composite_scorer
from agentic.core.types import Message, Role, AgentResult, ToolResult


class FakeAgent:
    """Stand-in agent for offline eval demo."""

    async def run(self, user_input: str) -> AgentResult:
        if "pong" in user_input.lower():
            msg = Message(role=Role.ASSISTANT, content="pong")
            return AgentResult(final_message=msg, messages=[msg])
        msg = Message(role=Role.ASSISTANT, content="file README.md\ndir src")
        tools = [
            ToolResult(tool_call_id="1", name="list_dir", content="file README.md\ndir src")
        ]
        return AgentResult(final_message=msg, messages=[msg], tool_calls_executed=tools)


async def main():
    cases = [
        EvalCase(id="identity", input="Reply with exactly: pong", expected="pong"),
        EvalCase(
            id="tool-list",
            input="List files",
            expected="file|dir",
            expected_tools=["list_dir"],
        ),
    ]
    harness = EvalHarness(
        name="smoke",
        scorer=composite_scorer(contains_all, tool_called, weights=[0.6, 0.4]),
        success_threshold=0.5,
    )
    report = await harness.run(FakeAgent(), cases)
    print(report.summary())
    for r in report.results:
        print(f"  {r.case_id}: success={r.success} score={r.score:.2f} tools={r.tools_used}")
    report.to_json("/tmp/eval_report.json")
    print("Wrote /tmp/eval_report.json")


if __name__ == "__main__":
    asyncio.run(main())
