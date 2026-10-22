"""Tiny plugin registry. Plugins are plain modules that call register_* at import time."""
from __future__ import annotations
import importlib
from typing import Callable
from .interfaces import Domain, Tool

TOOLS: dict[str, Tool] = {}
DOMAINS: dict[str, Domain] = {}
PROVIDERS: dict[str, Callable] = {}   # type name -> factory(config_dict) -> LLMProvider


def register_tool(tool: Tool) -> Tool:
    TOOLS[tool.name] = tool
    return tool


def register_domain(domain: Domain) -> Domain:
    DOMAINS[domain.name] = domain
    return domain


def register_provider(type_name: str):
    def deco(factory):
        PROVIDERS[type_name] = factory
        return factory
    return deco


def load_plugins(modules: list[str]) -> None:
    for m in modules:
        importlib.import_module(m)
