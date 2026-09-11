@echo off
setlocal
:: power_check.bat - LID-OFFLINE-1 (10 Sep 2026), v2. READ-ONLY, changes nothing.
:: v1 answered the main question (this machine has ONLY Modern Standby; it suspended 06:45:53 ->
:: 15:43:57 SAST on 10 Sep) but two of its four probes printed nothing:
::   * the LIDACTION alias is not recognised by powercfg /q, so it dumped only the scheme header.
::     v2 uses the real GUIDs: SUB_BUTTONS 4f971e89-... and LIDACTION 5ca83367-...
::   * Get-NetAdapterPowerManagement was wrapped in -ErrorAction SilentlyContinue, so whatever it
::     objected to was swallowed. v2 lets the error print, and falls back to the WMI class.
set STAMP=
for /f %%S in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set STAMP=%%S
set OUT=%~dp0host_queue\done\power_check_%STAMP%.txt
echo === power_check v2 %DATE% %TIME%   full output: %OUT%
> "%OUT%" echo === power_check v2 %DATE% %TIME%
>>"%OUT%" echo.
>>"%OUT%" echo --- LID CLOSE ACTION (0=do nothing 1=sleep 2=hibernate 3=shut down)
powercfg /q SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 >>"%OUT%" 2>&1
>>"%OUT%" echo.
>>"%OUT%" echo --- SLEEP / HIBERNATE IDLE TIMEOUTS (should be 0 = never, per David's setup)
powercfg /q SCHEME_CURRENT 238c9fa8-0aad-41ed-83f4-97be242c8f20 29f6c1db-86da-48c5-9fdb-f2b67b1f44da >>"%OUT%" 2>&1
>>"%OUT%" echo.
>>"%OUT%" echo --- NETWORK ADAPTER POWER MANAGEMENT (errors NOT suppressed this time)
powershell -NoProfile -Command "try { Get-NetAdapter -Physical | Get-NetAdapterPowerManagement | Select-Object Name,AllowComputerToTurnOffDevice | Format-List } catch { 'Get-NetAdapterPowerManagement failed: ' + $_.Exception.Message }" >>"%OUT%" 2>&1
powershell -NoProfile -Command "try { Get-CimInstance -Namespace root\wmi -ClassName MSPower_DeviceEnable | ForEach-Object { $id=$_.InstanceName; $n=(Get-CimInstance Win32_PnPEntity | Where-Object { $id -like ($_.PNPDeviceID -replace '\\','\\') + '*' }).Name; '{0,-55} wake/power-off allowed={1}' -f $n,$_.Enable } } catch { 'MSPower_DeviceEnable failed: ' + $_.Exception.Message }" >>"%OUT%" 2>&1
>>"%OUT%" echo.
>>"%OUT%" echo --- WHAT IS ALLOWED TO WAKE THIS MACHINE
powercfg /devicequery wake_armed >>"%OUT%" 2>&1
>>"%OUT%" echo.
>>"%OUT%" echo --- LAST WAKE / LAST SLEEP REASON
powercfg /lastwake >>"%OUT%" 2>&1
>>"%OUT%" echo.
>>"%OUT%" echo --- REQUESTS CURRENTLY HOLDING THE MACHINE AWAKE (needs admin; may say access denied)
powercfg /requests >>"%OUT%" 2>&1
type "%OUT%"
echo === power_check v2 done at %TIME%
exit /b 0
