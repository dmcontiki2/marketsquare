#!/usr/bin/env python3
"""
stranger_test.py -- SEC-GATE-1 (24 Sep 2026). A deploy is blocked unless this passes.

David, 24 Sep 2026: security must be the whole solution, not step one of fifteen. This test is the
part that keeps it whole: it walks EVERY route the backend serves - including routes added after
today - and proves, against the exact code being shipped, that:

  A0  the gate is installed and no running route is undeclared (deny by default is live)
  A1  every user / admin / maint / service route refuses a stranger (no sign-in, public app key only)
  B1  every admin / maint route refuses a signed-in ordinary user AND every other kind of token
      this app signs (session cookie, e-mailed sign-in link, employer link, device pass) - the
      token-confusion class found on 24 Sep
  B2  real admin credentials still get through (the gate must not lock David out)
  C   (--deep) a signed-in stranger B, typing victim A's e-mail and A's record ids into every
      user route, cannot read A's e-mail back or change A's account rows, and is refused on
      A's records; the owner A is NOT refused on her own records

It runs fully offline: a throwaway copy of the database, outbound network blocked in-process.
Only A0-B2 are needed to gate a deploy; --deep runs handlers as real users, so it runs where no
provider keys exist (the sandbox harness), never on the live box.

    python3 scripts/stranger_test.py --src <dir holding bea_main.py or main.py> --db <sqlite file> [--deep]
Exit 0 = PASS, 1 = FAIL (the report lists every failing route), 2 = could not run.
"""
import argparse
import hashlib
import json
import os
import shutil
import socket
import sys
import tempfile
import time
import types
from datetime import datetime, timedelta, timezone

GATE_CODES = {"signin_required", "superuser_required", "admin_required", "maint_required", "service_only",
              "undeclared_route", "not_owner", "not_you", "bad_body"}
A_EMAIL = "stranger-test-victim@example.invalid"
B_EMAIL = "stranger-test-attacker@example.invalid"


def block_network():
    real_connect = socket.socket.connect

    def guarded(self, addr):
        host = addr[0] if isinstance(addr, tuple) else addr
        if isinstance(host, str) and (host.startswith("127.") or host in ("localhost", "::1")):
            return real_connect(self, addr)
        raise OSError("stranger_test: outbound network blocked (%s)" % (host,))
    socket.socket.connect = guarded
    real_gai = socket.getaddrinfo

    def gai(host, *a, **k):
        if host in ("localhost", "127.0.0.1", "::1", None):
            return real_gai(host, *a, **k)
        raise socket.gaierror("stranger_test: DNS blocked (%s)" % host)
    socket.getaddrinfo = gai


def load_app(src, db):
    sys.path.insert(0, src)
    tmp = tempfile.mkdtemp(prefix="stranger_")
    os.environ.setdefault("MS_WEB_ROOT", tmp)
    import database
    copy = os.path.join(tmp, "marketsquare.db")
    shutil.copy(db, copy)
    database.DB_PATH = copy
    modname = "bea_main" if os.path.exists(os.path.join(src, "bea_main.py")) else "main"
    stubbed = []
    for _ in range(40):
        try:
            mod = __import__(modname)
            break
        except ModuleNotFoundError as e:       # sandbox only: an optional SDK that is not installed
            stubbed.append(e.name)
            sys.modules.pop(modname, None)
            parts = e.name.split(".")
            for i in range(1, len(parts) + 1):
                sys.modules.setdefault(".".join(parts[:i]), _Stub(".".join(parts[:i])))
    return mod, database, stubbed


class _Stub(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return _StubObj()


class _StubObj:
    def __call__(self, *a, **k):
        return _StubObj()

    def __getattr__(self, n):
        return _StubObj()


def fill_path(template, values):
    import re
    def rep(m):
        name, conv = m.group(1), m.group(2)
        if name in values:
            return str(values[name])
        if conv == "int" or name.endswith("_id") or name in ("id", "version_num"):
            return "999999"
        if "email" in name:
            return "nobody@example.invalid"
        return "x"
    return re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::([A-Za-z]+))?\}", rep, template)


