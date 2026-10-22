"""Optional RAG over your own notes. Needs: pip install .[rag]
Index:  python -m engbot.retrieval.local_docs ./my_notes   (.txt/.md files)
The agent then gets a `search_docs` tool. Swap Chroma for pgvector/Qdrant by editing only this file."""
import pathlib, sys
from engbot.core.registry import register_tool

DB_PATH = "data/chroma"


def _col():
    import chromadb
    from chromadb.utils import embedding_functions as ef
    return chromadb.PersistentClient(DB_PATH).get_or_create_collection(
        "docs", embedding_function=ef.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2"))


def index(folder: str, size: int = 1200):
    col = _col()
    for p in pathlib.Path(folder).rglob("*"):
        if p.suffix.lower() in {".txt", ".md"}:
            t = p.read_text(errors="ignore")
            chunks = [t[i:i + size] for i in range(0, len(t), size)]
            if chunks:
                col.upsert(ids=[f"{p}:{i}" for i in range(len(chunks))], documents=chunks,
                           metadatas=[{"source": str(p)}] * len(chunks))


class LocalDocsTool:
    name = "search_docs"
    description = "Semantic search over the user's own indexed course notes and textbooks."
    args_schema = {"query": "what to look up", "n": "results (default 4)"}

    def run(self, query: str, n: int = 4) -> str:
        r = _col().query(query_texts=[query], n_results=int(n))
        return "\n\n".join(f"[{m['source']}]\n{d}" for d, m in zip(r["documents"][0], r["metadatas"][0]))


register_tool(LocalDocsTool())

if __name__ == "__main__":
    index(sys.argv[1])
