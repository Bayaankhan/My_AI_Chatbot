"""Model-agnostic tool-using agent loop.

Tool calls use a plain-text protocol (a ```tool fenced JSON block) so ANY chat model works,
including ones without native function calling.
"""
from __future__ import annotations
import json, re
from typing import Iterator
from .interfaces import Domain, LLMProvider, Message
from .registry import TOOLS

TOOL_RE = re.compile(r"```tool\s*(\{.*?\})\s*```", re.S)

PROTOCOL = """
You can call tools. To call one, output EXACTLY one block and then stop writing:
```tool
{"name": "<tool_name>", "args": {"<arg>": "<value>"}}
```
You will receive the result, then continue. Use tools for exact arithmetic, symbolic math,
unit-sensitive numerics, and any claim needing a source. Never invent citations.
Available tools:
"""


def _tool_prompt(names: list[str]) -> str:
    lines = [f"- {n}: {TOOLS[n].description} args={json.dumps(TOOLS[n].args_schema)}" for n in names]
    return PROTOCOL + "\n".join(lines)


class Agent:
    def __init__(self, provider: LLMProvider, domain: Domain, max_steps: int = 6):
        self.provider, self.domain, self.max_steps = provider, domain, max_steps
        self.tool_names = [t for t in (domain.tools or TOOLS) if t in TOOLS]

    def run(self, history: list[Message], user_msg: str) -> Iterator[str]:
        """Yields the cumulative visible transcript so UIs can stream it."""
        system = self.domain.system_prompt + ("\n" + _tool_prompt(self.tool_names) if self.tool_names else "")
        msgs: list[Message] = [{"role": "system", "content": system}, *history,
                               {"role": "user", "content": user_msg}]
        shown = ""
        for _ in range(self.max_steps + 1):
            turn = ""
            for chunk in self.provider.stream(msgs):
                turn += chunk
                yield shown + turn
            m = TOOL_RE.search(turn)
            if not m:
                return
            shown += turn[: m.end()] + "\n\n"
            try:
                call = json.loads(m.group(1))
                result = TOOLS[call["name"]].run(**call.get("args", {}))
            except Exception as e:  # report errors to the model so it can recover
                result = f"TOOL ERROR: {type(e).__name__}: {e}"
            shown += f"> **Tool result**\n```\n{result[:3000]}\n```\n\n"
            yield shown
            msgs += [{"role": "assistant", "content": turn[: m.end()]},
                     {"role": "user", "content": f"Tool result:\n{result[:6000]}"}]
        yield shown + "\n_(stopped: tool step limit reached)_"
