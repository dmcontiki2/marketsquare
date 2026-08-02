#!/usr/bin/env python3
"""001_email_showcase_adverts.py — EMAIL-SHOWCASE-1 (OPEN_LOOPS D5a, David-approved 2 Aug 2026).
Runs ONCE on the server via the post_deploy hook. Creates the SIX remaining wave-1
email-showcase adverts (3 Cars + 3 Adventures; the property trio is already live as
315-317). Prints "SHOWCASE id=<id> | <title>" lines into the deploy log — harvest those
ids and run CityLauncher/emailer/flip_showcase_hrefs.py to deep-link the templates.
Idempotent underneath: the script skips adverts that already exist (seller+title match).
"""
import os, subprocess, sys

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the repo clone
script = os.path.join(SRC, "scripts", "create_email_showcase_adverts.py")
if not os.path.isfile(script):
    sys.exit("create_email_showcase_adverts.py not found in the clone — nothing run")
args = [sys.executable, script] + (["--apply"] if "--apply" in sys.argv else [])
sys.exit(subprocess.run(args).returncode)
