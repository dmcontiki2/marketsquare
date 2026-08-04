# Independent Peer Review — 2026-08-04-0516

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: security · Author: Claude · System Engineer: David*

**Scope:**
  - Records\BREACH_AUDIT_BRIEF_2026-08-04.md (10,451 chars)
  - nginx_security_headers.conf (952 chars)
  - assets\nginx_marketsquare.conf (3,394 chars)
  - migrations\005_prelaunch_server_side_gate.py (7,801 chars)
  - changelog.d\2026-08-03-edge-prelaunch-gate.md (2,551 chars)
  - changelog.d\2026-08-03-server-side-prelaunch-gate.md (2,643 chars)
  - changelog.d\folded\2026-08-03-remove-travelpayouts-drive-loader.md (2,563 chars)

**Usage:** 8378 in / 11298 out tokens · actual cost ≈ $0.1523

---

# Independent Security Peer Review — TrustSquare / Travelpayouts Drive Incident

## Overall assessment

The removal of the `tp-em.com` loader is necessary and appears to have stopped the presently observed Travelpayouts Drive traffic. The Cloudflare rule is useful emergency containment **only if the origin cannot be reached except through Cloudflare and all relevant hostnames are covered**. That prerequisite is not established and is likely false from the supplied nginx configuration.

I disagree with the apparent implication that the incident ceiling is limited to browser storage tokens and profile data. A remotely supplied script running in the TrustSquare origin had the ability to read, intercept, alter, and transmit substantially more: form inputs, uploaded identity documents, API responses, magic-link/session material, and privileged actions available to the active browser session.

The central unsafe condition right now is that the organization has treated a browser-origin supply-chain compromise as a narrow static-secret exposure, without proving either (a) that the origin bypass is closed or (b) what data/actions the third-party script could access during the 30-hour window.

---

# Verdicts on the eight conclusions

## 1. “API keys were not exposed.”

**Verdict: INSUFFICIENT EVIDENCE**  
**Severity: MAJOR**

The conclusion is too broad for the evidence provided.

The secret sweep in `Records\BREACH_AUDIT_BRIEF_2026-08-04.md` establishes only that a limited set of patterns did not occur as static literals in eleven identified browser-delivered files. It does **not** establish that API keys or credential-equivalents were not exposed.

### What the sweep does establish

It is reasonable to say:

> No obvious matching static secret literals were found in the eleven scanned files.

The listed server environment variables also support the narrower statement that the named environment variables were not intentionally embedded in those static files.

### What this reasoning misses

1. **The four downloaded Travelpayouts chunks were not scanned.**  
   The brief records downloads of:
   - `chunk.CIR5CNTC.js`
   - `chunk.Dux8q1cR.js`
   - `chunk.DHGU-5oI.js`
   - `chunk.BD_XmNjn.js`

   These are executable code delivered after the initial loader and are specifically identified in the browser capture, yet no content analysis is supplied. A remote script’s relevant behavior cannot be bounded by inspecting only the bootstrap loader.

2. **Runtime credentials are more important than static literals.**  
   The brief confirms any page script could access:
   - `sessionStorage.ms_admin_token`
   - `sessionStorage.ms_review_token`
   - potentially user/session data in `localStorage`
   - API responses available to the page
   - request headers and bodies created by the application.

   A bearer token usable against an API is functionally an API credential, irrespective of whether it is called an “API key.”

3. **The scan does not cover dynamically fetched content, source maps, API responses, browser caches, service-worker caches, or network request headers.**  
   The supplied regexes also cannot detect:
   - encoded, encrypted, split, concatenated, or runtime-derived secrets;
   - non-standard token formats;
   - values injected by server-rendered JSON;
   - secret-bearing API responses;
   - third-party code extracting credentials from intercepted `fetch` / XHR calls.

4. **`POST /agencies` being server-key protected proves little about other endpoints.**  
   The statement that `/agencies` uses `Depends(auth.require_api_key)` is positive evidence for that one endpoint, not evidence that all other endpoint authorization is correct or that no other API credential was exposed.

### Corrected conclusion

> No evidence currently demonstrates direct exposure of the listed server-side environment-variable secrets in the eleven scanned static files. However, credential-equivalent browser tokens and any credentials or sensitive values available through runtime requests/responses remain potentially exposed. The unexamined Travelpayouts chunks and runtime behavior prevent a broader “API keys were not exposed” conclusion.

---

## 2. “The material exposure was browser-held session tokens and profile data, chiefly `ms_admin_token`.”

**Verdict: DISAGREE**  
**Severity: BLOCKER**

This materially understates the exposure ceiling.

The loader was a remotely controlled script executing in the `trustsquare.co` page context, not merely an analytics pixel. As described in the brief, it executed before the cosmetic gate and had full DOM access. Any script in that position can generally:

