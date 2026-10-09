"""
Ingestion + chunking.

Each corpus document is a plain-text file shaped like:

    <Company> — Fiscal Year <FY> Annual Report
    Sector: <Sector> | Ticker: <Ticker>
    ======================================================================

    [[PAGE 1]]
    ## Item 1. Business Overview
    <paragraph text...>

    [[PAGE 2]]
    ## Item 1A. Risk Factors
    <paragraph text...>
    ...

Chunking strategy: one chunk per (page, section) unit. This is a deliberate
"structure-aware" chunking choice rather than a fixed-size sliding window:
each chunk is a single coherent disclosure item (Business Overview, Risk
Factors, MD&A, Financial Highlights, Notes), which keeps every retrieved
passage semantically self-contained and lets every citation point at an
exact (Document, Page, Section) triple instead of an arbitrary character
offset. For longer real-world documents, the same parser would additionally
split any section exceeding ~250 words into overlapping sub-chunks (see
`MAX_CHUNK_WORDS` / `OVERLAP_WORDS` below) so retrieval granularity stays
consistent regardless of how verbose a given section is.
"""
import os
import re
import glob
import json

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus")

PAGE_RE = re.compile(r"\[\[PAGE (\d+)\]\]")
SECTION_RE = re.compile(r"^##\s*(.+)$")

MAX_CHUNK_WORDS = 250
OVERLAP_WORDS = 40


def _split_long_section(text, max_words=MAX_CHUNK_WORDS, overlap=OVERLAP_WORDS):
    words = text.split()
    if len(words) <= max_words:
        return [text]
    parts = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        parts.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return parts


def parse_document(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    lines = raw.splitlines()
    title_line = lines[0].strip() if lines else os.path.basename(path)
    meta_line = lines[1].strip() if len(lines) > 1 else ""
    sector = ticker = ""
    m = re.match(r"Sector:\s*(.+?)\s*\|\s*Ticker:\s*(.+)", meta_line)
    if m:
        sector, ticker = m.group(1).strip(), m.group(2).strip()

    # company title without the " — Fiscal Year ... Annual Report" suffix
    company = title_line.split("—")[0].strip()

    chunks = []
    current_page = None
    current_section = None
    buf = []

    def flush():
        if current_page is not None and current_section is not None and buf:
            text = " ".join(buf).strip()
            for sub_idx, sub_text in enumerate(_split_long_section(text)):
                chunks.append({
                    "doc_file": os.path.basename(path),
                    "doc_title": title_line,
                    "company": company,
                    "sector": sector,
                    "ticker": ticker,
                    "page": current_page,
                    "section": current_section,
                    "sub_chunk": sub_idx,
                    "text": sub_text,
                })

    for line in lines[2:]:
        page_m = PAGE_RE.match(line.strip())
        if page_m:
            flush()
            buf = []
            current_page = int(page_m.group(1))
            current_section = None
            continue
        sec_m = SECTION_RE.match(line.strip())
        if sec_m:
            current_section = sec_m.group(1).strip()
            continue
        if line.strip():
            buf.append(line.strip())
    flush()

    return {
        "doc_file": os.path.basename(path),
        "doc_title": title_line,
        "company": company,
        "sector": sector,
        "ticker": ticker,
        "chunks": chunks,
    }


def load_corpus(corpus_dir=CORPUS_DIR):
    docs = []
    all_chunks = []
    for path in sorted(glob.glob(os.path.join(corpus_dir, "*.txt"))):
        doc = parse_document(path)
        docs.append(doc)
        all_chunks.extend(doc["chunks"])
    return docs, all_chunks


if __name__ == "__main__":
    docs, chunks = load_corpus()
    print(f"Loaded {len(docs)} documents, {len(chunks)} chunks total.")
    for c in chunks[:3]:
        print(json.dumps(c, indent=2)[:500])
        print("---")
