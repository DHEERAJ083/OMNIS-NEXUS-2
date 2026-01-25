# Omnis-Nexus Setup Script for Windows
$ErrorActionPreference = "Stop"

Write-Host "Setting up Omnis-Nexus Environment..." -ForegroundColor Cyan

# check python
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH."
}

# Create venv
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate and Install
Write-Host "Installing dependencies..."
& ".\.venv\Scripts\python" -m pip install -r requirements.txt

Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "To run the server manually:"
Write-Host "  .\.venv\Scripts\python omnis_nexus_server.py"
