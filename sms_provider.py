"""sms_provider.py -- PHONE-KEY-1 (David, 24 Sep 2026): one door for every SMS the app sends.

Provider-agnostic, fails DARK: with no provider configured ready() is False, every send returns
("skipped", "no sms provider configured") and nothing anywhere raises. Configure in
/etc/marketsquare/secrets.env (the unit's EnvironmentFile), never in the repo:

    SMS_PROVIDER=bulksms | clickatell | smsportal
    SMS_TOKEN=<token id>:<token secret>      (BulkSMS: basic-auth token pair;  Clickatell: the API key;
                                              SMSPortal: <client id>:<client secret>)
    SMS_SENDER=TrustSquare                    (optional alphanumeric sender where the network allows it)

Numbers are normalised to E.164 for South Africa (0XX... -> +27XX...); any other country must arrive
with its + prefix. No number is ever logged in full -- only its last three digits.
"""
import os, re, json, logging, base64, time

_log = logging.getLogger("sms")
_RATE = {}           # to_e164 -> [epoch, ...]  (per-number throttle: 6 messages an hour)
_TOKEN_CACHE = {}    # smsportal bearer token


def normalise(phone: str, default_cc: str = "27"):
    """Return +E.164 or None. ZA local 0XXXXXXXXX -> +27XXXXXXXXX; keeps a leading + as given."""
    p = re.sub(r"[^\d+]", "", phone or "")
    if not p:
        return None
    if p.startswith("00"):
        p = "+" + p[2:]
    if p.startswith("+"):
        digits = p[1:]
        return ("+" + digits) if 9 <= len(digits) <= 15 else None
    if p.startswith("0") and len(p) == 10:
        return "+" + default_cc + p[1:]
    if len(p) == 9 and default_cc == "27":
        return "+27" + p
    if p.startswith(default_cc) and 10 <= len(p) <= 13:
        return "+" + p
    return None


def mask(e164: str) -> str:
    e164 = e164 or ""
    return ("+" + "*" * max(0, len(e164) - 4) + e164[-3:]) if len(e164) >= 6 else "***"


def provider() -> str:
    return (os.environ.get("SMS_PROVIDER") or "").strip().lower()


def ready() -> bool:
    return provider() in ("bulksms", "clickatell", "smsportal") and bool((os.environ.get("SMS_TOKEN") or "").strip())


def _throttled(to: str, per_hour: int = 6) -> bool:
    now = time.time()
    hits = [t for t in _RATE.get(to, []) if now - t < 3600]
    if len(hits) >= per_hour:
        _RATE[to] = hits
        return True
    hits.append(now); _RATE[to] = hits
    return False


def send(to: str, text: str, purpose: str = "") -> tuple:
    """Send one SMS. Returns (status, info): status in 'sent' | 'skipped' | 'failed'."""
    e164 = normalise(to)
    if not e164:
        return ("failed", "number not recognised")
    if not ready():
        _log.info("sms skipped (%s): no provider configured -- to %s", purpose, mask(e164))
        return ("skipped", "no sms provider configured")
    if _throttled(e164):
        _log.warning("sms throttled (%s): %s", purpose, mask(e164))
        return ("skipped", "throttled")
    text = (text or "")[:459]              # three concatenated GSM parts at most
    try:
        import httpx
    except Exception:
        return ("failed", "httpx missing")
    tok = (os.environ.get("SMS_TOKEN") or "").strip()
    sender = (os.environ.get("SMS_SENDER") or "").strip()
    prov = provider()
    try:
        if prov == "bulksms":
            basic = base64.b64encode(tok.encode()).decode()
            body = {"to": e164, "body": text}
            if sender:
                body["from"] = sender
            r = httpx.post("https://api.bulksms.com/v1/messages", json=body,
                           headers={"Authorization": "Basic " + basic}, timeout=15)
            ok = r.status_code in (200, 201)
        elif prov == "clickatell":
            body = {"content": text, "to": [e164.lstrip("+")]}
            if sender:
                body["from"] = sender
            r = httpx.post("https://platform.clickatell.com/messages", json=body,
                           headers={"Authorization": tok, "Content-Type": "application/json"}, timeout=15)
            ok = r.status_code in (200, 202)
        elif prov == "smsportal":
            bearer = _TOKEN_CACHE.get("t")
            if not bearer or _TOKEN_CACHE.get("exp", 0) < time.time():
                cid, _, csec = tok.partition(":")
                basic = base64.b64encode((cid + ":" + csec).encode()).decode()
                a = httpx.get("https://rest.smsportal.com/Authentication",
                              headers={"Authorization": "Basic " + basic}, timeout=15)
                a.raise_for_status()
                bearer = a.json().get("token"); _TOKEN_CACHE.update({"t": bearer, "exp": time.time() + 20 * 60})
            body = {"messages": [{"content": text, "destination": e164.lstrip("+")}]}
            r = httpx.post("https://rest.smsportal.com/BulkMessages", json=body,
                           headers={"Authorization": "Bearer " + bearer, "Content-Type": "application/json"}, timeout=15)
            ok = r.status_code in (200, 201, 202)
        else:
            return ("skipped", "unknown provider")
        info = "%s %s" % (prov, r.status_code)
        if ok:
            _log.info("sms sent (%s) to %s via %s", purpose, mask(e164), prov)
            return ("sent", info)
        _log.warning("sms FAILED (%s) to %s: %s %s", purpose, mask(e164), info, (r.text or "")[:160])
        return ("failed", info)
    except Exception as exc:
        _log.warning("sms FAILED (%s) to %s: %s", purpose, mask(e164), exc)
        return ("failed", str(exc)[:120])
