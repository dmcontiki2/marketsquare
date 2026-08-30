#!/usr/bin/env python3
"""DRAFT_034_csp_connect_src.py -- INERT DRAFT (runner only executes NNN_*.py files).

RG-0180: tighten the served CSP connect-src from the blanket `'self' https:` to a
NAMED allowlist, closing the exfiltration half of the 3-4 Aug TP-Drive breach class
(script-src already blocks foreign CODE -- RG-0178 LOCKED; this blocks a running
script from TALKING to arbitrary HTTPS hosts).

WHY THIS IS A DRAFT AND NOT LIVE (30 Aug 2026, CTO decision, RUL-037): the
allowlist must be MEASURED from real traffic, never guessed. The app's pages touch
OSM tiles (incl. a/b/c subdomains), Wikimedia heritage images, and CDN assets --
one wrong entry bricks the maps for launch-day users. Static grep cannot settle
which of those are connect-src (fetch/XHR) vs img-src (element loads).

ACTIVATION PROCEDURE (2 Sep post-launch batch, attended):
 1. In Chrome (claude-in-chrome), walk: index, one adventures map, the heritage
    layer, a listing with photos, the dashboard. Read read_network_requests and
    collect every non-self host whose initiator is fetch/xhr/websocket/beacon.
 2. Fill ALLOWED below with exactly those origins (plus 'self').
 3. Rename this file to 034_csp_connect_src.py, commit, deploy. The migration
    edits the nginx CSP header exactly as 031 did (discovery via nginx -T per
    RG-0186 -- never a hand-written glob), reloads, then verifies the SERVED
    header on / and /terms carries the named list (033's lesson: measure the
    page, not the port-80 redirect).
 4. Ledger: RG-0180 prints READY TO LOCK on the first green run -- promote same
    session (DW-079 rule).
"""

ALLOWED = ["'self'"]  # + measured origins, activation step 2

raise SystemExit("DRAFT -- inert by name; follow the activation procedure in the docstring.")
