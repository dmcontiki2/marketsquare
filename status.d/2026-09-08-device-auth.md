- **DEVICE-AUTH-1 (8 Sep, David: "we only need the first login"):** an enrolled phone now passes the
  nginx Basic-auth gate on every ops page (migration 037: `auth_request /_device_ok` beside the
  existing `satisfy any` Basic auth; upstream errors map to 401 so an outage falls back to Basic, never
  500). Basic credentials unchanged. PHONE-HEADER-1 the same day: the dashboard header is one compact
  row on a phone and scrolls away in landscape.
