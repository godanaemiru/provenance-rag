"""
Generates a synthetic-but-realistic corpus of 23 annual-report-style documents
(10-K style: Business Overview, Risk Factors, MD&A, Financial Highlights, Notes)
for fictional companies spanning 20+ industries.

Why synthetic: the sandboxed build environment cannot reach SEC EDGAR or
HuggingFace to download real filings or pretrained embedding models (only
pypi.org / files.pythonhosted.org / github.com are reachable). To still
deliver a corpus with genuine cross-document semantic ambiguity (many docs
share topics like "cybersecurity incident" or "supply chain disruption" but
each has a distinct, specific instance), the corpus is generated from a
structured fact table below, and each document contains "needle" facts used
to test precise semantic retrieval and refusal behavior.

Every document is written with explicit PAGE markers so the ingestion
pipeline can cite (Document Title, Page N, Section) for every retrieved chunk.
"""
import os

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus")
os.makedirs(CORPUS_DIR, exist_ok=True)

COMPANIES = [
    dict(
        name="Nimbus Cloud Systems, Inc.", ticker="NCLS", sector="Enterprise Cloud Software",
        fy="2025", revenue="4.82 billion", net_income="612 million", rev_change="+18%",
        employees="14,300", rd_spend="891 million",
        overview="Nimbus Cloud Systems develops multi-tenant cloud infrastructure and data "
                 "orchestration software for mid-market enterprises, serving customers across "
                 "financial services, retail, and healthcare through its Nimbus Fabric platform.",
        risk="A March 2025 configuration error in the Nimbus Fabric access-control layer exposed "
             "metadata (not customer content) for approximately 40,000 tenant accounts for 6 hours "
             "before containment; the Company incurred $14 million in remediation and customer "
             "credits and now requires dual-approval for all production access-control changes.",
        driver="Revenue growth was driven by a 24% increase in Nimbus Fabric seat licenses and the "
               "acquisition of Ledgerline Analytics in Q2 FY2025, which added $310 million in "
               "annualized recurring revenue.",
        note="The Company's primary data center campus is located in Ashburn, Virginia, with "
             "secondary failover capacity in Dublin, Ireland and Singapore.",
    ),
    dict(
        name="Vertex Silicon Corporation", ticker="VSXC", sector="Semiconductor Manufacturing",
        fy="2025", revenue="9.14 billion", net_income="1.47 billion", rev_change="+7%",
        employees="22,900", rd_spend="1.63 billion",
        overview="Vertex Silicon designs and fabricates analog and mixed-signal semiconductors "
                 "used in automotive power management, industrial sensors, and 5G radio-frequency "
                 "front ends, operating fabrication plants in Taiwan and Oregon.",
        risk="A prolonged drought in Taiwan's Hsinchu region during FY2025 reduced ultrapure water "
             "allocation to the Company's Fab 4 facility by 30% for eleven weeks, cutting wafer "
             "output by an estimated 6% and delaying shipments to two automotive customers.",
        driver="Growth was constrained by softening consumer electronics demand but partially "
               "offset by a 31% increase in automotive power-management chip orders following new "
               "design wins with two European automakers.",
        note="Vertex Silicon holds 1,240 active patents related to gallium nitride (GaN) power "
             "transistor design as of fiscal year end.",
    ),
    dict(
        name="Meridian Biopharma, Inc.", ticker="MRBP", sector="Pharmaceuticals",
        fy="2025", revenue="6.35 billion", net_income="-210 million", rev_change="+3%",
        employees="9,700", rd_spend="2.41 billion",
        overview="Meridian Biopharma researches and commercializes therapies for autoimmune and "
                 "inflammatory diseases, with its flagship product Cerivant (brizukimab) approved "
                 "in the US, EU, and Japan for moderate-to-severe plaque psoriasis.",
        risk="In August 2025 the FDA issued a Complete Response Letter for Meridian's supplemental "
             "application seeking to expand Cerivant's label to pediatric patients aged 6-11, "
             "citing insufficient long-term safety data from the PEDIGREE-2 trial; the Company "
             "does not expect a refiled submission before mid-2026.",
        driver="The net loss reflects a $540 million upfront payment to license a Phase 2 oral "
               "IL-23 inhibitor from a South Korean biotech partner, recorded as an in-process "
               "R&D charge in Q3 FY2025.",
        note="Cerivant generated $4.1 billion of the Company's total FY2025 revenue, representing "
             "64% of net sales.",
    ),
    dict(
        name="Harborline Retail Group", ticker="HRBL", sector="Specialty Retail",
        fy="2025", revenue="11.2 billion", net_income="398 million", rev_change="+2%",
        employees="61,500", rd_spend="112 million",
        overview="Harborline Retail Group operates 640 home-goods and furniture stores across "
                 "North America under the Harborline and Coastal & Co. banners, alongside an "
                 "e-commerce platform representing 28% of total sales.",
        risk="Same-store sales declined 4.1% in FY2025 as elevated mortgage rates suppressed "
             "furniture demand tied to home purchases; the Company closed 38 underperforming "
             "stores and recorded a $61 million lease-impairment charge.",
        driver="E-commerce revenue grew 19% following the FY2024 rollout of augmented-reality "
               "room-planning tools, partially offsetting brick-and-mortar softness.",
        note="Harborline's largest distribution center, a 1.4 million square foot facility in "
             "Reno, Nevada, processes approximately 55% of e-commerce order volume.",
    ),
    dict(
        name="Cascade National Bank", ticker="CSNB", sector="Regional Banking",
        fy="2025", revenue="5.9 billion", net_income="1.31 billion", rev_change="+5%",
        employees="18,200", rd_spend="n/a",
        overview="Cascade National Bank is a regional bank holding company operating 410 branches "
                 "across the Pacific Northwest, providing commercial lending, retail deposits, and "
                 "wealth management services to over 2.3 million customers.",
        risk="Commercial real estate loans secured by office properties represented 9.8% of "
             "Cascade's loan portfolio at fiscal year end; the Bank increased its allowance for "
             "credit losses on this segment by $84 million during FY2025 due to rising office "
             "vacancy rates in Portland and Seattle.",
        driver="Net interest income rose as the Bank's deposit costs stabilized faster than "
               "expected following the rate environment of FY2024, expanding net interest margin "
               "by 22 basis points.",
        note="Cascade National Bank's Tier 1 capital ratio stood at 12.4% at fiscal year end, "
             "above the 10.5% level generally considered well-capitalized under regulatory "
             "guidance.",
    ),
    dict(
        name="Bluepeak Insurance Holdings", ticker="BPIH", sector="Property & Casualty Insurance",
        fy="2025", revenue="7.6 billion", net_income="-95 million", rev_change="+4%",
        employees="12,100", rd_spend="n/a",
        overview="Bluepeak Insurance Holdings underwrites homeowners, auto, and commercial "
                 "property insurance in 34 US states, with concentrated exposure in Gulf Coast "
                 "and California wildfire-prone regions.",
        risk="Hurricane Elva made landfall near Mobile, Alabama in September 2025, generating "
             "estimated gross claims of $1.1 billion for the Company, of which $740 million was "
             "ceded to reinsurance partners, resulting in a net underwriting loss for the "
             "property segment.",
        driver="The Company non-renewed approximately 46,000 California wildfire-zone homeowner "
               "policies during FY2025 as part of a program to reduce catastrophe-exposed "
               "concentration, a decision that reduced gross written premium growth by an "
               "estimated 3 percentage points.",
        note="Bluepeak's combined ratio for FY2025 was 104.2%, meaning claims and expenses "
             "exceeded premiums collected for the year.",
    ),
    dict(
        name="Redstone Energy Corporation", ticker="RSEC", sector="Oil & Gas Exploration",
        fy="2025", revenue="18.9 billion", net_income="2.86 billion", rev_change="-6%",
        employees="8,400", rd_spend="204 million",
        overview="Redstone Energy explores for and produces crude oil and natural gas in the "
                 "Permian Basin and Gulf of Mexico, operating both onshore unconventional wells "
                 "and offshore platforms.",
        risk="A subsea pipeline leak at the Company's Cormorant Deepwater platform in the Gulf of "
             "Mexico in May 2025 released an estimated 1,900 barrels of crude before shut-in; "
             "Redstone recorded a $187 million environmental remediation and regulatory-fine "
             "provision related to the incident.",
        driver="Lower average realized natural gas prices, down 19% year over year, drove the "
               "revenue decline despite a 4% increase in total production volumes.",
        note="Redstone's proved reserves at fiscal year end totaled 2.1 billion barrels of oil "
             "equivalent, with a reserve replacement ratio of 118% for the year.",
    ),
    dict(
        name="Solara Power, Inc.", ticker="SLRP", sector="Renewable Energy Generation",
        fy="2025", revenue="2.14 billion", net_income="71 million", rev_change="+34%",
        employees="4,600", rd_spend="196 million",
        overview="Solara Power develops, owns, and operates utility-scale solar and battery "
                 "storage projects across the southwestern United States, with 6.8 gigawatts of "
                 "operating generation capacity at fiscal year end.",
        risk="Section 45X advanced-manufacturing tax credits, which offset approximately 14% of "
             "Solara's project construction costs in FY2025, are subject to a pending "
             "congressional review that could reduce or eliminate the credit for projects "
             "beginning construction after 2026.",
        driver="Revenue growth reflects the commissioning of the 900-megawatt Sagebrook Solar "
               "and Storage facility in Arizona, the Company's largest project to date, which "
               "reached full commercial operation in January 2025.",
        note="Solara's battery storage fleet has a combined capacity of 2.3 gigawatt-hours, "
             "used primarily to shift solar generation into evening peak demand hours.",
    ),
    dict(
        name="Ironbridge Utilities, Inc.", ticker="IRUT", sector="Regulated Electric Utility",
        fy="2025", revenue="8.7 billion", net_income="1.02 billion", rev_change="+3%",
        employees="15,600", rd_spend="n/a",
        overview="Ironbridge Utilities is a regulated electric and gas utility serving 3.9 "
                 "million customers across the Midwest, operating a mix of natural gas, nuclear, "
                 "and wind generation assets.",
        risk="A June 2025 windstorm caused sustained outages for 410,000 customers and downed "
             "over 1,100 miles of distribution line; the Company's regulator approved recovery "
             "of $96 million of the $140 million restoration cost through a storm-cost rider, "
             "with the remaining $44 million disallowed as imprudently incurred.",
        driver="Rate base growth from the Company's grid-modernization program, approved by "
               "state regulators in FY2024, contributed the majority of net income growth.",
        note="Ironbridge's Fairfield Nuclear Generating Station operating license was renewed "
             "for an additional 20 years by the Nuclear Regulatory Commission in FY2025.",
    ),
    dict(
        name="Skyline Airways Holdings", ticker="SKYA", sector="Passenger Airlines",
        fy="2025", revenue="14.6 billion", net_income="-340 million", rev_change="+1%",
        employees="41,000", rd_spend="n/a",
        overview="Skyline Airways operates a domestic and international passenger network from "
                 "hub airports in Denver and Charlotte, with a fleet of 512 mainline and regional "
                 "aircraft.",
        risk="A software defect in Skyline's crew-scheduling system in December 2025 caused the "
             "cancellation of approximately 2,800 flights over five days during the holiday "
             "travel period, resulting in an estimated $410 million impact to revenue and "
             "customer-compensation costs.",
        driver="Elevated jet fuel prices, up 11% year over year, combined with the December "
               "operational disruption, drove the net loss despite record passenger volumes.",
        note="Skyline's on-time arrival rate for FY2025 was 71.4%, down from 79.8% in FY2024, "
             "largely attributable to the December scheduling-system disruption.",
    ),
    dict(
        name="Falcon Motors Corporation", ticker="FLCM", sector="Automotive Manufacturing",
        fy="2025", revenue="52.3 billion", net_income="1.98 billion", rev_change="-4%",
        employees="94,000", rd_spend="3.1 billion",
        overview="Falcon Motors designs, manufactures, and sells passenger vehicles and light "
                 "trucks under the Falcon and Aravel brands, with assembly plants in Michigan, "
                 "Ontario, and Mexico.",
        risk="In July 2025 Falcon Motors initiated a voluntary recall of 1.3 million model-year "
             "2023-2025 Aravel SUVs due to a brake-booster vacuum-hose defect linked to 14 "
             "reported crashes; the Company recorded a $290 million recall-related warranty "
             "charge in its fiscal third quarter.",
        driver="Revenue declined due to a 60-day production pause at the Ontario assembly plant "
               "in Q2 FY2025 related to a wiring-harness supplier shortage.",
        note="Falcon Motors' battery-electric vehicle sales represented 9.2% of total unit "
             "volume in FY2025, up from 6.1% in FY2024.",
    ),
    dict(
        name="Titan Industrial Works", ticker="TIWK", sector="Heavy Industrial Manufacturing",
        fy="2025", revenue="16.4 billion", net_income="1.55 billion", rev_change="+6%",
        employees="38,200", rd_spend="712 million",
        overview="Titan Industrial Works manufactures heavy construction equipment, mining "
                 "machinery, and industrial engines, distributing through an independent dealer "
                 "network across 140 countries.",
        risk="A labor strike at the Company's Peoria, Illinois engine-manufacturing complex "
             "lasted 37 days in FY2025, reducing engine shipment volumes by an estimated 12% for "
             "the fiscal third quarter and resulting in $58 million of incremental labor and "
             "overtime costs to recover backlog.",
        driver="Strong demand for mining equipment, particularly in copper and lithium extraction "
               "markets, drove order backlog to a record $24.6 billion at fiscal year end.",
        note="Titan's dealer network held approximately 4.8 months of equipment inventory at "
             "fiscal year end, within the Company's targeted 4-6 month range.",
    ),
    dict(
        name="Northwave Telecom, Inc.", ticker="NWTL", sector="Telecommunications",
        fy="2025", revenue="41.7 billion", net_income="4.02 billion", rev_change="+2%",
        employees="72,500", rd_spend="1.9 billion",
        overview="Northwave Telecom provides wireless, broadband, and fiber services to "
                 "residential and enterprise customers nationwide, with 5G coverage reaching "
                 "82% of the US population at fiscal year end.",
        risk="Postpaid phone subscriber net additions fell to 410,000 in FY2025 from 1.2 million "
             "in FY2024 as a regional competitor's aggressive fixed-wireless promotion drove "
             "elevated churn in the Company's southeastern service territory.",
        driver="Fiber broadband subscriber growth of 640,000 net additions, driven by an "
               "expansion of the fiber footprint to 3.2 million additional homes passed, "
               "partially offset wireless softness.",
        note="Northwave's fiber network passed 19.4 million homes at fiscal year end, with a "
             "take rate of 38%.",
    ),
    dict(
        name="Lumen Media Group", ticker="LMDG", sector="Media & Entertainment",
        fy="2025", revenue="9.3 billion", net_income="212 million", rev_change="-8%",
        employees="16,900", rd_spend="340 million",
        overview="Lumen Media Group produces and distributes filmed entertainment and operates "
                 "a direct-to-consumer streaming service, Lumen+, with 58 million global "
                 "subscribers at fiscal year end.",
        risk="Linear television advertising revenue declined 21% in FY2025 as advertisers "
             "continued shifting spend to streaming and social platforms, and the Company "
             "recorded a $410 million impairment charge against the carrying value of two "
             "regional cable news networks.",
        driver="Lumen+ subscriber growth of 9 million net additions was driven by the theatrical "
               "and streaming release of the Company's Ashfall film franchise's third installment.",
        note="Lumen+ achieved segment profitability for the first time in FY2025, reporting "
             "$140 million of operating income for the streaming segment.",
    ),
    dict(
        name="Everwell Consumer Products", ticker="EVWL", sector="Consumer Packaged Goods",
        fy="2025", revenue="21.5 billion", net_income="2.63 billion", rev_change="+3%",
        employees="47,000", rd_spend="580 million",
        overview="Everwell Consumer Products manufactures household cleaning, personal care, and "
                 "over-the-counter health products sold under 22 brands in more than 90 "
                 "countries.",
        risk="A voluntary recall of approximately 3.2 million units of the Company's Everwell "
             "Kids liquid multivitamin was issued in FY2025 after routine testing detected "
             "elevated vitamin A levels in a subset of production lots from the Company's "
             "Greenville, South Carolina facility.",
        driver="Volume growth in emerging markets, particularly India and Indonesia, offset "
               "continued private-label competitive pressure in North American home care "
               "categories.",
        note="Everwell's Greenville, South Carolina facility, implicated in the FY2025 "
             "multivitamin recall, manufactures approximately 40% of the Company's North "
             "American over-the-counter product volume.",
    ),
    dict(
        name="Greenfield Agritech Corporation", ticker="GRAG", sector="Agriculture & Crop Science",
        fy="2025", revenue="13.8 billion", net_income="1.11 billion", rev_change="+1%",
        employees="24,300", rd_spend="1.05 billion",
        overview="Greenfield Agritech develops seed genetics, crop protection chemicals, and "
                 "precision-agriculture software for row-crop farmers across North and South "
                 "America.",
        risk="A widespread drought across Argentina and southern Brazil reduced FY2025 soybean "
             "seed volumes by 9% in the Company's South American segment, and the Company "
             "extended $210 million of additional grower credit to affected customers to "
             "support next-season purchases.",
        driver="Precision-agriculture software subscriptions grew 41%, crossing 38 million "
               "enrolled acres, as adoption accelerated among mid-size North American grain "
               "farms.",
        note="Greenfield's FieldSense precision-agriculture platform is now used on "
             "approximately 38 million acres, up from 27 million acres in FY2024.",
    ),
    dict(
        name="Granite Peak Mining Co.", ticker="GPMC", sector="Metals & Mining",
        fy="2025", revenue="10.6 billion", net_income="1.84 billion", rev_change="+15%",
        employees="11,200", rd_spend="88 million",
        overview="Granite Peak Mining extracts and processes copper, lithium, and molybdenum "
                 "from four open-pit mines in Nevada, Arizona, and Chile.",
        risk="A tailings-dam stability review at the Company's Cerro Alto facility in Chile, "
             "prompted by a Chilean regulatory audit in FY2025, required $46 million of "
             "remediation work and a temporary 25% reduction in processing throughput for 10 "
             "weeks while reinforcement work was completed.",
        driver="Copper prices averaged 22% higher year over year amid tight global supply, "
               "driving the majority of revenue and net income growth despite flat production "
               "volumes.",
        note="Granite Peak's Cerro Alto facility in Chile accounts for approximately 31% of the "
             "Company's total copper production.",
    ),
    dict(
        name="Cornerstone Realty Trust", ticker="CRLT", sector="Commercial Real Estate (REIT)",
        fy="2025", revenue="3.4 billion", net_income="590 million", rev_change="+2%",
        employees="2,100", rd_spend="n/a",
        overview="Cornerstone Realty Trust is a REIT owning 214 office and mixed-use properties "
                 "concentrated in gateway US cities, with a portfolio focus on Class A office "
                 "space.",
        risk="Portfolio-wide office occupancy fell to 79.4% at fiscal year end from 85.1% a year "
             "earlier, and the Company recorded a $310 million impairment on three San Francisco "
             "office properties whose appraised values declined amid persistent remote-work "
             "trends.",
        driver="Growth in the Company's logistics and life-sciences property segments, which now "
               "represent 22% of net operating income, partially offset office-segment "
               "weakness.",
        note="Cornerstone's three impaired San Francisco properties had a combined pre-impairment "
             "carrying value of $890 million.",
    ),
    dict(
        name="Pathway Logistics Corporation", ticker="PWLG", sector="Freight & Logistics",
        fy="2025", revenue="19.7 billion", net_income="880 million", rev_change="+5%",
        employees="58,000", rd_spend="410 million",
        overview="Pathway Logistics operates a nationwide network of truckload, less-than-"
                 "truckload, and warehousing services, along with a growing parcel-delivery "
                 "division serving e-commerce retailers.",
        risk="A ransomware intrusion detected in the Company's warehouse-management systems in "
             "October 2025 disrupted order fulfillment at 19 distribution centers for "
             "approximately 60 hours; Pathway did not pay the ransom and restored operations "
             "from backups, incurring $37 million in incident-response and lost-throughput "
             "costs.",
        driver="Parcel-delivery segment revenue grew 27% following new contracts with two major "
               "e-commerce retailers, offsetting rate softness in the truckload spot market.",
        note="Pathway's warehouse-management ransomware incident in October 2025 affected 19 of "
             "the Company's 240 distribution centers nationwide.",
    ),
    dict(
        name="Cobalt Hospitality Group", ticker="CBHG", sector="Hotels & Hospitality",
        fy="2025", revenue="6.9 billion", net_income="510 million", rev_change="+9%",
        employees="33,000", rd_spend="n/a",
        overview="Cobalt Hospitality Group owns and franchises 1,180 hotels across upscale and "
                 "midscale segments under five brands, with concentrated presence in leisure and "
                 "convention-center markets.",
        risk="A data-privacy incident disclosed in FY2025 involving unauthorized access to a "
             "third-party reservations vendor exposed guest names, loyalty numbers, and partial "
             "payment card data for approximately 2.1 million guests across 140 franchised "
             "properties; the Company is named in four related class-action lawsuits.",
        driver="Revenue per available room (RevPAR) grew 7% as leisure travel demand remained "
               "resilient and the Company completed the conversion of 40 independent hotels to "
               "its branded flags during FY2025.",
        note="The FY2025 reservations-vendor data-privacy incident affected guests across 140 of "
             "Cobalt's 1,180 franchised properties.",
    ),
    dict(
        name="Helix Genomics, Inc.", ticker="HLXG", sector="Biotechnology",
        fy="2025", revenue="1.42 billion", net_income="-380 million", rev_change="+46%",
        employees="3,900", rd_spend="740 million",
        overview="Helix Genomics develops gene-editing therapies for inherited blood disorders, "
                 "with its lead product Zenovex (an ex vivo CRISPR-based therapy for sickle cell "
                 "disease) approved in the United States in FY2024.",
        risk="One of 340 patients treated commercially with Zenovex since launch experienced a "
             "delayed-onset secondary blood cancer in FY2025; the FDA has requested an updated "
             "long-term safety monitoring plan, and the Company voluntarily paused new patient "
             "enrollment for 45 days while the case was investigated, concluding it was unrelated "
             "to the therapy's editing mechanism.",
        driver="Revenue growth reflects the first full fiscal year of commercial Zenovex sales "
               "following its FY2024 approval, with 340 patients treated to date across 28 "
               "authorized treatment centers.",
        note="Zenovex has been administered to 340 patients across 28 authorized treatment "
             "centers in the United States since its FY2024 approval.",
    ),
    dict(
        name="Sentinel Cyber Defense Corp.", ticker="SNTC", sector="Cybersecurity Software",
        fy="2025", revenue="3.28 billion", net_income="340 million", rev_change="+21%",
        employees="7,800", rd_spend="620 million",
        overview="Sentinel Cyber Defense provides endpoint detection, identity threat "
                 "protection, and managed security monitoring to enterprise and government "
                 "customers.",
        risk="A supply-chain compromise of a widely used open-source logging library, disclosed "
             "industry-wide in FY2025, required Sentinel to patch and re-certify 96% of its "
             "customer-deployed sensor agents within a 30-day emergency window; the Company "
             "identified no evidence that its own systems or customer data were compromised.",
        driver="Growth was driven by a 38% increase in managed detection and response (MDR) "
               "subscriptions following expanded federal government contract awards.",
        note="Sentinel's federal government segment grew to represent 24% of total revenue in "
             "FY2025, up from 17% in FY2024.",
    ),
    dict(
        name="Harvest & Co. Foods, Inc.", ticker="HVCF", sector="Food & Beverage",
        fy="2025", revenue="17.9 billion", net_income="1.36 billion", rev_change="+2%",
        employees="52,400", rd_spend="290 million",
        overview="Harvest & Co. Foods manufactures packaged snacks, cereals, and frozen foods "
                 "distributed to grocery, club, and food-service channels across North America "
                 "and Europe.",
        risk="An avian influenza outbreak affected two contract egg-supplier farms used by the "
             "Company's frozen-breakfast division in FY2025, temporarily reducing egg-product "
             "input availability by an estimated 15% for the segment during the second fiscal "
             "quarter and requiring the qualification of three backup suppliers.",
        driver="Price increases implemented in late FY2024 continued to support margin "
               "expansion, though volume across the snacks portfolio declined 1.8% amid "
               "value-conscious consumer behavior.",
        note="Harvest & Co.'s frozen-breakfast division sources shell eggs from 11 contract "
             "farms, two of which were affected by the FY2025 avian influenza outbreak.",
    ),
]

