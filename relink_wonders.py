#!/usr/bin/env python3
"""One-off maintenance: re-match ALL live listings against the expanded wonders.json.

Run on the SERVER from /var/www/marketsquare with the BEA venv:
    cd /var/www/marketsquare && venv/bin/python relink_wonders.py

For each live listing it:
  1. Reads existing linked_wonders.
  2. Preserves any SELLER-set entries (auto_linked == False / missing).
  3. Clears auto-linked entries, then re-runs the same matcher used at publish
     (auto_link_wonders with the new max_links=5 default), against the expanded set.
  4. Merges seller-set + new auto-linked (seller-set always kept, never overwritten).

Idempotent: safe to run more than once. Never touches seller-set wonders.
"""
import json
import main as bea  # bea_main.py is deployed as main.py on the server


def jload(raw):
    if not raw:
        return []
    try:
        v = json.loads(raw)
        return v if isinstance(v, list) else []
    except Exception:
        return []


def main():
    conn = bea.database.get_db()
    rows = conn.execute(
        "SELECT id, linked_wonders FROM listings WHERE listing_status = 'live'"
    ).fetchall()
    ids = [(r["id"], r["linked_wonders"]) for r in rows]
    conn.close()

    print(f"Live listings: {len(ids)}")
    total_auto = 0
    changed = 0
    for lid, raw in ids:
        existing = jload(raw)
        # seller-set entries are those NOT flagged auto_linked
        seller_set = [w for w in existing if isinstance(w, dict) and not w.get("auto_linked")]
        seller_ids = {w["id"] for w in seller_set if "id" in w}

        # Clear linked_wonders so the matcher (which only fills NULL/empty) will run.
        c = bea.database.get_db()
        c.execute("UPDATE listings SET linked_wonders = NULL WHERE id = ?", (lid,))
        c.commit()
        c.close()

        # Reproduce publish-time context: city lat/lon, category, derived radius.
        c = bea.database.get_db()
        city = c.execute(
            "SELECT lat, lng FROM geo_cities WHERE id = (SELECT geo_city_id FROM listings WHERE id = ?)",
            (lid,),
        ).fetchone()
        cat = c.execute("SELECT category FROM listings WHERE id = ?", (lid,)).fetchone()
        country = c.execute(
            "SELECT g.country_iso2 FROM geo_cities g JOIN listings l ON l.geo_city_id = g.id WHERE l.id = ?",
            (lid,),
        ).fetchone()
        c.close()

        auto_ids = []
        if city and city["lat"] and city["lng"]:
            iso2 = country["country_iso2"] if country else "ZA"
            radius = bea._derived_radius_km(float(city["lat"]), float(city["lng"]), iso2)
            auto_ids = bea.auto_link_wonders(
                lid,
                float(city["lat"]),
                float(city["lng"]),
                cat["category"] if cat else "",
                radius_km=radius,
            )  # uses new max_links=5 default

        # Merge: seller-set always kept; add auto-linked that aren't already seller-set.
        merged = list(seller_set)
        for wid in auto_ids:
            if wid not in seller_ids:
                merged.append({"id": wid, "auto_linked": True})

        c = bea.database.get_db()
        c.execute(
            "UPDATE listings SET linked_wonders = ? WHERE id = ?",
            (json.dumps(merged), lid),
        )
        c.commit()
        c.close()

        total_auto += len(auto_ids)
        if merged != existing:
            changed += 1
        print(f"  listing {lid}: seller={len(seller_set)} auto={len(auto_ids)} total={len(merged)}")

    print(f"\nDone. Listings changed: {changed}/{len(ids)}. "
          f"Avg auto-links: {total_auto / max(1, len(ids)):.1f}")


if __name__ == "__main__":
    main()
