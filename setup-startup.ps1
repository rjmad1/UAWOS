# setup-startup.ps1
# Copies the VBScript wrapper to the Windows Startup folder and runs it.

$StartupFolder = [System.IO.Path]::Combine($env:APPDATA, 'Microsoft\Windows\Start Menu\Programs\Startup')
$DestPath = Join-Path $StartupFolder "uawos-dashboard.vbs"

if (Test-Path ".\uawos-dashboard.vbs") {
    Copy-Item -Path ".\uawos-dashboard.vbs" -Destination $DestPath -Force
    Write-Host "Successfully copied UAWOS Startup VBScript to: $DestPath" -ForegroundColor Green
    
    # Execute it now to run the daemon in the background immediately
    Write-Host "Starting background daemon..." -ForegroundColor Cyan
    Start-Process "wscript.exe" -ArgumentList "`"$DestPath`""
    Write-Host "UAWOS Dashboard background daemon started." -ForegroundColor Green
} else {
    Write-Error "Could not find uawos-dashboard.vbs in the current directory."
}
