#!/usr/bin/env python3
"""023_relink_wonders_railexp.py — HERITAGE-RAIL-1 (18 Aug 2026): re-match live
listings against the expanded wonders.json (332 -> 351; +19 sites along The Ghan,
the Great British Rail Journey and the Great American Crossing).

Same logic as the root relink_wonders.py (May expansion), embedded so it rides the
ONE deploy — relink_wonders.py itself is not in the manifest and never lands here.
Idempotent and safe to re-run: seller-set links are ALWAYS preserved; only
auto-linked entries are cleared and re-matched with the publish-time matcher.
"""
import json, sys

APPLY = "--apply" in sys.argv

def main():
    try:
        import main as bea  # CWD = live web root per the migrations contract
    except Exception as e:
        print("[023_relink] REFUSE: cannot import main (%s)" % e); return 3

    conn = bea.database.get_db()
    rows = conn.execute(
        "SELECT id, linked_wonders FROM listings WHERE listing_status = 'live'"
    ).fetchall()
    ids = [(r["id"], r["linked_wonders"]) for r in rows]
    conn.close()

    wonders = bea._load_wonders()
    print("[023_relink] catalog: %d wonders; live listings: %d" % (len(wonders), len(ids)))
    if len(wonders) < 351:
        print("[023_relink] REFUSE: catalog still has %d entries — expanded "
              "wonders.json has not landed; retry next deploy" % len(wonders)); return 3
    if not APPLY:
        print("[023_relink] dry-run OK: would re-match %d live listings" % len(ids)); return 0

    def jload(raw):
        if not raw: return []
        try:
            v = json.loads(raw); return v if isinstance(v, list) else []
        except Exception: return []

    total_auto = changed = 0
    for lid, raw in ids:
        existing = jload(raw)
        seller_set = [w for w in existing if isinstance(w, dict) and not w.get("auto_linked")]
        seller_ids = {w["id"] for w in seller_set if "id" in w}

        c = bea.database.get_db()
        c.execute("UPDATE listings SET linked_wonders = NULL WHERE id = ?", (lid,))
        c.commit(); c.close()

        c = bea.database.get_db()
        city = c.execute(
            "SELECT lat, lng FROM geo_cities WHERE id = (SELECT geo_city_id FROM listings WHERE id = ?)",
            (lid,)).fetchone()
        cat = c.execute("SELECT category FROM listings WHERE id = ?", (lid,)).fetchone()
        country = c.execute(
            "SELECT g.country_iso2 FROM geo_cities g JOIN listings l ON l.geo_city_id = g.id WHERE l.id = ?",
            (lid,)).fetchone()
        c.close()

        auto_ids = []
        if city and city["lat"] and city["lng"]:
            iso2 = country["country_iso2"] if country else "ZA"
            radius = bea._derived_radius_km(float(city["lat"]), float(city["lng"]), iso2)
            auto_ids = bea.auto_link_wonders(lid, float(city["lat"]), float(city["lng"]),
                                             cat["category"] if cat else "", radius_km=radius)

        merged = list(seller_set)
        for wid in auto_ids:
            if wid not in seller_ids:
                merged.append({"id": wid, "auto_linked": True})

        c = bea.database.get_db()
        c.execute("UPDATE listings SET linked_wonders = ? WHERE id = ?",
                  (json.dumps(merged), lid))
        c.commit(); c.close()

        total_auto += len(auto_ids)
        if merged != existing:
            changed += 1

    print("[023_relink] applied: %d/%d listings changed; avg auto-links %.1f"
          % (changed, len(ids), total_auto / max(1, len(ids))))
    return 0

if __name__ == "__main__":
    sys.exit(main())
