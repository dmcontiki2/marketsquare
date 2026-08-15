## 2026-08-15 — /tsl: GATE-EMAIL-1 SHIPPED · RG-0081 LOCKED · RG-0082 opened (edge-cache doc leak, pre-existing)

Guarded ship of the email-linked gate, David's word via /tsl. Gate: CM=ok DB=ok after fragment
fold. A stale 0-byte .git/index.lock (GIT-LOCK-1 class, 09:38) blocked the commit from the
sandbox (FUSE blocks unlink); cleared by the documented remedy — commit.bat run on David's
machine via desktop control (self-heals through git_unlock.bat), which also committed the
session's work (5dc62a7). Sandbox holds no GitHub credentials by design, so the deploy ref was
published by David's own wrapper (ms-deploy → deploy_marketsquare.bat). Rollback tag
pre-tsl-gateemail-20260815 at 400e907 (prior live release).

Live verify (~60s after push): off-list POST /review/request-link → 200 {"ok":true};
GET /review/enter?t=garbage → 302 /?gate=expired; anonymous /wonders + /listings → 401 (gate
holds); health 200 in 0.35s; SSL to 24 Sep. Full ledger: 0 regressed, **RG-0081 promoted to
LOCKED** (email door + break-glass code + cookie-first verify).

**RG-0082 OPENED** during the same verify: Cloudflare serves the gated index DOCUMENT to
anonymous visitors from edge cache (cf-cache-status HIT) once any cookie-holder primes it —
origin gate intact, data endpoints sealed, HTML shell only; class live since GATE-ENFORCE-2
armed 13 Aug, predates tonight's change. Fix lanes in the entry ref: CF cache rule (David's
console) or origin Cache-Control migration; must be reversible for the 29 Aug gate-down.

Testers (Maroushka, Maurice, Marietjie): next visit, type your email, click the link — in for
a year. Nothing to remember; the code still works behind "Have a code or admin password?".
