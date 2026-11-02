from app.rag.store import ingest, search

for s in ["fixed", "recursive"]:
    print(s, "chunks: ", ingest(strategy=s))
    open("outputs/w04_search.md", "a").write(f"{s} chunks: {ingest(strategy=s)}\n")
queries = [
    "How do I validate data with a custom validator?",
    "How can Pydantic validate multiple fields?",
    "What happens when incoming data has an invalid schema?",
    "How long does a refund take?",
    "How do I handle failed records in an ingestion pipeline?"
]
for s in ["fixed", "recursive"]:
    print(f"\n=== {s} ===")
    open("outputs/w04_search.md", "a").write(f"\n=== {s} ===\n")
    for q in queries:
        print(f"\nQuery: {q}")
        
        open("outputs/w04_search.md", "a").write(f"\nQuery: {q}\n")
        print()
        for h in search(q, k =5, strategy=s):
            open("outputs/w04_search.md", "a").write(f"{h['score']} {h['meta']['source']} | {h['text'][:100].replace('\n', ' ')}\n")
            print(h["score"], h["meta"]["source"], "|", h["text"][:100].replace("\n", " "))

        print("\n=== with metadata filter (public only) ===")
        open("outputs/w04_search.md", "a").write(f"\n=== with metadata filter (public only) ===\n")
        for h in search(q, k=3, strategy=s, where={"access": "public"}):
            open("outputs/w04_search.md", "a").write(f"{h['score']} {h['meta']['source']} | {h['text'][:100].replace('\n', ' ')}\n")
            print(h["score"], h["meta"]["source"], "|", h["text"][:100].replace("\n", " "))

