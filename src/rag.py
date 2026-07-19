"""
Provenance — main RAG pipeline CLI.

Usage:
    python3 src/rag.py build                 # ingest + embed + index the corpus
    python3 src/rag.py ask "some question"   # retrieve + generate a cited answer
    python3 src/rag.py demo                  # run the fixed demo query set

See README.md for the embedding/vector-store backend selection logic.
"""
import sys
import os
import json
import pickle

sys.path.insert(0, os.path.dirname(__file__))

from chunking import load_corpus
from embeddings import get_embedder, LocalLSAEmbedder, TransformerEmbedder
from vector_store import get_store
from generate import get_generator, answer_query, SIM_THRESHOLD

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EMBEDDER_STATE_PATH = os.path.join(DATA_DIR, "embedder_state.pkl")
EMBEDDER_KIND_PATH = os.path.join(DATA_DIR, "embedder_kind.json")


def build_index(embedder_prefer="auto", store_prefer="auto", top_k_default=5):
    docs, chunks = load_corpus()
    print(f"[build] {len(docs)} documents -> {len(chunks)} chunks")

    embedder = get_embedder(prefer=embedder_prefer)
    texts = [c["text"] for c in chunks]
    embeddings = embedder.fit(texts)

    store = get_store(prefer=store_prefer)
    ids = [f"{c['doc_file']}::p{c['page']}::{c['sub_chunk']}" for c in chunks]
    metadatas = [{k: v for k, v in c.items() if k != "text"} for c in chunks]
    store.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=texts)
    store.persist()

    os.makedirs(DATA_DIR, exist_ok=True)
    kind = "lsa" if isinstance(embedder, LocalLSAEmbedder) else "transformer"
    with open(EMBEDDER_KIND_PATH, "w") as f:
        json.dump({"kind": kind}, f)
    if kind == "lsa":
        embedder.save(EMBEDDER_STATE_PATH)

    print(f"[build] index persisted to {DATA_DIR}")
    return embedder, store


def load_pipeline(embedder_prefer="auto", store_prefer="auto"):
    with open(EMBEDDER_KIND_PATH, "r") as f:
        kind = json.load(f)["kind"]
    if kind == "lsa":
        embedder = LocalLSAEmbedder.load(EMBEDDER_STATE_PATH)
    else:
        embedder = TransformerEmbedder()
    store = get_store(prefer=store_prefer)
    store.load()
    return embedder, store


def ask(query, embedder, store, generator, top_k=5, threshold=SIM_THRESHOLD, verbose=True):
    q_emb = embedder.embed_one(query)
    retrieved = store.query(q_emb, top_k=top_k)
    result = answer_query(query, retrieved, generator, threshold=threshold)
    if verbose:
        print(f"\nQ: {query}")
        print(f"   top retrieval score: {result['top_score']}")
        if result["refused"]:
            print(f"A: {result['answer']}")
        else:
            print(f"A: {result['answer']}")
            print(f"   Sources: {result['citations']}")
    return result, retrieved


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "build":
        build_index()
    elif cmd == "ask":
        query = " ".join(sys.argv[2:])
        embedder, store = load_pipeline()
        generator = get_generator()
        ask(query, embedder, store, generator)
    else:
        print(__doc__)
