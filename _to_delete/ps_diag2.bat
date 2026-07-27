@echo off
setlocal enableextensions
set LOG=C:\Users\David\Projects\MarketSquare\ps_diag2_report.txt
echo === PS diagnosis round 2 %date% %time% === > "%LOG%"
echo [1] IFEO powershell.exe (64-bit view): >> "%LOG%"
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\powershell.exe" /s >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [2] IFEO powershell.exe (32-bit view): >> "%LOG%"
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\powershell.exe" /s >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [3] Smart App Control state (1=on 2=eval 0=off): >> "%LOG%"
reg query "HKLM\SYSTEM\CurrentControlSet\Control\CI\Policy" /v VerifiedAndReputablePolicyState >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [4] Installed antivirus products (via WORKING 32-bit PS): >> "%LOG%"
"%SystemRoot%\SysWOW64\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -Command "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | Select-Object displayName,productState | Format-List" >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [5] AppLocker block events (last 8): >> "%LOG%"
wevtutil qe "Microsoft-Windows-AppLocker/EXE and DLL" /c:8 /rd:true /f:text >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [6] CodeIntegrity block events (last 8): >> "%LOG%"
wevtutil qe "Microsoft-Windows-CodeIntegrity/Operational" /c:8 /rd:true /f:text >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo [7] HKLM Explorer DisallowRun: >> "%LOG%"
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /s >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo === END === >> "%LOG%"
echo Round-2 report written - closing in 6s.
timeout /t 6 /nobreak >nul
