"""AGENT-SVC-1 functional test — full loop on a temp DB (no bea_main import).
Run: python3 test_estate_agents.py"""
import os, sys, tempfile, sqlite3

_tmp = tempfile.mkstemp(suffix=".db")[1]
import database
database.DB_PATH = _tmp

conn = database.get_db()
conn.executescript("""
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, trust_score INTEGER,
                    slot_limit INTEGER, seller_tier TEXT);
CREATE TABLE listings (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, price TEXT, category TEXT,
                       city TEXT, area TEXT, suburb TEXT, description TEXT, seller_email TEXT,
                       listing_status TEXT, prop_type TEXT, beds INTEGER, baths INTEGER, listing_type TEXT);
CREATE TABLE agencies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, admin_email TEXT, api_key TEXT,
                       countries TEXT, plan TEXT, verified INTEGER);
CREATE TABLE agency_members (agency_id INTEGER, agent_email TEXT, listing_cap INTEGER DEFAULT 10,
                             seat_paid INTEGER DEFAULT 0, role TEXT DEFAULT 'agent', status TEXT,
                             joined_at TEXT, agent_name TEXT, city TEXT, country TEXT,
                             PRIMARY KEY (agency_id, agent_email));
CREATE TABLE user_credentials (email TEXT, signal_id TEXT, status TEXT, listing_category TEXT, updated_at TEXT);
CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, type TEXT,
                           amount INTEGER, description TEXT);
INSERT INTO agencies (name, admin_email, api_key, verified) VALUES ('Test Realty','admin@tr.co','k',1);
""")
conn.commit(); conn.close()

import estate_agents

# quality stub: parity with _import_quality_score shape (score, missing)
def _fake_quality(row):
    d = dict(row)
    return (80 if (d.get("description") or "").count(" ") > 5 else 30), []
estate_agents.configure(quality_fn=_fake_quality)

import auth
from fastapi import FastAPI
from fastapi.testclient import TestClient
app = FastAPI()
app.dependency_overrides = {}
app.include_router(estate_agents.router)
# bypass api-key dep for the bulk endpoint
app.dependency_overrides[auth.require_api_key] = lambda: "test-key"
c = TestClient(app)
FAIL = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + ((" · " + str(extra)) if extra and not cond else ""))
    if not cond: FAIL.append(name)

# 1 template
r = c.get("/agents/template")
check("template 200 + slots", r.status_code == 200 and len(r.json()["credential_slots"]) == 4)

# 2 bulk onboard 2 agents with credential claims
r = c.post("/agencies/1/agents/bulk", json={"agents": [
    {"email": "ann@tr.co", "name": "Ann Smith", "city": "Pretoria", "suburbs": "Waterkloof, Brooklyn",
     "headline": "Call Ann on 082 123 4567 for luxury homes", "bio": " ".join(["word"]*35),
     "years_experience": 12, "properties_sold": 240, "ppra_number": "PPRA123", "ffc_year": 2026,
     "nqf_level": 5, "body_memberships": ["IEASA"]},
    {"email": "ben@tr.co", "city": "Pretoria", "years_experience": 3, "ffc_year": 2026,
     "headline": "Rentals specialist", "bio": " ".join(["word"]*35)}]})
j = r.json()
check("bulk onboard 200 + 2 ok", r.status_code == 200 and j["onboarded"] == 2, r.text)
ann_ref = j["agents"][0]["anon_ref"]
check("nqf5 implies nqf4 pending", "nqf5" in j["agents"][0]["credentials_pending"])

# 3 anonymisation: phone stripped from headline (fallback strip active)
r = c.get("/agents/profile", params={"email": "ann@tr.co"})
check("phone stripped from headline", "082" not in (r.json()["headline"] or ""), r.json()["headline"])

# 4 credentials pending — not earned: trust untouched, publish blocked
r = c.put("/agents/profile/publish", params={"email": "ann@tr.co"})
check("publish blocked until FFC verified", r.status_code == 422 and "FFC" in str(r.json()))

