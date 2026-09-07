#!/usr/bin/env python3
"""RETIRED 7 Sep 2026 -- superseded the same morning by the ledger's own --shard / --combine
(LEDGER-SHARD-1, RG-0319). This file was written at 01:17 for the same reason (a ~180 s call
cap); the canonical lane landed at 06:56 with a stricter contract (a verdict is refused unless
every shard is present, fresh and judged by the same _judge()). One engine, one story:

    python3 scripts/regression_ledger.py --shard=1/3
    python3 scripts/regression_ledger.py --shard=2/3
    python3 scripts/regression_ledger.py --shard=3/3
    python3 scripts/regression_ledger.py --combine=3

Kept as a pointer only (unlink is blocked on this mount); it does nothing else."""
import sys
print(__doc__)
sys.exit(2)
