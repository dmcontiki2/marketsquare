#!/usr/bin/env python3
"""
fix.py - Orchestration v2 . Phase 3 (Fix). Consumes the GREEN lane of a triaged run, one
item at a time, under the verify-or-revert + lane gates, and records the result. It is the
connective tissue's downstream end: Detect -> Triage -> *Fix*.

fix.py does NOT write product code itself (the surgical edit is the Sonnet checkpoint, applied
with the established bash-python str-replace + node/ast + smoke discipline). It is the
deterministic queue-manager, gate-recorder and board-regenerator:

  --next                                   show the top green queued item + the safety checklist
  --ship  <id> --detail "..."              mark it shipped (deployed), record + drain the board
  --route <id> --to <ref> --reason "..."   send it to another track (not a green code fix), record
  --fail  <id> --reason "..."              mark it failed (reverted) and stage it, record

RED is never consumable here; amber stays staged, never shipped. Reads/writes triaged.json
(status queued -> shipped/routed/failed), appends fix_results.json, regenerates triage_board.html
(reuses the Triage board renderer + splices a 'Fix - this run' panel; Triage stays untouched).
"""
import argparse, datetime, json, os, sys
import triage  # same dir - reuse BOARD_CSS, esc, render_board


def load(p): return json.load(open(p, encoding="utf-8"))
def save(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2); f.write("\n")
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def green_queue(tri):
    return [x for x in tri["items"] if x["status"] == "queued" and x["lane"] == "green"]


def find(tri, iid):
    for x in tri["items"]:
        if iid in (x["id"], x.get("ref"), x.get("src")):
            return x
    return None


def recompute_summary(tri):
    it = tri["items"]; s = tri["summary"]
    s["to_fix_green"] = sum(1 for x in it if x["status"] == "queued" and x["lane"] == "green")
    s["review_amber"] = sum(1 for x in it if x["status"] == "staged" and x["lane"] == "amber")
    s["need_you_red"] = sum(1 for x in it if x["status"] == "staged" and x["lane"] == "red")
    s["shipped"] = sum(1 for x in it if x["status"] == "shipped")
    s["routed"] = sum(1 for x in it if x["status"] == "routed")
    s["failed"] = sum(1 for x in it if x["status"] == "failed")


def _panel(shipped, routed, failed):
    e = triage.esc
    def rows(items):
        out = ""
        for x in items:
            ref = e(x.get("ref") or x.get("src") or "")
            to = (" &rarr; " + e(x.get("routed_to"))) if x.get("routed_to") else ""
            why = e(x.get("ship_detail") or x.get("route_reason") or x.get("fail_reason") or "")
            out += ('<div class="it g"><div class="top"><span class="pri %s">%s</span>'
                    '<b>%s</b> <span class="vp filed">%s%s</span></div>'
                    '<div class="meta">%s</div></div>') % (x["priority"], x["priority"], e(x["title"]), ref, to, why)
        return out or '<div class="empty">none</div>'
    extra = ''
    if failed:
        extra = '<div class="col r"><h3>&#9888; Failed / reverted <span class="cnt">%d</span></h3>%s</div>' % (len(failed), rows(failed))
    return ('<h2>Fix &mdash; this run</h2><div class="lanes" style="grid-template-columns:1fr 1fr">'
            '<div class="col g"><h3>&#128640; Shipped <span class="cnt">%d</span></h3>%s</div>'
            '<div class="col"><h3>&#8618; Routed onward <span class="cnt">%d</span></h3>%s</div>'
            '%s</div>') % (len(shipped), rows(shipped), len(routed), rows(routed), extra)


def regen_board(tri, outdir):
    html = triage.render_board(tri)
    shipped = [x for x in tri["items"] if x["status"] == "shipped"]
    routed = [x for x in tri["items"] if x["status"] == "routed"]
    failed = [x for x in tri["items"] if x["status"] == "failed"]
    if shipped or routed or failed:
        html = html.replace('<div class="flowline">', _panel(shipped, routed, failed) + '<div class="flowline">', 1)
    with open(os.path.join(outdir, "triage_board.html"), "w", encoding="utf-8") as f:
        f.write(html)


def record(outdir, entry):
    p = os.path.join(outdir, "fix_results.json")
    log = load(p) if os.path.exists(p) else {"schema": "fix-v1", "results": []}
    log["results"].append(entry)
    save(p, log)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--next", action="store_true")
    ap.add_argument("--ship"); ap.add_argument("--route"); ap.add_argument("--fail")
    ap.add_argument("--detail", default=""); ap.add_argument("--to", default=""); ap.add_argument("--reason", default="")
    a = ap.parse_args()
    tp = os.path.join(a.dir, "triaged.json")
    tri = load(tp)

    if a.next or not (a.ship or a.route or a.fail):
        q = green_queue(tri)
        if not q:
            print("Fix queue empty - no green items to ship."); return 0
        x = q[0]
        print("NEXT GREEN ITEM: %s (%s) [%s]" % (x["id"], x.get("ref") or x.get("src"), x["priority"]))
        print("  title  : %s" % x["title"])
        print("  file   : %s   key: %s" % (x["file"], x["dedupe_key"]))
        print("  symptom: %s" % x["symptom"])
        print("  CHECKLIST: backup -> surgical edit (bash-python, never Edit/Write) -> node --check / ast.parse")
        print("             -> smoke all-green -> deploy + chmod 644 + CF purge -> record (--ship)")
        print("  (%d green item(s) queued)" % len(q))
        return 0

    iid = a.ship or a.route or a.fail
    x = find(tri, iid)
    if not x:
        print("item not found: %s" % iid); return 1
    if a.ship and x["lane"] != "green":
        print("REFUSING: %s is lane=%s - Fix only ships GREEN. Amber/red stay staged for the human." % (iid, x["lane"])); return 2

    if a.ship:
        x["status"] = "shipped"; x["shipped_at"] = now(); x["ship_detail"] = a.detail
        verb, extra = "ship", {"detail": a.detail}
    elif a.route:
        x["status"] = "routed"; x["routed_to"] = a.to; x["route_reason"] = a.reason
        verb, extra = "route", {"to": a.to, "reason": a.reason}
    else:
        x["status"] = "failed"; x["fail_reason"] = a.reason
        verb, extra = "fail", {"reason": a.reason}

    recompute_summary(tri)
    save(tp, tri)
    rec = {"at": now(), "id": x["id"], "ref": x.get("ref"), "lane": x["lane"],
           "priority": x["priority"], "action": verb, "title": x["title"]}
    rec.update(extra)
    record(a.dir, rec)
    regen_board(tri, a.dir)
    print("%s %s (%s) -> status=%s | %d green left in queue"
          % (verb, x["id"], x.get("ref"), x["status"], len(green_queue(tri))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
