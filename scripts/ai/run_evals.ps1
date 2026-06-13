# UAWOS - Promptfoo Evaluation Automator
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Running UAWOS Prompt Evaluation Suite via Promptfoo" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Resolve absolute paths
$PythonPath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../../.venv/Scripts/python.exe"))
$ConfigPath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../../.ai/evaluations/promptfooconfig.yaml"))

Write-Host "Config Path: $ConfigPath" -ForegroundColor Yellow
Write-Host "Python Path: $PythonPath" -ForegroundColor Yellow

# Set environment variable to ensure promptfoo uses the correct virtualenv python
$env:PROMPTFOO_PYTHON = $PythonPath

# Execute evaluation
npx promptfoo eval -c "$ConfigPath" --no-cache

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Promptfoo evaluation completed successfully!" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] Promptfoo evaluation failed with exit code $LASTEXITCODE." -ForegroundColor Red
    exit $LASTEXITCODE
}
