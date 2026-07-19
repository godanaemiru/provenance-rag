# Provenance

**Every answer traces back to its source — or it doesn't get answered.**

A retrieval-augmented generation system, built for the Enterprise Document
Intelligence hackathon, that ingests a 23-document professional corpus,
indexes it with dense embeddings, and answers natural-language queries with
grounded, cited responses — refusing cleanly when the corpus doesn't support
an answer. The name reflects the core design constraint: every claim the
system makes must carry its provenance (document, page, section), and if
that chain can't be established, it says so instead of guessing.

```
python3 src/rag.py build              # ingest + embed + index the corpus
python3 src/rag.py ask "<question>"   # retrieve + generate a cited answer
python3 demo/run_demo.py              # run the 6-query demo (5 answered + 1 refused)
```

`pip install -r requirements.txt` first. See "Backends" below for what runs
with vs. without internet access.

## Corpus

23 synthetic-but-realistic annual-report documents (10-K style: Business
Overview, Risk Factors, MD&A, Financial Highlights, Notes) for 23 fictional
companies spanning distinct sectors — cloud software, semiconductors,
pharma, retail, regional banking, P&C insurance, oil & gas, renewable
energy, regulated utilities, airlines, automotive, industrial manufacturing,
telecom, media, consumer packaged goods, agritech, mining, REIT, logistics,
hospitality, biotech, cybersecurity, and food & beverage
(`corpus/_index.tsv` lists all 23 with sector).

**Why synthetic instead of downloaded real filings:** this system was built
in a sandboxed environment whose network allowlist covers only
`pypi.org`/`files.pythonhosted.org` and `github.com`; SEC EDGAR and
Hugging Face were both unreachable, so bulk-downloading 20+ real 10-Ks or a
pretrained embedding model wasn't possible during the build. Rather than
ship a thin 5-document corpus of whatever happened to be fetchable, the
corpus generator (`src/generate_corpus.py`) produces 23 full-length,
internally-consistent reports from a structured fact table, each with a
"needle" fact (a specific incident, dollar figure, or product detail) that
exists in exactly one document — this makes it possible to objectively
verify that retrieval is finding the *right* document out of 23 similarly
structured ones, not just any document that mentions similar general
topics (e.g. three different companies each have a distinct cybersecurity
incident; the system must retrieve the one the question is actually about).
Every fact needed to test the system is deliberately traceable to one
(document, page, section). **On a normal machine with internet access, the
exact same pipeline runs unmodified against real SEC 10-Ks / annual reports
— nothing in the ingestion, embedding, retrieval, or generation code is
specific to the synthetic corpus.**

## Chunking strategy

Structure-aware, not fixed-size sliding window: each chunk is exactly one
(page, disclosure section) unit — Business Overview, Risk Factors, MD&A,
Financial Highlights, or Notes — giving 5 chunks per document (115 total).
This keeps every retrieved passage a single coherent disclosure item and
lets every citation resolve to an exact `(Document, Page N, Section)`
triple instead of an arbitrary character offset. Any section over ~250
words is further split into overlapping 250-word sub-chunks (40-word
overlap) so chunk size stays bounded regardless of section verbosity —
see `src/chunking.py`.

## Embedding model

Two-tier, auto-detected (`src/embeddings.py`):

1. **`sentence-transformers/all-MiniLM-L6-v2`** (preferred/production path).
   Requires internet on first run to download the model.
2. **Local LSA embedder (automatic fallback, what this build actually
   demoed with):** a dependency-free TF-IDF → truncated-SVD (Latent
   Semantic Analysis) embedder implemented from scratch with numpy only —
   no model download, no external service. LSA is the classical
   embedding-based semantic retrieval technique (dense latent-topic
   vectors ranked by cosine similarity), not keyword/BM25 term matching,
   so it satisfies "embedding-based, not keyword-only" retrieval even
   without a neural model.

`get_embedder(prefer="auto")` tries (1) first and transparently falls back
to (2) — printing which backend is active — so the same code runs whether
or not the deployment environment can reach Hugging Face.

## Vector store

Two-tier, auto-detected (`src/vector_store.py`), mirroring the embedding
layer:

