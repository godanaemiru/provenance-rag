"""
Runs the fixed demo query set required by the submission (>=5 distinct
queries including one that must be correctly refused) and writes a
markdown transcript to demo/demo_transcript.md for the video walkthrough
and Q&A tab.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rag import load_pipeline, ask
from generate import get_generator

DEMO_QUERIES = [
    "Tell me about the ransomware incident at Pathway Logistics.",
    "Why did Falcon Motors recall vehicles in fiscal year 2025?",
    "What happened at Granite Peak Mining's Cerro Alto facility?",
    "How many patients have been treated with Helix Genomics' Zenovex therapy?",
    "How much did Everwell Consumer Products recall, and why?",
    "What is the capital of France?",  # deliberate out-of-corpus refusal case
]


def main():
    embedder, store = load_pipeline()
    generator = get_generator()

    out_lines = ["# Demo Transcript — Provenance (Enterprise Document Intelligence RAG)\n"]
    out_lines.append(
        "6 queries against the 23-document synthetic annual-report corpus "
        "(see README for corpus/embedding/vector-store details). Query 6 is "
        "the required out-of-corpus refusal case.\n"
    )

    for i, q in enumerate(DEMO_QUERIES, start=1):
        result, retrieved = ask(q, embedder, store, generator, top_k=3, verbose=False)
        out_lines.append(f"## Query {i}: {q}\n")
        out_lines.append(f"**Top retrieval score:** {result['top_score']:.3f}  ")
        out_lines.append(f"**Refused:** {result['refused']}\n")
        out_lines.append(f"**Answer:**\n\n{result['answer']}\n")
        if result["citations"]:
            out_lines.append("**Citations:**")
            for c in result["citations"]:
                out_lines.append(f"- {c}")
        out_lines.append("")

    transcript = "\n".join(out_lines)
    out_path = os.path.join(os.path.dirname(__file__), "demo_transcript.md")
    with open(out_path, "w") as f:
        f.write(transcript)
    print(transcript)
    print(f"\n[demo] transcript written to {out_path}")


if __name__ == "__main__":
    main()
