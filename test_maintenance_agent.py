#!/usr/bin/env python3
# test_maintenance_agent.py - Maintenance Agent tripwires (B1, 29 Jul 2026).
# Source-level guards: the complaint pipeline must keep its fault codes, its
# immediate ACK, and a WORKING send path — regressions here mean complainants
# silently stop hearing back, the worst possible launch failure.
import os, re, sys

HERE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

def _read(name):
    with open(os.path.join(HERE, name), encoding="utf-8", errors="replace") as f:
        return f.read()

def test_fault_code_column_and_assignment():
    src = _read("bea_main.py")
    assert "ALTER TABLE email_triage ADD COLUMN fault_code" in src, "fault_code column migration lost"
    assert re.search(r'fault_code = f"\{result\.get\(.bin., .MISC.\)\}-\{_rowid\}"', src), \
        "fault-code assignment (BIN-rowid) lost from the inbound handler"

def test_triage_bins_present():
    src = _read("bea_main.py")
    assert '\\"bin\\": the app area' in src or '"bin\\": the app area' in src, \
        "triage prompt no longer asks for the fault bin"
    assert '"bin": _bin' in src, "triage result no longer carries the bin"

def test_ack_always_sends_except_spam():
    src = _read("bea_main.py")
    i = src.find('MAINT-B1 ACK')
    assert i > 0, "the ACK block is gone"
    blk = src[i:i+900]
    assert 'category != "spam"' in blk, "ACK must send for every non-spam complaint"
    assert 'MAINT_ACK_SEND' in blk, "ACK kill switch (MAINT_ACK_SEND) lost"
    assert "_smtp_send_reply" in blk, "ACK no longer uses the Resend-first send path"

def test_auto_reply_gate_not_gmail_only():
    # CORRECTED 21 Aug 2026 (TRUTH-REVIEW-1): the original pinned the SPELLING
    # os.getenv("RESEND_API_KEY"). ENVKEY-1 (19 Aug) rightly converted that read to
    # ai_provider.envkey() -- systemd does not export .env, so the bare form is the
    # actual bug -- and this guard then sat red for 10 scans against CORRECT code
    # (RG-0114 caught the sitting). Assert the PROPERTY: the gate consults Resend
    # via the envkey path, with the Gmail fallback -- and the outlawed bare form
    # must stay gone (a red here is a CODE-PATTERN claim, never a runtime one).
    src = _read("bea_main.py")
    assert 'and (bool(ai_provider.envkey("RESEND_API_KEY")) or bool(GMAIL_APP_PASSWORD))' in src, \
        "auto-reply gate regressed: must consult Resend (via envkey, ENVKEY-1) with Gmail fallback"
    assert 'and (bool(os.getenv("RESEND_API_KEY")) or bool(GMAIL_APP_PASSWORD))' not in src, \
        "auto-reply gate re-grew a bare os.getenv RESEND read (ENVKEY-1 class: invisible on the server)"

def test_escalation_brief_wired():
    # B3 (11 Aug 2026): the safety/legal/cost brief. Three properties must hold:
    # (1) categories come FROM the agent (import, not copy) so a new refuse marker
    #     can never silently miss the brief; (2) the one-tick format survives;
    # (3) the selftest exists so the format is provable offline.
    src = _read(os.path.join("scripts", "escalation_brief.py"))
    assert "from maintenance_agent import REFUSE_LEGAL_COSTLY, REFUSE_TRUST_CORE" in src, \
        "brief no longer imports the agent's refuse markers -- category drift now possible"
    assert "TICK: reply" in src, "one-tick action line lost from the brief format"
    assert "never block" in src, "the reports-inform-never-block contract line lost"
    assert "--selftest" in src, "brief selftest entry point lost"


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted({k: v for k, v in list(globals().items())
                            if k.startswith("test_") and callable(v)}.items()):
        try:
            fn(); print("PASS  " + name)
        except AssertionError as e:
            failed += 1; print("FAIL  " + name + " - " + str(e))
    sys.exit(1 if failed else 0)
