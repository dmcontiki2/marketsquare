## 2026-08-17 — Lockout prevention trio (David's asks after SSH-LOCKOUT-1)
The blackout lockout turned out to be TWO stale allowlists: the Hetzner SSH rule AND
the Cloudflare "PRELAUNCH GATE - block all except allowlisted IPs" WAF rule (found via
David's Ray ID in Security Events; his new IP added to both by hand, verified: root
200 / terms 200 / gated 401 / health 200 / ssh open). Preventions built:
(1) scripts/hetzner_fw_selfheal.py v2 — self-heals BOTH allowlists from David's own
machine (which by definition owns the new IP); additive only; needs two David-only
tokens: .secrets/hetzner_token.txt (Cloud API r+w) and .secrets/cf_waf_token.txt
(zone-scoped Firewall edit). Refuses safely with instructions until provided.
(2) RG-0099 LOCKED — the tripwire: port-22 reach + CF-not-blocking-own-IP from the
session vantage; a red names the exact fix line, no more mystery mornings.
(3) FALSE-FAIL-1 on the dashboard infra card — a failed TEST REQUEST (auth/transport)
now paints amber "? CAN'T TEST" with the honest reason; red FAIL is reserved for
probes that RAN and failed (David's screenshot showed every row "failing" identically
— that was a dead admin session, not thirteen dead services).
OPEN QUESTION flagged for David: Security Analytics shows ~91k requests/24h with only
4.19k mitigated — worth reading Top Statistics together; that volume is not our traffic.
Cost model impact: none.
