import numpy as np
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

docs = ["Refund policy: customers may send back purchases within 30 days.",
        "Our office is open Monday to Friday, 9 to 5.",
        "Shipping takes 3-5 business days.",
        "To reset your password, click 'Forgot password' on the login page."]
queries = ["How do I return an item?", "I can't log in", "When will my order arrive?", "When will the refund get processed"]

docs = [
    "Error E-4471: Payment gateway timeout.",
    "Customers can return purchased products within 30 days.",
    "Shipping usually takes 3 business days."
]

queries = [
    "E-4471",
    "How can I send back my purchase?",
    "Where is my parcel?"
]

ef = DefaultEmbeddingFunction()
D = np.array(ef(docs))
Q = np.array(ef(queries))

print("embedding shape: ", D.shape)
print("query embedding shape: ", Q.shape)

def cos(a,b): return a@b.T/ (np.linalg.norm(a, axis=1)[:, None] * np.linalg.norm(b, axis=1)[None, :])

tfidf = TfidfVectorizer().fit(docs + queries)

for i, q in enumerate(queries):
    sem = cos(Q[i:i+1], D)[0]
    kw = cosine_similarity(tfidf.transform([q]), tfidf.transform(docs))[0]
    print(f"\n{q}\n  semantic best: {docs[sem.argmax()][:45]!r} ({sem.max():.2f})\n  keyword  best: {docs[kw.argmax()][:45]!r} ({kw.max():.2f})")
