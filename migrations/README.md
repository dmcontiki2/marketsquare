# migrations/ — one-time server-side changes that ride the ONE deploy

Put a `NNN_short_name.py` here when a release needs a one-time change on the
server (schema change, data backfill, one-shot cleanup — everything the old
flag-guarded "Step 3e" scripts in the retired scp deploy used to do).

Contract (enforced by ops/autodeploy/post_deploy.sh):
- Runs ON the server with CWD = the live web root, as `python3 <script> --apply`.
- Runs EXACTLY ONCE — recorded by filename in `<live>/.migrations_done`.
- The live `*.db` files are snapshotted to `<live>/.db-backups/<ts>/` before the
  first pending migration of a deploy runs. Restore = copy back + restart.
- Number them (001_, 002_…): they run in sorted order. Never rename a shipped one.
- Make them idempotent anyway (check-then-act) — belt and braces.
- A failed migration stops the chain, is NOT recorded (so it retries next
  deploy), and never rolls back the code deploy itself.
