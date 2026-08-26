## 2026-08-26 — CSP-SCRIPT-SRC-5: 033 was measuring a 301 redirect, and racing the reload

Third and (probably) final fault in `migrations/033_csp_verify_served.py`. The CSP-SCRIPT-SRC-4 fix
earlier today was correct and PROVEN by the deploy that followed: the 04:05Z run's own diagnostic
printed the NEW policy — `add_header Content-Security-Policy default-src 'self'; script-src 'self'
'unsafe-inline' ...` — so the rewrite worked. It still failed, because the *verification* was wrong
in two independent ways.

**(1) It measured the wrong response.** `served_csp()` fetched `http://127.0.0.1/` and read the
headers off whatever came back. What comes back is:

```
HTTP/1.1 301 Moved Permanently
Location: https://trustsquare.co/
Content-Security-Policy: frame-ancestors 'self'
```

The port-80 block is a **redirect**, not the site. 033 was asserting the CSP of a 301 it does not
care about, and would have failed no matter how correctly it rewrote the config. It now speaks TLS
to `:443` with **SNI** so nginx selects the real vhost, and it **fails loudly on any 3xx** rather
than silently measuring it — reading a redirect as if it were the page is the whole bug and must
never be silent again.

**(2) It raced the reload.** `nginx -s reload` is asynchronous — the master signals the workers and
old workers keep serving until their connections drain. A fetch fired immediately after can be
answered by a worker still holding the OLD config, so a perfectly good rewrite measures as "no
effect". The post-reload read now polls for up to 15s until the answer stops changing.

**CLASS — and this is the third instance of one lesson in a single morning.** An assertion is only
as good as WHAT it measures:

| | compared | should have compared |
|---|---|---|
| `audit_global_qa.py` (DW-072) | raw bytes | content, line-endings normalised |
| `033` CSP-SCRIPT-SRC-4 | file prose incl. comments | the `add_header` directive |
| `033` CSP-SCRIPT-SRC-5 | a 301 redirect | the actual page over TLS |

Each one produced a confident, wrong answer for days. None was a logic error; all three were the
program looking at the wrong object. Worth carrying into every future probe: name what you are
measuring, then check that is what you fetched.

Diagnosis came from the 04:05Z deploy's own improved failure text plus one read-only
`curl -sI -H 'Host: trustsquare.co' http://127.0.0.1/` on the box — the SSH lane restored earlier
today is what made that possible at all.
