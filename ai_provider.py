#!/usr/bin/env python3
"""
ai_provider.py — the single seam for LLM inference (D1-FIX).
Swap the inference vendor in ONE place (AI_ACTIVE env), exactly like ai_service_tiers swaps feed providers.
Call sites use abstract task tiers ("haiku"/"sonnet"/"vision"/"triage"), never vendor model strings.

    from ai_provider import complete
    r = complete(messages, task="haiku", max_tokens=700)
    r.text, r.in_tokens, r.out_tokens, r.provider, r.model

Adding a provider = add an adapter to ADAPTERS + a task->model row. Flip AI_ACTIVE to switch. No call-site edits.
This reference includes the Anthropic adapter (byte-equivalent to the app's current call) + an OpenAI stub
to prove the seam is real. Spend logging is injected by the caller (keeps DB out of this module).
"""
import os, json
from dataclasses import dataclass

AI_ACTIVE = os.getenv("AI_ACTIVE", "anthropic")   # one place to swap the vendor

_ENVFILE_CACHE = None
def envkey(*names):
    """os.getenv first; fall back to the server .env file (the systemd unit does not
    export it to this process — ENVKEY-1, 17 Jul 2026). Cached after first read."""
    global _ENVFILE_CACHE
    for n in names:
        v = os.getenv(n)
        if v: return v
    if _ENVFILE_CACHE is None:
        _ENVFILE_CACHE = {}
        try:
            with open("/var/www/marketsquare/.env", encoding="utf-8") as f:
                for ln in f:
                    ln = ln.strip()
                    if ln and not ln.startswith("#") and "=" in ln:
                        k, v = ln.split("=", 1)
                        _ENVFILE_CACHE[k.strip()] = v.strip()
        except Exception:
            pass
    for n in names:
        if _ENVFILE_CACHE.get(n): return _ENVFILE_CACHE[n]
    return None

# abstract task tier -> per-provider model string (vendor names live HERE, not at call sites)
TASK_MODEL = {
    "anthropic": {"haiku":"claude-haiku-4-5-20251001","sonnet":"claude-sonnet-4-6",
                  "vision":"claude-haiku-4-5-20251001","triage":"claude-haiku-4-5-20251001"},
    # GPT-5.6 family (verified 31 Jul 2026 vs developers.openai.com/api/docs/models): Luna $0.20/$1.20,
    # Terra $2/$12, Sol $5/$30 per Mtok after the 30 Jul cuts; all three take image input, so Luna covers
    # the vision tier too. Luna = cheap tiers, Terra = reasoning rung ("gpt-5.6-sol" exists as flagship).
    # Vendor-doc gate UNCHANGED: golden-set eval before production traffic; OPENAI_API_KEY still
    # unprovisioned (David-only) — dashboard shows the lane DISABLED until the key lands. RG-0016.
    "openai":    {"haiku":"gpt-5.6-luna","sonnet":"gpt-5.6-terra",
                  "vision":"gpt-5.6-luna","triage":"gpt-5.6-luna"},
    # Scaleway EU (P1) — canon lives HERE per seam philosophy; deliberately ignores FAILOVER_MODEL_* env
    # (those belong to failover/ai_backends.py). Reasoning tier uses the non-thinking instruct variant
    # (qwen3.5-397b overthinks short tasks — live demo finding 17 Jul).
    "scaleway":  {"haiku":"mistral-medium-3.5-128b","sonnet":"mistral-medium-3.5-128b",
                  "vision":"mistral-medium-3.5-128b","triage":"mistral-medium-3.5-128b"},
    # ONE-MODEL STANDBY (David's ruling, 18 Jul 2026): whole row = mistral-medium-3.5-128b.
    # Golden-set basis same day: 7/7 text + 2/2 vision (qwen3.6 failed vision JSON; qwen3-235b
    # failed 1/7 adverts). One standby = one behaviour to know. Prior row ids in CHANGELOG.
}

@dataclass
class AIResult:
    text: str; in_tokens: int|None; out_tokens: int|None; provider: str; model: str; ok: bool=True
    # P2a (1 Aug 2026): failure CLASSIFICATION for the breaker — Peer major #4: a bare
    # ok-flag cannot distinguish ban from blip from our-own-bug. Defaults keep every
    # existing constructor call valid.
    status: int|None = None      # HTTP status, None on exception/no-call
    error_kind: str = ""         # timeout|connection|http_5xx|rate_limited|unauthorized|
                                 # credit_exhausted|unconfigured|invalid_request|unknown|"" (ok)

