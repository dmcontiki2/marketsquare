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


def tester_pages(here):
    """Every .html the site actually deploys, minus the operator console."""
    out = []
    mp = os.path.join(here, "ops", "autodeploy", "deploy_manifest.txt")
    with open(mp, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if "|" not in line:
                continue
            src = line.split("|")[0].strip()
            if src.endswith(".html") and src not in NOT_TESTER_FACING:
                out.append(src)
    return out

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
    assert '@app.post("/admin/faults/{fid}/retest-send")' in src, "the retest letter path is gone"

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

def test_retest_letter_asks_for_confirmation():
    src = _read("bea_main.py")
    i = src.find("def _fault_retest_email")
    assert i > 0, "the retest letter builder is gone"
    blk = src[i:i + 1400]
    assert "What was changed" in blk, "the retest letter no longer states what was fixed"
    assert "repeat the steps" in blk, "the retest letter no longer asks the tester to retest"

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


def test_snip_is_first_party():
    js = _read("ts_report.js")
    assert "getDisplayMedia" in js, "the screen-snip button is gone"
    assert "html2canvas" not in js, "a third-party capture library appeared (RG-0025)"


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
