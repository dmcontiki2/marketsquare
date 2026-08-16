## 2026-08-16 — Orchestrator: Email Templates view added · Durability Map 404 fixed
David's ask: the pre-launch email waves need eyeballs on the templates. New third view on
the Orchestration v2 page (next to Control Room and Durability Map): email_templates.html
— all 14 templates as live scaled previews with context (agency vs individual lane,
Trust-Score story 85/82/81/77/74, unsubscribe/launch-special/magic-link/Ruby-Spark chips,
snapshot date) and click-through to the real template HTML. Snapshots copied from
CityLauncher/emailer/templates (ZA canon; UK/US/AU localization layer separately in build).
DURABILITY-404-1: the Durability Map was broken because durability_map.html never had a
deploy-manifest row — the cockpit linked a file that never shipped. Manifest now carries
durability_map.html + email_templates.html + the 14 template snapshots (16 rows).
RG-0095 LOCKED: all three orchestrator views must answer 401-behind-auth, never 404.
Cost model impact: none — static pages on the existing auth lane.
