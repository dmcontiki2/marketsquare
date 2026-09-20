## 2026-09-20 — QUICK-SVC-DOOR-1: the Services door (RUL-159) + role registry + role pictures + language preview

David, 19-20 Sep, role-slate sitting 1 and the build that followed it.

**The slate.** `ROLE_SLATE_REVIEW.md` fully decided: 99 rows, 61 IN / 19 LATER / 19 OUT, no HOLD. Rulings made
the same session: RUL-153 (police clearance gates Nanny / Caregiver / Crèche assistant), RUL-154 (the
LATER / HOLD / ROUTED register), RUL-155 + RUL-156 (licence gate for every licence to practise), RUL-157 (one
picture of the WORK per role, photo 1 on every Services listing), RUL-159 (the door shape), RUL-160 (translation:
Claude drafts, an OpenAI Language reviewer proofreads, first-month user feedback corrects).

**The registry.** `roles/role_registry.json` is GENERATED from the slate by `scripts/build_role_registry.py`
(never hand-edited): questions, signals, gates, employer_kinds, aliases, finish_questions, enrol_link, role picture.
Board + contact sheet: `roles/ROLE_REGISTRY.html` (`scripts/role_registry_board.py`).

**The pictures.** 61 role pictures via the Higgsfield API on David's prepaid balance (auto top-up OFF);
model chosen by comparison (Soul 2 / Recraft / Ideogram / Grok Imagine 2.0 on welder, cleaner, nanny; trials kept in
`roles/pictures/_trial/`). Every one checked by eye (no people, no faces, no text) and approved by David.
`scripts/gen_role_pictures.py` (dry run by default). Door-size copies `assets/quick_ph/role_*.jpg` ride the
media lane to /static/quick.

**The door (quick.html).** Seven categories: Housekeeping folds into Services (the homehelp entry stays as the
hidden Casuals half, Services/Casuals on the wire). Services = group -> role -> class taps, five taps to a draft
for every role; the old "what" tap is gone; role-specific questions on the finish screen; `?role=<key>` enrolment
link lands on tap 3; photo 1 is the role picture; the searcher's shelf ranks soonest-available first. One engine:
a generated data block (`scripts/sync_quick_roles.py`) plus three one-line hooks — no category forked.

**Language — PREVIEW, NOT A RULING (David, 20 Sep: "only after I have had someone read it first").** The Quick
door follows the phone's language (en / zu / st / af / xh); a globe pill on every screen switches both ways;
"Languages I work in" chips on the finish screen. Words: `roles/quick_i18n.json` (143 strings x 4, Claude's first
draft, being read by David's people).

Verified in a rendered phone-width browser: every flow walked, 0 console errors, the other six categories unchanged.
Walkthroughs in the Visuals gallery: Services Door Walkthrough, Quick Door Languages.
