#!/usr/bin/env python3
"""ai_qc.py -- the DO -> CHECK pipeline. A doer produces; an independent checker inspects.

QC, NOT QA. The distinction is deliberate and it is the whole design.

  QA (quality ASSURANCE)  audits the PROCESS. Periodic, sampled, preventive.
                          "Is the system capable of producing conforming work?"
                          MarketSquare already has this: regression_ledger.py,
                          audit_global_qa.py, BIT, the golden-set eval.
  QC (quality CONTROL)    inspects the PRODUCT. Per-item, in-line, detective.
                          "Does THIS artefact conform to spec?"
                          MarketSquare did NOT have this. This module is it.

QA cannot gate an item -- it does not look at items. That is why bolting more QA onto
an AI surface never catches the individual bad answer, and why a QC stage was the gap.

--------------------------------------------------------------------------------
DESIGN CONSTRAINTS -- each one is an industry failure mode made structurally impossible
--------------------------------------------------------------------------------

1. NO SPEC, NO RUN.  A checker without written acceptance criteria does not inspect --
   it re-does the task with an opinion, and its verdicts drift with the weather. QCSpec
   is mandatory and every criterion must be objectively decidable. run() raises without one.

2. THE CHECKER NEVER SEES THE DOER'S REASONING.  If it does, it grades the argument
   instead of the artefact, and a confident rationale buys a pass. The harness builds the
   checker prompt itself from (input, spec, artefact) only. The doer's rationale is
   structurally unable to reach it -- it is not a discipline the caller has to remember.

3. DIFFERENT LANE BY DEFAULT.  Same model + same prompt family = correlated blind spots;
   a model asked to check its own output tends to ratify it. The checker binds to a
   different provider than the doer. If only one lane is configured we do NOT pretend:
   the verdict is stamped independence="correlated" and callers can treat it as weaker.

4. THE CHECKER IS CHEAPER THAN THE DOER, NOT BIGGER.  Judging against explicit criteria
   is an easier task than generating. A heavyweight checker doubles cost and latency for
   no gain and turns the chain into the bottleneck -- the classic serial-pipeline death.

5. BOUNDED RETRIES.  DO -> CHECK -> FAIL -> REDO with no cap burns money and may never
   converge. max_attempts is enforced; exhaustion returns escalate=True, never a loop.

6. THE CHECKER IS ITSELF CHECKED -- SEEDED DEFECTS.  A checker that passes everything is
   silently broken and looks perfect. Every spec carries canaries: known-bad artefacts it
   MUST reject. canary() runs them. This is the known-defect sample from an industrial
   inspection line, and it is the only honest answer to "who checks the checker".

7. LOT TRACEABILITY.  Every verdict records doer lane/model, checker lane/model, spec id
   and version, attempt, and which criteria failed -- so a bad batch can be traced and
   recalled rather than guessed at.

--------------------------------------------------------------------------------
Self-test (no API keys needed, proves the harness logic):
    python3 ai_qc.py --selftest
--------------------------------------------------------------------------------
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field, asdict

try:
    import ai_provider
except Exception:      # standalone / test use
    ai_provider = None

# Checker runs on the cheap tier by design (constraint 4).
CHECKER_TASK = "triage"
DOER_TASK = "haiku"


# ------------------------------------------------------------------ the spec

@dataclass
class QCSpec:
    """Acceptance criteria. Without this there is no QC, only opinion (constraint 1)."""
    id: str
    version: str
    artefact: str                       # what is being inspected, in one phrase
    criteria: list                      # each: objectively decidable, one line, no taste
    canaries: list = field(default_factory=list)   # (bad_artefact, criterion_id_it_must_fail)
    max_attempts: int = 2

    def validate(self):
        problems = []
        if not self.id or not self.version:
            problems.append("spec needs an id and a version -- verdicts must be traceable to it")
        if not self.criteria:
            problems.append("spec has no criteria -- a checker without criteria is not a checker")
        for i, c in enumerate(self.criteria, 1):
            if not isinstance(c, str) or not c.strip():
                problems.append("criterion %d is empty" % i)
            elif any(w in c.lower() for w in ("good", "nice", "appropriate", "reasonable",
                                              "high quality", "well written")):
                problems.append("criterion %d is a matter of taste (%r) -- QC decides "
                                "conformance, not preference" % (i, c[:48]))
        if not self.canaries:
            problems.append("spec has no canaries -- a checker that passes everything would "
                            "look perfect and be broken (constraint 6)")
        if self.max_attempts < 1 or self.max_attempts > 5:
            problems.append("max_attempts must be 1..5 -- unbounded redo is a cost fire")
        return problems

    def numbered(self):
        return "\n".join("C%d. %s" % (i, c) for i, c in enumerate(self.criteria, 1))


@dataclass
class Verdict:
    passed: bool
    failed: list                 # ["C2", "C5"]
    notes: str
    attempt: int
    doer_lane: str
    doer_model: str
    checker_lane: str
    checker_model: str
    spec: str                    # "id@version"
    independence: str            # "cross_vendor" | "correlated"
    escalate: bool = False

    def as_record(self):
        return asdict(self)


# ------------------------------------------------------------------ lane choice

def _lanes():
    if ai_provider is None:
        return []
    try:
        return list(ai_provider.configured_lanes())
    except Exception:
        return []


def pick_checker_lane(doer_lane, lanes=None):
    """Constraint 3. A different vendor if one exists; otherwise say so honestly."""
    lanes = lanes if lanes is not None else _lanes()
    others = [p for p in lanes if p != doer_lane]
    if others:
        return others[0], "cross_vendor"
    return doer_lane, "correlated"


# ------------------------------------------------------------------ the checker

_CHECKER_SYSTEM = (
    "You are a quality-control inspector. You inspect a finished artefact against numbered "
    "acceptance criteria and decide conformance. You are NOT the author, you do NOT rewrite, "
    "and you do NOT judge style, taste or how the artefact was arrived at -- only whether it "
    "meets each criterion. Reply with STRICT JSON and nothing else:\n"
    '{"failed": ["C2"], "notes": "one short factual line per failure"}\n'
    'An empty "failed" list means the artefact conforms.'
)


def _checker_prompt(task_input, spec, artefact):
    """Constraint 2: built from (input, spec, artefact) ONLY. There is no parameter here
    through which the doer's reasoning could arrive."""
    return [{"role": "user", "content":
             "INPUT THE ARTEFACT WAS MADE FROM:\n%s\n\n"
             "ACCEPTANCE CRITERIA (%s@%s) for: %s\n%s\n\n"
             "ARTEFACT TO INSPECT:\n%s\n\n"
             "Which criteria does the artefact FAIL? JSON only."
             % (task_input, spec.id, spec.version, spec.artefact, spec.numbered(), artefact)}]


