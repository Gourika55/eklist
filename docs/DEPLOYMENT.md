# Vercel frontend + Render backend

## Architecture

Browser → Vercel static UI → authenticated `/api/*` bridge → Render Python server → catalogue / jobs / source snapshots.

NVIDIA and Serper keys exist only on Render. Vercel holds a separate backend access token. A shared demo login protects API use and shared research history. This is a single shared demo workspace, not per-user tenancy: everyone with the login can inspect its research runs. Do not use it for confidential multi-user work.

## Free-tier boundary

The supplied `render.yaml` uses a **free** web service, with no paid disk. Render can sleep the service; local files are ephemeral across restart/redeploy. A trusted compressed catalogue seed is restored at startup, but research runs, evidence downloads and caches are temporary. An interrupted research job is not guaranteed to resume. Never describe this setup as durable hosting.

For durable local research history, upgrade the backend and mount a persistent disk at `/app/data`. Keep one backend instance; this SQLite/threaded implementation is not designed for multiple instances. A separate managed database/object store is an alternative, but that migration is not implemented here.

## 1. Store your catalogue seed

The development workspace provides `eklist-deploy/catalogue.sqlite.gz` (institution catalogue only) and `catalogue.sha256`. Private subscriber data, provider keys and research history are not in that file.

Upload the archive to storage you control and obtain a **direct HTTPS download URL**. The URL must return the gzip bytes, not a login or HTML sharing page. Prefer a private object with a long-lived scoped download URL. A short-lived URL must be refreshed before it expires, or the next cold start will fail. Check your source redistribution permissions before making the archive public. Do not commit the seed or private download URL to GitHub.

The SHA-256 of the prepared development archive is:

```text
0edf5b1971b0515d6aa5200a2391a4096e42b8a1575b05d5a918284aad522aec
```

If you rebuild/recompress the archive, use its newly computed SHA-256. Startup checks the hash, SQLite integrity and required catalogue tables before installing it. Existing populated catalogues are retained rather than overwritten.

## 2. Create the Render service

1. New → Web Service → connect `Gourika55/eklist` → branch `main`.
2. Runtime: **Docker**. Dockerfile: `./Dockerfile`. Service name: `eklist-api` (or your preferred name). Select **Free**.
3. Set health check path to `/healthz`.
4. Add these environment variables:

| Name | Value |
|---|---|
| `EKLIST_HOSTED` | `1` |
| `NVIDIA_API_KEY` | Your NVIDIA key |
| `SERPER_API_KEY` | Your Serper key |
| `EKLIST_MODEL` | `nvidia/nemotron-3.5-super-vl-120b-a12b` |
| `EKLIST_BACKEND_TOKEN` | A new random secret of at least 32 characters |
| `EKLIST_CATALOG_SEED_URL` | Direct HTTPS archive URL from step 1 |
| `EKLIST_CATALOG_SEED_SHA256` | The archive hash above |

Generate a separate backend token locally with `openssl rand -hex 32`. This is not your GitHub password or either provider key. Keep it for Vercel configuration too.

Render supplies `PORT`; the server listens on `0.0.0.0` in hosted mode. Docker includes `pdftotext` for PDF extraction.

5. Deploy. Logs should show `Catalogue restored: 74847 source rows` for the supplied seed, followed by server startup.
6. Copy the resulting `https://YOUR-SERVICE.onrender.com` URL. `/healthz` should return `{"status":"running"}`. This liveness endpoint intentionally exposes no records or provider status. Direct `/api/catalog` requests without the backend token should return 403.

Alternatively, import `render.yaml` as a Blueprint; review that it selects the free plan and supply the missing environment values. Creating the service is your action; no service has been provisioned merely by committing this file.

## 3. Import the Vercel project

1. Import `Gourika55/eklist`, branch `main`.
2. Root directory: repository root. Framework: **Other**.
3. `vercel.json` supplies build command `node scripts/build-frontend.mjs` and output directory `public`. Do not set the project root to `dist`: that would omit the API bridge.
4. Set these Vercel environment variables for Production (and Preview if you use previews):

| Name | Value |
|---|---|
| `EKLIST_BACKEND_URL` | The HTTPS Render service URL, without `/api` |
| `EKLIST_BACKEND_TOKEN` | Exactly the same backend token as Render |
| `EKLIST_DEMO_USER` | A demo username of your choice |
| `EKLIST_DEMO_PASSWORD` | A separate strong demo password |

Do not prefix these variables with `NEXT_PUBLIC_` or put them in browser code. Do not set `EKLIST_PROXY_LOCAL_TEST` in hosting environments.

5. Deploy. Visit `https://YOUR-PROJECT.vercel.app/api/health` first, enter the shared demo login in the browser's authentication prompt, then open the homepage. The health JSON must show `database: true`, `records: 74847`, `ai: true`, and `serper: true` for this dataset and configured keys. Provider booleans mean configured, not a successful live provider call.

Changing environment variables requires a new Vercel deployment.

## 4. Verify the complete deployed flow

Run `scripts/smoke-hosted.py` with these local environment variables:

```sh
export EKLIST_SITE_URL=https://YOUR-PROJECT.vercel.app
export EKLIST_DEMO_USER=your-demo-user
# Set EKLIST_DEMO_PASSWORD privately in your local shell.
python3 scripts/smoke-hosted.py
```

The smoke check verifies authentication, real catalogue query, fictional CSV import, research job start/polling and CSV export. It uses real provider calls and can spend API credits. It fails if research produces no result rows. Network availability, source content and model behavior can change; inspect the output rather than assuming a previous run proves current success.

Then verify in the browser:

- Query 50 UP colleges; inspect source rows and export CSV.
- Run a research request; inspect evidence and download results.
- Run jobs/hackathons; verify checks and deadline evidence, not merely a nonzero row count.
- Refresh and reopen a completed run while the backend is running.
- On free Render, demonstrate the documented loss of job history after a service replacement; the seed restores only the institution catalogue.

Share both deployed URLs to have the actual hosted path checked. Local bridge tests are not cloud deployment tests.

## Limits and troubleshooting

- **First request slow / 502:** free Render may be cold. Open Render `/healthz`, wait for startup and retry. The bridge times out after 55 seconds; background research uses short submit/poll requests.
- **Render deploy fails during seed load:** wrong hash, expired URL, HTML instead of gzip, or wrong SQLite tables. Fix the URL/hash; do not bypass the check.
- **401:** the demo username/password is missing or incorrect.
- **403:** Vercel and Render backend tokens differ, or a private-file shortcut was requested (disabled in hosted mode).
- **503:** Vercel bridge configuration is incomplete or backend URL is not HTTPS.
- **No catalogue:** do not display fake counts. Verify the seed import and `/api/health` record count.
- **Large uploads:** Vercel Functions have a platform request-size limit. The bridge rejects bodies above 4,000,000 bytes; split XLSX inputs to roughly 2.8 MB before base64 encoding. Local-mode 5 MB upload support does not imply the same hosted limit. Very large exports can also exceed platform response limits; narrow the query/export.
- **Private data:** do not upload your private contact source file to the Render image. The local-file shortcut is blocked. Normal user CSV import still works within request limits.

References: [Render free services](https://render.com/docs/free), [persistent disks](https://render.com/docs/disks), [port binding](https://render.com/docs/web-services#port-binding), [Vercel Function limits](https://vercel.com/docs/functions/limitations).
