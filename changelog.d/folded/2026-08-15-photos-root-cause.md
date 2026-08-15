## 2026-08-15 — TS-0034 photo swaps: the actual root cause, fourth and final layer
David kept seeing duplicates after every fix and every deploy — he was right each time. Full
chain, each layer masking the next: (1) immutable 1-year cache hid same-filename swaps;
(2) a sister session clobbered one replaced file; (3) my deploy-verification read a stale
mount view and raced the 2-min server pull timer, reporting his SUCCESSFUL deploys as absent;
(4) THE ROOT: the FEA viewer reads photos from the [photos:...] prefix in description, not
photo_urls — my repoints updated the wrong store. Descriptions for 267/268 now carry the
v2/v3 names; CDN purged. Runbook swap rule extended: update all three photo stores and verify
at the USER-VISIBLE layer. Deploy pipeline itself: zero failures today — every TSL run David
made deployed clean (server journal is the ground truth for verification, not mount git).