def gate_refused(resp):
    if resp.status_code not in (401, 403):
        return False
    try:
        return resp.json().get("code") in GATE_CODES
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--deep", action="store_true")
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    # The test mints its own credentials: it never needs, reads or prints the real ones, and the
    # tokens it forges are self-consistent with the app it has just imported.
    import secrets as _sec
    for _k in ("MS_API_KEY", "MS_ADMIN_KEY", "MS_JWT_SECRET", "MS_MAINT_KEY", "MS_REVIEW_SECRET"):
        os.environ[_k] = "stranger-test-" + _sec.token_hex(16)
    block_network()
    t0 = time.time()
    try:
        mod, database, stubbed = load_app(os.path.abspath(a.src), os.path.abspath(a.db))
        import security_gate as sg
        from fastapi.testclient import TestClient
    except Exception as exc:
        print("STRANGER TEST could not run: %r" % (exc,))
        return 2

    app = mod.app
    import jwt as pyjwt
    secret, algo = mod._JWT_SECRET, mod._JWT_ALGO
    admin_key = mod.MS_ADMIN_KEY
    api_key = os.environ.get("MS_API_KEY", "")
    if not secret or not admin_key:
        print("STRANGER TEST could not run: MS_JWT_SECRET / MS_ADMIN_KEY missing in this environment")
        return 2
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=1)

    def tok(claims):
        return pyjwt.encode(dict(claims, iat=now, exp=exp), secret, algorithm=algo)
    session_a = tok({"scope": "user", "sub": A_EMAIL})
    session_b = tok({"scope": "user", "sub": B_EMAIL})
    forged = {
        "user session cookie": session_b,
        "sign-in link": tok({"email": B_EMAIL, "purpose": "signin"}),
        "employer link": tok({"email": A_EMAIL, "purpose": "employer_confirm"}),
        "device pass as token": tok({"sub": "device/x", "scope": "device", "jti": "x"}),
        "admin-looking user token": tok({"sub": "master", "scope": "user"}),
    }
    real_admin_token = mod._make_token("master")

    fails, checked = [], {"A1": 0, "B1": 0, "B2": 0, "C": 0}
    policy = sg.load_policy()
    keys = sg.runtime_keys(app)

    # A0
    installed = any(getattr(m, "cls", None) is sg.SecurityGate for m in app.user_middleware)
    if not installed:
        fails.append(("A0", "*", "security gate is not installed in the app"))
    undeclared = [k for k, _ in keys if k not in policy]
    for k in undeclared:
        fails.append(("A0", k, "route has no declared rule in route_policy.json"))

    # U: the gate's own parsing, pinned against the bypasses found in review on 24 Sep 2026
    for raw, want in (("9", 9), ("0_9", 9), (" 9 ", 9), ("+9", 9), ("9.0", 9), (True, 1), (9.0, 9),
                      ("9a", None), ("", None), ("0x9", None), (9.5, None)):
        if sg._as_id(raw) != want:
            fails.append(("U", "_as_id", "%r -> %r, expected %r" % (raw, sg._as_id(raw), want)))
    from starlette.datastructures import Headers as _H
    for hdr, peer, want in (({}, "127.0.0.1", "127.0.0.1"),
                            ({"x-real-ip": "203.0.113.9", "cf-connecting-ip": "1.2.3.4"}, "127.0.0.1", "203.0.113.9"),
                            ({"x-real-ip": "162.158.1.1", "cf-connecting-ip": "1.2.3.4"}, "127.0.0.1", "1.2.3.4"),
                            ({"x-real-ip": "162.158.1.1"}, "127.0.0.1", "162.158.1.1")):
        got = sg.SecurityGate.real_ip(_H(headers=hdr), peer)
        if got != want:
            fails.append(("U", "real_ip", "%r -> %r, expected %r" % (hdr, got, want)))

    client = TestClient(app, raise_server_exceptions=False)
    stranger_headers = {"X-Api-Key": api_key} if api_key else {}

    def call(method, path, headers=None, cookies=None, **kw):
        client.cookies.clear()
        for k, v in (cookies or {}).items():
            client.cookies.set(k, v)
        return client.request(method, path, headers=headers or {}, **kw)

    for key, route in keys:
        pol = policy.get(key)
        if not pol or key.startswith("MOUNT "):
            continue
        method, template = key.split(" ", 1)
        level = pol["level"]
        path = fill_path(template, {})
        body = {"json": {}} if method in ("POST", "PUT", "PATCH", "DELETE") else {}
        if level in ("user", "superuser", "admin", "maint", "service"):
            checked["A1"] += 1
            r = call(method, path, headers=stranger_headers, **body)
            if not gate_refused(r):
                fails.append(("A1", key, "stranger got %s %s" % (r.status_code, r.text[:120])))
        if level in ("superuser", "admin", "maint"):
            for label, t in forged.items():
                checked["B1"] += 1
                r = call(method, path, headers=dict(stranger_headers, **{"X-Admin-Token": t}), **body)
                if not gate_refused(r):
                    fails.append(("B1", key, "%s accepted as admin: %s" % (label, r.status_code)))
            checked["B1"] += 1
            r = call(method, path, headers=stranger_headers, cookies={"ts_user": session_b}, **body)
            if not gate_refused(r):
                fails.append(("B1", key, "signed-in user got %s" % r.status_code))

    # B2: real admin credentials pass the gate (checked on read-only admin routes only)
    for key, route in keys:
        pol = policy.get(key)
        if not pol or pol["level"] != "admin" or not key.startswith("GET "):
            continue
        path = fill_path(key.split(" ", 1)[1], {})
        for label, hdr in (("admin key", {"X-Admin-Key": admin_key}), ("admin token", {"X-Admin-Token": real_admin_token})):
            checked["B2"] += 1
            r = call("GET", path, headers=hdr)
            if gate_refused(r):
                fails.append(("B2", key, "%s refused by the gate - lockout" % label))

    if a.deep:
        deep(mod, database, policy, keys, call, session_a, session_b, fails, checked, stranger_headers)

    elapsed = time.time() - t0
    report = {"result": "PASS" if not fails else "FAIL", "routes": len(keys), "checked": checked,
              "failures": [{"check": c, "route": k, "why": w} for c, k, w in fails],
              "stubbed_modules": stubbed, "seconds": round(elapsed, 1)}
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=1)
    print("STRANGER TEST %s - %d routes, checks %s, %.1fs" % (report["result"], len(keys), checked, elapsed))
    for c, k, w in fails[:200]:
        print("  FAIL %s %s: %s" % (c, k, w))
    return 0 if not fails else 1


