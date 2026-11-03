import re
from rank_bm25 import BM25Okapi
from .store import CLIENT, search
from sentence_transformers import CrossEncoder

_tok = lambda s: re.findall(r"\w+", s.lower())
_cache = {}
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def _bm25(strategy):
    if strategy not in _cache:
        col = CLIENT.get_collection(f"docs_{strategy}")
        data = col.get(include=["documents", "metadatas"])
        _cache[strategy] = (BM25Okapi([_tok(d) for d in data["documents"]]),
                            data["ids"], data["documents"], data["metadatas"])

    return _cache[strategy]

def keyword_search(query, strategy="recursive", k=20, allowed_access=None):
    bm25, ids, docs, metas = _bm25(strategy)

    scores = bm25.get_scores(_tok(query))
    order = sorted(range(len(ids)), key=lambda i: -scores[i])
    out = []
    for i in order:
        if allowed_access and metas[i]["access"] not in allowed_access:
            continue
        out.append(dict(id=ids[i], text=docs[i], meta = metas[i], score=float(scores[i])))
        if len(out) == k:
            break
    return out

def hybrid_search(query, strategy="recursive", k=5, allowed_access=None, pool=20):
    where = {"access": {"$in": list(allowed_access)}} if allowed_access else None
    sem = search(query, strategy, k=pool, where=where)
    kw = keyword_search(query, strategy, k=pool, allowed_access=allowed_access)
    fused, by_id = {}, {}
    for ranking in (sem, kw):
        for rank, h in enumerate(ranking):
            fused[h["id"]] = (
                fused.get(h["id"], 0) + 1 /(60 + rank)
            )
            by_id[h["id"]] = h
    top = sorted(fused, key=fused.get, reverse = True) [:k]
    # print("FUSED IDS:", list(fused.keys()))
    # print("BY_ID IDS:", list(by_id.keys()))
    # print("TOP IDS:", top)

    # missing = [i for i in top if i not in by_id]

    # print("MISSING IDS:", missing)
    return [dict(by_id[i], score=round(fused[i],4)) for i in top]

def rerank(query, chunks, k=5):
    pairs = [(query, chunk["text"]) for chunk in chunks]
    scores = reranker.predict(pairs)

    ranked=[]
    for chunk, score in zip(chunks, scores):
        ranked.append({
            **chunk,
            "rerank_score": float(score)
        })
    return sorted(ranked, key=lambda x: x["rerank_score"], reverse=True)[:k]

