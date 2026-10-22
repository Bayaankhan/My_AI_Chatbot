import argparse, yaml
import gradio as gr
from engbot.core import registry
from engbot.core.agent import Agent
import engbot.providers.openai_compat  # noqa: register built-in provider


def build(cfg_path="config.yaml"):
    cfg = yaml.safe_load(open(cfg_path))
    registry.load_plugins(cfg.get("plugins", []))
    pcfg = dict(cfg["provider"])
    provider = registry.PROVIDERS[pcfg.pop("type")](pcfg)

    def chat(message, history, domain_name):
        agent = Agent(provider, registry.DOMAINS[domain_name], cfg["agent"]["max_tool_steps"])
        past = [{"role": h["role"], "content": h["content"]} for h in history]
        yield from agent.run(past, message)

    demo = gr.ChatInterface(
        chat , title="My AI Assistant",
        additional_inputs=[gr.Dropdown(list(registry.DOMAINS), value=cfg["domain"], label="Subject module")],
    )
    return demo, cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    a = ap.parse_args()
    demo, cfg = build(a.config)
    demo.launch(server_name=cfg["ui"]["host"], server_port=cfg["ui"]["port"])


if __name__ == "__main__":
    main()