- read all DOM-visible data;
- install listeners for keystrokes, form fields, file-selection events, and submit events;
- monkey-patch `fetch`, `XMLHttpRequest`, `FormData`, browser history, and selected application functions;
- read `sessionStorage` and `localStorage`;
- make authenticated same-origin API calls using the victim’s browser credentials;
- read responses to same-origin requests permitted to the page;
- modify destination URLs, payment-related UI, or identity-verification UI;
- exfiltrate captured data over cross-origin requests;
- wait for users to enter data after the script has loaded.

### Identity-document flow substantially raises the impact

The brief explicitly says the same `index.html` contains the SA Smart ID / passport / driver’s-licence upload flow. Even if the Travelpayouts code did not intentionally collect uploads, a compromised script could have intercepted:

- document metadata;
- the selected file name, size, and MIME type;
- form values;
- upload request bodies, if the application sends them through JavaScript-accessible APIs;
- upload response data and stored-document URLs;
- identity fields entered before, during, or after document upload.

The supplied material does not establish whether the identity-document upload used a native browser form submission inaccessible to JavaScript, a direct-to-storage signed URL, a `fetch` request, or another mechanism. Therefore, it cannot support a claim that document data was outside the exposure boundary.

### `ms_admin_token` may be high impact, but its meaning is not established

The brief labels `ms_admin_token` as being sent in `X-Admin-Token`, but does not provide:

- the endpoint authorization implementation;
- token format;
- expiry;
- audience/scope;
- whether it is a JWT or static secret;
- whether it is accepted from all origins/paths;
- whether it grants privileged read, write, payout, user-management, or deployment-adjacent actions.

It is possible that it is the most serious credential. It is not proven from the supplied material, however, and it is unsafe to assume it is the sole material token.

### Corrected conclusion

> The likely exposure includes all data and actions available to a script executing in the TrustSquare origin during the exposure period: browser-held tokens, profile data, form inputs, identity-verification data, API requests/responses, and privileged actions available through active sessions. `ms_admin_token` is a priority investigation item, not a proven exposure ceiling.

---

## 3. “Rotate three secrets, not twenty.”

**Verdict: DISAGREE**  
**Severity: MAJOR**

Rotating all twenty environment variables without evidence would be operationally costly and not automatically justified. However, rotating only `MS_JWT_SECRET`, `MS_REVIEW_SECRET`, and `MS_ADMIN_PASSWORD` is not adequately supported.

### Secrets/tokens that need immediate review and likely rotation

| Material | Why it requires action |
|---|---|
| `MS_JWT_SECRET` | Required to invalidate potentially stolen JWTs **if** JWT verification properly checks signature and expiry. |
| `MS_REVIEW_SECRET` | Required to invalidate the stated 14-day reviewer JWTs. |
| `MS_ADMIN_PASSWORD` | Required if the admin credential was entered in a page exposed to the third-party script or if it protects a route reachable through a compromised session. |
| `MS_ADMIN_KEY` | Must be investigated and likely rotated because the brief explicitly records `ms_admin_token` being sent as `X-Admin-Token`, while a similarly named server-side `MS_ADMIN_KEY` exists. The relationship is unknown and potentially critical. |
| `ADMIN_KEY` | Same concern: the deployment has both `ADMIN_KEY` and `MS_ADMIN_KEY`, while browser storage contains an admin token. The token validation path must be inspected before deciding this is safe to retain. |
| Any long-lived browser/API bearer token not listed as an env var | Must be revoked/rotated at the token/session layer, not merely through secret rotation. |
| Magic-link signing/verification secret, if distinct from `MS_JWT_SECRET` | Must be identified. The brief says authentication uses magic links, but does not identify the signing or verification material. |

### Secrets that do not need automatic rotation solely because Drive ran

The following do not appear to need emergency rotation **on the evidence supplied**, provided investigation confirms they were never sent through browser-accessible requests, logs, or error responses:

- `ANTHROPIC_API_KEY`
- `AERODATABOX_KEY`
- `BREVO_API_KEY`
- `DUFFEL_ACCESS_TOKEN`
- `GMAIL_APP_PASSWORD`
- `HETZNER_S3_ACCESS_KEY` / `HETZNER_S3_SECRET_KEY`
- `JUSTTCG_API_KEY`
- `PAYSTACK_SECRET_KEY`
- `RESEND_API_KEY`
- `CF_CACHE_TOKEN`
- `MS_DEPLOY_KEY`

That is a conditional assessment, not a clearance. The relevant question is not merely “was it in static HTML?” but:

> Did a browser-accessible request, response, upload URL, source map, error path, endpoint, client-side configuration object, or deployed backup expose it?

### Specific concern: rotating signing keys may not revoke active tokens as assumed

The claim assumes all JWT-bearing routes validate signatures against the current secret and reject expired tokens. That must be tested. If tokens are opaque server-side tokens, changing `MS_JWT_SECRET` may do nothing. If a route accepts `X-Admin-Token` as a static value, rotating only `MS_ADMIN_PASSWORD` may do nothing.

