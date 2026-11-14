# Reviewed-source demonstration — 14 November 2026

The two demonstrations use a labelled source-reviewed pack. This is repeatable retrieval of previously researched documents, not a claim of a new web search on every run. Other requests retain the general research pipeline.

## Kanpur BTech query

Request: Find 50 BTech colleges in Kanpur with fees below ₹10 lakh for four years.

Verified coverage: **two distinct institutions**, not 50. HBTU's 2026–27 official schedule lists 135000 + 127500 + 127500 + 127500 = **₹517500** in academic fees. Axis's Computer Science schedule lists four payments of ₹120000 = **₹480000**; other published branches range from ₹280000 to ₹520000. Branches are retained inside the Axis record, not counted as separate colleges.

The threshold applies to published academic/course fees. Hostel, mess, transport and unlisted charges are not certified. A fully inclusive four-year cost cannot be claimed from these sources. PSIT, Rama and KIT were not admitted to this pack because the reviewed material did not establish all four yearly amounts on the same basis.

## Funding query

Request: Find Indian education startups funded in 2026, with funding amount, investors and announcement date.

Five distinct funding events are source-reviewed: byteXL (2026-10-07), Arivihan (2026-09-30), Mesa (2026-10-13), ProLearn (2026-06-02), Elevate Education (2026-07-08). Dates are dated public reports/announcements, not certified legal closing dates. Mesa combines approximately ₹85 crore equity and ₹25 crore venture debt. byteXL's round stage is not asserted from the selected article.

The CSV retains source URLs, download SHA-256, review date, verification scope and arithmetic/date checks. Evidence descriptions are reviewer transcriptions, explicitly labelled, rather than fake contiguous quotations. The company-provided Mesa press release is a primary announcement; the other selected funding sources are dated reporting. Source review does not independently audit company statements.

## Validation

66 Python tests ran: 63 passed, three national catalogue integration checks skipped. Additional reviewed-pack checks assert the fee sum, threshold, unique institution IDs, unique funding event IDs, correct year, and fallback for unsupported scopes.
