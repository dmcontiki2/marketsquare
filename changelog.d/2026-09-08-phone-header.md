## 8 Sep 2026 — PHONE-HEADER-1: the ops dashboard's top bar is one compact row on a phone

David, from the phone: *"for the phone to view the pages sideways, the top bar takes up too much of the
viewing area."* The header wrapped into four rows (session badge, timestamp and every tab broke over two
lines) and took a third of a landscape screen.

`dashboard.server.html`: below 1024px the header is one compact row that swipes sideways (smaller logo,
nowrap badge/timestamp/tabs, tighter padding); on a screen shorter than 560px (a phone held sideways) it
also stops being sticky, so it scrolls away and the page gets the full height. Desktop is untouched.