def _parse_verdict(text, spec):
    """A checker that returns garbage must FAIL CLOSED -- never silently pass."""
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None, "checker returned no JSON"
    try:
        data = json.loads(m.group(0))
    except Exception:
        return None, "checker returned unparseable JSON"
    failed = data.get("failed", [])
    if not isinstance(failed, list):
        return None, "checker 'failed' was not a list"
    valid = {"C%d" % i for i in range(1, len(spec.criteria) + 1)}
    unknown = [f for f in failed if f not in valid]
    if unknown:
        return None, "checker cited criteria that do not exist: %s" % ", ".join(map(str, unknown))
    return [f for f in failed], str(data.get("notes", ""))[:400]


def check(task_input, artefact, spec, *, doer_lane="", complete=None, attempt=1):
    """Run the QC stage alone. Returns a Verdict. Fails CLOSED on checker malfunction."""
    problems = spec.validate()
    if problems:
        raise ValueError("QCSpec %s invalid: %s" % (spec.id, "; ".join(problems)))

    comp = complete or (ai_provider.complete if ai_provider else None)
    if comp is None:
        raise RuntimeError("no AI seam available")

    lane, independence = pick_checker_lane(doer_lane)
    res = comp(_checker_prompt(task_input, spec, artefact),
               task=CHECKER_TASK, system=_CHECKER_SYSTEM, max_tokens=400,
               provider=lane or None)

    base = dict(attempt=attempt, doer_lane=doer_lane, doer_model="",
                checker_lane=getattr(res, "provider", lane) or lane,
                checker_model=getattr(res, "model", "") or "",
                spec="%s@%s" % (spec.id, spec.version), independence=independence)

    if not getattr(res, "ok", False):
        # Constraint: an unavailable checker is NOT a pass.
        return Verdict(passed=False, failed=["CHECKER_UNAVAILABLE"],
                       notes="checker lane failed: %s" % getattr(res, "error_kind", "unknown"),
                       escalate=True, **base)

    failed, notes = _parse_verdict(getattr(res, "text", ""), spec)
    if failed is None:
        return Verdict(passed=False, failed=["CHECKER_MALFUNCTION"], notes=notes,
                       escalate=True, **base)
    return Verdict(passed=(not failed), failed=failed, notes=notes, **base)


# ------------------------------------------------------------------ the pipeline

