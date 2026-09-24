"""ENVKEY-BLIND-1 (24 Sep 2026) -- proof that RG-0426 asks BOTH doors a key can arrive through,
and that its teeth survive.

WHAT WENT WRONG
---------------
RG-0426 ("The app has a SECOND working AI lane") FAILed with:

    only 1 AI vendor key is live on the box (ANTHROPIC_API_KEY) -- the ranked failover has
    nowhere to fall to

and its scope told David: "Provisioning the key is David's -- it is a vendor credential, and
the money behind it is his call."

He already owned it. /var/www/marketsquare/.env carries OPENAI_API_KEY, and the maintenance
brain's own published probe (/dashboard/maint: brain_lane openai, brain_keyed true, status 200)
proves an OpenAI call from that box succeeds.

The entry read ONLY /proc/<pid>/environ, citing RG-0147's "check at the point of use". But the
point of use is ai_provider.envkey(), whose docstring says in as many words that it falls back
to the server .env BECAUSE the systemd unit does not export it (ENVKEY-1, 17 Jul 2026). A
.env-sourced lane can never appear in /proc/<pid>/environ. The check could only ever FAIL --
it was not measuring the box, it was measuring one of the two doors and calling the other one
empty. Four consecutive stand-ups found a row aimed at David that was already a fact; this was
the one still in the ledger.

THE TWO HALVES THIS TEST PINS
-----------------------------
1. A lane keyed through the ENVKEY-1 door (server .env, invisible to /proc) COUNTS.
2. A box that genuinely has one lane still FAILs.

Half 2 is the one that matters. A "fix" that silenced the false red by dropping the assertion
would pass half 1 and be worse than the bug: it would report a real single-vendor box as fine.
The test therefore drives the union logic with a one-lane box and requires the conviction.

Run:  python3 scripts/test_envkey_blind1.py      (exit 0 = pass)
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "regression_ledger.py")
AIP = os.path.join(os.path.dirname(HERE), "ai_provider.py")

src = open(LEDGER, encoding="utf-8").read()
i = src.index('@entry("RG-0426"')
j = src.index('@entry("RG-0427"')
block = src[i:j]

fails = []

# --- Half 1: the entry must consult the ENVKEY-1 door, not only /proc -------------------
if "configured_lanes" not in block:
    fails.append("RG-0426 never asks ai_provider.configured_lanes() -- it is still reading only "
                 "/proc/<pid>/environ, the one door an ENVKEY-1 key can never appear in")

if "/proc/$pid/environ" not in block:
    fails.append("RG-0426 dropped the /proc read entirely -- unit-exported keys would now go "
                 "unseen; the fix is BOTH doors, not the other one")

if not re.search(r"lanes\s*=\s*set\(\)|lanes\.update|lanes\.add", block):
    fails.append("RG-0426 does not union the two doors into one lane set")

# The scope must no longer tell David to go buy a key as the stated remedy.
if "Provisioning the key is David's" in block:
    fails.append("RG-0426's scope still hands David a purchase for a key the box already "
                 "resolves at the point of use")

# --- The ENVKEY-1 premise this rests on must still be true in ai_provider ---------------
aip = open(AIP, encoding="utf-8").read()
if "def configured_lanes" not in aip:
    fails.append("ai_provider.configured_lanes() is gone -- RG-0426's point-of-use door is "
                 "wired to a function that no longer exists")
if "/var/www/marketsquare/.env" not in aip:
    fails.append("ai_provider.envkey() no longer reads the server .env -- ENVKEY-1 has changed "
                 "and RG-0426's re-aim must be re-derived, not assumed")

# --- Half 2: the teeth. A genuinely single-lane box must still FAIL ---------------------
# Drive the union arithmetic exactly as the entry does, with only the unit door answering.
def verdict(unit_names, pou_lanes):
    VENDORS = ("ANTHROPIC", "OPENAI", "SCALEWAY", "FAILOVER", "XAI", "GEMINI", "GOOGLE", "DEEPSEEK")
    lanes = set()
    for n in unit_names:
        if n.split("_")[0] in VENDORS:
            lanes.add(n.split("_")[0].lower())
    lanes.update(x.lower() for x in pou_lanes)
    return lanes

# the real box on 24 Sep: anthropic via the unit, openai via the .env door
if len(verdict(["ANTHROPIC_API_KEY"], ["anthropic", "openai"])) < 2:
    fails.append("the real 24 Sep box (anthropic via unit + openai via .env) still counts as "
                 "one lane -- the false FAIL is not fixed")

# a genuinely single-vendor box must still convict
if len(verdict(["ANTHROPIC_API_KEY"], ["anthropic"])) >= 2:
    fails.append("a one-lane box counts as two -- the assertion lost its teeth")

if not re.search(r"if len\(lanes\) < 2:\s*\n\s*out\.append\(\(FAIL", block):
    fails.append("RG-0426 no longer FAILs on fewer than two lanes -- the teeth were removed "
                 "rather than re-aimed")

if fails:
    print("FAIL (%d):" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("ENVKEY-BLIND-1 OK: RG-0426 unions the unit door and the ENVKEY-1 point-of-use door, "
      "counts the real box as two lanes, and still convicts a one-lane box.")
