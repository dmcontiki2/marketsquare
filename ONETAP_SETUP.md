# ONETAP-1 — Google sign-in: what only David can do

Status: **LIVE — Google is configured and serving** (verified 21 Aug 2026: `GET /auth/providers` → `{"google":true,"apple":false}`, and `/auth/oauth/google/start` returns 302 to Google). Apple stays dark by ruling (RUL-030). The text below is kept as the setup record; the buttons render because credentials exist on the
box. Nothing is broken while it is dark — email sign-in is untouched.

RUL-028 · regression ledger RG-0111 · implemented as the server-side OAuth redirect flow
(no third-party JavaScript — RG-0025).

---

## 1. Google (about 10 minutes, free)

1. Go to **console.cloud.google.com** → create a project (or reuse one) named `TrustSquare`.
2. **APIs & Services → OAuth consent screen**
   - User type: **External**
   - App name: `TrustSquare`  ·  support email: your address
   - Authorised domain: `trustsquare.co`
   - Scopes: leave the defaults (`email`, `profile`, `openid`)
   - Publish it (while in "Testing" only listed test users can sign in — that would be a retry
     for everyone else, so publish before launch)
3. **APIs & Services → Credentials → Create credentials → OAuth client ID**
   - Type: **Web application**
   - Authorised JavaScript origins: `https://trustsquare.co`
   - **Authorised redirect URI — must match exactly:**
     ```
     https://trustsquare.co/auth/oauth/google/callback
     ```
4. Copy the **Client ID** and **Client secret**.

## 2. Apple — NOT DOING IT (David, 19 Aug 2026)

Apple sign-in needs the $99/yr Apple Developer Program. **David's call: no.** Google alone is a
complete solution — it is free, it covers the overwhelming majority of users, and anyone without
a Google account still has the 6-digit email code (SIGNIN-CODE-1) as the fallback.

The Apple code stays in `bea_main.py` but is **dark and costs nothing**: with no
`APPLE_CLIENT_ID`, `_apple_client_secret()` returns `None`, `/auth/providers` reports
`apple: false`, and no Apple button is ever rendered. It is not a half-configured lane and it is
not a maintenance burden — it simply does not exist as far as the app or any user is concerned.
Nothing below this line involves Apple.

## 3. Put the credentials on the box

Easiest: run **`add_google_oauth.bat`** — it prompts for both values, appends them to the server
`.env` only if absent, restarts BEA and prints `/auth/providers` to prove the lane came up. It is
gitignored, like every other credential bat.

Or by hand (never into a file in the repo — same rule as the Paystack and Travelpayouts keys):

```
GOOGLE_CLIENT_ID=<the client id>
GOOGLE_CLIENT_SECRET=<the client secret>
```

Then restart the service.

## 4. Prove it

```
curl https://trustsquare.co/auth/providers
```

- `{"google":false,"apple":false}` → lane dark, no buttons (was the state until 21 Aug 2026)
- `{"google":true,"apple":false}` → **the state today** — Google button renders, Apple never does (RUL-030)
- `{"google":true,"apple":false}`  → the Google button renders. `apple:false` is
  correct and permanent — see section 2.

Then run the regression ledger — **RG-0111** flips to READY TO LOCK once a provider is live.
Finally, sign in yourself once from a browser that has never seen the site.

---

## What the user experiences once it is on

Tap **Continue with Google** → if they are already signed in to Google (most people, most of the
time) they are back in the app signed in. No email, no code, no link, no waiting, no device
dependency, **no retry**.

If they are not signed into Google, they see Google's own account chooser — a screen they already
trust and already know how to complete.
