# Installing the Tuppence dormancy sweep (EULA §6.3)

One-time, on the Hetzner box, as root:

```bash
cp /opt/marketsquare-src/ops/dormancy/tuppence-dormancy.service /etc/systemd/system/
cp /opt/marketsquare-src/ops/dormancy/tuppence-dormancy.timer   /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now tuppence-dormancy.timer
systemctl list-timers tuppence-dormancy.timer      # confirm the next run is scheduled
```

## Prove it is safe before trusting it

Dry run against the live DB — writes nothing, sends nothing:

```bash
cd /var/www/marketsquare && python3 tuppence_dormancy.py
```

Expected output today: `0 accounts warned · 0 expired`. Nothing on the platform can
reach 24 months of inactivity before roughly April 2028.

Force a future date to see the machinery work without waiting two years:

```bash
cd /var/www/marketsquare && python3 tuppence_dormancy.py --as-of 2028-06-01
```

## What it will never do

- Expire a balance with no warning on record → it warns instead and defers.
- Expire a balance whose warning is younger than 30 days → it waits.
- Run at all with `--apply` when `RESEND_API_KEY` is missing → exits 2, changes nothing.
- Touch a wallet in dry-run mode.
- Destructively update a balance — expiry is one offsetting `dormancy_expiry` row.

## Where to look when it does fire

```bash
journalctl -u tuppence-dormancy.service -n 100
sqlite3 /var/www/marketsquare/marketsquare.db \
  "SELECT email, warned_at, balance_at_warning, expired_at, expired_amount
     FROM tuppence_dormancy_notices ORDER BY warned_at DESC LIMIT 20;"
```

Regression ledger **RG-0129** asserts the sweep keeps existing with the notice as a
hard precondition. If someone weakens it, the ledger goes red the same day.
