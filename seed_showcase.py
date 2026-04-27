"""
seed_showcase.py
================
Creates 12 aspirational showcase listings on the BEA and adds each to the
wishlist_showcase table for the empty-state feed.

Run once on the server:
    python seed_showcase.py

Requires: requests  (pip install requests  or use venv)
API key:  reads from BEA_API_KEY env var or falls back to the dev key below.
"""

import os
import sys
import sqlite3
import requests
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL  = "http://localhost:8000"
API_KEY   = os.getenv("BEA_API_KEY", "ms_mk_2026_pretoria_admin")
DB_PATH   = os.getenv("MS_DB_PATH") or next(
    (p for p in [
        "/var/www/marketsquare/marketsquare.db",
        "/var/www/marketsquare/data/marketsquare.db",
        "/var/www/marketsquare/db/marketsquare.db",
    ] if os.path.exists(p)),
    None
)
HEADERS   = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

# ── Showcase listings ─────────────────────────────────────────────────────────
LISTINGS = [
    {
        "title": "1933 Double Eagle Gold Coin — Extremely Rare",
        "price": "R2 800 000",
        "category": "Collectors",
        "city": "Pretoria",
        "suburb": "Waterkloof",
        "description": "One of the most sought-after gold coins in the world. 1933 US Double Eagle, graded MS-65. Full provenance documentation available. Serious collectors only.",
        "trust_score": 95,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "Rolex Submariner Date Ref. 16610 — Full Set",
        "price": "R185 000",
        "category": "Collectors",
        "city": "Pretoria",
        "suburb": "Brooklyn",
        "description": "2002 Rolex Submariner Date in stainless steel. Full set — original box, papers, hangtags. Serviced 2023. Condition 9/10. A grail piece for serious watch collectors.",
        "trust_score": 92,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "Penny Black 1840 — First Adhesive Postage Stamp",
        "price": "R95 000",
        "category": "Collectors",
        "city": "Cape Town",
        "suburb": "Sea Point",
        "description": "The world's first adhesive postage stamp. Penny Black, Plate 5, four good margins, light cancel. Accompanied by independent expert certificate. A centrepiece for any serious philatelist.",
        "trust_score": 94,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "Magic: The Gathering Black Lotus Alpha — PSA 8",
        "price": "R750 000",
        "category": "Collectors",
        "city": "Johannesburg",
        "suburb": "Sandton",
        "description": "Alpha Edition Black Lotus, the single most iconic card in Magic: The Gathering history. PSA graded NM-MT 8. Only a handful of PSA 8 Alpha Lotuses exist worldwide.",
        "trust_score": 96,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "1908 Ford Model T — Fully Restored, First Year of Production",
        "price": "R1 200 000",
        "category": "Collectors",
        "city": "Pretoria",
        "suburb": "Centurion",
        "description": "First year of production Ford Model T, fully restored to factory specification. Running condition. One of the most historically significant automobiles ever made. Full restoration documentation.",
        "trust_score": 93,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "Krugerrand Gold Coin Collection — 50th Anniversary Set (1967–2017)",
        "price": "R420 000",
        "category": "Collectors",
        "city": "Pretoria",
        "suburb": "Hatfield",
        "description": "Complete 50-year Krugerrand collection, one coin per year from 1967 to 2017, all in proof condition. Housed in original SA Mint presentation cases. A landmark South African numismatic set.",
        "trust_score": 91,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "Rolex Daytona 'Paul Newman' Ref. 6239 — Vintage 1968",
        "price": "R2 100 000",
        "category": "Collectors",
        "city": "Cape Town",
        "suburb": "Camps Bay",
        "description": "The most coveted Rolex ever made. 1968 Daytona with original exotic 'Paul Newman' dial, cream with red sub-registers. Unpolished case. Accompanied by provenance letter and independent authentication.",
        "trust_score": 97,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "Inverted Jenny Airmail Error Stamp — Scott C3a",
        "price": "R1 650 000",
        "category": "Collectors",
        "city": "Johannesburg",
        "suburb": "Rosebank",
        "description": "1918 US 24¢ airmail stamp with inverted biplane — the most famous stamp error in philatelic history. One of approximately 100 known examples. PSE graded VF-80. A once-in-a-generation opportunity.",
        "trust_score": 98,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "Pokémon Base Set Charizard Holo — PSA 10 Gem Mint",
        "price": "R280 000",
        "category": "Collectors",
        "city": "Pretoria",
        "suburb": "Lynnwood",
        "description": "1999 Pokémon Base Set Unlimited Charizard Holo, PSA 10 Gem Mint. The most iconic card in Pokémon history. PSA 10 examples are extraordinarily rare — this is the holy grail for Pokémon collectors.",
        "trust_score": 90,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "Patek Philippe Ref. 5270G Grand Complication — Perpetual Calendar Chronograph",
        "price": "R3 400 000",
        "category": "Collectors",
        "city": "Cape Town",
        "suburb": "Constantia",
        "description": "Patek Philippe Grand Complication in 18k white gold. Perpetual calendar, chronograph, moon phase. Unworn, full set with Patek service card. The pinnacle of Swiss watchmaking.",
        "trust_score": 99,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "1oz Proof Gold Mandela Coin — 1994 Inauguration",
        "price": "R85 000",
        "category": "Collectors",
        "city": "Pretoria",
        "suburb": "Muckleneuk",
        "description": "1oz proof gold coin commemorating Nelson Mandela's inauguration as President, 1994. Struck by the SA Mint in limited numbers. Original capsule and presentation box. A piece of South African history.",
        "trust_score": 88,
        "seller_email": "showcase@trustsquare.co",
    },
    {
        "title": "Magic: The Gathering Beta Mox Sapphire — BGS 9 Mint",
        "price": "R320 000",
        "category": "Collectors",
        "city": "Durban",
        "suburb": "Umhlanga",
        "description": "Beta Edition Mox Sapphire, one of the legendary Power Nine cards. BGS graded 9 Mint. Near-perfect condition for a 1993 card. The cornerstone of any serious Vintage MTG collection.",
        "trust_score": 91,
        "seller_email": "showcase@trustsquare.co",
    },
]

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print("  MarketSquare · Showcase Seed Script")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    created_ids = []

    for i, listing in enumerate(LISTINGS, 1):
        print(f"[{i:02d}/{len(LISTINGS)}] Creating: {listing['title'][:55]}...")
        try:
            r = requests.post(
                f"{BASE_URL}/listings",
                json=listing,
                headers=HEADERS,
                timeout=10
            )
            if r.status_code in (200, 201):
                new_id = r.json().get("id")
                created_ids.append((new_id, i - 1))  # (listing_id, sort_order)
                print(f"           ✓ Created listing ID {new_id}")
            else:
                print(f"           ✗ Failed ({r.status_code}): {r.text[:100]}")
        except Exception as e:
            print(f"           ✗ Error: {e}")

    if not created_ids:
        print("\nNo listings created — nothing to add to showcase.")
        sys.exit(1)

    if DB_PATH is None:
        print("\n✗ Could not find marketsquare.db — set MS_DB_PATH env var and retry.")
        print("  e.g.  MS_DB_PATH=/path/to/marketsquare.db python seed_showcase.py")
        sys.exit(1)

    print(f"\nUsing DB: {DB_PATH}")
    print(f"Adding {len(created_ids)} listings to wishlist_showcase table...")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM wishlist_showcase")  # clear any previous showcase
        for listing_id, sort_order in created_ids:
            conn.execute(
                "INSERT OR REPLACE INTO wishlist_showcase (listing_id, sort_order, added_by) VALUES (?, ?, 'seed')",
                (listing_id, sort_order)
            )
        conn.commit()
        conn.close()
        print(f"✓ Showcase table populated with {len(created_ids)} listings.")
    except Exception as e:
        print(f"✗ DB error: {e}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("  Done. Open trustsquare.co to see the showcase feed.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
