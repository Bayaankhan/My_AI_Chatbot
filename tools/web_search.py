import re, httpx
from engbot.core.registry import register_tool


class WebSearchTool:
    name = "web_search"
    description = "Search the web (DuckDuckGo). Returns titles, URLs, snippets."
    args_schema = {"query": "search string", "n": "number of results (default 5)"}

    def run(self, query: str, n: int = 5) -> str:
        from duckduckgo_search import DDGS
        rows = DDGS().text(query, max_results=int(n))
        return "\n".join(f"- {r['title']} | {r['href']}\n  {r['body']}" for r in rows) or "No results"


class FetchPageTool:
    name = "fetch_page"
    description = "Download a web page and return its plain text (first ~6000 chars)."
    args_schema = {"url": "http(s) URL"}

    def run(self, url: str) -> str:
        html = httpx.get(url, timeout=20, follow_redirects=True, headers={"User-Agent": "engbot/0.1"}).text
        html = re.sub(r"(?s)<(script|style).*?</\1>", " ", html)
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))[:6000]


register_tool(WebSearchTool())
register_tool(FetchPageTool())
