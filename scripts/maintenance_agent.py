#!/usr/bin/env python3
"""maintenance_agent.py — Path A autonomous fix-agent (MAINTENANCE_AGENT.md B2b).
================================================================================
David's ruling 29 Jul 2026: TOTAL AUTONOMY on Path A, mechanical gates only, no
human veto; his absence never stalls a fix. This is the orchestrator that makes
that real, bound to what already exists rather than reinventing it:

  intake   GET /admin/faults?status=new   (localhost + MS_MAINT_KEY, like fault_reconcile)
  brain    POST /admin/maint/brain (bea_main) -- the ONE cost chokepoint (MAINT-BRAIN-1,
                                               17 Sep 2026): price card, spend log, rank-by-
                                               price step-down. The IDENTIFIED lane+model
                                               is recorded on every fix. This agent holds
                                               NO AI key and picks NO model (David's ruling:
                                               never halt on cost, step down; SPEND-GUARD-1).
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
# The agent's OWN checkout, captured before any --repo override. STALE-CODE-1 asks
# "which agent code is running?", which is never the sandbox the rehearsal patches.
SELF_REPO = REPO
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
_ONLY = _arg("--only", "")                           # HOST-CAP-1: drive the queue one ref at a time
_BUDGET_S = float(os.environ.get("MAINT_TIME_BUDGET_S", "0") or 0)   # 0 = no budget (default)
_BRAIN_STUB  = os.environ.get("MAINT_BRAIN_STUB")    # canned patches for a keyless rehearsal
if _BRAIN_STUB:
    LIVE = False   # a stubbed brain can NEVER ship — rehearsal is shadow, always

# ── MAINT-BRAIN-1 (17 Sep 2026): the brain is the app's chokepoint, not this file ──
# DELETED here: _load_local_ai_keys (a private key file), _LANE_KEY_NAMES (a private
# key-presence chain), _fix_task (a hardcoded "reason"), _ensure_brain_deps (httpx for
# private vendor calls). The agent now holds ONE credential (MS_MAINT_KEY) and POSTs to
# /admin/maint/brain, where bea_main applies the price card, the daily budget and the
# rank-by-price STEP-DOWN (David: never halt on cost), logs spend to the serving lane,
# and bans anthropic structurally (SPEND-GUARD-1). Key PRESENCE is no longer a state:
# brain_probe() makes one 4-token live call per run and the PROVEN result is what the
# dashboard shows (D2) -- auth/billing failure reads RED, never a silent fallback.
BRAIN = {"ok": False, "state": "UNPROBED", "provider": "", "model": "", "error_kind": "",
         "status": None, "cost_usd": 0.0}
RUN_COST = {"usd": 0.0, "calls": 0, "by_lane": {}, "by_tier": {}, "stepped_down": 0, "over_budget": 0}
_RUN_ID = None      # set by main(); stamps every spend row as maint:<run>

class _BrainReply:
    """Duck-typed like the old AIResult so every caller reads .text/.ok/.provider/.model."""
    def __init__(self, d):
        d = d or {}
        self.text = d.get("text") or ""
        self.ok = bool(d.get("ok"))
        self.provider = d.get("provider") or "none"
        self.model = d.get("model") or "unavailable"
        self.error_kind = d.get("error_kind") or ""
        self.state = d.get("state") or ""
        self.tier_used = d.get("tier_used") or ""
        self.stepped_down = bool(d.get("stepped_down"))
        self.over_budget = bool(d.get("over_budget"))
        self.cost_usd = float(d.get("cost_usd") or 0.0)
        self.raw = d

def _account(r):
    RUN_COST["usd"] = round(RUN_COST["usd"] + r.cost_usd, 6)
    RUN_COST["calls"] += 1
    RUN_COST["by_lane"][r.provider] = round(RUN_COST["by_lane"].get(r.provider, 0.0) + r.cost_usd, 6)
    RUN_COST["by_tier"][r.tier_used or "?"] = RUN_COST["by_tier"].get(r.tier_used or "?", 0) + 1
    if r.stepped_down: RUN_COST["stepped_down"] += 1
    if r.over_budget: RUN_COST["over_budget"] += 1

# VANTAGE-BRAIN-1 (17 Sep 2026): MAINT-BRAIN-1 refuses /admin/maint/brain to any caller
# that is not a process ON the box -- 403 {"detail":"brain endpoint is local-only"}. That is a
# DELIBERATE, PERMANENT property of WHERE a run is standing. It is not a transport failure, not
# a billing failure, and not a state of the brain. Collapsing it into "AMBER:transport /
# brain-unreachable" broke the RG-0187 contract at the one instrument that gates the whole B2b
# lane: an instrument LIMIT must read NOT EVALUATED, never a FAIL and never a health colour
# (CLAUDE.md evidence ladder; RG-0133's three properties). Two harms it caused, both proven on
# the 17 Sep 05:37Z run: (a) the dashboard's B2b row painted AMBER every time the loop ran from
# a laptop, so a REAL brain outage was indistinguishable from a remote vantage; (b) classify()
# reported "brain unreachable", which reads as a defect report about the brain. The FAIL-SAFE
# routing to Path B is deliberately UNCHANGED -- an unconsultable brain still means the human
# lane -- only the NAME of the state changed, because the name is what a person acts on.
def _vantage_refusal(e):
    """Return a reason string when e is MAINT-BRAIN-1's local-only refusal, else ''."""
    try:
        if not isinstance(e, urllib.error.HTTPError) or e.code != 403:
            return ""
        body = (e.read() or b"").decode("utf-8", "replace")
    except Exception:
        return ""
    return "local-only" if "local-only" in body else ""

def _declined(e):
    """One shape for 'the brain did not answer', with the vantage case named apart."""
    if _vantage_refusal(e):
        return {"error_kind": "vantage:local-only", "state": "NOT_EVALUATED:remote",
                "provider": "none", "model": "not-consultable-from-here"}
    return {"error_kind": "transport:%s" % type(e).__name__, "state": "AMBER:transport",
            "provider": "none", "model": "brain-unreachable"}

def brain(purpose, messages, task="fast", max_tokens=700, system=None):
    """ONE brain call through the chokepoint. Never raises: a transport failure is a
    declined answer (ok=False, error_kind named), the RG-0049 degradation contract."""
    key = maint_key()
    if not key:
        return _BrainReply({"error_kind": "no-maint-key", "state": "KEYLESS", "provider": "none"})
    body = {"run": _RUN_ID or "adhoc", "purpose": purpose, "task": task, "messages": messages,
            "system": system, "max_tokens": max_tokens}
    try:
        r = _BrainReply(api("POST", "/admin/maint/brain", key, body, timeout=180))
    except Exception as e:
        r = _BrainReply(_declined(e))
    _account(r)
    if r.stepped_down:
        say("brain: %s stepped DOWN %s -> %s (%s) budget-left %s"
            % (purpose, task, r.tier_used, r.model, (r.raw.get("budget") or {}).get("left_usd")))
    return r

def brain_probe():
    """D2: prove the brain with one cheap live call. Sets BRAIN for the heartbeat."""
    key = maint_key()
    if not key:
        BRAIN.update({"ok": False, "state": "KEYLESS", "error_kind": "no-maint-key"}); return BRAIN
    try:
        d = api("POST", "/admin/maint/brain", key, {"run": _RUN_ID or "adhoc", "purpose": "probe",
                                                    "probe": True}, timeout=60)
    except Exception as e:
        d = dict(_declined(e)); d["ok"] = False
    r = _BrainReply(d); _account(r)
    BRAIN.update({"ok": r.ok, "state": r.state or ("GREEN" if r.ok else "RED:unknown"),
                  "provider": r.provider if r.ok else (r.provider if r.provider != "none" else ""),
                  "model": r.model if r.ok else "", "error_kind": r.error_kind,
                  "status": d.get("status"), "cost_usd": r.cost_usd,
                  "card_version": d.get("card_version", "")})
    return BRAIN


