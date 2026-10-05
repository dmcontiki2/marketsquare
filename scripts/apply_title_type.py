#!/usr/bin/env python3
"""apply_title_type.py -- TITLE-TYPE-1 (5 Oct 2026, RUL-208).

Maroushka via David, 5 Oct 2026: "differentiate in the advert placement for advertisers to define the house type between
sectional title and Full title. To be an option in Trustsquare to select but not an option in the Quick where we want to be
as quick and easy as possible, and where we will allow them interchangeable for a searcher, except if he insist either".

Server: listings.title_type (TEXT, NULL = not said), auto-added at start-up like every other listing column; create, edit
and the Listing Coach accept it, normalised to 'Sectional title' / 'Full title'. App: the Sell flow, Edit and the Coach offer
it for Property (optional), the advert shows it, and Browse's Property filter gets 'Title: Any / Sectional title / Full
title' -- Any by default; an advert that has not said its title is never hidden by it. Quick asks nothing. Idempotent."""
import io, sys
EDITS = {
 "bea_main.py": [
  ('        ("listing_type", "TEXT"),\n', '        ("listing_type", "TEXT"),\n        ("title_type",   "TEXT"),   # TITLE-TYPE-1 (RUL-208): Sectional title / Full title, NULL = not said\n'),
  ("""    listing_type: Optional[str] = None
    # Tutor fields
""", """    listing_type: Optional[str] = None
    title_type: Optional[str] = None   # TITLE-TYPE-1 (RUL-208)
    # Tutor fields
"""),
  ("""    erf_size: Optional[int] = None
    listing_type: Optional[str] = None
    subject: Optional[str] = None
""", """    erf_size: Optional[int] = None
    listing_type: Optional[str] = None
    title_type: Optional[str] = None   # TITLE-TYPE-1 (RUL-208)
    subject: Optional[str] = None
"""),
  ("""    new_id = cursor.lastrowid
""", """    new_id = cursor.lastrowid
    if _norm_title_type(listing.title_type):   # TITLE-TYPE-1 (RUL-208)
        conn.execute("UPDATE listings SET title_type=? WHERE id=?", (_norm_title_type(listing.title_type), new_id))
"""),
  ("""    _reset_vehicle_confirmations(dict(existing), d)   # CARS-SPEC-1: edits clear section confirmations
""", """    _reset_vehicle_confirmations(dict(existing), d)   # CARS-SPEC-1: edits clear section confirmations
    if "title_type" in d:   # TITLE-TYPE-1 (RUL-208): only the two words, or '' to clear
        d["title_type"] = _norm_title_type(d["title_type"])
"""),
  ('''_AA_TEXT_COLS = ("prop_type", "listing_type", "subject", "level", "mode", "service_type", "availability", "condition")
''', '''_AA_TEXT_COLS = ("prop_type", "listing_type", "subject", "level", "mode", "service_type", "availability", "condition", "title_type")


def _norm_title_type(v) -> str:
    """TITLE-TYPE-1 (RUL-208): 'Sectional title' | 'Full title' | '' (not said)."""
    s = str(v or "").strip().lower()
    if "section" in s:
        return "Sectional title"
    if "full" in s or "freehold" in s:
        return "Full title"
    return ""
'''),
 ],
 "ms.js": [
  # Sell flow: one optional row after the property type
  ("""    ['ptype','Property type','select','House|Townhouse|Apartment|Duet|Plot|Smallholding'],
""", """    ['ptype','Property type','select','House|Townhouse|Apartment|Duet|Plot|Smallholding'],
    ['tenure','Title (optional)','select','Sectional title|Full title'],   /* TITLE-TYPE-1 (RUL-208) */
"""),
  ("""  if(A.ptype) fields.prop_type=A.ptype;
""", """  if(A.ptype) fields.prop_type=A.ptype;
  if(A.tenure) fields.title_type=A.tenure;   /* TITLE-TYPE-1 (RUL-208) */
"""),
  ("""  var mapped={make:1,model:1,variant:1,year:1,beds:1,baths:1,ltype:1,subjects:1,levels:1,title:1,name:1,trade:1,work:1};""",
   """  var mapped={make:1,model:1,variant:1,year:1,beds:1,baths:1,ltype:1,subjects:1,levels:1,title:1,name:1,trade:1,work:1,tenure:1};   /* TITLE-TYPE-1: a column, not a line */"""),
  # Edit + Coach (AA_CATEGORIES Property)
  ("""      {id:'beds',         label:'Bedrooms',            type:'number', placeholder:'e.g. 3'},
      {id:'baths',        label:'Bathrooms',           type:'number', placeholder:'e.g. 2'},
      {id:'garages',      label:'Garages / parking',   type:'number', placeholder:'e.g. 1'},
      {id:'parking_type',""", """      {id:'title_type',   label:'Title (optional)',    type:'select', options:['Sectional title','Full title']},   /* TITLE-TYPE-1 (RUL-208) */
      {id:'beds',         label:'Bedrooms',            type:'number', placeholder:'e.g. 3'},
      {id:'baths',        label:'Bathrooms',           type:'number', placeholder:'e.g. 2'},
      {id:'garages',      label:'Garages / parking',   type:'number', placeholder:'e.g. 1'},
      {id:'parking_type',"""),
  ("""    prop_type:    raw.prop_type    || parseDescPropType(),
""", """    prop_type:    raw.prop_type    || parseDescPropType(),
    title_type:   raw.title_type   || '',   // TITLE-TYPE-1 (RUL-208)
"""),
  ("""  if (fd.listing_type) payload.listing_type = fd.listing_type;
  if (fd.subject)      payload.subject      = fd.subject;""", """  if (fd.listing_type) payload.listing_type = fd.listing_type;
  if (fd.title_type !== undefined && fd.title_type !== null) payload.title_type = fd.title_type;   // TITLE-TYPE-1: '' clears it
  if (fd.subject)      payload.subject      = fd.subject;"""),
  # the app object + the advert's spec chips
  ("""          floor_area:   l.floor_area   || null,
          erf_size:     l.erf_size     || null,
""", """          floor_area:   l.floor_area   || null,
          erf_size:     l.erf_size     || null,
          title_type:   l.title_type   || null,   // TITLE-TYPE-1 (RUL-208)
"""),
  ("""    add('\\ud83c\\udfe0','Type', l.propType||l.prop_type);
""", """    add('\\ud83c\\udfe0','Type', l.propType||l.prop_type);
    add('\\ud83d\\udcdc','Title', l.title_type);   /* TITLE-TYPE-1 (RUL-208) */
"""),
  # Browse filter: read, apply (an advert that has not said is never hidden), clear
  ("""    filterState.property.type        = getSelOptInSection('Property Type','fs-property');
""", """    filterState.property.type        = getSelOptInSection('Property Type','fs-property');
    filterState.property.titleType   = getSelOptInSection('Title','fs-property');   // TITLE-TYPE-1 (RUL-208)
"""),
  ("""      if(fp.type && fp.type!=='' && l.propType && l.propType!==fp.type) return false;
""", """      if(fp.type && fp.type!=='' && l.propType && l.propType!==fp.type) return false;
      if(fp.titleType && l.title_type && l.title_type!==fp.titleType) return false;   // TITLE-TYPE-1: only if she insists, and only on adverts that said
"""),
 ],
 "marketsquare.html": [
  ("""        <div class="fs-opt" onclick="toggleOpt(this,'fp-type')">Other</div>
      </div>
    </div>
""", """        <div class="fs-opt" onclick="toggleOpt(this,'fp-type')">Other</div>
      </div>
    </div>

    <!-- TITLE-TYPE-1 (RUL-208): Any by default -- sectional and full title are interchangeable unless she insists -->
    <div class="fs-section">
      <div class="fs-label">Title</div>
      <div class="fs-options">
        <div class="fs-opt" onclick="toggleOpt(this,'fp-title')">Any</div>
        <div class="fs-opt" onclick="toggleOpt(this,'fp-title')">Sectional title</div>
        <div class="fs-opt" onclick="toggleOpt(this,'fp-title')">Full title</div>
      </div>
    </div>
"""),
 ],
}
for p, reps in EDITS.items():
    s = io.open(p, encoding="utf-8", newline="").read()
    if "TITLE-TYPE-1" in s:
        print(p, "already"); continue
    crlf = "\r\n" in s
    for a, b in reps:
        if crlf:
            a, b = a.replace("\n", "\r\n"), b.replace("\n", "\r\n")
        if s.count(a) != 1:
            sys.exit("%s: anchor count %d: %s" % (p, s.count(a), a[:80]))
        s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="").write(s); print(p, "ok")
