#!/usr/bin/env python3
"""
triage.py - Orchestration v2 - Phase 2 (Triage). Deterministic, zero-token.

Turns a raw Detect run (findings JSON) into a GOVERNED, de-duplicated, prioritized queue:

  1. DEDUPE    each finding (key = file::root-token, line-numbers EXCLUDED) against
               the ignore-list (dismissed), the BACKLOG (filed) and the CHANGELOG (done).
                 ignore-match  -> known-ignored  (drop, reason kept; never re-bother David)
                 done-match    -> resolved        (or REGRESSION if re-detected in a later run)
                 backlog-match -> known-filed     (reuse the existing id; do NOT duplicate)
                 no match      -> new             (mint a provisional id)
  2. CLASSIFY  a lane - RED checked FIRST by path/term (the policy's path pre-catch),
               GREEN only for confirmed safe classes, else AMBER. Fail-safe: ambiguous or
               needs-confirm NEVER goes green; we also take max(Detect-proposed, computed),
               so a red proposal is never downgraded.
  3. PRIORITIZE P1/P2/P3 (urgency, orthogonal to lane) - orders each lane.

Writes triaged.json (the machine queue Phase 3 Fix consumes) and triage_board.html (the
cockpit board). GREEN is the connective tissue to Fix; RED is human-only and NEVER auto-consumed.

Usage:
  python3 triage.py --findings detect_findings_S123.json
        [--root <dir with BACKLOG.md/CHANGELOG.md>] [--ignore ignore.json] [--out <dir>]

Model-tiering (ORCHESTRATION_POLICY 11): this is the deterministic default. A model is only
needed for the residual item a script genuinely cannot classify - it is surfaced, never guessed.
"""
import argparse
import datetime
import html
import json
import os
import re
import sys

# ----------------------------------------------------------------------------------
# Lane rules - auditable tables. RED = human-only, NEVER pre-authorized
# (Phase-0 design SS2 red lane = ORCHESTRATION_POLICY Gate 1 + Gate 2 + the v2 additions).
# ----------------------------------------------------------------------------------
RED_FILES = ("payments.py", "auth.py", ".env", "htpasswd", "database.py")
RED_PATTERNS = [
    # Gate 2 - financial release
    r"\btuppence\b", r"\bledger\b", r"\bcredit(?:s|ed|ing)?\b", r"\bdebit", r"\btop[- ]?up\b",
    r"\brefund", r"\bpayout", r"\breversal", r"\bpayment", r"paystack", r"\bwebhook", r"checkout",
    r"\bpricing\b", r"\bsubscription\b", r"plan activation", r"\bbilling\b", r"cost[- ]?ceiling",
    r"/dev/credit", r"\bslot price", r"\btier (?:price|cost)",
    # Gate 1 - regulatory
    r"\beula\b", r"\bterms\b", r"privacy policy", r"\bconsent\b", r"\bpopia\b", r"\bfsca\b",
    r"\bncc\b", r"\bcpa\b", r"banks act", r"direct marketer", r"non[- ]?refundable",
    r"\bkyc\b", r"sa[- ]?id\b", r"\bidentity\b", r"anonymity", r"\breveal\b", r"data retention",
    # v2 additions - secrets/security, permissions, deletions, public, schema
    r"\bsecret\b", r"api[_ ]?key", r"\bpassword\b", r"\bjwt\b", r"\bbearer\b", r"\bauth\b",
    r"admin[_ ]?key", r"\bpermission", r"\bcors\b", r"\bdelete\b", r"drop table", r"\bschema\b",
    r"\btruncate\b", r"destructive migration", r"\boutreach\b", r"send email", r"\bcampaign\b",
    r"public post", r"\bbroadcast\b",
]
# GREEN - auto-ship classes (only if confidence == confirmed AND no red hit).
GREEN_PATTERNS = [
    r"\bdemo\b", r"demo_listings", r"placeholder", r"\bph_\b",
    r"\brender", r"\blabel\b", r"\bbadge\b", r"\bcss\b", r"ms\.css", r"\btile\b", r"\bgrid\b",
    r"cosmetic", r"display", r"\bphoto", r"\bimage", r"\bhero\b", r"\bcurrency\b", r"\bicon\b",
    r"dead code", r"\bunused\b", r"\bf401\b", r"\bf841\b", r"\blint\b", r"vulture",
    r"redundant import", r"duplicate (?:dict )?key", r"changelog", r"status\.md", r"\bbacklog\b",
    r"doc drift", r"dashboard version", r"poka-?yoke", r"\bguard\b", r"\bmonitor\b",
]
LANE_RANK = {"green": 0, "amber": 1, "red": 2}
DONE_WORDS = ("fixed", "done", "resolved", "deployed", "shipped", "re-tagged",
              "poka-yoke", "live-verified", "auto-shipped", "✅")


