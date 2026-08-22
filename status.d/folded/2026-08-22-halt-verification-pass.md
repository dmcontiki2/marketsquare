**D-7 HALT verification pass (22 Aug, 07:25–07:40 SAST).** The three-cycle forensic programme completed
at 07:22; this pass re-probed its verdict live rather than repeating it. Verdict UNCHANGED: **HOLD** —
Hardening and Hack-proofness RED. Two additions. (1) The accept_intro double-charge is now **EXECUTED**
grade, not READ: replayed on a throwaway replica it charges the buyer once per request and drives the
wallet negative (-3T after four accepts, no floor). (2) NEW, missed by all three cycles — the BIT
Mitigator's automatic safe-state response is a **placebo**: all three SAFE_FLAGS are written, journalled
and reported as mitigations while nothing in bea_main.py or the front end reads them. Detection is real;
mitigation is decorative. Both findings were then handed to a fresh adversarial peer with one instruction -- break them -- and both were UPHELD with their grades RAISED: it ran the real app under a TestClient (four accepts, four charges, balance -3T) and applied the mitigator's full safe state (charge still succeeded). It found two more in the same class: decline_intro is unguarded (charged-then-declined, no refund row), and the shipped EULA promises a 1T hold/release the code never implements -- a legal exposure, and David's call which way it resolves. Four OPEN ledger entries carry it all: RG-0142 (money path idempotent and state-guarded), RG-0143 (no placebo breakers), RG-0144 (no public posture leak), RG-0145 (wallet matches the promise). The peer also found three false-red and three false-green paths in the entries as first written; all were FIXED the same session, with the correction recorded in each entry's ref, never weakened. Ledger 138 assertions, exit 0, all LOCKED holding, 12 open. Also noted: RG-0140/RG-0141 are live-build customer-facing defects that landed
after the consolidated report closed and belong on the launch board. Reserved to David: rotate the
exposed secrets, approve the deploy carrying these fixes, rule the gate/WAF posture, and make the
launch go/hold call.
