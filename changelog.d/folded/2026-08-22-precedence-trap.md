## 2026-08-22 — the precedence trap, twice, and the tool that ends it

Recorded separately from the rotation entry because the fault is about METHOD, not about
any one credential.

**systemd applies environment in order, and the last assignment wins.** The unit, then
every drop-in in *lexicographic* order (there are 17 on this service), then each
`EnvironmentFile` where its directive sits. A correctly-written 0600 drop-in is therefore
not enough — it has to be the *last* definition, and nothing about writing it tells you
whether it was.

It bit twice in one morning:

- **Paystack.** The new key was written to `paystack.conf`, the service restarted clean and
  reported `active` — and `/etc/environment`, loaded later via `env.conf`, still held the
  just-revoked key. Disk said rotated, Paystack said 401, **card payments were down and
  nothing reported it.**
- **CF_CACHE_TOKEN.** The new value went into `cloudflare.conf`; `datakeys.conf` sorts after
  it and held the old one. The rotation reported success and **changed nothing.**

**What caught both: reading back from `/proc/<pid>/environ`** — the RG-0147 assertion,
written that same morning off the first incident and earning itself on the second.
The write is not the fact.

**New standing tool: `scripts/consolidate_env_var.py VAR CANONICAL_FILE`.** Finds every
definition across the unit, all drop-ins and their EnvironmentFiles; strips all but the
canonical one (backups first); restarts; and reports the fingerprint the RUNNING PROCESS
ends up with. Plus `scripts/diag_env_var.py VAR`, which prints the whole precedence chain
in systemd's own order so the next session can SEE which file wins instead of guessing.

**CF_CACHE_TOKEN is NOT rotated.** A 53-character value was installed (Cloudflare tokens
are 40 — most likely the R2 token value from the previous step), it verified 401, and
cache purge broke until the previous token was restored from backup. Restored and PROBED:
token active, zone `trustsquare.co` reachable. The old token remains burnt-but-working and
is the lowest-harm item outstanding.
