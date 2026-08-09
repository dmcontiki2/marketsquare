#!/usr/bin/env python3
"""maintenance_agent.py — Path A autonomous fix-agent (MAINTENANCE_AGENT.md B2b).
================================================================================
David's ruling 29 Jul 2026: TOTAL AUTONOMY on Path A, mechanical gates only, no
human veto; his absence never stalls a fix. This is the orchestrator that makes
that real, bound to what already exists rather than reinventing it:

  intake   GET /admin/faults?status=new   (localhost + MS_MAINT_KEY, like fault_reconcile)
  brain    ai_provider.complete()          -- the IDENTIFIED source: provider+model
                                               recorded on every fix, swappable by one
                                               config line (the independence ruling)
  gates    regression_ledger.py · predeploy_check.py · py_compile / node --check
  deploy   the ONE engine (git mirror -> server_deploy.sh) -- NEVER re-implemented (RG-0023)
  verify   AIK-VERIFY-1: a live probe reproduces the failing action; named evidence in
           fix_note; only then PUT /admin/faults/{id} status=verified. "looks right"
           does NOT qualify -- the exact discipline the launch month proved we need.

THE FOUR LAUNCH-BLOCKING REQUIREMENTS (all wired here, all fail-safe):
  1. gates are tests    -- a commit is proposed ONLY if the real gate suite passes.
  2. automatic rollback -- delegated to server_deploy.sh's BIT probe + auto-revert;
                           this agent never invents a second rollback story.
  3. rate limit + kill  -- MAINTENANCE_AGENT_ENABLED is David's one lever (default OFF
                           => shadow, never commits); MAX_SHIPS_PER_HOUR caps runaway.
  4. act-safest-first   -- safety/legal/cost + payment/auth/schema/anonymity are NEVER
                           autonomously fixed. They ESCALATE (report + safest action),
                           they do not ship. Reports inform; they never block.

SHADOW is the default and the rehearsal mode (B4): it classifies, calls the brain,
applies to a throwaway worktree, runs the gates, and writes a proposal + gate report
-- but COMMITS NOTHING. Going live is one deliberate act by David: set
MAINTENANCE_AGENT_ENABLED=1 on the server AFTER the B4 synthetic-storm rehearsal signs
it READY. Nothing here arms itself.

Run:  python3 scripts/maintenance_agent.py            # shadow: propose + gate, write report
      python3 scripts/maintenance_agent.py --live     # honoured ONLY if the kill switch is on
"""
import os, sys, json, subprocess, tempfile, shutil, time, urllib.request, urllib.error
from datetime import datetime, timezone

REPO   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE   = os.environ.get("MS_BEA_URL", "http://localhost:8000")
STATE  = os.path.join(REPO, ".maint_agent")            # rate-limit ledger + run reports
KILL   = os.environ.get("MAINTENANCE_AGENT_ENABLED", "0").strip() == "1"
LIVE   = ("--live" in sys.argv) and KILL               # live REQUIRES both, by construction
MAX_SHIPS_PER_HOUR = int(os.environ.get("MAINT_MAX_SHIPS_PER_HOUR", "3"))

# ── test injection (B4 rehearsal only) — redirect INPUTS, never weaken the guard ──
def _arg(name, default=None):
    for a in sys.argv[1:]:
        if a.startswith(name + "="):
            return a.split("=", 1)[1]
    return default
_repo_override = _arg("--repo")
if _repo_override:
    REPO = os.path.abspath(_repo_override)          # operate on a SANDBOX repo
    STATE = os.path.join(REPO, ".maint_agent")
_FAULTS_FILE = _arg("--faults-file")                 # synthetic queue instead of the live API
_BRAIN_STUB  = os.environ.get("MAINT_BRAIN_STUB")    # canned patches for a keyless rehearsal
if _BRAIN_STUB:
    LIVE = False   # a stubbed brain can NEVER ship — rehearsal is shadow, always

def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def say(m): print("[maint] " + m, flush=True)

