## 2026-08-05 — Introduction relay: Option B selected, build spec written

- David chose Option B (masked-alias relay) as the introduction mechanism, over direct-email
  (status quo) and on-platform messaging. Reasoning: fewest added parts for full anonymity +
  "neutral ground" legal posture (we disclose nothing, we relay). Comparative brief in
  Records/INTRODUCTION_MECHANISM_BRIEF.
- DOCTRINE RULED (David, 5 Aug 2026): "Nothing of the customer's leaves TrustSquare except a
  consented, revocable email channel — never the address itself." To be enshrined in CLAUDE.md.
- Build spec: Records/INTRO_RELAY_BUILD_SPEC (+ nice docx). Reuses Cloudflare Email Routing +
  Worker (inbound, like /email/inbound) and Resend (outbound, _smtp_send_reply lane) — NO new
  subscription. New: intro_relay_aliases table, POST /intro/relay (X-Relay-Secret), _relay_forward
  helper, and the accept_intro change that STOPS leaking both raw emails to the n8n webhook.
  One-way-first scope; behind launch_switches.intro_relay (fail-closed/dark). Folds into the F1
  account-binding pass as one "who sees what, who pays" change; Peer-reviewed before any live intro.
- David's console prerequisites before end-to-end: CF Email Routing alias route + MX, RELAY_INBOUND_SECRET
  env, Resend authorised for *@relay.trustsquare.co. NOT code — the one part not doable from a session.
- STATUS: awaiting David — build P1 now behind the dark flag, or hold for the console prerequisites first.
