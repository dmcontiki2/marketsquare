"""
security_gate.py -- SEC-GATE-1 (24 Sep 2026)

David, 24 Sep 2026: "when i ask how can we be secure, then i would expect ... the safe solution,
not step one of a 15 step process towards being safe."

Security used to be written into each endpoint separately, so one forgotten check was one hole
(the 23 Sep audit found 17 of them, and the full review of all 292 routes on 24 Sep found 53 more).
This module moves the checks for whole CLASSES of hole into one place that runs before every handler:

  1. DENY BY DEFAULT   every route must be declared in route_policy.json with an access level;
                       an undeclared route is refused, so a new endpoint cannot ship open by accident.
  2. ACCESS LEVEL      public | user | superuser | admin | maint | service | token | device | reviewer.
                       "local": true on an admin/maint route also admits the server's own automation
                       (loopback caller that did not come through nginx).
  3. ACT AS YOURSELF   for signed-in users, every declared "actor" parameter (typed email in the path,
                       query, JSON or form) is rewritten to the proven session email. Typing somebody
                       else's address does nothing (same rule as _actor(): IDENTITY-BIND-2).
  4. OWNERSHIP         declared record ids (listing, agency, intro, document ...) must belong to the
                       signed-in user, looked up in ONE resolver table below.
  5. PRIVATE FIELDS    declared private keys (street address, editor emails, api keys ...) are removed
                       from public responses unless the caller owns that record or is admin.
  6. TRUE CLIENT IP    X-Forwarded-For / X-Real-IP / scope client are rewritten to the real client IP
                       (Cloudflare's CF-Connecting-IP, trusted only when the hop IS Cloudflare), so every
                       per-IP rate limit in the app counts real people, and a spoofed header counts nothing.

Admins (X-Admin-Key or an admin-scope X-Admin-Token) pass levels, binding and ownership - they act on
behalf of sellers from the console. Superusers (users.is_superuser, David's team, proven by sign-in)
pass ownership only.

Emergency lever: MS_GATE_ENFORCE=0 in the server environment makes the gate log-only (it still logs
every refusal it WOULD have made). There is no request-level way to turn it off.

The deploy is blocked unless scripts/stranger_test.py passes against the exact code being shipped.
"""
import ipaddress
import json
import logging
import os
import re
from urllib.parse import parse_qsl, quote, urlencode

from starlette.datastructures import Headers
from starlette.middleware import Middleware
from starlette.routing import Match, Mount

_log = logging.getLogger("bea.gate")

HERE = os.path.dirname(os.path.abspath(__file__))
POLICY_PATH = os.environ.get("MS_ROUTE_POLICY") or os.path.join(HERE, "route_policy.json")
LEVELS = ("public", "user", "superuser", "admin", "maint", "service", "token", "device", "reviewer")
MAX_BODY = 64 * 1024 * 1024          # bodies are only read for routes that bind/own from json/form

# Owner lookup, in ONE place. Each query takes the record id and returns the owner email(s).
# No row = record does not exist (the handler answers 404). A row whose owners are all empty =
# an ownerless record, which only an admin may act on.
RESOURCES = {
    "listing":            "SELECT LOWER(TRIM(seller_email)) FROM listings WHERE id = ?",
    "intro_seller":       "SELECT LOWER(TRIM(l.seller_email)) FROM intro_requests i "
                          "LEFT JOIN listings l ON l.id = i.listing_id WHERE i.id = ?",
    "intro_buyer":        "SELECT LOWER(TRIM(buyer_email)) FROM intro_requests WHERE id = ?",
    "intro_party":        "SELECT LOWER(TRIM(i.buyer_email)), LOWER(TRIM(l.seller_email)) "
                          "FROM intro_requests i LEFT JOIN listings l ON l.id = i.listing_id WHERE i.id = ?",
    "agency":             "SELECT LOWER(TRIM(admin_email)) FROM agencies WHERE id = ?",
    "agent_intro_agent":  "SELECT LOWER(TRIM(agent_email)) FROM agent_intros WHERE id = ?",
    "agent_intro_seller": "SELECT LOWER(TRIM(seller_email)) FROM agent_intros WHERE id = ?",
    "document":           "SELECT LOWER(TRIM(email)) FROM seller_documents WHERE id = ?",
}

