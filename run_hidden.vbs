' run_hidden.vbs -- launches a batch file with NO console window.
' Added 13 Sep 2026: Task Scheduler ran autodeploy_agent.bat directly, so a black
' cmd window flashed on David's screen every 20 minutes. Nothing was wrong -- the
' agent was simply visible. This wrapper hides the window and WAITS for the batch
' to finish, so the task's duration and exit code stay truthful and Task Scheduler's
' "do not start a new instance" guard still prevents overlapping ticks.
'
' Usage:  wscript.exe run_hidden.vbs "C:\full\path\to\script.bat"

If WScript.Arguments.Count = 0 Then WScript.Quit 1
Set sh = CreateObject("WScript.Shell")
rc = sh.Run("""" & WScript.Arguments(0) & """", 0, True)
WScript.Quit rc
