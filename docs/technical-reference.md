# Technical reference

Historical local-workspace measurements below are not bundled datasets or freshly rerun live-source claims. See the main README for clean-clone setup.

EkList turns a Hindi/English institution request, or user-uploaded tables, into a traceable working list. It provides a national institution catalogue, general CSV/XLSX reconciliation, and a separate subscriber profile-review workflow. It does not certify the truth of a source or discover private identities from the web.

## Run

Python 3.11+ and a modern browser are sufficient for the application. Node 18+ runs the frontend tests.

```sh
PORT=4174 python3 server.py
```

Open http://localhost:4174. The server binds to loopback only. Keep this terminal running for the demo. Do not host this server on the public internet without adding authentication, request throttling, deployment configuration and proper data-access controls.

The current workspace already has the imported SQLite database and local credentials. Credentials are in ignored `.env`, never browser code or the handoff archive. For a fresh copy, fill `.env` using `.env.example`. No key is required when the NVIDIA checkbox is disabled. The private contact CSV is not included in the archive; use the upload workflow instead.

## Data actually integrated

| Imported file | Source rows |
|---|---:|
| Colleges | 54,574 |
| Universities | 1,438 |
| Standalone institutions | 17,092 |
| R&D institutes | 291 |
| PM Vidyalaxmi | 1,452 |
| Total | 74,847 |

There are 73,401 distinct AISHE codes, not 74,847 distinct institutions. The exports state November 14, 2026; that is an export label, not a per-record verification date. State labels are retained as supplied; do not interpret their raw distinct count as a count of current Indian states.

`python3 ingest.py` rebuilds the catalogue from the five specifically named XLSX files in Downloads. This replaces the generated institution database, not source files. Source filename, original row, original values and file SHA-256 are preserved. The workbook source URL was not supplied, so no per-record official URL is invented. Websites listed in records remain source claims.

## Three usable workflows

### Institution requests

Examples: `Find 50 colleges in Delhi`, `उत्तर प्रदेश के 50 कॉलेज दिखाओ`, `Find 100 universities in India`, `Find 50 research institutes in India`.

NVIDIA `nvidia/nemotron-3.5-super-vl-120b-a12b` proposes JSON filters. The backend validates category, state, district, count, management and website requirements. Parameterized SQLite queries retrieve real records. Results are alphabetical, not a ranking. Maximum 500 entities per query; all 74,847 source rows remain searchable. There is no automatic all-India download through the UI.

A returned AISHE code retrieves all its source records. Source disagreements remain available. Code links identifiers; the model never generates institutions. The initial page load deliberately uses rules, so merely opening the app does not spend model tokens. Query-plan caching is memory-only. Invalid model output is rejected; provider failures may use an explicitly labelled rules fallback. Review the displayed filters.

### Any user-supplied table

Choose **Import CSV / XLSX**, select a file, choose the header row, preview the columns, map fields, and optionally enter its source URL. Choose whether to append to current results or replace the working list. Multiple files can be imported sequentially.

Supported mappings: name, shared entity ID, state, district, website, email, phone, address, category and source URL. Unmapped values remain in the original-record evidence. XLSX uses its first worksheet. File size limit: 5 MB; combined working-list limit: 5,000 records. The table displays the first 100 matching rows; use search to narrow it and export to obtain all rows. Existing national datasets use the dedicated importer, so the UI limit does not reduce catalogue coverage.

AISHE-style codes get a consistent namespace. Other identifiers must already be genuinely shared, preferably prefixed with their source namespace. A row number is not identity. Missing names are flagged through an explicit placeholder. Phone/address/name matches suggest review; they do not prove identity. Large lists use bounded candidate blocking (first 50 records per non-ID block), so possible-match recall is limited and not claimed complete.

### Subscriber CSV

Choose **Subscriber studio → Upload subscriber CSV**. Map email, name, personal LinkedIn/X URL, company, role and country where present. Only email is required; without usable profile associations, records stay separate. Up to 50,000 rows / 5 MB.

The matcher normalizes regional LinkedIn hosts, trailing slashes and tracking parameters, and maps twitter.com/x.com to one profile form. Personal-profile patterns are required; generic LinkedIn company pages do not count. Country disagreements do not block association. No country-resolution workflow is performed.

Shared-profile groups are candidates: enrichment could have attached the wrong profile. Confirm same person or keep separate; decisions are reversible within the session. Download the subscriber list CSV: confirmed groups become one row containing all emails; unconfirmed records and singletons remain separate. No email is automatically selected as active. The supplied contact data has no required engagement, bounce or consent events for that decision.

A fictional four-record example is provided in `examples/subscribers-fictional.csv`. It is not presented as independently discovered real data. The private local file contains 10,316 rows; the current algorithm found 12 candidate groups covering 46 rows. It is never sent to NVIDIA or Serper. Private-file shortcuts are for this local machine only. Uploaded data is not written to disk by the import endpoint; it remains in process/browser memory and user-triggered exports.

## Search as last resort

