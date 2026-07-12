@echo off
title Fix TrustSquare manifest MIME
color 0E
set SERVER=root@178.104.73.239
echo(
echo   Fixing manifest MIME on the server...
echo   (safe: validates nginx config before reloading, restores on any error)
echo(
ssh %SERVER% "F=/etc/nginx/mime.types; TS=$(date +%%s); if grep -q webmanifest $F; then echo '  [i] mime.types already lists webmanifest'; else cp $F $F.bak-$TS; sed -i 's#^}#    application/manifest+json  webmanifest;\n}#' $F; echo '  [..] added application/manifest+json for .webmanifest'; fi; if nginx -t; then nginx -s reload; echo '  [OK] nginx config valid and reloaded'; else echo '  [X] nginx -t FAILED - restoring backup, no change applied'; cp $F.bak-$TS $F; fi; echo '  --- manifest Content-Type is now: ---'; curl -sI http://localhost/static/brand/site.webmanifest"
echo(
echo   Done.
echo(
pause
