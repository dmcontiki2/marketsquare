## 2026-09-24 — authz_probe folded into the QA Bot (one probe, not two)

Earlier today the attended CTO pass built `scripts/authz_probe.py` as a stop-gap live
authorization probe (it found and got fixed the anonymous `/admin/purge-cache` hole,
ADMIN-LOCALGUARD-1). The parallel QA-BOT-1 session then landed `qa_bot/qa_bot.py`, an
independent auditor that supersedes it on every axis: OpenAPI-derived coverage of every
route, three attack personas incl. a real signed-in intruder against a real victim account,
OpenAI ruling each route's required class, on-box execution (behind Cloudflare, no UA trap),
snapshot/restore of victim data, and a deploy gate + nightly run.

Consolidated to one probe: `scripts/authz_probe.py` is now a deprecation stub that points to
`qa_bot/qa_bot.py`. Confirmed no coverage lost — the server policy already rules every route
the stop-gap probed, and its rulings match today's fixes (keep-live/cities/wonders/photo =
owner; experience/zoom = session; agency verify/rename + trust-score/credential = admin).
The three admin-intent routes the probe surfaced (AUTHZ-CONSOLE-KEY-1 / DW-153) are ruled
`admin` by the bot and are now attacked and deploy-gated by it — the QA Bot is the authority
on whether they are closed.