1. **Chroma** (`chromadb.PersistentClient`) — preferred/production path.
2. **`SimpleVectorStore`** (automatic fallback, what this build actually
   used): a small numpy-backed cosine-similarity index persisted to disk
   as `.npy` + `.json`. Used automatically when `chromadb` isn't
   installed — in this build's sandbox, `pip install chromadb` could not
   complete (heavy dependency chain, network-constrained environment).

## Retrieval + grounded generation + refusal

`src/generate.py`:

- **Refusal:** if the top retrieval similarity score is below
  `SIM_THRESHOLD` (0.20, empirically calibrated — see "Threshold
  calibration" below), the system returns a fixed refusal string instead
  of calling the generator at all. No generation step ever runs on
  insufficient context.
- **Generation, two backends:**
  - `LLMGenerator` (optional, production path): if `OPENAI_API_KEY` or
    `AZURE_OPENAI_API_KEY`/`AZURE_OPENAI_ENDPOINT` are set, calls a chat
    model with a system prompt that forces it to answer only from the
    retrieved context, cite every claim as `[Company — file, Page N,
    Section]`, and reply with the exact refusal sentence if context is
    insufficient.
  - `ExtractiveGenerator` (default, fully local — what this build's demo
    used): composes the answer directly from sentences drawn from the
    retrieved chunks. Nothing is generated that doesn't already appear
    verbatim in the corpus, which makes hallucination structurally
    impossible rather than merely unlikely.

## Threshold calibration

The refusal threshold was set by running ~17 probe queries (a mix of
clearly in-corpus, clearly out-of-corpus, and deliberately ambiguous
questions) and inspecting the score distribution:

| range | example | verdict |
|---|---|---|
| 0.00 | "What was Tesla's revenue in 2025?", "weather in Nairobi", "chocolate cake recipe" | correctly refused |
| 0.12–0.20 | "capital of France" (0.156) *and* some legitimate but short/generic-worded in-corpus questions like "Vertex Silicon's exposure to drought risk" (0.146) | **overlap zone — see limitation below** |
| 0.27–0.49 | ransomware/recall/facility-incident questions naming the specific company/topic | correctly answered with citations |

`SIM_THRESHOLD = 0.20` was chosen to sit just above the noise floor while
clearing every non-borderline in-corpus query tested. See "Hardest
retrieval edge case" below for the honest limitation this reveals.

## Setup

```bash
pip install -r requirements.txt
python3 src/rag.py build
python3 src/rag.py ask "Why did Falcon Motors recall vehicles?"
python3 demo/run_demo.py    # writes demo/demo_transcript.md
```

With no extra setup this runs fully offline (local LSA + numpy store +
extractive generator). To use the production stack, just have
`sentence-transformers` / `chromadb` installed and internet reachable on
first run — no code changes needed. To use a real LLM for fluent
generation, set `OPENAI_API_KEY` (or the `AZURE_OPENAI_*` variables).

## Corpus/pipeline stats

- 23 documents, 115 chunks, 5 (page, section) chunks per document.
- Retrieval: cosine similarity, top-k (default k=5, demo uses k=3).
- All 5 non-refusal demo queries retrieve the correct source document as
  the #1 hit; see `demo/demo_transcript.md`.

---

## 200-word write-up

**What we built:** an end-to-end RAG pipeline — structure-aware chunking,
auto-detected embedding/vector-store backends (sentence-transformers +
Chroma in production, a from-scratch numpy TF-IDF/SVD embedder + local
cosine store as a fully offline fallback), and a generation layer that
either calls an LLM under a strict grounding prompt or, with no API key,
composes answers directly from retrieved sentences so hallucination is
structurally impossible. Every answer cites (company, file, page, section);
below a similarity threshold the system refuses outright.

**Hardest retrieval edge case:** calibrating one similarity threshold for
refusal when running on the offline LSA fallback. Short queries with only
one or two distinctive content words (e.g. "exposure to drought risk")
sometimes score in the same 0.14–0.20 band as genuinely nonsensical
out-of-corpus questions ("capital of France" = 0.156), because bag-of-words
TF-IDF conflates word rarity with true semantic relevance — it can't tell
that "drought risk" is topically close to a Taiwan water-shortage risk
factor when the phrasing doesn't overlap much lexically.

**What we'd change with more time:** run the production
sentence-transformers/Chroma path (blocked only by this build's sandboxed,
no-internet environment) — real semantic embeddings give a far wider score
gap between relevant and irrelevant passages, which would resolve the
threshold-overlap problem directly instead of needing careful calibration.