Local catalogue retrieval is always first. **Search official sources · Serper** makes one bounded search only when clicked; ordinary catalogue requests make zero Serper calls. Searches request five results and are cached in server memory for one hour. UI labels actual search calls and cache hits. No unmeasured cost-saving percentage is claimed.

Search results are discovery links/snippets, not automatically accepted facts. Use **Upload downloaded data** in that dialog after obtaining a CSV/XLSX from the source. PDFs/HTML can be retained as supporting evidence, but generic PDF-to-table upload is not implemented. Search does not automatically crawl arbitrary websites or enrich private contacts.

## Research source packs

`data/source-packs.json` records 27 attempted sources: 20 institution home/contact-page snapshots and two historical DU admission bulletins downloaded; five source requests failed. There are dedicated contact-page captures where discoverable, otherwise the homepage snapshot is retained. Email extraction is regex-based candidate extraction, not deliverability or independent verification.

Seventeen catalogue identities matched uniquely to captured website hostnames. These are attached as supporting evidence in the record drawer. Ambiguous website hosts are not auto-associated. DU admission bulletins cover 2024–25 and 2025–26. They are not complete historical institution master lists; absence is not interpreted as closure. Snapshots retain URLs, retrieval timestamps and hashes. Their redistribution licenses have not been established; the handoff is a local research bundle, not a public data release.

## Matching and measurements

Production catalogue auto-linking uses exact AISHE identifiers. Fuzzy name comparisons only create review candidates. Subscriber association uses explicit normalized profiles and requires user review for final list consolidation. Original records survive merging.

`python3 scripts/benchmark.py` records a reproducible identifier-labelled benchmark and local performance measurements in `reports/benchmark.json`. It samples 500 same-ID pairs and 500 different-ID hard negatives, with seed 17. IDs are withheld from the evaluated name/location candidate function. Labels come from source identifiers, not an LLM, but they are not independent human audits. The candidate function is evaluation-only, distinct from production exact-ID linking.

Current proxy results: 420 true positives, 0 false positives, 80 false negatives, 500 true negatives; precision 100% and recall 84% on this sample. Exact-name baseline recall: 72.6%. Do not advertise this as 100% real-world accuracy. Some source-family overlaps are easy; identifier labels can contain errors. A held-out human-reviewed identity benchmark remains outstanding.

Current database performance: 25 query runs, median about 50 ms; maximum about 533 ms including cold evidence-index initialization. AI and network time excluded. This is not a multi-user load test. Query timings are displayed live and will vary by machine.

