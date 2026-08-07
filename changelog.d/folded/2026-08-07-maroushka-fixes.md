## 2026-08-07 (evening) — MAROUSHKA'S 7 AUG REPORTS + SELFCHECK-1 (David: "Build 1 after Maroushkas fixes")

Six faults closed, one endpoint built, one instrument repaired. Everything below is local until
`/ship` runs. The stale `.git/HEAD.lock` that made this morning's deploy a silent no-op (DW-026)
has been moved aside, so the ship can actually land.

**TS-0026 — "the pictures didn't pull through, there was no notice."** Two bugs, not one.
The batch-publish loop surfaced ONLY HTTP 422; a 400 (a format the server could not decode) and a
dropped request both vanished, and the single-photo advert path swallowed everything with
`.catch(()=>{})`. The advert published photo-less and said nothing. Both paths now name the photo
number and quote the server's own reason. The first cut of this fix pushed to `_photoFails` without
ever declaring it — `node --check` passed and the runtime would have thrown `ReferenceError` on the
first failing photo, breaking publish outright. Caught before ship; the declaration now sits at
block scope and is proven in scope at every use by brace-depth walk.

**The 502 was not a photo bug.** Her console showed `/listings?city=Pretoria` returning 502 while
publish 333/334/335 all returned 200. Checked from outside: all three listings carry populated
`photo_urls`, every R2 URL resolves 200 (10, 6 and 2 photos respectively), and `thumb_url`/
`medium_url` are set. The photos were never lost. Five timed probes of the same endpoint returned
200 in 0.65-1.18s, so the 502 was the restart window of this morning's failed deploy, not a chronic
fault. Nothing to fix; recorded so it is not chased again.

**TS-0025 — HEIC (PHOTO-TYPE-1).** The gate compared the browser's DECLARED `Content-Type` against
an allow-list. Windows and Android send `application/octet-stream` (or nothing) for a `.heic`
straight off an iPhone, so a photo `pillow-heif` can decode perfectly was refused — and refused
with "Only JPEG, PNG or WebP photos accepted", which was ALSO false whenever the wheel is present.
The bytes are now the gate: a supported or generic declared type passes through to `Image.open()`,
which is the real validator, and every rejection names what we actually accept. A decode failure on
iPhone bytes with no wheel present says so specifically and gives the Share > Options > Most
Compatible route out, instead of the blanket "could not read image file". Applied at all four
upload gates plus a byte-level HEIC sniff on the ID path (which stores raw bytes and would
otherwise have filed an unviewable document). 10/10 offline cases pass, including her exact one:
`ct=application/octet-stream` + `IMG_1.HEIC`.

**TS-0013 — "it doesn't allow me do upload it or verify my status as an agent."** The Agent Hub
credential upload was the ONE `/documents` POST in the app that omitted the `X-Api-Key` header,
against a route guarded by `Depends(auth.require_api_key)`. It returned 401 on every attempt, for
every user, since the day it shipped — never a permissions or account problem; that button could
not have worked for anybody. Its two sibling calls always sent the header, which is why the fault
looked user-specific. Also fixed on that path: `visibility:'ops'` was not a value the server
accepts and was silently coerced to `'private'` (now says what it does), and the document gate had
the same generic-Content-Type trap as TS-0025 — a phone photo of a certificate was refused outright.
HEIC documents are now converted to JPEG on the way in, because that path stores raw bytes and ops
cannot open a HEIC.

**RESEND-FROM-1 completed.** One sender was still reading the env raw:
`os.getenv("SUPPORT_FROM_EMAIL", ...)` on the credential-decision mail. Bitter irony — that mail
exists to fix TS-0010 (a credential decision that reached Maroushka silently), so an unverified or
malformed sender there would have re-created the exact silence it was built to end. Wrapped.
Unwrapped senders remaining: zero.

