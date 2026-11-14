# Opportunity library

The local library adds seven clusters alongside the existing catalogue, research and opportunity flows. `/api/packs` reports coverage; `/api/packs/records` returns records and exports CSV with evidence. `/api/packs/query` uses the configured model to propose a validated filter plan. Unknown conditions remain reviewable.

Refresh registered official sources with `python3 scripts/refresh-packs.py`. Import downloaded public snapshots with `python3 scripts/import-local-packs.py /absolute/manifest.json --root /absolute/project`. Add `--audit-only` to check hashes and text without model calls. Files need not be staged in Git. Never commit private uploads or credentials.

Local imports verify SHA-256 before extraction, preserve retrieval dates, and reuse downloaded content. Record identity is source-scoped. Same-name cross-source records remain candidates, not automatic merges. Exact quotation checks establish provenance, not independent semantic accuracy. Extraction is bounded (first 24,000 characters, up to eight proposed records per current request), so counts are not exhaustive source totals. Empty documents and rejected claims do not become opportunities. Eligibility, deadlines and relationships may remain unknown or unreviewed.

Snapshots and `data/packs.sqlite` are local artifacts, excluded from Git. A fresh hosted backend must refresh the registered sources or import its own mounted corpus; deploying code alone does not transfer local data. Commercial reuse permission is not assumed.

Verification: 60 Python tests passed with the national catalogue enabled; 14 JavaScript tests passed. Browser checks covered Hindi labels, Hindi URL persistence and removal of the requested explanatory paragraph. This is not a measured real-world extraction accuracy benchmark.
