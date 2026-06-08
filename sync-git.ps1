#!/usr/bin/env pwsh
# sync-git.ps1
# Synchronizes the local UAWOS repository with the remote GitHub repository.

$ErrorActionPreference = "Stop"

Write-Host "Checking git status..." -ForegroundColor Cyan
$status = git status --porcelain

if ($status) {
    Write-Host "Local changes detected. Staging and committing..." -ForegroundColor Green
    git add .
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "auto-sync: $timestamp"
} else {
    Write-Host "No local changes to commit." -ForegroundColor Gray
}

Write-Host "Pulling latest changes from remote..." -ForegroundColor Cyan
git pull --rebase origin main

# Check if there are commits to push
$statusRemote = git status -sb
if ($statusRemote -match "ahead") {
    Write-Host "Pushing changes to remote..." -ForegroundColor Green
    git push origin main
} else {
    Write-Host "Local repository is up-to-date with remote." -ForegroundColor Gray
}

Write-Host "Synchronization complete!" -ForegroundColor Green
