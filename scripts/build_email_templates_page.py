#!/usr/bin/env python3
"""
build_email_templates_page.py -- EMAIL-PAGE-TRUTH-1 (8 Sep 2026)

The ONE writer for the Ops Dashboard "Email Templates" view
(orchestration_v2/email_templates.html) and for the preview mirror it shows
(orchestration_v2/templates/*).

SOURCE OF TRUTH = CityLauncher/emailer/templates/ -- the copies the host-side wave runner
(launch_day_wave.bat -> wave_runner -> emailer.py) actually sends. Nothing sends from
orchestration_v2/templates/; it exists only so the deployed dashboard can preview the
letters. On 23 Aug 2026 the page was hand-built from a snapshot in that folder, the
sending copies then moved on (28 Aug intl pass, 4 Sep support route + browse link,
5 Sep inline mark, 6 Sep A/B arm, 8 Sep register letter) and the page kept saying
"exactly as the wave machinery sends them" for 16 days. This script makes that sentence
mechanical: run it, and the mirror + page are recomputed from the sending files.

    python3 scripts/build_email_templates_page.py            # rebuild mirror + page
    python3 scripts/build_email_templates_page.py --check    # exit 1 if anything is stale

What "as sent today" means: the emailer strips the <!--LAUNCH_SPECIAL_START/END--> block
unless launch_codes.enabled() is true; enabled() needs the .env flag + secret + deadline AND
the deadline not to have passed (SPECIAL-CLOSE-1). The mirror applies the same rule, so a
preview shows the block only while a real send would.

Regression ledger RG-0344 asserts mirror == as-sent(source) for every letter in the send
lane and that the page references each one. Stdlib only.
"""
import os, re, sys, json, datetime as _dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CL = os.path.normpath(os.path.join(REPO, "..", "CityLauncher"))
SRC = os.path.join(CL, "emailer", "templates")
MIRROR = os.path.join(REPO, "orchestration_v2", "templates")
PAGE = os.path.join(REPO, "orchestration_v2", "email_templates.html")
MANIFEST = os.path.join(REPO, "ops", "autodeploy", "deploy_manifest.txt")

SPECIAL_RE = re.compile(r"<!--LAUNCH_SPECIAL_START-->.*?<!--LAUNCH_SPECIAL_END-->", re.S)
AUX = {  # letters in the send lane that no wave category draws (their sender is named)
    "human_followup_outreach.html": "resend_human_clicks.py -- re-send to people who clicked the broken page (HUMAN-CLICKS-1)",
    "relink_apology_outreach.html": "resend_broken_link.py -- apology + working link after a broken-link send",
    "federation_intro_outreach.txt": "federation secretaries -- a permission request, plain text; sent by David (RUL-099 exception)",
}
TITLES = {
    "agency_outreach.html": "Property Agencies",
    "travel_agency_outreach.html": "Travel Agencies",
    "tour_guide_outreach.html": "Tour Guides & Operators",
    "cars_dealer_outreach.html": "Car Dealers",
    "collectors_dealer_outreach.html": "Collector Dealers",
    "tutor_institution_outreach.html": "Tutor Institutions",
    "service_company_outreach.html": "Service Companies",
    "property_outreach.html": "Property — individual sellers",
    "tutors_outreach.html": "Tutors — individual",
    "tutors_outreach.b.html": "Tutors — arm B (A/B test)",
    "collectors_outreach.html": "Collectors — individual",
    "services_casuals_outreach.html": "Services — casual",
    "services_technical_outreach.html": "Services — technical",
    "adventures_accommodation_outreach.html": "Stays — accommodation",
    "adventures_experiences_outreach.html": "Adventures — experiences",
    "sports_club_outreach.html": "Sports Clubs (the RUL-099 reference shape)",
    "adventures_outfitter_outreach.html": "Adventure outfitters — register letter",
    "human_followup_outreach.html": "Human follow-up (clicked the broken page)",
    "relink_apology_outreach.html": "Re-link apology",
    "federation_intro_outreach.txt": "Federation secretaries — permission letter",
    "placement_agency_outreach.html": "Placement Agencies",
}
PERSONAL_RE = re.compile(r"(\+27\s?\d|0\d{2}[ -]?\d{3}[ -]?\d{4}|call me|phone me|reply to this email|just reply|reaches me directly|contact me)", re.I)
SOURCE_LINE_RE = re.compile(r"(found your|where we got your|from your federation|published (?:club |member )?list|public(?:ly)? (?:published )?register|your (?:state|national) register)", re.I)
BROWSE_RE = re.compile(r'href="https://trustsquare\.co/?(?:\?[^"]*)?"')
WAVE_TAG_RE = re.compile(r"trustsquare\.co[^\"'\s]*[?&]src=")