def _classify(status, body_text=""):
    """Map an HTTP status (+error body) to the breaker's error_kind taxonomy."""
    if status in (401, 403):
        t = (body_text or "").lower()
        return "credit_exhausted" if any(w in t for w in ("credit", "billing", "quota", "insufficient")) else "unauthorized"
    if status == 429: return "rate_limited"
    if status in (400, 422): return "invalid_request"
    if status and status >= 500: return "http_5xx"
    return "unknown"

def _anthropic(messages, model, max_tokens, system, timeout=30):
    import httpx
    key=envkey("ANTHROPIC_API_KEY")   # ENVKEY-1 class, applied here too (Peer full-sweep, 31 Jul)
    if not key: return AIResult("",None,None,"anthropic",model,ok=False,error_kind="unconfigured")
    body={"model":model,"max_tokens":max_tokens,"messages":messages}
    if system: body["system"]=system
    # FAILOVER-PARITY-1 (18 Jul 2026): try/except + status/text ok-check, same rule as _scaleway.
    # Without this, an outage RAISED out of complete() and a ban/429 returned ok=True with empty
    # text — neither triggered the any-of fallback. Now both degrade to the standby lane per call.
    try:
        with httpx.Client(timeout=timeout) as c:
            r=c.post("https://api.anthropic.com/v1/messages",
                     headers={"x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"},
                     json=body)
        j=r.json()
        text=(j.get("content",[{}])[0].get("text","") or "")
        u=j.get("usage",{}) or {}
        _ok = (r.status_code==200 and bool(text))
        return AIResult(text, u.get("input_tokens"), u.get("output_tokens"), "anthropic", model,
                        ok=_ok, status=r.status_code,
                        error_kind="" if _ok else _classify(r.status_code, r.text[:300]))
    except httpx.TimeoutException:
        return AIResult("",None,None,"anthropic",model,ok=False,error_kind="timeout")
    except Exception:
        return AIResult("",None,None,"anthropic",model,ok=False,error_kind="connection")

def _to_openai_messages(messages, system):
    """Translate the app's Anthropic-style content-block messages -> OpenAI chat format.
    Anthropic block: {"role","content":[{"type":"text","text":...} | {"type":"image","source":{"type":"base64","media_type","data"}}]}
    OpenAI: {"role","content": str | [{"type":"text","text"} | {"type":"image_url","image_url":{"url":"data:<mt>;base64,<data>"}}]}"""
    out=[]
    if system: out.append({"role":"system","content":system})
    for m in messages:
        role=m.get("role","user")
        c=m.get("content")
        if isinstance(c,str):
            out.append({"role":role,"content":c}); continue
        parts=[]
        for blk in (c or []):
            t=blk.get("type")
            if t=="text":
                parts.append({"type":"text","text":blk.get("text","")})
            elif t=="image":
                src=blk.get("source",{}) or {}
                if src.get("type")=="base64":
                    url=f"data:{src.get('media_type','image/jpeg')};base64,{src.get('data','')}"
                    parts.append({"type":"image_url","image_url":{"url":url}})
        out.append({"role":role,"content":parts or ""})
    return out

def _openai(messages, model, max_tokens, system, timeout=30):
    """Real OpenAI adapter — chat/completions. Translates the app's content-block
    messages to OpenAI format, calls the API, parses text + token usage."""
    import httpx
    key=envkey("OPENAI_API_KEY")   # ENVKEY-1 class: systemd unit does not export the server .env
    if not key: return AIResult("",None,None,"openai",model,ok=False,error_kind="unconfigured")
    # gpt-5*/o* chat/completions 400-reject max_tokens ("Unsupported parameter") — they take max_completion_tokens.
    _tokkey = "max_completion_tokens" if model.startswith(("gpt-5","o")) else "max_tokens"
    body={"model":model,_tokkey:max_tokens,"messages":_to_openai_messages(messages,system)}
    # EFFORT PIN (GS-OAI-V1, 1 Aug 2026): production effort = the effort the golden set passed at.
    # Default reasoning burned the ENTIRE 120-token search-interpret budget (120 reasoning, 0 visible
    # — the 17 Jul qwen3.5 class again); reasoning_effort "none" passed every task INSIDE production
    # budgets with 0 burn. Changing this invalidates the gate tuple — re-run scripts/golden_openai_v1.py.
    if model.startswith("gpt-5"): body["reasoning_effort"]="none"
    try:
        with httpx.Client(timeout=timeout) as c:
            r=c.post("https://api.openai.com/v1/chat/completions",
                     headers={"Authorization":"Bearer "+key,"content-type":"application/json"},
                     json=body)
        j=r.json()
        text=(j.get("choices",[{}])[0].get("message",{}).get("content","") or "")
        u=j.get("usage",{}) or {}
        # FAILOVER-PARITY-1 rule (18 Jul), applied to _openai 31 Jul: 200-with-empty-text must degrade
        # to the fallback chain, not report ok — same rule as _anthropic/_scaleway.
        _ok = (r.status_code==200 and bool(text))
        return AIResult(text, u.get("prompt_tokens"), u.get("completion_tokens"), "openai", model,
                        ok=_ok, status=r.status_code,
                        error_kind="" if _ok else _classify(r.status_code, r.text[:300]))
    except httpx.TimeoutException:
        return AIResult("",None,None,"openai",model,ok=False,error_kind="timeout")
    except Exception:
        return AIResult("",None,None,"openai",model,ok=False,error_kind="connection")

