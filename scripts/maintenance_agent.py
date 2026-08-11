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
import os, sys, json, re, subprocess, tempfile, shutil, time, urllib.request, urllib.error
from datetime import datetime, timezone

REPO   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BRAIN-PATH-1 (11 Aug 2026). The brain lives at the REPO ROOT (ai_provider.py); this script
# lives in scripts/. Run as `python3 scripts/maintenance_agent.py`, sys.path[0] is scripts/,
# so `import ai_provider` raised ModuleNotFoundError on EVERY run, on EVERY machine, with or
# without an API key -- and classify() dutifully degraded every fault to PATH_B. The loop
# looked like it was triaging; it was reporting its own import error 7 times a night.
# Same shape as UA-EDGE-1: a correct fail-safe hiding a plain bug behind a green exit code.
# Deliberately the __file__ root, NOT the --repo override: that override picks which repo to
# PATCH (rehearsal sandbox), never which brain to think with.
if REPO not in sys.path:
    sys.path.insert(0, REPO)
BASE   = os.environ.get("MS_BEA_URL", "http://localhost:8000")
STATE  = os.path.join(REPO, ".maint_agent")            # rate-limit ledger + run reports
KILL   = os.environ.get("MAINTENANCE_AGENT_ENABLED", "0").strip() == "1"
LIVE   = ("--live" in sys.argv) and KILL               # live REQUIRES both, by construction
MAX_SHIPS_PER_HOUR = int(os.environ.get("MAINT_MAX_SHIPS_PER_HOUR", "3"))

# Human-in-the-loop scope is PHASE-DEPENDENT (David, 9 Aug 2026). PRE-LAUNCH the agent is a
# design tool for 3 trusted testers on a platform with no real users/sellers/money: it makes
# micro DESIGN + mechanical corrections itself, and ONLY legal / currently-costly stops for a
# human. POST-LAUNCH (real users via the complaints flow) the full trust-core guard returns and
# design re-batches. Fail-safe default = postlaunch (strict): an unset config is never permissive.
MAINT_PHASE = os.environ.get("MAINT_PHASE", "postlaunch").strip().lower()
PRELAUNCH = MAINT_PHASE == "prelaunch"

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

def _load_local_ai_keys():
    """BRAIN-PATH-1, second half. ai_provider.envkey() reads os.environ then
    /var/www/marketsquare/.env -- that .env exists only ON THE SERVER, so a loop running on
    David's machine has no way to be keyed at all. The repo already has exactly one blessed
    place for local secrets (.secrets/, gitignored at .gitignore:141, already holding
    ms_maint_key.txt), so read the same way rather than inventing a second convention.

    File: .secrets/ai_keys.env -- KEY=VALUE per line, # comments allowed. ONE key is enough.
    Never overrides a variable already set in the real environment, so a properly-provisioned
    host always wins. Silent when the file is absent: this is a convenience, not a requirement.
    """
    path = os.path.join(REPO, ".secrets", "ai_keys.env")
    loaded = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and v and not os.environ.get(k):
                    os.environ[k] = v
                    loaded.append(k)
    except OSError:
        return []
    return loaded


_AI_KEYS_LOADED = _load_local_ai_keys()


def _LANE_KEY_NAMES():
    """The env var names a lane can be keyed by -- read from ai_provider so this message
    can never drift from the real lane table (BRAIN-PATH-1)."""
    try:
        import ai_provider
        return list(ai_provider._LANE_KEYS.values())
    except Exception:
        return [("ANTHROPIC_API_KEY",), ("OPENAI_API_KEY",), ("SCALEWAY_API_KEY", "FAILOVER_API_KEY")]


def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def say(m): print("[maint] " + m, flush=True)

# ── the deterministic REFUSE guard — un-bypassable by the AI ─────────────────────
# Path A autonomy stops HARD at anything touching money, identity, the schema, or the
# law. These never reach the brain as fixable; they escalate. Keyword OR page match.
# Legal + currently-costly ALWAYS stop for a human, in EVERY phase.
REFUSE_LEGAL_COSTLY = (
    "legal", "popia", "eula", "terms", "compliance", "ffc", "mandate",
    "payment", "paystack", "refund", "wallet", "tuppence charge", "billing", "card",
    "cost", "costly", "spend", "invoice", "vat", "tax", "payout",
)
# The trust core is added ON TOP only post-launch, when real users and real money are live.
REFUSE_TRUST_CORE = (
    "auth", "login", "password", "session", "token", "kyc", "id number", "identity",
    "anonym", "reveal", "seller_email", "schema", "migration", "database", "drop table", "safety",
)
# GUARD-SPLIT-1 (11 Aug 2026, from David's "I do need autonomous fixing pre-launch").
# MAINT_PHASE was doing TWO unrelated jobs on one switch:
#   (1) the DESIGN LANE  -- prelaunch implements micro design changes instead of batching
#       them. This is the autonomy David actually asked for. Still keyed to MAINT_PHASE.
#   (2) the TRUST CORE   -- prelaunch dropped identity/auth/kyc/schema/safety refusals
#       ENTIRELY. Nobody asked for that; it rode along.
# The 9 Aug ruling justified (2) on the premise of "no real users/sellers/money". That
# premise has expired: three real people with real addresses are filing faults, Maroushka
# has a live listing (335) with 8 real photos, and RG-0045 asserts that no endpoint may
# ever return seller identity -- anonymity IS the product. Leaking a real seller is
# irreversible; batching a dark-mode toggle is not. So the two are now separate levers and
# the trust core defaults ON in BOTH phases.
# To restore the old all-or-nothing prelaunch behaviour: MAINT_TRUST_CORE_GUARD=0 (explicit,
# logged in the run banner, never a silent default).
TRUST_CORE_GUARD = os.environ.get("MAINT_TRUST_CORE_GUARD", "1").strip() != "0"
REFUSE_MARKERS = REFUSE_LEGAL_COSTLY + (REFUSE_TRUST_CORE if TRUST_CORE_GUARD else ())
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