def read(p):
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def read_bytes(p):
    with open(p, "rb") as fh:
        return fh.read()


# ── the send lane, read from the code that sends ───────────────────────────
def parse_emailer():
    src = read(os.path.join(CL, "emailer", "emailer.py"))
    m = re.search(r"\nTEMPLATES\s*=\s*\{(.*?)\n\}", src, re.S)
    if not m:
        raise SystemExit("emailer.py: TEMPLATES dict not found")
    files = {}   # file -> [keys]
    for key, fn in re.findall(r"'([^']+)'\s*:\s*TMPL_DIR\s*/\s*'([^']+)'", m.group(1)):
        files.setdefault(fn, []).append(key)
    subj = {}
    m2 = re.search(r"def subject_for\(.*?\n    subjects = \{(.*?)\n    \}", src, re.S)
    if m2:
        for key, text in re.findall(r"'([^']+)'\s*:\s*f?['\"](.*?)['\"],?\s*(?:#.*)?\n", m2.group(1)):
            subj[key] = text.replace("{city}", "{{city}}")
    m3 = re.search(r"\nAGENCY_CATEGORIES\s*=\s*\{(.*?)\n\}", src, re.S)
    agency = set(re.findall(r"'([^']+)'", m3.group(1))) if m3 else set()
    def _const(name):
        mm = re.search(r"\n%s\s*=\s*'([^']+)'" % name, src)
        return mm.group(1) if mm else "?"
    consts = {k: _const(k) for k in ("FROM_ADDRESS", "FROM_ADDRESS_EDU", "REPLY_TO")}
    return files, subj, agency, consts


def parse_policy():
    p = json.load(open(os.path.join(CL, "emailer", "waves_policy.json"), encoding="utf-8"))
    d = p.get("defaults", {})
    return {
        "batch_size": d.get("batch_size"), "min_gap_days": d.get("min_gap_days"),
        "send_days": d.get("send_days") or [], "bounce_stop_pct": d.get("bounce_stop_pct"),
        "bounce_stop_min_bounces": d.get("bounce_stop_min_bounces"), "max_complaints": d.get("max_complaints"),
        "daily_send_cap": d.get("daily_send_cap"), "send_timezone": d.get("send_timezone"),
        "domain_bounce_window_days": d.get("domain_bounce_window_days"),
        "email_variants": d.get("email_variants") or {}, "blocked": d.get("blocked_categories") or [],
        "person_only": d.get("person_only_categories") or [],
        "ramp": p.get("ramp") or {}, "agency_categories": p.get("agency_categories") or [],
    }


