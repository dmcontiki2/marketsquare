#!/bin/bash
# Applies the C4 security-header snippet to the live nginx marketsquare server.
# Safe + reversible: backs up config, includes the snippet at server scope,
# tests with `nginx -t`, and only reloads if the test passes.
set -e
H=root@178.104.73.239
scp nginx_security_headers.conf $H:/etc/nginx/snippets/security_headers.conf
ssh $H '
  set -e
  cfg=/etc/nginx/sites-enabled/marketsquare
  cp $cfg ${cfg}.bak-c4-$(date +%Y%m%d-%H%M%S)
  # Insert the include once, right after the trustsquare.co server_name line
  if ! grep -q "snippets/security_headers.conf" $cfg; then
    sed -i "/server_name trustsquare.co www.trustsquare.co;/a\\    include snippets/security_headers.conf;" $cfg
  fi
  nginx -t
  systemctl reload nginx
  echo "--- verifying live headers ---"
  curl -sI https://trustsquare.co/ | grep -iE "x-frame|x-content-type|referrer-policy|content-security|strict-transport" || echo "WARN: headers not visible (Cloudflare may strip/normalise some)"
'
