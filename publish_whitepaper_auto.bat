@echo off
title TrustSquare - Publish Whitepaper (unattended)
set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
set LOG=%PROJECT%\publish_whitepaper_log.txt

echo ============================================================ > "%LOG%"
echo TRUSTSQUARE PUBLISH LOG  %DATE% %TIME% >> "%LOG%"
echo ============================================================ >> "%LOG%"

for %%F in (whitepaper.html trustsquare_whitepaper_v3.12.pdf trustsquare_claim_visuals_v4.html trustsquare_preview.html) do (
    if not exist "%PROJECT%\%%F" (
        echo PREFLIGHT-FAIL: %%F missing >> "%LOG%"
        exit /b 1
    )
)
echo PREFLIGHT-OK >> "%LOG%"

scp "%PROJECT%\whitepaper.html" %SERVER%:%REMOTE%/static/whitepaper.html >> "%LOG%" 2>&1 || (echo UPLOAD-FAIL whitepaper.html >> "%LOG%" & exit /b 1)
echo UPLOADED whitepaper.html >> "%LOG%"
scp "%PROJECT%\trustsquare_whitepaper_v3.12.pdf" %SERVER%:%REMOTE%/static/trustsquare_whitepaper_v3.12.pdf >> "%LOG%" 2>&1 || (echo UPLOAD-FAIL pdf >> "%LOG%" & exit /b 1)
echo UPLOADED trustsquare_whitepaper_v3.12.pdf >> "%LOG%"
scp "%PROJECT%\trustsquare_claim_visuals_v4.html" %SERVER%:%REMOTE%/static/trustsquare_claim_visuals_v4.html >> "%LOG%" 2>&1 || (echo UPLOAD-FAIL visuals >> "%LOG%" & exit /b 1)
echo UPLOADED trustsquare_claim_visuals_v4.html >> "%LOG%"

ssh %SERVER% "ls -la %REMOTE%/static/whitepaper.html %REMOTE%/static/trustsquare_whitepaper_v3.12.pdf %REMOTE%/static/trustsquare_claim_visuals_v4.html; sha256sum %REMOTE%/static/trustsquare_whitepaper_v3.12.pdf" >> "%LOG%" 2>&1 || (echo VERIFY-FAIL >> "%LOG%" & exit /b 1)
echo PUBLISH-COMPLETE >> "%LOG%"
exit /b 0
