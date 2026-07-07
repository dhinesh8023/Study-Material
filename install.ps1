$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Installing StudyShare dependencies..." -ForegroundColor Cyan
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Installation failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Start the app with: python app.py" -ForegroundColor Yellow
