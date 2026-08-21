"""ACCOUNT-CLOSE-1 (21 Aug 2026) — EULA §14.1/§14.2/§14.3 in code.

David's ruling, 21 Aug 2026, after the termination reconciliation:

    Unused Tuppence is RETAINED on closure and RESTORED in full if the same
    verified identity registers again within 24 months. Forfeiture survives ONLY
    for breach under cause B5 (payment fraud / chargeback abuse) and cause B6
    (identity fraud). Tuppence is never converted to cash — retention is
    continued access to a service credit, never a right of repayment, so the
    Banks Act deposit-definition protection is untouched.

WHAT THIS REPLACES
    `DELETE FROM users WHERE email = ?` — the old endpoint hard-deleted the row and
    said nothing about Tuppence at all. It left orphaned transactions, no audit
    trail, and no way to honour §14.1's restore promise. It also contradicted
    §14.1 itself, which says account data is "deleted or anonymised within 30 days"
    — an immediate hard delete is neither reversible nor auditable.

HOW RETENTION WORKS — the wallet stays a pure SUM(amount)
    On closure the live balance is moved to zero by ONE offsetting
    `closure_retention` transactions row, and the amount is recorded in
    `account_closures`. On a qualifying return, ONE `closure_restore` row puts it
    back. No destructive UPDATE anywhere; the ledger explains itself.

IDENTITY — "the same verified identity"
    Matched on users.id_number_hash when the closing account had one (the strong
    proof), else on the email address (the weak proof). Both are recorded so an
    auditor can see which was used. A weak match still restores — the alternative
    is keeping money from someone who is probably its owner — but it is logged as
    'email' so a pattern of abuse is visible.

Stdlib + the app's own sqlite3 connection. No new dependencies.
"""
import sqlite3
from datetime import datetime, timezone