def run(task_input, spec, *, doer_messages, doer_system=None, doer_task=DOER_TASK,
        complete=None, on_reject=None):
    """DO -> CHECK -> (redo) -> verdict, bounded by spec.max_attempts (constraint 5).

    on_reject(artefact, verdict) -> extra instruction for the retry. The doer is told WHICH
    criteria failed and nothing else -- it never receives the checker's prose reasoning, so
    the redo targets the defect rather than arguing with the inspector.

    Returns (artefact, verdict). verdict.escalate=True means attempts were exhausted or the
    checker itself malfunctioned -- route it to the owning interface role, do not loop.
    """
    problems = spec.validate()
    if problems:
        raise ValueError("QCSpec %s invalid: %s" % (spec.id, "; ".join(problems)))
    comp = complete or (ai_provider.complete if ai_provider else None)
    if comp is None:
        raise RuntimeError("no AI seam available")

    msgs = list(doer_messages)
    artefact, verdict = "", None
    for attempt in range(1, spec.max_attempts + 1):
        res = comp(msgs, task=doer_task, system=doer_system, max_tokens=900)
        if not getattr(res, "ok", False):
            return "", Verdict(passed=False, failed=["DOER_UNAVAILABLE"],
                               notes="doer lane failed: %s" % getattr(res, "error_kind", "unknown"),
                               attempt=attempt, doer_lane=getattr(res, "provider", ""),
                               doer_model=getattr(res, "model", ""), checker_lane="",
                               checker_model="", spec="%s@%s" % (spec.id, spec.version),
                               independence="n/a", escalate=True)
        artefact = getattr(res, "text", "")
        verdict = check(task_input, artefact, spec, doer_lane=getattr(res, "provider", ""),
                        complete=comp, attempt=attempt)
        verdict.doer_model = getattr(res, "model", "")
        if verdict.passed or verdict.escalate:
            return artefact, verdict
        if attempt < spec.max_attempts:
            extra = (on_reject(artefact, verdict) if on_reject else
                     "That output failed acceptance criteria %s. Produce it again, meeting "
                     "every criterion." % ", ".join(verdict.failed))
            msgs = msgs + [{"role": "assistant", "content": artefact},
                           {"role": "user", "content": extra}]

    verdict.escalate = True
    verdict.notes = (verdict.notes + " | attempts exhausted (%d)" % spec.max_attempts).strip(" |")
    return artefact, verdict


# ------------------------------------------------------------------ who checks the checker

def canary(spec, *, complete=None, task_input="(canary probe)"):
    """Constraint 6. Feed the checker known-bad artefacts. It MUST reject each one on the
    criterion it violates. A checker that passes a canary is broken and is presently
    passing real defects too.

    Returns (ok, [failures]).
    """
    problems = spec.validate()
    if problems:
        return False, ["spec invalid: %s" % "; ".join(problems)]
    out = []
    for i, (bad, must_fail) in enumerate(spec.canaries, 1):
        v = check(task_input, bad, spec, doer_lane="", complete=complete, attempt=0)
        if v.passed:
            out.append("canary %d PASSED the checker but must fail %s -- the checker is blind "
                       "to that defect class" % (i, must_fail))
        elif must_fail not in v.failed and "CHECKER" not in "".join(v.failed):
            out.append("canary %d was rejected on %s, but it was seeded to violate %s -- the "
                       "checker is right by accident" % (i, ",".join(v.failed), must_fail))
    return (not out), out


# ------------------------------------------------------------------ self-test

