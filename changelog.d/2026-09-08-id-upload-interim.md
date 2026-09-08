## 8 Sep 2026 — ID-UPLOAD-INTERIM-1 (RUL-113): an ID upload earns 12 of 15 at once, the last 3 named as waiting

David, on the daily watch's one REAL ISSUES line (DW-109): *"lets fix this temporarily allowing the
upload without a verification; at least until i add credits to Didit. Until then allow the user 12
points for the upload with a note saying 'waiting confirmation to add an extra 3 points'."*

**Fault (DW-109, found 6 Sep):** the C2 rule of 16 Jul made an ID upload store the document, write a
`pending` credential and grant nothing — correct against the old +15 self-grant, but with the Home
Affairs lane parked (RUL-105, Didit unfunded) nothing was ever going to confirm an upload. So a 200
upload left `/id-status` reading **"No ID on file"** and the Trust card still offering **Upload ID →**.
David uploaded twice and was told the same thing twice.

**Fix (`bea_main.py`, `ms.js`, `migrations/038_id_upload_interim.py`):**
- `POST /users/{email}/upload-id` now calls `_grant_id_upload_interim`: the credential becomes
  `declared` with a `user_declarations` row of **12** points — the EXISTING partial-credit machinery,
  so the ONE scorer counts it and no surface hand-adds a number (EVIDENCE-TRUE). Idempotent: a second
  upload never doubles it; an `earned` credential is never touched. Response `status: "interim"`,
  `points_awarded 12`, `points_pending 3`, message *"ID received — 12 points added. Waiting
  confirmation to add an extra 3 points."*
- `GET /users/{email}/id-status` gains the **`pending`** state (document on file, unconfirmed) with
  `interim_points`, `pending_points` and `pending_note` — the branch that did not exist.
- `GET /users/{email}/trust` carries `partial_points 12` + the note on the ID row and the visible list
  still sums to the headline; `GET /sellers/credentials/{id}` lists the 12 as *"Government-issued ID
  uploaded — confirmation pending"*; `/trust-score/breakdown` counts the remaining 3 as pending.
- `ms.js`: the upload handler shows the note and re-renders from `/trust`; the Trust card row renders
  ◐ `+12 · 3 pending` with the note and stops offering **Upload ID →** over a document already on file;
  the Home Affairs card leads with the same line.
- Migration 038 converts the two uploads made before this shipped (the walkthrough account and one
  tester) from `pending` to `declared/12`. Dry-run + apply proven on a copy of the live database:
  2 converted, re-run 0.
- `ID_UPLOAD_INTERIM_POINTS` (env, default 12) is the ONE switch; `0` restores the C2 no-grant
  behaviour. Reversing it is David's call (RUL-113(c)), never a session's reading of "temporary".

**Proven before shipping** on the server's own interpreter against a copy of the live database:
id-status `pending` with the note for both accounts; `/trust` visible sum == headline; breakdown
`pending_points 3`; public list carries the 12; grant idempotent; earned untouched; a seller with no
upload still reads `none`. Asserted by **RG-0347 (LOCKED)** — source legs for every surface plus a
live anonymous read of the walkthrough account, which must never again read `none`.
