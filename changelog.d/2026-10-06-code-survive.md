## 2026-10-06 — CODE-SURVIVE-1 (RUL-210): sign-in codes no longer die on every deploy

- Pending sign-in codes lived in server memory; every deploy/restart wiped them, so a person typing the right code
  was told "wrong or expired". Probed on Maroushka's account: code sent 17:25 → restart 17:27 → refused 17:41;
  sent 17:58 → restart 18:00. Codes now persist in the private dir (0600) with their guess budget. RG-0907.
- RUL-210 recorded: after the first sign-up a browser stays signed in (180-day cookie, renewed on every visit,
  ends only on Sign out); a code is asked only to prove an email on a new phone/browser, and Google avoids even that.