RETENTION_MONTHS = 24
FRAUD_CAUSES = ("B5", "B6")          # the only causes that forfeit — David, 21 Aug 2026


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_schema(conn):
    """Additive only; safe to call on every boot."""
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS account_closures (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        email             TEXT NOT NULL,
        id_number_hash    TEXT,
        closed_at         TEXT NOT NULL,
        closure_type      TEXT NOT NULL,     -- user | breach | convenience
        cause             TEXT,              -- B1..B6 for breach closures
        retained_tuppence INTEGER NOT NULL DEFAULT 0,
        forfeited         INTEGER NOT NULL DEFAULT 0,
        restored_at       TEXT,
        restored_to_email TEXT,
        restore_match     TEXT               -- id_hash | email
    );
    CREATE INDEX IF NOT EXISTS idx_closures_email ON account_closures(email);
    CREATE INDEX IF NOT EXISTS idx_closures_idhash ON account_closures(id_number_hash);
    """)
    conn.commit()


def _balance(conn, email):
    """Case-insensitive by design. transactions.user_email is written by many call sites
    with whatever casing the caller had; matching exactly would silently read a zero
    balance for a mixed-case address and retain nothing. Caught in test, 21 Aug 2026."""
    r = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM transactions WHERE lower(user_email)=lower(?)",
        (email,)).fetchone()
    return int(r[0]) if r else 0


def close_account(conn, email, closure_type="user", cause=None):
    """Close an account per §14. Returns a dict describing what happened.

    closure_type: 'user' (§14.1) · 'breach' (§14.2) · 'convenience' (§14.3)
    cause:        B1..B6 for breach closures. B5/B6 forfeit; everything else retains.
    """
    ensure_schema(conn)
    email = (email or "").strip().lower()
    if not email:
        raise ValueError("email required")

    row = conn.execute("SELECT email, id_number_hash FROM users WHERE lower(email)=?",
                       (email,)).fetchone()
    if row is None:
        raise LookupError("no such user")
    id_hash = row["id_number_hash"] if "id_number_hash" in row.keys() else None
    # Write ledger rows against the address as STORED, so the wallet keeps summing.
    email = row["email"]

    bal = _balance(conn, email)
    forfeit = bool(closure_type == "breach" and (cause or "").upper() in FRAUD_CAUSES)
    retained = 0

    if bal > 0:
        if forfeit:
            conn.execute(
                "INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
                (email, "closure_forfeit", -bal,
                 f"Forfeited on termination for {cause} (EULA 14.2)"))
        else:
            retained = bal
            conn.execute(
                "INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
                (email, "closure_retention", -bal,
                 f"Retained on account closure - {bal}T held for {RETENTION_MONTHS} months, "
                 f"restored on return (EULA 14.1/14.3)"))

    conn.execute(
        "INSERT INTO account_closures (email, id_number_hash, closed_at, closure_type, "
        "cause, retained_tuppence, forfeited) VALUES (?,?,?,?,?,?,?)",
        (email, id_hash, _now(), closure_type, cause, retained, 1 if forfeit else 0))

    # §14.1: "account data is deleted or anonymised within 30 days". Mark closed now;
    # the anonymisation pass is a separate, dated job — we do NOT hard-delete here,
    # because a deleted row cannot honour the restore promise.
    try:
        conn.execute("UPDATE users SET closed_at=? WHERE lower(email)=?", (_now(), email))
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE users ADD COLUMN closed_at TEXT")
        conn.execute("UPDATE users SET closed_at=? WHERE lower(email)=?", (_now(), email))
    conn.commit()
    return {"email": email, "closure_type": closure_type, "cause": cause,
            "retained_tuppence": retained, "forfeited": forfeit, "balance_at_closure": bal}


def find_restorable(conn, email, id_number_hash=None):
    """The most recent unrestored, unforfeited closure this person can claim.

    Strong match on id_number_hash first, then email. Returns (row, match_kind) or
    (None, None). Anything older than RETENTION_MONTHS is not returned.
    """
    ensure_schema(conn)
    email = (email or "").strip().lower()
    cutoff = conn.execute(
        "SELECT strftime('%Y-%m-%dT%H:%M:%SZ','now',?)", (f"-{int(RETENTION_MONTHS*30.44)} days",)
    ).fetchone()[0]

    if id_number_hash:
        r = conn.execute(
            "SELECT * FROM account_closures WHERE id_number_hash=? AND restored_at IS NULL "
            "AND forfeited=0 AND retained_tuppence>0 AND closed_at>=? "
            "ORDER BY closed_at DESC LIMIT 1", (id_number_hash, cutoff)).fetchone()
        if r:
            return r, "id_hash"
    r = conn.execute(
        "SELECT * FROM account_closures WHERE lower(email)=lower(?) AND restored_at IS NULL "
        "AND forfeited=0 AND retained_tuppence>0 AND closed_at>=? "
        "ORDER BY closed_at DESC LIMIT 1", (email, cutoff)).fetchone()
    return (r, "email") if r else (None, None)


def restore_on_return(conn, email, id_number_hash=None):
    """Restore retained Tuppence to a returning user. Idempotent; None if nothing due."""
    row, match = find_restorable(conn, email, id_number_hash)
    if not row:
        return None
    amount = int(row["retained_tuppence"])
    _u = conn.execute("SELECT email FROM users WHERE lower(email)=lower(?)", (email,)).fetchone()
    email = _u["email"] if _u else (email or "").strip()
    conn.execute(
        "INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
        (email, "closure_restore", amount,
         f"Welcome back - {amount}T restored from your previous account (EULA 14.1/14.3)"))
    conn.execute(
        "UPDATE account_closures SET restored_at=?, restored_to_email=?, restore_match=? "
        "WHERE id=?", (_now(), email, match, row["id"]))
    conn.commit()
    return {"restored": amount, "match": match, "from_email": row["email"],
            "closed_at": row["closed_at"]}