# Keys that are never shown to a stranger on a public route, whatever the route declares.
GLOBAL_PRIVATE_KEYS = frozenset({
    "street_address", "attested_email", "changed_by", "api_key",
    "pin_hash", "password_hash", "id_number",
})
# An object carrying one of these keys equal to the caller's session email is the caller's own.
_OWNER_KEYS = ("seller_email", "email", "owner_email", "agent_email", "admin_email", "buyer_email", "user_email")

# Cloudflare edge ranges (https://www.cloudflare.com/ips/). CF-Connecting-IP is believed only when the
# hop that reached nginx is one of these - anyone else could type the header themselves.
_CF_NETS = tuple(ipaddress.ip_network(n) for n in (
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22", "141.101.64.0/18",
    "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20", "197.234.240.0/22", "198.41.128.0/17",
    "162.158.0.0/15", "104.16.0.0/13", "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22",
    "2400:cb00::/32", "2606:4700::/32", "2803:f800::/32", "2405:b500::/32", "2405:8100::/32",
    "2a06:98c0::/29", "2c0f:f248::/32",
))
_LOOPBACK = (ipaddress.ip_network("127.0.0.0/8"), ipaddress.ip_network("::1/128"))

_INT_RE = re.compile(r"[+-]?\d+(\.0*)?")


