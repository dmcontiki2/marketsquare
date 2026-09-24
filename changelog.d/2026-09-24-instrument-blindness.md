## 2026-09-24 — Four instruments that convicted from a vantage they could not see from

Four separate boards spent the week printing red at things that were not wrong, and one of those
reds was addressed to David personally. All four are now entries in the regression ledger with a
test behind each, so a revert goes red instead of going quiet.

**RG-0462 (ENVKEY-BLIND-1) — the one aimed at David.** RG-0426 failed with *"only 1 AI vendor key
is live on the box"* and its scope told him to go and provision a vendor credential. He already
owned it. The check read `/proc/<pid>/environ` alone, citing "check at the point of use" — but the
point of use is `ai_provider.envkey()`, which by ENVKEY-1's design (17 Jul 2026) falls back to
`/var/www/marketsquare/.env` *because the systemd unit does not export it*. A .env-sourced lane can
never appear in that read, so the check could only ever fail, whatever the box actually carried.
The independent corroboration needed no credential at all: `/dashboard/maint` published
`brain_lane: openai`, `brain_keyed: true`, `brain_probe {ok: true, status: 200}` the same day. The
probe now takes the **union** of both doors — unit-exported names from `/proc`, plus the lanes
`ai_provider.configured_lanes()` resolves on the box. Re-aimed, not weakened: fewer than two
reachable lanes still fails, and `scripts/test_envkey_blind1.py` drives a one-lane box to prove it.

**RG-0459 (LEDGER-VANTAGE-BLIND-1).** The 23 Sep board printed "4 previously-fixed issue(s) HAVE
COME BACK. Do not deploy over this." All four asserted on `../CityLauncher/…` or the Projects-root
`CLAUDE.md` — present on David's machine, not mounted on the stand-up task. The instrument read its
own blindness as four rotted fixes and carried a deploy block with it. `sibling_visible()` now
separates "cannot see" from "gone".

**RG-0460 (BIT-EDGE-BLIND-1).** The BIT board printed 7 FAIL including an S1, exit 2. `curl /health`
answered 200 in the same minute; the runner's urllib client got 403, `Server: cloudflare`,
`error code: 1010` — the edge refusing the default Python-urllib User-Agent. A named UA, and an edge
refusal now exits **3 = NOT MEASURED**, which is neither healthy nor failed.

**RG-0461 (BIT-NS-1).** `scripts/golden_seam_v2.py` died on `NameError: name 'os'` before reaching
its own check. In a scheduled run a traceback and silence read identically — nobody is watching
either. It now resolves stdlib on demand and otherwise says **THE BOARD DID NOT RUN**.

The shared class, and the reason these are one entry-set rather than four unrelated bugs: *an
instrument that could not measure must say so, not convict.* That doctrine was already in the ledger
five times (RG-0187, RG-0401, RG-0420, RG-0423, VANTAGE-BLIND-1) and none of these four had
inherited it.
