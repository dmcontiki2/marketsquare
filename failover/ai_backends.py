"""
failover/ai_backends.py - Phase 0 provider-agnostic AI adapter (TrustSquare).

One entry point, ai_call(), sits behind the model-tier constants so every Cloud
AI call can run on the PRIMARY backend (Anthropic / Claude) or transparently fall
over to a FAILOVER backend (any OpenAI-compatible endpoint - e.g. a vLLM server
serving an open-weight model), selected by config, with automatic fallback.

No model weights live here; this is a thin shim. Standard library only, so it
runs anywhere with zero new dependencies.

Wiring into bea_main.py - replace each raw
    requests.post("https://api.anthropic.com/v1/messages", ...)
site with:

    from failover import ai_backends as ai
    r = ai.ai_call(
        endpoint="ai_price_check", tier=ai.REASON,
        messages=[{"role": "user", "content": prompt}], max_tokens=600,
        hooks=ai.Hooks(ceiling=_check_cost_ceiling, spend=_log_ai_spend),
        email=email)
    text = r["text"]

Environment config:
    AI_BACKEND         = auto | primary | failover      (default: auto)
    AI_DRYRUN          = 1  -> force $0 dry-run everywhere
    ANTHROPIC_API_KEY  = ...                            (primary)
    FAILOVER_BASE_URL  = http://host:8000               (OpenAI-compatible)
    FAILOVER_API_KEY   = ...                            (optional)
    FAILOVER_MODEL_FAST / _VISION / _REASON / _REASON_VISION   (override model ids)
"""
from __future__ import annotations
import json
import os
import urllib.request

# -- capability tiers (mirror the audit) -----------------------------------
FAST = "fast"                    # Haiku-class text
FAST_VISION = "fast_vision"      # Haiku-class vision
REASON = "reason"                # Sonnet-class reasoning (text)
REASON_VISION = "reason_vision"  # Sonnet-class vision

# Sonnet-class model ids, named so the cost sweep records them as justified
# constants (P1: same Sonnet the metered bea_main endpoints use; not a new tier).
REASON_MODEL = "claude-sonnet-4-6"         # cost-ok: failover REASON tier, metered endpoints only
REASON_VISION_MODEL = "claude-sonnet-4-6"  # cost-ok: failover REASON_VISION tier, metered endpoints only

PRIMARY_MODEL = {
    FAST: "claude-haiku-4-5-20251001",
    FAST_VISION: "claude-haiku-4-5-20251001",
    REASON: REASON_MODEL,
    REASON_VISION: REASON_VISION_MODEL,
}

# Failover defaults (open-weight, served via an OpenAI-compatible endpoint).
FAILOVER_MODEL = {
    FAST: os.getenv("FAILOVER_MODEL_FAST", "qwen3-32b"),
    FAST_VISION: os.getenv("FAILOVER_MODEL_VISION", "qwen3-vl"),
    REASON: os.getenv("FAILOVER_MODEL_REASON", "deepseek-v4"),
    REASON_VISION: os.getenv("FAILOVER_MODEL_REASON_VISION", "qwen3-vl-large"),
}


class Hooks:
    """Optional cost-compliance hooks; map to bea_main._check_cost_ceiling / _log_ai_spend."""

    def __init__(self, ceiling=None, spend=None):
        self.ceiling = ceiling   # callable() -> bool  (True = ok to spend)
        self.spend = spend       # callable(email, endpoint, model_key, in_tok, out_tok)


