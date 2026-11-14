# Demonstrating EkList

## Before presenting

1. Start the local server and open http://localhost:4174.
2. Import the institution workbooks if showing catalogue search. A fresh GitHub clone has no national dataset.
3. Configure NVIDIA and Serper locally for public research; do not display `.env` on screen.
4. Run a small public query to check provider access and network availability.
5. Check time-sensitive sources again on presentation day. Never show expired cached opportunities as currently open.
6. Keep `examples/subscribers-fictional.csv` available for an offline import demonstration.

## Five-minute walkthrough

### 0:00 — State the problem

“Useful lists are spread across spreadsheets and websites. Copying names into a table loses their sources, hides missing fields, and can merge different entities. EkList brings records and evidence into the same workspace.”

### 0:30 — Search local data

With the catalogue imported, ask `उत्तर प्रदेश के 50 कॉलेज दिखाओ`.
Show the interpreted filters and returned count. Explain that the model plans filters, while SQLite supplies the actual institution records. Open a record and show its original workbook row. Export the CSV.

If the catalogue has not been imported, start with the fictional CSV instead; do not claim the national rows are included in the repository.

### 1:30 — Show public-source assembly

Open Research → CSV and submit a narrow objective, for example:

> Find organisations working on rural education in Rajasthan and any explicitly documented university partnerships. Include source evidence and leave unsupported partnerships blank.

Show downloaded sources, extracted claims, and gaps. Inspect a relationship quote: co-mention alone may not prove a partnership. These are reviewable research candidates, not independently certified relationships. Download results and evidence CSVs.

### 2:45 — Show stricter opportunity checks

Choose Hackathons and request:

> Find online hackathons for college students based in India, age 20, with registration deadlines in the next 30 days.

Inspect the rule outcomes and published eligibility/deadline quotes. Explain Qualified, Needs verification and Excluded. Do not weaken conditions simply to increase the qualified count. A zero result is an honest result; use an explicitly dated previous run only as a historical demonstration.

### 3:45 — Demonstrate user-owned data

Open Subscriber studio and upload the fictional example. Review the shared-profile association, confirm only the intended group, and export. Show that all emails are preserved and that no active inbox is guessed.

For other datasets use Import CSV / XLSX, preview headers and map fields. Preserve original columns as evidence.

### 4:30 — Close on measurable behavior

Show actual input/output counts, source locators, duplicate decisions, unknown fields and CSV output. Explain that completeness, provenance coverage, matching precision and recall measure different things. Never describe an LLM confidence score as verified accuracy.

## If the network fails

- Use the imported catalogue and fictional CSV workflow.
- Reopen a persisted research run, explicitly stating when it was collected.
- Show download failures in gaps rather than replacing them with invented records.
- Do not describe a cached screenshot as a fresh live result.

## Questions judges may ask

**What is novel?**
The implementation combines local retrieval, bounded source downloads, field evidence, explicit gaps and domain-specific checks in one export workflow. Do not claim that entity resolution or research agents have never existed before.

**What does the AI do?**
It interprets natural language and extracts structured public claims. Code validates the structure, locates quotes, applies identity rules and evaluates supported eligibility conditions.

**How does ML.ai contribute?**
ML.ai is a development agent, not the runtime data source. Present only work it actually performed: ingestion adapters, debugging, tests or documentation, supported by its real changes. The current implementation attribution is in the README.

**Can it find any lead?**
The research schema accepts different entities and attributes, but retrieval coverage and verification are bounded. Jobs and hackathons have specific connectors and checks. General research output remains evidence-linked candidates.

**Is it production-ready?**
It is a working local prototype. Shared deployment needs authentication, isolation, rate limiting and operational controls.


## Recorded walkthrough

[Download the narrated video](assets/EkList-walkthrough.mp4). Edited captured screens, with live/local/historical labels.

- **0:00** — One question. One usable list. (live deployment)
- **0:16** — Search the real catalogue. (live deployment)
- **0:35** — Follow every source row. (live deployment)
- **0:51** — Hindi or English. Your choice. (live deployment)
- **1:08** — Opportunities, beyond jobs. (local development corpus)
- **1:31** — See the connection. Inspect the proof. (local development corpus)
- **1:45** — Claims with quotations attached. (local development corpus)
- **2:02** — Bring your own data. (synthetic example · local build)
- **2:20** — Qualification you can inspect. (historical saved run · local build)
- **2:39** — Search. Download. Extract. Export. (historical saved run · local build)
- **2:58** — Build on evidence. Start with EkList. (eklist.vercel.app)
