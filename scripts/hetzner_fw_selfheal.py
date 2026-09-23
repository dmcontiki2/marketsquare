#!/usr/bin/env python3
"""hetzner_fw_selfheal.py — SSH-LOCKOUT-1 prevention (17 Aug 2026, David's ask #1).

WHY: the trustsquare-origin-lockdown firewall allowlists SSH (port 22) to David's
home IP. Home power/router resets change that IP (proven 17 Aug: blackout -> new IP
-> both David and the session locked out until a hand-fix at the Hetzner panel).

WHAT: run from David's machine AND from the sandbox (since 23 Sep 2026 they can have
DIFFERENT egress IPs -- SANDBOX-EGRESS-1, see PEERS below). Reads the
current public IP, reads the firewall's SSH rule via the Hetzner Cloud API, and if
the rule is not exactly [current IP], SETS it to that (NO-STALE-IP-1, 2 Sep 2026: stale
entries are pruned, every other rule stays intact).
Self-healing: the machine that owns the NEW IP is the machine that runs this.

TOKEN: .secrets/hetzner_token.txt (gitignored) or HETZNER_API_TOKEN env — a Hetzner
Cloud API token with read+write, created at console.hetzner.com > project > Security
> API tokens. Missing token => exit 2 with the instruction, changes nothing.

Run:  python3 scripts/hetzner_fw_selfheal.py           # heal if needed
      python3 scripts/hetzner_fw_selfheal.py --check   # report only, change nothing
"""
import json, os, sys, time, urllib.request

FIREWALL_ID = 11414216          # trustsquare-origin-lockdown
API = "https://api.hetzner.cloud/v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = "--check" in sys.argv

# SANDBOX-EGRESS-1 (23 Sep 2026, maintenance loop). The "one egress" premise broke: on
# 23 Sep David's PC left through 165.165.181.198 while the Cowork sandbox (a Hyper-V VM
# on the same PC) left through 197.184.121.169. The host tick, honouring NO-STALE-IP-1,
# SET the rule to the PC's address every 20 min and so locked every sandbox session out
# of port 22 for the whole day (RG-0099 red, three sessions saw it). Two vantages, two
# lanes, one rule:
#   * every run first BEACONS its own vantage (host / sandbox) and IP into PEERS, with
#     a UTC timestamp -- the file is gitignored (.secrets/) and shared over the mount;
#   * the HOST lane is the pruner: it SETS the rule to exactly {its own IP} U {every
#     peer beacon younger than PEER_TTL_H}. A sandbox IP older than that is a dead
#     address and is pruned, so NO-STALE-IP-1 still holds -- the bound is 24 h, not 0,
#     and it is short BECAUSE the sandbox lane re-adds itself on every SSH load;
#   * the SANDBOX lane is ADD-ONLY: it can only put its own IP in, never take one out,
#     so it can never lock the host out while the host's beacon is not yet on file.
# Either lane can only ever name the IP of the machine that ran it: still the anti-lockout.
PEERS = os.path.join(REPO, ".secrets", "egress_peers.json")
PEER_TTL_H = 24   # short on purpose: the sandbox re-adds itself on every SSH load
VANTAGE = "host" if os.name == "nt" else "sandbox"

def _beacon(my_ip):
    """Record this vantage's live egress; return the fresh IPs of the OTHER vantages."""
    now = time.time()
    try:
        peers = json.load(open(PEERS, encoding="utf-8"))
    except Exception:
        peers = {}
    if not CHECK:
        peers[VANTAGE] = {"ip": my_ip, "at": now,
                          "at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))}
        try:
            os.makedirs(os.path.dirname(PEERS), exist_ok=True)
            with open(PEERS, "w", encoding="utf-8") as f:
                json.dump(peers, f, indent=1)
        except OSError as e:
            print("[fw-selfheal] beacon not written (%s) -- peers unchanged" % e)
    fresh = []
    for v, rec in peers.items():
        if v == VANTAGE or not isinstance(rec, dict):
            continue
        if now - float(rec.get("at", 0)) <= PEER_TTL_H * 3600 and rec.get("ip"):
            fresh.append(rec["ip"])
    return fresh

def token():
    t = os.environ.get("HETZNER_API_TOKEN", "").strip()
    if t: return t
    p = os.path.join(REPO, ".secrets", "hetzner_token.txt")
    try:
        return open(p, encoding="utf-8").read().strip()
    except OSError:
        return ""

def api(path, tok, method="GET", body=None):
    req = urllib.request.Request(API + path, method=method,
        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json",
                 "User-Agent": "trustsquare-fw-selfheal/1"})
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(req, data=data, timeout=20) as r:
        return json.loads(r.read().decode() or "{}")