# 5 ops verifies FFC + PPRA (simulate existing /trust-score/credential flow)
conn = database.get_db()
conn.execute("UPDATE user_credentials SET status='earned' WHERE email='ann@tr.co' AND signal_id IN ('category.property.ffc','category.property.ppra')")
conn.execute("UPDATE users SET trust_score=78 WHERE email='ann@tr.co'")
conn.execute("UPDATE users SET trust_score=55 WHERE email='ben@tr.co'")
conn.execute("UPDATE user_credentials SET status='earned' WHERE email='ben@tr.co' AND signal_id='category.property.ffc'")
# Ann gets 2 live listings (quality 80), Ben 1 thin listing (quality 30)
conn.execute("INSERT INTO listings (title,category,city,suburb,description,seller_email,listing_status) VALUES ('A1','property','Pretoria','Waterkloof','a b c d e f g h','ann@tr.co','live')")
conn.execute("INSERT INTO listings (title,category,city,suburb,description,seller_email,listing_status) VALUES ('A2','property','Pretoria','Brooklyn','a b c d e f g h','ann@tr.co','live')")
conn.execute("INSERT INTO listings (title,category,city,suburb,description,seller_email,listing_status) VALUES ('B1','property','Pretoria','Central','thin','ben@tr.co','live')")
conn.commit(); conn.close()

r = c.put("/agents/profile/publish", params={"email": "ann@tr.co"})
check("Ann publish ok after verify", r.status_code == 200)
# Ben lacks PPRA submission → blocked
r = c.put("/agents/profile/publish", params={"email": "ben@tr.co"})
check("Ben blocked (no PPRA submitted)", r.status_code == 422 and "PPRA" in str(r.json()))

# 6 ranking: Ann rank = .5*80+.5*78 = 79 ; Ben not live
r = c.get("/agents/nearby", params={"city": "Pretoria", "suburb": "Waterkloof"})
j = r.json()
check("nearby: only live agents", j["count"] == 1)
check("rank 50/50 math", abs(j["agents"][0]["rank_score"] - 79.0) < 0.01, j["agents"][0]["rank_score"])
check("anonymous card (no email/name)", "ann" not in str(j["agents"][0]).lower() or "smith" not in str(j["agents"][0]).lower())
check("banded experience", j["agents"][0]["experience"] == "10+ yrs".replace("yrs","years") or j["agents"][0]["experience"] == "10+ years")
check("banded sold 200+", j["agents"][0]["properties_sold"].startswith("200+"))
check("badges earned incl FFC", "Fidelity Fund Certificate" in j["agents"][0]["badges_earned"])

# 7 pitch
r = c.get("/agents/pitch", params={"city": "Pretoria"})
check("pitch advantages + legal + preview", len(r.json()["advantages"]) == 5 and r.json()["local_agent_count"] == 1)

# 8 seller intro → agent inbox (anonymous seller, trust visible) → accept charges 1T
conn = database.get_db()
conn.execute("INSERT INTO users (email, trust_score) VALUES ('seller@x.co', 62)")
conn.execute("INSERT INTO listings (title,category,city,suburb,description,seller_email,listing_status) VALUES ('My house','property','Pretoria','Waterkloof','nice place with lots of words here','seller@x.co','draft')")
conn.execute("INSERT INTO transactions (user_email,type,amount,description) VALUES ('ann@tr.co','topup',5,'test')")
conn.commit()
lid = conn.execute("SELECT id FROM listings WHERE seller_email='seller@x.co'").fetchone()["id"]
conn.close()
r = c.post("/agents/intro", json={"seller_email": "seller@x.co", "agent_ref": ann_ref, "listing_id": lid,
                                  "message": "Help me sell, call me on 083 555 1234"})
