#!/usr/bin/env python3
"""OPS-SWEEP-1 (15 Aug 2026, David's ask): the always-on half of Report & Fix.

Runs on the Hetzner box every 15 min from cron (installed by migrations/020).
Computes the same amber/red verdicts the Ops Map chips show, and emails David
when anything NEWLY goes amber/red (or recovers) - "as they appear", no browser,
no laptop needed. Replies drive the other half:

    REPORT            -> next sweep emails the full report regardless of change
    FIX TS-nnnn       -> queued; Fable's morning Cowork run picks it up
    REVIEW TS-nnnn    -> held for David's next interactive session

Replies land via the CF email worker (catch-all) in email_triage; this script
reads them by id watermark. State: .ops_sweep_state.json beside the DBs.
Stdlib only. Fails soft: a check that errors reports itself as RED sweep-error.
"""
import json, os, re, sys, socket, ssl, sqlite3, subprocess, urllib.request
from datetime import datetime, timezone

ROOT = "/var/www/marketsquare"
DB = f"{ROOT}/marketsquare.db"
STATE = f"{ROOT}/.ops_sweep_state.json"
BASE = "http://localhost:8000"
TO = "dmcontiki2@gmail.com"
FROM = "TrustSquare Ops <ops@mail.trustsquare.co>"
REPLY_TO = "fable@trustsquare.co"
DASH = "https://trustsquare.co/dashboard.html"

def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def proc_env():
    try:
        pid = subprocess.run(["systemctl", "show", "-p", "MainPID", "marketsquare"],
                             capture_output=True, text=True).stdout.strip().split("=")[1]
        env = {}
        with open(f"/proc/{pid}/environ", "rb") as f:
            for kv in f.read().split(b"\0"):
                if b"=" in kv:
                    k, v = kv.decode(errors="replace").split("=", 1)
                    env[k] = v
        return env
    except Exception:
        return {}

def http_json(url, timeout=12):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read())

def check_all():
    items = []  # (key, level green|amber|red, label, detail)
    def add(key, level, label, detail=""):
        items.append((key, level, label, detail))
    # 1. API health
    try:
        h = http_json(f"{BASE}/health")
        add("api.health", "green" if h.get("status") == "ok" else "red",
            "BEA /health", h.get("status", "?"))
    except Exception as e:
        add("api.health", "red", "BEA /health", f"unreachable: {e}")
    # 2. systemd services
    for svc in ("marketsquare", "nginx", "redis-server"):
        try:
            r = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True)
            st = r.stdout.strip()
            add(f"svc.{svc}", "green" if st == "active" else "red", f"service {svc}", st)
        except Exception as e:
            add(f"svc.{svc}", "red", f"service {svc}", str(e))
    # 3. resources (endpoint self-reports status per metric)
    try:
        res = http_json(f"{BASE}/health/resources")
        for metric in ("ram", "disk", "cpu", "bandwidth"):
            m = res.get(metric, {})
            st, pct = m.get("status", "?"), m.get("pct")
            level = "green" if st == "ok" else ("red" if st in ("critical", "red") else "amber")
            add(f"res.{metric}", level, f"{metric} {pct}%", st)
    except Exception as e:
        add("res.endpoint", "amber", "resources endpoint", f"unreadable: {e}")
    # 4. faults (the Maintenance chips)
    try:
        c = sqlite3.connect(DB)
        act = "status NOT IN ('closed','verified','rejected','duplicate','fixed') AND dup_of IS NULL"
        nb = c.execute(f"SELECT COUNT(*) FROM app_faults WHERE {act} AND severity='blocker'").fetchone()[0]
        nm = c.execute(f"SELECT COUNT(*) FROM app_faults WHERE {act} AND severity='major'").fetchone()[0]
        nq = c.execute("SELECT COUNT(*) FROM app_faults WHERE status='new'").fetchone()[0]
        refs = [r[0] for r in c.execute(
            f"SELECT ref FROM app_faults WHERE ({act} AND severity IN ('blocker','major')) OR status='new'")]
        c.close()
        add("faults.blockers", "red" if nb else "green", f"fault blockers {nb}", " ".join(refs) if nb else "")
        add("faults.majors", "amber" if nm else "green", f"fault majors {nm}", " ".join(refs) if nm else "")
        add("faults.queue", "amber" if nq else "green", f"triage queue {nq} new", " ".join(refs) if nq else "")
    except Exception as e:
        add("faults.db", "red", "fault register", f"unreadable: {e}")
    # 5. SSL days remaining
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection(("trustsquare.co", 443), timeout=12) as sock:
            with ctx.wrap_socket(sock, server_hostname="trustsquare.co") as w:
                exp = datetime.strptime(w.getpeercert()["notAfter"], "%b %d %H:%M:%S %Y %Z")
        days = (exp - datetime.utcnow()).days
        add("ssl.days", "red" if days < 7 else ("amber" if days < 21 else "green"),
            f"SSL {days}d remaining", exp.strftime("%Y-%m-%d"))
    except Exception as e:
        add("ssl.days", "amber", "SSL check", f"failed: {e}")
    return items

