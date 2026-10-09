# RUL-217 Trainers door build — progress (scheduled run, 10 Oct 2026 SAST)
- [x] ledger BEFORE: shard 1/3 run in sandbox; host-side full run queued (host_queue 20261009-004442-956)
- [x] ROLE_SLATE_REVIEW.md: '# TUTORS — TRAINERS' section, 47 rows, 8 groups (bak-rul217-*)
- [x] scripts/build_role_registry.py: Trainers class, steps, signals, gates (28 clearance), aliases, AF names, picture prompts; CARWASH-1 hand edit carried into the builder (ROLE_PATCH)
- [x] roles/role_registry.json regenerated: 155 roles, non-trainer rows byte-equal to before
- [x] roles/pictures/<trainer>.png x47 — INTERIM illustrations (Noto Color Emoji objects, no people); photoreal set = gen_role_pictures.py --go (spend, David)
- [x] roles/quick_i18n.json: 65 trainer words x 15 languages (scripts/apply_trainers_i18n.py, Claude drafts RUL-160)
- [x] scripts/sync_quick_roles.py: QUICK-TRAINERS block (TRN_ROLES/TRN_GROUPS) + assets/quick_ph/role_<trainer>.jpg
- [x] quick.html + genie/HARNESS.html: scripts/apply_trainers_quick.py (door, rate units, catOut, payload, find example) -- headless test PASS (Tutors/Trainers/Soccer coach/R250 / session, 0 JS errors)
- [x] bea_main.py: GET /examples/trainers + _TRN_SESSION_RATE, Tutors-Trainers trust key, specialisation badges, tutors gate (apply_trainers_bea.py) + TRAINERS-GATE-1 clearance credential (apply_trainers_gate.py); route_policy.json declares the route
- [x] ms.js: trainer examples in Tutors + sheet 'I train people in this — list me free' + typical rate (apply_trainers_ms.py)
- [x] stories: 47 trainer How guides (build_trainer_guides.py), gallery + manifest (build_help.py), screens pushed to /help/img
- [x] role pictures (47 jpg) uploaded to /static/quick (media lane equivalent; nightly media_push will see them unchanged)
- [x] ledger RG-0949 (PASS in repo; renumbered from RG-0947, which Goal run 33b shipped first) / RG-0948 (live half after deploy); rulings_check RUL-217
- [x] merged origin/main (Goal run 33b) by hand -- merge commit 5749e92; deployed via request_deploy relay (live ~01:40 UTC 9 Oct / 03:40 SAST 10 Oct)
- [x] LIVE: /examples/trainers answers (af: Sokkerafrigter / Jou sessietarief / R300); role pictures 200; Chrome: Quick Tutors door shows Sport & fitness -> groups -> sports with pictures -> Per session/month/package (no floor), How = swimming_coach guide (200); TrustSquare: 47 trainer examples, Tutors tile 52, sheet 'I train people in this — list me free' + typical rate
- [x] ledger AFTER: 5 regressions, all pre-existing (RG-0154, 0234, 0344, 0840, 0871); RG-0948 + RG-0949 pass live
- [ ] NOT DONE: photo-real pictures (paid run ~US$3, David's call); own Quick screens for the trainer How guides (role_guide_screens.py) -- guides use the walked Tutors screens
DONE