def _code_stamp():
    """Which commit is this run actually executing? (STALE-CODE-1)

    CODE-STAMP-2 (4 Sep 2026): the three git legs are now INDEPENDENT and the slow one
    gets a mount-sized timeout. Before this, all three shared one try block, so when
    `git status --porcelain` took 21 s on the /Projects FUSE mount (measured 4 Sep 2026;
    the leg's timeout was 20 s) the TimeoutExpired escaped past the SHA that had already
    been read cleanly in 0.1 s, and the whole stamp collapsed to "unknown (TimeoutExpired)"
    -- published as such on /dashboard/maint, which is the very surface STALE-CODE-1 exists
    to make truthful. A slow worktree scan must cost at most the dirty FLAG, never the
    commit identity. Dirtiness we could not measure now says DIRTY-UNKNOWN rather than
    silently reading as clean (no instrument defaults to a healthy value)."""
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")

    def _git(args, timeout):
        try:
            r = subprocess.run(["git"] + args, cwd=SELF_REPO, env=env,
                               capture_output=True, text=True, timeout=timeout)
            return r.stdout.strip() if r.returncode == 0 else None
        except Exception:
            return None

    sha = _git(["rev-parse", "--short", "HEAD"], 60)
    if not sha:
        return "unknown (not a git checkout)"
    subj = _git(["log", "-1", "--format=%s"], 60) or ""
    dirty = _git(["status", "--porcelain", "--untracked-files=no"], 300)
    flag = "  DIRTY-UNKNOWN" if dirty is None else ("  DIRTY-WORKTREE" if dirty else "")
    return "%s%s  %s" % (sha, flag, subj[:64])


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

# GATE-COOKIE-1 (13 Aug 2026): GATE-ENFORCE-2 armed auth_request on the nginx
# catch-all this morning (migration 016, David's ruling closing DW-023/RG-0029) and
# the exempt list -- 007 unchanged -- never carried the maint-key lane, so remote
# intake/heartbeat 401'd at the ORIGIN before the app ever saw X-Maint-Key (proven
# 13:17Z run: "intake FAILED (HTTP Error 401)"). The sanctioned adaptation is the
# ledger's, verbatim doctrine from GATE-ENFORCE-1: CARRY THE REVIEW CREDENTIAL,
# never punch a hole in the gate. Same code file, same login lane, same once-per-run
# cache as regression_ledger._review_cookie; on any failure the caller sees the
# original 401 and the existing fail-safe machinery does its job. RG-0064.
_REVIEW = {"cookie": None, "tried": False, "rate_limited": False}

# GATE-CACHE-1 (14 Aug 2026): /review/login allows 8 logins per 10 min and EVERY process
# minted its own -- ledger-before + this agent + each per-fault run -- so one session
# exhausted the allowance and the gated reads then 401'd for a reason that had nothing to
# do with the app. Same cache file, same doctrine as regression_ledger._cookie_from_cache:
# log in once per session, share the token on disk (.secrets/, gitignored, 0600).
_REVIEW_CACHE = os.path.join(REPO, ".secrets", "review_cookie.json")
_REVIEW_CACHE_TTL = 12 * 3600


def _cookie_from_cache():
    try:
        d = json.load(open(_REVIEW_CACHE, encoding="utf-8"))
        if d.get("base") == BASE and time.time() < float(d.get("exp", 0)):
            return (d.get("cookie") or "").strip()
    except Exception:
        pass
    return ""


def _cookie_to_cache(cookie, ttl=None):
    try:
        os.makedirs(os.path.dirname(_REVIEW_CACHE), exist_ok=True)
        fd = os.open(_REVIEW_CACHE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"base": BASE, "cookie": cookie,
                       "exp": time.time() + (_REVIEW_CACHE_TTL if ttl is None else ttl)}, fh)
    except Exception:
        pass


def _review_cookie():
    if _REVIEW["tried"]:
        return _REVIEW["cookie"] or ""
    _REVIEW["tried"] = True
    cached = _cookie_from_cache()                      # GATE-CACHE-1: one login per session
    if cached:
        _REVIEW["cookie"] = cached
        return cached
    code = (os.environ.get("MS_REVIEW_CODE") or "").strip()
    if not code:
        try:
            code = open(os.path.join(REPO, ".secrets", "review_code.txt"),
                        encoding="utf-8").read().strip()
        except OSError:
            code = ""
    if not code:
        return ""
    try:
        req = urllib.request.Request(BASE + "/review/login",
                                     data=json.dumps({"code": code}).encode(),
                                     headers=dict(UA_HEADER, **{"Content-Type": "application/json"}),
                                     method="POST")
        body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        tok = (json.loads(body).get("token") or "").strip()
        _REVIEW["cookie"] = ("ts_review=" + tok) if tok else None
        if _REVIEW["cookie"]:
            _cookie_to_cache(_REVIEW["cookie"])
            say("gate: review credential minted -- calls ride through the armed gate")
    except urllib.error.HTTPError as e:
        _REVIEW["cookie"] = None
        if e.code == 429:
            _REVIEW["rate_limited"] = True
            say("gate: /review/login RATE-LIMITED (429) -- credential unavailable, this run "
                "is blind at the gate, not evidence that anything is broken (GATE-CACHE-1)")
    except Exception:
        _REVIEW["cookie"] = None
    return _REVIEW["cookie"] or ""

def api(method, path, key, body=None, timeout=30):
    hdrs = dict(UA_HEADER); hdrs.update({"X-Maint-Key": key, "Content-Type": "application/json"})
    data = json.dumps(body).encode() if body is not None else None
    try:
        req = urllib.request.Request(BASE + path, method=method, headers=hdrs)
        with urllib.request.urlopen(req, data=data, timeout=timeout) as r:
            return json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        if e.code not in (401, 403):
            raise
        ck = _review_cookie()
        if not ck:
            raise
        hdrs2 = dict(hdrs); hdrs2["Cookie"] = ck
        req2 = urllib.request.Request(BASE + path, method=method, headers=hdrs2)
        try:
            with urllib.request.urlopen(req2, data=data, timeout=timeout) as r:
                return json.loads(r.read().decode() or "null")
        except Exception:
            raise e

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