# ── C: a signed-in stranger against a victim's account ────────────────────────────────────────────
def deep(mod, database, policy, keys, call, session_a, session_b, fails, checked, hdr=None):
    import security_gate as sg
    hdr = hdr or {}
    conn = database.get_db()
    seeded = seed(conn)
    conn.close()
    owned = owned_fingerprint_sql(database)
    spec = mod.app.openapi()
    snap = database.DB_PATH + ".seeded"
    shutil.copy(database.DB_PATH, snap)

    for key, route in keys:
        pol = policy.get(key)
        if not pol or pol["level"] != "user" or key.startswith("MOUNT "):
            continue
        shutil.copy(snap, database.DB_PATH)       # every route starts from the same seeded state
        before_all = fingerprint(database, owned)
        method, template = key.split(" ", 1)
        values, query, jbody = {}, {}, {}
        for b in pol.get("bind", []):
            _place(b, A_EMAIL, values, query, jbody)
        own_ok = True
        for o in pol.get("own", []):
            rid = seeded.get(o["resource"])
            if rid is None:
                own_ok = False
                continue
            _place(o, rid, values, query, jbody)
        path = fill_path(template, values)
        body = synth_body(spec, template, method, jbody)
        kw = {}
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            kw["json"] = body
        checked["C"] += 1
        r = call(method, path, headers=hdr, cookies={"ts_user": session_b}, params=query, **kw)
        if r.status_code >= 500:
            checked.setdefault("C_5xx", []).append("%s %s" % (key, r.status_code))
        checked.setdefault("C_status", {}).setdefault(str(r.status_code), 0)
        checked["C_status"][str(r.status_code)] += 1
        if pol.get("own") and own_ok:
            code = None
            try:
                code = r.json().get("code")
            except Exception:
                pass
            if code != "not_owner":
                fails.append(("C", key, "stranger on victim's record got %s (expected not_owner)" % r.status_code))
            # the same attack with the id written the way pydantic still accepts ('0_<id>')
            v2, q2, j2 = dict(values), dict(query), json.loads(json.dumps(jbody))
            for o in pol.get("own", []):
                rid = seeded.get(o["resource"])
                if rid is not None:
                    _place(o, "0_%s" % rid, v2, q2, j2)
            kw2 = {}
            if method in ("POST", "PUT", "PATCH", "DELETE"):
                kw2["content"] = json.dumps(synth_body(spec, template, method, j2))
                kw2["headers"] = dict(hdr, **{"Content-Type": "Application/JSON"})
            else:
                kw2["headers"] = hdr
            r3 = call(method, fill_path(template, v2), cookies={"ts_user": session_b}, params=q2, **kw2)
            if r3.status_code < 400 or A_EMAIL in (r3.text or ""):
                fails.append(("C", key, "owner check bypassed with '0_<id>' / mixed-case content type: %s" % r3.status_code))
        if A_EMAIL in (r.text or ""):
            fails.append(("C", key, "victim's e-mail came back to the stranger"))
        if pol.get("bind") and method == "GET":
            # the same read with the actor parameter left out must not fall back to everybody's data
            q0 = {k: v for k, v in query.items() if k not in {b["name"] for b in pol["bind"] if b["in"] == "query"}}
            r0 = call(method, path, headers=hdr, cookies={"ts_user": session_b}, params=q0)
            if A_EMAIL in (r0.text or ""):
                fails.append(("C", key, "victim's e-mail came back when the actor parameter was left out"))
        after = fingerprint(database, owned)
        changed = [t for t in after if after[t] != before_all.get(t)]
        if changed:
            fails.append(("C", key, "stranger changed victim rows in %s" % ",".join(changed)))
        # owner control: A on her own records is never refused as not_owner
        if pol.get("own") and own_ok:
            r2 = call(method, path, headers=hdr, cookies={"ts_user": session_a}, params=query, **kw)
            try:
                if r2.json().get("code") == "not_owner":
                    fails.append(("C", key, "OWNER refused on her own record"))
            except Exception:
                pass


