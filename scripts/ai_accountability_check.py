#!/usr/bin/env python3
"""ai_accountability_check.py -- assert AI is policed by AI, and humans own interfaces.

Companion to regression_ledger.py. The ledger asks "is a fix still fixed".
This asks "is every AI decision still accountable to something, and is that
something the RIGHT something".

MarketSquare is AI-first BY DESIGN. AI was chosen for the high-throughput
judgement surfaces because that is where machine speed and consistency beat
human judgement. A human placed on a throughput path does not make it safer --
it throttles the business, and it decays, because a reviewer at volume
rubber-stamps within days. That is a control which only LOOKS like a control.

So the assertions here are deliberately the inverse of the naive ones:

  * every RED surface must be caught by a MACHINE -- a deterministic guard, a
    second vendor lane, or an economic absorber -- not by a person;
  * NO high-throughput surface may put a human on a per-item path (PR-6). A
    design that does is a defect and fails this check;
  * every surface that can raise an exception must route it to one of the four
    named human INTERFACE roles (R1 legal, R2 infrastructure, R3 partner,
    R4 accountable principal);
  * triggers must be exception-RATE based, never volume based (PR-7).

Exit 0 = accountable.  Exit 1 = a gap.  Exit 2 = register missing/unreadable.

Run:  python3 scripts/ai_accountability_check.py
      python3 scripts/ai_accountability_check.py --strict   (AMBER gaps fail too)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REGISTER = os.path.join(REPO, "AI_ACCOUNTABILITY_REGISTER.json")

FAIL, WARN, INFO = "FAIL", "WARN", "INFO"

REQUIRED = ("id", "surface", "file", "decides", "class", "throughput", "cost_of_wrong",
            "ai_check", "deterministic_guard", "exception_route", "human_touches",
            "exception_owner", "trigger", "built")

VALID_ROLE_IDS = ("R1", "R2", "R3", "R4", "-")

# Words that betray a volume-based trigger. PR-7: volume must never pull a human in.
VOLUME_WORDS = re.compile(r"\b(per week|per day|/week|/day|a week|a day|uploads|verifications|inbound)\b",
                          re.I)
RATE_WORDS = re.compile(r"(rate|%|disagree|overturn|dispute|refund|any |first |never|hard rule|"
                        r"standing condition|build now|do not switch)", re.I)


def _load():
    if not os.path.exists(REGISTER):
        print("AI ACCOUNTABILITY CHECK: register missing at %s" % REGISTER)
        sys.exit(2)
    try:
        with open(REGISTER, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001 -- a broken register must be loud
        print("AI ACCOUNTABILITY CHECK: register unreadable -- %s" % exc)
        sys.exit(2)


def check_shape(reg):
    out, seen = [], set()
    for s in reg.get("surfaces", []):
        sid = s.get("id", "<no id>")
        if sid in seen:
            out.append((FAIL, "%s appears twice -- ids must be unique" % sid))
        seen.add(sid)
        for field in REQUIRED:
            if field not in s:
                out.append((FAIL, "%s is missing '%s'" % (sid, field)))
            elif isinstance(s[field], str) and not s[field].strip():
                out.append((FAIL, "%s has an EMPTY '%s' -- a blank reads as answered" % (sid, field)))
        if s.get("class") not in ("RED", "AMBER", "GREEN"):
            out.append((FAIL, "%s has class %r" % (sid, s.get("class"))))
        if s.get("throughput") not in ("high", "medium", "low"):
            out.append((FAIL, "%s has throughput %r -- must be high, medium or low" % (sid, s.get("throughput"))))
        if s.get("human_touches") not in ("exceptions_only", "every_item", "none"):
            out.append((FAIL, "%s has human_touches %r" % (sid, s.get("human_touches"))))
        if s.get("exception_owner") not in VALID_ROLE_IDS:
            out.append((FAIL, "%s routes exceptions to %r, which is not a named interface role"
                        % (sid, s.get("exception_owner"))))
    if not seen:
        out.append((FAIL, "the register declares NO surfaces -- that cannot be true"))
    return out


def check_no_human_in_throughput(reg):
    """PR-6. The headline assertion. A human on a per-item path in a high-throughput
    surface is a DEFECT: it throttles the business and decays into rubber-stamping."""
    out = []
    for s in reg.get("surfaces", []):
        if s.get("human_touches") == "every_item":
            lvl = FAIL if s.get("throughput") in ("high", "medium") else WARN
            out.append((lvl, "%s (%s) puts a human on EVERY ITEM at %s throughput -- PR-6: that "
                             "throttles the business and decays into rubber-stamping. The check "
                             "must be a machine." % (s.get("id"), s.get("surface"), s.get("throughput"))))
    return out


def check_red_caught_by_machine(reg):
    """Every RED surface must be caught by something that runs at machine speed:
    a deterministic guard, a second vendor lane, or an economic absorber."""
    out = []
    for s in reg.get("surfaces", []):
        if s.get("class") != "RED":
            continue
        sid = s.get("id")
        ai = (s.get("ai_check") or "").strip()
        det = (s.get("deterministic_guard") or "").strip()
        if not ai and not det:
            out.append((FAIL, "%s (%s) is RED with NO machine-speed check -- neither an AI check "
                              "nor a deterministic guard" % (sid, s.get("surface"))))
            continue
        if det.upper().startswith("NOT YET BUILT") and not ai:
            out.append((FAIL, "%s is RED, its guard is not built, and there is no AI check to "
                              "carry it" % sid))
        if not (s.get("exception_route") or "").strip():
            out.append((FAIL, "%s is RED with no exception route -- a wrong answer has nowhere "
                              "to go" % sid))
    return out


def check_exception_ownership(reg):
    """Every surface that can raise an exception names a human INTERFACE role to own it.
    Owning the exception is not the same as doing the work."""
    out = []
    roles = {r.get("id") for r in reg.get("human_roles", [])}
    for want in ("R1", "R2", "R3", "R4"):
        if want not in roles:
            out.append((FAIL, "interface role %s has gone missing from the register" % want))
    for s in reg.get("surfaces", []):
        if s.get("human_touches") == "none":
            continue
        if s.get("exception_owner") in (None, "", "-"):
            out.append((FAIL, "%s (%s) can raise an exception but names no owning interface role"
                        % (s.get("id"), s.get("surface"))))
    for r in reg.get("human_roles", []):
        if r.get("touches") == "every_item":
            out.append((FAIL, "interface role %s (%s) is defined as touching every item -- "
                              "interface roles own exceptions, never throughput"
                        % (r.get("id"), r.get("role"))))
        if not (r.get("hire_trigger") or "").strip():
            out.append((FAIL, "interface role %s has no hire trigger -- nobody will know when it "
                              "is needed" % r.get("id")))
    return out


def check_triggers_are_rate_based(reg):
    """PR-7. A trigger phrased in raw volume pulls a human in exactly when the design is
    succeeding. Rising volume must never be the reason a person gets involved."""
    out = []
    for s in reg.get("surfaces", []):
        trig = (s.get("trigger") or "")
        if VOLUME_WORDS.search(trig) and not RATE_WORDS.search(trig):
            out.append((FAIL, "%s has a VOLUME-based trigger (%r) -- PR-7: rising volume is the "
                              "design working, not a reason to involve a person"
                        % (s.get("id"), trig[:70])))
    return out


def check_amber_gaps(reg, strict):
    out = []
    for s in reg.get("surfaces", []):
        if s.get("class") != "AMBER" or s.get("built") is True:
            continue
        out.append((FAIL if strict else WARN,
                    "%s (%s) is AMBER and not yet built -- %s"
                    % (s.get("id"), s.get("surface"), s.get("trigger"))))
    return out


def check_incentive_register(reg):
    out = []
    leaks = reg.get("incentive_register", {}).get("leaks", [])
    if not leaks:
        out.append((FAIL, "the incentive register is empty -- the Dragon Tail test has not been run"))
    for leak in leaks:
        for field in ("id", "surface", "actor", "if_they_optimise", "today", "action"):
            if not (leak.get(field) or "").strip():
                out.append((FAIL, "%s is missing '%s'" % (leak.get("id", "<no id>"), field)))
        if "Owner:" not in (leak.get("action") or ""):
            out.append((WARN, "%s names no owning role in its action" % leak.get("id")))
    return out


def check_rules_present(reg):
    out = []
    ids = {r.get("id") for r in reg.get("predesign_rules", [])}
    for want in ("PR-1", "PR-2", "PR-3", "PR-4", "PR-5", "PR-6", "PR-7", "PR-8", "PR-9"):
        if want not in ids:
            out.append((FAIL, "pre-design rule %s has gone missing from the register" % want))
    return out


def check_qc_pipeline(reg):
    """PR-9. QC gates the item; QA audits the system. MarketSquare had QA and no QC.
    Assert the DO -> CHECK pattern is declared, that its module is on disk, and that its
    eight constraints are all still named -- losing one silently is how a checker quietly
    becomes a rubber stamp."""
    out = []
    qc = reg.get("qc_pipeline")
    if not qc:
        out.append((FAIL, "no qc_pipeline declared -- PR-9 requires a DO -> CHECK stage"))
        return out
    mod = qc.get("module", "")
    if not mod:
        out.append((FAIL, "qc_pipeline names no module"))
    elif not os.path.exists(os.path.join(REPO, mod)):
        out.append((FAIL, "qc_pipeline module %s is not on disk -- the pattern is a claim, "
                          "not a mechanism" % mod))
    ns = {c.get("n") for c in qc.get("constraints", [])}
    for want in range(1, 9):
        if want not in ns:
            out.append((FAIL, "QC constraint %d has gone missing -- each one exists to make an "
                              "industry failure mode structurally impossible" % want))
    for c in qc.get("constraints", []):
        if not (c.get("failure_prevented") or "").strip():
            out.append((FAIL, "QC constraint %s names no failure it prevents -- a rule with no "
                              "reason gets deleted by the next session" % c.get("n")))
    if not qc.get("candidates"):
        out.append((WARN, "no QC candidate surfaces named -- the pattern exists but is wired "
                          "to nothing"))
    reds = {s.get("id") for s in reg.get("surfaces", []) if s.get("class") == "RED"}
    covered = {c.get("surface") for c in qc.get("candidates", [])}
    for rid in sorted(reds - covered):
        surf = next((s for s in reg.get("surfaces", []) if s.get("id") == rid), {})
        if surf.get("throughput") == "low":
            continue          # AS-11 the maintenance agent has mechanical gates instead
        if (surf.get("ai_check") or "").startswith("Not an AI decision"):
            continue          # AS-04 is deterministic by design -- nothing generated to inspect
        out.append((WARN, "%s is RED and has no DO -> CHECK spec named (PR-9)" % rid))
    return out


def main():
    strict = "--strict" in sys.argv
    reg = _load()

    groups = (
        ("register shape", check_shape(reg)),
        ("PR-6 no human in a throughput path", check_no_human_in_throughput(reg)),
        ("RED surfaces caught by a machine", check_red_caught_by_machine(reg)),
        ("exception ownership (interface roles)", check_exception_ownership(reg)),
        ("PR-7 triggers are exception-rate based", check_triggers_are_rate_based(reg)),
        ("AMBER build queue", check_amber_gaps(reg, strict)),
        ("PR-9 DO -> CHECK pipeline (QC, not QA)", check_qc_pipeline(reg)),
        ("Dragon Tail test", check_incentive_register(reg)),
        ("pre-design rules", check_rules_present(reg)),
    )

    fails = warns = 0
    print("AI ACCOUNTABILITY CHECK -- MarketSquare")
    print("=" * 74)
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

    S = reg.get("surfaces", [])
    counts = {c: sum(1 for s in S if s.get("class") == c) for c in ("RED", "AMBER", "GREEN")}
    hi = sum(1 for s in S if s.get("throughput") == "high")
    machine = sum(1 for s in S if s.get("human_touches") in ("none", "exceptions_only"))
    print("\n" + "=" * 74)
    print("%d surfaces: %d RED, %d AMBER, %d GREEN.  %d high-throughput."
          % (len(S), counts["RED"], counts["AMBER"], counts["GREEN"], hi))
    print("%d of %d surfaces keep humans off the per-item path." % (machine, len(S)))
    print("%d FAIL, %d WARN" % (fails, warns))
    if fails:
        print("RESULT: accountability gap -- see FAIL lines above.")
        return 1
    print("RESULT: AI is policed by machines; humans own interfaces, not throughput.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