def special_state():
    """Mirror of launch_codes.enabled(): flag + secret + deadline + the date gate."""
    env = {}
    envp = os.path.join(CL, ".env")
    if os.path.exists(envp):
        for line in read(envp).splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    flag = env.get("LAUNCH_SPECIAL_ENABLED", "").lower() in ("1", "true", "yes", "on")
    deadline = env.get("LAUNCH_SPECIAL_DEADLINE", "")
    secret = bool(env.get("LAUNCH_CODE_SECRET"))
    try:
        from zoneinfo import ZoneInfo
        today = _dt.datetime.now(ZoneInfo("Africa/Johannesburg")).date().isoformat()
    except Exception:
        today = _dt.datetime.now(_dt.timezone.utc).date().isoformat()
    on = bool(flag and secret and deadline and today <= deadline)
    return {"on": on, "flag": flag, "deadline": deadline or "(none)", "today": today,
            "env_readable": os.path.exists(envp)}


def as_sent(raw, special_on):
    return raw if special_on else SPECIAL_RE.sub("", raw)


def send_set(files, policy):
    """[(filename, group, keys, note)] in display order."""
    out = []
    for fn in sorted(files):
        keys = files[fn]
        if any(k.endswith(":register") for k in keys) or any("Sports Club" in k for k in keys):
            grp = "clubs"
        elif set(keys) & AGENCY_SET:
            grp = "org"
        else:
            grp = "ind"
        out.append((fn, grp, keys, ""))
    for cat, arms in sorted(policy["email_variants"].items()):
        for arm in arms:
            if arm == "a":
                continue
            base = None
            for fn, keys in files.items():
                if cat in keys:
                    base = fn
            if base:
                bf = base[:-5] + "." + arm + ".html"
                if os.path.exists(os.path.join(SRC, bf)) and not any(x[0] == bf for x in out):
                    out.append((bf, "other", [cat], "EMAIL-VARIANT-1 arm '%s' for %s -- assigned deterministically on prospect id" % (arm, cat)))
    for fn, note in AUX.items():
        if os.path.exists(os.path.join(SRC, fn)):
            out.append((fn, "other", [], note))
    return out


# ── badges: computed from the sending file, never typed ────────────────────
def badge(text, tone):
    col = {"green": "#16a34a", "blue": "#1d4ed8", "amber": "#b45309", "red": "#b91c1c", "grey": "#5f6b78"}[tone]
    return ('<span style="font-size:10.5px;font-weight:700;color:%s;background:%s18;border:1px solid %s55;'
            'border-radius:8px;padding:2px 7px;margin:0 5px 4px 0;display:inline-block">%s</span>' % (col, col, col, text))


def badges_for(fn, raw, sent, special):
    b = []
    if "{{unsubscribe_link}}" in raw or "{{optout_link}}" in raw:
        b.append(badge("unsubscribe", "green"))
    else:
        b.append(badge("no unsubscribe (not a cold letter)", "grey"))
    if "<!--LAUNCH_SPECIAL_START-->" in raw:
        if special["on"]:
            b.append(badge("launch special ON until %s" % special["deadline"], "amber"))
        else:
            b.append(badge("special block stripped · window closed %s" % special["deadline"], "green"))
    else:
        b.append(badge("no launch-special block", "green"))
    b.append(badge("CTA · {{magic_link}}", "blue") if "{{magic_link}}" in raw else badge("no magic-link CTA", "grey"))
    b.append(badge("replies → trustsquare.co/support", "green") if "trustsquare.co/support" in raw else badge("no support route", "amber"))
    hit = PERSONAL_RE.search(re.sub(r"<[^>]+>", " ", sent))
    if hit:
        b.append(badge("PERSONAL CHANNEL: “%s”" % hit.group(0)[:28], "red"))
    b.append(badge("browse link", "green") if BROWSE_RE.search(raw) else badge("no plain browse link", "grey"))
    b.append(badge("wave source tag", "green") if WAVE_TAG_RE.search(raw) else badge("no ?src= tag", "grey"))
    b.append(badge("TrustSquare mark inline", "green") if "trustsquare_icon" in raw else badge("no inline mark", "grey"))
    b.append(badge("says where we got the address", "green") if SOURCE_LINE_RE.search(re.sub(r"<[^>]+>", " ", sent)) else badge("no source line", "grey"))
    return "".join(b)


