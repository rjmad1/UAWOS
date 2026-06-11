Set WshShell = CreateObject("WScript.Shell")
strScriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & strScriptDir & "\run-daemon-persistent.ps1""", 0, false
