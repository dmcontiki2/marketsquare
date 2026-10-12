#!/usr/bin/env python3
"""LM-THUMBS-1 (David, 12 Oct 2026 05:40, on the Bee Lady's honey advert #273: "Did Marietjie remove these photos or was
it lost in going live?").

Neither: all 15 photos were on the advert. The Local Market advert page showed one big photo and two arrows, with no
row of small pictures, so 15 photos read as one. Every other advert page has the row (CARS-SPEC-1's shared gallery
strip). The Local Market page now carries the same row, wired to the same two functions.

Usage:  python3 apply_lm_thumbs.py <repo>      Idempotent; asserts every anchor; honours the work lock."""
import io, os, re, subprocess, sys

R = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["ms.js", "scripts/regression_ledger.py"]
if "--no-lock" not in sys.argv:
    lk = subprocess.run([sys.executable, os.path.join(R, "scripts", "work_lock.py"), "check"] + FILES, cwd=R,
                        capture_output=True, text=True)
    if lk.returncode == 3:
        print("STAND-OFF (RUL-140): " + lk.stdout.strip().splitlines()[0]); sys.exit(3)

def load(rel):
    return io.open(os.path.join(R, rel), encoding="utf-8", newline="").read()

def save(rel, s):
    p = os.path.join(R, rel)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    assert io.open(p, encoding="utf-8", newline="").read() == s, "write-back of %s did not read back identical" % rel

def rep(s, a, b, name):
    if b in s:
        return s
    assert s.count(a) == 1, "anchor %s: found %d times" % (name, s.count(a))
    return s.replace(a, b)

s = load("ms.js"); n0 = len(s)
s = rep(s, '''    const heroHtml =
      `<div class="photo-strip-wrap" id="pstrip-wrap-${lmStripId}">` +
        `<div class="photo-strip" id="pstrip-${lmStripId}" onscroll="updateStripDots('${lmStripId}',${lmPhotos.length})">` +
          lmSlides +
        `</div>` +
        lmDotsHtml + lmArrows +
''', '''    // LM-THUMBS-1 (12 Oct 2026, David on the Bee Lady's honey advert: "Did Marietjie remove these photos or was it lost
    // in going live?"): this page showed one big photo and two arrows, so 15 photos read as one. It now carries the same
    // row of small pictures as every other advert page (the shared gallery strip -- galThumbClick / syncGalThumbs).
    const lmThumbs = lmPhotos.length > 1
      ? '<div class="adv-thumbs" id="adv-thumbs-' + lmStripId + '">' + lmPhotos.map(function(u, ti){ return '<div class="adv-thumb' + (ti===0?' active':'') + '" id="adv-thumb-' + lmStripId + '-' + ti + '" onclick="advThumbClick(\\'' + lmStripId + '\\',' + ti + ')"><img src="' + _lmEsc(u) + '" alt="" loading="lazy"></div>'; }).join('') + '</div>'
      : '';
    const heroHtml =
      `<div class="photo-strip-wrap" id="pstrip-wrap-${lmStripId}">` +
        `<div class="photo-strip" id="pstrip-${lmStripId}" onscroll="updateStripDots('${lmStripId}',${lmPhotos.length}); if(typeof syncAdvThumbs==='function') syncAdvThumbs('${lmStripId}', Math.round(this.scrollLeft/this.offsetWidth))">` +
          lmSlides +
        `</div>` +
        lmDotsHtml + lmArrows + lmThumbs +
''', "lm hero")
save("ms.js", s)

g = load("scripts/regression_ledger.py")
if "LM-THUMBS-1 (David, 12 Oct 2026)" not in g:
    nums = [int(x) for x in re.findall(r"@entry\(.RG-(\d{4}).", g)]
    rid = "RG-%04d" % (max(nums) + 1)
    ENTRY = '''

@entry("%s", "LM-THUMBS-1 (David, 12 Oct 2026): a Local Market advert shows its row of small pictures like every other advert "
       "page -- the Bee Lady's honey advert had 15 photos and read as one ('did Marietjie remove these photos?')",
       OPEN, fixed_on="2026-10-12",
       scope="ms.js lmOpenDetail: the adv-thumbs row under the big photo, wired to advThumbClick / syncAdvThumbs (shared gallery strip).",
       ref="David 12 Oct 2026 05:40 with a screenshot of #273. All 15 photos were stored and served; only the row was missing.")
def rg_lm_thumbs_1():
    js = repo_file("ms.js")
    if js is None:
        return [(INFO, "NOT EVALUATED - repo not readable from here")]
    i = js.find("async function lmOpenDetail(")
    body = js[i:i + 9000] if i >= 0 else ""
    out = []
    if "id=\\"adv-thumbs-' + lmStripId" not in body or "lmDotsHtml + lmArrows + lmThumbs" not in body:
        out.append((FAIL, "a Local Market advert with many photos shows one big photo and no row of small pictures again"))
    if "syncAdvThumbs('${lmStripId}'" not in body:
        out.append((FAIL, "the Local Market row of small pictures no longer follows the big photo"))
    if "function galThumbClick(" not in js or "function syncGalThumbs(" not in js:
        out.append((FAIL, "the shared gallery strip functions are gone"))
    return out or [(INFO, "a Local Market advert carries the row of small pictures")]
''' % rid
    a = "\n\ndef _server_vantage_wrap():"
    assert g.count(a) == 1, "anchor ledger tail: %d" % g.count(a)
    g = g.replace(a, ENTRY.rstrip("\n") + "\n" + a)
    print("ledger entry", rid)
compile(g, "regression_ledger.py", "exec"); save("scripts/regression_ledger.py", g)
print("LM-THUMBS-1 applied: ms.js %d -> %d chars" % (n0, len(s)))
