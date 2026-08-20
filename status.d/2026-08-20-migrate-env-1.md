- **MIGRATE-ENV-1 shipped** — the two-fault migration jam (missing `MS_API_KEY` *and* the
  wrong Python interpreter) is fixed at class level in `ops/autodeploy/post_deploy.sh`.
  023/024/027 proven rc=0 on the box with the venv interpreter + service environment;
  023 relinked 84/104 listings against the expanded wonders catalog. RG-0125 flips green
  once a deploy records the chain past 022.