def _post(url, payload, headers, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _to_anthropic(messages):
    """Split an OpenAI-style message list into (system_str, messages_without_system)."""
    system = " ".join(
        m["content"] for m in messages
        if m.get("role") == "system" and isinstance(m.get("content"), str)
    )
    msgs = [m for m in messages if m.get("role") != "system"]
    return system, msgs


def _block_to_openai(b):
    """Translate one Anthropic content block to its OpenAI-compatible form."""
    if isinstance(b, dict) and b.get("type") == "image":
        s = b.get("source", {}) or {}
        if s.get("type") == "base64":
            url = "data:%s;base64,%s" % (s.get("media_type", "image/jpeg"), s.get("data", ""))
            return {"type": "image_url", "image_url": {"url": url}}
    return b  # text blocks share the same {"type":"text","text":...} shape


def _to_openai(messages):
    """Return messages with Anthropic image blocks converted for an OpenAI-compatible endpoint."""
    out = []
    for m in messages:
        c = m.get("content")
        if isinstance(c, list):
            out.append({**m, "content": [_block_to_openai(b) for b in c]})
        else:
            out.append(m)
    return out


def _inject_images(messages, images):
    """Append base64 image blocks (Anthropic shape) to the last user message.

    `images` = iterable of {"media_type": "...", "data": "<base64>"}; callers that
    already embed image blocks in `messages` don't need this.
    """
    blocks = [{"type": "image", "source": {"type": "base64",
              "media_type": im.get("media_type", "image/jpeg"), "data": im.get("data", "")}}
              for im in images]
    msgs = [dict(m) for m in messages]
    for m in reversed(msgs):
        if m.get("role") == "user":
            c = m.get("content")
            if isinstance(c, str):
                m["content"] = [{"type": "text", "text": c}] + blocks
            elif isinstance(c, list):
                m["content"] = list(c) + blocks
            else:
                m["content"] = blocks
            return msgs
    msgs.append({"role": "user", "content": blocks})
    return msgs


def _call_primary(tier, messages, max_tokens):
    key = os.environ["ANTHROPIC_API_KEY"]
    system, msgs = _to_anthropic(messages)
    payload = {"model": PRIMARY_MODEL[tier], "max_tokens": max_tokens, "messages": msgs}
    if system:
        payload["system"] = system
    out = _post(
        "https://api.anthropic.com/v1/messages", payload,
        {"content-type": "application/json", "x-api-key": key,
         "anthropic-version": "2023-06-01"},
    )
    text = "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text")
    u = out.get("usage", {})
    return {"text": text, "backend": "primary", "model": PRIMARY_MODEL[tier],
            "in_tokens": u.get("input_tokens"), "out_tokens": u.get("output_tokens")}


def _call_failover(tier, messages, max_tokens):
    base = os.environ["FAILOVER_BASE_URL"].rstrip("/")
    key = os.getenv("FAILOVER_API_KEY", "-")
    payload = {"model": FAILOVER_MODEL[tier], "max_tokens": max_tokens, "messages": _to_openai(messages)}
    out = _post(
        base + "/v1/chat/completions", payload,
        {"content-type": "application/json", "authorization": "Bearer " + key},
    )
    text = out["choices"][0]["message"]["content"]
    u = out.get("usage", {})
    return {"text": text, "backend": "failover", "model": FAILOVER_MODEL[tier],
            "in_tokens": u.get("prompt_tokens"), "out_tokens": u.get("completion_tokens")}


def ai_call(endpoint, tier, messages, max_tokens=512, *, images=None,
            dry_run=False, dry_run_payload=None, hooks=None, email=None):
    """Provider-agnostic AI call.

    Returns {text, backend, model, in_tokens, out_tokens}. Tries the configured
    backend order (auto = primary then failover) and returns the first success.
    """
    if tier not in PRIMARY_MODEL:
        raise ValueError("unknown tier: %r" % (tier,))

    if images:
        messages = _inject_images(messages, images)

    if dry_run or os.getenv("AI_DRYRUN") == "1":
        body = dry_run_payload if dry_run_payload is not None else {"ok": True}
        return {"text": json.dumps(body), "backend": "dryrun",
                "model": "(dry-run:%s)" % tier, "in_tokens": 0, "out_tokens": 0}

    if hooks and hooks.ceiling and not hooks.ceiling():
        raise RuntimeError("cost ceiling reached - refusing live AI call")

    mode = os.getenv("AI_BACKEND", "auto")
    order = {"primary": ["primary"], "failover": ["failover"],
             "auto": ["primary", "failover"]}.get(mode, ["primary", "failover"])

    last = None
    for backend in order:
        try:
            fn = _call_primary if backend == "primary" else _call_failover
            r = fn(tier, messages, max_tokens)
            if hooks and hooks.spend:
                try:
                    hooks.spend(email, endpoint, r["model"], r.get("in_tokens"), r.get("out_tokens"))
                except Exception:
                    pass  # spend logging must never break a serving path
            return r
        except Exception as e:  # noqa: BLE001 - try the next backend
            last = e
            continue
    raise RuntimeError("all AI backends failed for %s (%s): %s" % (endpoint, tier, last))
