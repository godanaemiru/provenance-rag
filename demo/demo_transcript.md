# Demo Transcript — Provenance (Enterprise Document Intelligence RAG)

6 queries against the 23-document synthetic annual-report corpus (see README for corpus/embedding/vector-store details). Query 6 is the required out-of-corpus refusal case.

## Query 1: Tell me about the ransomware incident at Pathway Logistics.

**Top retrieval score:** 0.394  
**Refused:** False

**Answer:**

A ransomware intrusion detected in the Company's warehouse-management systems in October 2025 disrupted order fulfillment at 19 distribution centers for approximately 60 hours; Pathway did not pay the ransom and restored operations from backups, incurring $37 million in incident-response and lost-throughput costs. [Pathway Logistics Corporation — PWLG.txt, Page 2, Item 1A. Risk Factors] Pathway's warehouse-management ransomware incident in October 2025 affected 19 of the Company's 240 distribution centers nationwide. [Pathway Logistics Corporation — PWLG.txt, Page 5, Notes to Financial Statements] Pathway Logistics Corporation (NASDAQ/NYSE: PWLG) operates in the Freight & Logistics sector. [Pathway Logistics Corporation — PWLG.txt, Page 1, Item 1. Business Overview]

**Citations:**
- [Pathway Logistics Corporation — PWLG.txt, Page 2, Item 1A. Risk Factors]
- [Pathway Logistics Corporation — PWLG.txt, Page 5, Notes to Financial Statements]
- [Pathway Logistics Corporation — PWLG.txt, Page 1, Item 1. Business Overview]

## Query 2: Why did Falcon Motors recall vehicles in fiscal year 2025?

**Top retrieval score:** 0.397  
**Refused:** False

**Answer:**

Falcon Motors designs, manufactures, and sells passenger vehicles and light trucks under the Falcon and Aravel brands, with assembly plants in Michigan, Ontario, and Mexico. [Falcon Motors Corporation — FLCM.txt, Page 1, Item 1. Business Overview] In July 2025 Falcon Motors initiated a voluntary recall of 1.3 million model-year 2023-2025 Aravel SUVs due to a brake-booster vacuum-hose defect linked to 14 reported crashes; the Company recorded a $290 million recall-related warranty charge in its fiscal third quarter. [Falcon Motors Corporation — FLCM.txt, Page 2, Item 1A. Risk Factors] Except as otherwise noted, all figures in this report are presented on a US GAAP basis for the fiscal year ended 2025. [Falcon Motors Corporation — FLCM.txt, Page 5, Notes to Financial Statements]

**Citations:**
- [Falcon Motors Corporation — FLCM.txt, Page 1, Item 1. Business Overview]
- [Falcon Motors Corporation — FLCM.txt, Page 2, Item 1A. Risk Factors]
- [Falcon Motors Corporation — FLCM.txt, Page 5, Notes to Financial Statements]

## Query 3: What happened at Granite Peak Mining's Cerro Alto facility?

**Top retrieval score:** 0.461  
**Refused:** False

**Answer:**

Granite Peak's Cerro Alto facility in Chile accounts for approximately 31% of the Company's total copper production. [Granite Peak Mining Co. — GPMC.txt, Page 5, Notes to Financial Statements] A tailings-dam stability review at the Company's Cerro Alto facility in Chile, prompted by a Chilean regulatory audit in FY2025, required $46 million of remediation work and a temporary 25% reduction in processing throughput for 10 weeks while reinforcement work was completed. [Granite Peak Mining Co. — GPMC.txt, Page 2, Item 1A. Risk Factors] Granite Peak Mining Co. [Granite Peak Mining Co. — GPMC.txt, Page 1, Item 1. Business Overview]

**Citations:**
- [Granite Peak Mining Co. — GPMC.txt, Page 5, Notes to Financial Statements]
- [Granite Peak Mining Co. — GPMC.txt, Page 2, Item 1A. Risk Factors]
- [Granite Peak Mining Co. — GPMC.txt, Page 1, Item 1. Business Overview]

## Query 4: How many patients have been treated with Helix Genomics' Zenovex therapy?

**Top retrieval score:** 0.273  
**Refused:** False

**Answer:**

Helix Genomics develops gene-editing therapies for inherited blood disorders, with its lead product Zenovex (an ex vivo CRISPR-based therapy for sickle cell disease) approved in the United States in FY2024. [Helix Genomics, Inc. — HLXG.txt, Page 1, Item 1. Business Overview] Revenue growth reflects the first full fiscal year of commercial Zenovex sales following its FY2024 approval, with 340 patients treated to date across 28 authorized treatment centers. [Helix Genomics, Inc. — HLXG.txt, Page 3, Item 7. Management's Discussion and Analysis (MD&A)] Zenovex has been administered to 340 patients across 28 authorized treatment centers in the United States since its FY2024 approval. [Helix Genomics, Inc. — HLXG.txt, Page 5, Notes to Financial Statements]

**Citations:**
- [Helix Genomics, Inc. — HLXG.txt, Page 1, Item 1. Business Overview]
- [Helix Genomics, Inc. — HLXG.txt, Page 3, Item 7. Management's Discussion and Analysis (MD&A)]
- [Helix Genomics, Inc. — HLXG.txt, Page 5, Notes to Financial Statements]

## Query 5: How much did Everwell Consumer Products recall, and why?

**Top retrieval score:** 0.348  
**Refused:** False

**Answer:**

A voluntary recall of approximately 3.2 million units of the Company's Everwell Kids liquid multivitamin was issued in FY2025 after routine testing detected elevated vitamin A levels in a subset of production lots from the Company's Greenville, South Carolina facility. [Everwell Consumer Products — EVWL.txt, Page 2, Item 1A. Risk Factors] Everwell Consumer Products (NASDAQ/NYSE: EVWL) operates in the Consumer Packaged Goods sector. [Everwell Consumer Products — EVWL.txt, Page 1, Item 1. Business Overview] Everwell's Greenville, South Carolina facility, implicated in the FY2025 multivitamin recall, manufactures approximately 40% of the Company's North American over-the-counter product volume. [Everwell Consumer Products — EVWL.txt, Page 5, Notes to Financial Statements]

**Citations:**
- [Everwell Consumer Products — EVWL.txt, Page 2, Item 1A. Risk Factors]
- [Everwell Consumer Products — EVWL.txt, Page 1, Item 1. Business Overview]
- [Everwell Consumer Products — EVWL.txt, Page 5, Notes to Financial Statements]

## Query 6: What is the capital of France?

**Top retrieval score:** 0.156  
**Refused:** True

**Answer:**

I don't have information on that in the indexed corpus. I can only answer questions supported by the ingested documents, and no retrieved passage was a close enough match to answer this confidently.

