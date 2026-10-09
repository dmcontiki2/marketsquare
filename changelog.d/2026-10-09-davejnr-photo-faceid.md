### Dave jnr's test: car photos and the repeated Face ID offer (fixback, 9 Oct 2026)

Dave jnr's property listing #534 lost 2 of 14 photos with "not anonymous ... plate" although the car in shot showed no
plate, and the app asked him to set up Face ID although his iPhone passkey had been on file since 4 Oct.

- **PHANTOM-PLATE-1** (bea_main.py `_anon_plate_takeover`) — the AI scanner boxes a plate on every car it sees; outside the
  vehicle categories the local plate detector could only confirm that, never overrule it. Now a plate/car region where the
  detector finds no plate and the zoomed OCR reads no text is dismissed; if that was all, the photo is accepted unchanged
  with no second AI read (it would repeat the same false plate) and is not reported to the seller as "redacted". The same
  check applies to a verify read. Real plates are still found and blurred; a car region naming a logo/brand/company still
  goes the old way. Detector unavailable → no dismissal (fail-closed as before).
- **PASSKEY-KNOWN-1** (ms.js `hubOffer`) — the Face ID offer read only the phone's own `ts_pk_here` flag, so signing in by
  e-mailed code on a browser without it brought the offer back. `/auth/passkey/status` already returns `count`; when the
  account has a passkey the offer is skipped and the flag is set. Refines PASSKEY-ALWAYS-1 (7 Oct).

**Shipped 9 Oct 2026 00:19 UTC** (main.py + static/ms.js; server rollback copies `*.ship-20261009-0019`). Live checks: BEA
active, /health 200, plate detector ready, site 200 in 0.3 s, smoke_test.py all pass, ms.js served with PASSKEY-KNOWN-1.
Live gate run (category property) on listing-246 eval photos: both no-plate side profiles ACCEPTED; the frontal photo with
a plate ACCEPTED with the plate blurred.