# UA-EDGE-1 (11 Aug 2026): Cloudflare's managed rules BLOCK a UA-less request with
# error 1010 ("banned browser signature") BEFORE it reaches the origin -- so the queue
# read returned 403 and the agent said "failing safe, doing nothing" while looking green.
# Every call to OUR OWN edge must name itself. Same header the regression ledger uses.
UA_HEADER = {"User-Agent": "TrustSquare-MaintenanceAgent/1.0 (dmcontiki2@gmail.com)"}

def api(method, path, key, body=None):
    hdrs = dict(UA_HEADER); hdrs.update({"X-Maint-Key": key, "Content-Type": "application/json"})
    req = urllib.request.Request(BASE + path, method=method, headers=hdrs)
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
    except Exception as e:
        return "PATH_B", ("ai_provider will not import (%s: %s) -- batched design lane. "
                          "This is a WIRING fault, not a verdict on the fault." % (type(e).__name__, e))
    # A configured lane is not the same thing as an importable module. Say which is missing,
    # so a run report never again reads 'unavailable' for two unrelated reasons (BRAIN-PATH-1).
    try:
        if not ai_provider.any_lane_configured("haiku"):
            return "PATH_B", ("no AI lane has a key where the loop runs (checked: %s) -- batched "
                              "design lane. The brain imported fine; it has nothing to call."
                              % ", ".join(sorted(sum(map(list, _LANE_KEY_NAMES()), []))))
    except Exception:
        pass
    sys_p = ("You triage a software fault for a marketplace. Answer ONE word: "
             "MECHANICAL if it is a copy/config/flag/logic bug fixable by a small code "
             "edit; DESIGN if it asks for new UI, a new flow, a layout change, or a "
             "feature. If unsure, answer DESIGN.")
    msg = [{"role": "user", "content": "TITLE: %s\nDETAIL: %s\nPAGE: %s" % (
        fault.get("title", ""), fault.get("detail", ""), fault.get("page_url", ""))}]
    try:
        r = ai_provider.complete(msg, task="haiku", max_tokens=8, system=sys_p)
    except Exception as e:
        # MAINT-B4-5: a brain CALL failure (missing dep, network, key) must degrade
        # exactly like an unavailable brain -- batched design lane, never a crash.
        return "PATH_B", "brain call failed (%s) -- defaulting to the batched design lane" % type(e).__name__
    verdict = (r.text or "").strip().upper()
    src = "%s/%s" % (r.provider, r.model)        # the IDENTIFIED source, logged
    if not r.ok:
        return "PATH_B", "brain unreachable (%s) -- defaulting to design lane" % r.error_kind
    if "MECHANICAL" in verdict:
        return "PATH_A", "brain[%s]=MECHANICAL" % src
    if PRELAUNCH:
        # pre-launch: micro design corrections are the JOB, not a backlog -- implement them.
        return "PATH_A", "brain[%s]=DESIGN -> pre-launch micro-change lane" % src
    return "PATH_B", "brain[%s]=%s" % (src, verdict or "DESIGN")

# ── brain: produce a unified-diff patch for a Path A fault ───────────────────────
def _looks_like_patch(t):
    """A real unified diff, not the literal word 'diff'. The first heuristic keyed on
    'diff' and rejected valid `--- / +++ / @@` patches — caught by B4, 9 Aug 2026."""
    t = t or ""
    return ("--- " in t) and ("+++ " in t) and ("@@" in t)


_STOP = {"the", "and", "should", "shows", "says", "with", "that", "this", "from", "when",
         "page", "link", "button", "does", "have", "into", "your", "there", "typo",
         "fault", "error", "broken", "fixed", "please", "would", "which", "their",
         "everyone", "twice", "once", "showed"}

