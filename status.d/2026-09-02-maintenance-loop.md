- **Maintenance loop 2 Sep (unattended):** RG-0099 lockout healed (home IP moved → added to
  Hetzner SSH allowlist, port 22 probed open). Fault queue empty (0 new / 0 fix-shipped /
  26 verified). Shadow agent heartbeat posted. Ledger 237 entries, 0 regressed, 0 unverified.
  No escalations. Follow-up for David: prune 4 stale IPs from `trustsquare-origin-lockdown`
  SSH rule; `.secrets/cf_waf_token.txt` still absent (CF self-heal half unarmed).
