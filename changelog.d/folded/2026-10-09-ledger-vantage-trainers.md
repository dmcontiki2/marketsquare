### The server's ledger no longer shows trainer photos as missing (Goal run 34b)

- **LEDGER-VANTAGE-TRAINERS-1** — RG-0949 and RG-0950 failed on every server checkout because the trainer pictures are
  gitignored and are not stored there, although all 47 load live. On the server they now read NOT EVALUATED, but only when
  every failure is a missing picture file **and** every trainer photo answers 200 image/* at its live URL. Any other
  failure stays red. They are still judged in full on David's PC.

Cost model impact: none. Schema: none.