def _place(spec, value, values, query, jbody):
    where, name = spec["in"], spec["name"]
    if where == "path":
        values[name] = value
    elif where == "query":
        query[name] = value
    elif where in ("json", "form"):
        cur = jbody
        parts = name.split(".")
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = value


def synth_body(spec, template, method, overrides):
    op = (spec.get("paths", {}).get(template, {}) or {}).get(method.lower(), {})
    schema = (((op.get("requestBody") or {}).get("content") or {}).get("application/json") or {}).get("schema")
    comps = spec.get("components", {}).get("schemas", {})
    body = _gen(schema, comps, 0) if schema else {}
    if not isinstance(body, dict):
        body = {}
    _merge(body, overrides)
    return body


def _merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _merge(dst[k], v)
        else:
            dst[k] = v


def _gen(s, comps, depth):
    if depth > 6 or not isinstance(s, dict):
        return None
    if "$ref" in s:
        return _gen(comps.get(s["$ref"].split("/")[-1], {}), comps, depth + 1)
    for alt in ("anyOf", "oneOf", "allOf"):
        if alt in s:
            for sub in s[alt]:
                if sub.get("type") != "null":
                    return _gen(sub, comps, depth + 1)
            return None
    if "enum" in s:
        return s["enum"][0]
    if "default" in s and s["default"] is not None:
        return s["default"]
    t = s.get("type")
    if t == "object" or "properties" in s:
        out = {}
        for name, sub in (s.get("properties") or {}).items():
            if name in (s.get("required") or []) or "email" in name:
                v = _gen(sub, comps, depth + 1)
                if "email" in name and (sub.get("type") == "string" or v is None or isinstance(v, str)):
                    v = A_EMAIL
                out[name] = v
        return out
    if t == "array":
        return []
    if t == "integer":
        return 1
    if t == "number":
        return 1.0
    if t == "boolean":
        return False
    return "x"


