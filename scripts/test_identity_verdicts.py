#!/usr/bin/env python3
"""IDENTITY-VERDICT-1 (27 Sep 2026) -- red on the pre-fix source, green on the fix.

RUL-176 (David, 27 Sep): "we dont store the customers banking details because that was an
earlier option before we had Paystack, we dont need it now."
RUL-178 (same conversation): the 5 Trust Score points banking carried are replaced by
checks that hold NO customer data. David approved all four options.

WHAT WAS BROKEN
  (a) POST /users/{email}/banking stored account holder, bank, last-4 and branch code and
      awarded 5 points -- 2 for "details on file" and 3 for a name match where BOTH SIDES
      were typed by the same person, so it evidenced almost nothing while holding a
      Seller's bank account for a purpose no code performed.
  (b) category.lm.phone_verified (2 pts) was declared and never written, although
      POST /auth/phone/verify was a complete OTP flow -- hashed code, attempt limit,
      expiry, single use.
  (c) category.lm.id_uploaded (2 pts) was written as "pending" on upload and could never
      become earned, and category.lm.id_admin_verified (5 pts) was never written at all,
      because no route existed for a human to confirm an identity document. One missing
      route, two dead credentials, 7 unreachable points.

THE PROPERTY THIS TEST EXISTS TO DEFEND, and the reason it is not just a shape check:
a customer account number must never be storable, loggable or returnable. The checks below
fail if the schema grows a column that could hold one, if payments.py logs or re-raises it,
or if the endpoint puts it in a response.

Run:  python3 scripts/test_identity_verdicts.py
"""
import ast
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FAILS = []