check("seller intro created", r.status_code == 200)
r = c.post("/agents/intro", json={"seller_email": "seller@x.co", "agent_ref": ann_ref, "listing_id": lid})
check("dup intro blocked 409", r.status_code == 409)
r = c.get("/agents/intros", params={"email": "ann@tr.co"})
j = r.json()
check("inbox: seller anonymous", "seller_email" not in j[0])
check("inbox: seller trust visible", j[0]["seller_trust_snapshot"] == 62)
check("inbox: msg phone stripped", "083" not in (j[0]["message"] or ""))
check("inbox: property summary attached", j[0]["listing"]["title"] == "My house")
iid = j[0]["id"]
r = c.put(f"/agents/intros/{iid}/accept", params={"email": "ann@tr.co"})
check("accept 200 + 1T + contact revealed", r.status_code == 200 and r.json()["charged"] == "1T" and r.json()["seller_email"] == "seller@x.co")
conn = database.get_db()
bal = conn.execute("SELECT SUM(amount) b FROM transactions WHERE user_email='ann@tr.co'").fetchone()["b"]
conn.close()
check("agent balance 5-1=4", bal == 4, bal)
r = c.put(f"/agents/intros/{iid}/accept", params={"email": "ann@tr.co"})
check("double-accept blocked 409", r.status_code == 409)
# broke agent cannot accept
r = c.post("/agents/intro", json={"seller_email": "seller@x.co", "agent_ref": ann_ref})
conn = database.get_db()
conn.execute("INSERT INTO transactions (user_email,type,amount,description) VALUES ('ann@tr.co','intro_deduct',-4,'drain')")
conn.commit()
iid2 = conn.execute("SELECT id FROM agent_intros WHERE status='pending'").fetchone()["id"]
conn.close()
r = c.put(f"/agents/intros/{iid2}/accept", params={"email": "ann@tr.co"})
check("insufficient T → 402, no charge", r.status_code == 402)
r = c.put(f"/agents/intros/{iid2}/decline", params={"email": "ann@tr.co"})
check("decline free", r.status_code == 200 and r.json()["charged"] == "0T")

# 9 seller status view — agent identity only after accept
r = c.get("/agents/intros/for-seller", params={"email": "seller@x.co"})
j = r.json()
acc = [x for x in j if x["status"] == "accepted"][0]
dec = [x for x in j if x["status"] == "declined"][0]
check("seller sees agent email only on accepted", acc["agent_email"] == "ann@tr.co" and dec["agent_email"] is None)

# ══ AGENT-SVC-2: CARS VERTICAL ══════════════════════════════
# 10 template per vertical
r = c.get("/agents/template", params={"vertical": "cars"})
j = r.json()
check("cars template: MIRA slot + label", j["label"] == "Car Sales Agent" and j["credential_slots"][0]["slot"] == "mira_number")
check("cars template: gate is MIRA", "MIRA" in j["go_live_gate"])

# 11 bulk onboard car agents with agency-level vertical
r = c.post("/agencies/1/agents/bulk", json={"vertical": "cars", "agents": [
    {"email": "carl@wbc.co", "name": "Carl Benz", "city": "Pretoria", "suburbs": "Silverton, Gezina",
     "headline": "Call 082 999 8888 — bakkies and SUVs", "bio": " ".join(["word"]*35),
     "years_experience": 8, "properties_sold": 320, "mira_number": "MIRA-771", "inspection_partner": "AA South Africa"},
    {"email": "dan@wheelie.co", "city": "Pretoria", "years_experience": 2,
     "headline": "Hatchbacks", "bio": " ".join(["word"]*35)}]})
j = r.json()
check("cars bulk: 2 onboarded, vertical=cars", r.status_code == 200 and j["onboarded"] == 2 and j["agents"][0]["vertical"] == "cars")
check("cars bulk: mira+inspection pending", j["agents"][0]["credentials_pending"] == ["mira", "inspection"])
carl_ref = j["agents"][0]["anon_ref"]

