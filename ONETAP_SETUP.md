# ONETAP-1 — Google & Apple sign-in: what only David can do

Status: **code shipped, lane dark.** The buttons do not render until credentials exist on the
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

## 2. Apple (about 30 minutes, needs the $99/yr Apple Developer Program)

Only if you want the Apple button too. Google alone is a complete solution; Apple matters most
for iPhone users, who are a large share of a marketplace audience.

1. **developer.apple.com → Certificates, Identifiers & Profiles → Identifiers**
   - Create an **App ID** (or reuse), enable **Sign in with Apple**
   - Create a **Services ID** — e.g. `co.trustsquare.web`. This is your `APPLE_CLIENT_ID`.
2. Configure the Services ID → **Sign in with Apple → Configure**
   - Domain: `trustsquare.co`
   - **Return URL — must match exactly:**
     ```
     https://trustsquare.co/auth/oauth/apple/callback
     ```
3. **Keys → Create a key**, enable Sign in with Apple, download the `.p8` **once** (it cannot be
   re-downloaded). Note the **Key ID**. Your **Team ID** is top-right in the portal.

> Apple lets users hide their real address behind `@privaterelay.appleid.com`. That is handled —
> identity is keyed on the provider's stable `sub`, not just the email — but be aware those users
> will show a relay address in your admin views.

## 3. Put the credentials on the box

Add to the server environment (never into a file in the repo — same rule as the Paystack and
Travelpayouts keys):

```
GOOGLE_CLIENT_ID=<from step 1.4>
GOOGLE_CLIENT_SECRET=<from step 1.4>

# Apple only if you did step 2
APPLE_CLIENT_ID=co.trustsquare.web
APPLE_TEAM_ID=<10-char team id>
APPLE_KEY_ID=<10-char key id>
APPLE_PRIVATE_KEY=<contents of the .p8, newlines as \n>
```

Then restart the service. A one-shot `.bat` on the proven `add_travelpayouts_key.bat` pattern is
the right way to do it — remember the lesson recorded there: cmd's `for /f` swallows the `=` in
`ssh` output, so pipe to a `%TEMP%` file and use `set /p`.

## 4. Prove it

```
curl https://trustsquare.co/auth/providers
```

- `{"google":false,"apple":false}` → lane dark, buttons hidden (this is today)
- `{"google":true,...}`            → the button renders on the sign-in screen

Then run the regression ledger — **RG-0111** flips to READY TO LOCK once a provider is live.
Finally, sign in yourself once from a browser that has never seen the site.

---

## What the user experiences once it is on

Tap **Continue with Google** → if they are already signed in to Google (most people, most of the
time) they are back in the app signed in. No email, no code, no link, no waiting, no device
dependency, **no retry**.

If they are not signed into Google, they see Google's own account chooser — a screen they already
trust and already know how to complete.
