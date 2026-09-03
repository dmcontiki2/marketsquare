## 2026-09-02 — NO-STALE-IP-1: origin SSH allowlist pruned 5 → 1, self-heal now sets instead of appends, CF half retired (RUL-091)

David, on the maintenance report's "prune the stale IPs with David at a calm moment": *there should
be no stale IPs*. Executed, not listed.

- **Evidence first:** server sshd log (21 days) shows ONE egress — 197.184.106.176 accepted until
  04:36Z on 2 Sep (David's overnight tasks), then only 197.185.137.157 (this session) — no overlap,
  so PC and sandbox share the address and the other four /32s were dead.
- **Pruned live:** firewall `trustsquare-origin-lockdown` SSH rule set to exactly
  `197.185.137.157/32` (was 5). Port 22 PROBED open after. 80/443 rules untouched (22 Cloudflare
  sources each).
- **`scripts/hetzner_fw_selfheal.py`:** heal = SET `[current IP]`, never append; "prune with
  David" wording gone. `CF_HALF_RETIRED = True` — the PRELAUNCH GATE was disabled 19 Aug
  (RUL-034) and the site launched 1 Sep, so the script no longer asks for `cf_waf_token.txt`.
- **Ledger:** new **RG-0245** (LOCKED) — live leg reads the Hetzner API and fails on ≠1 source
  IP; source leg fails if the script ever appends again. **RG-0188** INFO now states the CF half
  is retired instead of "unarmed, token missing". Both green this run.
- **RUL-091** recorded; `rulings_check.py` 91 checked, 0 FAIL.
- **Incidental:** the server REBOOTED at 16:47Z mid-ledger (kernel 6.8.0-117 → 6.8.0-138 after
  97 days up; initiator not in the journal). Caused a ~60 s 521 window that painted RG-0214/0229/
  0233 red once; re-run green, `/health` 200, `marketsquare.service` running, disk 45%.
- Ledger after: 238 entries, 216 holding, 0 regressed, 0 unverified, exit 0.
