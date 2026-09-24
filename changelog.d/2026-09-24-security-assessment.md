## 2026-09-24 — Security assessment (commercial live-app standard): breach closed, critical holes fixed

- BACKUP-PRIVATE-1 (server): the nightly DB backups (users DB + CityLauncher prospects, 14 days, 31 files) were
  uploaded into the PUBLIC media bucket and downloadable by date from the r2.dev URL. Copied and verified into the
  private encrypted bucket (r2crypt:public_bucket_rescue_20260924) + Hetzner volume, then deleted from the public
  bucket with David's approval (probe: 404). /usr/local/bin/backup_dbs_to_r2.py now writes only to r2crypt:daily.
- UPLOAD-KEY-1 (bea_main.py _s3_upload): upload filenames could climb out of the media mirror (../) and, with the
  app running as root, write any file on the server. Keys are now reduced to safe characters, flattened to
  prefix/name, contained by realpath, and executable extensions are disarmed; non-image/pdf uploads are served as
  application/octet-stream.
- CONTENT-GATE-1 (security_gate.py step 7): user-written record fields (title, suburb, message ...) are plain text
  and photo fields are plain https links on every JSON answer, so stored markup cannot run in ms.js, quick.html or
  the admin console (covers the JSON-description bypass too). Stranger test PASS on the server venv (302 routes).
- AA-AUTH-1 (AdvertAgent, deployed): /ai/run, /ai/jobs, /ai/jobs/{id}, /ai/ledger take identity only from the
  signed-in session; examples are curated fixtures only. Probed: anonymous reads now 401.
- CL-AUTH-2 (CityLauncher, deployed): /orchestration/control (ran systemctl as root for anyone), status, kpi and
  pipeline reads now need the launch key or an enrolled device; LAUNCH_API_KEY rotated. Probed: 401.
- nginx: /quick/, /quick.html and /q/ now carry the security headers; /media/ is sandboxed + nosniff;
  server_tokens off; TLS 1.0/1.1 retired.
- SEC-ASSESS-2 (bea_main.py): PAY-AMOUNT-1 -- Tuppence top-ups (verify + webhook), seller plans and the wishlist
  plan are granted only when Paystack shows a ZAR charge of at least the asked price (metadata alone is set by
  whoever starts the transaction); SMS-CAP-1 platform daily SMS ceiling (SMS_DAILY_CAP, default 300);
  ADMIN-CEIL-1 master password compared in constant time with a platform-wide failure ceiling; enrol `next`
  refuses backslash redirects; uploaded .doc/.docx keep their names, SVG is never served as an image.
- Server: prod venv upgraded (Pillow 12.3, PyJWT 2.15, python-multipart 0.0.32, starlette 1.3.1 / FastAPI
  0.135.3, aiohttp, cryptography, urllib3, requests, idna, anyio): pip-audit 0 known vulns, stranger test 302/302,
  QA gate pass. AdvertAgent venv patched. BEA and strategist bound to 127.0.0.1. OS packages upgraded.
