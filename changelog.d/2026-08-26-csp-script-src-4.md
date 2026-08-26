## 2026-08-26 — CSP-SCRIPT-SRC-4: 033 failed twice because it compared the wrong thing

`migrations/033_csp_verify_served.py` failed on two consecutive deploys (02:07Z and 03:54Z),
jamming the migration chain (RG-0125 red, DW-066). The rewritten 033 that rode the 03:54 deploy
did its job — it NAMED the surviving declaration, which the 24 Aug version could not — and that
diagnostic is what solved it.

**The bug.** Staleness was tested against the whole file text:

```python
stale = {p: t for p, t in files.items() if "script-src" not in t}
```

`/etc/nginx/snippets/security_headers.conf` carries a comment reading *"A full
Content-Security-Policy (script-src/style-src/img-src) is deliberately deferred..."*. That comment
contains the literal string `script-src`, so the **one file that needed rewriting tested as
already-fixed**, `stale` came back empty, the migration rewrote nothing — *"restoring 0 file(s)"*
in the 02:07Z run, which was the tell all along — and then failed honestly because the served
header had of course not changed.

**CLASS, and it is the same class as the CRLF false positive fixed in `audit_global_qa.py` the same
morning: the program compared the wrong thing.** One compared bytes when it meant content; this one
compared prose when it meant directives. Staleness is a property of the DIRECTIVE, so comments are
now stripped and only `add_header` values are tested. The failure diagnostic was given the same
treatment, or it re-reports the comment line as a declaration.

Proven against the real file content before shipping: old test -> `stale: False` (wrong);
new test -> 1 directive found, `stale: True` (correct).

**Policy verified safe before shipping** — the risk with a CSP is breaking the live site, so every
origin was inventoried rather than assumed: the ONLY remote script sources are `unpkg.com` (static
Leaflet tags on marketsquare.html, the teaser and the two studywork maps) and `cdnjs.cloudflare.com`
(Leaflet loaded dynamically by `ms.js aiLeaflet()`), both in the policy and both in RG-0177's
allowlist. `d3js.org` appears once and is a COMMENT inside vendored inline d3, not a remote load.
Every iframe is a same-origin relative path (`frame-src 'self'` holds), videos are self-hosted
`<video src>` not embeds, map tiles are covered by `img-src https:`, and the Google font pair is
covered by `style-src`/`font-src`.

Closes the CSP half of DW-069/RG-0178 and unjams the chain (RG-0125/DW-066) on the next deploy.
