- **First real-repo probe run: INVALID, not failed.** The refuse guard escalated it on the word
  `card` — the probe's fault text said "when I tap a card" (a listing card); `card` is a payment
  marker. The patch path was never reached, so the run says nothing about patch quality.
- **Checked before changing anything:** across all 30 live faults, substring matching differs
  from word-boundary matching exactly once (`anonym` in "anonymity" — correct anyway), and the
  standalone word `card` appears zero times. The guard is not misbehaving; the probe was.
- **Did not narrow the marker to make the probe pass.** Over-refusing costs a human glance;
  under-refusing costs a payment surface. Reworded the probe instead, and its wording is now
  verified against the full marker list before use — both targets clean. The probe also now
  reports ESCALATE as **INVALID** rather than FAIL, so a guard hit can never be misread as a
  patch-quality verdict.
- **Still unanswered, and still the last open question: can the agent patch a 1 MB file?**
  Three attempts today; none has yet reached the patch path against real code.
