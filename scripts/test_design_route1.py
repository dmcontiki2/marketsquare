#!/usr/bin/env python3
"""DESIGN-ROUTE-1 (26 Sep 2026) -- red on the pre-fix source, green on the fix.

WHAT WAS BROKEN. scripts/maintenance_agent.py classified a fault PATH_B and then wrote
the sentence "routed to design backlog (batched, designer gate)" into its report. Nothing
wrote a dossier; nothing in scripts/ referenced DESIGN_BACKLOG.md at all.

MEASURED, 26 Sep 2026, and printed verbatim by this test on the pre-fix source:
  TS-0027 and TS-0006 were both closed on 11 Aug 2026 with "routed to the design backlog"
  in their fix_note. DESIGN_BACKLOG.md holds exactly one dossier -- DCB-001 -- and it is
  neither of them. Two faults said routed; zero arrived.

WHY IT MATTERED BEYOND THE MISSING FILE. RUL-013 sent design work to the 'design' task
tier from 1 Sep 2026. OPEN_LOOPS L8 re-probed `grep task="design"` -> 0 callers on four
consecutive stand-ups (19, 23, 24, 25 Sep) and called the tier unwired. It was wired at
the chokepoint all along. It had no caller because no design work ever reached a backlog,
because the routing was a string. The zero was the symptom, not the fault.

WHAT THE FIX MAY NOT DO, asserted here so a later edit cannot quietly widen it: the
dossier's GATE line must be EMPTY. DESIGN_CHANGE_GUIDELINES.md criterion 10 says an absent
gate means NOT APPROVED, DO NOT BUILD, and binding the designer role is open item 2 --
David's. A filer that scored or approved its own dossier would be the real damage.

Run:  python3 scripts/test_design_route1.py
"""
import io
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FAILS = []


def check(name, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + name + (("  -- " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def main():
    src = io.open(os.path.join(HERE, "maintenance_agent.py"), encoding="utf-8").read()
    print("DESIGN-ROUTE-1")
    print("source shape:")
    check("the agent knows where the backlog is", "DESIGN_BACKLOG" in src)
    check("a dossier filer exists", "def file_design_dossier(" in src)
    check("the design tier is CALLED (RUL-013's lane)", 'task="design"' in src)
    check("the old proxy sentence is gone",
          'else "routed to design backlog (batched, designer gate)"' not in src)

    if FAILS:
        print("\nPRE-FIX SOURCE -- the damage, measured:")
        try:
            bl = io.open(os.path.join(REPO, "DESIGN_BACKLOG.md"), encoding="utf-8").read()
            ids = re.findall(r"DCB-\d{3}", bl)
            print("    DESIGN_BACKLOG.md holds %d dossier(s): %s"
                  % (len(set(ids)), ", ".join(sorted(set(ids))) or "none"))
        except Exception as e:
            print("    DESIGN_BACKLOG.md unreadable: %s" % e)
        print("    scripts/ references to DESIGN_BACKLOG.md that WRITE it: 0")
        print("    TS-0027 and TS-0006 fix_notes say 'routed to the design backlog' (11 Aug 2026).")
        print("    Neither is in the file. The routing is a sentence, not a mechanism --")
        print("    and that is why OPEN_LOOPS L8 read 0 design-tier callers for 26 days.")
        print("\nRED: %d check(s) failed -- %s" % (len(FAILS), ", ".join(FAILS)))
        return 1

    # ── behaviour, against a throwaway backlog file ─────────────────────────────
    sys.path.insert(0, HERE)
    os.environ.setdefault("MAINT_PHASE", "postlaunch")
    import maintenance_agent as ma

    tmp = tempfile.mkdtemp(prefix="designroute_")
    ma.DESIGN_BACKLOG = os.path.join(tmp, "DESIGN_BACKLOG.md")
    io.open(ma.DESIGN_BACKLOG, "w", encoding="utf-8").write(
        "# DESIGN BACKLOG\n\n---\n\n## DCB-001 -- existing\n\n    DOSSIER: existing\n")

    # The brain is local-only from most vantages; force the unreachable path first, because
    # a filer that only works with a live brain is a filer that fails on the bad day.
    ma.brain = lambda *a, **k: ma._BrainReply({"ok": False, "error_kind": "vantage:local-only"})

    fault = {"id": 99, "ref": "TS-0099", "title": "The city filter hides adverts with no warning",
             "detail": "I set a city and half the adverts vanished with nothing saying why.",
             "page_url": "/q/services"}

    print("behaviour:")
    dcb, note = ma.file_design_dossier(fault, "brain[test]=DESIGN")
    check("a dossier is filed even when the design tier is unreachable", dcb == "DCB-002",
          "got %r (%s)" % (dcb, note))

    body = io.open(ma.DESIGN_BACKLOG, encoding="utf-8").read()
    check("the fault reference is IN the file", "TS-0099" in body)
    check("the unreachable tier is NAMED, not papered over",
          "NONE --" in body and "not reached" in body)
    check("the GATE line is EMPTY (absent gate = do not build)",
          re.search(r"GATE:\s*--\s*EMPTY", body) is not None)
    check("the filer does NOT score its own dossier", "not scored" in body)
    check("unmet criteria are declared, not claimed",
          "criterion 3 is unmet" in body and "criterion 5 is unmet" in body)

    # Idempotent: the loop runs three times a day and must not re-file the same fault.
    dcb2, note2 = ma.file_design_dossier(fault, "brain[test]=DESIGN")
    check("a second run does not duplicate the dossier", dcb2 is None and "already filed" in note2,
          "got %r / %r" % (dcb2, note2))

    # With a live tier, the direction is carried and its source is stamped.
    ma.brain = lambda *a, **k: ma._BrainReply(
        {"ok": True, "text": "Say which filter is active above the grid and offer one tap to clear it.",
         "provider": "openai", "model": "gpt-5.6-sol"})
    fault2 = dict(fault, ref="TS-0100", title="Second report, same filter confusion")
    dcb3, _ = ma.file_design_dossier(fault2, "brain[test]=DESIGN")
    body = io.open(ma.DESIGN_BACKLOG, encoding="utf-8").read()
    check("a live design tier's direction is carried", dcb3 == "DCB-003" and "one tap to clear it" in body)
    check("the direction's source is stamped with the tier", "task=design, RUL-013" in body)
    check("gpt-5.6-sol is recorded as the source", "openai/gpt-5.6-sol" in body)

    print("")
    if FAILS:
        print("RED: %d check(s) failed -- %s" % (len(FAILS), ", ".join(FAILS)))
        return 1
    print("GREEN: PATH_B files a real dossier, the design tier is its first caller "
          "(RUL-013), and the gate stays empty and David's.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