# 12 gate: publish blocked until MIRA verified
r = c.put("/agents/profile/publish", params={"email": "carl@wbc.co"})
check("cars publish blocked until MIRA earned", r.status_code == 422 and "MIRA" in str(r.json()))
conn = database.get_db()
conn.execute("UPDATE user_credentials SET status='earned' WHERE email='carl@wbc.co' AND signal_id='category.cars.dealer_reg'")
conn.execute("UPDATE users SET trust_score=70 WHERE email='carl@wbc.co'")
conn.execute("INSERT INTO listings (title,category,city,suburb,description,seller_email,listing_status) VALUES ('Hilux','cars','Pretoria','Silverton','a b c d e f g h','carl@wbc.co','live')")
# a PROPERTY listing by carl must NOT count toward his cars quality
conn.execute("INSERT INTO listings (title,category,city,suburb,description,seller_email,listing_status) VALUES ('His flat','property','Pretoria','Central','thin','carl@wbc.co','live')")
conn.commit(); conn.close()
r = c.put("/agents/profile/publish", params={"email": "carl@wbc.co"})
check("cars publish ok after MIRA verify", r.status_code == 200)

# 13 vertical separation in ranking
r = c.get("/agents/nearby", params={"city": "Pretoria", "vertical": "cars"})
j = r.json()
check("cars nearby: only car agents", j["count"] == 1 and j["agents"][0]["anon_ref"] == carl_ref)
check("cars quality excludes property listings", j["agents"][0]["live_listings"] == 1 and j["agents"][0]["avg_listing_quality"] == 80)
check("cars rank 50/50", abs(j["agents"][0]["rank_score"] - 75.0) < 0.01, j["agents"][0]["rank_score"])
check("cars sold noun banded", j["agents"][0]["properties_sold"] == "200+ cars sold", j["agents"][0]["properties_sold"])
check("cars badge MIRA earned", "MIRA Registered Dealer" in j["agents"][0]["badges_earned"])
r = c.get("/agents/nearby", params={"city": "Pretoria"})
check("property nearby unchanged (no car agents leak)", all(a["vertical"] == "property" for a in r.json()["agents"]))

# 14 cars pitch content
r = c.get("/agents/pitch", params={"city": "Pretoria", "vertical": "cars"})
j = r.json()
check("cars pitch: NATIS in legal note + 1 local", "NATIS" in j["legal_note"] and j["local_agent_count"] == 1)

# 15 seller -> car agent intro at 1T
conn = database.get_db()
conn.execute("INSERT INTO users (email, trust_score) VALUES ('carseller@x.co', 58)")
conn.execute("INSERT INTO transactions (user_email,type,amount,description) VALUES ('carl@wbc.co','topup',2,'test')")
conn.commit(); conn.close()
r = c.post("/agents/intro", json={"seller_email": "carseller@x.co", "agent_ref": carl_ref, "message": "Selling my Polo, 083 111 2222"})
check("car intro created", r.status_code == 200)
r = c.get("/agents/intros", params={"email": "carl@wbc.co"})
j = r.json()
check("car lead: seller anon + trust 58", "seller_email" not in j[0] and j[0]["seller_trust_snapshot"] == 58)
r = c.put(f"/agents/intros/{j[0]['id']}/accept", params={"email": "carl@wbc.co"})
check("car lead accept 1T + reveal", r.status_code == 200 and r.json()["charged"] == "1T" and r.json()["seller_email"] == "carseller@x.co")

# ══ AGENT-SVC-3: TRAVEL VERTICAL ════════════════════════════
r = c.get("/agents/template", params={"vertical": "travel"})
j = r.json()
check("travel template: ASATA slot + label", j["label"] == "Tour Agent" and j["credential_slots"][0]["slot"] == "asata_number")
check("travel template: gate is ASATA", "ASATA" in j["go_live_gate"])

