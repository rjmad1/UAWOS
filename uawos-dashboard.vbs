Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File C:\Users\rajaj\Projects\UAWOS\run-daemon-persistent.ps1", 0, false
