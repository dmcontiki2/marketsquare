### ALERT-OFFORIGIN-1 — the watch's alarm no longer depends on the origin (5 Sep 2026)

DW-097 closed. The RED alert used to be one ssh command to the box it reports on, so it failed on
exactly the days it was needed (26 Aug, 5 Sep). The Cloudflare uptime Worker now exposes a
key-gated `POST /alert` and `scripts/watch_alert.py` calls that lane first, keeping the old ssh
lane as a fallback. Asserted by ledger **RG-0279**, whose live leg dry-probes the endpoint on every
run — so the path cannot rot unseen between emergencies.

Earlier the same day, the maintenance loop closed DW-096 (third SSH lockout) and wired
`hetzner_fw_selfheal.py` into the 20-minute host tick (**RG-0274**).
