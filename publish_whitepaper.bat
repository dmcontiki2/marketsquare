@echo off
title TrustSquare - Publish Whitepaper
color 0A
set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare

echo.
echo  ============================================================
echo   TRUSTSQUARE  ^|  Publishing whitepaper to trustsquare.co
echo   %DATE% %TIME%
echo  ============================================================
echo.
echo  This POSTS the whitepaper publicly (irrevocable disclosure).
echo  Press Ctrl+C now to abort, or
pause

for %%F in (whitepaper.html trustsquare_whitepaper_v3.12.pdf trustsquare_claim_visuals_v4.html trustsquare_preview.html) do (
    if not exist "%PROJECT%\%%F" (
        echo  ERROR: %%F not found in %PROJECT%
        pause
        exit /b 1
    )
)

echo  Uploading landing page...
scp "%PROJECT%\whitepaper.html" %SERVER%:%REMOTE%/static/whitepaper.html || goto :fail
echo  Uploading whitepaper PDF...
scp "%PROJECT%\trustsquare_whitepaper_v3.12.pdf" %SERVER%:%REMOTE%/static/trustsquare_whitepaper_v3.12.pdf || goto :fail
echo  Uploading claim visuals...
scp "%PROJECT%\trustsquare_claim_visuals_v4.html" %SERVER%:%REMOTE%/static/trustsquare_claim_visuals_v4.html || goto :fail
echo  Uploading pre-launch preview page...
scp "%PROJECT%\trustsquare_preview.html" %SERVER%:%REMOTE%/static/preview.html || goto :fail

echo  Verifying on server...
ssh %SERVER% "ls -la %REMOTE%/static/whitepaper.html %REMOTE%/static/trustsquare_whitepaper_v3.12.pdf %REMOTE%/static/trustsquare_claim_visuals_v4.html && sha256sum %REMOTE%/static/trustsquare_whitepaper_v3.12.pdf" || goto :fail

echo.
echo  ============================================================
echo   PUBLISHED. Now capture INDEPENDENT date evidence (5 min):
echo  ============================================================
echo   1. Wayback Machine - open these two URLs in a browser:
echo      https://web.archive.org/save/https://trustsquare.co/static/whitepaper.html
echo      https://web.archive.org/save/https://trustsquare.co/static/trustsquare_whitepaper_v3.12.pdf
echo      Save the resulting archive URLs.
echo   2. Zenodo DOI (free, CERN) - zenodo.org : New upload, attach the
echo      same PDF, title = whitepaper title, note "supports CIPC
echo      provisional application 2026/06760, filed 30 June 2026".
echo      Publish and save the DOI.
echo   3. Record both in Patents\PATENT_PENDING_2026-06-30.md
echo      (Publication evidence section is waiting for them).
echo.
pause
exit /b 0

:fail
color 0C
echo.
echo  UPLOAD FAILED - nothing published until all three files land.
pause
exit /b 1
