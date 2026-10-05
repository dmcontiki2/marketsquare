#!/usr/bin/env python3
"""065_email_examples_2.py -- EMAIL-EXAMPLES-2 (David, 5 Oct 2026).
Runs ONCE on the server via post_deploy. Creates the eight showcase adverts the collectors, tutors,
services-technical and services-casual letters' phone cards depict (each trio = one existing super + two new),
so every card in every outreach letter opens the advert it shows. Prints "SHOWCASE id=<id> | <title>".
Idempotent underneath (seller+title match); aborts untouched if a template or a photo is missing."""
import os, subprocess, sys
SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script = os.path.join(SRC, "scripts", "create_email_examples_2.py")
if not os.path.isfile(script):
    sys.exit("create_email_examples_2.py not found in the clone -- nothing run")
args = [sys.executable, script] + (["--apply"] if "--apply" in sys.argv else [])
sys.exit(subprocess.run(args).returncode)
