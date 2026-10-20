# SNAP_PROGRESS — the Snap lane build (QUICK_SNAP_BRIEF.md §8). Read this FIRST; continue from NEXT. Never redo a committed unit.
Worktree `_snap_wt/`, branch `snap`, IP hold: never push, never deploy, never touch main. Commit after every unit.
(Session note 19 Oct 2026 23:40 UTC: `_snap_wt/.git` and `.git/worktrees/_snap_wt/gitdir` were rewritten as RELATIVE paths and the
worktree LOCKED, because the previous session had left absolute `/sessions/<id>/...` paths that no later session or David's Windows
git could resolve. `git worktree list` says "locked" -- correct; do not prune.)

## PLAN (U1) — decisions a continuing session must keep
- **Route U2:** `POST /listings/snap-draft` (multipart: `photos` 0..3, `sentence`, `category_hint` = the Quick door she is on,
  `city`, `country_iso2`, `lang`). Flag-dark: 404 unless `launch_switches.quick_snap` (new column, default 0; `_flags_payload`
  + `effective.quick_snap` + `_FlagsUpdate.quick_snap`). Photos -> the existing `vision_draft()` route function is AWAITED
  directly (no refactor); sentence -> `_qf_parse_plain` split + a small Snap mapper (role from roles/role_registry.json labels
  and aliases, area from the door's six tiles + the city's suburbs, days from weekday words, price + basis from `R350 a day`).
  Merge: sentence wins on price / area / days. Answer: `{cat, kind:'sell', fields:{...}, listing:{quick-publish body,
  source:'quick_snap'}, confidence, missing:[step keys], warnings}`. Declared in route_policy.json at the public app key
  level, same as vision-draft. Counters: table `quick_snap_log(day, kind snap|say|both, outcome draft|missing|error)`.
- **quick.html U3:** door gains two ghost buttons under Find/Sell: "Snap it" (camera / gallery; the share-sheet hand-over
  `takeShared` pattern) and "Say it" (browser SpeechRecognition when present; typed box ALWAYS). One combined screen:
  thumbnail + sentence box + "Make my advert". Result -> `ci`, `mode='sell'`, `picks` built from `fields` by `flow().steps`
  keys, `QUICK.itemName`, `window.QPHOTO` = her photo (the existing own-photo upload after publish, PHOTO-KIND-1 hold path),
  `step=flow().steps.length; drawDraft()`. `missing` -> `step=<first missing step index>; drawStep()` + one `.qf-note` line.
  Everything guarded by `/flags effective.quick_snap` (hidden when OFF) and LIVE. HARNESS.html = quick.html byte-identical.
- **Vision category hint:** vision_draft overwrites any category outside (property, services, adventures, cars) with the hint,
  so the DOOR she is on is the hint (Collectors door -> cards read as collectors). Mapping vision -> Quick key:
  property, cars, adventures, collectors, local_market->localmarket, services->homehelp/services by the role's class, tutors.
- **Never a guess published:** a field the reader cannot place is `missing` and she lands on that step; safe defaults only
  where the default is not a claim (collectors `auth`='Not yet', localmarket `ship`='Collect').
- **Proofs U6:** the candidate quick.html served by a local static server in headless Chromium with `/flags`, `/quick/me`,
  `/listings/snap-draft` and `/listings/quick-publish` mocked by a fetch shim (the Goal run 44 method, applied to the
  worktree copy); route proof = `snap_draft` helpers on a throwaway copy of `backups/marketsquare.db.bak-*`.
- Words: all new strings through roles/quick_i18n.json + the existing apply_*_i18n pattern (U4). No AI model named anywhere.

## LOG (one line per unit)
- U1 DONE 19 Oct 2026 23:45 UTC · read brief, CLAUDE.md, STANDING_ORDERS.md, FASTLANE §5, QF module (quick.html 5681-6337), bea_main quick_publish (5516) / vision_draft (27240) / find-parse (37755-37886) / flags (26173, 26276) · NEXT: U2
- U2 DONE 19 Oct 2026 23:48 UTC · POST /listings/snap-draft + GET /admin/quick-snap/stats + launch_switches.quick_snap (DDL, /flags, /admin/flags) + route_policy.json · verified: py_compile; scripts/snap_route_proof.py on a throwaway DB copy (backups/2026-10-12 zip) 21/21 PASS (cleaner sentence, card photo one-tap, sentence wins, honey, unread photo, unplaced sentence, 404 when OFF, counters) · NEXT: U3
- U3 DONE 19 Oct 2026 23:55 UTC · quick.html: door buttons Snap it / Say it (flag-dark), one Snap screen (door chips, photo camera/gallery/share-sheet mailbox p=snap, sentence box + browser speech recognition, GPS fix), POST snap-draft, picks poured into the normal flow (fillAhead), missing -> that step + one line, words lead the advert, q_snap_* beacons; bea_main: lat/lng -> nearest suburb, Quick manifest share_target while ON; HARNESS byte-identical · verified: node --check on every script block, py_compile, route proof 23/23 · NEXT: U4
- U4 DONE 20 Oct 2026 00:02 UTC · 21 Snap words in all 15 Quick languages (scripts/apply_snap_i18n.py -> roles/quick_i18n.json + the QI18N block in quick.html, same generator as sync_quick_roles.py), stories/quick_snap.json How story (en/af + zu/xh/nso drafts, 6 steps), server lines use the i18n keys (em dash) · verified: node --check all blocks, py_compile, HARNESS byte-identical, no AI model named · NEXT: U5
- U5 DONE 20 Oct 2026 00:04 UTC · dashboard.server.html: switch row 'Snap or say' (ls_m_snap -> launch_switches.quick_snap, armable in launch mode like the fast lane) + counters line read from GET /admin/quick-snap/stats (snaps · says · both -> drafts, asked a step, photos unread, published beacon; NOT MEASURED on a failed read; nothing typed by hand) · verified: node --check every script block, anchors asserted · NEXT: U6
- U6 DONE 20 Oct 2026 00:58 UTC · route proof re-run 23/23 PASS; rendered proof (scripts/snap_render_proof.py: worktree page served locally, APIs mocked from the route proof's answers) → visuals/snap_1..7_2026-10-20.png + two sheets: doors ON, Say → full cleaner draft → Publish(mocked) → "Your listing is live."; Snap photo → Collectors draft with her photo; unplaced → "What are you selling?" + line; switch OFF → no buttons; fillAhead fix kept; HARNESS identical; node parse 7/7; py_compile; ledger RG-1064..1067 OPEN (all pass in worktree); RULINGS RUL-242 + rulings_check (reflected); changelog.d fragment; stranger test NOT runnable here (/var/www) → ship gate · NEXT: U7
- U7 DONE 20 Oct 2026 00:59 UTC · report to David; nothing pushed, nothing deployed, no live listing · NEXT: none — DONE. Merge + ship + live one-tap proof + arming are the next session's, on David's word.
- U8 DONE 20 Oct 2026 03:58 UTC · David: 'Merge' (05:45 SAST). Branch snap merged into main (08d177e; conflicts: quick_i18n.json union of PLAN-FULL-NOTE-1 words + 21 Snap words, QI18N regenerated by sync_quick_roles.py, HARNESS byte-identical, QUICK_SNAP_BRIEF.md kept). Shipped through the gate: stranger test PASS, QA Bot gate clean, DEPLOY OK 03:58Z. Live probe: /flags quick_snap=false, doors absent, POST /listings/snap-draft 404 · NEXT: David says 'arm snap' -> flip from his browser -> live one-tap proof (QA advert, deleted) -> RG-1064..1067 LOCKED.
DONE
