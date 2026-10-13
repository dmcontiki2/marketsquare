@echo off
title TrustSquare - Publish Whitepaper Addendum A
set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
echo  This POSTS Whitepaper Addendum A publicly (irrevocable disclosure). Ctrl+C to abort, or
pause
scp "%PROJECT%\trustsquare_whitepaper_v3.13_addendumA.pdf" %SERVER%:%REMOTE%/static/trustsquare_whitepaper_v3.13_addendumA.pdf || goto :fail
scp "%PROJECT%\whitepaper.html" %SERVER%:%REMOTE%/static/whitepaper.html || goto :fail
ssh %SERVER% "chmod 644 %REMOTE%/static/whitepaper.html %REMOTE%/static/trustsquare_whitepaper_v3.13_addendumA.pdf && sha256sum %REMOTE%/static/trustsquare_whitepaper_v3.13_addendumA.pdf" || goto :fail
echo  PUBLISHED. Opening Wayback saves...
start "" "https://web.archive.org/save/https://trustsquare.co/static/whitepaper.html"
start "" "https://web.archive.org/save/https://trustsquare.co/static/trustsquare_whitepaper_v3.13_addendumA.pdf"
echo %DATE% %TIME% PUBLISHED addendumA >> "%PROJECT%\publish_whitepaper_log.txt"
pause
exit /b 0
:fail
echo  UPLOAD FAILED - check above.
pause
exit /b 1
