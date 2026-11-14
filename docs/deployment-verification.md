# Deployment preparation verification — 14 November 2026

These checks ran locally using the hosted-mode Python server and the exact Node handler configured for the Vercel API bridge. They are **not** evidence of a deployed Render or Vercel service.

| Check | Observed result |
|---|---|
| Restore compressed catalogue after checksum validation | 74,847 source rows |
| Hindi UP college query through authenticated bridge | 50 real catalogue entities |
| Fictional subscriber CSV import through bridge | 4 input records |
| Anonymous bridge request | HTTP 401 |
| Direct backend request without server token | HTTP 403 |
| Hosted private-file shortcut | HTTP 403 |
| Live Remotive + NVIDIA job run | 16 exported listings; partial status |
| Live NVIDIA/Serper public research | 5 exported rows; 5 downloaded sources; partial status |
| Provider/source metrics for research | 6 model calls, 2 search calls, 33 rejected extractions |
| Python suite with development catalogue enabled | 56 passed |
| JavaScript suite including bridge tests | 14 passed |
| Static frontend build script | Completed |

Partial results retain gaps and unknown criteria. The jobs CSV includes all categories; 16 exported listings does not mean 16 qualified jobs. Research rows remain unreviewed source-backed candidates.

A browser loaded the static UI through the local bridge test server, but authenticated browser interaction was not completed: the automation could not complete its native HTTP authentication navigation. The HTTP/API pipeline and exports were tested programmatically. Actual cloud build, cold-start seed retrieval, browser login and deployed end-to-end verification remain pending the owner's service setup.

The catalogue restore test used the prepared local gzip archive. The owner's eventual external archive URL still needs testing. A Docker image build was not run in this verification.
