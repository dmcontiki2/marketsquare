#!/usr/bin/env python3
"""role_registry_board.py -- roles/role_registry.json -> roles/ROLE_REGISTRY.html (the visual + picture
contact sheet) and roles/role_picture_prompts.txt (for pasting into the Gemini or Grok app by hand).
Re-run after every build_role_registry.py or gen_role_pictures.py run."""
import html, io, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
reg = json.load(io.open(os.path.join(ROOT, "roles", "role_registry.json"), encoding="utf-8"))
roles = reg["roles"]
man_p = os.path.join(ROOT, "roles", "pictures", "manifest.json")
man = json.load(io.open(man_p, encoding="utf-8")) if os.path.exists(man_p) else {}
E = html.escape
import base64
def thumb(path):  # embedded so the board works from the Visuals gallery copy too
    from PIL import Image
    b = io.BytesIO(); Image.open(path).convert("RGB").resize((320, 320)).save(b, "JPEG", quality=78)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
def card(r):
    st = r["status"]; g = r.get("gate")
    pic = r.get("role_picture"); has = pic and os.path.exists(os.path.join(ROOT, pic["file"]))
    if has: img = '<img src="%s" alt="">' % thumb(os.path.join(ROOT, pic["file"]))
    elif pic: img = '<div class="ph" title="%s">picture to make</div>' % E(pic["prompt"])
    else: img = '<div class="ph out">no picture</div>'
    badges = ""
    if g: badges += '<span class="b %s">%s</span>' % ("clr" if g["type"] == "police_clearance" else "lic",
            "clearance gate" if g["type"] == "police_clearance" else "licence: " + ", ".join(g["licences"]).replace("_", " "))
    if r.get("aliases"): badges += '<span class="b al">also: %s</span>' % E(", ".join(r["aliases"]))
    if r.get("merged_into"): badges += '<span class="b al">now: %s</span>' % E(r["merged_into"].replace("_", " "))
    if r.get("routed_to"): badges += '<span class="b al">position lane (RUL-124)</span>'
    if r.get("split"): badges += '<span class="b al">split into real trades</span>'
    ok = man.get(r["key"], {}).get("approved")
    return ('<div class="c %s %s">%s<div class="t"><b>%s</b><i>%s</i><span class="s">%s%s</span>%s</div></div>'
            % (st, r["service_class"].lower(), img, E(r["label"]["en"]), E(r["label"].get("af") or ""),
               st.upper(), " · approved" if ok else "", badges))
sec = ""
for cls in ("Casuals", "Technical"):
    rs = [r for r in roles if r["service_class"] == cls]
    groups = []
    for r in rs:
        if r["group"] not in groups: groups.append(r["group"])
    sec += '<h2 class="%s">Services — %s <small>%d IN · %d LATER · %d OUT</small></h2>' % (
        cls.lower(), cls, *[sum(1 for r in rs if r["status"] == s) for s in ("in", "later", "out")])
    for g in groups:
        sec += '<h3>%s</h3><div class="grid">%s</div>' % (E(g), "".join(card(r) for r in rs
               if r["group"] == g and r["status"] != "out"))
        outs = [r for r in rs if r["group"] == g and r["status"] == "out"]
        if outs: sec += '<div class="grid small">%s</div>' % "".join(card(r) for r in outs)
n_in = reg["counts"]["in"]; n_pics = sum(1 for r in roles if r.get("role_picture") and r["status"] == "in"
       and os.path.exists(os.path.join(ROOT, r["role_picture"]["file"])))
page = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Role Registry</title><style>
:root{--bg:#0e1411;--fg:#e8efe9;--mut:#8fa39a;--cas:#16A97C;--tech:#3b82c4;--in:#22c55e;--later:#f59e0b;--out:#6b7280;--clr:#a855f7;--lic:#0ea5e9;--card:#16201b}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.4 system-ui,sans-serif;padding:16px}
h1{margin:0 0 4px}p.sub{color:var(--mut);margin:0 0 12px}
.key span{display:inline-block;margin:2px 8px 2px 0;padding:2px 8px;border-radius:10px;font-size:12px}
h2{margin:28px 0 4px;padding:6px 10px;border-radius:8px}h2.casuals{background:#0b3326;border-left:6px solid var(--cas)}h2.technical{background:#0c2233;border-left:6px solid var(--tech)}
h2 small{color:var(--mut);font-weight:400;margin-left:8px}h3{margin:16px 0 6px;color:var(--mut);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}.grid.small{margin-top:8px;opacity:.55}
.c{background:var(--card);border-radius:10px;overflow:hidden;border-top:4px solid var(--in)}.c.later{border-top-color:var(--later)}.c.out{border-top-color:var(--out)}
.c img,.ph{width:100%;aspect-ratio:1;object-fit:cover;display:block}.ph{display:flex;align-items:center;justify-content:center;background:#1d2a24;color:var(--mut);font-size:12px;cursor:help}.ph.out{cursor:default}
.casuals .ph{background:#10271f}.technical .ph{background:#10202d}
.t{padding:6px 8px}.t b{display:block}.t i{display:block;color:var(--mut);font-size:12px}.s{font-size:11px;color:var(--mut)}
.b{display:block;margin-top:4px;padding:1px 6px;border-radius:8px;font-size:11px;width:fit-content}.b.clr{background:var(--clr);color:#fff}.b.lic{background:var(--lic);color:#012}.b.al{background:#2a3631;color:var(--mut)}
</style></head><body><h1>Role Registry</h1>
<p class="sub">Generated from ROLE_SLATE_REVIEW.md by scripts/build_role_registry.py · @N@ roles · role pictures made: @P@ of @I@ IN · hover a grey square to read its prompt</p>
<div class="key"><span style="background:var(--cas);color:#012">Casuals</span><span style="background:var(--tech);color:#012">Technical</span><span style="border:2px solid var(--in)">IN</span><span style="border:2px solid var(--later)">LATER</span><span style="border:2px solid var(--out)">OUT</span><span style="background:var(--clr)">police-clearance gate (RUL-153)</span><span style="background:var(--lic);color:#012">licence gate (RUL-156)</span></div>
@SEC@</body></html>"""
page = page.replace("@N@", str(len(roles))).replace("@P@", str(n_pics)).replace("@I@", str(n_in)).replace("@SEC@", sec)
io.open(os.path.join(ROOT, "roles", "ROLE_REGISTRY.html"), "w", encoding="utf-8").write(page)
lines = []
for r in roles:
    if r["status"] in ("in", "later") and r.get("role_picture"):
        lines.append("### %s  [%s]  -> save as roles/pictures/%s.png\n%s\n" % (r["label"]["en"], r["status"].upper(), r["key"], r["role_picture"]["prompt"]))
io.open(os.path.join(ROOT, "roles", "role_picture_prompts.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("wrote roles/ROLE_REGISTRY.html (%d/%d pictures) and roles/role_picture_prompts.txt (%d prompts)" % (n_pics, n_in, len(lines)))
