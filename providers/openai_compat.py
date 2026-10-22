"""One provider for every OpenAI-compatible server: Ollama, vLLM, llama.cpp, LM Studio, TGI, hosted APIs."""
import json
import httpx
from engbot.core.registry import register_provider


class OpenAICompatProvider:
    def __init__(self, base_url, model, api_key="x", temperature=0.2, max_tokens=4096, **_):
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.body = dict(model=model, temperature=temperature, max_tokens=max_tokens, stream=True)

    def stream(self, messages):
        with httpx.stream("POST", self.url, headers=self.headers, timeout=None,
                          json={**self.body, "messages": messages}) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                delta = json.loads(data)["choices"][0].get("delta", {})
                if delta.get("content"):
                    yield delta["content"]


@register_provider("openai_compat")
def _factory(cfg):
    return OpenAICompatProvider(**cfg)
