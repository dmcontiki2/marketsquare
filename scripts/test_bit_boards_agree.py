#!/usr/bin/env python3
"""BIT-BOARD-DRIFT-1 -- the two BIT boards may diverge only where a REASON is written down.

OPEN_LOOPS L13 (opened 19 Sep 2026, re-probed on four consecutive stand-ups and never
started): the build-integrity board exists as TWO files six weeks apart --

  bit/bit_runner.py       what the stand-up runs, through the Cloudflare edge
  ops/bit/bit_runner.py   what ops/autodeploy/deploy_manifest.txt ships to
                          /var/www/marketsquare/bit/ and what trustsquare-bit.timer
                          runs every 15 minutes on the box, against localhost:8000

Different inodes, no link, and -- until this file -- NOTHING ASSERTED THEY AGREE. That is
the whole of L13: a real fix to either board silently fails to reach the other, which is
exactly what happened to BIT-EDGE-BLIND-1 (fixed in bit/ on 23 Sep, still absent from ops/
on 27 Sep).

WHY THIS IS AN ASSERTION AND NOT A MERGE. RG-0460 carries the warning in its own scope
text: the ops copy is a DELIBERATE localhost variant (it probes localhost:8000 and carries
BIT_AA_BASE, and it reads the HTML shell from disk rather than over HTTP). Blind-copying
the edge copy over it would destroy that wiring and was explicitly ruled out. So the fix L13
needs is not one file -- it is a single writer for what must agree plus a NAMED reason for
each thing that may differ. This file is that writer.

MEASURED 2026-09-27 19:2xZ, which is what the baseline below records:

  bit/bit_registry.json and ops/bit/bit_registry.json  byte-identical (md5 a49a3b6cb7f2)
  CHECKS registry key sets                             identical (6 keys)
  6 of 9 shared functions                              byte-identical
  3 of 9 shared functions                              differ, each for a named vantage reason

TEETH IN BOTH DIRECTIONS -- this is the part that makes it worth shipping:

  (1) A function in SHARED_IDENTICAL that stops being identical FAILS. That is a fix landing
      in one board and not the other -- L13's loop, caught at the moment it happens instead
      of on the fifth stand-up.
  (2) A function in VANTAGE_DIVERGENT that BECOMES identical also FAILS. That is a blind copy
      having destroyed the server board's localhost wiring -- RG-0460's trap, which a
      one-directional test would wave through.
  (3) A new shared function appearing in one board and not the other FAILS.
  (4) The two registries drifting apart FAILS: the check SET is data and has exactly one truth.

NOT WEAKENED, AND NOT A BASELINE THAT FORGIVES: the three divergences are not "accepted
because they are there". Each carries the reason it may differ, and if that reason ever stops
being true the entry has to be deleted, which makes the test red until someone does the work.

Exit 0 = the two boards agree everywhere they must and differ only where written down.
Exit 1 = drift. The named divergence is printed verbatim, both ways.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDGE = os.path.join(ROOT, "bit", "bit_runner.py")
OPS = os.path.join(ROOT, "ops", "bit", "bit_runner.py")
EDGE_REG = os.path.join(ROOT, "bit", "bit_registry.json")
OPS_REG = os.path.join(ROOT, "ops", "bit", "bit_registry.json")

# Shared logic that carries no vantage of its own. These MUST stay byte-identical: a fix to
# one is a fix both boards need.
SHARED_IDENTICAL = [
    "c_http_json",
    "c_http_json_count",
    "c_http_status",
    "c_no_demo_bleed",
    "c_ai_example_contract",
    "run_one",
]

# Permitted to differ, each with the reason. Delete an entry the day its reason stops being
# true -- that is what makes this a gate and not a rubber stamp.
VANTAGE_DIVERGENT = {
    "_get": (
        "edge copy carries a named User-Agent and the BIT-EDGE-BLIND-1 / _is_edge_refusal "
        "detector because it goes through Cloudflare; the ops copy talks to localhost:8000 "
        "on the box, where no edge can refuse it"
    ),
    "_feature_ids": (
        "ops copy resolves the advertised feature list from BIT_AA_BASE (the AdvertAgent "
        "service on the box's own loopback port); the edge copy resolves it over the public "
        "origin"
    ),
    "c_http_shell": (
        "ops copy reads the HTML shell from disk on the box (via='disk') because it is the "
        "authority on what was actually deployed; the edge copy must fetch it over HTTP "
        "because it has no filesystem there"
    ),
}

FN_RE = r"^def (%s)\(.*?(?=^def |^CHECKS|^\Z)"


def _funcs(path):
    src = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"^def (\w+)\(.*?(?=^def |^CHECKS|^\Z)", src, re.S | re.M):
        out[m.group(1)] = m.group(0)
    return out, src


def _checks_keys(src):
    m = re.search(r"^CHECKS\s*=\s*\{(.*?)\}", src, re.S | re.M)
    if not m:
        return None
    return sorted(set(re.findall(r'"([a-z_]+)"\s*:', m.group(1))))


def main():
    fails = []
    notes = []

    for p in (EDGE, OPS, EDGE_REG, OPS_REG):
        if not os.path.exists(p):
            print("CANNOT MEASURE: missing %s" % p)
            return 2

    # (4) the check SET is data and has exactly one truth
    ra = open(EDGE_REG, "rb").read()
    rb = open(OPS_REG, "rb").read()
    if ra != rb:
        try:
            ia = sorted(b.get("id", "?") for b in json.loads(ra).get("bits", []))
            ib = sorted(b.get("id", "?") for b in json.loads(rb).get("bits", []))
            only_e = sorted(set(ia) - set(ib))
            only_o = sorted(set(ib) - set(ia))
        except Exception:
            only_e = only_o = ["<unparseable>"]
        fails.append(
            "REGISTRY DRIFT: bit/bit_registry.json (%d B, md5 %s) and ops/bit/bit_registry.json "
            "(%d B, md5 %s) are no longer identical. Only in bit/: %s. Only in ops/: %s. The "
            "check SET is data, not vantage -- the two boards must grade the same checks."
            % (len(ra), hashlib.md5(ra).hexdigest()[:12], len(rb),
               hashlib.md5(rb).hexdigest()[:12], only_e, only_o)
        )
    else:
        notes.append("registries byte-identical (%d B, md5 %s)"
                     % (len(ra), hashlib.md5(ra).hexdigest()[:12]))

    fe, se = _funcs(EDGE)
    fo, so = _funcs(OPS)

    ke, ko = _checks_keys(se), _checks_keys(so)
    if ke is None or ko is None:
        fails.append("CANNOT READ the CHECKS registry out of one of the boards "
                     "(edge=%r ops=%r) -- the shape this test relies on has changed."
                     % (ke, ko))
    elif ke != ko:
        fails.append("CHECKS REGISTRY DRIFT: edge keys %s vs ops keys %s. A check type "
                     "present on one board and not the other means one board silently "
                     "skips checks the other grades." % (ke, ko))
    else:
        notes.append("CHECKS registry key sets identical (%d: %s)" % (len(ke), ", ".join(ke)))

    # (1) and (3)
    for name in SHARED_IDENTICAL:
        if name not in fe or name not in fo:
            fails.append(
                "SHARED FUNCTION MISSING: %s() is %s in bit/bit_runner.py and %s in "
                "ops/bit/bit_runner.py. Shared logic has to exist on both boards."
                % (name, "present" if name in fe else "ABSENT",
                   "present" if name in fo else "ABSENT")
            )
            continue
        he = hashlib.md5(fe[name].encode()).hexdigest()
        ho = hashlib.md5(fo[name].encode()).hexdigest()
        if he != ho:
            fails.append(
                "DRIFT IN SHARED LOGIC: %s() differs between the two boards (edge md5 %s, "
                "ops md5 %s). This function carries no vantage of its own, so a fix to one "
                "copy is a fix the other board needs -- carry it across, or, if the "
                "divergence is deliberate, move %s into VANTAGE_DIVERGENT with the reason. "
                "This is OPEN_LOOPS L13's exact failure mode: BIT-EDGE-BLIND-1 was fixed in "
                "bit/ on 23 Sep and never reached ops/." % (name, he[:12], ho[:12], name)
            )
        else:
            notes.append("%s() identical (md5 %s)" % (name, he[:12]))

    # (2) the reverse direction -- a blind copy is as bad as a missed fix
    for name, reason in sorted(VANTAGE_DIVERGENT.items()):
        if name not in fe or name not in fo:
            fails.append("VANTAGE FUNCTION MISSING: %s() is not on both boards (edge=%s "
                         "ops=%s)." % (name, name in fe, name in fo))
            continue
        he = hashlib.md5(fe[name].encode()).hexdigest()
        ho = hashlib.md5(fo[name].encode()).hexdigest()
        if he == ho:
            fails.append(
                "VANTAGE COLLAPSE: %s() is now IDENTICAL on both boards (md5 %s), but it is "
                "declared divergent for a reason: %s. Identical almost certainly means the "
                "edge copy was blind-copied over the server copy, which destroys the "
                "server board's localhost wiring -- RG-0460 warns about this by name. Either "
                "restore the vantage or, if the reason has genuinely stopped being true, "
                "delete %s from VANTAGE_DIVERGENT and move it to SHARED_IDENTICAL."
                % (name, he[:12], reason, name)
            )
        else:
            notes.append("%s() differs as declared (edge %s / ops %s) -- %s"
                         % (name, he[:8], ho[:8], reason))

    # (3) a new shared function on one board only
    ignore = {"main", "emit_findings_file", "_disk_for", "_is_edge_refusal"}
    for name in sorted((set(fe) ^ set(fo)) - ignore):
        if name in SHARED_IDENTICAL or name in VANTAGE_DIVERGENT:
            continue
        fails.append(
            "UNDECLARED ONE-SIDED FUNCTION: %s() exists on %s board only. Every function "
            "shared by the two boards is either identical (SHARED_IDENTICAL) or divergent "
            "with a written reason (VANTAGE_DIVERGENT); a function on one board alone is "
            "neither, and is how the two boards drift apart unnoticed."
            % (name, "edge" if name in fe else "ops")
        )

    if fails:
        print("BIT-BOARD-DRIFT-1: FAIL -- the two BIT boards have drifted.\n")
        for f in fails:
            print("  * %s\n" % f)
        print("bit/bit_runner.py      %d B" % os.path.getsize(EDGE))
        print("ops/bit/bit_runner.py  %d B" % os.path.getsize(OPS))
        return 1

    print("BIT-BOARD-DRIFT-1: PASS -- the two BIT boards agree everywhere they must and "
          "differ only where the reason is written down.")
    for n in notes:
        print("  - %s" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
