@echo off
setlocal enableextensions
set LOG=C:\Users\David\Projects\MarketSquare\defender_check_report.txt
echo === Defender status check %date% %time% === > "%LOG%"
"%SystemRoot%\SysWOW64\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -Command "Get-MpComputerStatus | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled,BehaviorMonitorEnabled,AntivirusSignatureLastUpdated | Format-List" >> "%LOG%" 2>&1
echo [AV products registered:] >> "%LOG%"
"%SystemRoot%\SysWOW64\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -Command "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | Select-Object displayName,productState | Format-List" >> "%LOG%" 2>&1
echo === END === >> "%LOG%"
echo Defender check written - closing in 5s.
timeout /t 5 /nobreak >nul