### Corrected conclusion

> Do not blindly rotate every provider secret. Immediately rotate/revoke all browser-session and privileged-token material; determine the relationship of `ms_admin_token` to `MS_ADMIN_KEY` / `ADMIN_KEY`; rotate those keys if related or if uncertain; and verify revocation behavior with real tests. Retain provider secrets only after reviewing browser-visible requests, responses, logs, source maps, and upload flows.

---

## 4. “The payload contents are unrecoverable from the operator’s side, because the POSTs went browser → vendor without traversing the server.”

**Verdict: DISAGREE**  
**Severity: MAJOR**

It is correct that TrustSquare’s origin logs ordinarily would not contain browser-to-`tp-em.com` POST bodies. It is not correct to declare the data unrecoverable.

### Potential evidence sources

1. **Travelpayouts / `tp-em.com` records**  
   The vendor is the most likely custodian of request payloads, request metadata, account configuration, linked subprocessor records, and retention schedules. TrustSquare should immediately issue:
   - a preservation request;
   - a request for all data associated with project ID `557391`;
   - a request for endpoint payload schemas and actual retained fields;
   - a list of subprocessors and processing locations;
   - an incident/security contact request;
   - deletion/suppression instructions if legally and contractually appropriate.

2. **Browser artifacts**  
   Devices used by the founder/testers may retain:
   - Chrome/Firefox network caches;
   - DevTools network exports/HAR files;
   - browser history;
   - service-worker and Cache Storage entries;
   - screenshots;
   - endpoint security / EDR telemetry;
   - locally retained DNS and network telemetry.

   This is not likely to reconstruct every historical visitor’s POST body, but it can establish the exact code, request format, and potentially captured test payloads.

3. **Corporate/network infrastructure**  
   If any traffic crossed a managed proxy, secure web gateway, DNS resolver, VPN, endpoint agent, or packet-capture system, there may be timing, domain, URL, and possibly payload metadata. TLS normally prevents payload recovery at ordinary DNS/CDN layers, but metadata remains useful.

4. **Vendor-facing and legal evidence**  
   The vendor’s contractual records, privacy records, data-processing documentation, support tickets, and legal preservation process may establish data categories even if raw payloads are no longer retained.

5. **Cloudflare and origin records for related context**  
   Cloudflare cannot normally provide the third-party POST body, but it may establish which TrustSquare pages were served, cache status, visitor volume, request timing, and exposure period. Origin logs may identify identity-flow usage and relevant page/API actions during the window.

### Corrected conclusion

> TrustSquare probably cannot reconstruct historical `tp-em.com` POST payloads from its own origin logs alone. It is unsupported to call them unrecoverable. Preserve browser/network evidence and urgently obtain retention, payload, and processing information from Travelpayouts and its relevant entities.

---

## 5. “A country-scoped Cloudflare block is adequate as a short-term pre-launch gate.”

**Verdict: DISAGREE**  
**Severity: BLOCKER**

A country allow rule is not an authentication mechanism and is not adequate as the stated pre-launch gate without additional controls.

### Direct-origin bypass is not ruled out

`assets\nginx_marketsquare.conf` contains a server block intended to reject direct raw-IP access:

```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name 178.104.73.239;
    ...
    return 444;
}
```

This does **not** prove that a request sent to the origin IP with:

```http
Host: trustsquare.co
```

will be rejected. Under nginx server selection, a request reaching the origin with `Host: trustsquare.co` can select the `server_name trustsquare.co www.trustsquare.co` server block and receive the real application. The raw-IP server block only handles the IP hostname/default-server selection; it is not an origin firewall.

No supplied configuration shows:

- a Hetzner firewall restricting inbound 80/443 to Cloudflare IP ranges;
- host firewall rules (`nftables`, `iptables`, `ufw`) doing the same;
- protection of IPv6 origin addresses;
- protection of old DNS records, alternate hostnames, staging domains, or direct service endpoints;
- origin authentication from Cloudflare, such as Authenticated Origin Pulls;
- testing of direct-origin requests with `Host: trustsquare.co`.

If the origin IP is known, discoverable from historical DNS, leaked in mail headers, GitHub/deployment materials, certificate transparency, or found by scanning, the Cloudflare WAF rule can be bypassed.

### A South Africa allow rule is not an access-control boundary

If widened to the entire country, the rule allows any user who can obtain a South African IP address, including:

- VPN users;
- bot operators;
- compromised South African endpoints;
- mobile/ISP NAT users;
- unwanted visitors located in South Africa;
- attackers using cloud/VPN exit points accepted by Cloudflare geolocation.

This is materially weaker than allowing named testers through a real authentication layer.

### The existing rule is containment, not a repaired authorization model

The application’s anonymous API authorization defects still exist behind the WAF. The changelog at `changelog.d\2026-08-03-edge-prelaunch-gate.md` states:

> “No phase 2 needed.”

