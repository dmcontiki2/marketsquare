# RESUME HERE — TrustSquare security incident (started 3 Aug, continued 4 Aug 2026)

Read this first next session. It is the single pickup point for the Travelpayouts Drive breach work.

## What the incident was
A Travelpayouts "Drive" loader (`https://tp-em.com/NTU3Mzkx.js`) was committed into
`marketsquare.html` line 4 and 9 `adventures_*_map.html` pages, and shipped live by the normal
deploy. It ran remote third-party code in `<head>` on the index page — which also carries the
identity-document upload flow — before the client-side "pre-launch" gate (a `display:none` div, a
curtain not a door) ever rendered. Proven exfiltration to tp-em.com from behind the "locked" screen.
Full write-ups: `changelog.d/2026-08-0*` and `Records/BREACH_AUDIT_BRIEF_2026-08-04.md`.

## DONE and verified (do not redo)
- **Loader removed** from all 10 pages; live HTML has 0 tp-em.com refs. Ledger RG-0025 INVERTED.
- **Drive fully disabled** in the Travelpayouts panel (boost Maximum -> None).
- **Cloudflare WAF rule** blocks all non-allowlisted traffic (RG-0027). Exemptions: /health,
  /payment/webhook, /.well-known/.
- **Origin firewall (RG-0028) — the big one.** The Peer review found the WAF was bypassable by
  hitting the Hetzner IP (178.104.73.239) directly with Host: trustsquare.co. FIXED with a Hetzner
  Cloud Firewall: inbound TCP 22 = David's IP only; 80/443 = Cloudflare's 15 IPv4 + 7 IPv6 ranges
  only; outbound untouched. Verified: direct hit now fails to connect; /health still 200 via CF.
- **MS_JWT_SECRET rotated** on the live box (openssl rand -hex 32), old secret purged from the
  systemd unit, single source now /etc/environment. Verified via /proc that the process uses the new
  secret. Reviewer secret auto-rotated (derived). Admin login re-tested, works. Exposed breach-window
  tokens are dead.
- **Code hardening (JWT-HARDEN-1, in bea_main.py, live on next deploy):** removed the
  `ms_jwt_secret_change_me` fallback; admin auth now FAILS CLOSED if the secret is unset.

## Independent audit
GPT-5.6 Peer review at `Records/PEER_REVIEW_2026-08-04-0516_security.md`. It CONFIRMED the analysis,
CORRECTED three of Claude's claims (exposure ceiling was wider than "just tokens"; payloads are
unrecoverable *from our logs* not absolutely; a country block is not authentication), and found the
origin-bypass BLOCKER above. Re-run any time with `run_peer_audit.bat`.

## STILL OPEN (priority order, none on fire)
1. **Testers — GATE BUILT 5 Aug, awaiting deploy.** Maroushka (miconradie1@gmail.com), Maurice (conradiedm@gmail.com — his
   yahoo bounced), Marietjie (marietjie.marais59@gmail.com), David (davidconradie1234@gmail.com).
   Do NOT widen the WAF to South Africa (Peer: a country is not auth). Real fix = enforce the
   existing server-side /review/login token at the ORIGIN (bea_main.py already has the machinery,
   just not enforced). This is the natural next build.
2. `.bak-tpdrive-*` backups of the compromised pages still in the web tree — move out of /var/www.
3. `/.well-known/` WAF exemption is broader than ACME needs — narrow to /.well-known/acme-challenge/.
4. Four Travelpayouts JS chunks never examined (chunk.CIR5CNTC.js + 3).
5. Cloudflare + service-worker caches may still hold old compromised HTML — purge + verify.
6. `unpkg.com` Leaflet makes "no third-party code" untrue — self-host/pin.
7. Hardening from the box: secret in world-readable /etc/environment (move to chmod 600 file);
   uvicorn binds 0.0.0.0 (bind 127.0.0.1 — firewall already mitigates).

## Housekeeping
- Standing order from David (4 Aug): NO access for any agent other than David. Honor it.
- Delete old-secret backups (*.bak-jwt-*) on the server once the new secret is trusted.
