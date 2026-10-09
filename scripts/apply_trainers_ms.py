#!/usr/bin/env python3
"""apply_trainers_ms.py -- TRAINERS-EX-1 (RUL-217) in TrustSquare (ms.js). Idempotent; refuses to apply twice.

TrustSquare's Tutors list gets one AI example per trainer role nobody real offers in the city (GET /examples/trainers),
exactly like the casual work roles in Services (GENERIC-EX-1): marked, after real adverts, hidden by the AI-examples
switch, counted on the Home tile while the switch is on, off the map, no introduction. Its tap sheet offers
'I train people in this -- list me free' into Quick's sell flow for that sport, and says what a session typically costs.
"""
import io, os, shutil, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "ms.js")
MARK = "TRAINERS-EX-1"

LOAD_OLD = "    if (added) { try { renderGrid(); } catch(e){} try { renderCatCounts(); } catch(e){} }   // GX-TILE-COUNT-1: the tile follows"
LOAD_NEW = r"""    // TRAINERS-EX-1 (RUL-217, David 8 Oct 2026: "the same for tutors, but for a branch of tutors namely Trainers ... To also
    // make it Global"): one AI example per trainer role nobody real (and no stored example) offers in this city, in Tutors.
    try {
      const tkey = 'T|' + key;
      let trows = _msGxCache.get(tkey);
      if (!trows) {
        const r2 = await fetch(BEA_URL + '/examples/trainers?country=' + encodeURIComponent(cc) + '&city=' + encodeURIComponent(city)
                               + '&lang=' + encodeURIComponent(lang)).catch(function(){ return null; });
        trows = (r2 && r2.ok) ? await r2.json().catch(function(){ return null; }) : null;
        if (Array.isArray(trows)) _msGxCache.set(tkey, trows); else trows = [];
      }
      if (seq === _msListSeq && trows.length) {
        const tHere = LISTINGS.filter(function(l){ return l.cat === 'Tutors' && !l.generic && !String(l.id).startsWith('ph_')
          && (!l.isLive || !l.city || l.city === city); });
        trows.forEach(function(row){
          const en = String(row.service_type || '');
          if (!en || LISTINGS.some(function(l){ return l.id === 'gx_' + row.role_key; })) return;
          if (tHere.some(function(l){ const t = String(l.subject || '') + ' ' + String(l.service_type || l.serviceType || '') + ' ' + String(l.title || '');
            return new RegExp('\\b' + esc(en), 'i').test(t); })) return;
          const m = _msMapBeaListing(row);
          m.id = 'gx_' + row.role_key; m.beaListingId = null; m.generic = true; m.trainer = true; m.role_key = row.role_key;
          m.typical_rate = row.typical_rate || null; m.typical_rate_source = row.typical_rate_source || null;
          m.demo_example = true; m.is_demo = 1; m.area = city || m.area; m.suburb = city || m.suburb;
          LISTINGS.push(m); added++;
        });
      }
    } catch(e) { console.warn('TRAINERS-EX-1:', e); }
""" + LOAD_OLD

CTA_OLD = "text-decoration:none;margin-bottom:8px;\">I do this work — list me free</a>'"
CTA_NEW = ("text-decoration:none;margin-bottom:8px;\">' + (l.trainer ? 'I train people in this — list me free' : 'I do this work — list me free') + '</a>'")

P_OLD = "Whoever lists this work sets their own rate.</p>'"
P_NEW = ("Whoever lists this work sets their own rate.</p>'\n"
         "    + ((l.trainer && l.typical_rate) ? '<p style=\"margin:-6px 0 14px;font-size:13px;color:var(--text-3,#6b7280);\">"
         "A session here typically costs about ' + lm(l.typical_rate.replace(' / session', '')) + ' (our estimate).</p>' : '')   // TRAINERS-EX-1")


def main():
    s = io.open(F, encoding="utf-8").read()
    if MARK in s:
        sys.exit("already applied (%s in ms.js)" % MARK)
    for a, b in ((LOAD_OLD, LOAD_NEW), (CTA_OLD, CTA_NEW), (P_OLD, P_NEW)):
        n = s.count(a)
        if n != 1:
            sys.exit("anchor found %d times, expected 1: %r" % (n, a[:80]))
        s = s.replace(a, b)
    shutil.copyfile(F, F + ".bak-trainers-%s" % time.strftime("%Y%m%d-%H%M%S"))
    io.open(F, "w", encoding="utf-8").write(s)
    print("ms.js: TRAINERS-EX-1 applied")


if __name__ == "__main__":
    main()
