#!/usr/bin/env python3
"""PHOTO-CAP-2 (David 4 Oct 2026, via Dave jnr: "up our number of photos per property to 20"). PHOTO-CAP-1 (15 Jul 2026,
David-approved after costing) already allows 24 photos for Property, Cars and places to stay and 12 elsewhere -- in the
Sell flow. The Edit screen, where every Quick listing gets its photos, kept its own hard-coded 10. One rule, one place:
msPhotoCap() holds the caps; the Sell flow and Edit both read it. Idempotent; asserts every anchor."""
import io, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, "ms.js")
s = io.open(P, encoding="utf-8", newline="").read(); n0 = len(s)
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)
s = rep(s, "function sfMaxPhotos(){\n",
           "/* PHOTO-CAP-2 (4 Oct 2026): ONE photo cap for every screen that adds photos -- PHOTO-CAP-1's numbers. */\n"
           "function msPhotoCap(cat, sub){\n"
           "  var c=String(cat||'');\n"
           "  if(/^(property|cars?)(_|$)/i.test(c)) return 24;\n"
           "  if(/accommodation|^stays?$/i.test(c) || (/^adventures?$/i.test(c) && sub==='accommodation')) return 24;\n"
           "  return 12;\n"
           "}\n"
           "function sfMaxPhotos(){\n", "msPhotoCap")
s = rep(s, "  if(sfState.cat==='Cars'||sfState.cat==='Property') return 24;\n  if(sfState.cat==='Adventures'&&sfState.sub==='accommodation') return 24;\n  return 12;\n}",
           "  return msPhotoCap(sfState.cat, sfState.sub);   /* PHOTO-CAP-2: the one rule */\n}", "sfMaxPhotos body")
s = rep(s, "  const room = 10 - _elPhotoUrls.length;\n  if (room <= 0) { showToast('Maximum 10 photos'); inp.value = ''; return; }",
           "  const _cap = msPhotoCap(elCurrentCat);   // PHOTO-CAP-2: Edit obeys PHOTO-CAP-1 (24 property/cars/stays, 12 elsewhere) -- was a hard 10\n"
           "  const room = _cap - _elPhotoUrls.length;\n  if (room <= 0) { showToast('Maximum ' + _cap + ' photos'); inp.value = ''; return; }", "edit room")
s = rep(s, "  if (leftOut > 0) _tail += ' — ' + leftOut + ' left out (10-photo maximum)';",
           "  if (leftOut > 0) _tail += ' — ' + leftOut + ' left out (' + _cap + '-photo maximum)';", "edit tail")
io.open(P, "w", encoding="utf-8", newline="").write(s)
assert io.open(P, encoding="utf-8", newline="").read() == s
print("PHOTO-CAP-2 applied: ms.js %d -> %d chars" % (n0, len(s)))
