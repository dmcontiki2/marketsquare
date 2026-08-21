## 2026-08-21 — ID-NPR-3: the provider module was not on the deploy manifest, and the lane had no probe

David pasted the Didit key into the server `.env`, restarted, and asked me to check it. Two
findings, and the first is the one that mattered.

**The code was never deployed.** `GET /users/{email}/id-status` on the live server returned
`{"detail":"Not Found"}` — FastAPI's unknown-route 404, not my endpoint's "User not found"
404, which is how you tell the two apart. Neither `55094e0` nor `ce58ca2` is an ancestor of
`origin/deploy`; the live release is still `a68b755`. So a correct API key was sitting in a
`.env` on a server running code that has never heard of it. Inert, not broken — but it looked
done from the outside, which is the failure mode worth naming.

**`id_verify_provider.py` was not in `ops/autodeploy/deploy_manifest.txt`.** Placement is an
allowlist copy, so `bea_main.py` would have shipped WITHOUT the provider module. Because the
import sits inside the endpoint rather than at module scope, that would not have crashed
startup — it would have 500'd every verification attempt on a server reporting itself
perfectly healthy. This is the same class as CityLauncher's TEACH-DEPLOY-1 on the same day: a
hardcoded file list that new files are invisible to. Added, and the regression ledger now
asserts it, so the next new module in this lane trips red instead of half-shipping.

**Added `GET /id-verify/status`** — a public, secret-free probe reporting provider, whether a
key is configured, whether the lane is available, and the price. CLAUDE.md's supplier
doctrine says a dead feed must turn red rather than go silent; this lane had no way to be
seen from outside at all, which is precisely why "did the key land?" cost a round-trip. It
answers READY or DARK in one call, and the ledger asserts it stays.

No behaviour change to the verification logic itself. Guards remain 14/14.

Cost model impact: none — the probe reads local config and calls no supplier.