# ── MAINT-INTAKE-2 (RG-0223, 31 Aug 2026): the loop reads EVERY LIVE intake lane ──
# The blindness this closes: this agent's only intake is GET /admin/faults?status=new,
# which is fed by the in-app REPORT tab -- and RUL-040 REMOVES that tab at soft launch,
# when customer complaints take over. Probed live 31 Aug: /flags says fault_report=false
# (correct, soft-public opened 29 Aug), so the app_faults lane is deliberately shut and
# every run since has truthfully reported "0 seen" while the lane that actually carries
# customer complaints -- inbound email -> POST /email/inbound -> email_triage -- was
# never looked at by the brain at all. A loop that reports an empty queue because it is
# reading a closed door is worse than one that reports nothing.
#
# Deliberately a CENSUS, not a fix lane: it reads counts and says them. It never drafts,
# never replies, never touches a customer message -- email replies stay behind
# EMAIL_AUTO_SEND and legal/compliance stay excluded. What it buys is that the run report
# and the console can no longer say "0 seen" without also saying what the customer lane
# holds. Counts-only by construction: DASH-TRIAGE-REDACT-1 (RG-0222) serves rows only to
# an admin credential. Since CENSUS-DOOR-1 / ADMIN-KEY-LOCAL-1 (25 Sep 2026) this census
# presents that credential for its ONE read (the route is admin-only everywhere now) and
# still throws the rows away unread -- the brain never sees a customer's message.
def _staff_key_for_census():
    """MS_ADMIN_KEY for the counts-only census read, or '' when this machine holds none.

    David's machine: .secrets/deploy_keys.txt. ON THE BOX (ADMIN-KEY-LOCAL-1, 25 Sep 2026 inspection, qa-02): the
    key the RUNNING app holds -- its /proc/<MainPID>/environ (this unit runs as root), then the service secrets
    file and the app .env. The loopback exemption this read used to lean on is gone, so on the box it must carry
    the key like every other caller. Used for this one GET only; the value is never printed or stored."""
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               ".secrets", "deploy_keys.txt"), encoding="utf-8") as f:
            for ln in f:
                if ln.startswith("MS_ADMIN_KEY="):
                    return ln.split("=", 1)[1].strip()
    except Exception:
        pass
    v = os.environ.get("MS_ADMIN_KEY", "").strip()
    if v:
        return v
    try:
        pid = subprocess.run(["systemctl", "show", "-p", "MainPID", "--value", "marketsquare"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        if pid.isdigit() and pid != "0":
            with open("/proc/%s/environ" % pid, "rb") as fh:
                for kv in fh.read().split(b"\0"):
                    if kv.startswith(b"MS_ADMIN_KEY="):
                        v = kv.split(b"=", 1)[1].decode("utf-8", "replace").strip()
                        if v:
                            return v
    except Exception:
        pass
    for path in ("/etc/marketsquare/secrets.env", "/var/www/marketsquare/.env"):
        try:
            for ln in open(path, encoding="utf-8"):
                ln = ln.strip()
                if ln.startswith("export "):
                    ln = ln[7:].strip()
                if ln.startswith("MS_ADMIN_KEY="):
                    v = ln.split("=", 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
        except OSError:
            pass
    return ""


def email_lane_census():
    """Counts from the live customer-email lane. Fail-SOFT: never affects the run.

    CENSUS-DOOR-1 (maintenance loop, 25 Sep 2026): SEC-GATE-1 (24 Sep) made
    GET /dashboard/email-triage admin-only (loopback automation on the box still admitted),
    so the anonymous counts read this census was built on returned 401 and RG-0223 went red.
    Same class as GATE-SYNC-1 (RG-0457), and the same decision: a reader of a route the gate
    closed moves to the staff door. ADMIN-KEY-LOCAL-1 (25 Sep 2026 inspection, qa-02): the box
    no longer admits a key-less loopback read either, so the census goes straight to the staff
    door whenever this machine holds the key (David's machine: deploy_keys.txt; the box: the
    running app's own key) and reads anonymously only when it holds none. COUNTS ONLY is kept
    by construction: whatever the door, 'items' is never copied into the report -- the agent
    still never reads, drafts or quotes a customer message.
    """
    try:
        def _read(hdrs):
            req = urllib.request.Request(BASE + "/dashboard/email-triage?limit=1", headers=hdrs)
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode() or "{}")
        _k = _staff_key_for_census()
        door = "staff" if _k else "anonymous"
        d = _read(dict(UA_HEADER, **({"X-Admin-Key": _k} if _k else {})))
        d.pop("items", None)          # counts only, whatever the door
        st = d.get("by_status_30d") or {}
        held = int(st.get("drafted", 0)) + int(st.get("failed", 0))
        return {"lane": "email_triage", "total": d.get("total", 0),
                "by_category_30d": d.get("by_category_30d") or {},
                "by_status_30d": st, "held_30d": held,
                "door": door,
                "note": "counts only (RG-0222); rows are never copied into the report"}
    except Exception as e:
        return {"lane": "email_triage", "error": "%s: %s" % (type(e).__name__, str(e)[:80]),
                "note": "customer email lane UNREAD this run -- treat 'seen' as partial"}


# RUL-013 / SPEND-GUARD-1 history: the fix tier used to be chosen HERE (_fix_task() returned a
# hardcoded "reason"). Deleted 17 Sep 2026 (MAINT-BRAIN-1): the agent REQUESTS a tier; the
# chokepoint decides the rung from the price card and the day's budget. Fable never runs here.
FIX_TIER = "reason"       # requested; the chokepoint may step DOWN, never up

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN-ROUTE-1 (26 Sep 2026) -- PATH_B actually files a dossier.
#
# WHAT WAS BROKEN, and it was a proxy assertion, not a gap: classify() returned
# PATH_B and the loop wrote the sentence "routed to design backlog (batched,
# designer gate)" into its report. Nothing wrote a dossier. Nothing in scripts/
# touched DESIGN_BACKLOG.md at all. MEASURED 26 Sep 2026: TS-0027 and TS-0006 were
# both closed on 11 Aug with "routed to the design backlog" in their fix_note, and
# DESIGN_BACKLOG.md holds exactly ONE dossier -- DCB-001, which is neither of them.
# Two faults said routed; zero arrived. The register said done and the lane was empty,
# which is the same class as the orphaned-commit fault the push guard above exists for.
#
# AND IT IS WHY OPEN_LOOPS L8 READ ZERO FOR 26 DAYS. RUL-013 sent design work to the
# 'design' task tier from 1 Sep 2026; four consecutive stand-ups re-probed
# `grep task="design"` -> 0 callers and called the tier unwired. The tier was wired
# at the chokepoint the whole time. It had no caller because no design work ever
# reached a backlog, because the routing was a string. The count was the symptom.
#
# WHAT THIS DOES, and deliberately no more: it writes the dossier in the exact
# template DESIGN_CHANGE_GUIDELINES.md publishes, with the PROPOSED DIRECTION asked
# of the design tier (task="design" -- RUL-013's allocated lane, its first real
# caller), and it leaves the GATE LINE EMPTY. The guidelines are explicit that an
# absent gate means NOT APPROVED, DO NOT BUILD, and open item (2) -- binding the
# designer role -- is still David's. So this files evidence for a decision; it never
# makes one, never scores itself a pass, and never ships anything user-visible.
#
# The brain is local-only from a sandbox vantage (VANTAGE-BRAIN-1). When it cannot be
# reached, the dossier is filed with PROPOSED DIRECTION left blank and the reason
# NAMED in the line -- never a guess, and never a silent omission. A dossier with no
# direction is still a dossier; a dossier that invents one is worse than none.
# ══════════════════════════════════════════════════════════════════════════════
DESIGN_BACKLOG = os.path.join(REPO, "DESIGN_BACKLOG.md")


def _next_dcb_id():
    """The next DCB-nnn, read from the file itself so two runs cannot collide on a number."""
    try:
        body = open(DESIGN_BACKLOG, encoding="utf-8").read()
    except Exception:
        return "DCB-001", ""
    nums = [int(m) for m in re.findall(r"DCB-(\d{3})", body)]
    return "DCB-%03d" % ((max(nums) + 1) if nums else 1), body


def design_direction(fault):
    """Ask the DESIGN tier for a solution-free direction sketch. RUL-013's lane.

    Returns (text, source, why_blank). A failure is reported, never papered over:
    an unreachable brain yields ('', source, reason) and the dossier says so.
    """
    sys_p = ("You are the design lane for a marketplace. Given a user's complaint, sketch ONE "
             "possible DIRECTION in at most three sentences. Reuse existing patterns. Do NOT "
             "write code, do NOT name files, do NOT claim the change is approved. If the "
             "complaint does not describe a design problem, answer exactly: NO DIRECTION.")
    msg = [{"role": "user", "content": "TITLE: %s\nDETAIL: %s\nPAGE: %s" % (
        fault.get("title", ""), fault.get("detail", ""), fault.get("page_url", ""))}]
    r = brain("design", msg, task="design", max_tokens=400, system=sys_p)
    src = "%s/%s" % (r.provider, r.model)
    if not r.ok:
        return "", src, "design tier not reached (%s)" % (r.error_kind or "unknown")
    txt = (r.text or "").strip()
    if not txt or txt.upper().startswith("NO DIRECTION"):
        return "", src, "design tier returned NO DIRECTION"
    return txt, src, ""


def file_design_dossier(fault, why_classified):
    """Append a dossier for this fault to DESIGN_BACKLOG.md. Returns (dcb_id, note).

    (None, reason) when nothing was written -- and the caller must report that reason
    verbatim rather than the old sentence, which asserted a routing that never happened.
    """
    ref = fault.get("ref") or ("id-%s" % fault.get("id"))
    dcb, body = _next_dcb_id()
    if body and ("FEEDER: Maintenance (%s)" % ref) in body:
        return None, "dossier for %s already filed -- not duplicated" % ref
    direction, src, why_blank = design_direction(fault)
    title = (fault.get("title") or "untitled").strip().replace("\n", " ")[:80]
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40] or "design-change"
    block = [
        "",
        "---",
        "",
        "## %s -- %s" % (dcb, title),
        "",
        "    DOSSIER: %s        DATE: %s   FEEDER: Maintenance (%s)" % (slug, time.strftime("%Y-%m-%d"), ref),
        "    PROBLEM: %s" % ((fault.get("detail") or title).strip().replace("\n", " ")[:400]),
        "    EVIDENCE: %s (one report). Criterion 1 needs >=2 independent reports, recurrence",
        "             >=3, or a measured number -- so this dossier is NOT yet scorable on",
        "             evidence alone. Filed so the second report has something to join.",
        "    PROPOSED DIRECTION (rides separately): %s" % (direction.replace("\n", " ") if direction
                                                          else "NONE -- %s" % why_blank),
        "    DIRECTION SOURCE: %s (task=design, RUL-013)" % src,
        "    SCOPE: not yet named -- criterion 3 is unmet until a session names files/screens.",
        "    REVERT: not yet named -- criterion 5 is unmet.",
        "    MEASUREMENT: retest by %s." % ref,
        "    SCORE: not scored. Filed by the maintenance loop; scoring is a session's act.",
        "    GATE:   -- EMPTY. Absent gate = NOT APPROVED, DO NOT BUILD",
        "            (DESIGN_CHANGE_GUIDELINES.md criterion 10; binding the designer role",
        "             is open item 2 and is David's).",
        "    ROUTED BECAUSE: %s" % (why_classified or "").replace("\n", " ")[:200],
        "",
    ]
    try:
        with open(DESIGN_BACKLOG, "a", encoding="utf-8") as fh:
            fh.write("\n".join(block))
    except Exception as e:
        return None, "could not write DESIGN_BACKLOG.md (%s) -- NOT routed" % str(e)[:80]
    return dcb, ("filed %s in DESIGN_BACKLOG.md, GATE empty (not approved)" % dcb)


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
    if not BRAIN.get("ok"):
        _st = BRAIN.get("state", "UNPROBED")
        _why = ("NOT MEASURED from this vantage (the brain endpoint is local-only)"
                if str(_st).startswith("NOT_EVALUATED")
                else "a WIRING/BILLING state")
        return "PATH_B", ("brain %s -- batched design lane. This is %s, not a verdict on the "
                          "fault." % (_st, _why))
    sys_p = ("You triage a software fault for a marketplace. Answer ONE word: "
             "MECHANICAL if it is a copy/config/flag/logic bug fixable by a small code "
             "edit; DESIGN if it asks for new UI, a new flow, a layout change, or a "
             "feature. If unsure, answer DESIGN.")
    msg = [{"role": "user", "content": "TITLE: %s\nDETAIL: %s\nPAGE: %s" % (
        fault.get("title", ""), fault.get("detail", ""), fault.get("page_url", ""))}]
    r = brain("classify", msg, task="fast", max_tokens=8, system=sys_p)
    verdict = (r.text or "").strip().upper()
    src = "%s/%s" % (r.provider, r.model)        # the IDENTIFIED source, logged
    if not r.ok:
        if (r.error_kind or "").startswith("vantage:"):
            return "PATH_B", ("brain NOT CONSULTABLE from this vantage (MAINT-BRAIN-1: the endpoint "
                              "is local-only) -- design lane by FAIL-SAFE. A property of where this "
                              "run stood, not a fault in the brain and not a verdict on the fault.")
        return "PATH_B", "brain unreachable (%s) -- defaulting to design lane" % r.error_kind
    if "MECHANICAL" in verdict:
        return "PATH_A", "brain[%s]=MECHANICAL" % src
    if PRELAUNCH:
        # pre-launch: micro design corrections are the JOB, not a backlog -- implement them.
        # RUL-013: in this phase a tester report IS a design REQUEST, resolved not batched.
        return "PATH_A", "brain[%s]=DESIGN -> pre-launch design REQUEST (RUL-013), implemented" % src
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
    own distinctive tokens (quoted literals first), rank by hit count, return the relevant
    source with its contents. Added 9 Aug 2026 -- a blind prompt (no file shown) was why
    the real Sonnet patch never applied in B4 Tier 2.

    CAND-FIX-1 (11 Aug 2026, after the FIRST armed live run returned 0/2 "no clean patch"):
    the 9 Aug version could never fire on this repo, for two compounding reasons.
      1. It dropped any file over 12,000 bytes. EVERY file the app lives in is over it --
         ms.js 1,074,965 · bea_main.py 906,981 · marketsquare.html 405,115 ·
         dashboard.server.html 449,274 · ms.css 129,178. So the "show the brain the file"
         fix could never apply to any real application file. Large files are now WINDOWED
         (a real excerpt around the densest token cluster) instead of discarded.
      2. It ranked by raw grep hits across the WHOLE repo, including the agent's own
         output. TS-0024's top two "candidate files" were .maint_agent/run_*.json -- the
         agent's own run reports, which contain the fault's title verbatim. The brain was
         handed two copies of its own exhaust and asked to patch it. Ledgers, changelogs,
         status files, backups and previews are now excluded before ranking.
    """
    text = " ".join([fault.get("title", ""), fault.get("detail", "")])
    quoted = re.findall(r"['\"]([^'\"]{2,40})['\"]", text)
    words = [w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", text)
             if w.lower() not in _STOP]
    toks = quoted + words
    hits = {}
    for tok in toks:
        try:
            gp = subprocess.run(["git", "grep", "-lF", "--", tok], cwd=REPO,
                                capture_output=True, text=True, timeout=20)
            for fpath in gp.stdout.split():
                if _is_noise(fpath):
                    continue          # never rank our own paperwork or the agent's exhaust
                hits[fpath] = hits.get(fpath, 0) + 1
        except Exception:
            pass
    out = []
    for fpath in sorted(hits, key=lambda f: (-hits[f], f)):
        if len(out) >= max_files:
            break
        full = os.path.join(REPO, fpath)
        try:
            size = os.path.getsize(full)
            body = open(full, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if size <= max_bytes:
            out.append((fpath, body))
            continue
        w = _window(fpath, body, toks)     # too big to send whole -- send the real excerpt
        if w:
            out.append(w)
    return out


def _is_noise(p):
    """Paths that can never be the SOURCE of a fault, only a record of one. Ranking these
    is how the agent ended up reading its own run reports back to itself (CAND-FIX-1)."""
    if any(seg in p for seg in (".maint_agent/", "changelog.d/", "status.d/", "Records/",
                                "AUDIT_GLOBAL_QA/", "DAILY_WATCH/", "_to_delete/", "logs/",
                                "node_modules/", ".git/")):
        return True
    if os.path.basename(p) in ("CHANGELOG.md", "STATUS.md", "CHANGE_REGISTER.md",
                               "OPEN_LOOPS.md", "FAULT_REGISTER.md", "APP_PREVIEW.html"):
        return True
    # PROBE-EXHAUST-1 (13 Aug 2026, real-repo probe run 8): the test harnesses QUOTE
    # faults verbatim by design (seed dicts, storm fixtures), so ranking them hands the
    # brain the fault's own DEFINITION as the thing to patch -- the rewrite lane showed
    # sonnet the probe's seed entry, where the misspelling is CORRECT, and sonnet rightly
    # changed nothing. Same class as ranking run reports (CAND-FIX-1), new costume.
    if os.path.basename(p) in ("maint_realrepo_probe.py", "maint_b4_rehearsal.py"):
        return True
    return ".bak" in p or p.endswith((".log", ".lock", ".new"))


def _window(fpath, body, toks, radius=70, hard_cap=16000):
    """Return (label, excerpt) around the densest cluster of token hits, with the real line
    range named. The bytes are exact, so a diff written against them applies -- and the
    agent applies with `git apply --3way`, which resolves the surrounding blob anyway."""
    lines = body.split("\n")
    low = [t.lower() for t in toks[:14] if len(t) >= 4]
    # WINDOW-AIM-1 (13 Aug 2026, real-repo probe run 5): the old aim marked every line
    # containing ANY token and took the densest cluster -- so generic tokens ("admin",
    # "message", "required") outgunned the one DISTINCTIVE token and the brain was shown
    # lines 1158-1298 while the seeded defect sat at line 122. Sonnet's NObugfix was
    # correct; the aim was wrong. Now: tokens that are RARE in this file (<= 8 hit
    # lines) steer the window; common tokens only pad the cluster. No rare token ->
    # old behavior unchanged.
    per_tok = {}
    for t in set(low):
        hits_t = [i for i, ln in enumerate(lines, 1) if t in ln.lower()]
        if hits_t:
            per_tok[t] = hits_t
    if not per_tok:
        return None
    rare2 = sorted({i for t, ls in per_tok.items() if len(ls) <= 2 for i in ls})
    rare8 = sorted({i for t, ls in per_tok.items() if len(ls) <= 8 for i in ls})
    marks = sorted({i for ls in per_tok.values() for i in ls})
    aim = rare2 or rare8 or marks  # rarest evidence steers; ties broken by density below
    best = max(aim, key=lambda L: sum(1 for m in aim if abs(m - L) <= radius))
    lo, hi = max(1, best - radius), min(len(lines), best + radius)
    excerpt = "\n".join(lines[lo - 1:hi])
    if len(excerpt) > hard_cap:
        excerpt = excerpt[:hard_cap]
    label = ("%s  [EXCERPT lines %d-%d of %d -- the rest of the file is unchanged and NOT "
             "shown; write the diff against these exact bytes]" % (fpath, lo, hi, len(lines)))
    return (label, excerpt)

def _strip_fences(text):
    """PATCH-FENCE-1 (13 Aug 2026): sonnet wraps diffs in ```diff fences; written
    verbatim to .proposed.patch they are 'corrupt patch at line N' -- N being the
    CLOSING fence -- and the whole MAINT-B4-6 'diffs slip' class falls out of exactly
    this. Strip leading/trailing fences only; never touch the body."""
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.strip("`\n")
        t = t.split("\n", 1)[1] if "\n" in t else t
    return t

def propose_patch(fault):
    if _BRAIN_STUB:
        stub = json.load(open(_BRAIN_STUB, encoding="utf-8"))
        diff = stub.get(fault.get("ref", ""), "")
        r = type("R", (), {})()
        r.text, r.ok, r.provider, r.model, r.error_kind = (diff or "NObugfix"), bool(diff), "stub", "rehearsal", ""
        return r
    if not BRAIN.get("ok"):
        return _BrainReply({"text": "NObugfix", "provider": "none", "model": "unavailable",
                            "error_kind": BRAIN.get("state", "UNPROBED")})
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
    # MAINT-B4-5 contract kept: brain() never raises -- a failed call is a DECLINED fix.
    r = brain("patch", msg, task=FIX_TIER, max_tokens=2000, system=sys_p)
    if not r.ok and not r.text:
        r.text = "NObugfix"
    return r  # caller reads .text/.ok/.provider/.model


# ── MAINT-B4-6: whole-file rewrite fallback (11 Aug 2026) ────────────────────────
# Tier 2 on the server proved the deferred risk real: real-brain unified diffs still
# slip against exact bytes ("patch did not apply cleanly", run 07:10Z). Fallback:
# when a diff fails to APPLY (and only then), re-ask the brain for the COMPLETE
# corrected file and diff it mechanically ourselves. Single file, size-capped,
# stub-safe (rehearsal stubs never reach it), and the full gate suite still judges
# the result — this changes how a fix is EXPRESSED, never what may ship.
def propose_rewrite(fault):
    if _BRAIN_STUB:
        return None, "stub mode: rewrite fallback not exercised"
    files = _candidate_files(fault, max_files=1)
    if not files:
        return None, "no single candidate file to rewrite"
    path, content = files[0]
    # WINDOW-SPLICE-1 (13 Aug 2026, real-repo probe runs 7-8): for WINDOWED large files
    # the old prompt was impossible -- it demanded "the COMPLETE file, start to finish"
    # while the excerpt label said "the rest is NOT shown", and sonnet safely returned
    # the block unchanged ("rewrite identical to original"). Worse, rw["path"] was the
    # LABEL string, so an "applied" rewrite would have written an excerpt to a
    # garbage-named file. Now: parse the label, ask for the corrected BLOCK, and the
    # applier splices it by line range under a bytes-must-match guard.
    span = None
    m = re.match(r"^(.*?)\s+\[EXCERPT lines (\d+)-(\d+) of (\d+)", path)
    if m:
        path, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        span = (lo, hi)
        sys_p = ("You are a careful maintenance engineer. Your earlier unified diff did not "
                 "apply. The block below is lines %d-%d of %s. Return the corrected text of "
                 "EXACTLY this block -- the same lines, start to finish, with ONLY the "
                 "minimal change needed to resolve the fault. No commentary, no fences, no "
                 "diff markers: block text only." % (lo, hi, path))
    else:
        sys_p = ("You are a careful maintenance engineer. Your earlier unified diff did not "
                 "apply. Return the COMPLETE corrected contents of the single file shown -- "
                 "the whole file, start to finish, with ONLY the minimal change needed to "
                 "resolve the fault. No commentary, no fences, no diff markers: file text only.")
    msg = [{"role": "user", "content": "FAULT %s\nTITLE: %s\nDETAIL: %s\n\n### FILE: %s\n%s" % (
        fault.get("ref"), fault.get("title", ""), fault.get("detail", ""), path, content)}]
    r = brain("rewrite", msg, task=FIX_TIER, max_tokens=4000, system=sys_p)
    if not r.ok and not r.text:
        return None, "rewrite brain call failed (%s)" % (r.error_kind or "unknown")
    text = (r.text or "").strip()
    if not r.ok or not text or "NObugfix" in text:
        return None, "brain declined a rewrite"
    if text.startswith("```"):
        text = text.strip("`\n")
        text = text.split("\n", 1)[1] if "\n" in text else text
    if len(text) > 3 * len(content) + 2000 or len(text) < len(content) // 3:
        return None, "rewrite size wildly off (%d vs %d) -- refused" % (len(text), len(content))
    if text == content.strip():
        return None, "rewrite identical to original -- no change proposed"
    return {"path": path, "span": span, "orig_block": content,
            "text": text + ("\n" if not text.endswith("\n") else ""),
            "source": "%s/%s" % (r.provider, r.model)}, "ok"


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
def _post_heartbeat(report, mode, key):
    """MAINT-DASH-1 (12 Aug 2026): after every completed REAL run, tell the dashboard
    the truth about the loop -- brain keyed or not, armed or not, what was seen and done.
    Facts only (lane NAMES, never a key value). Fail-SOFT in the RG-0049 spirit: a dead
    dashboard can never hurt the run it is reporting on. Rehearsals (--faults-file) do
    NOT post -- a synthetic storm must never stamp the production card as a real run."""
    if _FAULTS_FILE:
        say("heartbeat skipped (rehearsal run -- synthetic faults never stamp the dashboard)")
        return
    if not key:
        return
    lanes = {}
    for a in report.get("actions", []):
        lanes[a.get("lane", "?")] = lanes.get(a.get("lane", "?"), 0) + 1
    # D2/D3 (17 Sep 2026): brain_keyed is the PROVEN probe result, not key presence; armed
    # and live are EFFECTIVE cover (switch AND brain), the raw switch is armed_switch.
    proven = bool(BRAIN.get("ok"))
    # MAINT-VANTAGE-2 (18 Sep 2026) -- RG-0382's contract, applied to the fields beside the one it
    # fixed. KILL and LIVE are read from the env of WHOEVER POSTS. On the box that is the server's
    # MAINTENANCE_AGENT_ENABLED, i.e. the real arming state. From a host run (maint_host.bat, which
    # deliberately never sets it) or any other off-box vantage, they are locally-false values that
    # say nothing about whether the agent is armed -- and posting them overwrote the server's state
    # with a reading the runner could not observe. PROVEN 18 Sep: the card read armed:true
    # mode:LIVE at 02:20Z, then armed:false after a host SHADOW run at 02:35Z. NOTHING WAS
    # DISARMED. A reader -- David, a stand-up, the next session -- would have concluded the
    # maintenance lane was off while it was armed and running, or re-armed what was never off.
    # A LIMIT MUST STAY DISTINGUISHABLE FROM A FAULT: off-box, these post as None (NOT MEASURED),
    # never as False. The vantage signal is the brain probe's own refusal kind, which MAINT-BRAIN-1
    # returns precisely because the endpoint is local-only -- so "can I reach the local-only
    # endpoint" is exactly "am I on the box", and no second mechanism is invented to ask it.
    _offbox = str(BRAIN.get("error_kind") or "").startswith("vantage:")
    # The server's heartbeat whitelist (_MAINT_HB_FIELDS in bea_main.py) is a fixed tuple, so a new
    # key would be silently dropped -- and bea_main.py was held by another lane when this shipped
    # (SO-5). The vantage therefore rides `mode`, which IS whitelisted and is already free text, so
    # the card tells the truth today without waiting on a second file. arming_vantage is sent too
    # and costs nothing: it starts working the moment that tuple gains the key.
    if _offbox:
        mode = "%s  [arming NOT MEASURED -- off-box vantage]" % mode
    hb = {"run": report.get("run"), "mode": mode, "phase": MAINT_PHASE,
          "armed": None if _offbox else (KILL and proven),
          "live": None if _offbox else (LIVE and proven),
          "armed_switch": None if _offbox else KILL,
          "arming_vantage": "off-box (NOT MEASURED)" if _offbox else "on-box",
          "brain_keyed": proven,
          "brain_lane": BRAIN.get("provider") or "",
          "brain_state": BRAIN.get("state", "UNPROBED"),
          "brain_model": BRAIN.get("model") or "",
          "brain_probe": {"ok": proven, "status": BRAIN.get("status"),
                          "error_kind": BRAIN.get("error_kind") or "",
                          "card_version": BRAIN.get("card_version") or ""},
          "cost": dict(RUN_COST),
          "seen": report.get("seen", 0), "acted": len(report.get("actions", [])),
          "lanes": lanes, "code": _code_stamp(),
          # MAINT-INTAKE-2: the card must never paint an empty app_faults queue as a quiet
          # day when the customer lane is the one carrying mail. Whitelisted server-side
          # (_MAINT_HB_FIELDS), so this reaches the dashboard once the change deploys.
          "email_lane": (report.get("intake") or {}).get("email_lane") or {}}
    try:
        api("POST", "/dashboard/maint", key, hb)
        say("heartbeat -> /dashboard/maint (brain %s%s, %s, run cost $%.4f over %d call(s))"
            % (hb["brain_state"], ("/" + hb["brain_lane"]) if proven else "",
               ("arming NOT MEASURED (off-box vantage)" if _offbox else
                ("ARMED" if hb["armed"] else ("ARMED-SWITCH but NO BRAIN" if KILL else "shadow"))),
               RUN_COST["usd"], RUN_COST["calls"]))
    except Exception as e:
        say("heartbeat POST failed (%s) -- run unaffected, dashboard will show stale" % e)


def main():
    os.makedirs(STATE, exist_ok=True)
    mode = "LIVE" if LIVE else ("SHADOW (kill switch ON, --live not passed)" if KILL
                                else "SHADOW (kill switch OFF — default, cannot commit)")
    if "--shadow" in sys.argv:
        mode = "SHADOW (--shadow: one rehearsal cycle on the real queue, commit withheld)"
    say("run %s  mode=%s  phase=%s  trust-core=%s  rate<=%d/h"
        % (now(), mode, MAINT_PHASE,
           "GUARDED" if TRUST_CORE_GUARD else "OFF (MAINT_TRUST_CORE_GUARD=0)",
           MAX_SHIPS_PER_HOUR))
    # STALE-CODE-1 (11 Aug 2026). Twice in one day a run was read as a real test when the
    # box was actually on an older commit -- once for BRAIN-PATH-1, once for CAND-FIX-1 --
    # because `git pull` says "Already up to date" whether or not the fix was ever pushed.
    # Both times the only tell was a stale wording in the output, spotted by eye. The run
    # now states the code it IS: an unexpected SHA or a dirty tree is visible immediately,
    # before anyone reasons about the result.
    say("code    %s" % _code_stamp())
    key = maint_key()
    global _RUN_ID
    _RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if key and not _BRAIN_STUB:
        b = brain_probe()
        # TIER-NAME-1: lane + tier are the labels; the model that served is a register fact.
        say("brain   %s%s (probe $%.5f, card %s)" % (
            b["state"], ("  " + b["provider"] + " · fast tier, served by " + b["model"]) if b["ok"] else
            ("  " + (b.get("error_kind") or "")), b.get("cost_usd", 0.0), b.get("card_version", "?")))
    elif _BRAIN_STUB:
        BRAIN.update({"ok": True, "state": "STUB", "provider": "stub", "model": "rehearsal"})
    if not _FAULTS_FILE and not key:
        # a key is required ONLY for the live API path; a synthetic --faults-file
        # rehearsal needs none (proven necessary by the B4 first run, 9 Aug).
        say("no MS_MAINT_KEY resolvable — cannot read the queue. Failing safe."); return 0
    faults = open_faults(key)
    if faults is None:
        return 0
    # HOST-CAP-1 (14 Aug 2026). BRAIN-DEPS-2 fixed the BACKGROUND half of this problem
    # (the sandbox reaps detached processes at the bash-call boundary); this is the
    # FOREGROUND half, found the same way -- by losing two runs to it. The Cowork sandbox
    # also hard-caps a single call at ~178 s, and one PATH_A fault on a megabyte file
    # (window + brain + worktree on FUSE + the full 46 s gate ledger) does not fit. Killed
    # mid-gate the run wrote NOTHING: no report, no heartbeat, no record that the queue was
    # ever read. Two knobs, no change to any guard:
    #   --only=REF            drive the queue one fault per invocation
    #   MAINT_TIME_BUDGET_S=N stop cleanly BEFORE starting a fault that cannot finish
    # and the report is now written after EVERY fault, so a kill can cost at most the one
    # fault in flight. Deferred faults are named in the report -- never silently dropped.
    if _ONLY:
        want = {r.strip().upper() for r in _ONLY.split(",") if r.strip()}
        faults = [f for f in faults
                  if (f.get("ref") or ("TS-%04d" % f.get("id", 0))).upper() in want]
        say("--only=%s -- %d fault(s) selected" % (_ONLY, len(faults)))
    # MAINT-INTAKE-2: name the other live lane before anyone reads "seen" as "the queue".
    _email = email_lane_census()
    if _email.get("error"):
        say("email lane UNREAD (%s) -- 'seen' below counts app_faults ONLY" % _email["error"])
    else:
        say("email lane  %d total, %d held (30d %s) -- census only, not a fix lane"
            % (_email.get("total", 0), _email.get("held_30d", 0),
               _email.get("by_category_30d") or {}))
    report = {"run": _RUN_ID, "mode": mode, "seen": len(faults),
              "intake": {"app_faults_new": len(faults), "email_lane": _email},
              "actions": []}
    _t0 = time.time()
    _report_path = os.path.join(STATE,
                                "run_%s.json" % datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))

    def _flush():
        try:
            open(_report_path, "w").write(json.dumps(report, indent=2))
        except Exception as e:
            say("report write failed (%s) -- run continues" % type(e).__name__)

    for _i, f in enumerate(faults):
        ref = f.get("ref") or ("TS-%04d" % f.get("id", 0))
        if _BUDGET_S and (time.time() - _t0) > _BUDGET_S:
            for g in faults[_i:]:
                gref = g.get("ref") or ("TS-%04d" % g.get("id", 0))
                report["actions"].append({"ref": gref, "lane": "DEFERRED",
                                          "why": "time budget %.0fs reached before this fault "
                                                 "was started" % _BUDGET_S,
                                          "title": (g.get("title") or "")[:80],
                                          "outcome": "deferred to the next invocation "
                                                     "(HOST-CAP-1) -- not examined"})
            say("time budget %.0fs reached -- %d fault(s) deferred, run closing cleanly"
                % (_BUDGET_S, len(faults) - _i))
            _flush()
            break
        try:
            lane, why = classify(f)
        except Exception as e:
            # MAINT-B4-5: classification can never kill the queue -- escalate and move on.
            lane, why = "ESCALATE", "agent error during classify (%s) -- escalated, run continues" % type(e).__name__
        item = {"ref": ref, "lane": lane, "why": why, "title": (f.get("title") or "")[:80]}

        if lane in ("ESCALATE", "PATH_B"):
            # neither is autonomously fixed: escalate = report+safest; path_b = design backlog.
            if lane == "ESCALATE":
                item["outcome"] = "escalated (safety/legal/cost)"
            else:
                # DESIGN-ROUTE-1: file the dossier, then report what was WRITTEN -- never
                # the old sentence, which asserted a routing nothing performed.
                try:
                    dcb, note = file_design_dossier(f, why)
                except Exception as e:
                    dcb, note = None, "dossier filer errored (%s) -- NOT routed" % type(e).__name__
                if dcb:
                    item["dossier"] = dcb
                    item["outcome"] = "design backlog: %s (batched, designer gate)" % note
                else:
                    item["outcome"] = "design change NOT routed -- %s" % note
            report["actions"].append(item); say("%s -> %s (%s)" % (ref, lane, why)); _flush(); continue

        # ── PATH_A: propose, gate, and (only if fully armed) ship ───────────────────
        try:
            r = propose_patch(f)
        except Exception as e:
            item["outcome"] = "agent error during propose (%s) -> escalate for a human" % type(e).__name__
            report["actions"].append(item); say("%s -> propose error (%s)" % (ref, type(e).__name__)); _flush(); continue
        item["source"] = "%s/%s" % (r.provider, r.model)      # identified, every time
        if not r.ok or "NObugfix" in (r.text or "") or not _looks_like_patch(r.text):
            item["outcome"] = "brain declined a small mechanical fix -> escalate for a human"
            report["actions"].append(item); say("%s -> no clean patch (%s)" % (ref, item["source"])); _flush(); continue

        work = tempfile.mkdtemp(prefix="maint_")
        try:
            subprocess.run(["git", "worktree", "add", "--detach", work], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
            # GATE-CREDS-1 (13 Aug 2026): worktrees carry TRACKED files only, so the
            # gate suite's live-probe half (regression ledger) ran credential-less and
            # crashed 401-red against the armed origin gate -- every patch, however
            # perfect, gated red from the moment 016 armed. Give the throwaway worktree
            # the same .secrets the real repo runs with; removed in the finally below.
            _sec_src = os.path.join(REPO, ".secrets")
            if os.path.isdir(_sec_src):
                shutil.copytree(_sec_src, os.path.join(work, ".secrets"), dirs_exist_ok=True)
            patch = os.path.join(work, ".proposed.patch")
            _pt = _strip_fences(r.text)
            open(patch, "w").write(_pt + ("" if _pt.endswith("\n") else "\n"))
            # PATCH-FENCE-1 + --recount (13 Aug 2026): models fence their diffs and
            # miscount hunk headers; verbatim write + strict apply WAS the 'diffs
            # slip' class. Proven by hand: fenced+miscounted -> corrupt at the closing
            # fence; stripped + --recount --3way -> rc=0 and the seeded typo fixed.
            ap = subprocess.run(["git", "apply", "--recount", "--3way", patch], cwd=work,
                                capture_output=True, text=True, timeout=60)
            if ap.returncode != 0:
                # PATCH-EVIDENCE-1 (13 Aug 2026): 'did not apply' with no artifact was
                # undiagnosable for two days -- keep the failing diff and git's words.
                try:
                    os.makedirs(STATE, exist_ok=True)
                    _fp = os.path.join(STATE, "failed_%s_%s.patch"
                                       % (ref, datetime.now(timezone.utc).strftime("%H%M%S")))
                    shutil.copyfile(patch, _fp)
                    item["apply_error"] = (ap.stderr or ap.stdout or "")[:300]
                    item["failed_patch"] = _fp
                except Exception:
                    pass
                rw, why_rw = propose_rewrite(f)
                if not rw:
                    item["outcome"] = "patch did not apply cleanly; rewrite fallback: %s -> escalate" % why_rw
                    report["actions"].append(item); continue
                # MAINT-B4-6 / WINDOW-SPLICE-1: whole small file, or splice the corrected
                # block into the real file by the window's line range -- guarded: the block
                # we showed the brain must still match the worktree bytes exactly.
                _tgt = os.path.join(work, rw["path"])
                if rw.get("span"):
                    _lo, _hi = rw["span"]
                    _body = open(_tgt, encoding="utf-8", errors="replace").read()
                    _ls = _body.split("\n")
                    if "\n".join(_ls[_lo - 1:_hi]) != rw["orig_block"]:
                        item["outcome"] = ("rewrite splice refused: window bytes moved under "
                                           "us -> escalate for a human")
                        report["actions"].append(item); continue
                    _new = _ls[:_lo - 1] + rw["text"].rstrip("\n").split("\n") + _ls[_hi:]
                    open(_tgt, "w", encoding="utf-8").write("\n".join(_new))
                else:
                    open(_tgt, "w", encoding="utf-8").write(rw["text"])
                item["source"] = rw["source"]
                item["via"] = "rewrite-fallback"
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
            # SHIP-PUSH-GUARD-1 (14 Aug 2026): the push result was captured and DISCARDED.
            # With push auth missing (as it was the moment the agent was first armed) every
            # run committed to a throwaway worktree, failed to push in silence, counted a
            # ship against the rate limit, then force-removed the worktree at the end of the
            # loop -- orphaning the commit. The fault was left "fix-shipped": the register
            # said done, the site never changed, and the work was unrecoverable. Never again:
            # a push that did not happen is not a ship, and the work is kept on a real branch.
            _push = subprocess.run(["git", "push", "origin", "HEAD:deploy"],
                                   cwd=work, capture_output=True, timeout=120, text=True)
            if _push.returncode != 0:
                _err = ((_push.stderr or "") + (_push.stdout or "")).strip().splitlines()
                _err = _err[-1][:160] if _err else "rc=%d" % _push.returncode
                _salvage = "maint-unshipped/%s-%s" % (ref, time.strftime("%Y%m%d-%H%M%S"))
                subprocess.run(["git", "branch", _salvage], cwd=work,
                               capture_output=True, timeout=30)
                api("PUT", "/admin/faults/%d" % f["id"], key,
                    {"status": "escalated",
                     "fix_note": "maint-agent: fix built and gated GREEN but PUSH FAILED (%s). "
                                 "Work preserved on branch %s -- NOT shipped, NOT verified."
                                 % (_err, _salvage)})
                item["outcome"] = ("PUSH FAILED (%s) -> escalated; work kept on %s. "
                                   "No ship recorded." % (_err, _salvage))
                report["actions"].append(item); say("%s -> %s" % (ref, item["outcome"]))
                continue
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
            _flush()          # HOST-CAP-1: a kill costs at most the fault in flight

    path = _report_path
    _flush()
    say("report -> %s  (%d seen, %d acted)" % (path, report["seen"], len(report["actions"])))
    _post_heartbeat(report, mode, key)
    report["backup"] = _backup_lane()
    report["standup"] = _standup_lane()
    report["host_queue"] = _hostqueue_lane()
    report["screen_walk"] = _screen_walk_lane()
    _flush()
    return 0


def _screen_walk_lane():
    """SCREEN-WALK-1 (24 Sep 2026): the forward-looking half of the machinery.

    The regression ledger guards faults we have already NAMED. Nothing looked at the live app
    the way a person does, so on 24 Sep David was the detector: every home tile read 0 in
    Afrikaans over 58 loaded listings. scripts/screen_walk.py opens the live app in a real
    headless browser in each South African language, as a RETURNING reader, and fails when any
    language shows different numbers from English (tiles, Featured, each Browse screen) or the
    page throws. Proven to catch the 24 Sep build and pass the fixed one.

    Runs only where its browser toolkit can run (the Linux Cowork sandbox; the toolkit is cached
    at Projects/.tools/screen_walk so no download happens). Skipped on the origin and on the
    Windows host. ~30 s, hard cap 120 s, never raises. The witness it writes is what ledger
    RG-0456 judges -- a producer that lives in code, not in a sentence (BACKUP-IN-AGENT-1)."""
    rec = {"ran": False, "state": "NOT_MEASURED", "outcome": ""}
    if os.path.realpath(REPO).startswith("/opt/marketsquare-src") or not sys.platform.startswith("linux"):
        rec["outcome"] = "skipped: the screen walk runs in the Linux sandbox only"
        say("screen walk lane: %s" % rec["outcome"])
        return rec
    try:
        prod = os.path.join(REPO, "scripts", "screen_walk.py")
        if not os.path.isfile(prod):
            rec["outcome"] = "producer scripts/screen_walk.py missing"
        else:
            rec["ran"] = True
            r = subprocess.run([sys.executable, prod], cwd=REPO, capture_output=True, text=True,
                               timeout=120, env=dict(os.environ, MS_BEA_URL=BASE))
            rec["state"] = {0: "OK", 1: "MISMATCH"}.get(r.returncode, "NOT_MEASURED")
            tail = [l for l in ((r.stdout or "") + (r.stderr or "")).splitlines() if l.strip()]
            rec["outcome"] = " | ".join(tail[-4:])[:400] if tail else "(no output)"
    except Exception as e:
        rec["outcome"] = "FAILED: %s %s" % (type(e).__name__, str(e)[:120])
    say("screen walk lane: %s -- %s" % (rec["state"], rec["outcome"][:160]))
    return rec


def _standup_lane():
    """STANDUP-WATCHDOG-1 (written 23 Sep 2026, wired here the same day).

    WHY THIS EXISTS. The daily stand-up is the routine that notices everything else, and
    when IT stops nothing notices. Two separate silent outages are on the record:
    2 Aug - 18 Sep 2026, when every run was cloud-only with no write path and 47 days of
    pulses were run but never logged; and 20-22 Sep 2026, when the schedule simply did not
    fire and PULSE_LOG went three days unwritten. Both were found by a human reading the
    file weeks later, which is not a detector.

    So the loop that runs every ~20 minutes now reads the freshness of the stand-up's own
    output. The producer is scripts/standup_freshness.py; this is the one line that makes
    it a lane. It never raises: a watchdog that can take the run down with it is worse
    than no watchdog. And per RG-0187 an unreadable PULSE_LOG reports UNKNOWN, never
    FRESH -- a confident green from a blind probe is exactly how the next outage hides.
    """
    rec = {"ran": False, "state": "UNKNOWN", "reason": "", "age_h": None}
    try:
        sys.path.insert(0, os.path.join(REPO, "scripts"))
        import standup_freshness as _sf
        r = _sf.check()
        rec.update({"ran": True, "state": r.get("state"), "reason": r.get("reason"),
                    "age_h": r.get("age_h")})
    except Exception as e:
        rec["reason"] = "watchdog could not run: %s: %s" % (type(e).__name__, str(e)[:120])
    say("standup lane: %s (%s)" % (rec["state"], rec["reason"] or "-"))
    return rec


def _hostqueue_lane():
    """HOSTQUEUE-WATCHDOG-1 (25 Sep 2026).

    WHY THIS EXISTS. HOST-QUEUE-1 (RUL-095) is Claude's only pair of hands outside the
    sandbox: every git push and every host-side run goes through a .req that
    autodeploy_agent.bat executes on David's PC on a ~20-minute tick. On 25 Sep that agent
    stopped after 13:15:06Z and nothing noticed for 7h31m. By the evening stand-up FIVE
    commits were stranded unpushed -- including the 25 Sep inspection's critical fixes --
    so nothing had reached the mirror and nothing could deploy, while every instrument
    that looks at the SITE read green, correctly, because the site was fine. The site
    being healthy is not evidence that the way to change it is open.

    The detector is deliberately not "have results appeared lately": the agent only writes
    a result when there is work, so quiet is normal. The unambiguous signal is a PENDING
    request that nobody executed -- a permission-backed instruction sitting past two whole
    ticks means the executor is not running. Same shape as STANDUP-WATCHDOG-1 above.

    Local-only by construction: host_queue/ is gitignored, so it exists on the mount and on
    David's PC and never on the origin -- the lane skips there (BACKUP-ORIGIN-SKIP-1's
    precedent) rather than reporting a confident UNKNOWN from a vantage that cannot see it.
    Never raises: a watchdog that can take the run down with it is worse than no watchdog,
    and per RG-0187 an unreadable queue reports UNKNOWN, never OK.
    """
    import glob, time as _t
    rec = {"ran": False, "state": "UNKNOWN", "pending": None, "oldest_pending_h": None,
           "last_result_h": None, "ahead": None, "oldest_unpushed_h": None, "reason": ""}
    if os.path.realpath(REPO).startswith("/opt/marketsquare-src"):
        rec["reason"] = "skipped: host_queue is local-only and never reaches the origin"
        say("host-queue lane: %s" % rec["reason"])
        return rec
    try:
        qdir = os.path.join(REPO, "host_queue")
        if not os.path.isdir(qdir):
            rec["reason"] = "no host_queue/ directory on this vantage"
            say("host-queue lane: UNKNOWN (%s)" % rec["reason"]); return rec
        now = _t.time()
        pend = glob.glob(os.path.join(qdir, "*.req"))
        done = glob.glob(os.path.join(qdir, "done", "*.result"))
        rec["pending"] = len(pend)
        if done:
            rec["last_result_h"] = round((now - max(os.path.getmtime(f) for f in done)) / 3600.0, 2)
        rec["ran"] = True
        # The second signal, and the one that would have caught 25 Sep: work can be stranded
        # with NOTHING queued. Nothing was queued between 13:01Z and 20:38Z that day, yet five
        # commits -- including the inspection's criticals -- sat unpushed for hours, because the
        # push is what the dead agent was supposed to do. Commits ahead of the mirror ARE the
        # harm; a queued request is only one way of causing it.
        try:
            import subprocess
            env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
            r = subprocess.run(["git", "log", "--format=%ct", "origin/main..HEAD"],
                               cwd=REPO, env=env, capture_output=True, text=True, timeout=30)
            times = [int(x) for x in r.stdout.split() if x.isdigit()] if r.returncode == 0 else []
            rec["ahead"] = len(times)
            if times:
                rec["oldest_unpushed_h"] = round((now - min(times)) / 3600.0, 2)
        except Exception as e:
            rec["ahead"] = None
            rec["reason"] = "ahead-count unavailable: %s" % type(e).__name__
        stranded = bool(rec.get("ahead")) and (rec.get("oldest_unpushed_h") or 0) > (40 / 60.0)
        if stranded:
            rec["state"] = "STALLED"
            rec["reason"] = ("%d commit(s) committed but never pushed, oldest %.1f h -- they are "
                             "not on the mirror, so the origin cannot pull them and nothing they "
                             "fix is live" % (rec["ahead"], rec["oldest_unpushed_h"]))
            say("host-queue lane: %s (%s)" % (rec["state"], rec["reason"]))
            return rec
        if not pend:
            rec["state"] = "OK"
            rec["reason"] = ("nothing queued, nothing unpushed; newest result %s h old"
                             % (rec["last_result_h"] if rec["last_result_h"] is not None else "?"))
        else:
            oldest = min(os.path.getmtime(f) for f in pend)
            rec["oldest_pending_h"] = round((now - oldest) / 3600.0, 2)
            # two whole ticks is the bar: one missed tick is ordinary, two is an executor
            # that is not running.
            if (now - oldest) > 40 * 60:
                rec["state"] = "STALLED"
                rec["reason"] = ("%d request(s) queued and unexecuted, oldest %.1f h -- "
                                 "autodeploy_agent.bat is not running on David's PC, so no push "
                                 "and no deploy can leave this machine: %s"
                                 % (len(pend), rec["oldest_pending_h"],
                                    os.path.basename(sorted(pend)[0])))
            else:
                rec["state"] = "OK"
                rec["reason"] = ("%d request(s) queued, oldest %.2f h -- inside one tick"
                                 % (len(pend), rec["oldest_pending_h"]))
    except Exception as e:
        rec["reason"] = "watchdog could not run: %s: %s" % (type(e).__name__, str(e)[:120])
    say("host-queue lane: %s (%s)" % (rec["state"], rec["reason"] or "-"))
    return rec


def _backup_lane():
    """BACKUP-IN-AGENT-1 (23 Sep 2026): the DB-archive producer runs INSIDE the agent run.
    BACKUP-UNATTENDED-1 (10 Sep) wired backup_db_sandbox.py into 'step 2a' of the loop as a
    line in MAINTENANCE_AGENT.md -- and the loop's own step list never carried it, so the lane
    ran on 10, 11 and 12 Sep and then stopped for 11 days while RG-0234 sat red (the same
    silence the 10 Sep fix was written to end). A producer that lives in prose is a chore;
    this one lives in the code every run executes. Guarded: skipped when the newest archive
    is younger than 20 h; hard 150 s cap; never raises -- a backup fault degrades the run
    (recorded in the report), it never kills it (RG-0049 spirit)."""
    import glob, time as _t
    rec = {"ran": False, "outcome": ""}
    # BACKUP-ORIGIN-SKIP-1 (23 Sep 2026): the same file runs on the origin's own
    # maintenance-agent.timer (/opt/marketsquare-src). There the producer would try to back
    # the server up ONTO ITSELF over ssh -- a daily "FAILED" line at best, a pointless copy
    # at worst. The archive's job is an OFF-BOX copy, so this lane only runs off the box.
    if os.path.realpath(REPO).startswith("/opt/marketsquare-src"):
        rec["outcome"] = "skipped: running on the origin -- the archive lane is off-box only"
        say("backup lane: %s" % rec["outcome"])
        return rec
    try:
        newest = max((os.path.getmtime(z) for z in glob.glob(os.path.join(REPO, "backups", "*.zip"))),
                     default=0)
        age_h = (_t.time() - newest) / 3600.0
        if age_h < 20:
            rec["outcome"] = "skipped: newest archive is %.1f h old (<20 h)" % age_h
            say("backup lane: %s" % rec["outcome"])
            return rec
        prod = os.path.join(REPO, "scripts", "backup_db_sandbox.py")
        if not os.path.isfile(prod):
            rec["outcome"] = "producer scripts/backup_db_sandbox.py missing"
            say("backup lane: %s" % rec["outcome"])
            return rec
        rec["ran"] = True
        r = subprocess.run([sys.executable, prod], cwd=REPO, capture_output=True, text=True, timeout=150)
        tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
        rec["outcome"] = ("ok: " if r.returncode == 0 else "FAILED rc=%d: " % r.returncode) + \
                         (tail[-1][:200] if tail else "(no output)")
    except Exception as e:
        rec["outcome"] = "FAILED: %s %s" % (type(e).__name__, str(e)[:120])
    say("backup lane: %s" % rec["outcome"])
    return rec

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