def check(name, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + name + (("  -- " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def main():
    bea = io.open(os.path.join(REPO, "bea_main.py"), encoding="utf-8").read()
    pay = io.open(os.path.join(REPO, "payments.py"), encoding="utf-8").read()
    msjs = io.open(os.path.join(REPO, "ms.js"), encoding="utf-8").read()
    policy = json.load(io.open(os.path.join(REPO, "route_policy.json"), encoding="utf-8"))
    keys = {r["key"] for r in policy["routes"]}

    print("IDENTITY-VERDICT-1")
    print("the banking store is gone (RUL-176):")
    check("POST /users/{email}/banking no longer exists", '@app.post("/users/{email}/banking")' not in bea)
    check("it is not still declared to the gate", "POST /users/{email}/banking" not in keys)
    check("the BankingIn model is gone", "class BankingIn" not in bea)
    check("no code writes the banking_* columns",
          not re.search(r"UPDATE users SET banking_holder|banking_account_last4\s*=", bea))
    check("the retired credentials are no longer awarded",
          "category.lm.banking" not in bea)
    check("the app no longer reads stored bank details",
          "banking_added_at" not in msjs and "banking_account_last4" not in msjs)
    # The READ side matters as much as the write side: identity-status kept REPORTING the
    # four banking fields after the store was removed, which is a surface still describing
    # data we had undertaken not to hold. Found on the live box post-deploy, 27 Sep.
    m_idst = re.search(r'def identity_status\(.*?\n(?=\n@app\.|\n# )', bea, re.S)
    idst = m_idst.group(0) if m_idst else ""
    check("identity-status exists", bool(idst))
    # Check the SELECT, not the prose: the docstring legitimately NAMES the fields it
    # removed, and a test that cannot tell an explanation from a live reference is a test
    # that will be silenced by rewording rather than by fixing.
    m_sel = re.search(r"SELECT id_name.*?FROM users WHERE email=", idst, re.S)
    sel = m_sel.group(0) if m_sel else ""
    check("  ... its SELECT exists", bool(sel))
    check("  ... its SELECT no longer reads the retired banking fields",
          "banking_" not in sel, "SELECT still reads: %s"
          % ", ".join(sorted(set(re.findall(r"banking_\w+", sel)))))
    check("  ... it reports the three verdicts instead",
          all(c in idst for c in ("phone_verified_at", "payment_name_verified_at",
                                  "bank_name_verified_at")))
    check("  ... a missing verdict column names the MIGRATION, not the seller",
          "060_identity_verdicts.py" in idst and "503" in idst)

    print("the five columns are LEFT ALONE (dropping them is David's, not mine):")
    mig = os.path.join(REPO, "migrations", "060_identity_verdicts.py")
    check("migration 060 exists", os.path.isfile(mig))
    if os.path.isfile(mig):
        m = io.open(mig, encoding="utf-8").read()
        check("it adds no column that could hold an account number",
              not re.search(r'ADD COLUMN\s+\w*(account_number|account_name|cardholder|iban)', m))
        check("it does not DROP the banking columns", "DROP COLUMN" not in m.upper())
        check("it adds the three verdict columns",
              all(c in m for c in ("phone_verified_at", "payment_name_verified_at", "bank_name_verified_at")))

    print("the three dead credentials are wired (RUL-178):")
    check("phone OTP awards category.lm.phone_verified",
          'category.lm.phone_verified", "earned"' in bea and "PHONE-CRED-1" in bea)
    check("an admin route can confirm an identity document",
          '@app.post("/admin/identity/confirm")' in bea and "POST /admin/identity/confirm" in keys)
    check("confirming earns the pending id_uploaded",
          'category.lm.id_uploaded", "earned"' in bea)
    check("id_admin_verified does NOT stack on id_ai_verified",
          "ai_already_earned" in bea and "superseded" in bea)

    print("the two replacement credentials:")
    check("payment-name credential declared at 3 pts",
          re.search(r'"category\.lm\.payment_name_verified":.*?"points": 3', bea) is not None)
    check("bank-name credential declared at 2 pts",
          re.search(r'"category\.lm\.bank_name_verified":.*?"points": 2', bea) is not None)
    check("the payment check runs on BOTH payment paths",
          bea.count("_payment_name_check(conn, email,") >= 2)
    check("a payment with no reported name is NOT MEASURED, not a mismatch",
          "NOT MEASURED" in bea and "def payment_account_name" in pay)
    check("bank codes come from Paystack, not a hardcoded table",
          "def list_banks" in pay and "GET /payment/banks" in keys
          and "MS_BANKS = null" in msjs)

    print("THE PROPERTY: an account number must not be storable, loggable or returnable.")
    # payments.resolve_account_name must not log or re-raise the number
    m = re.search(r"def resolve_account_name\(.*?\n(?=\ndef |\Z)", pay, re.S)
    body = m.group(0) if m else ""
    check("resolve_account_name exists", bool(body))
    check("  ... it never logs the number",
          not re.search(r"(_log|logging|logger|print)\s*\([^)]*account_number", body))
    check("  ... it never re-raises the vendor exception (the query string carries the number)",
          "raise" not in body.replace("# ", ""))
    check("  ... it returns only ok/account_name/reason",
          set(re.findall(r'return \{"ok": \w+', body)) and "account_number" not in
          re.sub(r"#.*", "", body).split("return")[-1])
    # the endpoint must not echo it
    m2 = re.search(r"def verify_bank_name\(.*?\n(?=\n@app\.|\Z)", bea, re.S)
    ep = m2.group(0) if m2 else ""
    check("verify_bank_name exists", bool(ep))
    ep_nocomment = re.sub(r"#.*", "", ep)
    check("  ... no SQL in it writes an account number or name",
          not re.search(r"(INSERT|UPDATE)[^\n]*\b(acct|account_number|account_name)\b", ep_nocomment))
    check("  ... the response carries no account number or name",
          not re.search(r'return \{[^}]*\bacct\b', ep_nocomment, re.S)
          and not re.search(r'"account_name"\s*:', ep_nocomment))
    check("  ... an unreachable bank is NOT MEASURED, never a failed match",
          "could not reach your bank" in ep and "checked\": False" in ep.replace("'", '"'))
    check("  ... the app clears the typed number after the call", "acc = '';" in msjs)

    print("")
    if FAILS:
        print("RED: %d check(s) failed -- %s" % (len(FAILS), ", ".join(FAILS)))
        return 1
    print("GREEN: banking storage is gone, the 5 points are replaced by third-party checks, "
          "and an account number cannot be stored, logged or returned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
