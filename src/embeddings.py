"""
Embedding layer with an automatic two-tier backend:

1. TransformerEmbedder (preferred): sentence-transformers/all-MiniLM-L6-v2,
   a widely used open-source sentence-embedding model (384-dim). This is the
   production path and is what should be used whenever the machine running
   this code has normal internet access (it downloads the model once from
   Hugging Face and caches it locally).

2. LocalLSAEmbedder (automatic fallback): a dependency-free Latent Semantic
   Analysis embedder built from scratch with numpy only (TF-IDF -> truncated
   SVD via numpy.linalg.svd). It requires no model download and no external
   service, so the system still runs end-to-end in network-restricted
   environments. LSA is a genuine dense-vector embedding technique (it is
   the classical example of embedding-based semantic retrieval, predating
   neural sentence embeddings) -- ranking is done by cosine similarity in a
   reduced latent-topic space, not by keyword/BM25 term overlap, so it still
   satisfies "embedding-based, not keyword-only" retrieval.

get_embedder() tries (1) and transparently falls back to (2), printing which
backend is active. This project was built and demoed with backend (2)
because the sandboxed build environment could not reach huggingface.co;
switching to backend (1) on a normal machine requires no code changes.
"""
import os
import re
import json
import math
import pickle
import numpy as np

STOPWORDS = set("""
a an the of and or in on at to for with by from as is are was were be been
being this that these those it its it's their his her our your my we you i
he she they them us not no nor so than then too very can will would should
could may might must shall do does did doing have has had having a's about
above after again against all am any because before below between both
but down during each few further here how into itself more most other out
over own same some such under until up while who whom why
""".split())

TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


def tokenize(text, bigrams=False):
    unigrams = [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS and len(t) > 1]
    if not bigrams:
        return unigrams
    # Optional: bigrams can help distinctive two-word phrases, but empirically
    # (see README) they hurt recall more than they help on this corpus because
    # they require exact adjacent-word matches between query phrasing and
    # source text. Left available but off by default.
    bigram_tokens = [f"{a}_{b}" for a, b in zip(unigrams, unigrams[1:])]
    return unigrams + bigram_tokens


