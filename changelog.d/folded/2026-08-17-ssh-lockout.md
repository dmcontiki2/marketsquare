## 2026-08-17 — SSH lockout diagnosed + fixed at the Hetzner panel (SSH-LOCKOUT-1)
Post-blackout, port 22 timed out for BOTH David and the session while the site served
normally. Root cause found in the Hetzner console Activities feed: the
trustsquare-origin-lockdown Cloud Firewall (applied ~11 Aug, part of the G2 origin
hardening) allowlists SSH to two of David's home IPs — and the blackout's router
reboot moved him to a NEW IP (197.185.190.11; the Cowork sandbox shares his egress,
which is why both lanes died together and why sessions ever had SSH at all). Fix,
driven in David's Chrome with his go: ADDED .190.11 to the SSH rule (nothing removed),
"Firewall rule added" confirmed, SSH verified restored, ops chips ALL GREEN.
Standing lesson for the runbook: David's home IP is dynamic — after any
power/router event, re-add the current IP at Hetzner > Firewalls >
trustsquare-origin-lockdown (the Hetzner web console is the break-glass; deploys are
pull-based and never depended on SSH). Consider a small stale-IP pruning pass with
David later. Cost model impact: none.
