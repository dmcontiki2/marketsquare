#!/usr/bin/env python3
"""060_identity_verdicts.py -- IDENTITY-VERDICT-1 (27 Sep 2026).

RUL-176 (David, 27 Sep): "we dont store the customers banking details because that was an
earlier option before we had Paystack, we dont need it now." RUL-178 (same conversation):
the five Trust Score points that banking carried are replaced by checks that hold NO
customer data -- David approved options 1-4.

This migration adds three columns, and the point of every one of them is that it is a
VERDICT AND A DATE, never the evidence:

  phone_verified_at        the OTP at POST /auth/phone/verify succeeded (that flow was
                           already complete and awarded nothing -- PHONE-CRED-1)
  payment_name_verified_at the name Paystack returned on a real payment matched the
                           verified ID name (PAYNAME-1)
  bank_name_verified_at    Paystack's /bank/resolve returned an account name that matched
                           the verified ID name (BANKRESOLVE-1)

WHAT IS DELIBERATELY NOT ADDED: any column that could hold an account number, an account
name, a bank, a branch code, or a cardholder name. The account number in BANKRESOLVE-1
exists only as a local variable for the length of one HTTPS call and is never written
anywhere -- asserted by scripts/test_identity_verdicts.py, which fails if the schema grows
a column that could hold it.

The five existing users.banking_* columns are LEFT IN PLACE and simply stop being read or
written. Dropping them is a deletion, which is reserved to David (STANDING_ORDERS SO-3),
and SQLite migrations in this project are additive by convention.
"""
import os, sqlite3, sys

APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")

COLS = (
    ("phone_verified_at", "TEXT"),
    ("payment_name_verified_at", "TEXT"),
    ("bank_name_verified_at", "TEXT"),
)

# A column whose NAME suggests it could hold the evidence rather than the verdict.
FORBIDDEN = ("account_number", "account_name", "cardholder", "card_name", "iban", "swift")


def main():
    if not os.path.isfile(DB):
        print("060: no database at %s -- nothing to do" % DB); return 0
    conn = sqlite3.connect(DB)
    try:
        have = {r[1] for r in conn.execute("PRAGMA table_info(users)")}
        todo = [(n, t) for n, t in COLS if n not in have]
        bad = [c for c in have if any(f in c.lower() for f in FORBIDDEN)]
        if bad:
            print("060: REFUSING -- users already carries %s, which this ruling says we do "
                  "not hold. Resolve that before adding verdict columns." % bad)
            return 2
        if not todo:
            print("060: all three verdict columns already present -- no change"); return 0
        if not APPLY:
            print("060: would add %s (re-run with --apply)" % ", ".join(n for n, _ in todo))
            return 0
        for n, t in todo:
            conn.execute("ALTER TABLE users ADD COLUMN %s %s" % (n, t))
        conn.commit()
        print("060: added %s" % ", ".join(n for n, _ in todo))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