I disagree. The edge rule means the routes are presently unavailable through Cloudflare to non-allowlisted source IPs. It does not repair endpoint authorization, does not secure a bypassed origin, and will cease protecting the API when removed for launch.

### Corrected conclusion

> A narrowly scoped IP allowlist may be acceptable for hours/days of emergency containment only after proving the origin is reachable solely through Cloudflare and all hostnames are covered. A country allowlist is not an adequate pre-launch access-control solution. Implement origin-side authentication/authorization before expanding access.

---

## 6. The exemption set: `/health`, `/payment/webhook`, `/.well-known/`

**Verdict: DISAGREE — the exemption set is not demonstrated safe**  
**Severity: MAJOR**

### `/health`

It may be necessary for automated deploy rollback, but it remains publicly reachable and therefore must be treated as an endpoint.

Required verification:

- Does it reveal version, commit SHA, environment, hostname, database status, dependency status, or secrets?
- Is it strictly read-only?
- Is it rate limited?
- Can the deploy process instead use a private localhost/origin-only health check?
- Is the endpoint reachable directly at the origin?

A public health endpoint is often acceptable, but its response must be deliberately minimal. Nothing supplied verifies that.

### `/payment/webhook`

This must be externally reachable, but it is a high-value public attack surface. The WAF exception permits access from anyone to that exact path; safety therefore depends entirely on application-layer controls not provided in this review.

Required controls include:

- accept only the intended HTTP method, normally `POST`;
- validate Paystack’s signature before parsing or acting on the payload;
- use constant-time signature comparison;
- enforce small request-size limits and expected content type;
- reject stale/replayed events;
- make event handling idempotent;
- return non-sensitive errors;
- rate-limit abusive requests;
- ensure no alternate payment-webhook routes exist;
- verify it cannot be used to create payment state before signature verification.

The supplied configuration does not establish any of these.

### `/.well-known/`

This is the weakest exemption.

The WAF rule allows every request beginning with `/.well-known/`:

```text
not starts_with(http.request.uri.path, "/.well-known/")
```

