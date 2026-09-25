#!/usr/bin/env python3
"""enrol_import.py -- ORG-ENROL-1 importer, run ON THE SERVER (it talks to the BEA on localhost).

    python3 enrol_import.py --agency 12 --csv people.csv --out slips.html [--lang zu]

people.csv columns: name,role[,lang][,former]   (role = a key from roles/role_registry.json, e.g.
home_cleaner; lang = en|zu|xh|af|nso; former = yes/no). One row per person.

It calls POST /agencies/{id}/enrol?format=sheet and writes the printable slips page. It sends nothing
to anyone and it CANNOT create an advert (the endpoint cannot). The admin key is read from the
environment or /etc/marketsquare/secrets.env and is never printed.
"""
import argparse, csv, json, os, sys, urllib.request


def _admin_key():
    k = os.environ.get("MS_ADMIN_KEY", "")
    if k:
        return k
    try:
        for line in open("/etc/marketsquare/secrets.env", encoding="utf-8"):
            if line.startswith("MS_ADMIN_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agency", type=int, required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    a = ap.parse_args()
    rows = []
    with open(a.csv, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
            if not r.get("name"):
                continue
            rows.append({"name": r["name"], "role": r.get("role", ""), "lang": r.get("lang") or a.lang,
                         "former": r.get("former", "").lower() in ("1", "y", "yes", "true", "former")})
    if not rows:
        sys.exit("no rows with a name in %s" % a.csv)
    key = _admin_key()
    if not key:
        sys.exit("MS_ADMIN_KEY not found (environment or /etc/marketsquare/secrets.env)")
    req = urllib.request.Request("%s/agencies/%d/enrol?format=sheet" % (a.base, a.agency),
                                 data=json.dumps({"rows": rows, "lang": a.lang}).encode("utf-8"),
                                 headers={"Content-Type": "application/json", "X-Admin-Key": key}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            page = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        sys.exit("refused %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:400]))
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(page)
    os.chmod(a.out, 0o600)
    print("enrolled %d -> %s (private: each slip is that person's key)" % (len(rows), a.out))


if __name__ == "__main__":
    main()
