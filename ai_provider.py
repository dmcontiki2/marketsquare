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
    # STALE 2024-era ids — VERIFY against current OpenAI catalog when OPENAI_API_KEY is provisioned (vendor doc gate: golden-set eval before production traffic)
    "openai":    {"haiku":"gpt-4o-mini","sonnet":"gpt-4o","vision":"gpt-4o","triage":"gpt-4o-mini"},
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

def _anthropic(messages, model, max_tokens, system, timeout=30):
    import httpx
    key=os.getenv("ANTHROPIC_API_KEY")
    if not key: return AIResult("",None,None,"anthropic",model,ok=False)
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
        return AIResult(text, u.get("input_tokens"), u.get("output_tokens"), "anthropic", model,
                        ok=(r.status_code==200 and bool(text)))
    except Exception:
        return AIResult("",None,None,"anthropic",model,ok=False)

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
    key=os.getenv("OPENAI_API_KEY")
    if not key: return AIResult("",None,None,"openai",model,ok=False)
    body={"model":model,"max_tokens":max_tokens,"messages":_to_openai_messages(messages,system)}
    try:
        with httpx.Client(timeout=timeout) as c:
            r=c.post("https://api.openai.com/v1/chat/completions",
                     headers={"Authorization":"Bearer "+key,"content-type":"application/json"},
                     json=body)
        j=r.json()
        text=(j.get("choices",[{}])[0].get("message",{}).get("content","") or "")
        u=j.get("usage",{}) or {}
        return AIResult(text, u.get("prompt_tokens"), u.get("completion_tokens"), "openai", model,
                        ok=bool(text) or r.status_code==200)
    except Exception:
        return AIResult("",None,None,"openai",model,ok=False)

def _scaleway(messages, model, max_tokens, system, timeout=30):
    """Scaleway EU adapter (P1) — OpenAI-compatible chat/completions at api.scaleway.ai.
    Key: SCALEWAY_API_KEY or FAILOVER_API_KEY (either name). Qwen reasoning models may return
    content=null with the text in message.reasoning when the thinking budget runs out —
    fall back to that field before declaring the reply empty."""
    import httpx
    key=envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY")
    if not key: return AIResult("",None,None,"scaleway",model,ok=False)
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
        return AIResult(text, u.get("prompt_tokens"), u.get("completion_tokens"), "scaleway", model,
                        ok=(r.status_code==200 and bool(text)))
    except Exception:
        return AIResult("",None,None,"scaleway",model,ok=False)

# Fallback chain order = dict order: anthropic -> openai -> scaleway
ADAPTERS={"anthropic":_anthropic,"openai":_openai,"scaleway":_scaleway}

def complete(messages, *, task="haiku", max_tokens=700, system=None, provider=None, timeout=30):
    prov = provider or AI_ACTIVE
    model = TASK_MODEL.get(prov,{}).get(task) or TASK_MODEL["anthropic"]["haiku"]
    fn = ADAPTERS.get(prov)
    if not fn: return AIResult("",None,None,prov,model,ok=False)
    res = fn(messages, model, max_tokens, system, timeout)
    # any-of fallback: if the active provider is unavailable, try the others in order (feeds-style)
    if not res.ok:
        for alt in [p for p in ADAPTERS if p!=prov]:
            m=TASK_MODEL.get(alt,{}).get(task)
            if not m: continue
            r2=ADAPTERS[alt](messages,m,max_tokens,system,timeout)
            if r2.ok: return r2
    return res
