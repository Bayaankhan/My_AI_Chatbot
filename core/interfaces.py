"""The only contracts the rest of the system depends on. Implement these to extend engbot."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterator, Protocol, runtime_checkable

Message = dict  # {"role": "system"|"user"|"assistant", "content": str}


@runtime_checkable
class LLMProvider(Protocol):
    def stream(self, messages: list[Message]) -> Iterator[str]:
        """Yield text chunks."""
        ...


class Tool(Protocol):
    name: str
    description: str          # shown to the model
    args_schema: dict         # {"arg": "description"}

    def run(self, **kwargs) -> str: ...


@dataclass
class Domain:
    """A subject area: system prompt + which tools it may use. Add chemistry, law, etc. the same way."""
    name: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)   # tool names; empty = all registered
