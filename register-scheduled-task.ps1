# register-scheduled-task.ps1
# Script to register the UAWOS Dashboard Daemon as a Windows Scheduled Task.

$TaskName = "UAWOS_Dashboard_Daemon"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) {
    $ScriptDir = "C:\Users\rajaj\Projects\UAWOS"
}
$ScriptPath = Join-Path $ScriptDir "run-daemon-persistent.ps1"

Write-Host "Registering Scheduled Task: $TaskName" -ForegroundColor Cyan
Write-Host "Target Script Path: $ScriptPath" -ForegroundColor Gray

# 1. Define Trigger: At Logon of the current user
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# 2. Define Action: Run PowerShell in a hidden window to execute the persistent daemon script
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ScriptPath`""

# 3. Define Settings:
# - Allow starting on batteries (critical for laptops)
# - Don't stop if going on battery
# - Start as soon as possible if trigger missed
# - Restart 3 times on failure, waiting 1 minute between attempts
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# 4. Get Current User Security Context
$User = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
Write-Host "Registering task to run under user account: $User" -ForegroundColor Gray

# 5. Register Task
try {
    Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Settings $Settings -User $User -Force | Out-Null
    Write-Host "Scheduled Task '$TaskName' registered successfully." -ForegroundColor Green
    
    # 6. Start the task immediately
    Write-Host "Starting Scheduled Task..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Scheduled Task started successfully. The daemon is now running in the background." -ForegroundColor Green
} catch {
    Write-Error "Failed to register Scheduled Task: $_"
    Write-Host "`nTroubleshooting Tip: If you get an access denied error, try running this script in an Administrator PowerShell window." -ForegroundColor Yellow
}
