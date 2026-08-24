# notify_attention.ps1 - WINDOW-ZORDER-1 (25 Aug 2026)
#
# David: "my terminal window just stubbornly appears behind the claude window and
# then i miss it... it used to sit in front of Claude and not behind."
#
# WHY THE WINDOW CANNOT SIMPLY RAISE ITSELF
# Windows refuses SetForegroundWindow to a process that does not own the current
# foreground - deliberately, so background apps cannot steal your typing. When a
# Claude session launches the deploy, the launch is non-foreground BY DESIGN
# ("the user's focus is preserved"), so the console opens behind whatever David
# is looking at. Fighting that would be fighting the thing that stops every other
# app interrupting him.
#
# So we use the signal Windows provides FOR EXACTLY THIS: FlashWindowEx. It
# flashes the taskbar button and the caption until the window is looked at
# (FLASHW_TIMERNOFG). That is the native "I need you" and it works from behind.
#
# Called from a .bat with no new window, so this process shares the parent's
# console - GetConsoleWindow() returns the very window that is waiting.
param([string]$Title = "")

if ($Title -ne "") { $host.UI.RawUI.WindowTitle = $Title }

try { [Console]::Beep(880,120); [Console]::Beep(1320,200) } catch { }

try {
  Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class TsFlash {
  [StructLayout(LayoutKind.Sequential)]
  public struct FLASHWINFO {
    public uint cbSize; public IntPtr hwnd; public uint dwFlags;
    public uint uCount; public uint dwTimeout;
  }
  [DllImport("user32.dll")] public static extern bool FlashWindowEx(ref FLASHWINFO pwfi);
  [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
  public static void Go() {
    IntPtr h = GetConsoleWindow();
    if (h == IntPtr.Zero) { return; }
    FLASHWINFO fi = new FLASHWINFO();
    fi.cbSize   = (uint)Marshal.SizeOf(typeof(FLASHWINFO));
    fi.hwnd     = h;
    fi.dwFlags  = 0x0000000F;   // FLASHW_ALL (caption+tray) | FLASHW_TIMERNOFG
    fi.uCount   = 0;            // keep flashing until the window is brought forward
    fi.dwTimeout= 0;
    FlashWindowEx(ref fi);
  }
}
"@ -ErrorAction Stop
  [TsFlash]::Go()
} catch {
  # A notifier must NEVER break a deploy. If the flash cannot load, the beep and
  # the window title still did their job.
}
