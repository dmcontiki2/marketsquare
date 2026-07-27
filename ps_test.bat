@echo off
setlocal enableextensions
set LOG=C:\Users\David\Projects\MarketSquare\ps_test_report.txt
echo === PowerShell re-test %date% %time% === > "%LOG%"
echo [1] bare powershell: >> "%LOG%"
powershell -NoProfile -Command "Write-Output BARE_OK" >> "%LOG%" 2>&1
echo exitcode=%errorlevel% >> "%LOG%"
echo [2] full path: >> "%LOG%"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -Command "Write-Output FULLPATH_OK" >> "%LOG%" 2>&1
echo exitcode=%errorlevel% >> "%LOG%"
echo [3] deploy step-0 rehearsal on a COPY (no real files touched): >> "%LOG%"
copy /y marketsquare.html ms_bump_rehearsal.html >nul
powershell -NoProfile -Command "$f='C:\Users\David\Projects\MarketSquare\ms_bump_rehearsal.html'; $c=Get-Content -Raw -LiteralPath $f; $c=[regex]::Replace($c,'ms\.js\?v=(\d+)',{'ms.js?v='+([int]$args[0].Groups[1].Value+1)}); Set-Content -NoNewline -LiteralPath $f -Value $c; Write-Host ('REHEARSAL_BUMP_OK -> ' + [regex]::Match($c,'ms\.js\?v=(\d+)').Value)" >> "%LOG%" 2>&1
echo exitcode=%errorlevel% >> "%LOG%"
echo === END === >> "%LOG%"
echo Test done - closing in 5s.
timeout /t 5 /nobreak >nul
