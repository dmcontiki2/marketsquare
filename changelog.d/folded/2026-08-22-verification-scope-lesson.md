## 2026-08-22 — three false failures from one wrong assumption about a verification endpoint

`CF_CACHE_TOKEN` took five attempts. **Four of them failed because of the check, not the
credential.** Recorded because the failure mode is subtle and cost the most time of anything
in the rotation.

- **Wrong endpoint.** The installer verified with `GET /user/tokens/verify`. That is a
  USER-level endpoint. A token scoped to one zone's Cache Purge cannot call it, so it
  answers **401 whether the token is good or not**. The original token passed only because
  it was broader (Cache Purge + DNS Write, account-scoped) — which made the check look
  sound right up until it was replaced by a properly narrow one. **A verification that
  fails closed on correct input is worse than no verification: it destroys good work.**
- **Wrong constant.** "Cloudflare API tokens are 40 characters" was asserted from memory
  and is false — this account issues 53. That wrong number was then wired into the
  installer as a warning, so the tool *agreed* with the wrong diagnosis and sent David back
  to re-copy a correct value three times.
- **What proved it:** replacing the check with the job the credential exists to do — a real
  `POST /zones/{zone}/purge_cache` against a URL that does not exist. Harmless, and end to
  end. It passed first time on the value that had been "failing" all along.

**Rule taken from this: verify a credential by exercising its ACTUAL permission, never by
calling a broader endpoint it may not be entitled to.** The same rule already existed one
level down (RG-0147: verify at the point of use, not at the file) — this extends it: the
probe must be inside the credential's own scope, or a least-privilege credential will read
as broken. Every verifier written today follows it: Resend by a send probe, Paystack by a
transaction call, Anthropic by a models list, R2 by a bucket listing, Gmail by an SMTP
login, Cloudflare by a purge.

Net effect: the new token is deliberately NARROWER than the one it replaces — one zone,
Cache Purge only, no DNS Write.
