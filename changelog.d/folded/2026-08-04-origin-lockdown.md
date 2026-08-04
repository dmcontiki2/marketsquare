## 2026-08-04 — The origin now refuses everything except Cloudflare (ORIGIN-LOCKDOWN-1)

**Found by the Peer, missed by the Author.** The GPT-5.6 independent security review
(`Records/PEER_REVIEW_2026-08-04-0516_security.md`) opened with a BLOCKER: the Cloudflare WAF rule
from RG-0027 only ever governed traffic that *chose* to arrive via Cloudflare.

The nginx block `server { server_name 178.104.73.239; return 444; }` rejects requests addressed to
the **raw IP**. It does nothing about a request carrying `Host: trustsquare.co` — that selects the
real vhost and gets served in full.

**Proven, not theorised.** On 4 Aug:

```
curl -k --resolve trustsquare.co:443:178.104.73.239 https://trustsquare.co/   ->  200, 391 KB
```

The entire marketplace, straight off Hetzner, WAF bypassed. And the origin IP is printed in
`assets/nginx_marketsquare.conf`, so anyone with repo access — or historical DNS, or certificate
transparency — could find it. The Author's 3 Aug "site is closed to the outside world" conclusion
was wrong: every verification had gone *through* Cloudflare, so it measured the one road that was
already guarded and never asked whether there was another.

**Fix — Hetzner Cloud Firewall** (deny-all inbound by default), applied to the CPX22:

| Port | Source |
|---|---|
| TCP 22 | David's IP only |
| TCP 80 | Cloudflare's 15 IPv4 + 7 IPv6 published ranges |
| TCP 443 | the same 22 ranges |

Outbound deliberately left empty (allow-all), so deploys, Paystack calls and R2 are unaffected.

**Verified both directions.** The same curl now fails to connect after 21 s. `/health` still returns
200 *through* Cloudflare, and `/` still returns 403 to non-ZA traffic — the bypass is shut without
closing the legitimate road.

**Ledger.** `RG-0028` added as LOCKED, and it is the load-bearing entry: it attempts a raw TCP
connect to the origin on 80 and 443 and fails if either is accepted, and separately checks `/health`
still answers through Cloudflare. **RG-0027's edge rule is only an access boundary while RG-0028
holds.** Remove the firewall and the WAF is decorative again.

**Watch items.** Cloudflare's published ranges change occasionally — if legitimate traffic starts
failing, re-pull `cloudflare.com/ips-v4` and `ips-v6` first. A GitHub webhook posting direct to the
IP rather than via the domain would now be dropped.

**Still open from the same review** (not addressed here): the `X-Admin-Token` validation path is
unknown, so it is not yet established that rotating `MS_JWT_SECRET` revokes anything; `MS_ADMIN_KEY`
and `ADMIN_KEY` need investigating alongside it; the four Travelpayouts JS chunks remain unexamined;
`*.bak-tpdrive-*` copies of the compromised pages are still in the web tree; the `/.well-known/`
WAF exemption is broader than ACME needs; CDN and service-worker caches are unverified; `unpkg.com`
Leaflet makes "no third-party code" untrue as written. **The Peer also advised against widening the WAF rule to South Africa** — a country is not
an authentication boundary.
