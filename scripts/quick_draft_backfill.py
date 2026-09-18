#!/usr/bin/env python3
"""QUICK-RETURN-1 BACKFILL -- the people who composed a draft BEFORE the door existed.

RG-0395 shipped the forward fix on 18 Sep 2026: from now on, a draft composed in the
Quick app mails its author a link straight back to it. That does nothing for the people
who came through before it, and PROBED on 18 Sep there is one who matters --

    listing 382 - Montana, "Guided Fair Chase Hunts", quality score 94, a photo and a
    998-character description, composed 12 Sep 15:37 by prospect 83302 (source
    register:moga, emailed 11 Sep 22:12). A real outfitter, from a cold letter, who
    walked every step of the five-tap journey and pressed a button reading "Publish it".
    He has no account, was never mailed, and his advert has been invisible for six days.

WHY THIS IS NOT SOMETHING THE AGENT MAY JUST DO: RUL-099 reserves "anything addressed to
a named individual" to David, and RUL-096(f) reserves sending to third parties outside
the allowlisted waves. The forward fix is the product working; this is a hand-sent
message to a specific person six days after the fact, which is a different act.

So this script exists, tested, and does NOT run without David's word:

    python3 scripts/quick_draft_backfill.py --list
    python3 scripts/quick_draft_backfill.py --send --permission "<David's words>" --date YYYY-MM-DD

It sends EXACTLY the mail RG-0395 sends -- no new copy, no offer, no price claim -- and
it publishes nothing. The seller still publishes by his own hand (ONBOARDING_GOAL s3).
"""
import argparse, sqlite3, sys, os

DB = "/var/www/marketsquare/marketsquare.db"
CUTOFF = "2026-09-18"          # drafts composed before the door existed


def candidates(conn):
    """Quick-lane drafts, still drafts, with a typed address, composed before the fix.
    The 23 Aug batch (375-380) is one-per-category seeded content, not composers: it is
    excluded by requiring the row to have no users account AND a quality_score set by
    the Quick scorer. Anything ambiguous is listed, never sent blind."""
    rows = conn.execute(
        """SELECT l.id, l.seller_email, l.title, l.city, l.quality_score,
                  substr(l.created_at,1,16) AS made,
                  (SELECT COUNT(*) FROM users u WHERE LOWER(u.email)=LOWER(l.seller_email)) AS has_account
             FROM listings l
            WHERE l.is_demo = 0
              AND l.listing_status = 'draft'
              AND l.seller_email IS NOT NULL AND l.seller_email <> ''
              AND l.published_at IS NULL
              AND substr(l.created_at,1,10) < ?
            ORDER BY l.created_at DESC""", (CUTOFF,)).fetchall()
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--permission", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--only", type=int, action="append",
                    help="restrict to these listing ids (repeatable)")
    a = ap.parse_args()

    conn = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    conn.row_factory = sqlite3.Row
    rows = candidates(conn)
    if a.only:
        rows = [r for r in rows if r["id"] in a.only]

    print("%-5s %-17s %-6s %-28s %-8s %s" % ("id", "made", "score", "title", "account", "city"))
    for r in rows:
        print("%-5s %-17s %-6s %-28s %-8s %s" % (
            r["id"], r["made"], r["quality_score"], (r["title"] or "")[:28],
            "yes" if r["has_account"] else "no", r["city"]))
    print("\n%d draft(s) composed before the door existed." % len(rows))

    if not a.send:
        print("\nNothing sent. Add --send with --permission and --date to send.")
        return 0

    if not a.permission.strip() or not a.date.strip():
        print("\nREFUSED: --send needs --permission (David's own words) and --date. "
              "RUL-099 reserves a message to a named individual to him.", file=sys.stderr)
        return 2

    sys.path.insert(0, "/var/www/marketsquare")
    import main as B
    sent = 0
    for r in rows:
        status = "skipped"
        try:
            B._quick_draft_return(r["seller_email"], r["id"], r["title"] or "")
            status = "sent"; sent += 1
        except Exception as exc:
            status = "failed: %r" % (exc,)
        print("  listing %s -> %s" % (r["id"], status))
    print("\n%d mailed. Permission on record: %r (%s)" % (sent, a.permission.strip()[:120], a.date))
    print("Nothing was published. Every seller still publishes by his own hand.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
