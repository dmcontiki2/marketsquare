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

# abstract task tier -> per-provider model string (vendor names live HERE, not at call sites)
TASK_MODEL = {
    "anthropic": {"haiku":"claude-haiku-4-5-20251001","sonnet":"claude-sonnet-4-6",
                  "vision":"claude-haiku-4-5-20251001","triage":"claude-haiku-4-5-20251001"},
    # STALE 2024-era ids — VERIFY against current OpenAI catalog when OPENAI_API_KEY is provisioned (vendor doc gate: golden-set eval before production traffic)
    "openai":    {"haiku":"gpt-4o-mini","sonnet":"gpt-4o","vision":"gpt-4o","triage":"gpt-4o-mini"},
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
    with httpx.Client(timeout=timeout) as c:
        r=c.post("https://api.anthropic.com/v1/messages",
                 headers={"x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"},
                 json=body)
    j=r.json()
    text=(j.get("content",[{}])[0].get("text","") or "")
    u=j.get("usage",{}) or {}
    return AIResult(text, u.get("input_tokens"), u.get("output_tokens"), "anthropic", model)

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

ADAPTERS={"anthropic":_anthropic,"openai":_openai}

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
