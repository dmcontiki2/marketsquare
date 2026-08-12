## 2026-08-11 - SSH lockout was ISP IP rotation, not a dead server (SSH-IP-ROTATION-1)

**Symptom.** `ssh root@178.104.73.239` timed out from David's PowerShell. Port 22 also timed
out from the Cowork sandbox, which made it look like the box was down.

**It was not down.** `GET https://trustsquare.co/health` returned 200
(`TrustSquare BEA 1.3.1`) throughout. Server uptime on reconnect: 75 days. All three services
(marketsquare, advertagent, citylauncher) active, disk 44%. Nothing had crashed.

**Cause.** The Hetzner Cloud Firewall `trustsquare-origin-lockdown` (ORIGIN-LOCKDOWN-1, 4 Aug)
allows TCP 22 from David's IP ONLY. His ISP had rotated him to a new address, so his own SSH
was refused by his own firewall. Deny-all inbound means a refused source gets a timeout, not a
rejection - which is exactly what a dead box looks like. That ambiguity is what cost the time.

**Also found - the rule label had drifted from the rule.** The rule was named
`SSH - David only (197.185.169.80)` while the source box actually contained `197.185.142.142`.
Two different stale addresses, neither current. A label that disagrees with its own rule is
worse than no label; it sends the next reader looking in the wrong place.

**Fix applied** (David's call, offered against the wider-range and single-IP alternatives):
`197.185.155.69` ADDED alongside `197.185.142.142` on the port 22 rule - both /32, nothing
widened. Label corrected to `SSH - David only (.142.142 + .155.69, updated 11 Aug 2026)`.
Ports 80/443 (Cloudflare edge ranges) untouched.

**Verified after the change.** SSH returns `ubuntu-4gb-nbg1-1`. Full regression ledger run:
every LOCKED fix holding, 3 known defects still open - RG-0028 (origin refuses direct 80/443)
still passes, so the lockdown was not weakened.

**Operational fact worth keeping.** The Cowork sandbox egresses via David's public IP - the
sandbox regained SSH the instant the rule applied. So sandbox SSH has been dead since 4 Aug
whenever David's IP rotated, and it recovers automatically with this same fix. Session-based
SSH work and David's own SSH share one dependency.

**Recurrence.** This WILL happen again on the next rotation. Diagnosis order for next time is
in ACCESS_CHEATSHEET.md: check /health first - if it is 200, the server is fine and it is the
firewall. Deliberately NOT ledgered: an assertion pinned to a rotating IP would fail by design
and train us to ignore red.
