# ============================================================================
#  repair_claude_mem.ps1  --  one-shot repair for claude-mem memory
#  Built 2026-06-28. Root cause: chroma-mcp cold-download (onnxruntime +
#  chromadb, ~tens of MB via uvx) NEVER finished inside claude-mem's 30s
#  connection timeout, so the worker's vector-sync path failed on every cycle
#  and the worker has not run since 23 Jun. Fix = pre-warm the uvx cache ONCE
#  with no timeout, clear stale locks, restart the worker, then verify.
#
#  Run from PowerShell:
#     cd C:\Users\David\Projects\MarketSquare
#     powershell -ExecutionPolicy Bypass -File .\repair_claude_mem.ps1
#  Safe to re-run. Touches only ~/.claude-mem runtime + the uvx cache.
# ============================================================================

$ErrorActionPreference = "Continue"
$mem = Join-Path $env:USERPROFILE ".claude-mem"
$chromaDir = Join-Path $mem "chroma"
$uvx = Join-Path $env:USERPROFILE ".local\bin\uvx.exe"

function Say($m){ Write-Host ("[repair] " + $m) }

Say "claude-mem dir: $mem"

# --- 1. Clear stale worker locks (PID 15916 from 23 Jun is long dead) --------
foreach ($f in @("worker.pid","supervisor.json")) {
    $p = Join-Path $mem $f
    if (Test-Path $p) {
        Copy-Item $p "$p.stale" -Force -ErrorAction SilentlyContinue
        Remove-Item $p -Force -ErrorAction SilentlyContinue
        Say "cleared stale $f (backup left as $f.stale)"
    }
}

# --- 2. Make sure the chroma data dir exists (it was never created) ----------
if (-not (Test-Path $chromaDir)) {
    New-Item -ItemType Directory -Path $chromaDir -Force | Out-Null
    Say "created missing chroma data dir: $chromaDir"
} else {
    Say "chroma data dir already present"
}

# --- 3. THE FIX: pre-warm the uvx cache with NO timeout ----------------------
# Exactly the dependency set claude-mem launches, but we let it finish.
if (-not (Test-Path $uvx)) {
    Say "WARNING: uvx not found at $uvx -- is uv installed? (winget install astral-sh.uv)"
    Say "Skipping prewarm; the rest will still run but Chroma may still time out."
} else {
    Say "Pre-warming Chroma dependency cache (this may take 1-3 min on first run)..."
    $env:UV_NO_PROGRESS = "1"
    # --help just makes chroma-mcp resolve+download then exit cleanly.
    & $uvx --python 3.13 --with "onnxruntime>=1.20" --with "protobuf<7" `
        chroma-mcp==0.2.6 --help *> (Join-Path $mem "prewarm.log")
    if ($LASTEXITCODE -eq 0) {
        Say "Chroma cache warmed OK -- future 30s connects will now succeed."
    } else {
        Say "Prewarm exit code $LASTEXITCODE -- see $mem\prewarm.log (may still be fine if wheels cached)."
    }
}

# --- 4. Restart the claude-mem worker ---------------------------------------
Say "Restarting claude-mem worker..."
& npx claude-mem restart 2>&1 | ForEach-Object { Say $_ }
if ($LASTEXITCODE -ne 0) {
    Say "restart returned $LASTEXITCODE; trying 'npx claude-mem repair'..."
    & npx claude-mem repair 2>&1 | ForEach-Object { Say $_ }
}

# --- 5. Verify worker health ------------------------------------------------
Start-Sleep -Seconds 3
$pidFile = Join-Path $mem "worker.pid"
if (Test-Path $pidFile) {
    $info = Get-Content $pidFile -Raw | ConvertFrom-Json
    Say ("New worker PID = " + $info.pid + " on port " + $info.port)
    try {
        $h = Invoke-RestMethod -Uri ("http://127.0.0.1:" + $info.port + "/health") -TimeoutSec 5
        Say ("Health: " + ($h | ConvertTo-Json -Compress))
    } catch {
        Say "Health ping failed (worker may still be booting) -- recheck in a minute."
    }
} else {
    Say "No new worker.pid yet -- open a Claude Code CLI session to trigger a spawn, then re-run health check."
}

Say "Done. Next: open ONE Claude Code CLI session in this project so a summary gets written,"
Say "then run:  python claude_mem_digest.py --db `"$mem\claude-mem.db`" --project MarketSquare --limit 10 --out .\CLAUDE_MEM_DIGEST.md"
