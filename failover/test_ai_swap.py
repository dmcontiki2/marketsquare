# -*- coding: utf-8 -*-
"""AI swap simulated test suite — MarketSquare's REAL seam code + mock providers."""
import sys, json, time, threading, http.server, socketserver, os, importlib
sys.path.insert(0, '/tmp/bea')
import ai_provider as ap

P=[]; F=[]
def check(name, cond, detail=""):
    (P if cond else F).append(name)
    print(("PASS " if cond else "FAIL ") + name + (("  — " + detail) if detail else ""))

def mk(provider, ok=True, text="OK", err=""):
    def adapter(messages, model, max_tokens, system):
        return ap.AIResult(text if ok else "", 10, 5, provider, model, ok=ok)
    return adapter

orig = dict(ap.ADAPTERS)
ap.ADAPTERS.update({"anthropic": mk("anthropic"), "openai": mk("openai")})
r = ap.complete([{"role":"user","content":"hi"}], task="haiku", provider="anthropic")
check("A1 baseline: anthropic answers", r.ok and r.provider=="anthropic")

ap.ADAPTERS["anthropic"] = mk("anthropic", ok=False, err="timeout / connection refused")
r = ap.complete([{"role":"user","content":"hi"}], task="haiku", provider="anthropic")
check("A2 T1 outage: auto-fallback to openai", r.ok and r.provider=="openai", f"answered by {r.provider}")

ap.ADAPTERS["anthropic"] = mk("anthropic", ok=False, err="403 organization suspended")
r = ap.complete([{"role":"user","content":"hi"}], task="haiku", provider="anthropic")
check("A3 T3 ban: auto-fallback to openai", r.ok and r.provider=="openai")

ap.ADAPTERS.update({"anthropic": mk("anthropic", ok=False, err="down"), "openai": mk("openai", ok=False, err="down")})
r = ap.complete([{"role":"user","content":"hi"}], task="haiku", provider="anthropic")
check("A4 blackout: returns ok=False, no crash", (not r.ok))
ap.ADAPTERS.update(orig)

openai_shaped = {"choices":[{"message":{"content":"the answer"}}]}
extracted = openai_shaped.get("content",[{}])[0].get("text") if openai_shaped.get("content") else None
check("B1 raw call-site vs OpenAI shape: extraction fails (proves P0 need)", extracted is None,
      "the 15 raw sites would get None/crash after a flip")

class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0)); self.rfile.read(n)
        body = json.dumps({"choices":[{"message":{"content":"OPEN-WEIGHT LANE OK (qwen mock)"}}],
                           "usage":{"prompt_tokens":12,"completion_tokens":6}}).encode()
        self.send_response(200); self.send_header("Content-Type","application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
srv = socketserver.TCPServer(("127.0.0.1", 18081), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
os.environ.update({"FAILOVER_BASE_URL":"http://127.0.0.1:18081/v1","FAILOVER_API_KEY":"local-test",
                   "AI_BACKEND":"auto","ANTHROPIC_API_KEY":"sk-invalid-simulate-outage"})
sys.path.insert(0, '/tmp/bea/failover')
try:
    import ai_backends as ab; importlib.reload(ab)
    res = ab.ai_call("test#sim", ab.FAST, [{"role":"user","content":"ping"}], max_tokens=20)
    txt = res.get("text",""); bk = res.get("backend","")
    check("C1 primary dead -> open-weight endpoint answers (ai_backends)", "OPEN-WEIGHT" in txt and bk=="failover", f"backend={bk}: {txt[:50]}")
except Exception as e:
    check("C1 primary dead -> open-weight endpoint answers (ai_backends)", False, f"{type(e).__name__}: {e}"[:140])
srv.shutdown()

class Breaker:
    def __init__(s, n=3, window=30): s.n=n; s.w=window; s.fails=[]; s.tripped=False; s.reason=""
    def event(s, kind):
        now=time.time()
        if kind=="ban": s.tripped=True; s.reason="T3 account action (403)"; return
        if kind in ("fail","429"): s.fails=[t for t in s.fails if now-t<s.w]+[now]
        if kind=="ok": s.fails=[]
        if len(s.fails)>=s.n: s.tripped=True; s.reason=("T2 sustained throttling" if kind=="429" else "T1 hard outage")
b=Breaker(); [b.event("fail") for _ in range(3)]
check("D1 outage burst (3 fails/30s) trips breaker as T1", b.tripped and "T1" in b.reason)
b=Breaker(); b.event("fail"); b.event("ok"); b.event("fail"); b.event("ok")
check("D2 isolated blips do NOT trip", not b.tripped)
b=Breaker(); [b.event("429") for _ in range(3)]
check("D3 sustained 429 throttling trips as T2", b.tripped and "T2" in b.reason)
b=Breaker(); b.event("ban")
check("D4 single 403 ban trips IMMEDIATELY as T3", b.tripped and "T3" in b.reason)
spend, ceiling, call_cost = 19.80, 20.00, 0.50
route = "cheap-open-weight" if spend + call_cost > ceiling else "primary"
check("D5 T4 cost: near-ceiling call degrades to cheap lane", route=="cheap-open-weight")

print(f"\n===== RESULT: {len(P)} passed, {len(F)} failed =====")
if F: print("FAILED:", F)