**SELFCHECK-1 — `GET /ops/selfcheck` (David's "Build 1").** A session cannot open an SSH tunnel to
the box (port 22 is firewalled to David's IP), so every "is that dependency actually installed / is
the flag actually on / did the deploy actually land" question cost a manual round-trip through
David — and on 5 Aug one of them was answered by inference instead of evidence and had to be
retracted. This endpoint answers them over one authenticated HTTPS GET: deploy stamp and uptime,
dependency presence (`pillow_heif` first among them), AI lanes configured by NAME, launch-switch
states, fault counts by status, today's AI spend and active holds, live listing count, and
since-boot request/4xx/5xx counters with the last 5xx path. Facts only — no secrets, no keys, no
customer data, no fault text; every block independently guarded so a partial failure still yields a
usable report and nothing is ever guessed. Gated on the existing shared API key, so it needs no new
env var (the ENVKEY-1 lesson: systemd does not export the server `.env`).

**LEDGER-OFFLINE-1 — the instrument was lying.** Run from a machine with no route to the site, the
regression ledger reported 15 network-backed entries as `REGRESSION: Tunnel connection failed` and
closed with "Do not deploy over this." That is the cry-wolf failure: a tripwire that reports the
instrument as the app teaches you to ignore the tripwire. A one-time cached preflight now
distinguishes a transport failure from an HTTP answer (any status means the site replied and every
check is valid), and unreachable entries report as **UNVERIFIED** — loudly not a pass, messages
still printed, exit code 2 for "blind" versus 1 for "regressed" and 0 for genuinely clean. Same
rule as LEDGER-FAULT-1 before it: a skip is "unverified here", never "now passing". The board went
from *16 REGRESSED* to *0 regressed, 18 unverified* — the truth. Nothing consumes the exit code, so
the deploy path is unaffected.

**Tripwires added:** RG-0040 (a photo is judged by its bytes, never the browser's claim),
RG-0041 (a photo that does not upload always says so), RG-0042 (the ops self-check publishes facts
and never a secret), RG-0043 (every client upload to a key-guarded endpoint actually carries the
key). All four green. RG-0041's own first version matched the `.catch(()=>{})` written inside the
comment documenting the old bug and reported a regression against a correct file — corrected to
scan code only, because a tripwire that cries wolf gets ignored.

**TS-0022 — PHOTO-REPLACE-1, David's ruling 7 Aug.** Third report of the same complaint
(TS-0007, TS-0008, now this), so it was treated as a doctrine change rather than a third patch.
The blur was already minimal and already vision-driven — a model boxes the region, a zoom-in
refine pass tightens the coordinates, and the mask is a feathered capsule aligned to the text
angle. The sprawl came from the OTHER rule: the pipeline was forbidden to reject a photo (15 Jul:
"a seller photo must NEVER be held because the pretty blur could not be verified — ugly-but-
anonymous beats rejected"), so it escalated instead — four correction rounds, each re-scanning the
already-blurred image and painting the new boxes on top of the old, then a last-resort rung
blurring every region ever accumulated. David reversed it in Maroushka's own terms: "if we cant
blurr a photo enough and it starts looking bad, then we should request a replacement rather."

Coverage is now measured before each new layer and before the last-resort rung, by UNION rasterise
onto a grid so the same plate boxed across four rounds counts ONCE — summing box areas would
double-count the accumulation and start refusing perfectly good photos. Above 18% of the frame the
photo is refused and the seller is asked for a different one, in words that name the real problem:
hiding the details would spoil the picture, so a generic "could not blur" would have sent them back
to retake a photo that fails the same way. Offline: a typical plate reads 2.5%, a plate plus dealer
strip 4.6%, the same plate boxed four times still 2.5% (union proof exact), and the TS-0007/0008
"half the facade" case reads 61% and is refused. Normal photos are untouched.

Behind `launch_switches.photo_replace_request`, default ON, ceiling tunable via
`ANON_MAX_BLUR_FRAC` without a code change; OFF restores the July behaviour without a deploy. The
switch reader fails SAFE — any doubt reads as ON. Worth stating plainly, because it is why this was
safe to build on a ruling rather than a review: **this direction cannot weaken anonymity.** Refusing
a photo cannot leak what the blur failed to hide. On the Launch Switch page it carries the same
OFF/ON/implication hover explainer as its neighbours. Tripwire RG-0044 asserts the measure, the
fail-safe default and the honest wording all stay.