def _as_id(value):
    """The integer FastAPI/pydantic will see for this id - or None if it will refuse it.
    The gate must look up exactly the record the handler will act on: '0_9', ' 9 ', '+9', '9.0'
    and JSON true all reach a handler as 9 or 1, so they must be checked as 9 or 1 here."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value == int(value) else None
    t = str(value).strip().replace("_", "")
    if not _INT_RE.fullmatch(t):
        return None
    return int(t.split(".")[0])


_PARAM_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::([A-Za-z]+))?\}")


def _ip(value):
    try:
        return ipaddress.ip_address((value or "").strip())
    except ValueError:
        return None


def _in(ip, nets):
    return ip is not None and any(ip in n for n in nets)


def load_policy(path=None):
    """Read and validate route_policy.json. A malformed file raises: better a failed deploy than
    a gate that silently means something else."""
    with open(path or POLICY_PATH, encoding="utf-8") as f:
        data = json.load(f)
    routes = data["routes"] if isinstance(data, dict) else data
    pol = {}
    for e in routes:
        key, lvl = e.get("key"), e.get("level")
        if not key or lvl not in LEVELS:
            raise ValueError("route_policy: bad entry %r (level %r)" % (key, lvl))
        for b in e.get("bind", []):
            if b.get("in") not in ("path", "query", "json", "form") or not b.get("name"):
                raise ValueError("route_policy: bad bind on %s: %r" % (key, b))
        for o in e.get("own", []):
            if o.get("in") not in ("path", "query", "json", "form") or not o.get("name"):
                raise ValueError("route_policy: bad own on %s: %r" % (key, o))
            if o.get("resource") not in RESOURCES:
                raise ValueError("route_policy: unknown resource on %s: %r" % (key, o.get("resource")))
        if key in pol:
            raise ValueError("route_policy: duplicate key %s" % key)
        pol[key] = e
    return pol


def route_key(method, route):
    if isinstance(route, Mount):
        return "MOUNT " + route.path
    return method + " " + route.path


def runtime_keys(app):
    """Every (key) the running app can answer - the stranger test and the startup check use this."""
    keys = []
    for r in app.router.routes:
        if isinstance(r, Mount):
            keys.append(("MOUNT " + r.path, r))
            continue
        for m in sorted(getattr(r, "methods", None) or []):
            if m == "HEAD" and "GET" in r.methods:
                continue
            keys.append((m + " " + r.path, r))
    return keys


def _dumps(obj):
    # Byte-for-byte the shape Starlette's JSONResponse renders (compact, UTF-8), so a body the gate
    # re-serialises reads exactly like one it did not touch (the deploy health check greps '"status":"ok"').
    return json.dumps(obj, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")


async def _send_json(send, status, payload, extra_headers=()):
    body = _dumps(payload)
    headers = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]
    headers.extend(extra_headers)
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})


def _set_header(scope, name, value):
    name_b = name.lower().encode("latin-1")
    hdrs = [(k, v) for (k, v) in scope["headers"] if k != name_b]
    if value is not None:
        hdrs.append((name_b, value.encode("latin-1")))
    scope["headers"] = hdrs


def _get_dotted(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _set_dotted(obj, dotted, value):
    parts = dotted.split(".")
    cur = obj
    for part in parts[:-1]:
        if not isinstance(cur, dict):
            return False
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            return False          # never invent a nested object the handler did not send
        cur = nxt
    if not isinstance(cur, dict):
        return False
    cur[parts[-1]] = value
    return True


def _norm(v):
    return (str(v) if v is not None else "").strip().lower()


class SecurityGate:
    """Pure ASGI middleware, installed innermost (just in front of the router)."""

    def __init__(self, app, *, fastapi_app, session_email, is_admin, is_maint, db, is_superuser,
                 policy=None, enforce=None):
        self.app = app
        self.fa = fastapi_app
        self.session_email = session_email
        self.is_admin = is_admin
        self.is_maint = is_maint
        self.db = db
        self.is_superuser = is_superuser
        self.policy = policy if policy is not None else load_policy()
        self.enforce = (os.environ.get("MS_GATE_ENFORCE", "1") != "0") if enforce is None else enforce

    # ── helpers ───────────────────────────────────────────────────────────────────────────
    def _match(self, scope):
        partial = None
        for r in self.fa.router.routes:
            m, child = r.matches(scope)
            if m == Match.FULL:
                return r, child
            if m == Match.PARTIAL and partial is None:
                partial = (r, child)
        return None, None

    def _lookup(self, method, route):
        key = route_key(method, route)
        pol = self.policy.get(key)
        if pol is None and method == "HEAD" and not isinstance(route, Mount):
            key = "GET " + route.path
            pol = self.policy.get(key)
        return key, pol

    @staticmethod
    def real_ip(hdrs, peer):
        xr = _ip(hdrs.get("x-real-ip"))
        if xr is None:
            return peer
        if _in(xr, _CF_NETS):
            cf = _ip(hdrs.get("cf-connecting-ip"))
            if cf is not None:
                return str(cf)
        return str(xr)

    async def _refuse(self, send, scope, key, status, detail, code, who=""):
        _log.warning("SEC-GATE %s %s %s -> %s %s (%s)", "DENY" if self.enforce else "WOULD-DENY",
                     key, (scope.get("client") or ("?",))[0], status, code, who)
        if self.enforce:
            await _send_json(send, status, {"detail": detail, "code": code})
            return True
        return False

    def _owners(self, resource, value):
        sql = RESOURCES[resource]
        v = _as_id(value)
        if v is None:
            return set()                      # not an id the handler would accept: nobody owns it
        conn = self.db()
        try:
            rows = conn.execute(sql, (v,)).fetchall()
        finally:
            conn.close()
        if not rows:
            return None                       # no such record: the handler answers 404
        owners = set()
        for row in rows:
            for x in tuple(row):
                if x:
                    owners.add(_norm(x))
        return owners                         # empty set = ownerless record

    # ── the gate ──────────────────────────────────────────────────────────────────────────
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        hdrs = Headers(scope=scope)
        client = scope.get("client") or ("", 0)
        peer = client[0]
        via_nginx = "x-real-ip" in hdrs
        peer_is_loopback = _in(_ip(peer), _LOOPBACK)

        # 6. true client IP for every handler below
        real = self.real_ip(hdrs, peer)
        if real and real != peer:
            scope["client"] = (real, client[1] if len(client) > 1 else 0)
        if via_nginx:
            _set_header(scope, "x-real-ip", real)
            _set_header(scope, "x-forwarded-for", real)
            _set_header(scope, "cf-connecting-ip", real)
        elif "x-forwarded-for" in hdrs and not peer_is_loopback:
            _set_header(scope, "x-forwarded-for", real)
        hdrs = Headers(scope=scope)

        if scope["method"] == "OPTIONS":
            return await self.app(scope, receive, send)       # CORS preflight / 405 from the router

        route, child = self._match(scope)
        if route is None:
            return await self.app(scope, receive, send)       # 404 / 405 from the router
        key, pol = self._lookup(scope["method"], route)

        # 1. deny by default
        if pol is None:
            _log.error("SEC-GATE undeclared route %s - add it to route_policy.json", key)
            if await self._refuse(send, scope, key, 403, "This route has no declared access rule.",
                                  "undeclared_route"):
                return
            return await self.app(scope, receive, send)

        level = pol["level"]
        cookies = _cookies(hdrs)
        admin = bool(self.is_admin(hdrs, cookies))
        session = None
        if level in ("user", "superuser", "public") or pol.get("hide"):
            session = self.session_email(cookies.get("ts_user"))

        # 2. access level. "local": true lets the box's own automation (a loopback caller that did NOT
        #    come through nginx: the BIT timer, the deploy purge, the maintenance agent) through as well.
        local_ok = bool(pol.get("local")) and peer_is_loopback and not via_nginx
        denied = None
        if level == "user" and not (session or admin):
            denied = (401, "Please sign in to do that.", "signin_required")
        elif level == "superuser" and not (admin or (session and self.is_superuser(session))):
            denied = (401, "Only the TrustSquare team can do that.", "superuser_required")
        elif level == "admin" and not (admin or local_ok):
            denied = (401, "Admin credentials required.", "admin_required")
        elif level == "maint" and not (admin or local_ok or self.is_maint(hdrs)):
            denied = (401, "Maintenance credentials required.", "maint_required")
        elif level == "service" and not (peer_is_loopback and not via_nginx):
            denied = (403, "This is a server-to-server route.", "service_only")
        if denied:
            if await self._refuse(send, scope, key, *denied, who=session or ""):
                return
            return await self.app(scope, receive, send)

        # 3 + 4. act as yourself, and only on your own records
        if level == "user" and not admin and session and (pol.get("bind") or pol.get("own")):
            specs = list(pol.get("bind", [])) + list(pol.get("own", []))
            body = b""
            ctype = hdrs.get("content-type", "")
            if any(s["in"] in ("json", "form") for s in specs):
                body = await _read_body(receive)
                if body is None:
                    await _send_json(send, 413, {"detail": "Request too large.", "code": "too_large"})
                    return
            rewritten = False
            json_obj = None
            media = ctype.split(";")[0].strip().lower()
            is_json = (media == "application/json" or not media
                       or (media.startswith("application/") and media.endswith("+json")))
            if body and is_json:
                try:
                    json_obj = json.loads(body)
                except ValueError:
                    json_obj = None
            form_pairs = None
            if body and media == "application/x-www-form-urlencoded":
                form_pairs = parse_qsl(body.decode("latin-1"), keep_blank_values=True)
            multipart = None
            if body and media == "multipart/form-data":
                multipart = await _multipart_fields(scope, body)
            if (body.strip() and any(x["in"] in ("json", "form") for x in specs)
                    and json_obj is None and form_pairs is None and multipart is None):
                # A body the gate cannot read is a body it cannot bind or check - refuse it rather than
                # let the handler read something the gate never saw.
                await _send_json(send, 415, {"detail": "Unreadable request body.", "code": "bad_body"})
                return

            path_params = dict(child.get("path_params", {}))
            query = parse_qsl(scope.get("query_string", b"").decode("latin-1"), keep_blank_values=True)
            new_path = False
            new_query = False

            for b in pol.get("bind", []):
                name, where = b["name"], b["in"]
                if where == "path":
                    if name in path_params and _norm(path_params[name]) != session:
                        path_params[name] = session
                        new_path = True
                elif where == "query":
                    vals = [v for (k, v) in query if k == name]
                    if vals and any(_norm(v) != session for v in vals):
                        query = [(k, v) for (k, v) in query if k != name] + [(name, session)]
                        new_query = True
                elif where == "json":
                    cur = _get_dotted(json_obj, name) if isinstance(json_obj, dict) else None
                    if cur not in (None, "") and _norm(cur) != session:
                        if _set_dotted(json_obj, name, session):
                            rewritten = True
                elif where == "form":
                    if form_pairs is not None:
                        vals = [v for (k, v) in form_pairs if k == name]
                        if vals and any(_norm(v) != session for v in vals):
                            form_pairs = [(k, v) for (k, v) in form_pairs if k != name] + [(name, session)]
                            rewritten = True
                    elif multipart is not None:
                        vals = multipart.get(name, [])
                        if any(_norm(v) != session for v in vals):
                            if await self._refuse(send, scope, key, 403,
                                                  "You can only do that for your own account.",
                                                  "not_you", who=session):
                                return

            if pol.get("own") and not self.is_superuser(session):
                for o in pol["own"]:
                    name, where = o["name"], o["in"]
                    if where == "path":
                        value = path_params.get(name)
                    elif where == "query":
                        vals = [v for (k, v) in query if k == name]
                        value = vals[-1] if vals else None
                    elif where == "json":
                        value = _get_dotted(json_obj, name) if isinstance(json_obj, dict) else None
                    else:
                        if form_pairs is not None:
                            vals = [v for (k, v) in form_pairs if k == name]
                        else:
                            vals = (multipart or {}).get(name, [])
                        value = vals[-1] if vals else None
                    if value in (None, ""):
                        continue
                    owners = self._owners(o["resource"], value)
                    if owners is None:
                        continue
                    if session not in owners:
                        if await self._refuse(send, scope, key, 403, "That isn't yours.", "not_owner",
                                              who=session):
                            return

            if new_path:
                plain = _PARAM_RE.sub(lambda m: str(path_params[m.group(1)]), route.path)
                raw = _PARAM_RE.sub(lambda m: quote(str(path_params[m.group(1)]),
                                                    safe="/" if m.group(2) == "path" else ""),
                                    route.path)
                scope["path"] = scope.get("root_path", "") + plain
                scope["raw_path"] = (scope.get("root_path", "") + raw).encode("utf-8")
            if new_query:
                scope["query_string"] = urlencode(query).encode("latin-1")
            if rewritten:
                if json_obj is not None:
                    body = _dumps(json_obj)
                elif form_pairs is not None:
                    body = urlencode(form_pairs).encode("latin-1")
                _set_header(scope, "content-length", str(len(body)))
            if body or any(s["in"] in ("json", "form") for s in specs):
                receive = _replay(body, receive)

        # 5. private fields on public answers
        hide = set(pol.get("hide", []))
        if level in ("public", "token", "reviewer", "device"):
            hide |= GLOBAL_PRIVATE_KEYS
            hide -= set(pol.get("expose", []))
        if hide and not admin:
            send = _scrubbing_send(send, hide, session)

        # 7. CONTENT-GATE-1 (24 Sep 2026, security assessment): user-written record fields are plain text
        #    and photo fields are plain https links, on EVERY JSON answer (admins included - the console
        #    renders the same records). Many render paths in ms.js / quick.html / the admin console put
        #    these into innerHTML, so markup is neutralised here once instead of at 200 separate sinks.
        send = _encoding_send(send)

        return await self.app(scope, receive, send)


def _cookies(hdrs):
    out = {}
    for part in hdrs.get("cookie", "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out.setdefault(k.strip(), v.strip())
    return out


async def _read_body(receive):
    chunks, size = [], 0
    while True:
        msg = await receive()
        if msg["type"] == "http.disconnect":
            break
        chunk = msg.get("body", b"")
        size += len(chunk)
        if size > MAX_BODY:
            return None
        chunks.append(chunk)
        if not msg.get("more_body"):
            break
    return b"".join(chunks)


def _replay(body, receive):
    sent = False

    async def _receive():
        nonlocal sent
        if not sent:
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return await receive()
    return _receive


async def _multipart_fields(scope, body):
    """Text fields of a multipart body (files ignored), without consuming the real stream."""
    from starlette.requests import Request
    req = Request(dict(scope), receive=_replay(body, _never))
    out = {}
    try:
        form = await req.form()
        for k, v in form.multi_items():
            if isinstance(v, str):
                out.setdefault(k, []).append(v)
        await form.close()
    except Exception:
        return {}
    return out


async def _never():
    return {"type": "http.disconnect"}


def _scrub(obj, hide, session):
    if isinstance(obj, list):
        return [_scrub(x, hide, session) for x in obj]
    if isinstance(obj, dict):
        if session and any(_norm(obj.get(k)) == session for k in _OWNER_KEYS if obj.get(k)):
            return obj                          # the caller's own record: untouched
        return {k: _scrub(v, hide, session) for k, v in obj.items() if k not in hide}
    return obj


def _scrubbing_send(send, hide, session):
    state = {"start": None, "chunks": [], "json": False}

    async def _send(message):
        if message["type"] == "http.response.start":
            ctype = Headers(raw=message.get("headers", [])).get("content-type", "")
            state["json"] = ctype.startswith("application/json")
            if not state["json"]:
                await send(message)
            else:
                state["start"] = message
            return
        if message["type"] == "http.response.body" and state["json"]:
            state["chunks"].append(message.get("body", b""))
            if message.get("more_body"):
                return
            raw = b"".join(state["chunks"])
            try:
                parsed = json.loads(raw)
                cleaned = _scrub(parsed, hide, session)
                if cleaned != parsed:            # only a body that really lost a private key is rewritten
                    raw = _dumps(cleaned)
            except ValueError:
                pass
            start = dict(state["start"])
            start["headers"] = [(k, v) for (k, v) in start.get("headers", []) if k.lower() != b"content-length"]
            start["headers"].append((b"content-length", str(len(raw)).encode()))
            await send(start)
            await send({"type": "http.response.body", "body": raw})
            return
        await send(message)
    return _send


# ---- 7. CONTENT-GATE-1: output encoding for user-written record fields ------------------------------
# Keys whose values are ALWAYS plain text when they sit on a record (a dict carrying "id").
_TEXT_KEYS = frozenset({
    "title", "suburb", "area", "city", "prop_type", "make", "model", "msg", "message", "seller_name",
    "display_name", "business_name", "agency_name", "headline", "tagline", "summary", "heading",
    "caption", "location", "name", "subtitle", "bullets", "sections", "description", "desc",
    # CONTENT-GATE-2 (25 Sep 2026 inspection, ts1-01/ts2-01/ts3-02/ts3-04): seller- and buyer-written fields the
    # app also paints into the page, which this list had missed.
    "subject", "level", "mode", "service_type", "service_class", "availability", "buyer_name", "buyer_first_name",
    "price", "per", "other_name", "from_name", "colour", "variant", "body_type", "condition", "destination",
})
# Keys whose values must be a plain https:// (or same-site /path) link - nothing that can break out of
# an attribute or run as a scheme.
_URL_KEYS = frozenset({"thumb_url", "photo", "medium_url", "photo_url", "image_url", "avatar_url",
                       "logo_url", "photos", "photo_urls", "images"})
_URL_OK = re.compile(r"^(https://[^\s\"'<>`\\]+|/(?!/)[^\s\"'<>`\\]*|data:image/(?:png|jpeg|jpg|webp|gif);base64,[A-Za-z0-9+/=]+)$")


def _pt(v):
    if isinstance(v, str):
        if "<" in v or ">" in v:
            v = re.sub(r"<[^>]*>", "", v).replace("<", "\u2039").replace(">", "\u203a")
        if '"' in v:
            # CONTENT-GATE-2 (25 Sep 2026 inspection, ts2-03): a straight double quote let a title break out of
            # alt="..." / src="..." and add its own handler; it leaves as a typographic quote instead.
            v = re.sub(r'(^|[\s(\[{])"', lambda m: m.group(1) + "\u201c", v).replace('"', "\u201d")
        return v
    if isinstance(v, list):
        return [_pt(x) for x in v]
    if isinstance(v, dict):
        return {k: _pt(x) for k, x in v.items()}
    return v


def _text_field(v):
    """Plain text; a description stored as a JSON document is decoded, cleaned and re-encoded, because
    escaped markup inside it (\\u003c) only turns into '<' after the browser parses it."""
    if isinstance(v, str) and v.lstrip().startswith(("{", "[")):
        try:
            doc = json.loads(v)
        except ValueError:
            return _pt(v)
        cleaned = _pt(doc)
        return v if cleaned == doc else json.dumps(cleaned, ensure_ascii=False)
    return _pt(v)


def _url_field(v):
    if isinstance(v, str):
        return v if (not v or _URL_OK.match(v)) else ""
    if isinstance(v, list):
        return [x for x in (_url_field(y) for y in v) if x or x == 0]
    return v


def _encode(obj):
    if isinstance(obj, list):
        return [_encode(x) for x in obj]
    if isinstance(obj, dict):
        record = "id" in obj or "pair_id" in obj   # CONTENT-GATE-2: Buzz pair rows carry pair_id, not id
        out = {}
        for k, v in obj.items():
            if k in _URL_KEYS:
                out[k] = _url_field(v)
            elif record and k in _TEXT_KEYS:
                out[k] = _text_field(v)
            else:
                out[k] = _encode(v)
        return out
    return obj


def _encoding_send(send):
    state = {"start": None, "chunks": [], "json": False}

    async def _send(message):
        if message["type"] == "http.response.start":
            ctype = Headers(raw=message.get("headers", [])).get("content-type", "")
            state["json"] = ctype.startswith("application/json")
            if not state["json"]:
                await send(message)
            else:
                state["start"] = message
            return
        if message["type"] == "http.response.body" and state["json"]:
            state["chunks"].append(message.get("body", b""))
            if message.get("more_body"):
                return
            raw = b"".join(state["chunks"])
            try:
                parsed = json.loads(raw)
                cleaned = _encode(parsed)
                if cleaned != parsed:            # untouched answers keep their exact bytes
                    raw = _dumps(cleaned)
            except Exception:
                pass
            start = dict(state["start"])
            start["headers"] = [(k, v) for (k, v) in start.get("headers", []) if k.lower() != b"content-length"]
            start["headers"].append((b"content-length", str(len(raw)).encode()))
            await send(start)
            await send({"type": "http.response.body", "body": raw})
            return
        await send(message)
    return _send


def install(app, **hooks):
    """Put the gate innermost (after CORS / GZip / the device-renew middleware, right in front of the
    router) and log every running route that has no declared rule."""
    policy = load_policy()
    app.user_middleware.append(Middleware(SecurityGate, fastapi_app=app, policy=policy, **hooks))
    missing = [k for (k, _r) in runtime_keys(app) if k not in policy]
    for k in missing:
        _log.error("SEC-GATE undeclared route at startup: %s (it will be refused)", k)
    _log.info("SEC-GATE installed: %d declared routes, %d undeclared", len(policy), len(missing))
    return missing
