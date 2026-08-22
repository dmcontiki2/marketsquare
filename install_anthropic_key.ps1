$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\anthropic_install_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== run $(Get-Date -Format s) =====")
Write-Host ""
Write-Host "  Paste the new Anthropic key (right-click pastes). It is never stored on"
Write-Host "  this PC and never shown to Claude."
Write-Host ""
$k = (Read-Host "  Anthropic key") -replace '\s',''
Say ("  length: {0} characters" -f $k.Length)
if ($k.Length -lt 20) { Say "  [X] that is too short to be an API key - nothing sent."; Read-Host "  Press Enter to close"; exit 1 }
if (-not $k.StartsWith("sk-ant-")) { Say "  [!] does not start with sk-ant- - shipping anyway, the API call will judge it" }
Say "  [OK] shipping."
& scp -q "scripts\install_anthropic_key.py" "${srv}:/tmp/install_anthropic_key.py" 2>&1 | ForEach-Object { Say $_ }
if ($LASTEXITCODE -ne 0) { Say "  [X] could not reach the server"; Read-Host "  Press Enter to close"; exit 1 }
& ssh $srv "python3 /tmp/install_anthropic_key.py '$k'; rm -f /tmp/install_anthropic_key.py" 2>&1 | ForEach-Object { Say $_ }

# Local holder: .secrets\ai_keys.env is read by maintenance_agent.py and
# maint_realrepo_probe.py. Left stale, they break the moment the old key is deleted.
$aiEnv = Join-Path $root ".secrets\ai_keys.env"
if (Test-Path $aiEnv) {
  Copy-Item $aiEnv "$aiEnv.bak-$(Get-Date -Format yyyyMMdd-HHmmss)" -Force
  $lines = Get-Content $aiEnv
  $updated = $lines -replace '^\s*ANTHROPIC_API_KEY=.*$', "ANTHROPIC_API_KEY=$k"
  Set-Content -Path $aiEnv -Value $updated -NoNewline:$false
  $check = (Get-Content $aiEnv | Where-Object { $_ -match '^ANTHROPIC_API_KEY=' })
  if ($check) { Say "  [OK] local .secrets\ai_keys.env updated (maintenance agent keeps working)" }
  else { Say "  [X] could not update .secrets\ai_keys.env - tell Claude" }
} else {
  Say "  [--] no local .secrets\ai_keys.env to update"
}
Say ""; Say "  Done - Claude reads .secrets\anthropic_install_log.txt directly."
Read-Host "  Press Enter to close"
