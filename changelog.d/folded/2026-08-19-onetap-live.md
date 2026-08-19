## 19 Aug 2026 — Google one-tap sign-in is LIVE, verified from outside

`add_google_oauth.bat` installed the credentials, the ENVKEY-1 fix rode the deploy, and the lane
came up. **Verified independently, not reported:**

```
/auth/providers            -> {"google":true,"apple":false}
/auth/oauth/google/start   -> 302 accounts.google.com/o/oauth2/v2/auth
    client_id      = 869589580243-…apps.googleusercontent.com   (matches the console exactly)
    redirect_uri   = https://trustsquare.co/auth/oauth/google/callback   (character match)
    scope          = openid email profile
    response_type  = code
    nonce + state  = both present, state signed
    prompt         = select_account
```

`scope` matters more than it looks: `openid email profile` are Google's **non-sensitive** scopes,
so the 100-user cap shown on the Audience page does not apply, no Google verification review is
required, and users never see the *"unverified app"* screen. Those are all triggered by sensitive
scopes (Gmail, Drive) that this never requests. **The 10,000-user question is settled.**

`apple:false` is correct and permanent (RUL-030).

### Board reconciled after the gate came down

Four entries still carried the old "gate is up" premise. None weakened — each repointed at what
still matters, with the ruling cited:

- **RG-0108** — its containment clause asserted anonymous `/listings` must be 401. Retired; it now
  proves the admin-door exemptions exposed nothing **private** (`/tuppence/*`, `/users/*`), which
  is the real risk. **LOCKED.**
- **RG-0090** — asserted the *gated* HTML shell is never CDN-cached for the public. The shell is
  public by design now, so the assertion has no subject. **PARKED, not deleted**: the original
  check is preserved verbatim in the body, because the cache-poisoning risk is real and returns
  the instant the gate is re-armed.
- **RG-0107 / RG-0109 / RG-0110** — all three promoted to **LOCKED**, each with a note on how the
  ruling changed its standing. RG-0107's rule explicitly "survives the gate it was born in";
  RG-0110 is now the *fallback* door behind Google, and stays locked so the fallback can never
  quietly vanish.

### Third false red from the same cause

`RG-0107` was sitting open purely because this ledger's own probe rate tripped the 8-per-10-minute
limiter and it read the 429 as a failure. That is now fixed in **RG-0081, RG-0107 and RG-0108**
alike: a 429 is the limiter *answering*, which proves the endpoint is reachable — the opposite of
what it was being reported as.

**Board: 110 entries · 106 holding · 0 regressed · 2 open** (RG-0075 and RG-0101, both pre-existing
and unrelated). Rulings: 27, 0 FAIL.
