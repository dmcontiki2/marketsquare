## 2026-09-24 — LINK-KEY-1 / PHONE-KEY-1 (RUL-167): the casual worker's key is a phone number or her private link

David, 24 Sep 2026, approving D2 of the casual-workers plan: *"allow a phone number (one-time code) or the draft
link itself as the account key for casual workers, EULA sign-off still mandatory in the app"*. RUL-166's gate is
untouched — nothing goes live without a signed EULA, recorded server-side — only the KEY widened.

- **Key accounts:** an ordinary `users` row with a synthetic, never-mailed identity `w-…@key.trustsquare.co`,
  plus `users.phone` and/or `users.key_hash` (new columns, migrated on boot). Every mail sender skips a key
  identity; when a phone is on file and an SMS provider is configured, the live letter, a new introduction
  request and a relayed message become an SMS nudge instead ("open your TrustSquare link").
- **The Quick door** offers three keys: **E-mail** (as before), **Phone** (six-digit code by SMS — shown only
  while `/quick/me` reports `sms_ready`), **WhatsApp link** (default for the services door). The link key returns
  a one-time `key_url`; the arrival screen shows it and the WhatsApp self-send carries it ("this is my KEY, keep
  it"). `GET /k/<secret>` is her permanent key (no-lapse rule): each visit mints a 20-minute sign-in hop and lands
  her in the app on her draft, where the hub's scroll-to-end Terms and `publish_listing`'s 403 gate stand as
  before. A phone-code session gets the same hop from `/auth/session-link`.
- **Phone codes:** `/auth/phone/start` (3 codes per number per hour, 10 per connection, 503 `sms_unavailable`
  until `SMS_PROVIDER`/`SMS_TOKEN` are set in /etc/marketsquare/secrets.env — the door then falls back to the
  link, never a dead end) and `/auth/phone/verify` (10 minutes, 5 tries, hashed at rest).
- **sms_provider.py:** one door for every SMS — BulkSMS, Clickatell or SMSPortal, E.164 normalisation for ZA,
  per-number throttle, numbers never logged in full. Fails dark.
- Guard: RG-0450. HARNESS.html copied from quick.html (house rule). Still open on the human side: David's SMS
  account (the key lands in .secrets, then the server env) and the WhatsApp Business number for the posters.
- **Rendered walk, 24 Sep 07:4x UTC, 390 px:** /q/homehelp → Gardener → Centurion → Every day → R350 → *WhatsApp link* → Save → key link shown and
  carried in the WhatsApp self-send → key link opened in a fresh browser → Seller Hub signed in as `w-…@key` with the draft in front →
  Publish my advert → the scroll-to-end Terms + two consents → Go live → advert #401 live, no e-mail in the public read, `eula_accepted_at`
  stamped on the key account by publish_listing; withdrawn again through the app's own route. The "You're live" screen now says where
  requests land for a key account (Seller Hub / SMS) instead of "your email" (marketsquare.html ids + ms.js sobDone wording).