def build_document(c):
    sections = [
        ("Item 1. Business Overview",
         f"{c['name']} (NASDAQ/NYSE: {c['ticker']}) operates in the {c['sector']} sector. "
         f"{c['overview']} For fiscal year {c['fy']}, the Company reported total revenue of "
         f"${c['revenue']} and net income of ${c['net_income']} ({c['rev_change']} year over "
         f"year revenue change). The Company employed approximately {c['employees']} people as "
         f"of fiscal year end and invested ${c['rd_spend']} in research and development during "
         f"the year."
         ),
        ("Item 1A. Risk Factors",
         f"Operational and Regulatory Risk. {c['risk']} The Company continues to monitor this "
         f"matter and has implemented corrective actions as described in Item 7. Investors "
         f"should consider this risk factor alongside general risks common to the "
         f"{c['sector']} industry, including competitive pressure, input cost inflation, "
         f"regulatory change, and macroeconomic cyclicality."
         ),
        ("Item 7. Management's Discussion and Analysis (MD&A)",
         f"Fiscal {c['fy']} revenue of ${c['revenue']} compared to the prior fiscal year "
         f"reflected a change of {c['rev_change']}. {c['driver']} Management believes the "
         f"Company's underlying operating trends remain consistent with its multi-year "
         f"strategic plan, and it continues to monitor the risk factor described in Item 1A "
         f"for further financial statement impact in future periods."
         ),
        ("Item 8. Financial Highlights",
         f"The following selected figures are derived from the Company's audited financial "
         f"statements for fiscal year {c['fy']}: total revenue ${c['revenue']}; net income "
         f"${c['net_income']}; year-over-year revenue change {c['rev_change']}; research and "
         f"development expense ${c['rd_spend']}; total employees {c['employees']}. These "
         f"figures should be read together with the notes to the financial statements below."
         ),
        ("Notes to Financial Statements",
         f"{c['note']} Except as otherwise noted, all figures in this report are presented on "
         f"a US GAAP basis for the fiscal year ended {c['fy']}. This report was prepared for "
         f"internal corpus-testing purposes as part of a retrieval-augmented generation "
         f"benchmark and is not an actual regulatory filing."
         ),
    ]

    # One section = one page. Keeps citations unambiguous: Page N <-> Section N.
    full_text_parts = [f"{c['name']} — Fiscal Year {c['fy']} Annual Report",
                        f"Sector: {c['sector']} | Ticker: {c['ticker']}",
                        "=" * 70, ""]
    for page_no, (heading, text) in enumerate(sections, start=1):
        full_text_parts.append(f"[[PAGE {page_no}]]")
        full_text_parts.append(f"## {heading}")
        full_text_parts.append(text)
        full_text_parts.append("")
    return "\n".join(full_text_parts)


def main():
    index_lines = []
    for c in COMPANIES:
        doc_text = build_document(c)
        fname = c["ticker"] + ".txt"
        path = os.path.join(CORPUS_DIR, fname)
        with open(path, "w") as f:
            f.write(doc_text)
        index_lines.append(f"{fname}\t{c['name']}\t{c['sector']}")
        print(f"wrote {fname} ({len(doc_text.split())} words)")

    with open(os.path.join(CORPUS_DIR, "_index.tsv"), "w") as f:
        f.write("filename\tcompany\tsector\n")
        f.write("\n".join(index_lines) + "\n")

    print(f"\nTotal documents: {len(COMPANIES)}")


if __name__ == "__main__":
    main()