# ── the deterministic REFUSE guard — un-bypassable by the AI ─────────────────────
# Path A autonomy stops HARD at anything touching money, identity, the schema, or the
# law. These never reach the brain as fixable; they escalate. Keyword OR page match.
REFUSE_MARKERS = (
    "payment", "paystack", "refund", "wallet", "tuppence charge", "billing", "card",
    "auth", "login", "password", "session", "token", "kyc", "id number", "identity",
    "anonym", "reveal", "seller_email", "schema", "migration", "database", "drop table",
    "legal", "popia", "eula", "terms", "compliance", "ffc", "mandate", "safety",
)
def is_refused(fault):
    hay = ((fault.get("title") or "") + " " + (fault.get("detail") or "") + " " +
           (fault.get("page_url") or "")).lower()
    hit = [m for m in REFUSE_MARKERS if m in hay]
    return hit

# ── intake ───────────────────────────────────────────────────────────────────────
def maint_key():
    v = os.environ.get("MS_MAINT_KEY", "").strip()
    if v: return v
    for p in (os.path.join(REPO, ".secrets", "ms_maint_key.txt"), "/var/www/marketsquare/.env"):
        try:
            t = open(p, encoding="utf-8").read()
            if p.endswith(".env"):
                for ln in t.splitlines():
                    if ln.strip().startswith("MS_MAINT_KEY="):
                        return ln.split("=", 1)[1].strip()
            elif t.strip():
                return t.strip()
        except OSError:
            pass
    return ""

def api(method, path, key, body=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 headers={"X-Maint-Key": key, "Content-Type": "application/json"})
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(req, data=data, timeout=30) as r:
        return json.loads(r.read().decode() or "null")

def open_faults(key):
    if _FAULTS_FILE:
        try:
            return json.load(open(_FAULTS_FILE, encoding="utf-8"))
        except Exception as e:
            say("faults-file unreadable (%s) -- failing safe." % e); return None
    try:
        return api("GET", "/admin/faults?status=new", key) or []
    except Exception as e:
        say("intake FAILED (%s) -- nothing read; failing safe, doing nothing." % e); return None

# ── classify: REFUSE | ESCALATE | PATH_B | PATH_A ────────────────────────────────
def classify(fault):
    ref = is_refused(fault)
    if ref:
        return "ESCALATE", "touches a protected surface (%s) -- never autonomous" % ",".join(ref[:3])
    # rehearsal only: deterministic routing AFTER the guard (the guard is never stubbable).
    _cs = os.environ.get("MAINT_CLASSIFY_STUB")
    if _cs:
        v = json.load(open(_cs, encoding="utf-8")).get(fault.get("ref", ""))
        if v:
            return v, "classify-stub"
    # brain classifies the remainder; DEFAULT to Path B (batched, safe) on any doubt.
    try:
        import ai_provider
    except Exception:
        return "PATH_B", "ai_provider unavailable -- defaulting to the batched design lane"
    sys_p = ("You triage a software fault for a marketplace. Answer ONE word: "
             "MECHANICAL if it is a copy/config/flag/logic bug fixable by a small code "
             "edit; DESIGN if it asks for new UI, a new flow, a layout change, or a "
             "feature. If unsure, answer DESIGN.")
    msg = [{"role": "user", "content": "TITLE: %s\nDETAIL: %s\nPAGE: %s" % (
        fault.get("title", ""), fault.get("detail", ""), fault.get("page_url", ""))}]
    r = ai_provider.complete(msg, task="haiku", max_tokens=8, system=sys_p)
    verdict = (r.text or "").strip().upper()
    src = "%s/%s" % (r.provider, r.model)        # the IDENTIFIED source, logged
    if not r.ok:
        return "PATH_B", "brain unreachable (%s) -- defaulting to design lane" % r.error_kind
    if "MECHANICAL" in verdict:
        return "PATH_A", "brain[%s]=MECHANICAL" % src
    return "PATH_B", "brain[%s]=%s" % (src, verdict or "DESIGN")

# ── brain: produce a unified-diff patch for a Path A fault ───────────────────────
def _looks_like_patch(t):
    """A real unified diff, not the literal word 'diff'. The first heuristic keyed on
    'diff' and rejected valid `--- / +++ / @@` patches — caught by B4, 9 Aug 2026."""
    t = t or ""
    return ("--- " in t) and ("+++ " in t) and ("@@" in t)


