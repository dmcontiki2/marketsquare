# rig_autorenew — the rendered proof for AUTO-RENEW-1 (RUL-224, 12 Oct 2026)

The REAL app, locally, with a **Paystack stand-in** beside it, driven by headless Chromium at 412×915 as QA
accounts. Used because no Paystack test key was within reach on build day. **The stand-in is not Paystack**:
it follows Paystack's published API and webhook shapes (plans, a hosted checkout page, a subscription opened by
the first card payment, signed webhooks, disable / enable), keeps everything in memory, takes no money and only
answers on 127.0.0.1.

| File | Role |
|---|---|
| `rig_sync.sh` | copies the working tree to `/home/claude/rig`; rewrites the two origin constants in the RIG COPY ONLY |
| `rig_run.py` | the real backend (`bea_main`, security gate on), throwaway database, `payments._BASE_URL` -> the stand-in |
| `rig_front.py` | plays nginx: serves `marketsquare.html`, `ms.js` ... and passes the rest to the backend (one origin, :8080) |
| `paystack_standin.py` | the stand-in (:8999), with `/__standin/renew` to play a renewal or a failed renewal |
| `rig_start.sh` | starts all three with rig-only made-up keys (a `sk_test_...` string, `ALLOW_TEST_PAYMENTS=1`) |
| `verify_auto_renew.py` | the 46 rendered checks and the pictures (`SHOT_DIR`, default `/home/claude/shots/AUTO_RENEW_shots`) |
| `run_verify.sh` | fresh rig + the proof, in the background; log in `/home/claude/rigdata/verify.log` |

Run (cloud workspace or any Linux box with Python 3.11+, node, Playwright's Chromium):
`pip install fastapi uvicorn boto3 bcrypt python-multipart httpx pillow PyJWT playwright`, put the repo at
`/home/claude/ms`, this folder at `/home/claude/rigkit`, then `./rig_sync.sh && ./run_verify.sh`.

IDENTITY-GUARD-1: QA accounts only (`dmcontiki2+qa-...`), a clean headless browser, never David's Chrome; the
browser refuses every request that is not to the rig itself, so the live site is never touched.

**When a Paystack TEST key is available**, the same `verify_auto_renew.py` flow is the script to follow against
the real thing: point `payments._BASE_URL` back at Paystack, set the test key, and the one step this rig cannot
show — Paystack itself opening and billing the subscription — is seen.
