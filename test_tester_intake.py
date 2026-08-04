#!/usr/bin/env python3
# test_tester_intake.py - in-app tester fault intake tripwires (MAINT-B1b, 5 Aug 2026).
# Source-level guards. What these protect: the pre-launch month depends on testers
# being able to file a fault IN THE APP and on every filed fault producing a reference
# and an acknowledgement. A silent regression here means testers report into a void.
import os, re, sys

HERE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

PAGES = ["marketsquare.html", "marketsquare_admin.html", "support.html", "terms.html",
         "privacy.html", "adventures_au_map.html", "adventures_bw_map.html",
         "adventures_c2c_map.html", "adventures_de_map.html", "adventures_mz_map.html",
         "adventures_na_map.html", "adventures_reserve_map.html", "adventures_uk_map.html",
         "adventures_us_map.html"]

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
    for name in PAGES:
        p = os.path.join(HERE, name)
        if not os.path.isfile(p):
            continue
        assert "ts_report.js" in _read(name), "report widget missing from " + name

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
