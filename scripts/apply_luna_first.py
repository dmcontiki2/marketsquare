#!/usr/bin/env python3
"""LUNA-FIRST-1 (RUL-203, David 4 Oct 2026): "luna does the first check on every photo, and terra double-checks only photos
that need blurring ... Drop Gemini." Every FIRST photo check (seller upload gate + agency import) is read by OpenAI
gpt-5.6-luna (the 'vision' tier, ~$0.0005 a check). A photo luna calls clean, at/above the confidence gate, with no
moderation flag and no wrong-subject call, is accepted on luna's word. Anything else -- a plate, a sign, low confidence,
a flag, a failed or unparseable answer -- is re-read by gpt-5.6-terra, whose verdict drives everything after it exactly
as before (reject-only bridge / blur + verify). A luna outage never falls back to an untested model: the call is
no-fallback, and a failure simply goes to terra. Proven before the switch: honest eval 22/22, 0 plate misses, 3 false
flags (terra 4). Kill switch: PHOTO_SCAN_FIRST=terra (env or server .env). Idempotent; asserts every anchor."""
import io, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bea_main.py")
s = io.open(P, encoding="utf-8", newline="").read(); n0 = len(s)
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)
s = rep(s, 'def _anon_photo_scan(jpeg_b64, provider, category=""):\n',
           'def _anon_photo_scan(jpeg_b64, provider, category="", first=False, who="", _task="reason"):\n'
           '    """LUNA-FIRST-1 (RUL-203): first=True -> luna reads it first; only a photo luna does not pass as clean goes to\n'
           '    terra (this same function, the reason tier), whose answer is returned. The luna read is metered here."""\n'
           '    if first and _task == "reason":\n'
           '        try:\n'
           '            import ai_provider as _apf\n'
           '            _first_on = (_apf.envkey("PHOTO_SCAN_FIRST") or "luna").lower() != "terra"\n'
           '        except Exception:\n'
           '            _first_on = False\n'
           '        if _first_on:\n'
           '            _l, _lit, _lot, _lsv = _anon_photo_scan(jpeg_b64, "openai", category, False, who, "vision")\n'
           '            if _l and _l.get("verdict") == "clean" and float(_l.get("confidence") or 0) >= _ANON_PHOTO_CONF \\\n'
           '                    and _l.get("flag") != "inappropriate" and _l.get("fits") is not False:\n'
           '                return _l, _lit, _lot, _lsv          # caller meters it, as for any scan\n'
           '            if _lit is not None or _lot is not None:  # luna flagged it: meter luna here, terra is metered by the caller\n'
           '                try:\n'
           '                    _log_ai_spend(who or "", "/photo#anon-first-luna", "vision", _lit, _lot,\n'
           '                                  provider=(_lsv[0] if _lsv else None), model=(_lsv[1] if _lsv else None))\n'
           '                except Exception:\n'
           '                    pass\n', "signature")
s = rep(s, '            task="reason", max_tokens=1400, provider=provider)   # Sonnet for import scans',
           '            task=_task, max_tokens=1400, provider=provider,\n'
           '            allow_fallback=(_task != "vision"))   # LUNA-FIRST-1: the luna read never falls to an untested lane; Sonnet for import scans',
        "complete call")
s = rep(s, '        _b64.b64encode(pbuf.getvalue()).decode(),\n        _anon_scan_provider(_ts_active_provider()), category or "")   # GEMINI-CANARY-1\n',
           '        _b64.b64encode(pbuf.getvalue()).decode(),\n        _ts_active_provider(), category or "", first=True, who=spend_who)   # LUNA-FIRST-1 (RUL-203; Gemini dropped)\n',
        "seller gate")
s = rep(s, '        scan, _it, _ot, _svd = _anon_photo_scan(_b64.b64encode(pbuf.getvalue()).decode(), provider, category)\n'
           '        if _it is not None or _ot is not None:\n            _log_ai_spend(agent, "/agencies/import#photo-scan"',
           '        scan, _it, _ot, _svd = _anon_photo_scan(_b64.b64encode(pbuf.getvalue()).decode(), provider, category, first=True, who=agent)   # LUNA-FIRST-1\n'
           '        if _it is not None or _ot is not None:\n            _log_ai_spend(agent, "/agencies/import#photo-scan"',
        "agency import")
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("LUNA-FIRST-1 applied: %d -> %d chars" % (n0, len(s)))