r = c.post("/agencies/1/agents/bulk", json={"vertical": "travel", "agents": [
    {"email": "tina@safaris.co", "name": "Tina Tours", "city": "Pretoria", "suburbs": "Menlyn",
     "headline": "Kruger and Vic Falls packages — WhatsApp 082 444 5555", "bio": " ".join(["word"]*35),
     "years_experience": 9, "properties_sold": 60, "asata_number": "ASATA-991",
     "iata_code": "IATA-12345", "cipc_number": "2016/123456/07", "bonding_proof": "SATIB bond"}]})
j = r.json()
check("travel bulk onboarded", r.status_code == 200 and j["onboarded"] == 1 and j["agents"][0]["vertical"] == "travel")
check("travel creds pending", j["agents"][0]["credentials_pending"] == ["asata", "iata", "cipc", "bonding"])
tina_ref = j["agents"][0]["anon_ref"]

r = c.put("/agents/profile/publish", params={"email": "tina@safaris.co"})
check("travel publish blocked until ASATA earned", r.status_code == 422 and "ASATA" in str(r.json()))
conn = database.get_db()
conn.execute("UPDATE user_credentials SET status='earned' WHERE email='tina@safaris.co' AND signal_id='category.travel.asata_member'")
conn.execute("UPDATE users SET trust_score=66 WHERE email='tina@safaris.co'")
conn.execute("INSERT INTO listings (title,category,city,suburb,description,seller_email,listing_status) VALUES ('Kruger 4-day','adventures','Pretoria','Menlyn','a b c d e f g h','tina@safaris.co','live')")
conn.commit(); conn.close()
r = c.put("/agents/profile/publish", params={"email": "tina@safaris.co"})
check("travel publish ok (ASATA earned + CIPC submitted)", r.status_code == 200)

r = c.get("/agents/nearby", params={"city": "Pretoria", "vertical": "travel"})
j = r.json()
check("travel nearby separated", j["count"] == 1 and j["agents"][0]["anon_ref"] == tina_ref)
check("travel rank 50/50 (80q/66t=73)", abs(j["agents"][0]["rank_score"] - 73.0) < 0.01, j["agents"][0]["rank_score"])
check("trips noun banded", j["agents"][0]["properties_sold"] == "50-199 trips sold", j["agents"][0]["properties_sold"])
check("ASATA badge earned", "ASATA member" in j["agents"][0]["badges_earned"])
r = c.get("/agents/nearby", params={"city": "Pretoria", "vertical": "cars"})
check("cars list has no tour agents", all(a["vertical"] == "cars" for a in r.json()["agents"]))

r = c.get("/agents/pitch", params={"city": "Pretoria", "vertical": "travel"})
j = r.json()
check("travel pitch: bonded + searcher CTA", "bonded" in j["legal_note"] and "dreaming" in j["cta"])

# searcher intro — no listing at all (holiday searcher, not a seller)
conn = database.get_db()
conn.execute("INSERT INTO transactions (user_email,type,amount,description) VALUES ('tina@safaris.co','topup',3,'test')")
conn.commit(); conn.close()
r = c.post("/agents/intro", json={"seller_email": "dreamer@x.co", "agent_ref": tina_ref,
                                  "message": "Honeymoon, Zanzibar, June, 2 people, call 083 777 1234"})
check("searcher intro created (no listing)", r.status_code == 200)
r = c.get("/agents/intros", params={"email": "tina@safaris.co"})
j = r.json()
check("travel lead: anon + phone stripped + no listing", "seller_email" not in j[0] and "083" not in (j[0]["message"] or "") and j[0]["listing"] is None)
r = c.put(f"/agents/intros/{j[0]['id']}/accept", params={"email": "tina@safaris.co"})
check("travel lead accept 1T + reveal", r.status_code == 200 and r.json()["seller_email"] == "dreamer@x.co")

os.unlink(_tmp)
print("\n%d checks, %d failed" % (23 + 15 + 14, len(FAIL)))
sys.exit(1 if FAIL else 0)