def main():
    tok = token()
    if not tok:
        print("[fw-selfheal] NO TOKEN: create a read+write Cloud API token at "
              "console.hetzner.com > Default project > Security > API tokens and save it "
              "to .secrets/hetzner_token.txt (David-only paste). Nothing changed.")
        return 2
    try:
        my_ip = urllib.request.urlopen("https://api.ipify.org", timeout=10).read().decode().strip()
    except Exception as e:
        print("[fw-selfheal] cannot read current public IP (%s) — offline? Nothing changed." % e)
        return 1
    fw = api("/firewalls/%d" % FIREWALL_ID, tok)["firewall"]
    rules = fw["rules"]
    ssh = [r for r in rules if r.get("direction") == "in" and str(r.get("port")) == "22"]
    if not ssh:
        print("[fw-selfheal] REFUSE: no inbound port-22 rule found — layout changed, human review.")
        return 3
    ips = ssh[0].get("source_ips", [])
    want = my_ip + "/32"
    # NO-STALE-IP-1 (David, 2 Sep 2026): the SSH rule holds EXACTLY the live egress IPs.
    # Every entry that is not a live vantage is a dead address left by a router reset, and
    # a dead allowlist entry is an open door for whoever the ISP hands that IP to next.
    # Heal = set, not append -- on the HOST lane. SANDBOX-EGRESS-1 (23 Sep 2026) widened
    # "the one IP" to "the live vantages": see PEERS / _beacon above.
    peers = _beacon(my_ip)
    want_set = sorted({want} | {p + "/32" for p in peers})
    if VANTAGE == "host":
        if sorted(ips) == want_set:
            print("[fw-selfheal] ok: SSH rule holds exactly %s (host + %d fresh sandbox beacon). "
                  "Nothing to do." % (want_set, len(peers)))
            return 0
        stale = [i for i in ips if i not in want_set]
        if CHECK:
            print("[fw-selfheal] WOULD SET the SSH rule to %s (currently: %s; stale: %s). "
                  "Run without --check to heal." % (want_set, ips, stale))
            return 0
        ssh[0]["source_ips"] = want_set
        api("/firewalls/%d/actions/set_rules" % FIREWALL_ID, tok, method="POST", body={"rules": rules})
        print("[fw-selfheal] HEALED: SSH allowlist is now exactly %s; pruned %d stale: %s"
              % (want_set, len(stale), stale))
        return 0
    # sandbox lane: add-only. It puts its own IP in; only the host tick ever takes one out.
    if want in ips:
        print("[fw-selfheal] ok: SSH rule already holds this sandbox's %s (rule: %s). "
              "Nothing to do." % (want, ips))
        return 0
    new_ips = sorted(set(ips) | {want})
    if CHECK:
        print("[fw-selfheal] WOULD ADD %s to the SSH rule (currently: %s) -- sandbox lane is "
              "add-only; the host tick prunes. Run without --check to heal." % (want, ips))
        return 0
    ssh[0]["source_ips"] = new_ips
    api("/firewalls/%d/actions/set_rules" % FIREWALL_ID, tok, method="POST", body={"rules": rules})
    print("[fw-selfheal] HEALED (sandbox lane, add-only): SSH allowlist is now %s; the host "
          "tick prunes anything older than %d h" % (new_ips, PEER_TTL_H))
    return 0


# ── Cloudflare half (SSH-LOCKOUT-1 sibling: the PRELAUNCH GATE WAF rule) ──────
CF_ZONE  = "trustsquare.co"
CF_RULE_ID = "8a38bd913d0b43db93152f996f50d8ac"   # PRELAUNCH GATE - block all except allowlisted IPs

def cf_token():
    t = os.environ.get("CF_WAF_TOKEN", "").strip()
    if t: return t
    try:
        return open(os.path.join(REPO, ".secrets", "cf_waf_token.txt"), encoding="utf-8").read().strip()
    except OSError:
        return ""

CF_HALF_RETIRED = True   # RUL-034 (19 Aug 2026): PRELAUNCH GATE rule DISABLED; launched 1 Sep 2026.

def cf_heal(my_ip):
    if CF_HALF_RETIRED:
        print("[fw-selfheal] CF: half RETIRED -- the PRELAUNCH GATE rule is disabled (RUL-034) and "
              "the site launched 1 Sep 2026; nothing at the edge allowlists IPs any more. No token needed.")
        return 0
    tok = cf_token()
    if not tok:
        print("[fw-selfheal] CF: no token (.secrets/cf_waf_token.txt — zone-scoped, Zone.Firewall "
              "Services edit). The Cloudflare PRELAUNCH GATE cannot self-heal until provided.")
        return 2
    def capi(path, method="GET", body=None):
        req = urllib.request.Request("https://api.cloudflare.com/client/v4" + path, method=method,
            headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json",
                     "User-Agent": "trustsquare-fw-selfheal/1"})
        data = json.dumps(body).encode() if body is not None else None
        with urllib.request.urlopen(req, data=data, timeout=20) as r:
            return json.loads(r.read().decode())
    zid = capi("/zones?name=" + CF_ZONE)["result"][0]["id"]
    rs = capi("/zones/%s/rulesets/phases/http_request_firewall_custom/entrypoint" % zid)["result"]
    rule = next((r for r in rs.get("rules", []) if r.get("id") == CF_RULE_ID or
                 "PRELAUNCH GATE" in (r.get("description") or "")), None)
    if not rule:
        print("[fw-selfheal] CF: PRELAUNCH GATE rule not found — layout changed, human review."); return 3
    expr = rule["expression"]
    if my_ip in expr:
        print("[fw-selfheal] CF ok: %s already in the gate allowlist." % my_ip); return 0
    import re as _re
    m = _re.search(r"\{([^}]*)\}", expr)
    if not m:
        print("[fw-selfheal] CF: no IP set found in expression — human review."); return 3
    new_expr = expr.replace(m.group(0), "{" + m.group(1).rstrip() + " " + my_ip + "}")
    if CHECK:
        print("[fw-selfheal] CF WOULD update expression to: %s" % new_expr[:160]); return 0
    capi("/zones/%s/rulesets/%s/rules/%s" % (zid, rs["id"], rule["id"]), method="PATCH",
         body={"expression": new_expr, "action": rule["action"],
               "description": rule.get("description", "")})
    print("[fw-selfheal] CF HEALED: added %s to the PRELAUNCH GATE allowlist." % my_ip)
    return 0

def main_all():
    rc = main()
    try:
        my_ip = urllib.request.urlopen("https://api.ipify.org", timeout=10).read().decode().strip()
        rc2 = cf_heal(my_ip)
    except Exception as e:
        print("[fw-selfheal] CF half errored: %s" % e); rc2 = 1
    return max(rc, rc2)

if __name__ == "__main__":
    sys.exit(main_all())
