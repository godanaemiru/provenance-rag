"""
Grounded answer synthesis + refusal logic.

Design goal: it must be structurally impossible for this layer to state a
fact that isn't present in a retrieved chunk. Two generator backends:

1. LLMGenerator (optional): if OPENAI_API_KEY or AZURE_OPENAI_* env vars are
   set, calls a chat completion model with a strict system prompt that
   forces it to answer ONLY from the supplied context and to cite
   (Company, Page, Section) inline, or reply with the refusal sentence
   verbatim if the context is insufficient. Recommended for production use.

2. ExtractiveGenerator (default / fully local, no API key or internet
   needed): composes the answer directly out of sentences drawn from the
   retrieved chunks -- nothing is generated that doesn't already appear in
   the corpus, which trivially satisfies "no hallucination" by
   construction. This is the backend actually exercised in this build's
   demo, since the sandboxed environment has no LLM API credentials.

Refusal logic (applies to both backends): if the top retrieval score is
below SIM_THRESHOLD, or no chunks are retrieved at all, the system returns
the fixed refusal string instead of calling either generator.
"""
import os
import re
from embeddings import tokenize

REFUSAL_MESSAGE = (
    "I don't have information on that in the indexed corpus. "
    "I can only answer questions supported by the ingested documents, and "
    "no retrieved passage was a close enough match to answer this confidently."
)

SIM_THRESHOLD = 0.20  # tuned empirically against ~17 in-corpus and out-of-corpus
                       # probe queries; see README "Threshold calibration" section
                       # for the score distribution and the known edge-case gap.


def _sentence_split(text):
    # Lightweight sentence splitter; good enough for our short report paragraphs.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
    return [p.strip() for p in parts if p.strip()]


def _best_sentence(query_tokens, text):
    sentences = _sentence_split(text)
    if not sentences:
        return text
    best, best_score = sentences[0], -1
    q_set = set(query_tokens)
    for s in sentences:
        s_tokens = set(tokenize(s))
        overlap = len(q_set & s_tokens)
        if overlap > best_score:
            best_score = overlap
            best = s
    return best


def format_citation(meta):
    return f"[{meta['company']} — {meta['doc_file']}, Page {meta['page']}, {meta['section']}]"


class ExtractiveGenerator:
    name = "extractive (local, no external API)"

    def answer(self, query, retrieved, max_sources=3):
        query_tokens = tokenize(query)
        used = retrieved[:max_sources]
        lines = []
        for r in used:
            meta = r["metadata"]
            sentence = _best_sentence(query_tokens, r["document"])
            lines.append(f"{sentence} {format_citation(meta)}")
        answer_text = " ".join(lines)
        citations = [format_citation(r["metadata"]) for r in used]
        return answer_text, citations


class LLMGenerator:
    """Optional OpenAI / Azure OpenAI backed generator. Not used in this
    build's demo (no API credentials in the sandbox) but included so the
    system can be pointed at a real LLM with zero code changes -- just set
    OPENAI_API_KEY (or AZURE_OPENAI_ENDPOINT/AZURE_OPENAI_API_KEY) in the
    environment."""

    name = "llm (OpenAI/Azure OpenAI chat completion)"

    SYSTEM_PROMPT = (
        "You are a document-grounded question answering assistant. You will "
        "be given a user question and a set of numbered CONTEXT passages, "
        "each tagged with its source (company, document file, page, "
        "section). Answer using ONLY information contained in the CONTEXT "
        "passages. For every factual claim, cite the exact source tag it "
        "came from, in the form [Company — file, Page N, Section]. "
        "If the CONTEXT does not contain enough information to answer the "
        "question, respond with exactly: \"" + REFUSAL_MESSAGE + "\" and "
        "nothing else. Never use outside knowledge, and never guess."
    )

    def __init__(self):
        if os.environ.get("AZURE_OPENAI_API_KEY"):
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            )
            self.model = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        elif os.environ.get("OPENAI_API_KEY"):
            from openai import OpenAI
            self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        else:
            raise RuntimeError("No OPENAI_API_KEY or AZURE_OPENAI_API_KEY set.")

    def answer(self, query, retrieved, max_sources=5):
        used = retrieved[:max_sources]
        context_blocks = []
        for i, r in enumerate(used, start=1):
            meta = r["metadata"]
            context_blocks.append(
                f"[{i}] SOURCE: {format_citation(meta)}\n{r['document']}"
            )
        user_prompt = (
            f"QUESTION: {query}\n\nCONTEXT:\n" + "\n\n".join(context_blocks)
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )
        text = resp.choices[0].message.content
        citations = [format_citation(r["metadata"]) for r in used]
        return text, citations


def get_generator(prefer="auto"):
    if prefer in ("auto", "llm"):
        try:
            gen = LLMGenerator()
            print(f"[generate] using {gen.name}")
            return gen
        except Exception as e:
            if prefer == "llm":
                raise
            print(f"[generate] LLM backend unavailable ({type(e).__name__}: {e}); "
                  f"falling back to extractive generator.")
    gen = ExtractiveGenerator()
    print(f"[generate] using {gen.name}")
    return gen


def answer_query(query, retrieved, generator, threshold=SIM_THRESHOLD):
    if not retrieved or retrieved[0]["score"] < threshold:
        return {
            "answer": REFUSAL_MESSAGE,
            "citations": [],
            "refused": True,
            "top_score": retrieved[0]["score"] if retrieved else None,
        }
    answer_text, citations = generator.answer(query, retrieved)
    return {
        "answer": answer_text,
        "citations": citations,
        "refused": False,
        "top_score": retrieved[0]["score"],
    }
