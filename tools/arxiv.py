import xml.etree.ElementTree as ET
import httpx
from engbot.core.registry import register_tool

NS = {"a": "http://www.w3.org/2005/Atom"}


class ArxivTool:
    name = "arxiv_search"
    description = "Search arXiv for papers. Returns title, authors, date, link, abstract excerpt."
    args_schema = {"query": "arXiv query, e.g. 'all:heat exchanger optimization'", "n": "max results (default 5)"}

    def run(self, query: str, n: int = 5) -> str:
        r = httpx.get("https://export.arxiv.org/api/query", timeout=30,
                      params={"search_query": query, "max_results": int(n), "sortBy": "relevance"})
        out = []
        for e in ET.fromstring(r.text).findall("a:entry", NS):
            g = lambda t: " ".join((e.findtext(f"a:{t}", "", NS) or "").split())
            authors = ", ".join(a.findtext("a:name", "", NS) for a in e.findall("a:author", NS)[:4])
            out.append(f"- {g('title')} ({g('published')[:10]}) - {authors}\n  {g('id')}\n  {g('summary')[:350]}...")
        return "\n".join(out) or "No results"


register_tool(ArxivTool())
