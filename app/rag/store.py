import pathlib, chromadb

from .chunking import fixed_chunks, recursive_chunks

CLIENT = chromadb.PersistentClient(path="chroma_db")

STRATEGIES = {"fixed": fixed_chunks, "recursive": recursive_chunks}

def ingest(docs_dir = "data/docs", strategy="recursive"):
    col = CLIENT.get_or_create_collection(f"docs_{strategy}", metadata={"hnsw:space": "cosine"})
    ids, texts, metas = [], [], []
    root = pathlib.Path(docs_dir)
    for path in root.rglob("*.md"):
        rel = str(path.relative_to(root))
        access = "internal" if "internal" in path.parts else "public"
        for i,ch in enumerate(STRATEGIES[strategy](path.read_text(errors="ignore"))):
            ids.append(f"{rel}::{strategy}::{i}")
            texts.append(ch)
            metas.append({"source": rel, "chunk": i, "access": access})

    for s in range(0, len(ids), 100):
        col.add(ids=ids[s:s+100], documents=texts[s:s+100], metadatas=metas[s:s+100])
    return col.count()

def search(query, strategy="recursive", k=5, where=None):
    col = CLIENT.get_collection(f"docs_{strategy}")
    r = col.query(query_texts=[query], n_results=k, where=where)
    return [dict(id=i, text=d, meta=m, score=round(1-dist, 3)) for i,d,m,dist in zip(r["ids"][0], r["documents"][0], r["metadatas"][0], r["distances"][0])]


