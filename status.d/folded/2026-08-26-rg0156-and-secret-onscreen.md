## 2026-08-26 — Orchestrator locked, secret-at-rest class closed

RG-0156 **LOCKED**: orchestrator.html is in the deploy manifest, the client-side access code is
gone (it gated nothing — nginx 401s anonymously, which is the real gate), a failed feed now says
FEED UNAVAILABLE instead of five cheerful empties, and the health badge has a grey unmeasured
state. Four presence assertions added so the fix cannot be silently removed.

RG-0189 **LOCKED** (SECRET-ONSCREEN-1): no file under `.secrets/` may hold 2+ credentials at rest,
and secret entry no longer requires a GUI. Built `add_secret.bat` and
`scripts/split_rotated_secrets.py`; rewrote `ROTATE_SECRETS.bat` so the dump is transit-only and
credential backups self-prune.

RG-0188 back to **OPEN** — an empty placeholder token file had falsely flipped it to READY TO LOCK.
Presence is not runnability; the assertion now says so.

RG-0160 is **not a build job**: the dossier PDFs exist and are wired; one `media_push.bat` run
closes it.

Ledger 182 · 159 holding · 2 REGRESSED (RG-0125, RG-0154 — both clear on the 27 Aug ship) · 19 open.
