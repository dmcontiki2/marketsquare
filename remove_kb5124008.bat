@echo off
REM ===========================================================================
REM  Removes Windows update KB5124008 (installed 8 Sep 2026), which broke the
REM  Claude sandbox: the little Linux machine can no longer see the hard drive.
REM  Anthropic have no fix yet; removing this update is the only known remedy.
REM  Reported here: github.com/anthropics/claude-code/issues/92984
REM
REM  David gave permission on 10 Sep 2026: "please proceed and remove that
REM  update until Anthropic has fixed the issue."
REM
REM  This needs administrator rights, so Windows will ask you to approve it.
REM  If this does not work: Settings > Windows Update > Update history >
REM  Uninstall updates > KB5124008 > Uninstall.
REM ===========================================================================
echo.
echo Removing Windows update KB5124008 ...
echo Windows will ask for permission in a moment. Say Yes.
echo.
powershell -NoProfile -Command "Start-Process wusa.exe -ArgumentList '/uninstall','/kb:5124008','/norestart' -Verb RunAs"
echo.
echo When the Windows box says it is finished, restart the PC.
echo After the restart the sandbox should work again.
echo.
pause
