"""
deploy_router.py — OPTIONAL authenticated HTTPS deploy trigger for MarketSquare.

This is the "port 443" trigger for Phase 3. It lets a session that CANNOT ssh to
the box and CANNOT push to the mirror (e.g. a cloud Cowork session, whose only
route to the server is HTTPS) start a deploy by calling one endpoint. It runs the
SAME server_deploy.sh engine the timer uses — one engine, one rollback story.

╔══ SECURITY — READ THIS ════════════════════════════════════════════════════╗
║ • The endpoint is DISABLED unless the server env var MS_DEPLOY_TOKEN is set. ║
║   No token set  →  every call gets 503. Fail-closed by default.             ║
║ • The token lives ONLY on the server (in the systemd unit / a root-only     ║
║   env file David sets by hand). It is NEVER in the repo, a session, or chat.║
║ • Caller must send it as the  X-Deploy-Token  header. Compared in constant  ║
║   time. It is never logged.                                                 ║
║ • Give it its OWN token — do not reuse MS_ADMIN_KEY. Deploy is more          ║
║   powerful than a cache purge; least privilege.                             ║
╚═════════════════════════════════════════════════════════════════════════════╝

TO ENABLE (optional — the git-pull timer already gives you hands-free deploys):
  1. Add these THREE lines to bea_main.py, just after `app = FastAPI(...)`:

         from deploy_router import router as _deploy_router      # noqa: E402
         app.include_router(_deploy_router)

     (deploy_router.py must be deployed next to main.py — add it to
      deploy_manifest.txt if you want the timer to ship it too.)

  2. On the server, set the token in the systemd drop-in (root-only), e.g.:
         mkdir -p /etc/systemd/system/marketsquare.service.d
         printf '[Service]\nEnvironment=MS_DEPLOY_TOKEN=%s\n' "$(openssl rand -hex 24)" \
             > /etc/systemd/system/marketsquare.service.d/deploy-token.conf
         chmod 600 /etc/systemd/system/marketsquare.service.d/deploy-token.conf
         systemctl daemon-reload && systemctl restart marketsquare
     Then read the token back ONCE (root shell only) to give to whoever will
     trigger deploys. Do not paste it into a session that will be logged.

  3. Trigger a deploy over HTTPS:
         curl -sS -X POST https://trustsquare.co/admin/deploy \
              -H "X-Deploy-Token: <the token>"
     → 202 {"status":"started"}  — the engine runs in the background; watch
       /var/log/marketsquare-deploy.log or GET /admin/deploy/status.
"""
import hmac
import os
import subprocess
import time

from fastapi import APIRouter, Header, HTTPException

router = APIRouter()

_DEPLOY_SCRIPT = os.environ.get(
    "MS_DEPLOY_SCRIPT", "/opt/marketsquare-src/ops/autodeploy/server_deploy.sh"
)
_DEPLOY_LOG = os.environ.get("MS_LOG", "/var/log/marketsquare-deploy.log")


def _token_ok(supplied: str | None) -> bool:
    expected = os.environ.get("MS_DEPLOY_TOKEN", "")
    if not expected:
        # Fail-closed: the feature is off until a token is configured server-side.
        raise HTTPException(status_code=503, detail="Deploy endpoint disabled (no MS_DEPLOY_TOKEN set on server).")
    if not supplied:
        raise HTTPException(status_code=401, detail="Missing X-Deploy-Token header.")
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=403, detail="Bad deploy token.")
    return True


@router.post("/admin/deploy")
def trigger_deploy(x_deploy_token: str | None = Header(default=None)):
    """Kick off a git-pull deploy in the background. Returns 202 immediately.

    Idempotent & safe to call repeatedly: server_deploy.sh holds a flock, so
    overlapping calls do not collide, and a call with nothing new on the tracked
    ref is a no-op.
    """
    _token_ok(x_deploy_token)
    if not os.path.exists(_DEPLOY_SCRIPT):
        raise HTTPException(status_code=500, detail=f"Deploy script not found at {_DEPLOY_SCRIPT}.")
    try:
        # Detach: the HTTP call returns fast; the deploy runs on its own, logging
        # to the deploy log. --force so an explicit trigger always re-checks now.
        with open(_DEPLOY_LOG, "a") as logf:
            subprocess.Popen(
                ["/usr/bin/env", "bash", _DEPLOY_SCRIPT, "--force"],
                stdout=logf,
                stderr=logf,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Failed to start deploy: {exc}")
    return {"status": "started", "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


@router.get("/admin/deploy/status")
def deploy_status(x_deploy_token: str | None = Header(default=None)):
    """Return the tail of the deploy log so a caller can see how the last run went."""
    _token_ok(x_deploy_token)
    try:
        with open(_DEPLOY_LOG, "r", errors="replace") as f:
            lines = f.readlines()[-40:]
    except FileNotFoundError:
        lines = ["(no deploy log yet)"]
    return {"log_tail": [ln.rstrip("\n") for ln in lines]}