class LocalLSAEmbedder:
    """Pure-numpy TF-IDF -> truncated SVD (LSA) embedder. No downloads required."""

    name = "local-lsa-tfidf-svd"

    def __init__(self, n_components=40, min_df=1, max_df_ratio=0.15):
        self.n_components = n_components
        self.min_df = min_df
        self.max_df_ratio = max_df_ratio
        self.vocab = {}
        self.idf = None
        self.V_k = None  # (vocab, k) projection matrix
        self.fitted = False

    def fit(self, texts):
        # Build vocabulary + document frequencies
        doc_token_sets = [set(tokenize(t)) for t in texts]
        df = {}
        for toks in doc_token_sets:
            for t in toks:
                df[t] = df.get(t, 0) + 1
        n_docs = len(texts)
        max_df = int(self.max_df_ratio * n_docs)
        # min_df=1 keeps rare terms: in this corpus, a fact that appears in
        # only one chunk (e.g. a specific incident or product name) is
        # exactly the discriminative signal retrieval depends on, so it must
        # not be dropped. max_df instead strips near-universal boilerplate
        # terms shared by every document's template phrasing (e.g. "Company",
        # "fiscal", "audited statements") so the embedding space is driven by
        # discriminative content rather than shared report scaffolding --
        # without this, every chunk looks spuriously similar to every other.
        vocab_terms = sorted(t for t, d in df.items() if self.min_df <= d <= max_df)
        self.vocab = {term: i for i, term in enumerate(vocab_terms)}
        n_docs = len(texts)
        idf = np.zeros(len(vocab_terms), dtype=np.float64)
        for term, i in self.vocab.items():
            idf[i] = math.log((1 + n_docs) / (1 + df[term])) + 1.0
        self.idf = idf

        tf_matrix = self._tf_matrix(texts)
        tfidf = tf_matrix * self.idf[np.newaxis, :]
        # L2-normalize rows before SVD (standard for text LSA)
        norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        tfidf_norm = tfidf / norms

        k = min(self.n_components, min(tfidf_norm.shape) - 1)
        k = max(k, 2)
        U, S, Vt = np.linalg.svd(tfidf_norm, full_matrices=False)
        self.V_k = Vt[:k, :].T  # (vocab, k)
        self.k = k
        self.fitted = True

        # Deliberately NOT L2-renormalized: document/query vector magnitude in
        # this latent space reflects how much real vocabulary signal the text
        # contained. Renormalizing a near-empty (mostly out-of-vocabulary)
        # query up to unit length would let one incidental token match get
        # amplified into spurious full-confidence similarity -- exactly the
        # false-positive failure mode observed during testing (e.g. "capital
        # of France" scoring high against a "capital ratio" chunk). Leaving
        # magnitude intact means weak/OOV queries naturally produce small
        # dot products against every document, so they correctly fall below
        # the refusal threshold instead of being rescaled into false
        # confidence. Documents are unit-normalized at vector-store index
        # time (see vector_store.SimpleVectorStore.add), so retrieval score
        # is effectively cosine-similarity scaled by query signal strength.
        embeddings = tfidf_norm @ self.V_k
        return embeddings

    def _tf_matrix(self, texts):
        n = len(texts)
        v = len(self.vocab)
        mat = np.zeros((n, v), dtype=np.float64)
        for row, text in enumerate(texts):
            toks = tokenize(text)
            if not toks:
                continue
            counts = {}
            for t in toks:
                if t in self.vocab:
                    counts[t] = counts.get(t, 0) + 1
            max_count = max(counts.values()) if counts else 1
            for t, cnt in counts.items():
                # sublinear tf scaling (1 + log(count)) normalized by max term freq
                mat[row, self.vocab[t]] = (1 + math.log(cnt)) / (1 + math.log(max_count))
        return mat

    @staticmethod
    def _normalize(mat):
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return mat / norms

    def embed(self, texts):
        if not self.fitted:
            raise RuntimeError("LocalLSAEmbedder must be fit() before embed().")
        tf_matrix = self._tf_matrix(texts)
        tfidf = tf_matrix * self.idf[np.newaxis, :]
        norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        tfidf_norm = tfidf / norms
        embeddings = tfidf_norm @ self.V_k
        return embeddings

    def embed_one(self, text):
        return self.embed([text])[0]

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump({
                "vocab": self.vocab, "idf": self.idf, "V_k": self.V_k,
                "k": self.k, "n_components": self.n_components,
            }, f)

    @classmethod
    def load(cls, path):
        with open(path, "rb") as f:
            state = pickle.load(f)
        obj = cls(n_components=state["n_components"])
        obj.vocab = state["vocab"]
        obj.idf = state["idf"]
        obj.V_k = state["V_k"]
        obj.k = state["k"]
        obj.fitted = True
        return obj


class TransformerEmbedder:
    """sentence-transformers/all-MiniLM-L6-v2 wrapper. Requires internet access
    on first run to download model weights (cached afterwards)."""

    name = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer  # may raise ImportError
        self.model = SentenceTransformer(model_name)  # may raise on no internet/no cache

    def fit(self, texts):
        return self.embed(texts)

    def embed(self, texts):
        vecs = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vecs, dtype=np.float64)

    def embed_one(self, text):
        return self.embed([text])[0]

    def save(self, path):
        # Nothing to persist beyond the model name; embeddings themselves are
        # persisted by the vector store.
        with open(path, "wb") as f:
            pickle.dump({"model_name": self.model_name if hasattr(self, "model_name") else "sentence-transformers/all-MiniLM-L6-v2"}, f)

    @classmethod
    def load(cls, path):
        return cls()


def get_embedder(prefer="auto", n_components=40):
    """
    prefer: "auto" (try transformer, fall back to LSA), "transformer", or "lsa".
    Returns an embedder instance (not yet fit).
    """
    if prefer in ("auto", "transformer"):
        try:
            embedder = TransformerEmbedder()
            print(f"[embeddings] using {embedder.name}")
            return embedder
        except Exception as e:
            if prefer == "transformer":
                raise
            print(f"[embeddings] sentence-transformers unavailable ({type(e).__name__}: {e}); "
                  f"falling back to local LSA embedder.")
    embedder = LocalLSAEmbedder(n_components=n_components)
    print(f"[embeddings] using {embedder.name}")
    return embedder
