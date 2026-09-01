## 2026-09-01 — OUTREACH-TRIAGE-1 (RUL-087): prospect replies leave David's inbox

David, launch day, after one tutor's reply consumed an afternoon: *"these emails should not arrive
in my inbox for me to respond to. It should be answered by an AI agent. How would i respond to
100's of emails a day if we get traction?"* — then, on the design: *"Green light given"*.

**RUL-087 recorded**, amending RUL-069 in part. That ruling deliberately excluded this lane
(*"B2B recruitment mail David owns personally"*) — right while reply volume was zero, a scaling
defect the moment the waves landed.

**No new mail infrastructure.** The existing `cloudflare_email_worker` → `/email/inbound` →
`email_triage` engine, E2E-proven 24 Aug for support@, gains a THIRD mail class. Reuse before
recreate, applied.

**Built in `bea_main.py`:**

- `_is_outreach_lane()` + `_OUTREACH_ADDRESSES` (env `OUTREACH_REPLY_ADDRESSES`, default
  `david@trustsquare.co`). Six-case unit check passes, including the near-miss
  `david@mail.trustsquare.co` — the SENDING subdomain, which must NOT be treated as the reply lane.
- A separate classifier prompt for the lane, fed only from canon (national coverage and the live
  city list, free listing, seller sets rate, BUYER pays the introduction fee, no commission on the
  seller's own fees, anonymity until accept, local/online/both). Explicitly barred from inventing
  pricing, dates or features, and told to fall back to `outreach_commercial` when unsure — a human
  reading it is cheap, a wrong automated answer to a prospect is not.
- Four classes: `outreach_machine` · `outreach_faq` · `outreach_optout` · `outreach_commercial`.
- Lane-aware auto-send gate. `outreach_machine` → **silent log, live from day one** (answering an
  autoresponder can never be right — an Addico autoresponder is precisely what cost the afternoon).
  Everything else DRAFTS and queues; `OUTREACH_AUTO_SEND=1` later graduates the FAQ class alone,
  and only on measured accuracy.
- `_smtp_send_reply()` gained `from_email` / `reply_to` so this lane answers as
  `David at TrustSquare <david@mail.trustsquare.co>` with Reply-To `david@trustsquare.co` — the
  wave's own identity — instead of TrustSquare Support.
- **The MAINT-B1 fault-queue ack is barred on this lane outright.** A tutor asking whether we cover
  Johannesburg has not filed a fault, and *"your report is logged in our fix queue"* would be
  nonsense to a prospect. This was a live hazard: the ack fires for any non-spam mail carrying a
  fault_code, and this lane routes through the same handler.

**RG-0236 stays OPEN, and its assertion is now red-capable** against regression: ripping
`_is_outreach_lane`, `outreach_machine` or the graduated gate out of `bea_main.py` produces three
FAILs (proven against a fixture repo before the green was believed). It promotes only when routine
prospect replies are answered with David's inbox out of the path, PROBED on real traffic —
**shipped is not measured**, which is the whole lesson of the leak found the same morning.

**David's acts to finish it:** deploy (publish the `deploy` ref, per ONE-DEPLOY), then let the
first real replies land and read the classifier's calls in `/admin/email-triage` before anyone
turns `OUTREACH_AUTO_SEND` on.

Verification this session: `py_compile` clean · lane unit cases 6/6 · `rulings_check.py` 87
rulings, 0 FAIL, RUL-087 reflected · RG-0236 red-capability proven on a fixture.
