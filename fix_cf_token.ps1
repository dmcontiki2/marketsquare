$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\cf_token_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== consolidate CF_CACHE_TOKEN $(Get-Date -Format s) =====")
& scp -q "scripts\consolidate_env_var.py" "${srv}:/tmp/consolidate_env_var.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/consolidate_env_var.py CF_CACHE_TOKEN /etc/systemd/system/marketsquare.service.d/cloudflare.conf" 2>&1 | ForEach-Object { Say $_ }
& scp -q "scripts\install_cf_token.py" "${srv}:/tmp/x.py" 2>&1 | Out-Null
& ssh $srv "python3 - <<'EOF'
import json,os,subprocess,urllib.request,hashlib
def out(c): return subprocess.run(c,shell=True,capture_output=True,text=True).stdout.strip()
pid=out('systemctl show -p MainPID --value marketsquare'); env={}
for e in open('/proc/%s/environ'%pid,'rb').read().decode('utf8','replace').split(chr(0)):
    if '=' in e:
        k,v=e.split('=',1); env[k]=v
t=env.get('CF_CACHE_TOKEN','')
print('  token fingerprint now: %s'%hashlib.sha256(t.encode()).hexdigest()[:8])
def cf(u):
    r=urllib.request.Request(u,headers={'Authorization':'Bearer '+t})
    return json.loads(urllib.request.urlopen(r,timeout=20).read().decode())
try:
    print(\"  [OK] token status: %s\"%cf('https://api.cloudflare.com/client/v4/user/tokens/verify')['result']['status'])
    print(\"  [OK] zone access : %s\"%cf('https://api.cloudflare.com/client/v4/zones/'+env.get('CF_ZONE_ID',''))['result']['name'])
except Exception as ex:
    print('  [X] verify failed: %s'%str(ex)[:120])
EOF
rm -f /tmp/consolidate_env_var.py /tmp/x.py" 2>&1 | ForEach-Object { Say $_ }
Say ""; Say "  Done - Claude reads .secrets\cf_token_log.txt directly."
Read-Host "  Press Enter to close"
