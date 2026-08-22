# SECRETS REGISTER — every credential, its holder, and when it was last verified

Born 22 Aug 2026 during the DW-029 / DW-057 rotation. The exposure register had been
counting eight credentials for fifteen days; the box actually carried nine more in a
world-readable file. This register exists so the count can never be a guess again.

**Rule:** every credential has a row. Every row carries a STATUS and a dated
verification saying HOW it was checked. `python3 scripts/regression_ledger.py`
asserts this file is current (RG-0146). Never delete a row — supersede it.

STATUS values: `ROTATED` (replaced and probed since exposure) · `BURNT` (exposed,
still live, not yet replaced) · `REMOVED` (deliberately unset) · `PUBLIC` (not secret
by design) · `UNKNOWN` (not yet established — treat as burnt) · `UNROTATABLE-ACCEPTED` (exposed, cannot be replaced by any means the vendor offers; carries a dated decision and its reasoning, never a silent pass).

REGISTER_VERIFIED: 2026-08-22

## Rotated and proven — 22 Aug 2026

| Credential | Holder | Rotated | Verified how |
|---|---|---|---|
| MS_ADMIN_KEY | secrets.env (0600) | 05:54 | ROTATE_SECRETS.bat, service healthy after restart |
| MS_DEPLOY_KEY | secrets.env (0600) | 05:54 | same run; local `.secrets/deploy_keys.txt` updated to match |
| MS_MAINT_KEY | secrets.env (0600) | 05:54 | same run; local `.secrets/ms_maint_key.txt` updated to match |
| MS_ADMIN_PASSWORD | secrets.env (0600) | 05:54 | same run |
| LAUNCH_CODE_SECRET | secrets.env (0600) | 05:54 | same run |
| RESEND_API_KEY | resend.conf (0600) | 06:01 | PROBED: empty-body send probe returned 422 (auth passed). Both old keys deleted in the Resend dashboard |
| PAYSTACK_SECRET_KEY | paystack.conf (0600) | ~06:20 | PROBED: `GET /transaction/totals` returned 200. Old key killed by Paystack at roll |
| PAYSTACK_WEBHOOK_SECRET | paystack.conf (0600) | ~06:20 | same value — Paystack signs webhooks with the secret key |
| MS_JWT_SECRET | secrets.env (0600) | ~06:40 | PROBED: fingerprint changed ec305410 -> 7fc37454, /health 200, reviewer cookie re-minted |
| GMAIL_APP_PASSWORD | gmail.conf (0600) | 09:5x | PROBED: **SMTP LOGIN ACCEPTED** — a real 16-lowercase-letter app password. First time this fallback has EVER authenticated |
| ANTHROPIC_API_KEY | anthropic.conf (0600) + local `.secrets/ai_keys.env` | 09:4x | PROBED: `GET /v1/models` returned 200. Burnt key identified as **`david-api-key`** (`sk-ant-api03-0Bz...`, on the box since 14 Jul) by matching the server's own backup against the console hint — NOT by guessing from names. Deleted, along with the orphaned `marketsquare-maintenance`. Survivors: `trustsquare-2026-08-22-b`, `marketsquare-video-reports`, `Haiku AdvertAgent` |
| HETZNER_S3_ACCESS_KEY + HETZNER_S3_SECRET_KEY | hetzner_s3.conf (0600) | 10:0x | PROBED: real `ListObjectsV2` against `marketsquare-media` succeeded. **THE NAME LIES — these are CLOUDFLARE R2 credentials**, endpoint `2026215991ebbdad051b8ef569d622aa.eu.r2.cloudflarestorage.com`. New token is scoped to the media bucket ONLY (was account-wide), so a future leak cannot reach `trustsquare-backups`. Old Cloudflare token `MarketSquare Media` still to be deleted |
| CF_CACHE_TOKEN | cloudflare.conf (0600) | 10:4x | PROBED: **a real cache purge against `trustsquare.co` succeeded**. New token `trustsquare-cache-purge-2026-08-22` is scoped to that ONE zone and Cache Purge ONLY — the old token also carried DNS Write, which nothing in the code uses. Old `Trustsquare Cache Purge` token to be deleted |
| NUMISTA_API_KEY + JUSTTCG_API_KEY | zz-catalog-keys.conf (0600) | 11:4x | PROBED: Numista `/api/v3/types` returned 200 (58 matches) with its `Numista-API-Key` header; JustTCG `/v1/cards` returned 200 with `x-api-key`. Both were defined in `datakeys.conf` in systemd's QUOTED form, which the first tools could not see — burnt values now stripped off disk. Canonical file is named to sort LAST so nothing can override it. **JUSTTCG_API_KEY was then UNSET 12:08 — the TCG price lane is deliberately DARK.** Its free tier is licensed personal/non-commercial and MarketSquare is commercial; the key is rotated, valid and backed up, so switching on is one paste the day David subscribes ($19/mo). See FEED_LICENCES.md + RG-0148 |
| MS_DEPLOY_TOKEN | deploy-token.conf (0600) | 12:34 | Minted fresh server-side (e205259d -> 76b30e21), local `.secrets/deploy_keys.txt` updated in the same run. No vendor, no counterpart |
| EMAIL_INBOUND_SECRET | zz-inbound.conf + /etc/environment + app .env, ALL THREE (0600) | 12:41 | PROBED: running process holds it. Took four attempts — three different values were found in three files at once, and the service was being restarted underneath us by the 2-minute autodeploy timer. Resolved by writing ONE value to EVERY location so precedence cannot matter. **PROBED anonymously 12:5x: `/email/inbound` answers 401 'Invalid inbound secret', NOT the 503 the code returns when the variable is empty — so the secret is loaded and being compared.** Worker `trustsquare-email-triage` pasted to match; that half is unverifiable from outside by construction and is proven only by real inbound mail |
| RELAY_INBOUND_SECRET | zz-inbound.conf + app .env (0600) | 12:37 | Rotated (b454baa6 -> 16bbb094). Read via `ai_provider.envkey()`, so it needs process env OR the app .env — the first attempt skipped it entirely because the check only looked at process env. **PROBED: `/intro/relay` answers 401 anonymously, so the door enforces — but that endpoint returns 401 for BOTH a wrong secret and an empty one, so unlike the email door this does NOT prove the value is set. The relay's server half rests on the process fingerprint (READ-grade), not a probe.** Worker `intro-relay` pasted to match |

