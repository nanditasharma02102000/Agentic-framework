from __future__ import annotations

import asyncio
import os
import shlex
from typing import Optional
from agentic.core.registry import Tool, tool


class ShellTool:
    """Safe-ish shell execution tool."""

    def __init__(
        self,
        cwd: Optional[str] = None,
        timeout: float = 60.0,
        allowed_commands: Optional[list[str]] = None,
        env: Optional[dict] = None,
    ) -> None:
        self.cwd = cwd or os.getcwd()
        self.timeout = timeout
        self.allowed_commands = allowed_commands
        self.env = env or os.environ.copy()

    def as_tool(self) -> Tool:
        @tool(
            name="shell",
            description=(
                "Execute a shell command and return stdout + stderr. "
                "Use for listing files, running scripts, system info, etc. "
                "Prefer non-interactive commands. Timeout applies."
            ),
        )
        async def shell(command: str, working_directory: Optional[str] = None) -> str:
            return await self.run(command, cwd=working_directory)

        return shell

    async def run(self, command: str, cwd: Optional[str] = None) -> str:
        if self.allowed_commands:
            parts = shlex.split(command)
            if not parts or parts[0] not in self.allowed_commands:
                return f"Error: command '{parts[0] if parts else command}' not allowed"

        workdir = cwd or self.cwd
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workdir,
                env=self.env,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                return f"Error: command timed out after {self.timeout}s"
            out = stdout.decode(errors="replace").strip()
            err = stderr.decode(errors="replace").strip()
            code = proc.returncode
            result = f"exit_code={code}\n"
            if out:
                result += f"stdout:\n{out}\n"
            if err:
                result += f"stderr:\n{err}\n"
            return result
        except Exception as e:
            return f"Error executing shell: {e}"
