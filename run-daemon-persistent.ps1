# run-daemon-persistent.ps1
# This script is executed by the Windows Scheduled Task to keep the dashboard running.

# Ensure we are in the correct directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) {
    $ScriptDir = "C:\Users\rajaj\Projects\UAWOS"
}
Set-Location $ScriptDir

# Redirect stdout and stderr to log files
$OutLog = Join-Path $ScriptDir "uawos_persistent_out.log"
$ErrLog = Join-Path $ScriptDir "uawos_persistent_err.log"

Start-Transcript -Path $OutLog -Append

Write-Output "$(Get-Date): Persistent Daemon run script initiated."

# Check if Docker is running, if not start Docker Desktop
$DockerRunning = $false
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $DockerInfo = docker info --format '{{.Name}}' 2>$null
    if ($DockerInfo) {
        $DockerRunning = $true
    }
}

if (-not $DockerRunning) {
    Write-Output "$(Get-Date): Docker is not running. Attempting to start Docker Desktop..."
    $DockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $DockerPath) {
        Start-Process $DockerPath
        # Wait up to 45 seconds for Docker to start
        for ($i = 0; $i -lt 45; $i++) {
            Start-Sleep -Seconds 1
            $DockerInfo = docker info --format '{{.Name}}' 2>$null
            if ($DockerInfo) {
                Write-Output "$(Get-Date): Docker Desktop started successfully."
                $DockerRunning = $true
                break
            }
        }
    } else {
        Write-Output "$(Get-Date): Docker Desktop executable not found at $DockerPath"
    }
}

if ($DockerRunning) {
    Write-Output "$(Get-Date): Starting Docker Compose services..."
    docker compose up -d 2>&1 | Write-Output
} else {
    Write-Output "$(Get-Date): Docker not running or not found. Skipping docker compose."
}

# Run the Python daemon in the foreground and auto-restart on exit
$PythonPath = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) {
    $PythonPath = "python"
}

Write-Output "$(Get-Date): Script directory is $ScriptDir"
Write-Output "$(Get-Date): Python path is $PythonPath"

while ($true) {
    Write-Output "$(Get-Date): Launching UAWOS Dashboard Daemon..."
    & $PythonPath uawos_dashboard_daemon.py
    Write-Output "$(Get-Date): UAWOS Dashboard Daemon exited. Restarting in 5 seconds..."
    Start-Sleep -Seconds 5
}

Stop-Transcript