## Still burnt — exposed, live, NOT yet replaced

| Credential | Why it matters | Rotate where | Blocked on |
|---|---|---|---|

## Removed rather than rotated

| Credential | What was found | Action | Date |
|---|---|---|---|
| COMMAND_SECRET | **Nothing consumes it.** No reference in any Python, JavaScript, batch or shell file in the repo, none in the deployed code on the server, and the running process did not carry it. It survived only as a stale line | **DELETED** from `/etc/environment` rather than rotated — a burnt secret that nothing reads is pure liability, and rotation would have preserved a thing with no purpose | 2026-08-22 |

## Unrotatable — accepted risk, with reasons

| Credential | Why it cannot be rotated | Why accepting it is reasonable | Decided |
|---|---|---|---|
| TRAVELPAYOUTS_TOKEN | Travelpayouts issues **one permanent token per account**. The dashboard (Programs → Aviasales → API) offers a copy button and nothing else — no regenerate, no roll, no second token. VERIFIED on the page 22 Aug 2026. | Read-only access to **cached fare data**. No customer data, no money, no write path, no billing exposure (marker 758984, no contract). Worst case is a stranger pulling free fare data on our quota — and quota exhaustion degrades exactly the way the design already handles: `data_flights` returns no indicative fare and the UI falls back to the agency card (SUPPLIER FALLBACK DOCTRINE, 1 Aug). The token is server-side only and RG-0025 forbids any Travelpayouts script on app pages, so it cannot leak again through the front end. | 2026-08-22, Claude (CTO call, RUL-037). Revisit if Travelpayouts ever adds token rotation, or if the affiliate account gains a payout balance worth stealing. |

## Removed or not applicable

| Credential | Status | Note |
|---|---|---|

| GMAIL_ADDRESS | not a secret | restored explicitly to gmail.conf so the app stops relying on a hardcoded fallback |
| MS_API_KEY | PUBLIC | published in ms.js by design — rotation is meaningless |
| FOUNDERS_ID_SALT | DECISION PENDING | rotating invalidates every existing ID hash. Claude's call, not yet taken — see the open ledger entry |
| Google ACCOUNT password | **CHANGED 22 Aug 2026** | Was exposed twice without being counted: stored on the box as `GMAIL_APP_PASSWORD` in `/etc/environment` (0644) for months and therefore printed into the DW-057 transcript dump on 20 Aug, then re-pasted to the server 22 Aug during the rotation. David changed it 22 Aug, superseding every exposed value (fingerprints 9e27def9 and 26c6616b are both dead). 2FA remains ON. |

## Structural findings — 22 Aug 2026

0. **The Gmail SMTP fallback had NEVER worked.** The value stored as `GMAIL_APP_PASSWORD`
   was 15 characters and Gmail answered 534 to it — it was David's Google ACCOUNT password,
   not an app password, and the account had no app passwords at all (list confirmed empty
   22 Aug). Every send attempt failed, was logged, and was swallowed. A real app password
   was created and installed 22 Aug and SMTP login now succeeds. Two lessons: a credential
   named for what it is SUPPOSED to be tells you nothing about what it IS, and a fallback
   nobody has ever exercised is decoration until proven — the same class as the placebo
   breaker in RG-0143.

1. **`/etc/environment` was mode 0644, world-readable, holding nine live secrets.**
   Now 0600. It is loaded by the marketsquare unit via `EnvironmentFile`, which is
   also why it silently overrode a correctly-written drop-in (the Paystack trap).
2. **`msdeploy` has a login shell** — so the world-readable file had a real reader,
   not a theoretical one.
3. **The exposure inventory was incomplete for fifteen days.** DW-029/DW-057 listed
   eight credentials; the same `systemctl show -p Environment` dump that burnt those
   also printed these nine. A register that is a prose list in a watch row will drift;
   this file is the replacement.
4. **A variable's NAME is not evidence of what it holds — three instances in one morning.**
   `GMAIL_APP_PASSWORD` held a Google ACCOUNT password. `PAYSTACK_WEBHOOK_SECRET` held the
   live Paystack SECRET KEY. `HETZNER_S3_*` holds CLOUDFLARE R2 credentials, and cost a
   photo-storage outage when Hetzner credentials were installed into an R2 lane on the
   strength of the name. In every case the truth was one probe away — the endpoint, the
   character count, the vendor's own error message. **Read what the value IS before acting
   on what it is CALLED.**

5. **A credential can live in more than one place with different values.** The
   authoritative value is whatever the RUNNING PROCESS holds — verify there, never
   on disk alone.
