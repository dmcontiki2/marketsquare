#!/usr/bin/env python3
# test_tester_intake.py - in-app tester fault intake tripwires (MAINT-B1b, 5 Aug 2026).
# Source-level guards. What these protect: the pre-launch month depends on testers
# being able to file a fault IN THE APP and on every filed fault producing a reference
# and an acknowledgement. A silent regression here means testers report into a void.
import os, re, sys

HERE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

# Pages the tab is deliberately NOT on. Everything else that SHIPS must carry it —
# the list is derived from the deploy manifest, never hand-typed, because a hand-typed
# list is exactly how three tester-reachable pages (ranking explainer, agency import
# guide, agents-as-a-service) were missed on 5 Aug and the tripwire still read green.
NOT_TESTER_FACING = set()   # 5 Aug: David ruled the tab belongs on EVERY page, his own
                            # console included. Nothing is excluded. Keep it that way.


def _manifest_html(here):
    """Every .html the site actually deploys, as (source, destination) pairs."""
    out = []
    mp = os.path.join(here, "ops", "autodeploy", "deploy_manifest.txt")
    with open(mp, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if "|" not in line:
                continue
            parts = [x.strip() for x in line.split("|")]
            src, dest = parts[0], parts[1] if len(parts) > 1 else parts[0]
            if src.endswith(".html") and src not in NOT_TESTER_FACING:
                out.append((src, dest))
    return out


def _is_email_body(here, src, dest):
    """EMAIL-NOT-A-PAGE-1 (19 Aug 2026). An email BODY is not a page a tester can land on,
    so requiring the fault widget on one was a verdict that could never be satisfied
    correctly: ts_report.js cannot run in a mail client, and shipping the tag would put a
    <script src=...> inside outbound mail - spam-filter poison and a tracker-shaped artifact
    in an invitation. That single wrong assertion put DANGER on 46 pre-deploy scans from
    4 Aug onward and aborted the strict-mode nightly, which is exactly how a real fault gets
    waved through.

    Detected STRUCTURALLY, never by a hand-typed name (the same reason the manifest drives
    this file): published under a templates/ directory AND carrying the 600px email wrapper
    AND containing no <script> at all. A real PAGE added under templates/ will carry a script
    or lack the email wrapper, so it falls through to the page rule and must carry the widget.
    The classification fails SAFE - anything ambiguous is treated as a page."""
    if "/templates/" not in dest.replace("\\", "/"):
        return False
    try:
        body = open(os.path.join(here, src), encoding="utf-8", errors="replace").read()
    except OSError:
        return False
    return "<script" not in body.lower() and re.search(r"max-width:\s*600px", body) is not None


def tester_pages(here):
    """Every deployed .html a tester can actually land on - email bodies excluded,
    and so is the Basic-Auth-gated /orchestrator/ ops realm (OPS-REALM-EXEMPT-1,
    30 Aug 2026): a tester cannot LAND on a page that answers 401 anonymously, so
    the widget requirement never applied there. The 8-scan red RG-0114 caught was
    this guard demanding ts_report.js on the contagion model + defence map the
    moment they joined the manifest (dest orchestrator/...) -- gated ops documents,
    not tester pages. Judged by DEST (where it is served), never by source name."""
    return [s for s, d in _manifest_html(here)
            if not _is_email_body(here, s, d)
            and not d.strip().lstrip("/").startswith("orchestrator/")]


def email_bodies(here):
    """The deployed .html files that are email bodies, not pages."""
    return [s for s, d in _manifest_html(here) if _is_email_body(here, s, d)]

def _read(name):
    with open(os.path.join(HERE, name), encoding="utf-8", errors="replace") as f:
        return f.read()

def test_intake_table_survives():
    src = _read("bea_main.py")
    assert "CREATE TABLE IF NOT EXISTS app_faults" in src, "app_faults table lost"
    for col in ("ref", "fault_code", "dup_of", "recurrence", "retest_sent_at"):
        assert re.search(r"\n\s+" + col + r"\s+\w", src[src.find("CREATE TABLE IF NOT EXISTS app_faults"):][:2000]), \
            "app_faults column lost: " + col

def test_intake_endpoint_present():
    src = _read("bea_main.py")
    assert '@app.post("/app/fault")' in src, "the tester intake endpoint is gone"
    assert '@app.get("/admin/faults")' in src, "the maintenance queue endpoint is gone"
    assert '@app.post("/admin/faults/{fid}/close-send")' in src, "the closure letter path is gone"

def test_intake_is_fail_closed():
    src = _read("bea_main.py")
    i = src.find("def _fault_report_enabled")
    assert i > 0, "the launch-switch reader is gone"
    assert "return False" in src[i:i+700], "flag read must fail CLOSED on error"
    j = src.find('@app.post("/app/fault")')
    blk = src[j:j+1600]
    assert "_fault_report_enabled()" in blk, "intake no longer checks the launch switch"
    assert "_fault_caller_ok" in blk, "intake no longer requires tester credentials"

def test_every_fault_gets_a_reference_and_ack():
    src = _read("bea_main.py")
    assert 'ref = "TS-%04d" % fid' in src, "the tester-facing reference (TS-nnnn) is gone"
    assert 'os.getenv("FAULT_ACK_SEND", "1")' in src, \
        "the auto-ACK default flipped off, or its kill switch was renamed"
    assert "_send_system_email" in src[src.find("Auto-ACK"):src.find("Auto-ACK") + 1200], \
        "the ACK no longer uses the Resend-first send path"

def test_close_letter_closes_with_a_response():
    """NO-RETEST-1 (David, 11 Aug 2026): there are no retests. A complaint is fixed,
    verified on named machine evidence, and CLOSED with a letter telling the reporter
    what changed. Their 'still broken' reply always reopens."""
    src = _read("bea_main.py")
    i = src.find("def _fault_close_email")
    assert i > 0, "the closure letter builder is gone"
    blk = src[i:i + 1600]
    assert "What was changed" in blk, "the closure letter no longer states what was fixed"
    assert "closed" in blk, "the closure letter no longer tells the reporter it is closed"
    assert "awaiting-retest" not in src, "the retired retest-wait status is back (NO-RETEST-1)"
    assert "/retest-" not in src, "a retest route is back in bea_main.py (NO-RETEST-1)"

def test_reporter_widget_is_first_party_and_flag_gated():
    js = _read("ts_report.js")
    # RG-0025: no third-party origin may be contacted from any tester-facing page.
    origins = set(re.findall(r"https?://[a-zA-Z0-9.\-]+", js))
    assert origins <= {"https://trustsquare.co"}, \
        "third-party origin in the tester widget (RG-0025): " + ", ".join(sorted(origins))
    assert "document.createElement('script')" not in js and 'createElement("script")' not in js, \
        "the tester widget injects a script tag - it must stay dependency-free"
    assert "d.fault_report" in js, "the widget no longer honours the server flag"
    assert "isTester()" in js, "the widget no longer restricts itself to testers"
    assert "window.DEMO_MODE === true" in js, "demo-mode guard lost (CLAUDE.md demo-wiring rule)"

def test_widget_is_wired_into_every_tester_page():
    pages = tester_pages(HERE)
    assert len(pages) >= 14, "the manifest lists only %d tester pages - is it truncated?" % len(pages)
    missing = [n for n in pages
               if os.path.isfile(os.path.join(HERE, n)) and "ts_report.js" not in _read(n)]
    assert not missing, ("a tester could land on these pages with no way to report a fault: "
                         + ", ".join(missing))

def test_dashboard_switch_is_usable_during_launch_mode():
    d = _read("dashboard.server.html")
    assert "ls_m_fault" in d, "the fault-reporting switch is gone from the Launch Switch page"
    assert "'fault_report'" in d or '"fault_report"' in d, "the switch is not bound to the server flag"
    assert "id!=='ls_m_fault'" in d.replace(" ", ""), \
        ("the fault switch lost its exemption from the launch-mode disable rule - it would render "
         "greyed out during exactly the month it is needed")


def test_a_signed_in_account_can_file():
    """The 5 Aug 401: the tab rendered for superusers but the POST refused them, because
    ms.js declares API_KEY with `const` (not on window) and superusers never enter the
    reviewer code. Every in-app report failed. Both halves of the fix are asserted here."""
    src = _read("bea_main.py")
    assert "def _fault_known_user" in src, "the account-is-a-credential check is gone"
    assert "_fault_caller_ok(x_review_token, ts_review, x_api_key, reporter_email)" in src, \
        "the intake no longer accepts a signed-in account - superuser reports will 401 again"
    js = _read("ms.js")
    assert "window.API_KEY = API_KEY" in js, \
        "ms.js stopped exposing API_KEY on window - the widget's fallback silently dies again"


def test_reading_reports_is_stricter_than_filing_them():
    """A fault carries the page you were on, your console output and your screenshot.
    Knowing someone's address must never be enough to read it."""
    src = _read("bea_main.py")
    i = src.find('@app.get("/app/faults/mine")')
    assert i > 0, "the tester's own-reports endpoint is gone"
    blk = src[i:i + 1400]
    assert "_fault_caller_ok(x_review_token, ts_review, x_api_key)" in blk, \
        "the read path now accepts a bare email address - anyone knowing an address could " \
        "read that person's fault reports"


def test_intake_asks_three_things_not_five():
    """David, 5 Aug: 'we basically paste a snip and say what is wrong... this simple will
    increase fix rate tremendously.' Never make someone classify a fault to report it."""
    js = _read("ts_report.js")
    assert "How badly did it affect you" not in js, "the severity picker is back"
    assert "Which part of the app" not in js, "the area picker is back"
    src = _read("bea_main.py")
    assert "def _fault_bin_from_page" in src, \
        "the bin is no longer derived from the page - dropping the picker would lose the taxonomy"
    assert 'severity = "major"' in src, \
        "unclassified faults no longer default to major - they would sink to the bottom unseen"


def test_paste_is_the_attachment_path():
    """David, 5 Aug: 'can\'t we just have a paste option?' Win+Shift+S then Ctrl+V is
    two things people already do; a capture button was one thing they had to learn."""
    js = _read("ts_report.js")
    assert "addEventListener('paste'" in js, "the paste handler is gone - Ctrl+V would do nothing"
    assert "clipboardData" in js, "the clipboard read is gone"
    assert "e.dataTransfer" in js, "drag-and-drop (same handler, free) is gone"
    assert "removeEventListener('paste'" in js, \
        "the document-level paste listener is never unhooked - it would keep firing after close"
    assert "html2canvas" not in js and "cdn" not in js.lower().split("*/")[-1], \
        "a third-party capture library appeared (RG-0025)"


def test_maintenance_key_opens_faults_and_nothing_else():
    """The whole point of a scoped key is the scope. If MS_MAINT_KEY ever guards an
    endpoint outside the fault lane, a leaked maintenance credential stops costing us a
    complaint list and starts costing us the platform (SEC-1, 23 Jul 2026)."""
    src = _read("bea_main.py")
    assert "def _require_maint" in src, "the scoped maintenance credential is gone"
    guarded = re.findall(r"@app\.(?:get|post|put|delete)\(\"([^\"]+)\"\)\s*\n(?:async )?def [^\n]*\n?[^\n]*Depends\(_require_maint\)", src)
    # GATE-EXEMPT-MAINT-1 (David's ruling, 13 Aug 2026; migration 018, live 14 Aug): the maint
    # lane's scope is the fault endpoints PLUS the maintenance dashboard -- "and ONLY those"
    # (RG-0065). This guard asserted the pre-ruling scope, so it failed on CORRECT code and put
    # DANGER on every deploy; a verdict that is always wrong is how a real one gets waved through.
    # It stays strict: the allowlist is exact, and anything outside it still fails.
    MAINT_SCOPE_EXACT = {"/dashboard/maint"}
    MAINT_SCOPE_PREFIX = ("/admin/faults",)
    stray = [r for r in guarded
             if r not in MAINT_SCOPE_EXACT and not r.startswith(MAINT_SCOPE_PREFIX)]
    assert not stray, "MS_MAINT_KEY now opens endpoints outside the fault lane: " + ", ".join(stray)
    assert src.count("Depends(_require_maint)") == 5, \
        "expected exactly 5 maintenance-scoped endpoints (4x /admin/faults + /dashboard/maint), found %d" \
        % src.count("Depends(_require_maint)")
    i = src.find('@app.post("/admin/flags")')
    assert "Depends(_require_admin)" in src[i:i + 200], \
        "the launch switches must stay on the FULL admin credential, never the scoped one"
    i = src.find("def _require_maint")
    body = src[i:src.find("\ndef ", i + 10)]      # the whole function, not a guessed window
    assert "compare_digest" in body, "the maintenance key comparison is no longer constant-time"
    assert "MS_MAINT_KEY" in body, "the scoped key is no longer checked at all"


def test_labels_do_not_impersonate_buttons():
    """The recurring class behind TS-0001, TS-0002 and TS-0003: an element that LOOKS like a
    control and is not one. Three of the first six tester reports were this same fault wearing
    different clothes — a count, a badge, a pill. A label may not carry button styling."""
    css = _read("ms.css")
    i = css.find(".wl-sig-badge{")
    assert i > 0, "the wishlist signal badge style is gone"
    rule = css[i:css.find("}", i)]
    assert "cursor:default" in rule, \
        "the signal badge lost cursor:default - it reads as clickable again (TS-0002/0003)"
    assert "border-radius:50px" not in rule, "the badge is a pill again, which reads as a button"
    js = _read("ms.js")
    i = js.find("const badge = s.signal_type")
    assert i > 0, "the signal badge label line is gone"
    line = js[i:js.find("\n", i)]
    assert "'viewed'" in line and "'VIEW'" not in line, \
        "the badge label reverted to an imperative verb - 'viewed' describes, 'VIEW' instructs"


def test_photo_gate_covers_the_sellers_own_brand():
    """TS-0004: a honey jar carrying the producer's own label reached the live feed.
    The anonymiser hunted agency logos and number plates - property and cars framing -
    and never considered that for a home producer the product label IS the identity."""
    src = _read("bea_main.py")
    i = src.find("_ANON_SCAN_PROMPT = ")
    assert i > 0, "the photo anonymiser prompt is gone"
    prompt = src[i:src.find("_ANON_SCAN_PROMPT_TOURS", i)]
    assert "SELLER'S OWN brand" in prompt, \
        "the anonymiser no longer looks for the seller's own brand on the goods (TS-0004)"
    assert "Nikon" in prompt or "resold" in prompt, \
        "the carve-out for mass-market manufacturer marks is gone - it would start " \
        "blurring the Toyota badge on a car someone is reselling"


def test_every_photo_door_applies_the_same_rules():
    """Two doors let photos into the app: seller upload and agency import. On 5 Aug the
    agency door was found to skip the moderation flag entirely — anonymity was checked,
    acceptability was not. A rule that holds at one door and not the other is not a rule."""
    src = _read("bea_main.py")
    i = src.find("def _anon_photo_pass")
    assert i > 0, "the agency-import photo pass is gone"
    blk = src[i:i + 3200]
    assert 'scan.get("flag") == "inappropriate"' in blk, \
        "the agency import no longer checks the moderation flag - an anonymous but " \
        "unacceptable photo could be attached from an agency feed"
    assert "_anon_photo_scan" in blk, "the agency import stopped using the shared vision scan"


def test_email_bodies_never_carry_script():
    """The other half of EMAIL-NOT-A-PAGE-1. Email bodies are exempt from the widget, so
    this is the assertion that keeps that exemption honest: they must carry NO script at
    all - not ts_report.js, not a third party (RG-0025). Exempting them from one rule
    without binding them to a stricter one is how an exemption becomes a hole."""
    bodies = email_bodies(HERE)
    assert len(bodies) >= 14, \
        "only %d email bodies classified - the structural test or the manifest changed" % len(bodies)
    dirty = [n for n in bodies
             if os.path.isfile(os.path.join(HERE, n)) and "<script" in _read(n).lower()]
    assert not dirty, ("a script tag reached an outbound email body: " + ", ".join(dirty))


def test_widget_is_deployable():
    mani = _read(os.path.join("ops", "autodeploy", "deploy_manifest.txt"))
    assert "ts_report.js" in mani, "ts_report.js is not on the deploy manifest - it would never ship"

if __name__ == "__main__":
    failed = 0
    for name, fn in sorted({k: v for k, v in list(globals().items())
                            if k.startswith("test_") and callable(v)}.items()):
        try:
            fn(); print("PASS  " + name)
        except AssertionError as e:
            failed += 1; print("FAIL  " + name + " - " + str(e))
        except Exception as e:
            failed += 1; print("FAIL  " + name + " - " + type(e).__name__ + ": " + str(e))
    sys.exit(1 if failed else 0)
