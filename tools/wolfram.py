"""Optional. Set WOLFRAM_APP_ID and enable in config.yaml plugins."""
import os, httpx
from engbot.core.registry import register_tool


class WolframTool:
    name = "wolfram"
    description = "Wolfram|Alpha short-answer API for facts, unit conversion, constants, tough integrals."
    args_schema = {"query": "natural-language query"}

    def run(self, query: str) -> str:
        r = httpx.get("https://api.wolframalpha.com/v1/result", timeout=30,
                      params={"appid": os.environ["WOLFRAM_APP_ID"], "i": query})
        return r.text


register_tool(WolframTool())