## Validation

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
npm test
python3 scripts/benchmark.py
```

Tests cover Hindi/count parsing, import totals, state filters, invalid plans, provenance, profile normalization, no name-only subscriber linking, CSV mapping, malformed files, geographic conflicts and safe exports. Browser checks cover NVIDIA Hindi query, real-record CSV export, evidence drawer, private-file aggregate view, subscriber CSV import/confirmation/export and XLSX header mapping/import.

## Demo script

1. Show the national dataset counts and ask for 50 UP colleges in Hindi.
2. Show the parsed filters, NVIDIA engine, result count, local query time and zero search calls.
3. Query Delhi; open Acharya Narendra Dev College to show original source rows and supporting official-site evidence.
4. Export CSV, then show the general import workflow using the R&D workbook (header row 3).
5. Open the fictional subscriber CSV, confirm the three-email group, and export two final rows from four input rows.
6. Show the measured-results panel with its evaluation limitations. Demonstrate Serper only when additional evidence is needed.

## Engineering attribution and limits

This implementation was built with Codex. ML.ai was opened earlier and inspected files, then stopped at the user's request. No ML.ai implementation contribution is claimed. Both provider integrations have been exercised with public queries. API credentials are server-side and excluded from git/archive; no private records were sent to external providers.

This is a functional local prototype, not a production multi-user platform. It does not certify recognition/affiliation, current contact ownership, active inboxes or complete geographic coverage. No generic PDF/HTML table-upload ingestion, automatic verified web enrichment, persistent subscriber-review storage, distributed search, or independent human accuracy certification is claimed.

## Public research → evidence-backed CSV (new)

Open **Research → CSV** or the Research Workspace. Enter an objective across domains, such as space missions and launch dates, organisations and programmes, or institutions and public partnerships. The new workflow runs alongside the existing institution/subscriber/import features.

- Persistent background jobs in `data/research.sqlite`, with additive entity, claim, evidence and source-document tables. No migration or replacement of the national catalogue.
- A strict institution query uses the existing catalogue when supported. Other requests use a flexible NVIDIA-generated field plan, up to two Serper searches and six public downloads.
- The backend downloads public HTML, text, CSV, XLSX and text-based PDFs itself. `pdftotext` is required for PDFs. Up to 3 MB per source, first worksheet for XLSX, first 22,000 extracted characters per document are passed to NVIDIA. Truncation/failures appear in gaps. No OCR or authenticated crawling.
- Downloaded bytes are stored by SHA256 in `data/research-sources/`; parsed source text and timestamps persist in SQLite. Private subscriber files and user imports are not sent to research providers.
- An attribute must have an exact located quote containing the subject name and extracted value. Relationship quotes must contain both names. These deterministic checks establish textual provenance only; the model's interpretation and relevance remain **unreviewed**, not independently verified. Co-mention can still be misinterpreted; inspect evidence before relying on relationships.
- Same names across web sources remain separate rather than being automatically merged. Exact AISHE codes still link catalogue records. The research layer does not yet implement cross-source fuzzy identity review or persistent claim acceptance.
- Dataset, evidence explorer and clickable relationship adjacency view are available. This is a SQLite-backed evidence graph, not a separate Neo4j deployment or general-purpose multi-hop query engine.
- Download `results.csv` (up to requested count), `entities.csv`, `claims.csv`, `evidence.csv`, `sources.csv`, and `gaps.csv`. All candidates are retained in the supporting exports. Missing requested values remain blank. A row is a source-backed candidate, not certification that all query criteria are met.
- Jobs survive page refresh. A server restart marks unfinished jobs interrupted, preserving partial evidence. One research job runs at a time. Recent jobs can be reopened.
- Public-network addresses are checked on each redirect; connections are pinned to the checked IP, HTTPS certificates remain verified, and response/expanded-workbook limits are enforced. Research text is treated as data, not executable instructions.

API: `POST /api/research/jobs` with `{ "query": "..." }`, poll `GET /api/research/jobs/{id}`, download `GET /api/research/jobs/{id}?export=results` (or the other export kinds). `GET /api/research/jobs` lists recent runs. Public research uses the configured NVIDIA and Serper credentials; local institution retrieval is preferred when the strict planner can fully represent the request.

## Remote jobs and hackathons

The **Opportunity Intelligence** workspace adds two domain-specific workflows without replacing the institution, research, import or subscriber tools.

- **Remote jobs:** documented Remotive active-jobs API, up to 100 returned records, source attribution and canonical Remotive links. Six-hour disk cache respects its recommended maximum four retrievals/day. Remotive states that its feed is delayed by 24 hours. Active status is a publisher claim, not employer confirmation. No third-party job-board redistribution or signup gates.
- **Hackathons:** A curated organiser URL registry, targeted discovery and Hack Club's public Event microdata directory. One bounded Serper search fills source gaps. Up to eight organiser pages, first 26,000 characters each. No 403/authentication bypass. Directory pages are not accepted as individual listings.
- NVIDIA interprets Hindi/English into visible typed conditions. Unsupported constraints are shown and prevent automatic qualification; experience, minimum-salary and detailed timezone matching are not implemented. India is the supported country filter; worldwide and explicit India statements qualify, broad APAC or unspecified exception lists remain unknown.
- Qualification is deterministic over published fields: PASS, FAIL, UNKNOWN, CONFLICT. Qualified means the explicit requested checks passed, not verification of the employer/organiser or a guarantee of acceptance. Eligibility text extracted from pages remains subject to model omission or semantic error; exact quotes prove provenance only.
- Registration, submission, application and event-start dates are distinct. Timezone-bearing dates are compared against the runtime UTC clock. Date-only deadlines clearly in the past are rejected; ambiguous boundary dates remain unknown. Publication date is not a deadline. Event end does not become registration end.
- Missing salary, missing registration status, broad geographic eligibility and omitted age remain visible. Age constraints are checked when published. Source caveats about payment to access work are flagged for review. Arbitrary employment/eligibility requirements cannot all be certified from these connectors.
- Exact source IDs or canonical URL + edition start deduplicate. Different requisitions/editions remain separate. Conflicting values are flagged and original evidence preserved. Name-only fuzzy cross-board identity matching is not implemented. Duplicate decisions export separately; no opportunity-specific manual merge UI yet.
- Search/filter Qualified, Needs verification, Excluded or All. Inspect rule outcomes and supporting source field paths/quotes. Download complete category CSVs plus evidence, duplicate decisions and gaps. Text search also filters result-category CSV exports; evidence and audit exports retain all records.
- Runs and source snapshots persist locally in `data/opportunities/`. API: `POST /api/opportunities` with `{kind:"jobs"|"hackathons",query:"..."}`, `GET /api/opportunities/{id}`, `?export=qualified|needs_verification|excluded|all|evidence|duplicates|gaps`. Two concurrent runs maximum; restart marks unfinished runs interrupted. No private uploaded/subscriber data goes to these providers.

Source documentation: https://github.com/remotive-com/remote-jobs-api and https://github.com/hackclub/hackathons . Source coverage is bounded, not exhaustive. Review recorded source restrictions before redistributing data.

## Repository distribution

This repository contains application code, tests, and fictional examples. Local institution databases, downloaded source snapshots, private contacts, credentials, and workspace reports are excluded. Import your source workbooks to populate the catalogue. Use CSV upload for contacts, or configure EKLIST_PRIVATE_CONTACTS_PATH locally.
