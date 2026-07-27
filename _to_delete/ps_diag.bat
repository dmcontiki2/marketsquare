@echo off
setlocal enableextensions
set LOG=C:\Users\David\Projects\MarketSquare\ps_diag_report.txt
echo === PowerShell diagnosis %date% %time% === > "%LOG%"
echo [1] where powershell: >> "%LOG%"
where powershell >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [2] PATH: >> "%LOG%"
echo %PATH% >> "%LOG%"
echo. >> "%LOG%"
echo [3] bare powershell invocation: >> "%LOG%"
powershell -NoProfile -Command "Write-Output BARE_OK" >> "%LOG%" 2>&1
echo exitcode=%errorlevel% >> "%LOG%"
echo. >> "%LOG%"
echo [4] full path System32: >> "%LOG%"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -Command "Write-Output FULLPATH_OK" >> "%LOG%" 2>&1
echo exitcode=%errorlevel% >> "%LOG%"
echo. >> "%LOG%"
echo [5] SysWOW64: >> "%LOG%"
"%SystemRoot%\SysWOW64\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -Command "Write-Output WOW64_OK" >> "%LOG%" 2>&1
echo exitcode=%errorlevel% >> "%LOG%"
echo. >> "%LOG%"
echo [6] pwsh PS7: >> "%LOG%"
where pwsh >> "%LOG%" 2>&1
pwsh -NoProfile -Command "Write-Output PWSH_OK" >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [7] icacls powershell.exe: >> "%LOG%"
icacls "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [8] AppLocker service: >> "%LOG%"
sc query appidsvc >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [9] AppLocker SrpV2 policy: >> "%LOG%"
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\SrpV2" /s >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [10] SRP Safer policy: >> "%LOG%"
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers" /s >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [11] Explorer DisallowRun: >> "%LOG%"
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun" /s >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [12] WindowsApps alias stub: >> "%LOG%"
dir "%LOCALAPPDATA%\Microsoft\WindowsApps\powershell.exe" >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [13] Defender ASR rules: >> "%LOG%"
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Windows Defender Exploit Guard\ASR\Rules" /s >> "%LOG%" 2>&1
reg query "HKLM\SOFTWARE\Microsoft\Windows Defender\Windows Defender Exploit Guard\ASR\Rules" /s >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo === END === >> "%LOG%"
echo Report written to ps_diag_report.txt - closing in 8s.
timeout /t 8 /nobreak >nul