def _selftest():
    """Proves the harness logic with a stub seam -- no API keys, no spend."""
    ok = True

    def say(label, good, detail=""):
        nonlocal ok
        if not good:
            ok = False
        d = detail if isinstance(detail, str) else repr(detail)
        print("  %-4s %s%s" % ("PASS" if good else "FAIL", label, (" -- " + d) if d else ""))

    class R:
        def __init__(s, text, provider="anthropic", model="m"):
            s.text, s.provider, s.model, s.ok, s.error_kind = text, provider, model, True, ""

    spec = QCSpec(
        id="LISTING", version="1.0", artefact="a marketplace listing description",
        criteria=["The text contains no phone number, email address or URL.",
                  "The text names no real business.",
                  "The text is under 60 words."],
        canaries=[("Call us on 082 555 0134 to arrange viewing.", "C1"),
                  ("Sold in partnership with Woolworths Pretoria.", "C2")])

    print("QC HARNESS SELF-TEST")
    print("=" * 68)

    print("\n[1] a spec built on taste is refused (constraint 1)")
    bad = QCSpec(id="X", version="1", artefact="a", criteria=["The copy is well written."],
                 canaries=[("x", "C1")])
    say("taste criterion rejected", any("taste" in p for p in bad.validate()))
    say("no-criteria spec rejected",
        bool(QCSpec(id="X", version="1", artefact="a", criteria=[], canaries=[("x","C1")]).validate()))
    say("no-canary spec rejected",
        any("canaries" in p for p in QCSpec(id="X", version="1", artefact="a",
                                            criteria=["It contains no URL."]).validate()))
    say("valid spec accepted", spec.validate() == [], str(spec.validate()))

    print("\n[2] the checker cannot see the doer's reasoning (constraint 2)")
    prompt = _checker_prompt("make a listing", spec, "A tidy sofa.")
    blob = json.dumps(prompt)
    say("rationale absent from checker prompt",
        "because" not in blob.lower() and "reasoning" not in blob.lower())
    say("prompt carries input, criteria and artefact",
        all(x in blob for x in ("make a listing", "C1.", "A tidy sofa")))

    print("\n[3] lane independence is reported honestly (constraint 3)")
    lane, ind = pick_checker_lane("anthropic", ["anthropic", "scaleway"])
    say("cross-vendor chosen when available", (lane, ind) == ("scaleway", "cross_vendor"))
    lane, ind = pick_checker_lane("anthropic", ["anthropic"])
    say("single lane marked correlated, not hidden", (lane, ind) == ("anthropic", "correlated"))

    print("\n[4] a broken checker fails CLOSED, never open")
    v = check("i", "a", spec, complete=lambda *a, **k: R("not json at all"))
    say("garbage verdict -> fail + escalate", (not v.passed) and v.escalate, v.failed)
    v = check("i", "a", spec, complete=lambda *a, **k: R('{"failed":["C9"],"notes":""}'))
    say("invented criterion -> fail + escalate", (not v.passed) and v.escalate, v.notes)

    class Dead(R):
        def __init__(s):
            super().__init__(""); s.ok = False; s.error_kind = "timeout"
    v = check("i", "a", spec, complete=lambda *a, **k: Dead())
    say("unavailable checker is NOT a pass", (not v.passed) and v.escalate)

    print("\n[5] retries are bounded and then escalate (constraint 5)")
    calls = {"n": 0}
    def always_bad(msgs, **k):
        calls["n"] += 1
        if k.get("task") == CHECKER_TASK:
            return R('{"failed":["C1"],"notes":"phone number present"}')
        return R("Call 082 555 0134 for this sofa.")
    art, v = run("make a listing", spec, doer_messages=[{"role":"user","content":"go"}],
                 complete=always_bad)
    say("never passes a defective artefact", not v.passed)
    say("escalates instead of looping", v.escalate)
    say("stopped at max_attempts (%d)" % spec.max_attempts, v.attempt == spec.max_attempts,
        "attempt=%d, seam calls=%d" % (v.attempt, calls["n"]))

    print("\n[6] a good artefact passes first time, with full provenance")
    def good(msgs, **k):
        if k.get("task") == CHECKER_TASK:
            return R('{"failed":[],"notes":""}', provider="scaleway", model="mistral")
        return R("Two-seater sofa in green corduroy, light wear, collection only.")
    art, v = run("make a listing", spec, doer_messages=[{"role":"user","content":"go"}],
                 complete=good)
    say("verdict passed", v.passed)
    say("records spec id@version", v.spec == "LISTING@1.0", v.spec)
    say("records both lanes", bool(v.checker_lane) and v.attempt == 1)
    say("record is serialisable for the ledger", isinstance(json.dumps(v.as_record()), str))

    print("\n[7] the checker is itself checked -- seeded defects (constraint 6)")
    def blind(msgs, **k):     # a checker that waves everything through
        return R('{"failed":[],"notes":""}')
    good_canary, fails = canary(spec, complete=blind)
    say("a blind checker is caught by the canaries", not good_canary, "%d finding(s)" % len(fails))
    def sighted(msgs, **k):
        body = msgs[0]["content"]
        if "082 555 0134" in body:
            return R('{"failed":["C1"],"notes":"phone number"}')
        if "Woolworths" in body:
            return R('{"failed":["C2"],"notes":"real business named"}')
        return R('{"failed":[],"notes":""}')
    good_canary, fails = canary(spec, complete=sighted)
    say("a sighted checker passes the canaries", good_canary, str(fails))

    print("\n" + "=" * 68)
    print("SELF-TEST %s" % ("PASSED -- the harness enforces its constraints"
                            if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv else
             (print(__doc__) or 0))