That is broader than the ACME need. It exposes arbitrary paths beneath that prefix to the origin. Further, `assets\nginx_marketsquare.conf` contains no explicit `location` for `/.well-known/`; based on the shown config, such requests fall through to:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
}
```

Thus the assertion that this exemption is simply “certbot” is unproven. It may instead expose arbitrary `/.well-known/*` paths to FastAPI.

### Corrected remediation

- Replace the prefix exception with only the exact ACME challenge path needed, ideally `/.well-known/acme-challenge/`.
- Add an explicit nginx static `location` for that directory.
- Restrict it to `GET`/`HEAD`.
- Return `404` or `444` for all other `/.well-known/*` paths.
- Ensure the application proxy never receives ACME challenge paths.

---

## 7. Was anything missed entirely?

**Verdict: AGREE — material areas were missed or left unverified**  
**Severity: MAJOR**

The brief itself correctly identifies several important missing areas. The remediation does not demonstrate that they were closed.

### A. Four unexamined downloaded JavaScript chunks

**Severity: BLOCKER**

The loader downloaded four additional executable chunks. Their contents, hashes, behavior, and destinations are not presented. This is a direct gap in incident scoping.

The statement in `changelog.d\folded\2026-08-03-remove-travelpayouts-drive-loader.md` that the loader had “full same-origin access” is correct, but the investigation must analyze the code that actually executed, not just the first-stage loader.

### B. Cloudflare/browser caches may retain compromised HTML

**Severity: MAJOR**

The root document location in `assets\nginx_marketsquare.conf` does not set `Cache-Control: no-store` or another explicit cache policy:

```nginx
location = / {
    root /var/www/marketsquare;
    try_files /index.html =404;
}
```

The static assets location has a one-year immutable cache policy. The dashboard and command pages have no-store directives, but the root identity-flow page does not.

The review must establish:

- whether Cloudflare cached the old HTML;
- whether a purge was performed for `/`, `/index.html`, all map-page URLs, and relevant query variants;
- actual response headers before and after remediation;
- `CF-Cache-Status` behavior;
- browser cache lifetime and whether old documents can still be loaded;
- whether cached pages retain the removed loader reference.

The supplied material only says the current live HTML has no `tp-em.com` reference. It does not prove all cached copies were purged.

### C. Service worker / PWA persistence

**Severity: MAJOR**

The configuration serves a PWA manifest and long-lived static assets, but no service-worker inventory is supplied.

A cross-origin Travelpayouts script could not ordinarily register a service worker directly from `tp-em.com` to control `trustsquare.co`; service workers must be same-origin. However, an already-existing TrustSquare service worker may have cached old HTML/assets, may have unsafe `postMessage` handling, or may have been influenced through an existing same-origin upload/XSS route. This must be inspected rather than assumed absent.

Required actions:

- enumerate service-worker registration(s);
- inspect scope and script URL;
- inspect Cache Storage;
- issue a service-worker version/update/unregister strategy if needed;
- test a fresh browser profile and a previously visiting browser profile.

### D. The nine map pages remain a separate surface

**Severity: MAJOR**

The loader removal covered nine `adventures_*_map.html` pages, which is good. However, the shown nginx configuration does not explicitly serve these pages as static locations. The review should identify their live URLs and serving mechanism, then test all of them from:

- a non-allowlisted network;
- a direct-origin request;
- a browser with stale cache;
- a browser with JavaScript disabled;
- a fresh profile.

Do not infer coverage from repository file names.

### E. `*.bak-tpdrive-*` files are retained beside web files

**Severity: MAJOR**

`changelog.d\folded\2026-08-03-remove-travelpayouts-drive-loader.md` states:

> “Backups kept beside each file as `*.bak-tpdrive-20260803-185930`.”

Those backups contain the removed third-party loader and may be served accidentally now or in a future nginx/static-serving change. They also remain a contamination source in the deployment tree.

They should be removed from the web root and repository deployment artifact, retained only in a protected backup location, and explicitly tested as inaccessible over HTTP.

### F. `unpkg.com` and Google Fonts remain supply-chain/privacy dependencies

**Severity: MAJOR**

The “no third-party code may run on the app” ruling is inconsistent with the stated continued use of `unpkg.com` Leaflet and Google Fonts.

- A JavaScript dependency from `unpkg.com` is third-party executable code. Without a restrictive CSP and without SRI or self-hosting/pinning, it remains a supply-chain compromise path.
- Google Fonts is not normally executable JavaScript, but it leaks visitor IP/addressing metadata to Google and expands the privacy/data-transfer surface. CSS can also load additional resources.
- `nginx_security_headers.conf` explicitly says there is no effective `script-src` restriction. Therefore future external scripts remain unrestricted.

The no-third-party-code policy should either be implemented technically or restated honestly as “no Travelpayouts Drive loader.”

### G. Header configuration may not be active

**Severity: MINOR**

`nginx_security_headers.conf` is supplied, but `assets\nginx_marketsquare.conf` does not show an `include` directive for it. I cannot verify that the stated headers are actually emitted.

Also, even if emitted, the current CSP is only:

```http
Content-Security-Policy: frame-ancestors 'self'
```

That provides clickjacking protection but no restriction on scripts, connections, images, forms, workers, or base URLs. It would not have constrained the Drive loader.

### H. Internal documentation contradiction

**Severity: MINOR**

`changelog.d\2026-08-03-server-side-prelaunch-gate.md` correctly says the migration leaves the API open and identifies it as “phase 2.” By contrast, `changelog.d\2026-08-03-edge-prelaunch-gate.md` says:

> “No phase 2 needed.”

That latter statement is not correct as a security conclusion. The WAF masks the anonymous API from non-allowlisted Cloudflare traffic; it does not implement endpoint authentication, protect direct-origin access, or provide a launch-ready authorization model.

---

## 8. POPIA

**Verdict: INSUFFICIENT EVIDENCE for a final legal conclusion; DISAGREE with any implication that this is merely a technical incident**  
**Severity: BLOCKER**

This needs South African privacy counsel urgently. The facts supplied create a credible potential personal-information compromise, particularly because the page includes identity-document collection and behavioral profiling was enabled.

### What is reasonably clear from the supplied material

TrustSquare is likely the POPIA **responsible party** for personal information processed through its platform. A vendor processing data on its behalf is likely an **operator**, but the exact role depends on the contract and the vendor’s actual use of collected data.

The observed Drive configuration includes:

- behavioral analysis;
- targeted offers;
- automatic background-tab opening;
- cross-domain telemetry collection;
- data transfer to `tp-em.com` / Travelpayouts infrastructure;
- no consent gate;
- no established disclosure to users;
- use on a page handling identity information.

### Likely POPIA obligations to investigate

1. **Security safeguards — POPIA section 19**  
   TrustSquare must take reasonable technical and organisational measures to prevent loss, damage, unauthorised destruction, and unlawful access to or processing of personal information. Remote unpinned third-party code with unrestricted same-origin access on an identity-verification page is difficult to reconcile with that standard.

2. **Written operator controls — section 21**  
   TrustSquare should have a written contract requiring the operator to establish and maintain required security measures. The supplied “EULA disclosure clause” discussion is not a substitute for a data-processing/security agreement.

3. **Cross-border transfer conditions — section 72**  
   A transfer outside South Africa requires an applicable legal basis/condition, such as adequate legal protection, contractual obligations, consent, or another statutory condition. The claimed “Hong Kong processor” location and subprocessor chain must be verified; it is not established by the supplied material alone.

4. **Openness and notification to data subjects**  
   Processing notices must describe material aspects of collection and processing. A hidden or absent consent/disclosure mechanism for behavioral profiling on an identity-document page is a serious concern. Whether consent is the required lawful basis depends on the processing purpose and applicable provisions, but lack of transparency is independently problematic.

5. **Security compromise notification — section 22**  
   If there are reasonable grounds to believe personal information has been accessed or acquired by an unauthorised person, TrustSquare must notify the Information Regulator and affected data subjects **as soon as reasonably possible** after discovery, taking account of any needs of law enforcement. POPIA does not impose GDPR’s fixed 72-hour deadline in the wording generally applicable here; it does impose an urgency standard.

   The absence of recovered POST payloads does not necessarily defeat the “reasonable grounds” threshold. The fact that remotely controlled code executed with access to identity-flow inputs and browser-held data is significant.

6. **Records and accountability**  
   Preserve:
   - the deployed files and Git history;
   - vendor configuration screenshots/export;
   - browser HARs;
   - Cloudflare logs/cache records;
   - a timeline;
   - affected page/API scopes;
   - vendor preservation correspondence;
   - the decision process for notification;
   - remediation and testing records.

### Special category / identity-document issue

The material does not let me determine whether the identity-document process processes POPIA “special personal information,” biometric information, or unique identifiers in a manner triggering additional restrictions. An identity document photo alone should not be casually assumed to equal biometric processing, but the workflow may include facial comparison, extraction, matching, or unique-identifier processing. Counsel must inspect the actual verification vendor/process.

### Corrected conclusion

> Treat this as a potential POPIA security-compromise and unlawful/insufficiently transparent processing incident pending urgent fact-finding. Obtain legal advice on section 22 notification, section 21 operator controls, section 72 cross-border transfer conditions, and any special-information/identity-verification obligations. Do not wait for perfect payload reconstruction before making the notification decision.

---

# Additional material findings

## [BLOCKER] Cloudflare WAF can be bypassed if the origin accepts direct requests with `Host: trustsquare.co`

**Evidence:** `assets\nginx_marketsquare.conf` has a raw-IP rejection server block and a separate `server_name trustsquare.co` application server block, but no origin firewall configuration is shown.

**Why this matters:** An attacker who reaches `178.104.73.239` and sends `Host: trustsquare.co` may be served by the real virtual host, bypassing Cloudflare and its WAF rule altogether.

**Cheap verification:**

```bash
curl -k --resolve trustsquare.co:443:178.104.73.239 https://trustsquare.co/
curl -k --resolve trustsquare.co:443:178.104.73.239 https://trustsquare.co/wonders
```

Perform this from a controlled non-allowlisted system, with logging, after confirming it is permitted operationally.

**Required fix:** Restrict inbound 80/443 at Hetzner and host firewall layers to Cloudflare’s published IP ranges only, plus explicitly necessary management/monitoring sources. Review IPv6 separately. Use Cloudflare Authenticated Origin Pulls or another origin-authentication mechanism as defense in depth.

---

## [MAJOR] The “server-side gate” is unarmed and does not protect the API even if armed

**Evidence:** `migrations\005_prelaunch_server_side_gate.py` is explicitly “deliberately left unarmed” in the brief. It applies `auth_basic` only to five explicit document routes and leaves the catch-all API proxy open.

**Why this matters:** The claimed server-side remediation has not been deployed. Even if deployed, it would not protect anonymous API routes. It also leaves map-page serving behavior uncertain.

**Required fix:** Implement application/origin authorization by default, with explicit allowlist exceptions for only health, ACME, and verified webhooks. Do not rely on an IP WAF as the only authorization layer.

---

## [MAJOR] `/.well-known/` is likely reaching FastAPI rather than certbot

**Evidence:** The Cloudflare exception permits every `/.well-known/*` path. The supplied nginx site configuration contains no `location` serving ACME files, so the catch-all FastAPI proxy likely handles it.

**Required fix:** Add explicit nginx handling for only `/.well-known/acme-challenge/`, then block all other `/.well-known` paths before the proxy.

---

## [MAJOR] The “no third-party code” remediation is incomplete

**Evidence:** `changelog.d\folded\2026-08-03-remove-travelpayouts-drive-loader.md` says:

> “no third-party code may run on the app, at all.”

But the brief states the pages still load Leaflet from `unpkg.com` and Google Fonts; `nginx_security_headers.conf` confirms there is no `script-src` CSP and no SRI.

**Why this matters:** The same category of supply-chain compromise remains possible through any remote JavaScript dependency.

**Required fix:** Self-host or tightly pin/version all JavaScript dependencies; remove remote executable dependencies where feasible; deploy a tested CSP with nonces/hashes for inline event handlers or refactor away from 163 inline `onclick` handlers.

---

## [MAJOR] Backup copies of compromised pages remain in the web deployment tree

**Evidence:** The loader-removal changelog says `*.bak-tpdrive-20260803-185930` backups were retained “beside each file.”

**Why this matters:** Files containing the old loader may be publicly reachable now depending on serving rules, and become reachable after a future configuration change. They also increase the chance of accidental redeployment.

**Required fix:** Move backups out of `/var/www/marketsquare`, exclude them from deployments, and test public inaccessibility before deleting/replacing them.

---

## [QUESTION] Is `ms_admin_token` derived from or equivalent to `MS_ADMIN_KEY` / `ADMIN_KEY`?

**Evidence:** The brief identifies `ms_admin_token` sent in `X-Admin-Token`, and separately lists `ADMIN_KEY` and `MS_ADMIN_KEY` server environment variables.

**Why this matters:** If the browser token is a static admin key, then the current plan fails to rotate the exposed credential. If it is a JWT, scope/expiry/revocation must be verified. If it is opaque, signing-key rotation may not revoke it.

**Required answer:** Provide the code path for every endpoint accepting `X-Admin-Token`, including token format, validation, scope, expiry, and revocation behavior.

---

## [QUESTION] Does `/wishlist/feed?buyer_token=<32-hex>` use a bearer capability in the URL?

**Evidence:** The brief records an observed request with the token in the query string.

**Why this matters:** URL tokens can leak through browser history, client/proxy/CDN/origin logs, monitoring tooling, screenshots, and same-origin referrers. The current `Referrer-Policy: strict-origin-when-cross-origin` reduces cross-origin path leakage in normal navigation, but does not solve logs/history or same-origin leakage.

**Required fix if it is an authorization token:** Remove it from URLs; use an `Authorization` header or secure HttpOnly cookie; expire/revoke existing values; scrub logging where feasible.

---

## [PRAISE] Removing the loader from all identified pages and disabling the vendor features was the correct immediate action

**Evidence:** The brief says all ten identified pages were changed and the live HTML was checked for `tp-em.com`; vendor features were also disabled.

This is materially better than merely changing a vendor-panel setting, because observed `/collect` calls continued until the script itself was removed.

---

## [PRAISE] The brief correctly recognizes the client-side pre-launch overlay as non-security control

**Evidence:** Both the brief and `migrations\005_prelaunch_server_side_gate.py` accurately describe the JavaScript gate as a “curtain, not a door.”

That diagnosis is sound. The remaining issue is that the actual server-side control was left unarmed and the edge workaround must not be mistaken for repaired application authorization.

---

# Corrected remediation plan

## Immediate — before widening access beyond the founder

1. **Prove or close direct-origin access.**  
   Block origin 80/443 except from Cloudflare IP ranges at Hetzner and host-firewall layers. Test direct-origin access with `Host: trustsquare.co`. Cover IPv4, IPv6, historical DNS, alternate hostnames, and non-Cloudflare service exposure.

2. **Do not widen the WAF rule to South Africa.**  
   Keep a narrow named-tester IP allowlist only as emergency containment, or deploy actual authentication first. A country rule is not a secure gate.

3. **Apply a real origin-side access gate.**  
   The unarmed `auth_basic` migration is better than the cosmetic overlay but insufficient alone. Protect documents, APIs, map routes, static routes that expose sensitive content, and alternate pages by default. Maintain explicit minimal exceptions.

4. **Tighten the three public exceptions.**
   - Make `/health` minimal and preferably private/origin-restricted.
   - Validate `/payment/webhook` signature before processing; add replay/idempotency/size/method controls.
   - Replace broad `/.well-known/` allowance with a static ACME-only location and deny the remainder.

5. **Revoke/rotate browser-accessible and privileged credentials.**
   - Rotate `MS_JWT_SECRET`, `MS_REVIEW_SECRET`, and `MS_ADMIN_PASSWORD`.
   - Investigate and likely rotate `MS_ADMIN_KEY` and `ADMIN_KEY`.
   - Revoke active tokens/sessions directly, rather than assuming secret rotation is sufficient.
   - Test old admin/review/user tokens after rotation.

6. **Preserve incident evidence before it expires.**
   - Export Travelpayouts configuration and account records.
   - Preserve HARs, browser profiles/caches from testing devices, Cloudflare logs, origin logs, Git commits, deployed artifacts, and timeline.
   - Send vendor preservation and data-processing requests.

## Near-term — complete incident scoping

7. **Acquire and analyze the loader plus all four chunks.**  
   Hash them, retain copies, identify all network destinations, inspect DOM/event/network interception behavior, and document actual data schemas sent to `/collect` and `/collect_batch`.

8. **Investigate all data-bearing browser flows.**
   - identity-document upload implementation;
   - magic-link issuance/redemption;
   - `X-Admin-Token` authorization;
   - reviewer JWT authorization;
   - URL token use such as `buyer_token`;
   - API response data accessible before login.

9. **Purge and verify caches.**
   - Purge Cloudflare for all affected URLs.
   - Check cache headers and `CF-Cache-Status`.
   - Inventory service workers and Cache Storage.
   - Test fresh and previously visiting browser profiles.

10. **Remove compromised backups from web-serving paths.**  
    Retain them only in protected incident-evidence storage.

## Launch-hardening

11. **Replace the current CSP posture.**  
    `frame-ancestors 'self'` is not a script-control policy. Refactor inline event handlers or adopt nonce/hash-based patterns, then implement restrictive `script-src`, `connect-src`, `img-src`, `form-action`, `base-uri`, and `object-src` directives. Use CSP reporting during rollout.

12. **Eliminate or control third-party executable supply chain.**  
    Self-host Leaflet or pin/version it with integrity controls where appropriate. Treat Google Fonts as a privacy dependency; self-host fonts if minimizing third-party visitor disclosure is required.

13. **Perform endpoint-by-endpoint AuthN/AuthZ review.**  
    The observed anonymous `200` responses to `/wonders`, `/flags`, `/local-market/listings`, `/geo/cities`, `/tuppence/balance`, and tokenized wishlist endpoints need a documented classification:
    - intentionally public;
    - authenticated;
    - admin/reviewer-only;
    - internal-only.

    “Behind Cloudflare WAF for now” is not an endpoint authorization design.

14. **Obtain POPIA legal review and make notification decision promptly.**  
    Establish the Travelpayouts processor/subprocessor chain, data categories, cross-border basis, section 21 contract posture, and whether section 22 notice is required.

---

# What I would have done differently

1. I would have immediately treated this as a **same-origin third-party script compromise**, not primarily as a static-secret scan problem.
2. I would have blocked the origin at the network layer first, then used Cloudflare as an additional control rather than the sole pre-launch barrier.
3. I would have preserved and analyzed the executed chunks before concluding anything about the payload or exposure ceiling.
4. I would have revoked all browser-accessible sessions/tokens and investigated the admin-token validation path before choosing which secrets to rotate.
5. I would have initiated vendor preservation/privacy inquiries immediately, before logs and configuration evidence aged out.
6. I would not have widened access to a country until a real authenticated pre-launch mechanism existed.
7. I would have removed compromised backups from the web root and purged/verified browser/CDN caches as part of the initial containment.

---

# What is still unsafe right now

- **Potential direct-origin access is unprovenly blocked.** The supplied nginx configuration does not prevent a direct request to the origin IP using `Host: trustsquare.co`.
- **The application’s anonymous API authorization model remains unresolved.** The WAF only masks it for non-allowlisted Cloudflare traffic.
- **The unarmed nginx server-side gate is not protecting anything.**
- **A country-scoped allowlist would permit unauthenticated access by a broad attacker population.**
- **`/.well-known/` is an unnecessarily broad public exception and may route to FastAPI.**
- **`/payment/webhook` security cannot be assessed from the supplied material.**
- **Potentially compromised admin, reviewer, user, and URL-carried tokens have not been conclusively revoked.**
- **The executed Travelpayouts chunks and their collected payload formats remain unexamined.**
- **Identity-document and form-input exposure has not been scoped.**
- **Old compromised content may remain in CDN, browser, or service-worker caches.**
- **Compromised backup files remain beside deployable web files.**
- **Remote executable dependency risk remains through `unpkg.com`, with no restrictive CSP.**
- **POPIA notification, processor-contract, and cross-border-transfer obligations have not been resolved.**

---

# Three findings the System Engineer should discuss first

1. **BLOCKER — Origin bypass:** Is `178.104.73.239` reachable directly with `Host: trustsquare.co`, bypassing Cloudflare and the WAF? If this has not been tested and network-restricted, the current containment may be bypassable.

2. **BLOCKER — Exposure ceiling:** Why is this being characterized as chiefly `ms_admin_token` and profile data when the compromised script had same-origin access on an identity-document upload page? The upload and token authorization paths need code-level investigation and revocation.

3. **BLOCKER — POPIA/vendor evidence:** Have Travelpayouts and relevant `tp-em.com` operators received a preservation/data-processing request, and has counsel assessed the section 22 notification threshold? The lack of local POST logs is not a basis to defer this.

---

# What I could not verify from the supplied material

I could not verify:

- whether direct-origin traffic is blocked by Hetzner firewall, host firewall, Cloudflare Authenticated Origin Pulls, or other controls not shown;
- the FastAPI route implementations, including authorization on every endpoint;
- the semantics, expiry, scope, and revocation behavior of `ms_admin_token`, `ms_review_token`, `buyer_token`, JWTs, magic links, `ADMIN_KEY`, and `MS_ADMIN_KEY`;
- whether the supplied nginx headers file is actually included in the live nginx configuration;
- the contents and behavior of the Travelpayouts loader chunks;
- whether identity documents or file uploads were actually transmitted/exfiltrated;
- whether Cloudflare/browser/service-worker caches retained the compromised pages;
- whether the map pages and backup files are publicly reachable;
- webhook signature, replay, idempotency, and input-validation controls;
- Travelpayouts’ legal entity, actual processing location, retention practices, subprocessor chain, or contract terms;
- the final POPIA legal notification obligation, which requires fact development and qualified South African legal advice.