def norm(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def first_token(s):
    m = re.search(r"[A-Za-z_][A-Za-z0-9_.\[\]]{2,}", s or "")
    return m.group(0) if m else "general"


def searchable(f):
    parts = [f.get(k, "") for k in ("slice", "symptom", "root_cause", "root_token", "file", "area")]
    parts += f.get("match_terms", [])
    return " ".join(parts).lower()


def dedupe_key(f):
    fa = os.path.basename(f.get("file") or f.get("area") or "general")
    rt = f.get("root_token") or first_token(f.get("root_cause", ""))
    return "{}::{}".format(norm(fa), norm(rt))


# ----------------------------------------------------------------------------------
# Second-brain sources
# ----------------------------------------------------------------------------------
ID_RE = re.compile(r"\b([A-Z]{2,}[0-9]*-[A-Z0-9]+|[A-Z]{2,}-\d+)\b")


def load_backlog(path):
    rows = []
    try:
        txt = open(path, encoding="utf-8").read()
    except Exception:
        return rows
    for line in txt.splitlines():
        m = ID_RE.search(line)
        if not m:
            continue
        low = line.lower()
        rows.append({"id": m.group(1), "text": low,
                     "done": ("✅" in line or " done" in low or "done)" in low or "resolved" in low)})
    return rows


def load_changelog_sections(path):
    secs = []
    try:
        txt = open(path, encoding="utf-8").read()
    except Exception:
        return secs
    chunks = re.split(r"(?m)^##\s+", txt)
    for c in chunks:
        if not c.strip():
            continue
        head = c.splitlines()[0]
        sm = re.search(r"session\s+(\d+)", head, re.I)
        low = c.lower()
        secs.append({"session": int(sm.group(1)) if sm else None,
                     "text": low, "has_done": any(w in low for w in DONE_WORDS)})
    return secs


def terms_in(text, terms):
    """All terms present as WHOLE tokens (word-boundaried), so 'per' never matches 'person'."""
    for t in terms:
        t = t.lower()
        if not re.search(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", text):
            return False
    return True


def match_ignore(key, text, ignore):
    for e in ignore:
        if e.get("key"):
            if e["key"] == key:
                return e
            continue  # keyed entries match by identity only - collision-free
        terms = [t.lower() for t in e.get("match_terms", [])]
        if terms and terms_in(text, terms):
            return e
    return None


def match_done(finding, sections):
    terms = [t.lower() for t in finding.get("match_terms", [])]
    if not terms:
        return None
    best = None
    for s in sections:
        if s["has_done"] and terms_in(s["text"], terms):
            if best is None or (s["session"] or 0) > (best["session"] or 0):
                best = s
    return best


def match_filed(finding, rows):
    terms = [t.lower() for t in finding.get("match_terms", [])]
    if not terms:
        return None
    for r in rows:
        if not r["done"] and terms_in(r["text"], terms):
            return r["id"]
    return None


# ----------------------------------------------------------------------------------
# Classifiers
# ----------------------------------------------------------------------------------
def classify_lane(text, file, confidence, proposed):
    files = (file or "").lower()
    red = any(rf in files for rf in RED_FILES) or any(re.search(p, text) for p in RED_PATTERNS)
    if red:
        lane = "red"
    elif confidence == "confirmed" and any(re.search(p, text) for p in GREEN_PATTERNS):
        lane = "green"
    else:
        lane = "amber"  # fail-safe: ambiguous / needs-confirm never reaches green
    # never downgrade what Detect already proposed
    if LANE_RANK.get(proposed, 0) > LANE_RANK[lane]:
        lane = proposed
    return lane


def classify_priority(sev, text):
    sev = (sev or "").upper()
    hot = ("crash", "referenceerror", "reference error", "breaks", "broken", "exposed",
           "unauth", "500", "money", "ledger", "secret")
    if sev == "HIGH" or any(w in text for w in hot):
        return "P1"
    if sev == "MED":
        return "P2"
    return "P3"


PRIO_RANK = {"P1": 0, "P2": 1, "P3": 2}


# ----------------------------------------------------------------------------------
# Triage
# ----------------------------------------------------------------------------------
def triage(findings_doc, ignore, backlog_rows, changelog_secs):
    run = findings_doc.get("detect_run", "detect-run")
    run_session = None
    sm = re.search(r"s?(\d+)", str(findings_doc.get("session") or run), re.I)
    if sm:
        run_session = int(sm.group(1))
    items = []
    for i, f in enumerate(findings_doc.get("findings", []), 1):
        text = searchable(f)
        key = dedupe_key(f)
        lane = classify_lane(text, f.get("file"), f.get("confidence"), f.get("proposed_lane", "green"))
        prio = classify_priority(f.get("sev"), text)

        verdict, ref, reason, status = "new", None, None, "queued"
        ig = match_ignore(key, text, ignore)
        filed = match_filed(f, backlog_rows)        # an OPEN backlog item is filed, not "done"
        done = match_done(f, changelog_secs)
        if ig:
            verdict, ref, reason, status = "known-ignored", ig.get("ref"), ig.get("reason"), "dropped"
        elif filed:
            verdict, ref, status = "known-filed", filed, "queued"
            reason = "Already on the backlog as {} - reusing, not re-filed.".format(filed)
        elif done:
            dsess = done["session"]
            if run_session is not None and dsess is not None and run_session > dsess:
                verdict, status = "regression", "queued"
                reason = "Re-detected after being fixed in Session {} - regression.".format(dsess)
            else:
                verdict, status = "resolved", "dropped"
                ref = "Session {}".format(dsess) if dsess else "changelog"
                reason = "Already fixed in {} - resolved this run.".format(ref)
        else:
            verdict, status = "new", "queued"

        # red is human-only: it is staged for David, never queued for Fix
        if status == "queued" and lane in ("amber", "red"):
            status = "staged"

        items.append({
            "id": "T-{}-{:02d}".format(run_session or 0, i),
            "src": f.get("id"),
            "dedupe_key": key,
            "title": f.get("slice") or f.get("symptom", "")[:60],
            "symptom": f.get("symptom", ""),
            "root_cause": f.get("root_cause", ""),
            "file": f.get("file", ""),
            "sev": (f.get("sev") or "").upper(),
            "priority": prio,
            "lane": lane,
            "verdict": verdict,
            "ref": ref,
            "reason": reason,
            "confidence": f.get("confidence", ""),
            "suggested_fix": f.get("fix", ""),
            "status": status,
            "consumed_by_fix": (status == "queued" and lane == "green"),
        })

    items.sort(key=lambda x: (LANE_RANK.get(x["lane"], 9), PRIO_RANK.get(x["priority"], 9)))
    summary = {
        "run": run, "session": run_session,
        "in": len(items),
        "to_fix_green": sum(1 for x in items if x["status"] == "queued" and x["lane"] == "green"),
        "review_amber": sum(1 for x in items if x["status"] == "staged" and x["lane"] == "amber"),
        "need_you_red": sum(1 for x in items if x["status"] == "staged" and x["lane"] == "red"),
        "resolved": sum(1 for x in items if x["verdict"] == "resolved"),
        "dismissed": sum(1 for x in items if x["verdict"] == "known-ignored"),
        "known_filed": sum(1 for x in items if x["verdict"] == "known-filed"),
        "new": sum(1 for x in items if x["verdict"] == "new"),
        "regression": sum(1 for x in items if x["verdict"] == "regression"),
    }
    return {
        "schema": "triage-v1",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_run": run,
        "scope": findings_doc.get("scope", ""),
        "summary": summary,
        "items": items,
    }


# ----------------------------------------------------------------------------------
# Board (visual, cockpit aesthetic)
# ----------------------------------------------------------------------------------
BOARD_CSS = """
:root{--navy:#0c1a2e;--ink:#1b2733;--muted:#5f6b78;--line:#e3e7ec;--bg:#f6f8fa;--card:#fff;
--green:#2f7d32;--greenbg:#e7f4e8;--amber:#9a6212;--amberbg:#fbf0db;--red:#a32d2d;--redbg:#fbe9e9;
--teal:#0f6e56;--tealbg:#e1f5ee;--blue:#185fa5;--bluebg:#e6f1fb;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font-family:'Segoe UI',Inter,system-ui,sans-serif;line-height:1.5}
.doc{max-width:980px;margin:0 auto;padding:24px 20px 60px}
header.hd{background:var(--navy);color:#fff;border-radius:16px;padding:20px 24px;margin-bottom:16px}
header.hd .ey{font-size:11.5px;letter-spacing:1.4px;text-transform:uppercase;color:#7fd4bb;font-weight:700}
header.hd h1{margin:6px 0 3px;font-size:22px;font-weight:700}
header.hd p{margin:0;color:#b9c4d0;font-size:13px}
.strip{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 6px}
.kpi{flex:1;min-width:96px;border:1px solid var(--line);border-radius:11px;padding:10px 12px;background:var(--card)}
.kpi .v{font-size:22px;font-weight:800;line-height:1}.kpi .l{font-size:11px;color:var(--muted);margin-top:3px;font-weight:600}
.kpi.g .v{color:var(--green)}.kpi.a .v{color:var(--amber)}.kpi.r .v{color:var(--red)}.kpi.t .v{color:var(--teal)}.kpi.m .v{color:var(--muted)}
h2{font-size:12px;letter-spacing:.8px;text-transform:uppercase;color:var(--muted);font-weight:700;margin:22px 0 10px}
.lanes{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.col{border:1px solid var(--line);border-radius:13px;padding:11px;background:var(--card)}
.col h3{margin:0 0 9px;font-size:13.5px;display:flex;justify-content:space-between;align-items:center}
.col.g h3{color:var(--green)}.col.a h3{color:var(--amber)}.col.r h3{color:var(--red)}
.col h3 .cnt{font-size:11px;font-weight:700;border-radius:20px;padding:2px 9px}
.col.g h3 .cnt{background:var(--greenbg);color:var(--green)}.col.a h3 .cnt{background:var(--amberbg);color:var(--amber)}.col.r h3 .cnt{background:var(--redbg);color:var(--red)}
.it{border:1px solid var(--line);border-radius:10px;padding:9px 11px;margin-bottom:8px;border-left:4px solid var(--line)}
.it.g{border-left-color:var(--green)}.it.a{border-left-color:var(--amber)}.it.r{border-left-color:var(--red)}
.it .top{display:flex;gap:6px;align-items:center;margin-bottom:3px;flex-wrap:wrap}
.it b{font-size:13px}
.it .meta{font-size:11px;color:var(--muted);margin-top:3px;line-height:1.4}
.it .meta code{background:#eef1f4;border-radius:5px;padding:1px 5px;font-size:10.5px}
.pri{font-size:10px;font-weight:800;border-radius:6px;padding:1px 6px}
.pri.P1{background:var(--redbg);color:var(--red)}.pri.P2{background:var(--amberbg);color:var(--amber)}.pri.P3{background:#eef1f4;color:var(--muted)}
.vp{font-size:10px;font-weight:700;border-radius:20px;padding:2px 8px;border:1px solid var(--line);color:var(--muted)}
.vp.filed{background:var(--bluebg);color:var(--blue);border-color:#cfe0f2}
.vp.new{background:var(--tealbg);color:var(--teal);border-color:#a9e0cf}
.vp.reg{background:var(--redbg);color:var(--red);border-color:#f0c4c4}
.empty{color:var(--muted);font-size:12px;font-style:italic;padding:8px 4px}
.flowline{background:var(--greenbg);border:1px solid #bfe0c1;border-radius:11px;padding:10px 14px;font-size:12.5px;color:#23612a;margin-top:12px}
.flowline b{color:var(--green)}
details{border:1px solid var(--line);border-radius:12px;background:var(--card);margin-top:10px;padding:4px 14px}
details summary{cursor:pointer;font-size:13px;font-weight:700;padding:9px 0;color:var(--ink)}
.drow{display:flex;gap:9px;align-items:flex-start;padding:8px 0;border-top:1px solid var(--line);font-size:12px}
.drow .dico{font-size:13px;margin-top:1px}
.drow .dttl{font-weight:600}.drow .dwhy{color:var(--muted);font-size:11.5px;margin-top:1px}
.dref{font-size:10.5px;color:var(--muted);white-space:nowrap}
.foot{text-align:center;color:var(--muted);font-size:11px;margin-top:24px}
@media(max-width:720px){.lanes{grid-template-columns:1fr}}
"""


def esc(s):
    return html.escape(str(s or ""))


def _item_card(it):
    vp = ""
    if it["verdict"] == "known-filed":
        vp = '<span class="vp filed">filed: {}</span>'.format(esc(it["ref"]))
    elif it["verdict"] == "new":
        vp = '<span class="vp new">new</span>'
    elif it["verdict"] == "regression":
        vp = '<span class="vp reg">REGRESSION</span>'
    fix = ' &middot; <span title="handed to Phase 3 Fix">&rarr; Fix</span>' if it["consumed_by_fix"] else ""
    return (
        '<div class="it {lane}"><div class="top"><span class="pri {pri}">{pri}</span>'
        '<b>{title}</b> {vp}</div>'
        '<div class="meta">{symptom}<br><code>{file}</code> &middot; {key}{fix}</div></div>'
    ).format(lane=it["lane"], pri=it["priority"], title=esc(it["title"]), vp=vp,
             symptom=esc(it["symptom"]), file=esc(it["file"] or "-"), key=esc(it["dedupe_key"]), fix=fix)


def render_board(tri):
    s = tri["summary"]
    queued = [x for x in tri["items"] if x["status"] in ("queued", "staged")]
    green = [x for x in queued if x["lane"] == "green"]
    amber = [x for x in queued if x["lane"] == "amber"]
    red = [x for x in queued if x["lane"] == "red"]
    resolved = [x for x in tri["items"] if x["verdict"] == "resolved"]
    dismissed = [x for x in tri["items"] if x["verdict"] == "known-ignored"]

    def col(items, lane, title, sub):
        body = "".join(_item_card(x) for x in items) or '<div class="empty">{}</div>'.format(sub)
        return ('<div class="col {l}"><h3>{t}<span class="cnt">{n}</span></h3>{b}</div>'
                ).format(l=lane, t=title, n=len(items), b=body)

    drows = ""
    for x in resolved:
        drows += ('<div class="drow"><span class="dico">&#10003;</span><div style="flex:1">'
                  '<div class="dttl">{t}</div><div class="dwhy">{w}</div></div>'
                  '<div class="dref">{r}</div></div>').format(
                      t=esc(x["title"]), w=esc(x["reason"]), r=esc(x["ref"] or ""))
    dis = ""
    for x in dismissed:
        dis += ('<div class="drow"><span class="dico">&#8856;</span><div style="flex:1">'
                '<div class="dttl">{t}</div><div class="dwhy">{w}</div></div>'
                '<div class="dref">{r}</div></div>').format(
                    t=esc(x["title"]), w=esc(x["reason"]), r=esc(x["ref"] or ""))

    red_note = ("" if red else
                '<div class="empty" style="font-style:normal">Nothing in the red lane this run &mdash; '
                'no money, secrets, permissions, deletions or public actions were touched. '
                'Red always waits for you; today it has nothing to ask.</div>')

    return """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Triage Board - Orchestration v2</title><style>{css}</style></head><body><div class="doc">
<header class="hd"><div class="ey">Solar Council &middot; TrustSquare &middot; Orchestration v2 &middot; Phase 2</div>
<h1>Triage Board</h1><p>{run} &middot; {scope} &middot; triaged {gen}</p></header>

<div class="strip">
  <div class="kpi g"><div class="v">{to_fix}</div><div class="l">&rarr; Fix (green)</div></div>
  <div class="kpi a"><div class="v">{amber}</div><div class="l">review (amber)</div></div>
  <div class="kpi r"><div class="v">{red}</div><div class="l">needs you (red)</div></div>
  <div class="kpi t"><div class="v">{resolved}</div><div class="l">resolved</div></div>
  <div class="kpi m"><div class="v">{dismissed}</div><div class="l">dismissed</div></div>
  <div class="kpi m"><div class="v">{n_in}</div><div class="l">findings in</div></div>
</div>

<h2>The governed queue &middot; who may act</h2>
<div class="lanes">{green_col}{amber_col}{red_col}</div>
{red_note}
<div class="flowline"><b>Detect &rarr; Fix tissue:</b> the {to_fix} green item(s) above are the queue
Phase 3 (Fix) consumes, highest priority first. Amber is do-and-notify; red is human-only and never auto-consumed.</div>

<details open><summary>&#10003; Resolved this run ({n_res})</summary>{drows}</details>
<details><summary>&#8856; Dismissed &mdash; won't be re-raised ({n_dis})</summary>{dis}</details>

<p class="foot">Generated by triage.py (deterministic, zero-token) &middot; triage_board.html &middot; behind the orchestrator login</p>
</div></body></html>""".format(
        css=BOARD_CSS, run=esc(tri["source_run"]), scope=esc(tri["scope"]), gen=esc(tri["generated_at"]),
        to_fix=s["to_fix_green"], amber=s["review_amber"], red=s["need_you_red"], resolved=s["resolved"],
        dismissed=s["dismissed"], n_in=s["in"],
        green_col=col(green, "g", "&#128994; Green", "no green items"),
        amber_col=col(amber, "a", "&#128993; Amber", "no amber items"),
        red_col=col(red, "r", "&#128308; Red", "no red items"),
        red_note=red_note, n_res=len(resolved), drows=drows or '<div class="empty">none</div>',
        n_dis=len(dismissed), dis=dis or '<div class="empty">none</div>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", required=True)
    ap.add_argument("--root", default=None, help="dir holding BACKLOG.md + CHANGELOG.md (default: findings dir/..)")
    ap.add_argument("--ignore", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    fdir = os.path.dirname(os.path.abspath(a.findings))
    root = a.root or os.path.dirname(fdir)  # orchestration_v2/ -> MarketSquare/
    out = a.out or fdir
    ignore_path = a.ignore or os.path.join(fdir, "ignore.json")

    findings_doc = json.load(open(a.findings, encoding="utf-8"))
    ignore = json.load(open(ignore_path, encoding="utf-8")).get("ignored", []) if os.path.exists(ignore_path) else []
    backlog_rows = load_backlog(os.path.join(root, "BACKLOG.md"))
    changelog_secs = load_changelog_sections(os.path.join(root, "CHANGELOG.md"))

    tri = triage(findings_doc, ignore, backlog_rows, changelog_secs)

    with open(os.path.join(out, "triaged.json"), "w", encoding="utf-8") as f:
        json.dump(tri, f, indent=2)
        f.write("\n")
    with open(os.path.join(out, "triage_board.html"), "w", encoding="utf-8") as f:
        f.write(render_board(tri))

    s = tri["summary"]
    print("triage: %d in -> %d green->Fix, %d amber, %d red | %d resolved, %d dismissed, %d filed, %d new, %d regression" % (
        s["in"], s["to_fix_green"], s["review_amber"], s["need_you_red"],
        s["resolved"], s["dismissed"], s["known_filed"], s["new"], s["regression"]))
    print("wrote: %s  +  %s" % (os.path.join(out, "triaged.json"), os.path.join(out, "triage_board.html")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
