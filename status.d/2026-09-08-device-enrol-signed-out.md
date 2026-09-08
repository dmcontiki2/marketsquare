- **DEVICE-ENROL-2 (8 Sep):** the ops dashboard said SIGNED OUT to David's enrolled phone (and to the
  laptop on first PIN login) because the slow tokenless summary call landed AFTER the token and the
  reload guard was dead (`DATA` starts as `{}`, truthy). Fixed in dashboard.server.html — stale
  heartbeat dropped, token-bearing fetch always wins, banner removed on a real paint. RG-0341 LOCKED.