def card(href, title, meta, badges_html, open_label="Open the real letter ↗", txt=False):
    frame = ('<iframe src="%s" loading="lazy" style="width:200%%;height:340px;transform:scale(.5);'
             'transform-origin:0 0;border:0;pointer-events:none;background:#fff"></iframe>' % href)
    return ('<div style="background:#fff;border:1px solid var(--line);border-radius:13px;overflow:hidden;display:flex;flex-direction:column">\n'
            '  <div style="height:170px;overflow:hidden;position:relative;background:#eef1f5;border-bottom:1px solid var(--line)">\n'
            '    %s\n    <a href="%s" target="_blank" style="position:absolute;inset:0" title="Open %s"></a>\n  </div>\n'
            '  <div style="padding:12px 14px 14px">\n'
            '    <div style="font-weight:800;font-size:14px;color:var(--navy)">%s</div>\n'
            '    <div style="font-size:11.5px;color:var(--muted);margin:2px 0 8px">%s</div>\n'
            '    <div style="margin-bottom:8px">%s</div>\n'
            '    <a href="%s" target="_blank" style="display:inline-block;text-decoration:none;font-size:12px;font-weight:700;'
            'padding:7px 13px;border-radius:9px;background:var(--navy);color:#fff">%s</a>\n  </div>\n</div>\n'
            % (frame, href, href, title, meta, badges_html, href, open_label))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(check_only=False):
    global AGENCY_SET
    files, subj, AGENCY_SET, consts = parse_emailer()
    policy = parse_policy()
    special = special_state()
    lane = send_set(files, policy)
    today = _dt.date.today().strftime("%-d %b %Y") if os.name != "nt" else _dt.date.today().strftime("%d %b %Y")
    stale, written, orphans = [], [], []
    man = read(MANIFEST) if os.path.exists(MANIFEST) else ""
    missing_rows = []

    # 1. mirror
    os.makedirs(MIRROR, exist_ok=True)
    cards = {"org": [], "clubs": [], "ind": [], "other": []}
    for fn, grp, keys, note in lane:
        sp = os.path.join(SRC, fn)
        raw = read(sp)
        sent = as_sent(raw, special["on"])
        mp = os.path.join(MIRROR, fn)
        cur = read_bytes(mp) if os.path.exists(mp) else None
        want = sent.encode("utf-8")
        if cur != want:
            stale.append(fn)
            if not check_only:
                with open(mp, "wb") as fh:
                    fh.write(want)
                written.append(fn)
        row = "orchestration_v2/templates/%s | orchestrator/v2/templates/%s" % (fn, fn)
        if row not in man:
            missing_rows.append(row)
        mtime = _dt.datetime.fromtimestamp(os.path.getmtime(sp)).strftime("%d %b %Y")
        kb = max(1, round(len(want) / 1024))
        subject = next((subj[k] for k in keys if k in subj), "")
        meta = []
        if keys:
            meta.append("drawn by: " + esc(", ".join(keys)))
        if subject:
            meta.append("subject: “" + esc(subject) + "”")
        if note:
            meta.append(esc(note))
        meta.append("%d KB · sending copy last changed %s · as sent today" % (kb, mtime))
        cards[grp].append(card("templates/" + fn, esc(TITLES.get(fn, fn)), " · ".join(meta),
                               badges_for(fn, raw, sent, special), txt=fn.endswith(".txt")))
    lane_names = {x[0] for x in lane}
    for fn in sorted(os.listdir(MIRROR)):
        if fn.endswith((".html", ".txt")) and ".bak" not in fn and fn not in lane_names and fn != "placement_agency_outreach.html":
            orphans.append(fn)

    # 2. placement lane (David's reserved send, lives only here)
    pl = []
    pa = os.path.join(MIRROR, "placement_agency_outreach.html")
    if os.path.exists(pa):
        raw = read(pa)
        pl.append(card("templates/placement_agency_outreach.html", "Placement Agencies — cold invite",
                       "J-1 · cruise · H-2A · education consultancies · %d KB · last changed %s · sending reserved to David (RUL-046)"
                       % (max(1, round(len(raw) / 1024)), _dt.datetime.fromtimestamp(os.path.getmtime(pa)).strftime("%d %b %Y")),
                       badges_for("placement_agency_outreach.html", raw, raw, special)))
    seq = os.path.join(MIRROR, "placement_onboarding", "SEQUENCE.md")
    rows = re.findall(r"^\|\s*(\d)\s*\|\s*(Day \d+)[^|]*\|\s*([^|]+?)\s*\|", read(seq), re.M) if os.path.exists(seq) else []
    for n, day, subject in rows:
        fp = os.path.join(MIRROR, "placement_onboarding", "onboard_%s.html" % n)
        if not os.path.exists(fp):
            continue
        raw = read(fp)
        b = badge("no launch-special block", "green") if "<!--LAUNCH_SPECIAL_START-->" not in raw else badge("launch-special block present", "red")
        b += badge("post-acceptance sequence · no unsubscribe block", "grey") if "{{unsubscribe_link}}" not in raw else badge("unsubscribe", "green")
        if "aunching soon" in raw:
            b += badge("launching soon marker (RUL-051)", "green")
        pl.append(card("templates/placement_onboarding/onboard_%s.html" % n, "%s · %s" % (n, esc(subject)),
                       "%s · %d KB · last changed %s" % (day, max(1, round(len(raw) / 1024)),
                                                                  _dt.datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%d %b %Y")), b))

    # 3. agency-lane design drafts (not in the send lane)
    dz = []
    dd = os.path.join(MIRROR, "agency_lane_design")
    if os.path.isdir(dd):
        for fn in sorted(os.listdir(dd)):
            if fn.endswith(".html"):
                raw = read(os.path.join(dd, fn))
                b = badge("three-lane onboarding block", "blue") if ("agency-import-guide" in raw or "agents-as-a-service" in raw) else badge("no three-lane block", "grey")
                b += badge("NOT what sends today", "amber")
                dz.append(card("templates/agency_lane_design/" + fn, esc(TITLES.get(fn, fn)) + " — design draft",
                               "AGENCY-WAVE-1 design, 23 Aug 2026 · %d KB" % max(1, round(len(raw) / 1024)), b, open_label="Open the draft ↗"))

    # 4. the page
    ramp = policy["ramp"]
    spec_line = ("<strong style=\"color:#b45309\">ON until %s</strong>" % special["deadline"]) if special["on"] else \
                ("OFF — window closed %s (RUL-060(a)); the block is stripped from every letter at send time and from these previews" % special["deadline"])
    days = policy["send_days"]
    daytxt = "every day" if len(days) == 7 else "/".join(days)
    ctx = (
        "<strong style=\"color:var(--navy)\">How the waves run</strong> (read from CityLauncher/emailer/waves_policy.json and emailer.py, %s): "
        "one email per prospect, ever · batch %s, doubling per clean wave (≤%s%% bounce) to a cap of %s · sends %s, at most one wave per city per %s local day (%s) "
        "· stop-loss when bounces exceed %s%% with at least %s bounces, judged per city AND domain-wide over %s days · complaints tolerated: %s "
        "· domain cap %s letters a day · blocked lanes: %s · person-only lanes: %s · A/B arms: %s. "
        "Sender %s (education lane %s); replies go to %s, never to a person (RUL-100). Launch special: %s. "
        "Agency sends are David's own act (RUL-053(f)); the placement lane is reserved (RUL-046). "
        "Every letter the runner sends is filed under MarketSquare/visuals/letters/ (RUL-099(e)). Wave-day checklist: AGENCY_WAVE_RUNBOOK.md."
        % (today, policy["batch_size"], ramp.get("clean_bounce_pct"), ramp.get("max_batch"), daytxt, policy["min_gap_days"], policy["send_timezone"],
           policy["bounce_stop_pct"], policy["bounce_stop_min_bounces"], policy["domain_bounce_window_days"], policy["max_complaints"],
           policy["daily_send_cap"], esc(", ".join(policy["blocked"]) or "none"), esc(", ".join(policy["person_only"]) or "none"),
           esc(", ".join("%s: %s" % (k, "/".join(v)) for k, v in policy["email_variants"].items()) or "none"),
           esc(consts["FROM_ADDRESS"]), esc(consts["FROM_ADDRESS_EDU"]), esc(consts["REPLY_TO"]), spec_line))
    n_lane = len(lane)

    def section(title, items):
        if not items:
            return ""
        return "<h2>%s</h2>\n<div class=\"grid\">%s</div>\n" % (title, "".join(items))

    html = (
        "<!doctype html><html><head><meta charset=\"utf-8\">\n"
        "<title>Orchestration v2 — Email Templates</title>\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        "<style>\n"
        ":root{--navy:#0c1a2e;--ink:#1b2733;--muted:#5f6b78;--line:#e3e7ec;--bg:#f6f8fa;--card:#fff}\n"
        "body{margin:0;background:var(--bg);color:var(--ink);font-family:'Segoe UI',system-ui,sans-serif}\n"
        ".doc{max-width:1180px;margin:0 auto;padding:26px 20px 60px}\n"
        "header.hd{background:var(--navy);color:#fff;border-radius:16px;padding:22px 24px;margin-bottom:20px}\n"
        "header.hd .k{font-size:11px;letter-spacing:2px;font-weight:800;color:#7fd6c2;text-transform:uppercase}\n"
        "header.hd h1{margin:6px 0 4px;font-size:26px}\n"
        "header.hd p{margin:0;color:#c6d2e2;font-size:13.5px}\n"
        "h2{font-size:16px;margin:26px 0 12px;color:var(--navy)}\n"
        ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}\n"
        ".ctx{background:#fff;border:1px solid var(--line);border-radius:13px;padding:13px 16px;font-size:12.5px;color:var(--muted);line-height:1.55}\n"
        ".note{background:#fff7ed;border:1px solid #fdba74;border-radius:13px;padding:11px 16px;font-size:12.5px;color:#7c2d12;line-height:1.5;margin-top:8px}\n"
        "</style></head><body><div class=\"doc\">\n"
        "<header class=\"hd\">\n  <div class=\"k\">Solar Council · TrustSquare</div>\n"
        "  <h1>Email Templates — the letters the waves send</h1>\n"
        "  <p>%d letters in the send lane, shown exactly as the wave runner sends them today — each preview is a byte-faithful copy of the sending file in "
        "CityLauncher/emailer/templates (the host-side wave runner's own folder), with the launch-special block handled the way the emailer handles it. "
        "Rebuilt %s by scripts/build_email_templates_page.py; every badge and date is computed from the sending copies, none is typed. Click any card to open the real letter.</p>\n"
        "</header>\n"
        "<div style=\"display:flex;gap:8px;margin-bottom:18px\">\n"
        "  <a href=\"cockpit.html\" style=\"text-decoration:none;font-size:13px;font-weight:700;padding:9px 16px;border-radius:10px;background:#fff;color:var(--navy);border:1.5px solid var(--line)\">\U0001F6F0️ Control Room</a>\n"
        "  <a href=\"durability_map.html\" style=\"text-decoration:none;font-size:13px;font-weight:700;padding:9px 16px;border-radius:10px;background:#fff;color:var(--navy);border:1.5px solid var(--line)\">\U0001F9ED Durability Map</a>\n"
        "  <a href=\"email_templates.html\" style=\"text-decoration:none;font-size:13px;font-weight:700;padding:9px 16px;border-radius:10px;background:var(--navy);color:#fff;border:1.5px solid var(--navy)\">\U0001F4E7 Email Templates</a>\n"
        "</div>\n"
        "<div class=\"ctx\">%s</div>\n"
        % (n_lane, today, ctx)
    )
    html += section("Sending now — organisations: agencies, dealers, operators, institutions (%d)" % len(cards["org"]), cards["org"])
    html += section("Sending now — clubs and published registers, the RUL-099 letter shape (%d)" % len(cards["clubs"]), cards["clubs"])
    html += section("Sending now — individual sellers (%d)" % len(cards["ind"]), cards["ind"])
    html += section("Also in the send lane — A/B arms, follow-ups and the permission letter (%d)" % len(cards["other"]), cards["other"])
    html += section("Placement lane — David's reserved send (RUL-046): the invite and the 8-email onboarding sequence, Day 0–18", pl)
    if dz:
        html += section("Agency-lane design drafts — NOT in the send lane", dz)
        html += ("<div class=\"note\">These three were built on 23 Aug 2026 for the console-link agency wave (three-lane onboarding block: concierge / console self-serve / IT import guide). "
                 "The agency letters the runner actually sends do not carry that block yet — the gap is regression ledger RG-0346 (OPEN) and it prints READY TO LOCK when the sending copies carry the agency story with a console link.</div>\n")
    html += ("<div class=\"ctx\" style=\"margin-top:26px\">Method: source folder %s · mirror folder orchestration_v2/templates/ (deployed to /orchestrator/v2/templates/) · "
             "regression ledger RG-0344 fails the day a sending copy changes without this page being rebuilt. Rebuild: <code>python3 scripts/build_email_templates_page.py</code></div>\n"
             % esc(os.path.relpath(SRC, os.path.dirname(REPO)).replace(os.sep, "/")))
    html += "</div>\n<script src=\"/static/ts_report.js?v=6\" defer></script>\n</body></html>\n"

    # --check judges the page by what it REFERENCES, not by bytes: the build stamp carries
    # today's date, so a byte compare would call the page stale every morning for nothing.
    page_txt = read(PAGE) if os.path.exists(PAGE) else ""
    page_stale = (not page_txt) or ("build_email_templates_page.py" not in page_txt) or \
                 any(('href="templates/%s"' % fn) not in page_txt for fn, _g, _k, _n in lane)
    if not check_only:
        with open(PAGE, "wb") as fh:
            fh.write(html.encode("utf-8"))

    # 5. report
    print("[email-page] send lane: %d letters (%d org, %d clubs/registers, %d individual, %d other) · placement %d · design drafts %d"
          % (n_lane, len(cards["org"]), len(cards["clubs"]), len(cards["ind"]), len(cards["other"]), len(pl), len(dz)))
    print("[email-page] launch special: %s (flag=%s deadline=%s today=%s)" % ("ON" if special["on"] else "OFF", special["flag"], special["deadline"], special["today"]))
    if check_only:
        print("[email-page] --check: %d mirror file(s) stale: %s" % (len(stale), ", ".join(stale) or "none"))
        print("[email-page] --check: page %s" % ("STALE" if page_stale else "current"))
    else:
        print("[email-page] mirror: %d rewritten (%s), %d unchanged" % (len(written), ", ".join(written) or "-", n_lane - len(written)))
        print("[email-page] page: rewritten (%d bytes)" % len(html))
    if orphans:
        print("[email-page] NOTE orphan previews not in the send lane (nothing sends them): " + ", ".join(orphans))
    if missing_rows:
        print("[email-page] MANIFEST rows missing -- add to ops/autodeploy/deploy_manifest.txt:")
        for r in missing_rows:
            print("    " + r)
    return 1 if (check_only and (stale or page_stale)) else 0


AGENCY_SET = set()
if __name__ == "__main__":
    sys.exit(build(check_only="--check" in sys.argv))