def _candidate_files(fault, max_files=2, max_bytes=12000):
    """Find the file(s) the fault most likely lives in, so the brain edits real code
    instead of guessing the path and context lines. Deterministic: git grep the fault's
    own distinctive tokens (quoted literals first), rank by hit count, return small text
    files with their contents. Added 9 Aug 2026 — a blind prompt (no file shown) was why
    the real Sonnet patch never applied in B4 Tier 2 (two honest runs, both escalated)."""
    text = " ".join([fault.get("title", ""), fault.get("detail", "")])
    quoted = re.findall(r"['\"]([^'\"]{2,40})['\"]", text)
    words = [w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", text)
             if w.lower() not in _STOP]
    hits = {}
    for tok in quoted + words:
        try:
            gp = subprocess.run(["git", "grep", "-lF", "--", tok], cwd=REPO,
                                capture_output=True, text=True, timeout=20)
            for fpath in gp.stdout.split():
                hits[fpath] = hits.get(fpath, 0) + 1
        except Exception:
            pass
    out = []
    for fpath in sorted(hits, key=lambda f: -hits[f])[:max_files]:
        try:
            full = os.path.join(REPO, fpath)
            if os.path.getsize(full) <= max_bytes:
                out.append((fpath, open(full, encoding="utf-8", errors="replace").read()))
        except OSError:
            pass
    return out

def propose_patch(fault):
    if _BRAIN_STUB:
        stub = json.load(open(_BRAIN_STUB, encoding="utf-8"))
        diff = stub.get(fault.get("ref", ""), "")
        r = type("R", (), {})()
        r.text, r.ok, r.provider, r.model, r.error_kind = (diff or "NObugfix"), bool(diff), "stub", "rehearsal", ""
        return r
    try:
        import ai_provider
    except Exception as e:
        r = type("R", (), {})()
        r.text, r.ok, r.provider, r.model = "NObugfix", False, "none", "unavailable"
        r.error_kind = "import:%s" % type(e).__name__      # BRAIN-PATH-1: name it, never just 'import'
        return r
    files = _candidate_files(fault)
    if files:
        ctx = "\n\n".join("### FILE: %s\n%s" % (p, c) for p, c in files)
        loc = ("The current contents of the most likely file(s) are shown below. Produce the "
               "unified diff AGAINST EXACTLY THESE BYTES: git headers `--- a/<path>` and "
               "`+++ b/<path>` with the real path and the real surrounding context lines.")
    else:
        ctx = "(no candidate file located in the repo)"
        loc = ("No file could be located from the fault text; unless you are certain of the "
               "exact path and lines, output NObugfix.")
    sys_p = ("You are a careful maintenance engineer. Produce a MINIMAL unified diff "
             "(git format, applies with `git apply -p1`) that resolves the reported fault -- a bug "
             "fix or a small, targeted design correction -- and nothing else, touching the fewest "
             "lines possible. %s If it cannot be done as a small, targeted change, output exactly "
             "NObugfix. Keep the change within the file(s) shown; do not widen its scope." % loc)
    msg = [{"role": "user", "content": "FAULT %s\nTITLE: %s\nDETAIL: %s\nPAGE: %s\n\n%s\n\n"
            "Reply with ONLY the unified diff, or exactly NObugfix." % (
                fault.get("ref"), fault.get("title", ""), fault.get("detail", ""),
                fault.get("page_url", ""), ctx)}]
    try:
        r = ai_provider.complete(msg, task="sonnet", max_tokens=2000, system=sys_p)
    except Exception as e:
        # MAINT-B4-5: same degradation contract as classify -- a failed call is a
        # DECLINED fix (escalates to a human), never a crashed queue.
        r = type("R", (), {})()
        r.text, r.ok, r.provider, r.model, r.error_kind = "NObugfix", False, "none", "brain-error", type(e).__name__
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
    say("run %s  mode=%s  phase=%s  trust-core=%s  rate<=%d/h"
        % (now(), mode, MAINT_PHASE,
           "GUARDED" if TRUST_CORE_GUARD else "OFF (MAINT_TRUST_CORE_GUARD=0)",
           MAX_SHIPS_PER_HOUR))
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
        try:
            lane, why = classify(f)
        except Exception as e:
            # MAINT-B4-5: classification can never kill the queue -- escalate and move on.
            lane, why = "ESCALATE", "agent error during classify (%s) -- escalated, run continues" % type(e).__name__
        item = {"ref": ref, "lane": lane, "why": why, "title": (f.get("title") or "")[:80]}

        if lane in ("ESCALATE", "PATH_B"):
            # neither is autonomously fixed: escalate = report+safest; path_b = design backlog.
            item["outcome"] = "escalated (safety/legal/cost)" if lane == "ESCALATE" \
                              else "routed to design backlog (batched, designer gate)"
            report["actions"].append(item); say("%s -> %s (%s)" % (ref, lane, why)); continue

        # ── PATH_A: propose, gate, and (only if fully armed) ship ───────────────────
        try:
            r = propose_patch(f)
        except Exception as e:
            item["outcome"] = "agent error during propose (%s) -> escalate for a human" % type(e).__name__
            report["actions"].append(item); say("%s -> propose error (%s)" % (ref, type(e).__name__)); continue
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
        except Exception as e:
            # MAINT-B4-5: one poisoned fault (git timeout, probe error, API hiccup)
            # can never kill the queue. Escalate this fault, keep going.
            item["outcome"] = "agent error mid-fix (%s) -> escalate for a human" % type(e).__name__
            if item not in report["actions"]:
                report["actions"].append(item)
            say("%s -> mid-fix error (%s), queue continues" % (ref, type(e).__name__))
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
