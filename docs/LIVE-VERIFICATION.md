# Live verification — 14 November 2026

Frontend: https://eklist.vercel.app  
Backend: https://eklist-api.onrender.com

## Observed live flows

| Flow | Observed result |
|---|---|
| Public opportunity library | 80 source-scoped records returned by the deployed API |
| Delhi catalogue | 50 institution results; original source records inspected |
| Hindi catalogue | Uttar Pradesh college query returned the local directory |
| Research library filter | 24 candidates; one matched the requested Summer Research name condition; graph and deadline quote inspected |
| Paid remote jobs for India | 4 qualified, 7 needing verification, 5 excluded |
| India-eligible online hackathons, age 20, next 30 days | 1 qualified, 6 needing verification |
| Rajasthan rural-education organisations | 10 candidates, 5 saved sources, 19 claims; missing university partnerships stayed blank |
| Fictional subscriber CSV | 4 input rows; one association group containing 3 rows; manual identity decision and CSV export control exercised |
| Generic CSV import | 3 fictional rows imported through column preview and mapping; export control exercised |

The downloaded job CSV contained 4 rows; hackathon CSV 1 row; NGO result CSV 10 rows; NGO evidence CSV 19 rows; library CSV 24 rows. The library export includes candidates and their statuses, not just matches. Catalogue and imported-list export controls displayed success, but their browser-generated downloads were not independently saved by the automation.

## Limits

These are observed run results, not an accuracy benchmark. Qualification means the implemented checks passed against retrieved evidence at that time. Feeds may lag; deadlines and vacancies change. NGO candidates still require review; shared page context does not certify an organisation or partnership. The library is an initial evidence corpus, not 80 currently open opportunities. Original catalogue fields may contain source errors.

Free Render storage is ephemeral. The catalogue seed and bundled public opportunity seed restore the initial corpus, while newly created research histories can disappear on restart. Presenter sign-in uses the existing deployment credentials for provider-powered workflows and uploads. Public catalogue and pack browsing do not require sign-in.

## Repeat the demo

1. Open the live workspace and sign in with the configured presenter account.
2. Ask “Find 50 colleges in Delhi”; inspect a source record and export.
3. Switch Hindi and ask “उत्तर प्रदेश के 50 कॉलेज दिखाओ”.
4. Browse the 80-record library; filter research records, inspect a quote and graph, then export.
5. Run the remote-jobs or hackathon query above; open qualification checks before downloading the qualified CSV.
6. Run the Rajasthan NGO query; inspect evidence and missing fields; export results and evidence separately.
7. Import `examples/general-import-fictional.csv` through column preview and mapping.
8. Demonstrate subscriber associations with `examples/subscribers-fictional.csv`, explicitly mapping its profile columns.

## Automated checks

17 JavaScript tests passed. Python ran 61 tests: 58 passed and 3 catalogue integration tests skipped. The public seed restoration test verifies 80 records and idempotent re-running.
