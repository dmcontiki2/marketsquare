# Decision Brief — Account Binding for Paid Actions

*5 August 2026 · AI-SERVICES-AUDIT-1 Finding F1 (Peer round-2 BLOCKER) · for David's decision · no code changed*

## The hole, in one paragraph

Every paid AI endpoint takes the account to charge as a plain parameter — the caller
simply states which email pays. The only thing in front of these endpoints is one shared
API key, and that key ships in plain sight inside the front-end JavaScript (ms.js), so
anyone who opens page source has it. Nothing ties the key-holder to the email being
charged. Identity is asserted, never proven.

**Why it is a blocker, not a nuisance:** anyone who views source can drain a specific
seller's Tuppence by running AI on that seller's own listing, and Price Check / Yield
charge whatever email is passed with no ownership tie at all. It is an authorization hole,
and exactly the class of thing that must not be open at launch.

## Why it is bigger than the AI services

Not a bug in the five AI endpoints — it is the app's whole identity model. The same
shared-key-plus-passed-email pattern runs many write and charge paths. That is why I did
NOT hot-patch it: fixing one place while the pattern lives everywhere gives false comfort.
It needs one deliberate decision applied consistently — yours to make.

## The good news — the mechanism already exists

The app already issues a per-visitor session token (ts_review cookie / X-Review-Token) and
already uses it to authenticate the in-app fault reporter (`_fault_caller_ok`) by tying a
caller to their own identity. The fix is to make paid/charging endpoints derive the charged
account from that session instead of a passed parameter — reusing plumbing already in the
codebase, not a new auth system.

## Options

| Option | What it means | Trade-off |
|---|---|---|
| **A · Session-bound charges (recommended)** | Charged account = the authenticated session, never a passed email. Reuses ts_review. | Best security; touches each charging endpoint once; pattern already proven in-app. |
| B · Per-user API keys | Replace the one shared key with a key per account; the key identifies the payer. | Strong, but new issuance/rotation/storage to build and manage — heavier for a solo founder. |
| C · Ownership re-check only | Keep passed email but verify it against the session on every paid call. | Half-measure: still leaks the shared key; only as good as the weakest endpoint that forgets. |

**Recommendation: Option A.** Closes the hole at the source, reuses existing machinery,
applies as one consistent rule. Scope it as its own piece — reviewed, ledger-locked,
drilled — not folded into today's AI-services fixes.

## What I need from you

One decision: A, B, or C. On your go I scope Option A across the charging endpoints, add
its regression-ledger assertion, and bring it back for the same Peer pass. Until then the
two contained fixes from this round — the KYC SSRF guard (F3, RG-0036) and the atomic spend
reservation (F2, RG-0037) — are done on disk, awaiting the next deploy.
