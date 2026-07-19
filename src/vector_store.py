"""
Vector store layer with an automatic two-tier backend, mirroring embeddings.py:

1. ChromaStore (preferred): persistent Chroma collection (pip install chromadb).
   This is the production path named in the hackathon brief.

2. SimpleVectorStore (automatic fallback): a small numpy-backed cosine-similarity
   index persisted to disk as .npy + .json. Used automatically when chromadb
   is not installed / cannot be installed (as in this build's sandbox, which
   could not complete a chromadb install within the environment's constraints).

Both stores expose the same interface: add(ids, embeddings, metadatas, documents),
query(embedding, top_k) -> list of (id, score, metadata, document), and persist()/load().
"""
import os
import json
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


class SimpleVectorStore:
    backend_name = "numpy-cosine (local fallback store)"

    def __init__(self, persist_dir=DATA_DIR, collection_name="corpus"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.ids = []
        self.embeddings = None  # (n, dim) numpy array, rows L2-normalized
        self.metadatas = []
        self.documents = []

    def add(self, ids, embeddings, metadatas, documents):
        embeddings = np.asarray(embeddings, dtype=np.float64)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embeddings = embeddings / norms
        self.ids.extend(ids)
        self.metadatas.extend(metadatas)
        self.documents.extend(documents)
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

    def query(self, embedding, top_k=5):
        if self.embeddings is None or len(self.ids) == 0:
            return []
        # NOTE: the query vector is intentionally NOT renormalized to unit
        # length here. Documents are unit vectors (normalized in add()), so
        # the dot product below is cosine similarity scaled by the query
        # vector's own magnitude. For embedders that already emit unit
        # vectors (e.g. sentence-transformers), this is plain cosine
        # similarity as usual. For the local LSA embedder, a query's
        # magnitude reflects how much in-vocabulary signal it actually
        # contained -- renormalizing a near-empty/out-of-corpus query up to
        # unit length would amplify a single incidental token match into
        # spurious full-confidence similarity, which is exactly the
        # false-positive failure mode this design avoids.
        q = np.asarray(embedding, dtype=np.float64)
        scores = self.embeddings @ q
        top_idx = np.argsort(-scores)[:top_k]
        results = []
        for i in top_idx:
            results.append({
                "id": self.ids[i],
                "score": float(scores[i]),
                "metadata": self.metadatas[i],
                "document": self.documents[i],
            })
        return results

    def persist(self):
        np.save(os.path.join(self.persist_dir, f"{self.collection_name}_emb.npy"), self.embeddings)
        with open(os.path.join(self.persist_dir, f"{self.collection_name}_meta.json"), "w") as f:
            json.dump({
                "ids": self.ids,
                "metadatas": self.metadatas,
                "documents": self.documents,
            }, f)

    def load(self):
        emb_path = os.path.join(self.persist_dir, f"{self.collection_name}_emb.npy")
        meta_path = os.path.join(self.persist_dir, f"{self.collection_name}_meta.json")
        self.embeddings = np.load(emb_path)
        with open(meta_path, "r") as f:
            state = json.load(f)
        self.ids = state["ids"]
        self.metadatas = state["metadatas"]
        self.documents = state["documents"]
        return self

    def exists(self):
        return os.path.exists(os.path.join(self.persist_dir, f"{self.collection_name}_emb.npy"))


class ChromaStore:
    backend_name = "chromadb (persistent collection)"

    def __init__(self, persist_dir=DATA_DIR, collection_name="corpus"):
        import chromadb  # may raise ImportError
        self.client = chromadb.PersistentClient(path=os.path.join(persist_dir, "chroma"))
        self.collection = self.client.get_or_create_collection(collection_name)

    def add(self, ids, embeddings, metadatas, documents):
        self.collection.add(ids=ids, embeddings=[list(map(float, e)) for e in embeddings],
                             metadatas=metadatas, documents=documents)

    def query(self, embedding, top_k=5):
        res = self.collection.query(query_embeddings=[list(map(float, embedding))], n_results=top_k)
        results = []
        for i in range(len(res["ids"][0])):
            # chroma returns squared-L2 distance by default; convert to a similarity-like score
            dist = res["distances"][0][i]
            score = 1.0 / (1.0 + dist)
            results.append({
                "id": res["ids"][0][i],
                "score": score,
                "metadata": res["metadatas"][0][i],
                "document": res["documents"][0][i],
            })
        return results

    def persist(self):
        pass  # PersistentClient writes through automatically

    def load(self):
        return self

    def exists(self):
        return self.collection.count() > 0


def get_store(prefer="auto", persist_dir=DATA_DIR, collection_name="corpus"):
    if prefer in ("auto", "chroma"):
        try:
            store = ChromaStore(persist_dir=persist_dir, collection_name=collection_name)
            print(f"[vector_store] using {store.backend_name}")
            return store
        except Exception as e:
            if prefer == "chroma":
                raise
            print(f"[vector_store] chromadb unavailable ({type(e).__name__}: {e}); "
                  f"falling back to local numpy vector store.")
    store = SimpleVectorStore(persist_dir=persist_dir, collection_name=collection_name)
    print(f"[vector_store] using {store.backend_name}")
    return store