def _scaleway(messages, model, max_tokens, system, timeout=30):
    """Scaleway EU adapter (P1) — OpenAI-compatible chat/completions at api.scaleway.ai.
    Key: SCALEWAY_API_KEY or FAILOVER_API_KEY (either name). Qwen reasoning models may return
    content=null with the text in message.reasoning when the thinking budget runs out —
    fall back to that field before declaring the reply empty."""
    import httpx
    key=envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY")
    if not key: return AIResult("",None,None,"scaleway",model,ok=False,error_kind="unconfigured")
    body={"model":model,"max_tokens":max_tokens,"messages":_to_openai_messages(messages,system)}
    try:
        with httpx.Client(timeout=timeout) as c:
            r=c.post("https://api.scaleway.ai/v1/chat/completions",
                     headers={"Authorization":"Bearer "+key,"content-type":"application/json"},
                     json=body)
        j=r.json()
        msg=(j.get("choices",[{}])[0].get("message",{}) or {})
        text=(msg.get("content") or "")
        if not text:  # Qwen reasoning models put the text here when the thinking budget runs out
            text=(msg.get("reasoning") or "")
        u=j.get("usage",{}) or {}
        _ok = (r.status_code==200 and bool(text))
        return AIResult(text, u.get("prompt_tokens"), u.get("completion_tokens"), "scaleway", model,
                        ok=_ok, status=r.status_code,
                        error_kind="" if _ok else _classify(r.status_code, r.text[:300]))
    except httpx.TimeoutException:
        return AIResult("",None,None,"scaleway",model,ok=False,error_kind="timeout")
    except Exception:
        return AIResult("",None,None,"scaleway",model,ok=False,error_kind="connection")

# Fallback chain order = dict order: anthropic -> openai -> scaleway
ADAPTERS={"anthropic":_anthropic,"openai":_openai,"scaleway":_scaleway}

def complete(messages, *, task="haiku", max_tokens=700, system=None, provider=None,
             timeout=30, allow_fallback=True, probe=False):
    """P2a (1 Aug 2026): breaker-aware. Chain = [requested/active] + others, minus lanes the
    breaker or the AI_DRILL_BAN overlay excludes. Attribution is recorded PER ADAPTER
    INVOCATION (Peer cost review). probe=True is the direct no-fallback trial mode —
    a probe's outcome is unambiguously the target's (Peer blocker #3). RAILS (Correction 2,
    seam part): at most one attempt per configured lane, no retries, output hard-capped by
    max_tokens — worst-case = sum of per-lane caps, computable before dispatch. Breaker
    unattached (standalone scripts) = exactly yesterday's behavior."""
    try:
        import ai_breaker as _brk
    except Exception:
        _brk = None
    prov = provider or AI_ACTIVE
    if probe:
        allow_fallback = False
    def _allowed(p):
        if _brk is None: return True
        if probe and p == prov:
            return p not in _brk.drill_banned()   # probes bypass state gates, never the drill
        return _brk.allows(p, task)
    chain = [prov] + ([p for p in ADAPTERS if p != prov] if allow_fallback else [])
    chain = [p for p in chain if ADAPTERS.get(p) and TASK_MODEL.get(p, {}).get(task)]
    open_chain = [p for p in chain if _allowed(p)]
    if not open_chain:
        return AIResult("",None,None,prov,TASK_MODEL.get(prov,{}).get(task,""),
                        ok=False, error_kind="unconfigured" if not chain else "unknown")
    res = None
    for p in open_chain:
        r = ADAPTERS[p](messages, TASK_MODEL[p][task], max_tokens, system, timeout)
        if _brk is not None:
            _brk.record(p, task, r.ok, r.error_kind or ("" if r.ok else "unknown"),
                        (r.error_kind or "")[:60], probe=probe)
        if r.ok:
            return r
        if res is None:
            res = r   # report the FIRST failure (the requested lane's) when all lanes fail
    return res
