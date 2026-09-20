#!/usr/bin/env python3
"""gen_role_pictures.py -- one picture of the WORK per role (RUL-157), from roles/role_registry.json.

DRY RUN BY DEFAULT: prints what it would make and the estimated spend, and spends nothing.
Spending is David's call, so a real run needs --go.

  python3 scripts/gen_role_pictures.py                      # dry run, all IN roles
  python3 scripts/gen_role_pictures.py --provider gemini --go --limit 3   # try three first
  python3 scripts/gen_role_pictures.py --provider gemini --go             # the rest
  python3 scripts/gen_role_pictures.py --only welder --redo --go          # redo one

Providers (default higgsfield; the model is a setting, never the name of a function -- swap it freely):
  higgsfield HIGGSFIELD_API_KEY (prepaid API balance) default model xai/grok-imagine-image-2.0
  gemini  GEMINI_API_KEY  (Google AI Studio key)   default model gemini-2.5-flash-image
  xai     XAI_API_KEY                               default model grok-imagine-image-2.0
  openai  OPENAI_API_KEY  (already in .env)         default model gpt-image-1
Keys are read from the environment or MarketSquare/.env and are never printed.
Existing pictures are skipped (so a stopped run resumes), unless --redo.
Every picture made is logged in roles/pictures/manifest.json (provider, model, date, prompt).
After a run: python3 scripts/role_registry_board.py  -> the contact sheet to approve.
"""
import argparse, base64, datetime, hashlib, io, json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "roles", "role_registry.json")
PICS = os.path.join(ROOT, "roles", "pictures")
MAN = os.path.join(PICS, "manifest.json")
EST_USD = {"higgsfield": 0.06, "gemini": 0.039, "xai": 0.07, "openai": 0.04}
DEFAULT_MODEL = {"higgsfield": "xai/grok-imagine-image-2.0", "gemini": "gemini-2.5-flash-image", "xai": "grok-imagine-image-2.0", "openai": "gpt-image-1"}
ENVKEY = {"higgsfield": "HIGGSFIELD_API_KEY", "gemini": "GEMINI_API_KEY", "xai": "XAI_API_KEY", "openai": "OPENAI_API_KEY"}

def key_for(provider):
    name = ENVKEY[provider]
    if os.environ.get(name): return os.environ[name]
    envf = os.path.join(ROOT, ".env")
    if os.path.exists(envf):
        for line in io.open(envf, encoding="utf-8"):
            line = line.strip()
            if line.startswith("export "): line = line[7:]
            if line.startswith(name + "="): return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def post(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=dict(headers, **{"Content-Type": "application/json"}))
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())

def generate(provider, model, key, prompt):
    if provider == "higgsfield":
        # prepaid balance, auto top-up OFF: spend stops at zero (chosen 19 Sep 2026; model compared on
        # welder / home cleaner / nanny against Soul 2, Recraft and Ideogram -- roles/pictures/_trial)
        os.environ["HF_KEY"] = key
        import higgsfield_client as hc
        res = hc.subscribe(model, arguments={"prompt": prompt, "aspect_ratio": "1:1"})
        with urllib.request.urlopen(res["images"][0]["url"], timeout=120) as r:
            return r.read()
    if provider == "gemini":
        d = post("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model,
                 {"contents": [{"parts": [{"text": prompt}]}],
                  "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}}},
                 {"x-goog-api-key": key})
        for c in d.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                if "inlineData" in p: return base64.b64decode(p["inlineData"]["data"])
        raise RuntimeError("no image in response: %s" % json.dumps(d)[:300])
    if provider == "xai":
        d = post("https://api.x.ai/v1/images/generations",
                 {"model": model, "prompt": prompt, "n": 1, "response_format": "b64_json"},
                 {"Authorization": "Bearer " + key})
        return base64.b64decode(d["data"][0]["b64_json"])
    if provider == "openai":
        d = post("https://api.openai.com/v1/images/generations",
                 {"model": model, "prompt": prompt, "size": "1024x1024", "n": 1},
                 {"Authorization": "Bearer " + key})
        return base64.b64decode(d["data"][0]["b64_json"])
    raise ValueError(provider)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--provider", default="higgsfield", choices=sorted(EST_USD))
    ap.add_argument("--model")
    ap.add_argument("--go", action="store_true", help="actually generate (spends money)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--only")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--include-later", action="store_true")
    a = ap.parse_args()
    model = a.model or DEFAULT_MODEL[a.provider]
    reg = json.load(io.open(REG, encoding="utf-8"))
    want = {"in", "later"} if a.include_later else {"in"}
    todo = [r for r in reg["roles"] if r["status"] in want and r.get("role_picture")]
    if a.only: todo = [r for r in todo if r["key"] == a.only]
    if not a.redo: todo = [r for r in todo if not os.path.exists(os.path.join(ROOT, r["role_picture"]["file"]))]
    if a.limit: todo = todo[:a.limit]
    est = len(todo) * EST_USD[a.provider]
    print("%d pictures to make with %s / %s -- estimated US$%.2f" % (len(todo), a.provider, model, est))
    if not a.go:
        for r in todo[:5]: print("  e.g. %-32s %s" % (r["key"], r["role_picture"]["prompt"][:90] + "..."))
        print("DRY RUN -- nothing spent. Add --go to generate.")
        return 0
    key = key_for(a.provider)
    if not key:
        print("NO KEY: set %s in the environment or MarketSquare/.env" % ENVKEY[a.provider]); return 2
    os.makedirs(PICS, exist_ok=True)
    man = json.load(io.open(MAN, encoding="utf-8")) if os.path.exists(MAN) else {}
    import concurrent.futures as cf
    def one(r):
        try: return r, generate(a.provider, model, key, r["role_picture"]["prompt"]), None
        except Exception as e: return r, None, str(e)[:200]
    made = 0
    with cf.ThreadPoolExecutor(max(1, a.threads)) as ex:
        for fut in cf.as_completed([ex.submit(one, r) for r in todo]):
            r, img, err = fut.result()
            if err: print("  FAIL %-30s %s" % (r["key"], err)); continue
            io.open(os.path.join(ROOT, r["role_picture"]["file"]), "wb").write(img)
            man[r["key"]] = {"provider": a.provider, "model": model, "made": datetime.datetime.now().isoformat(timespec="seconds"),
                             "prompt_sha": hashlib.sha256(r["role_picture"]["prompt"].encode()).hexdigest()[:12], "approved": False}
            io.open(MAN, "w", encoding="utf-8").write(json.dumps(man, indent=1))
            made += 1; print("  ok   %s" % r["key"], flush=True)
    print("made %d of %d" % (made, len(todo)))
    return 0 if made == len(todo) else 1

if __name__ == "__main__":
    sys.exit(main())