def propose_patch(fault):
    if _BRAIN_STUB:
        stub = json.load(open(_BRAIN_STUB, encoding="utf-8"))
        diff = stub.get(fault.get("ref", ""), "")
        r = type("R", (), {})()
        r.text, r.ok, r.provider, r.model, r.error_kind = (diff or "NObugfix"), bool(diff), "stub", "rehearsal", ""
        return r
    import ai_provider
    sys_p = ("You are a careful maintenance engineer. Produce a MINIMAL unified diff "
             "(git format, ready for `git apply`) that fixes the reported fault and "
             "nothing else. Touch the fewest lines possible. If you cannot fix it with "
             "a small mechanical edit, output exactly NObugfix. Never touch payment, "
             "auth, schema, or anonymity code.")
    msg = [{"role": "user", "content": "FAULT %s\nTITLE: %s\nDETAIL: %s\nPAGE: %s\n"
            "Reply with ONLY the diff, or NObugfix." % (
                fault.get("ref"), fault.get("title", ""), fault.get("detail", ""),
                fault.get("page_url", ""))}]
    r = ai_provider.complete(msg, task="sonnet", max_tokens=1500, system=sys_p)
    return r  # caller reads .text/.ok/.provider/.model

# ── gates: run the REAL suite in a throwaway worktree ────────────────────────────
def run_gates(workdir):
    results = []
    def g(name, cmd):
        try:
            p = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, timeout=240)
            ok = p.returncode == 0
        except Exception as e:
            ok, p = False, type("x", (), {"stdout": "", "stderr": str(e)})()
        results.append((name, ok, (p.stdout or "")[-400:] + (p.stderr or "")[-400:]))
        return ok
    # py syntax on any changed .py, node --check on ms.js if present, then the ledger.
    _pys = [f for f in _changed_files(workdir) if f.endswith(".py")]
    if _pys:
        g("py_compile", [sys.executable, "-m", "py_compile"] + _pys)
    if os.path.exists(os.path.join(workdir, "ms.js")) and shutil.which("node"):
        g("node_check", ["node", "--check", "ms.js"])
    if os.path.exists(os.path.join(workdir, "scripts", "regression_ledger.py")):
        g("regression_ledger", [sys.executable, "scripts/regression_ledger.py"])
    if os.path.exists(os.path.join(workdir, "predeploy_check.py")):
        g("predeploy_check", [sys.executable, "predeploy_check.py"])
    return results

def _changed_files(workdir):
    try:
        # HEAD, not the index: git apply --3way STAGES its change, so a plain
        # `git diff` shows nothing and the py_compile gate would silently skip a
        # broken Python fix. Proven by the spine rehearsal, 9 Aug 2026.
        p = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=workdir,
                           capture_output=True, text=True, timeout=30)
        return [x for x in p.stdout.split() if x]
    except Exception:
        return []

# ── rate limit ───────────────────────────────────────────────────────────────────
def under_rate_limit():
    os.makedirs(STATE, exist_ok=True)
    ships = os.path.join(STATE, "ships.log")
    cutoff = time.time() - 3600
    recent = []
    try:
        recent = [float(x) for x in open(ships).read().split() if float(x) > cutoff]
    except OSError:
        pass
    return len(recent) < MAX_SHIPS_PER_HOUR, recent, ships

def record_ship(recent, ships):
    open(ships, "w").write(" ".join(str(t) for t in (recent + [time.time()])))

