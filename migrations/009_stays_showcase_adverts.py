#!/usr/bin/env python3
"""009_stays_showcase_adverts.py — STAYS-SHOWCASE-1 (OPEN_LOOPS D8, 7 Aug 2026).
Runs ONCE on the server via the post_deploy hook. Creates the THREE Stays / B&B
email-showcase adverts (adventures_accommodation) — the fourth and final trio,
after property 315-317, cars 318-320 and adventures-experiences 321-323.

Prints "SHOWCASE id=<id> | <title>" lines into the deploy log — harvest those ids
and run CityLauncher/emailer/flip_showcase_hrefs.py to deep-link the Stays cards
in adventures_accommodation_outreach.html.

Idempotent underneath: the script skips adverts that already exist (seller+title
match) and aborts untouched if the clone template is missing or the wrong category.
"""
import os, subprocess, sys

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the repo clone
script = os.path.join(SRC, "scripts", "create_stays_showcase_adverts.py")
if not os.path.isfile(script):
    sys.exit("create_stays_showcase_adverts.py not found in the clone — nothing run")
args = [sys.executable, script] + (["--apply"] if "--apply" in sys.argv else [])
sys.exit(subprocess.run(args).returncode)
