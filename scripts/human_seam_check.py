#!/usr/bin/env python3
"""human_seam_check.py -- assert the human seam is designed, not assumed.

Companion to regression_ledger.py. The ledger answers "is a fix still fixed".
This answers a different question: "for every place an AI decides something on a
user's behalf, have we written down what a wrong answer costs, what the machine
falls back to, WHICH HUMAN ROLE takes over, and the measurable trigger that says
the seam must now be filled."

Why it exists: MarketSquare starts at zero humans by design. Klarna could rehire
the 700 people it fired; we have no bench. So the seam a human will one day stand
in has to be cut and asserted while it is still empty.

Exit 0 = every surface is declared and every RED surface is covered.
Exit 1 = a surface is undeclared, or a RED surface has no human role / no trigger.
Exit 2 = the register itself is missing or unreadable.

Run:  python3 scripts/human_seam_check.py
      python3 scripts/human_seam_check.py --strict   (AMBER gaps also fail)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REGISTER = os.path.join(REPO, "HUMAN_SEAM_REGISTER.json")

FAIL, WARN, INFO = "FAIL", "WARN", "INFO"

REQUIRED_FIELDS = ("id", "surface", "file", "decides", "class", "cost_of_wrong",
                   "machine_fallback", "human_role", "trigger", "seam_built")


def _load():
    if not os.path.exists(REGISTER):
        print("HUMAN SEAM CHECK: register missing at %s" % REGISTER)
        sys.exit(2)
    try:
        with open(REGISTER, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001 - a broken register must be loud
        print("HUMAN SEAM CHECK: register unreadable -- %s" % exc)
        sys.exit(2)


def check_shape(reg):
    """Every surface declares every field. A blank field is worse than no entry:
    it looks answered."""
    out = []
    seen = set()
    for s in reg.get("surfaces", []):
        sid = s.get("id", "<no id>")
        if sid in seen:
            out.append((FAIL, "%s appears twice -- ids must be unique" % sid))
        seen.add(sid)
        for field in REQUIRED_FIELDS:
            if field not in s:
                out.append((FAIL, "%s is missing '%s'" % (sid, field)))
            elif isinstance(s[field], str) and not s[field].strip():
                out.append((FAIL, "%s has an EMPTY '%s' -- a blank reads as answered" % (sid, field)))
        if s.get("class") not in ("RED", "AMBER", "GREEN"):
            out.append((FAIL, "%s has class %r -- must be RED, AMBER or GREEN" % (sid, s.get("class"))))
    if not seen:
        out.append((FAIL, "the register declares NO surfaces -- that cannot be true"))
    return out


def check_red_surfaces(reg):
    """A RED surface -- one where a wrong answer cannot be undone by a refund --
    must name a human role and a measurable trigger. 'None needed' is not an
    acceptable answer for RED."""
    out = []
    for s in reg.get("surfaces", []):
        if s.get("class") != "RED":
            continue
        sid = s.get("id")
        role = (s.get("human_role") or "").strip().lower()
        if not role or role in ("none", "none needed", "n/a", "tbd"):
            out.append((FAIL, "%s (%s) is RED with no named human role -- the seam is "
                              "undesigned" % (sid, s.get("surface"))))
        trig = (s.get("trigger") or "").strip().lower()
        if not trig or trig in ("none", "tbd", "unknown"):
            out.append((FAIL, "%s (%s) is RED with no measurable trigger -- nobody will ever "
                              "know when to fill the seam" % (sid, s.get("surface"))))
        if not (s.get("machine_fallback") or "").strip():
            out.append((FAIL, "%s is RED with no machine fallback declared" % sid))
    return out


def check_amber_surfaces(reg, strict):
    """AMBER gaps are reported, and fail only under --strict. They are the work
    queue, not the alarm."""
    out = []
    for s in reg.get("surfaces", []):
        if s.get("class") != "AMBER":
            continue
        if s.get("seam_built") is True:
            continue
        lvl = FAIL if strict else WARN
        out.append((lvl, "%s (%s) is AMBER with the seam NOT yet built -- %s"
                    % (s.get("id"), s.get("surface"), s.get("trigger"))))
    return out


def check_incentive_register(reg):
    """The Dragon Tail test. Every declared information leak must carry an action.
    A leak with no action is a leak nobody owns."""
    out = []
    leaks = reg.get("incentive_register", {}).get("leaks", [])
    if not leaks:
        out.append((FAIL, "the incentive register is empty -- the Dragon Tail test has not "
                          "been run on any surface"))
    for leak in leaks:
        for field in ("id", "surface", "actor", "if_they_optimise", "today", "action"):
            if not (leak.get(field) or "").strip():
                out.append((FAIL, "%s is missing '%s'" % (leak.get("id", "<no id>"), field)))
    return out


def check_rules_present(reg):
    """The six pre-design rules are canon. Losing one silently is the failure mode
    this whole file exists to prevent."""
    out = []
    ids = {r.get("id") for r in reg.get("predesign_rules", [])}
    for want in ("PR-1", "PR-2", "PR-3", "PR-4", "PR-5", "PR-6"):
        if want not in ids:
            out.append((FAIL, "pre-design rule %s has gone missing from the register" % want))
    return out


def main():
    strict = "--strict" in sys.argv
    reg = _load()

    groups = (
        ("register shape", check_shape(reg)),
        ("RED surfaces", check_red_surfaces(reg)),
        ("AMBER surfaces", check_amber_surfaces(reg, strict)),
        ("incentive register (Dragon Tail test)", check_incentive_register(reg)),
        ("pre-design rules", check_rules_present(reg)),
    )

    fails = warns = 0
    print("HUMAN SEAM CHECK -- MarketSquare")
    print("=" * 72)
    for title, results in groups:
        print("\n[%s]" % title)
        if not results:
            print("  INFO  all clear")
            continue
        for level, msg in results:
            print("  %-5s %s" % (level, msg))
            if level == FAIL:
                fails += 1
            elif level == WARN:
                warns += 1

    surfaces = reg.get("surfaces", [])
    counts = {c: sum(1 for s in surfaces if s.get("class") == c) for c in ("RED", "AMBER", "GREEN")}
    built = sum(1 for s in surfaces if s.get("seam_built") is True)
    print("\n" + "=" * 72)
    print("%d surfaces: %d RED, %d AMBER, %d GREEN. %d of %d seams built."
          % (len(surfaces), counts["RED"], counts["AMBER"], counts["GREEN"], built, len(surfaces)))
    print("%d FAIL, %d WARN" % (fails, warns))
    if fails:
        print("RESULT: the human seam is INCOMPLETE where it matters most.")
        return 1
    print("RESULT: every RED surface has a named role and a measurable trigger.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