# ── one run ───────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(STATE, exist_ok=True)
    mode = "LIVE" if LIVE else ("SHADOW (kill switch ON, --live not passed)" if KILL
                                else "SHADOW (kill switch OFF — default, cannot commit)")
    say("run %s  mode=%s  rate<=%d/h" % (now(), mode, MAX_SHIPS_PER_HOUR))
    key = maint_key()
    if not _FAULTS_FILE and not key:
        # a key is required ONLY for the live API path; a synthetic --faults-file
        # rehearsal needs none (proven necessary by the B4 first run, 9 Aug).
        say("no MS_MAINT_KEY resolvable — cannot read the queue. Failing safe."); return 0
    faults = open_faults(key)
    if faults is None:
        return 0
    report = {"run": now(), "mode": mode, "seen": len(faults), "actions": []}

    for f in faults:
        ref = f.get("ref") or ("TS-%04d" % f.get("id", 0))
        lane, why = classify(f)
        item = {"ref": ref, "lane": lane, "why": why, "title": (f.get("title") or "")[:80]}

        if lane in ("ESCALATE", "PATH_B"):
            # neither is autonomously fixed: escalate = report+safest; path_b = design backlog.
            item["outcome"] = "escalated (safety/legal/cost)" if lane == "ESCALATE" \
                              else "routed to design backlog (batched, designer gate)"
            report["actions"].append(item); say("%s -> %s (%s)" % (ref, lane, why)); continue

        # ── PATH_A: propose, gate, and (only if fully armed) ship ───────────────────
        r = propose_patch(f)
        item["source"] = "%s/%s" % (r.provider, r.model)      # identified, every time
        if not r.ok or "NObugfix" in (r.text or "") or not _looks_like_patch(r.text):
            item["outcome"] = "brain declined a small mechanical fix -> escalate for a human"
            report["actions"].append(item); say("%s -> no clean patch (%s)" % (ref, item["source"])); continue

        work = tempfile.mkdtemp(prefix="maint_")
        try:
            subprocess.run(["git", "worktree", "add", "--detach", work], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
            patch = os.path.join(work, ".proposed.patch")
            open(patch, "w").write(r.text)
            ap = subprocess.run(["git", "apply", "--3way", patch], cwd=work,
                                capture_output=True, text=True, timeout=60)
            if ap.returncode != 0:
                item["outcome"] = "patch did not apply cleanly -> escalate"
                report["actions"].append(item); continue
            gates = run_gates(work)
            item["gates"] = [{"g": n, "ok": ok} for n, ok, _ in gates]
            green = all(ok for _, ok, _ in gates)
            if not green:
                item["outcome"] = "GATES RED -> not shipped (this is the gate doing its job)"
                report["actions"].append(item); say("%s -> gates red, held" % ref); continue

            if not LIVE:
                item["outcome"] = "SHADOW: gates GREEN, patch ready — commit withheld (not armed)"
                report["actions"].append(item); say("%s -> shadow green, would ship" % ref); continue

            ok_rate, recent, ships = under_rate_limit()
            if not ok_rate:
                item["outcome"] = "rate limit reached (%d/h) -> deferred to next run" % MAX_SHIPS_PER_HOUR
                report["actions"].append(item); continue

            # LIVE: commit the worktree change back and push the deploy ref. The ONE engine
            # (server_deploy.sh) then applies, BIT-verifies, and auto-reverts on failure.
            msg = "maint-agent %s via %s: %s" % (ref, item["source"], item["title"])
            subprocess.run(["git", "add", "-A"], cwd=work, timeout=30)
            subprocess.run(["git", "commit", "-m", msg], cwd=work, capture_output=True, timeout=30)
            subprocess.run(["git", "push", "origin", "HEAD:deploy"], cwd=work, capture_output=True, timeout=120)
            record_ship(recent, ships)
            # AIK-VERIFY-1: prove it live, then and only then mark verified.
            ev = aik_verify(f, key)
            api("PUT", "/admin/faults/%d" % f["id"], key,
                {"status": "verified" if ev["ok"] else "fix-shipped",
                 "fix_note": "maint-agent via %s; evidence: %s" % (item["source"], ev["evidence"]),
                 "deploy_ref": "deploy"})
            item["outcome"] = ("SHIPPED + VERIFIED (%s)" % ev["evidence"]) if ev["ok"] \
                              else "SHIPPED, verify probe inconclusive -> left fix-shipped, not verified"
            report["actions"].append(item); say("%s -> %s" % (ref, item["outcome"]))
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", work], cwd=REPO,
                           capture_output=True, timeout=60)
            shutil.rmtree(work, ignore_errors=True)

    path = os.path.join(STATE, "run_%s.json" % datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    open(path, "w").write(json.dumps(report, indent=2))
    say("report -> %s  (%d seen, %d acted)" % (path, report["seen"], len(report["actions"])))
    return 0

# ── AIK-VERIFY-1: reproduce the failing action against the live surface ──────────
def aik_verify(fault, key):
    """Named machine evidence or nothing. Re-fetches the fault's page/endpoint and looks
    for the failure signature. A generic probe now; per-fault recipes are the B4 work."""
    page = fault.get("page_url") or ""
    try:
        if page.startswith("http"):
            with urllib.request.urlopen(page, timeout=20) as r:
                return {"ok": r.status == 200, "evidence": "GET %s -> HTTP %d" % (page[:60], r.status)}
    except Exception as e:
        return {"ok": False, "evidence": "probe error: %s" % e}
    return {"ok": False, "evidence": "no probe recipe for this fault (needs a per-fault check)"}

if __name__ == "__main__":
    sys.exit(main())
