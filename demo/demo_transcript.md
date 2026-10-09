# Demo Transcript — Provenance (Enterprise Document Intelligence RAG)

6 queries against the 23-document synthetic annual-report corpus (see README for corpus/embedding/vector-store details). Query 6 is the required out-of-corpus refusal case.

## Query 1: Tell me about the ransomware incident at Pathway Logistics.

**Top retrieval score:** 0.676  
**Refused:** False

**Answer:**

Pathway Logistics suffered a warehouse‑management ransomware intrusion in October 2025 that hit 19 of its 240 distribution centers nationwide【Pathway Logistics Corporation — Fiscal Year 2025 Annual Report — PWLG.txt, Page 5, Notes to Financial Statements】. The attack disrupted order fulfillment at those centers for roughly 60 hours【Pathway Logistics Corporation — Fiscal Year 2025 Annual Report — PWLG.txt, Page 2, Item 1A. Risk Factors】. Pathway chose not to pay the ransom; instead it restored operations from backups, incurring about $37 million in incident‑response and lost‑throughput costs【Pathway Logistics Corporation — Fiscal Year 2025 Annual Report — PWLG.txt, Page 2, Item 1A. Risk Factors】. The company has since implemented corrective actions to address the vulnerability【Pathway Logistics Corporation — Fiscal Year 2025 Annual Report — PWLG.txt, Page 2, Item 1A. Risk Factors】.

**Citations:**
- [Pathway Logistics Corporation â€” Fiscal Year 2025 Annual Report — PWLG.txt, Page 5, Notes to Financial Statements]
- [Pathway Logistics Corporation â€” Fiscal Year 2025 Annual Report — PWLG.txt, Page 2, Item 1A. Risk Factors]
- [Pathway Logistics Corporation â€” Fiscal Year 2025 Annual Report — PWLG.txt, Page 1, Item 1. Business Overview]

## Query 2: Why did Falcon Motors recall vehicles in fiscal year 2025?

**Top retrieval score:** 0.657  
**Refused:** False

**Answer:**

Falcon Motors voluntarily recalled the vehicles because a brake‑booster vacuum‑hose defect was discovered in the 2023‑2025 Aravel SUVs, a problem that had been linked to 14 reported crashes【Falcon Motors Corporation — Fiscal Year 2025 Annual Report — FLCM.txt, Page 2, Item 1A. Risk Factors】.

**Citations:**
- [Falcon Motors Corporation â€” Fiscal Year 2025 Annual Report — FLCM.txt, Page 2, Item 1A. Risk Factors]
- [Falcon Motors Corporation â€” Fiscal Year 2025 Annual Report — FLCM.txt, Page 5, Notes to Financial Statements]
- [Falcon Motors Corporation â€” Fiscal Year 2025 Annual Report — FLCM.txt, Page 1, Item 1. Business Overview]

## Query 3: What happened at Granite Peak Mining's Cerro Alto facility?

**Top retrieval score:** 0.604  
**Refused:** False

**Answer:**

Granite Peak’s Cerro Alto facility in Chile underwent a regulatory‑driven tailings‑dam stability review after a Chilean audit in FY 2025. The review uncovered issues that required about $46 million in remediation work and forced the plant to cut its processing throughput by roughly 25 % for a ten‑week period while reinforcement work was completed【Granite Peak Mining Co. — Fiscal Year 2025 Annual Report — GPMC.txt, Page 2, Item 1A. Risk Factors】.

**Citations:**
- [Granite Peak Mining Co. â€” Fiscal Year 2025 Annual Report — GPMC.txt, Page 5, Notes to Financial Statements]
- [Granite Peak Mining Co. â€” Fiscal Year 2025 Annual Report — GPMC.txt, Page 1, Item 1. Business Overview]
- [Granite Peak Mining Co. â€” Fiscal Year 2025 Annual Report — GPMC.txt, Page 2, Item 1A. Risk Factors]

## Query 4: How many patients have been treated with Helix Genomics' Zenovex therapy?

**Top retrieval score:** 0.600  
**Refused:** False

**Answer:**

Helix Genomics reports that Zenovex has been administered to **340 patients** to date — 340 patients have been treated across 28 authorized treatment centers【Helix Genomics — Fiscal Year 2025 Annual Report, Page 5, Notes to Financial Statements】【Helix Genomics — Fiscal Year 2025 Annual Report, Page 3, MD&A】

**Citations:**
- [Helix Genomics, Inc. â€” Fiscal Year 2025 Annual Report — HLXG.txt, Page 5, Notes to Financial Statements]
- [Helix Genomics, Inc. â€” Fiscal Year 2025 Annual Report — HLXG.txt, Page 1, Item 1. Business Overview]
- [Helix Genomics, Inc. â€” Fiscal Year 2025 Annual Report — HLXG.txt, Page 3, Item 7. Management's Discussion and Analysis (MD&A)]

## Query 5: How much did Everwell Consumer Products recall, and why?

**Top retrieval score:** 0.575  
**Refused:** False

**Answer:**

Everwell Consumer Products voluntarily recalled **approximately 3.2 million units** of its Everwell Kids liquid multivitamin after routine testing found **elevated vitamin A levels** in a subset of production lots from its Greenville, South Carolina facility【Everwell Consumer Products — Fiscal Year 2025 Annual Report — EVWL.txt, Page 2, Item 1A. Risk Factors】.

**Citations:**
- [Everwell Consumer Products â€” Fiscal Year 2025 Annual Report — EVWL.txt, Page 1, Item 1. Business Overview]
- [Everwell Consumer Products â€” Fiscal Year 2025 Annual Report — EVWL.txt, Page 5, Notes to Financial Statements]
- [Everwell Consumer Products â€” Fiscal Year 2025 Annual Report — EVWL.txt, Page 2, Item 1A. Risk Factors]

## Query 6: What is the capital of France?

**Top retrieval score:** 0.374  
**Refused:** True

**Answer:**

I don't have information on that in the indexed corpus. I can only answer questions supported by the ingested documents, and no retrieved passage was a close enough match to answer this confidently.

