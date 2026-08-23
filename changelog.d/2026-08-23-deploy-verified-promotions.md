## 2026-08-23 — deploy verified; RG-0154 + RG-0158 promoted to LOCKED

David published the deploy ref (74ab420) in an attended session. Verified from the
sandbox: origin/deploy == HEAD, 0 ahead; /health 200; ledger 151 entries, 139 holding,
0 REGRESSED. Both entries that were waiting on this deploy now pass live and were
promoted OPEN -> LOCKED same-session per the ledger rule: RG-0154 (session badge
derived + dated — SESSION-COUNTER-1 + migration 030 live; its passing live probes also
prove the server runs the new bea_main.py, closing the drift substance of DW-058) and
RG-0158 (SAW teaser live with both honesty labels + index banner — locked the morning
after, exactly as its ref predicted). check_deploy_drift.py itself needs SSH (no host
key in sandbox) — the host-side daily check will read clean and close DW-058 formally.
Expected knock-on: DW-061's FEA sensor will re-alert on this deploy (deploy-not-tamper
pattern); closes with --update-baseline on the box, attended.
