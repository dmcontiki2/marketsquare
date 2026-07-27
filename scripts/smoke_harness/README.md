# Detail-render smoke harness (added 27 Jul 2026)

WHY: the __rows incident. Static checks (grep for code presence, node --check) all passed
while openDetail() THREW at runtime - a one-character corruption made every super-listing
click die silently. Presence is not execution. This harness EXECUTES the app: it loads
index.html + ms.js in headless Chromium against replayed live API data, calls openDetail()
on every super listing, and asserts the detail actually renders with the right map and
extensions. Claude runs it in the cloud container before shipping ms.js changes.

FILES: server.py (serves index.html, ms.js and captured API JSON same-origin),
verify.mjs (the executable assertions). Refresh the *.json captures with curl before a run.
Setup in the container: npm install playwright; launch with executablePath /opt/pw-browsers/chromium.
