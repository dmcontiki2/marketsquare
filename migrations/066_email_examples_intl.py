#!/usr/bin/env python3
"""066_email_examples_intl.py -- EMAIL-EXAMPLES-INTL-1 (David, 5 Oct 2026).
Runs ONCE on the server via post_deploy: 39 showcase adverts in New York, London and Sydney (two per category, three
for casual work) so US / UK / Australian outreach letters show three example cards in the reader's own country, and
corrects the car details of showcase adverts 287 / 292 / 297. Idempotent underneath; aborts untouched if a template
or a photo is missing."""
import os, subprocess, sys
SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script = os.path.join(SRC, "scripts", "create_email_examples_intl.py")
if not os.path.isfile(script):
    sys.exit("create_email_examples_intl.py not found in the clone -- nothing run")
sys.exit(subprocess.run([sys.executable, script] + (["--apply"] if "--apply" in sys.argv else [])).returncode)