def seed(conn):
    """Victim A owns one of each resource; attacker B exists. Throwaway DB only."""
    ids = {}

    def insert(table, values):
        cols = {r[1]: r for r in conn.execute("PRAGMA table_info(%s)" % table)}
        if not cols:
            return None
        row = {}
        for name, info in cols.items():
            notnull, default, pk = info[3], info[4], info[5]
            if name in values:
                row[name] = values[name]
            elif notnull and default is None and not pk:
                t = (info[2] or "").upper()
                row[name] = 0 if ("INT" in t or "REAL" in t or "NUM" in t) else "x"
        q = "INSERT INTO %s (%s) VALUES (%s)" % (table, ",".join(row), ",".join("?" * len(row)))
        cur = conn.execute(q, tuple(row.values()))
        return cur.lastrowid

    for em in (A_EMAIL, B_EMAIL):
        if not conn.execute("SELECT 1 FROM users WHERE email=?", (em,)).fetchone():
            insert("users", {"email": em, "name": em.split("@")[0]})
    conn.execute("UPDATE users SET tuppence_balance = 50 WHERE email IN (?, ?)", (A_EMAIL, B_EMAIL)) \
        if any(r[1] == "tuppence_balance" for r in conn.execute("PRAGMA table_info(users)")) else None
    ids["listing"] = insert("listings", {"seller_email": A_EMAIL, "title": "victim listing"})
    ids["agency"] = insert("agencies", {"admin_email": A_EMAIL, "name": "victim agency"})
    try:
        iid = insert("intro_requests", {"listing_id": ids["listing"], "buyer_email": A_EMAIL})
        ids["intro_buyer"] = ids["intro_seller"] = ids["intro_party"] = iid
    except Exception:
        pass
    for res, table, vals in (("agent_intro_agent", "agent_intros", {"agent_email": A_EMAIL, "seller_email": A_EMAIL}),
                             ("document", "seller_documents", {"email": A_EMAIL})):
        try:
            ids[res] = insert(table, vals)
        except Exception:
            pass
    if "agent_intro_agent" in ids:
        ids["agent_intro_seller"] = ids["agent_intro_agent"]
    conn.commit()
    return {k: v for k, v in ids.items() if v is not None}


# Account-state rows attributed to the victim. A stranger acting as himself must never change these.
_OWNED = [("users", "email"), ("listings", "seller_email"), ("user_credentials", "email"),
          ("seller_documents", "email"), ("agencies", "admin_email"), ("agent_profiles", "agent_email"),
          ("ai_spend_holds", "email"), ("transactions", "user_email"), ("intro_requests", "buyer_email"),
          ("tuppence_monthly_grants", "email"), ("seller_extra_slots", "email"), ("planner_specs", "user_email"),
          ("user_declarations", "email"), ("launch_codes", "email"), ("founders_badges", "email"),
          ("account_closures", "email"), ("coach_ask_log", "email")]
_VOLATILE = {"last_seen", "last_active", "updated_at", "view_count", "views"}


def owned_fingerprint_sql(database):
    conn = database.get_db()
    out = []
    try:
        for table, col in _OWNED:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(%s)" % table)]
            if col in cols:
                keep = [c for c in cols if c not in _VOLATILE]
                out.append((table, "SELECT %s FROM %s WHERE LOWER(%s) = ? ORDER BY 1" % (",".join(keep), table, col)))
    finally:
        conn.close()
    return out


def fingerprint(database, owned):
    conn = database.get_db()
    fp = {}
    try:
        for table, q in owned:
            rows = [tuple(r) for r in conn.execute(q, (A_EMAIL,)).fetchall()]
            fp[table] = hashlib.sha256(repr(rows).encode()).hexdigest()
    finally:
        conn.close()
    return fp


if __name__ == "__main__":
    sys.exit(main())
