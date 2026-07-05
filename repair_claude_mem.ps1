# ============================================================================
#  repair_claude_mem.ps1  --  v2 (root-cause fix), rebuilt 2026-07-01
#
#  WHY v2:
#  v1 (28 Jun) fixed the FIRST failure — chroma-mcp's cold-download exceeding
#  the 30s *connect* timeout — by pre-warming the uvx wheel cache. That worked
#  (the 29 Jun logs show Chroma connecting in ~2s). But it exposed a SECOND,
#  deeper failure one layer down: the embedding OPERATION itself. Every
#  `chroma_add_documents` call cold-loads the ~90MB ONNX embedding model and
#  exceeds the MCP request timeout (~60s), so EVERY batch fails (even a 2-doc
#  batch), the sync watermark never advances, and it retries the same batch
#  forever. Net effect: the vector-sync path is chronically broken.
#
#  KEY INSIGHT: claude-mem's record-of-truth is SQLite. Session summaries are
#  written to SQLite directly (INSERT into session_summaries) and are what the
#  digest reads. The Chroma vector store only powers *semantic* search, and it
#  has NEVER successfully synced for this project (chroma-sync-state = 0/0/0).
#  So the durable fix is to stop gating memory on that fragile subsystem:
#
#     >>> Run claude-mem SQLite-only:  CLAUDE_MEM_CHROMA_ENABLED = "false" <<<
#
#  Recording, the digest, and keyword/FTS search all keep working; only
#  semantic vector search is dropped (it was never working here anyway). This
#  removes the entire uvx -> onnxruntime -> chroma-mcp -> MCP-stdio timeout
#  chain that caused every recurrence to date. Fully reversible (flip back to
#  "true" and re-run to restore vectors; see the OPTIONAL appendix below).
#
#  Run from PowerShell:
#     cd C:\Users\David\Projects\MarketSquare
#     powershell -ExecutionPolicy Bypass -File .\repair_claude_mem.ps1
#  Safe to re-run (idempotent). Touches only ~/.claude-mem runtime + restart.
# ============================================================================

$ErrorActionPreference = "Continue"
$mem          = Join-Path $env:USERPROFILE ".claude-mem"
$settingsPath = Join-Path $mem "settings.json"
$stamp        = Get-Date -Format "yyyyMMdd-HHmmss"

function Say($m){ Write-Host ("[repair] " + $m) }

Say "claude-mem dir: $mem"

# --- 1. THE FIX: run SQLite-only by disabling the Chroma vector add-on -------
if (-not (Test-Path $settingsPath)) {
    Say "ERROR: $settingsPath not found -- is claude-mem installed? Aborting."
    return
}
try {
    $settings = Get-Content $settingsPath -Raw -ErrorAction Stop | ConvertFrom-Json
} catch {
    Say "ERROR: settings.json is not valid JSON -- not touching it. $_"
    return
}
if ($settings.CLAUDE_MEM_CHROMA_ENABLED -eq "false") {
    Say "Chroma already disabled (CLAUDE_MEM_CHROMA_ENABLED=false) -- good."
} else {
    Copy-Item $settingsPath "$settingsPath.bak-$stamp" -Force -ErrorAction SilentlyContinue
    $settings | Add-Member -NotePropertyName CLAUDE_MEM_CHROMA_ENABLED -NotePropertyValue "false" -Force
    ($settings | ConvertTo-Json -Depth 8) | Set-Content $settingsPath -Encoding UTF8
    Say "Set CLAUDE_MEM_CHROMA_ENABLED=false (backup: settings.json.bak-$stamp)"
}

# --- 2. Clear any stale worker locks so the restart spawns cleanly -----------
foreach ($f in @("worker.pid","supervisor.json")) {
    $p = Join-Path $mem $f
    if (Test-Path $p) {
        Copy-Item $p "$p.stale" -Force -ErrorAction SilentlyContinue
        Remove-Item $p -Force -ErrorAction SilentlyContinue
        Say "cleared stale $f (backup left as $f.stale)"
    }
}

# --- 3. Restart the claude-mem worker ---------------------------------------
Say "Restarting claude-mem worker (SQLite-only -- no uvx/Chroma launch now)..."
& npx claude-mem restart 2>&1 | ForEach-Object { Say $_ }
if ($LASTEXITCODE -ne 0) {
    Say "restart returned $LASTEXITCODE; trying 'npx claude-mem repair'..."
    & npx claude-mem repair 2>&1 | ForEach-Object { Say $_ }
}

# --- 4. Verify worker health + confirm Chroma really is disabled ------------
Start-Sleep -Seconds 3
$pidFile = Join-Path $mem "worker.pid"
if (Test-Path $pidFile) {
    $info = Get-Content $pidFile -Raw | ConvertFrom-Json
    $port = $info.port
    Say ("New worker PID = " + $info.pid + " on port " + $port)
    try {
        $h = Invoke-RestMethod -Uri "http://127.0.0.1:$port/health" -TimeoutSec 5
        Say ("Health: " + ($h | ConvertTo-Json -Compress))
    } catch {
        Say "Health ping failed (worker may still be booting) -- recheck in a minute."
    }
    try {
        $c = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/chroma/status" -TimeoutSec 5
        if ($c.status -eq "disabled") {
            Say "Chroma status = disabled -- CONFIRMED SQLite-only. This is the fix holding."
        } else {
            Say ("Chroma status = " + $c.status + " (expected 'disabled'); re-check settings.json.")
        }
    } catch {
        Say "Chroma status ping failed -- non-fatal; verify with: npx claude-mem status"
    }
} else {
    Say "No new worker.pid yet -- open a Claude Code CLI session to trigger a spawn, then re-run."
}

Say ""
Say "Done. The recording path is now SQLite-only and no longer depends on Chroma."
Say "Next: open ONE Claude Code CLI session in this project so a fresh summary is written,"
Say "then refresh the digest:"
Say "  python claude_mem_digest.py --db `"$mem\claude-mem.db`" --project MarketSquare --limit 10 --out .\CLAUDE_MEM_DIGEST.md"

# ============================================================================
#  OPTIONAL APPENDIX -- re-enable semantic (vector) search later
#  ---------------------------------------------------------------------------
#  Only if you decide you want vector search back. The robust way is to warm
#  the actual EMBEDDING MODEL (not just the wheels, which is all v1 did) so the
#  first real add_documents call doesn't cold-load under the ~60s timeout:
#
#    1. Set CLAUDE_MEM_CHROMA_ENABLED = "true" in settings.json
#    2. Warm wheels AND model once, with no timeout, e.g.:
#         $env:UV_NO_PROGRESS = "1"
#         uvx --python 3.13 --with "onnxruntime>=1.20" --with "protobuf<7" `
#             chroma-mcp==0.2.6 --client-type persistent `
#             --data-dir "$mem\chroma" --help *> "$mem\prewarm.log"
#       (then run one indexing pass; the model file caches under ~/.cache)
#    3. Restart: npx claude-mem restart
#  If embeds still time out on this box, stay SQLite-only -- it's the reliable
#  configuration and loses only semantic ranking, not memory itself.
# ============================================================================