def read_commands(state):
    """David's email replies since the last seen triage row."""
    cmds, last = [], state.get("last_triage_id", 0)
    try:
        c = sqlite3.connect(DB)
        rows = c.execute(
            "SELECT id, from_addr, subject, body_preview FROM email_triage WHERE id > ? ORDER BY id", (last,)).fetchall()
        c.close()
        for rid, frm, subj, body in rows:
            state["last_triage_id"] = rid
            if TO.split("@")[0] not in (frm or "").lower():
                continue
            text = f"{subj or ''}\n{body or ''}"
            if re.search(r"\bREPORT\b", text, re.I):
                cmds.append(("REPORT", None))
            for m in re.finditer(r"\b(FIX|REVIEW)\s+(TS-\d{4}|[a-z]+\.[a-z]+)", text, re.I):
                cmds.append((m.group(1).upper(), m.group(2)))
    except Exception as e:
        print(f"[warn] command read failed: {e}")
    return cmds

def send_email(subject, html, key):
    req = urllib.request.Request("https://api.resend.com/emails",
        data=json.dumps({"from": FROM, "to": [TO], "reply_to": REPLY_TO,
                         "subject": subject, "html": html}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "marketsquare-ops-sweep/1.0"})  # Resend edge 403s the default urllib UA
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status

DOT = {"green": "&#128994;", "amber": "&#128992;", "red": "&#128308;"}
def render(items, changes, recovered):
    rows = "".join(
        f"<tr><td style='padding:4px 8px'>{DOT[lv]}</td>"
        f"<td style='padding:4px 8px;font-weight:600'>{lb}</td>"
        f"<td style='padding:4px 8px;color:#555'>{dt}</td></tr>"
        for k, lv, lb, dt in items if lv != "green")
    if not rows:
        rows = "<tr><td style='padding:4px 8px'>&#128994;</td><td style='padding:4px 8px'>All green</td><td></td></tr>"
    rec = ("<p style='color:#1d9e75;margin:8px 0'>Recovered: " + ", ".join(recovered) + "</p>") if recovered else ""
    return (f"<div style='font-family:Inter,Arial,sans-serif;max-width:560px;margin:auto'>"
            f"<h2 style='color:#0c1a2e'>Ops sweep &mdash; {now()}</h2>"
            f"<table style='border-collapse:collapse'>{rows}</table>{rec}"
            f"<p style='color:#555;font-size:13px;margin-top:14px'>Reply <b>FIX TS-nnnn</b> &mdash; Fable takes it "
            f"at its next scheduled run (laptop must be on).<br>Reply <b>REVIEW TS-nnnn</b> &mdash; held for your "
            f"next session.<br>Reply <b>REPORT</b> &mdash; full report within 15 min.<br>"
            f"<a href='{DASH}'>Open the dashboard</a> to review live.</p></div>")

def main():
    dry = "--dry" in sys.argv
    force_full = "--full" in sys.argv
    state = {}
    if os.path.exists(STATE):
        try: state = json.load(open(STATE))
        except Exception: state = {}
    items = check_all()
    prev = state.get("levels", {})
    changes = [(k, lv, lb, dt) for k, lv, lb, dt in items
               if lv != "green" and prev.get(k, "green") != lv]
    recovered = [lb for k, lv, lb, dt in items if lv == "green" and prev.get(k, "green") != "green"]
    cmds = read_commands(state)
    for verb, ref in cmds:
        if verb == "REPORT": force_full = True
        elif verb == "FIX":
            state.setdefault("fix_requests", []).append({"ref": ref, "at": now(), "status": "queued"})
            print(f"[cmd] FIX {ref} queued for Fable pickup")
        elif verb == "REVIEW":
            state.setdefault("review_requests", []).append({"ref": ref, "at": now()})
            print(f"[cmd] REVIEW {ref} held for next session")
    for k, lv, lb, dt in items:
        print(f"[{lv:5}] {k:16} {lb}  {dt}")
    should_send = force_full or changes or recovered
    if should_send and not dry:
        key = proc_env().get("RESEND_API_KEY", "")
        if not key:
            print("[error] RESEND_API_KEY not found - no email sent")
        else:
            n_a = sum(1 for _, lv, _, _ in items if lv == "amber")
            n_r = sum(1 for _, lv, _, _ in items if lv == "red")
            subj = (f"TrustSquare ops: {n_r} red, {n_a} amber" if (n_a or n_r)
                    else "TrustSquare ops: all green again")
            try:
                st = send_email(subj, render(items, changes, recovered), key)
                print(f"[email] sent ({st}): {subj}")
            except Exception as e:
                print(f"[error] email failed: {e}")
    elif should_send:
        print("[dry] would send email")
    if not dry:
        state["levels"] = {k: lv for k, lv, _, _ in items}
        state["last_run"] = now()
        json.dump(state, open(STATE, "w"), indent=1)
    return 0

if __name__ == "__main__":
    sys.exit(main())
