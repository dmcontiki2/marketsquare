## 2026-08-26 — Third-party sweep (unattended): RED, 3 days to soft launch

Verdict **RED**, and not for the site — the site probes green (`/health` ok v1.3.1, `/` 200 in
0.47 s, `/payment/test` paystack_connected, `/dashboard/bit` 8/8, TLS 88 days, EULA v1.15 live).

RED because: (1) `GET /launch-api/prospects/list` serves **200 PII records with pre-authenticated
magic links to an anonymous reader** — re-probed independently this run, and the gate was failing
open *by design*; (2) the **migration chain is jammed** at `033_csp_verify_served.py` (failed on the
02:07:10Z deploy) and the fix for it is sitting unshipped in `b77cd2b`; (3) **no `script-src` CSP**
at the edge on either the index or an app path; (4) **SSH to the origin is down and took the
RED-alert path with it** — the alert channel is one SSH command to the box; (5) the **external
uptime watcher is still not deployed**, day 4, which is also the structural fix for (4).

Executed this run, not reported: **LAUNCH-API-FAILCLOSED-1** (`require_launch_key` now 403s when
`LAUNCH_API_KEY` is unconfigured — inert until the CityLauncher deploy rides, so the exposure is
live until David deploys) and **CRLF-DRIFT-1** (`audit_global_qa.py` normalises line endings before
the byte compare; proven — the 17,389-byte "drift" is exactly the repo's CR count).

Ledger **exit 1 — 181 entries, 156 holding, 3 REGRESSED (RG-0099, RG-0125, RG-0154), 20 open,
2 UNVERIFIED**. Rulings **56, 0 FAIL**. EULA sync green. `THIRD_PARTY_LAUNCH_REGISTER.md` rewritten
from probes; `OPEN_LOOPS.md` annotated (B1 is discharged and mis-filed under BLOCKING).

David-only and dated in the register: Hetzner firewall IP (restores SSH + the alert path),
`LAUNCH_API_KEY` + CityLauncher deploy, Google consent-screen state, the four `DOMAIN_*` fields
(RDAP unreachable for the third sweep running), the uptime-watcher deploy, and the **last ship on
Wed 27 Aug** — which must carry the migration-033 rewrite.
